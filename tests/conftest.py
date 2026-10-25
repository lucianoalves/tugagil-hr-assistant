"""Tests must not inherit scoring overrides from a developer's shell."""

import os

os.environ.pop("TUGAAGIL_SCORING_WEIGHTS_JSON", None)
os.environ.pop("TUGAAGIL_SCORING_WEIGHTS_FILE", None)
