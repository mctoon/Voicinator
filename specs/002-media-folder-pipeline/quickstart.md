# Quickstart: 002 Media Folder Pipeline

Run the pipeline and verify behavior.

---

## Prerequisites

- Python 3.11+; run from repo root.
- Config: `voicinator.toml` (and optionally `inbox_queue_config.toml` or pipeline base paths in master config). At least one base path under which channel folders exist with structure: `[Channel Name]/Videos 1 to be transcribed/`.
- One or more media files in `Videos 1 to be transcribed` (e.g. moved there via 001 inbox-queue UI).

---

## 1. Start the app

```bash
./run.sh
```

App runs (Flask); pipeline API and unknown-speakers API are available if implemented.

---

## 2. Verify pipeline config

- **GET** `/api/pipeline/config`  
  Expect: `basePaths`, `stepFolders`, `unknownSpeakersStepName`, `finalFolderName`.

---

## 3. Discover input media

- **GET** `/api/pipeline/discover`  
  Expect: `items` array with `mediaPath`, `pairedFolderPath`, `channelName`, `basePath` for each file in "Videos 1 to be transcribed".

---

## 4. Run pipeline (one pass)

- **POST** `/api/pipeline/run`  
  No body or `{}`. Each run processes all discovered files in step 1 (no limit). Only one run at a time; if a run is in progress, request is rejected or queued.  
  Expect: `processed`, `movedToStep5` or `movedToVideos`, `errors`.

- Check filesystem: media (and paired folder) should move to "Videos 2 audio extracted", then "Videos 3 transcribed", etc., according to step completion. If speaker is unknown, file should land in "Videos 5 needs speaker identification".

---

## 5. Transcript outputs

- Open the paired folder for a file that reached step 3 or beyond.  
  Expect: word-level transcript (e.g. JSON with `word`, `start`, `end`) and a human-readable TXT with speaker labels and paragraph-level text.

---

## 6. Unknown-speakers UI (when step 5 has files)

- **GET** `/api/pipeline/speakers/files`  
  Expect: list of media in "Videos 5 needs speaker identification".

- Open the unknown-speakers page in the web UI; select a file; load segments; play a segment; resolve as existing / new / placeholder.

- After resolving all segments for a file, the system **automatically** moves the file and paired folder through step 6 → 7 → 8 → Videos; no separate "Move to Videos" action required.

---

## 7. Status

- **GET** `/api/pipeline/status`  
  Expect: counts by step (e.g. how many files in step 1, step 5, Videos).
