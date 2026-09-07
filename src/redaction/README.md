# Redaction Module

Implemented baseline responsibilities:
- detect and mask email addresses
- detect and mask phone numbers
- detect and mask URLs
- detect and mask LinkedIn profile URLs
- detect and mask GitHub profile URLs

Redaction is applied in `/api/validate` before any optional LLM usage.
