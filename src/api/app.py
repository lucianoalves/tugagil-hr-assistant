"""ASGI API. Long running LLM work belongs to the durable worker."""

import base64
import os
import uuid
from typing import Any
from urllib.parse import quote

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from starlette.concurrency import run_in_threadpool

from src.api.secrets import bearer_matches, secret_matches
from src.api.server import RateLimiter, validate_payload
from src.config import Settings, get_settings
from src.engine.documents import (
    export_docx,
    export_linkedin_pack,
    extract_document,
    split_linkedin_pack,
)
from src.engine.jobs import analyze_job
from src.worker import Worker


class AnalysisInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cv_text: str = Field(default="", max_length=200000)
    linkedin_text: str = Field(default="", max_length=50000)


class LinkedInPackInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    linkedin_text: str = Field(min_length=1, max_length=50000)
    locale: str = Field(default="pt", max_length=8)


class JobInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cv_text: str = Field(min_length=1, max_length=200000)
    job_text: str = Field(min_length=20, max_length=100000)


class DocumentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    extension: str
    data: str = Field(max_length=14 * 1024 * 1024)


class StoredDocumentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    path: str = Field(min_length=1, max_length=200)


def stored_document(config: Settings, path: str, user: str) -> str:
    """Download only this authenticated user's private document; never arbitrary URLs."""
    try:
        uuid.UUID(user)
        owner, filename = path.split("/")
        stem, extension = filename.rsplit(".", 1)
        uuid.UUID(stem)
    except ValueError as exc:
        raise ValueError("Caminho inválido") from exc
    if owner != user or extension not in ("pdf", "docx"):
        raise ValueError("Ficheiro indisponível")
    if not config.supabase_url or not config.supabase_service_role_key:
        raise ValueError("Storage indisponível")
    url = (
        config.supabase_url.rstrip("/") + "/storage/v1/object/authenticated/cv-files/" + quote(path)
    )
    with (
        httpx.Client(timeout=20) as client,
        client.stream(
            "GET",
            url,
            headers={
                "apikey": config.supabase_service_role_key,
                "Authorization": "Bearer " + config.supabase_service_role_key,
            },
        ) as response,
    ):
        response.raise_for_status()
        content = bytearray()
        for chunk in response.iter_bytes():
            content.extend(chunk)
            if len(content) > 10 * 1024 * 1024:
                raise ValueError("Ficheiro demasiado extenso")
    return extract_document({"extension": extension, "data": base64.b64encode(content).decode()})


