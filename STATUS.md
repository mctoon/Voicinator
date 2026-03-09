# Voicinator – Project status

**Last updated**: 2026-03-08

## Current focus: 002 Media Folder Pipeline

Active development is on **002 Media Folder Pipeline** (transcript outputs, step 2/3 processors, diarization, unknown-speakers UI). For speckit/implement and check-prerequisites, use branch `002-media-folder-pipeline` or set `SPECIFY_FEATURE=002-media-folder-pipeline`.

## Overview

Voicinator is a local, quality-first voice fingerprinting and transcription stack for Mac M2. This repo holds docs, specs, and feature implementations: **001-inbox-queue-web-ui**, **002-media-folder-pipeline**, **013-auto-pipeline-processing**.

## 001 Inbox-to-Queue Web UI

**Status**: Implemented (all 45 tasks from `specs/001-inbox-queue-web-ui/tasks.md` completed). Channel eligibility requires only "Videos not transcribed"; queue folder is created on move if missing. When moving a media file, the sidecar folder (same base name as the primary) is created at the queue if it does not exist; sister files (same prefix, e.g. .info.json, -thumb.jpg) and any source paired folder contents are moved into the sidecar; the primary stays in the queue directory.

- **Run**: From repo root, `./run.sh` (creates/activates `.venv`, installs deps, starts Flask). Port and bootstrap options from **master config** `voicinator.toml` at repo base (default port 8027). Open http://localhost:8027/ (or the port in `voicinator.toml`).
- **Master config**: `voicinator.toml` at repo root: `[server] port`, optional `[server] logPath`, optional `[inbox] configPath`. See `voicinator.toml.example`. Log file defaults to `logs/voicinator.log`; all requests and media paths are logged there.
- **Inbox config**: TOML or JSON; path from master config `[inbox].configPath`, or `INBOX_CONFIG` env, or default `inbox_queue_config.toml`. See `inbox_queue_config.toml.example`.
- **Stack**: Python 3.11+, Flask, vanilla JS frontend; no database; filesystem-only.
- **Features**: Tabs per path, channel list (with “Move 3”, “Move all”, Explore), explore view with file list and “Queue selected”, media preview subpanel (play/pause, volume, scrubber, jump), two-path tabs (source → destination queue).

## 002 Media Folder Pipeline

**Status**: Implemented (all tasks in `specs/002-media-folder-pipeline/tasks.md` completed). **Step 2**: audio extraction (ffmpeg → mono 16 kHz WAV in paired folder). **Step 3**: Whisper Large-v3 via faster-whisper; word-level JSON and human-readable TXT in paired folder. **Step 4**: NeMo MSDD diarization (EncDecDiarLabelModel); segments.json and RTTM in paired folder (requires `nemo_toolkit[asr]` and model). **Step 5**: speaker resolver interface with file-based persistence; matchSegment uses stored resolutions; files with any unknown speaker stay in step 5. **Steps 6–8**: stubs (move only). **User Story 5**: unknown-speakers API and web UI; list files in step 5, segments, segment audio playback, resolve (existing/new/placeholder); when all segments resolved, backend auto-moves file through step 6→7→8→Videos.

- **API**: `GET /api/pipeline/config`, `GET /api/pipeline/discover`, `POST /api/pipeline/run`, `GET /api/pipeline/status`; speakers: `GET /api/pipeline/speakers/files`, `GET /api/pipeline/speakers/files/{mediaId}/segments`, `GET /api/pipeline/speakers/segment-audio`, `POST /api/pipeline/speakers/resolve`, `GET /api/pipeline/speakers/speakers`, `POST /api/pipeline/speakers/files/{mediaId}/move-to-videos`.
- **UI**: `/unknownSpeakersPage.html` – list files, select file → segments, play segment, resolve speaker; automatic move when all resolved.
- **Config**: Optional `[pipeline] basePaths` and `unknownSpeakersStepName` in `voicinator.toml`; if basePaths empty, pipeline uses inbox tab paths. Speaker resolutions stored in `data/speaker_resolutions.json` (stub until real DB).
- **Deps**: `faster-whisper` (step 3); optional `nemo_toolkit[asr]` for step 4 (NeMo MSDD).

## 013 Automatic Pipeline Processing

**Status**: Implemented. Pipeline processing is automatic: no API call or run button. A background thread scans all step folders (1–8) at a configurable interval (default 60 s); selects one file (highest step number first); runs one step for that file; sleeps when no work. One file in progress at a time. First discovery runs immediately on startup, then every `scanIntervalSeconds`.

- **Config**: `[pipeline] scanIntervalSeconds` (default 60), `autoProcessingEnabled` (default true). See `voicinator.toml.example`.
- **API**: When auto-processing is enabled, `POST /api/pipeline/run` returns **410 Gone** with a message that processing is automatic. `GET /api/pipeline/config`, `GET /api/pipeline/discover`, `GET /api/pipeline/status` unchanged (read-only).
- **Quickstart**: `./run.sh`; place a file in "Videos 1 to be transcribed"; within 1 minute it is discovered and processed. No POST run required.

## Requirements (from prompts)

- 001-inbox-queue-web-ui: Local web UI to queue media from “Videos not transcribed” to “Videos 1 to be transcribed”; tabbed UI; optional two paths per tab (source/destination); media subpanel; pagination/virtualization; run.sh + requirements.txt; Flask; config file (TOML/JSON).
- 002-media-folder-pipeline: Process media from "Videos 1 to be transcribed" through step folders; sister files in paired folder; word-level and human-readable transcripts; unknown speakers to step 5; web UI to resolve speakers.
- 013-auto-pipeline-processing: Automatic pipeline processing: background discovery loop (all steps 1–8), one file at a time, highest step first; configurable scan interval (default 60 s); no POST run API when auto enabled.

## Issues / notes

- None currently. Manual verification: run `./run.sh`, open UI, confirm tabs (if config exists), channels, move 3, explore, media subpanel per quickstart.md.
