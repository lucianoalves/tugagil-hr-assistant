# Pilot secrets and portal contract

The member portal (`tugaweb`) calls this API with a shared server key. Vercel Cron calls `GET /internal/maintenance` with a separate secret. Neither value is read from a file in the repository.

## Where the variables are set

Production and preview values live in the Vercel project's Environment Variables for this service (the deployment whose entrypoint is `src.api.app:app`, from `pyproject.toml`). `vercel.json` only sets the cron path (`/internal/maintenance`, `0 3 * * *`, region `dub1`). It does not contain secret values. When `CRON_SECRET` is set on that project, Vercel sends `Authorization: Bearer <CRON_SECRET>` on the cron request.

The GitHub Actions quality workflow does not receive these secrets.

Locally, export the variables in the shell or inject a gitignored `.env` with `uv run --env-file .env` or `uvicorn --env-file .env`. `Settings` does not open `.env`, `.local/`, or `pilot-deploy.json`. `.local/` and `pilot-deploy.json` are gitignored. A long-running process caches settings until restart, so a change applies on the next deploy or process start.

| Name | Role |
| --- | --- |
| `TUGAAGIL_API_KEY` | Current portal key. Required. Sent as `x-api-key`. |
| `TUGAAGIL_API_KEY_PREVIOUS` | Retiring portal key. Optional, rotation window only. |
| `CRON_SECRET` | Current cron secret. Required outside development and on Vercel. |
| `CRON_SECRET_PREVIOUS` | Retiring cron secret. Optional, rotation window only. |
| `SUPABASE_URL` | Supabase project URL for storage download and task RPCs. |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key. Server-side only. |
| `GEMINI_API_KEY` | Gemini Developer API key. Not a Vertex credential. |
| `LLM_ENABLED` | Must be true before `permit_ai` is sent to `portal_claim_task`. |
| `LLM_ALLOW_PAID` | Default false. Blocks tasks whose `billing_mode` is `paid`. |
| `ENVIRONMENT` | `development` or `test` may boot without secrets and still reject calls. Any other value, or `VERCEL=1`, refuses to start unless the API key and cron secret are set. |
| `TUGAAGIL_REQUIRE_USER_CONTEXT` | ASGI default true. Requires `x-user-id`. |

`SUPABASE_SERVICE_ROLE_KEY`, the database password, `GEMINI_API_KEY`, the portal key, and the cron secret were exposed in a developer's plaintext `.local/pilot-deploy.json`. That file is not in this repository's history. Rotate the live values anyway. Do not rewrite git history for this.

## Rotation

1. Generate new values outside the repo. Do not reuse the exposed ones. Do not paste them into git, issues, logs, or `.local/`.
2. In Vercel Environment Variables for this service, set `TUGAAGIL_API_KEY` and `CRON_SECRET` to the new values, and set `TUGAAGIL_API_KEY_PREVIOUS` and `CRON_SECRET_PREVIOUS` to the values still in use. Rotate `SUPABASE_SERVICE_ROLE_KEY` in the same step (Supabase dashboard, then this project's env). Rotate the database password in Supabase. Rotate `GEMINI_API_KEY` in Google AI Studio and update this project's env. This service does not read the database password; the portal and Supabase do.
3. Redeploy this service so the process reloads the environment. During the overlap it accepts the current and previous portal key and cron secret. Comparison is constant time and responses never include the secret.
4. Update the portal's server environment so the header `x-api-key` is the new `TUGAAGIL_API_KEY`. Confirm `POST /api/validate` and `POST /internal/process` succeed, and that the next scheduled `GET /internal/maintenance` is authorized.
5. Clear `TUGAAGIL_API_KEY_PREVIOUS` and `CRON_SECRET_PREVIOUS`, then redeploy. Delete any leftover `.local/pilot-deploy.json` from developer machines.

## Contract the portal must send

All routes except `GET /health` and `GET /internal/maintenance` require:

- `x-api-key`: the current shared key, or the previous key during rotation.
- `x-user-id`: the member's Supabase auth user UUID when `TUGAAGIL_REQUIRE_USER_CONTEXT` is true (the ASGI default). `POST /internal/process` always parses this header as a UUID and passes it as `actor_filter` to `portal_claim_task`.

`GET /internal/maintenance` does not use `x-api-key`. It requires `Authorization: Bearer <CRON_SECRET>` (previous secret accepted during rotation). That route is the Vercel cron, not a member action.

`x-user-plan` and `x-user-role` are ignored by the ASGI API. Sending `free`, `associate`, or nothing does not grant or deny access. The legacy `python -m src.api.server` process may record those headers in its audit log and still does not authorize on them.

This service does not read membership, plan, or pilot tables. Synchronous routes (`/api/validate`, `/api/analyze-job`, extract, export) run for any caller that presents the shared key and user id. The portal must enforce associate plan and pilot access before it calls them and before it inserts a task.

Queued work is claimed with `portal_claim_task(worker, permit_ai, actor_filter)`. `permit_ai` is true only when `LLM_ENABLED` is true and `GEMINI_API_KEY` is set. The worker does not receive or compare a plan code. It reads `id`, `lease_token`, `operation`, `content.cv_text`, `content.linkedin_text`, `job_text`, `billing_mode`, `model`, `request`, `resources`, `confirmed_gaps`, `score`, and `score_modules`, then finishes with `portal_finish_task(task, token, response, failure, tokens_in, tokens_out)`.

An automatic `associate` assignment written at signup is compatible with this API, as long as the portal's own gate and `portal_claim_task` read that same membership row. There is no second allow-list here that would still require a manual plan change. If a new member cannot create applications, the check is in the portal or in that RPC, not in a plan header.

## Gemini billing

Calls use the Gemini Developer API (`google-genai` with `GEMINI_API_KEY`), not Vertex AI. This repo has no GCP project, region, or workload-identity settings. The model id comes from the task row (`task["model"]`), not from a constant here.

`LLM_ALLOW_PAID` defaults to false. A claimed task with `billing_mode=paid` is refused and is not sent to Gemini. Tasks the database marks as anything else are still sent when `permit_ai` is true, so the flag is not proof that the Google key is on the free tier. It only blocks work the portal labels as paid.

Before real member documents go to a paid model or to Vertex: sign a DPA with Google, set `LLM_ALLOW_PAID=true` only after that, point `GEMINI_API_KEY` at a billed key (or add a Vertex client, which is not implemented), and have the portal store `billing_mode=paid` plus the allowed model. Leave the flag false until then.
