"""Constant-time checks for shared secrets.

Callers must not log provided values or configured secrets.
"""

from __future__ import annotations

import hmac

_DIGEST_KEY = b"tugagil-hr-assistant-secret-compare"
_BEARER_PREFIX = "bearer "


def _digest(value: str) -> bytes:
    return hmac.digest(_DIGEST_KEY, value.encode("utf-8"), "sha256")


def secret_matches(provided: str, current: str, previous: str = "") -> bool:
    """True when `provided` equals the current secret, or the previous one during rotation.

    Fail closed when the current secret is unset. Both digests are compared before
    returning so a match on the first candidate does not skip the second.
    """
    current_clean = current.strip()
    previous_clean = previous.strip()
    if not current_clean:
        return False
    provided_digest = _digest(provided.strip())
    current_ok = hmac.compare_digest(provided_digest, _digest(current_clean))
    if previous_clean:
        previous_ok = hmac.compare_digest(provided_digest, _digest(previous_clean))
    else:
        previous_ok = False
        hmac.compare_digest(provided_digest, _digest("previous-unset"))
    return bool(current_ok | previous_ok)


def bearer_matches(authorization_header: str, current: str, previous: str = "") -> bool:
    """Match `Authorization: Bearer <secret>` against the cron secret pair."""
    header = authorization_header.strip()
    prefix_len = len(_BEARER_PREFIX)
    if len(header) >= prefix_len and header[:prefix_len].lower() == _BEARER_PREFIX:
        token = header[prefix_len:].strip()
    else:
        # A raw secret without the Bearer scheme must not match.
        token = "invalid-scheme:" + header
    return secret_matches(token, current, previous)
