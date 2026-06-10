# Drive Search Hardening (without Composio)

Checklist applied in real session:

- OAuth validated with `setup.py --check`.
- Initial failure diagnosis: `HttpError 403 accessNotConfigured` (Drive API disabled in GCP project).
- After enabling API in Console, search returned to normal.

Confirmed robustness improvements:

1. Input escaping (`'` and `\\`) when building `fullText contains '...`.
2. Default filter `trashed = false` in textual mode.
3. Pagination via `nextPageToken` until reaching `--max`.
4. `--max >= 1` validation.

Recommended minimum test:

- Common term: `relatório`
- Term with apostrophe: `O'Reilly`
- `--max` above page size to validate pagination.
