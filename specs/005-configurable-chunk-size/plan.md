# Implementation Plan: Configurable Chunk Size for Tuning

**Branch**: `005-configurable-chunk-size` | **Date**: 2026-03-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-configurable-chunk-size/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add a configurable chunk duration (default 30 seconds) for splitting long audio before transcription, so operators can tune the process without code changes. Configuration lives in `voicinator.toml` under `[pipeline]`; a documented min/max range is enforced; missing or invalid values fall back to 30 s. The pipeline will use this value where audio is split into segments (preprocessing before or during step 3 transcription).

## Technical Context

**Language/Version**: Python 3.11+ (per run.sh and requirements; 3.10–3.13 for NeMo)  
**Primary Dependencies**: Flask, faster-whisper (large-v3), NeMo MSDD (step 4), pydub/librosa for audio; TOML (tomllib/tomli) for config  
**Storage**: Filesystem only (paired folders, no DB)  
**Testing**: pytest (per workspace rules); ruff check  
**Target Platform**: Mac M2, local; Apple Silicon  
**Project Type**: Web service (Flask) + pipeline CLI-style steps  
**Performance Goals**: Pipeline docs: Whisper ~1× real-time; chunk size tuning for different accents/noise  
**Constraints**: Chunk duration within documented range (e.g. 10–120 s); default 30 s  
**Scale/Scope**: Single pipeline run at a time; config applied per run from voicinator.toml  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No project-specific constitution file (`.specify/memory/constitution.md` is template-only). Workspace rules apply: Python 3.11+, Flask, config file (TOML/JSON), filesystem-only, small functions, multiple smaller files. No violations identified for this feature.

## Project Structure

### Documentation (this feature)

```text
specs/005-configurable-chunk-size/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   └── masterConfigModel.py   # Add chunk duration load + validation
│   ├── services/
│   │   └── pipeline/
│   │       ├── step2_audio.py     # (unchanged; full extract)
│   │       └── step3_transcribe.py # Use chunk duration when chunking implemented
│   └── api/
│       └── pipelineRoutes.py      # GET /config: expose chunkDurationSeconds
tests/
├── unit/
└── integration/
```

**Structure Decision**: Existing Voicinator layout is retained. Config is centralized in `masterConfigModel`; pipeline steps and API remain under `backend/`. No new top-level packages.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

None.
