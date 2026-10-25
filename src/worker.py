"""A standalone worker; task leases and quotas are held transactionally in PostgreSQL."""

import argparse
import json
import time
import uuid
from typing import Any

import httpx

from src.ai.gemini import GeminiProvider
from src.ai.service import analyze
from src.api.server import validate_payload
from src.config import Settings, get_settings
from src.engine.jobs import analyze_job


class Worker:
    def __init__(self, settings: Settings):
        if not settings.supabase_url or not settings.supabase_service_role_key:
            raise ValueError("Configure SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY no backend")
        self.settings = settings
        self.id = str(uuid.uuid4())
        self.client = httpx.Client(
            base_url=settings.supabase_url.rstrip("/") + "/rest/v1/",
            headers={
                "apikey": settings.supabase_service_role_key,
                "Authorization": "Bearer " + settings.supabase_service_role_key,
            },
            timeout=20,
        )

    def rpc(self, name: str, body: dict[str, Any]) -> Any:
        response = self.client.post("rpc/" + name, json=body)
        response.raise_for_status()
        return response.json() if response.content else None

    def once(self, actor: str | None = None) -> bool:
        task = self.rpc(
            "portal_claim_task",
            {
                "worker": self.id,
                "permit_ai": self.settings.llm_enabled and bool(self.settings.gemini_api_key),
                "actor_filter": actor,
            },
        )
        if not task:
            return False
        result = None
        failure = None
        tokens_in = tokens_out = 0
        try:
            content = task["content"]
            if task["operation"] == "cv_rules":
                result, status = validate_payload(
                    {
                        "cv_text": content["cv_text"],
                        "linkedin_text": content.get("linkedin_text", ""),
                    }
                )
                if status != 200:
                    raise ValueError("Não foi possível analisar este currículo")
            elif task["operation"] == "job_rules":
                result = analyze_job(content["cv_text"], task["job_text"])
            else:
                if task["billing_mode"] == "paid" and not self.settings.llm_allow_paid:
                    raise ValueError("Chamadas pagas não autorizadas neste ambiente")
                provider = GeminiProvider(self.settings.gemini_api_key)
                try:
                    result, tokens_in, tokens_out = analyze(
                        provider,
                        task["model"],
                        task["operation"],
                        content["cv_text"],
                        content.get("linkedin_text", ""),
                        task.get("job_text") or "",
                        task.get("resources") or [],
                        task.get("confirmed_gaps") or [],
                        task.get("request") or {},
                    )
                finally:
                    provider.close()
        except ValueError as exc:
            # Controlled validation errors contain no raw model or document content.
            failure = "Resposta sem evidências válidas; reveja as fontes ou tente novamente."
            print(
                json.dumps(
                    {
                        "event": "analysis_validation_failed",
                        "task_id": task["id"],
                        "type": type(exc).__name__,
                    }
                )
            )
        except Exception as exc:
            failure = "Serviço temporariamente indisponível; os resultados por regras continuam disponíveis."
            print(
                json.dumps(
                    {"event": "analysis_failed", "task_id": task["id"], "type": type(exc).__name__}
                )
            )
        accepted = self.rpc(
            "portal_finish_task",
            {
                "task": task["id"],
                "token": task["lease_token"],
                "response": result,
                "failure": failure,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
            },
        )
        print(
            json.dumps(
                {
                    "event": "analysis_finished",
                    "task_id": task["id"],
                    "accepted": accepted,
                    "success": failure is None,
                }
            )
        )
        return True

    def close(self):
        self.client.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    settings = get_settings()
    worker = Worker(settings)
    try:
        while True:
            try:
                processed = worker.once()
            except httpx.HTTPError as exc:
                print(json.dumps({"event": "worker_connection_failed", "type": type(exc).__name__}))
                if args.once:
                    raise SystemExit(1) from None
                processed = False
            if args.once:
                break
            if not processed:
                time.sleep(settings.worker_poll_seconds)
    except KeyboardInterrupt:
        pass
    finally:
        worker.close()


if __name__ == "__main__":
    main()
