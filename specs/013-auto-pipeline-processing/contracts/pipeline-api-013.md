# Contract: Pipeline API (013 – Automatic Processing)

Changes to the pipeline API when automatic processing (013) is enabled. Base prefix remains `/api/pipeline` where applicable.

---

## Removed or disabled

- **POST /api/pipeline/run** MUST NOT be exposed when automatic processing is enabled. Either:
  - Do not register the route, or
  - Return 410 Gone (or 404) with a body indicating that processing is automatic and no run trigger is needed.

Processing is triggered solely by file presence in pipeline step folders; no client call starts a run.

---

## Unchanged (read-only)

- **GET /api/pipeline/config** — Returns base paths, step folders, unknown-speakers step name, final folder name. Still supported for operator visibility.
- **GET /api/pipeline/discover** — Returns media in "Videos 1 to be transcribed" (or optionally all steps). Useful for debugging and UI.
- **GET /api/pipeline/status** — Returns counts by step. Still supported for operator visibility.

These endpoints remain read-only and do not trigger processing.