def _requires_configured_secrets(config: Settings) -> bool:
    """Deployed runtimes must not boot when the portal key or cron secret is missing.

    `VERCEL=1` covers a project that left `ENVIRONMENT` at its development default.
    """
    if os.getenv("VERCEL") == "1":
        return True
    return config.environment not in {"development", "test"}


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or get_settings()
    if _requires_configured_secrets(config) and (not config.api_key or not config.cron_secret):
        raise ValueError("TUGAAGIL_API_KEY and CRON_SECRET are required outside development")
    app = FastAPI(title="TugÁgil HR Assistant", version="0.4.0", docs_url=None, redoc_url=None)
    limiter = RateLimiter(60, 60)

    @app.middleware("http")
    async def boundary(request: Request, call_next):
        request_id = str(uuid.uuid4())
        maintenance = request.url.path == "/internal/maintenance"
        if maintenance:
            # Vercel Cron sends `Authorization: Bearer $CRON_SECRET`. No x-api-key.
            if not bearer_matches(
                request.headers.get("authorization", ""),
                config.cron_secret,
                config.cron_secret_previous,
            ):
                return JSONResponse({"error": {"code": "unauthorized"}}, status_code=401)
        elif request.url.path != "/health":
            # Portal shared key. Plan and pilot are not headers this API authorizes on.
            provided = request.headers.get("x-api-key", "")
            if not secret_matches(provided, config.api_key, config.api_key_previous):
                return JSONResponse({"error": {"code": "unauthorized"}}, status_code=401)
            user = request.headers.get("x-user-id", "")
            if config.require_user_context and not user:
                return JSONResponse({"error": {"code": "missing_user_context"}}, status_code=400)
            allowed, retry = limiter.check(user or "anonymous")
            if not allowed:
                return JSONResponse(
                    {"error": {"code": "rate_limit_exceeded"}},
                    status_code=429,
                    headers={"Retry-After": str(retry)},
                )
            limit = 15 * 1024 * 1024 if request.url.path == "/api/extract" else 2 * 1024 * 1024
            chunks = bytearray()
            async for chunk in request.stream():
                chunks.extend(chunk)
                if len(chunks) > limit:
                    return JSONResponse({"error": {"code": "payload_too_large"}}, status_code=413)
            # Cached body is forwarded by Starlette's request wrapper.
            request._body = bytes(chunks)
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response

    async def payload(request: Request, schema: type[BaseModel]) -> dict[str, Any]:
        return schema.model_validate(await request.json()).model_dump()

    @app.exception_handler(ValueError)
    async def invalid_input(_request: Request, _exc: ValueError):
        return JSONResponse(
            {"error": {"code": "invalid_payload", "message": "Conteúdo inválido"}}, status_code=400
        )

    @app.exception_handler(ValidationError)
    async def invalid_schema(_request: Request, _exc: ValidationError):
        return JSONResponse(
            {"error": {"code": "invalid_payload", "message": "Verifique os campos e limites"}},
            status_code=400,
        )

    @app.get("/health")
    def health():
        return {"status": "ok", "version": "0.4.0", "llm_enabled": config.llm_enabled}

    @app.post("/api/validate")
    async def validate(request: Request):
        body, status = await run_in_threadpool(
            validate_payload, await payload(request, AnalysisInput)
        )
        return JSONResponse(body, status_code=status)

    @app.post("/api/analyze-job")
    async def job(request: Request):
        body = await payload(request, JobInput)
        return await run_in_threadpool(analyze_job, body["cv_text"], body["job_text"])

    @app.post("/api/extract")
    async def extract(request: Request):
        return {
            "text": await run_in_threadpool(extract_document, await payload(request, DocumentInput))
        }

    @app.post("/api/extract-stored")
    async def extract_stored(request: Request):
        body = await payload(request, StoredDocumentInput)
        return {
            "text": await run_in_threadpool(
                stored_document, config, body["path"], request.headers.get("x-user-id", "")
            )
        }

    def process_one(actor: str | None = None) -> dict[str, int]:
        worker = Worker(config)
        try:
            return {"processed": int(worker.once(actor))}
        finally:
            worker.close()

    @app.post("/internal/process")
    async def process(request: Request):
        actor = str(uuid.UUID(request.headers.get("x-user-id", "")))
        return await run_in_threadpool(process_one, actor)

    @app.get("/internal/maintenance")
    async def maintenance():
        # A bounded recovery invocation, compatible with the Hobby daily cron.
        return await run_in_threadpool(process_one)

    @app.exception_handler(httpx.HTTPError)
    async def upstream_unavailable(_request: Request, _exc: httpx.HTTPError):
        return JSONResponse({"error": {"code": "service_unavailable"}}, status_code=503)

    @app.post("/api/export-cv")
    async def export(request: Request):
        body = await payload(request, AnalysisInput)
        document = await run_in_threadpool(export_docx, body["cv_text"])
        return {"data": base64.b64encode(document).decode("ascii")}

    @app.post("/api/split-linkedin")
    async def split_linkedin(request: Request):
        body = await payload(request, LinkedInPackInput)
        try:
            sections = await run_in_threadpool(split_linkedin_pack, body["linkedin_text"])
        except ValueError as exc:
            return JSONResponse({"error": {"code": "invalid_document", "message": str(exc)}}, 400)
        return {"sections": sections}

    @app.post("/api/export-linkedin-pack")
    async def export_linkedin(request: Request):
        body = await payload(request, LinkedInPackInput)
        try:
            document = await run_in_threadpool(
                export_linkedin_pack, body["linkedin_text"], body.get("locale") or "pt"
            )
        except ValueError as exc:
            return JSONResponse({"error": {"code": "invalid_document", "message": str(exc)}}, 400)
        return {
            "filename": "linkedin-sections.zip",
            "data": base64.b64encode(document).decode("ascii"),
        }

    return app


app = create_app()
