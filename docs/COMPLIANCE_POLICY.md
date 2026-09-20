# Compliance Policy Draft

## LinkedIn Data Policy
- LinkedIn scraping is not allowed.
- LinkedIn input must come from user-provided text, structured form data, or profile export.
- The platform does not call unofficial LinkedIn APIs or automated scraping workflows.

## Retention and Deletion Policy
- Default retention window for validation records is 180 days.
- Records older than 180 days should be deleted by scheduled cleanup in production deployments.
- Users should be able to request deletion of their validation data before the retention deadline.

## Environment Notes
- Local development may persist sample payloads and logs for debugging.
- Production environments should keep only the minimum metadata required for audit and quality operations.
- Raw CV/LinkedIn text should not be retained beyond processing needs when optional narrative generation is enabled.
