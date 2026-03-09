# Implementation Plan: Local Media Folder Pipeline

**Branch**: `002-media-folder-pipeline` | **Date**: 2026-03-07 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/002-media-folder-pipeline/spec.md`

## Summary

Media in "Videos 1 to be transcribed" is discovered under configured base folders; processed through fixed step folders (Videos 2 → … → Videos 8); media and paired folder move together. **Transcription**: Whisper Large-v3 (required). **Diarization**: NeMo Multi-Scale Diarization Decoder (MSDD); Pyannote is not used. Transcripts (word-level + human-readable per-speaker) go to the paired folder. Unknown speakers route to step 5; web UI lists files, plays segments, resolves identity; when all resolved, system automatically moves file through step 6 → 7 → 8 → Videos. Single run at a time; each run processes all discovered files; run/step logging to configurable sink. Extend existing backend/frontend; speaker DB interface with stub (local/file persistence) when DB absent.

## Technical Context

**Language/Version**: Python 3.11+ (per repo run.sh / requirements)  
**Primary Dependencies**: Flask (existing); **Whisper Large-v3** for transcription (openai-whisper or faster-whisper with large-v3 model); **NeMo Multi-Scale Diarization Decoder (MSDD)** for diarization (NVIDIA NeMo toolkit); path handling, TOML/JSON config; optional speaker DB client (interface; stub when absent). **Pyannote is not to be used.**  
**Storage**: Filesystem for media and paired folders; local storage or files for speaker-resolution stub until real DB exists.  
**Testing**: pytest (optional per spec); ruff for lint.  
**Target Platform**: Mac (M2); local.  
**Project Type**: Web application (extend existing backend + frontend).  
**Performance Goals**: Process all discovered media per run; single run at a time; sequential steps per file.  
**Constraints**: No Pyannote; transcription MUST use Whisper Large-v3; diarization MUST use NeMo MSDD. Configurable log sink (FR-017). No moving files outside defined folder structure.  
**Scale/Scope**: Multiple base folders and channel folders; one run at a time; each run processes all files in step 1.

## Constitution Check

*No project-specific constitution file; follow Voicinator development guidelines and 001 patterns.*

## Project Structure

### Documentation (this feature)

```text
specs/002-media-folder-pipeline/
├── plan.md              # This file
├── research.md          # Phase 0: Whisper Large-v3, NeMo MSDD, no Pyannote
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/           # Phase 1
└── tasks.md             # Phase 2 (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/          # Pipeline config, step plan
│   ├── services/        # pipeline, discovery, move, run; step 3 = Whisper Large-v3; step 4 = NeMo MSDD
│   └── api/             # pipeline routes, unknown-speakers routes
└── tests/

frontend/
├── src/
│   ├── components/      # Unknown-speakers list, segment player, resolve UI
│   ├── pages/
│   └── services/
└── (existing)
```

**Structure Decision**: Reuse 001 backend/frontend. Step 3 processor uses Whisper Large-v3; step 4 processor uses NeMo MSDD (not Pyannote).

## Complexity Tracking

*(None required.)*
