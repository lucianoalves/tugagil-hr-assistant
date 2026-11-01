"""Tests must not inherit scoring overrides from a developer's shell."""

import os

os.environ.pop("TUGAAGIL_SCORING_WEIGHTS_JSON", None)
os.environ.pop("TUGAAGIL_SCORING_WEIGHTS_FILE", None)
# Tests must not inherit developer or CI secrets, and must not print them.
for _secret_name in (
    "TUGAAGIL_API_KEY",
    "TUGAAGIL_API_KEY_PREVIOUS",
    "CRON_SECRET",
    "CRON_SECRET_PREVIOUS",
    "GEMINI_API_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "SUPABASE_URL",
    "LLM_ALLOW_PAID",
    "LLM_ENABLED",
    "VERCEL",
):
    os.environ.pop(_secret_name, None)
