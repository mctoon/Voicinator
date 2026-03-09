# Quickstart: 013 Automatic Pipeline Processing

Verify that the pipeline processes media automatically (no API call or run button).

---

## Prerequisites

- Python 3.11+; run from repo root.
- Config: `voicinator.toml` with pipeline base paths (or inbox tab paths) and channel folders. Automatic processing enabled (default when 013 is implemented).
- At least one base path under which channel folders exist with step folders: `[Channel]/Videos 1 to be transcribed/`, … , `Videos 8 export ready`, `Videos`.

---

## 1. Start the app

```bash
./run.sh
```

The app starts and the background discovery loop starts. No need to call any API to begin processing.

---

## 2. Place a media file in step 1

- Put one media file (and optionally sister files) in:  
  `[base]/[Channel Name]/Videos 1 to be transcribed/`
- Do **not** call POST /api/pipeline/run.

Within **1 minute**, the system should discover the file and start processing (e.g. step 2 then step 3). The file (and paired folder) will move through step folders as each step completes. Only one file is processed at a time; higher step numbers have priority if multiple files exist.

---

## 3. Verify discovery and status (read-only API)

- **GET** `/api/pipeline/discover`  
  Optional: may show only step 1 or all steps; use to see if files are visible.
- **GET** `/api/pipeline/status`  
  Expect counts by step to change as the file moves (e.g. from step 1 to step 2, then step 3, etc.).

---

## 4. Confirm no run API

- **POST** `/api/pipeline/run`  
  Expect **410 Gone** (or 404) and a message that processing is automatic. No run is triggered by this call.

---

## 5. Idle and priority

- When no media is in any step folder, the system sleeps until the next scan (no busy-wait).
- If you add one file in step 1 and one in step 4, the file in step 4 is processed first (higher step number has priority). Then the step 1 file will be processed in a later cycle.

---

## 6. Restart behavior

- Stop the app, leave a media file in "Videos 1 to be transcribed", then start the app again.
- Within 1 minute of startup, that file should be discovered and processing should start automatically (no manual run).
