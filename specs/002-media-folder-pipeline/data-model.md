# Data Model: 002 Media Folder Pipeline

Entities and flows for the local media folder pipeline. No database required for pipeline state; filesystem is source of truth.

---

## Entities

### Base folder (config)

- **Base folder**: Configured root path. Under it: `[Channel Name]/Videos 1 to be transcribed/`, etc.
- **Channel folder**: Directory under a base, named e.g. after a YouTube channel. Contains step folders and final `Videos`.

### Step folder (filesystem)

- **Step folder**: One of the fixed names from the Processing folder plan (spec):  
  `Videos 1 to be transcribed`, `Videos 2 audio extracted`, … , `Videos 8 export ready`, `Videos`.
- Step order: 1 → 2 → 3 → 4 → 5. At 5: if any unknown speaker → stay in 5; else → 6 → 7 → 8 → `Videos`.

### Media file and paired folder

- **Media file**: Primary audio/video file in a step folder. Identified by path; has a stem (base name).
- **Paired folder**: Directory with the same base name as the media file (stem). Holds the media file, sister files, and all generated outputs (transcripts, RTTM, etc.). Moves with the media between steps.
- **Sister file**: File in the same directory (or paired folder) with same stem, different extension/suffix. Treated as part of the same unit; all live in the paired folder.

### Pipeline run (in-memory / log)

- **Discovery**: List of `(base_path, channel_name, step_folder, media_path, paired_folder_path)` for each media file in "Videos 1 to be transcribed". Each run processes all discovered files (no per-run limit). Only one run executes at a time; further run requests are rejected or queued until the current run completes.
- **Step result**: For each file, after a step: success → move media + paired folder to next step; failure → leave in place, log error. Run start, run end, and each step outcome are logged to a configurable sink (FR-017).

### Transcript outputs (files in paired folder)

- **Word-level transcript**: Structured (e.g. JSON): `[{ "word": "...", "start": 0.0, "end": 0.5 }, ...]`. Sub-second precision.
- **Human-readable transcript**: Plain TXT; speaker labels at paragraph level; blocks of text per speaker (Otter-style).

### Speaker and segments (for unknown-speakers UI)

- **Speaker**: Identity or placeholder. May be: existing (in speaker DB), new (name provided), unknown (placeholder name). Referenced by segment.
- **Segment**: Time range (start, end) and optional speaker id/label. From diarization output (e.g. RTTM). Used for playback and resolution in UI.

### Speaker DB interface (adapter)

- **Operations**: list speakers; match segment → speaker or unknown; add sample to speaker; create new speaker; create placeholder. Implementation can be stub (all unknown) until real DB exists.

---

## Processing flow

1. **Config**: Load base paths (and optional step-5 override).
2. **Discover**: For each base path, scan `[base]/[channel]/Videos 1 to be transcribed/` for media files; for each, resolve paired folder (same stem); collect list.
3. **For each media file** (in discovery order or by channel):
   - Ensure media + sister files are in paired folder (create paired folder if missing; move sister files in per 001 behavior).
   - **Step 2**: Audio extraction → write to paired folder; move media + paired folder to "Videos 2 audio extracted".
   - **Step 3**: Transcription → word-level + human-readable in paired folder; move to "Videos 3 transcribed".
   - **Step 4**: Diarization → segments/RTTM in paired folder; move to "Videos 4 diarized".
   - **Step 5**: Speaker identification → match segments to speakers; if any unknown → move to "Videos 5 needs speaker identification" and stop for that file; else move to "Videos 6 speakers matched".
   - **Step 6–8**: Summarization → export → move to "Videos 8 export ready" then to "Videos".
4. **Unknown-speakers UI**: List media in "Videos 5 needs speaker identification"; for each, load segments; user plays segment, resolves (existing/new/placeholder). When all speakers for a file are resolved, the system automatically moves the media and paired folder to the next step in the pipeline (step 6 → 7 → 8 → Videos); no explicit "Move to Videos" user action is required.

---

## Validation rules

- Do not move files outside `[base]/[channel]/` or to folder names not in the step plan.
- On step failure: do not move media or paired folder to next step; log and continue with next file or next run.
- Paired folder always has same name as media stem; always move together.
- Word-level transcript: `start`/`end` floats; at least one decimal place.
