# Implementation Plan: Automatic Pipeline Processing

**Branch**: `013-auto-pipeline-processing` | **Date**: 2026-03-07 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/013-auto-pipeline-processing/spec.md`

## Summary

Pipeline processing is triggered automatically by file presence: no API call or "run" button. A background discovery loop scans all pipeline step folders (1–8) under configured bases/channels at least every 1 minute; when media is found, the system selects one file (highest step number first), runs that step’s processor for that file, then sleeps until the next scan. Only one media file is processed at a time. When no work exists, the system sleeps until the next scan. The explicit "run pipeline" API (e.g. POST /api/pipeline/run) is removed or disabled. Extends the existing 002 backend (discovery, move, step processors); adds a persistent worker/scheduler that invokes discovery and single-file processing.

## Technical Context

**Language/Version**: Python 3.11+ (same as repo and 002)  
**Primary Dependencies**: Flask (existing); same as 002 (faster-whisper, pipeline services). New: background loop (thread or scheduler) with configurable scan interval (e.g. 30–60 s to satisfy “within 1 minute” discovery).  
**Storage**: Filesystem only (no new storage); pipeline state is “which file is in which folder.”  
**Testing**: pytest (optional); ruff for lint. Manual verification per quickstart.  
**Target Platform**: Mac (M2); local (same as 002).  
**Project Type**: Web application — extend existing backend; no new frontend for this feature (optional: status/health for auto-run).  
**Performance Goals**: Discovery within 1 minute of file appearance or startup; one file in progress at a time; sleep when idle (no busy-wait).  
**Constraints**: Reuse 002 step processors and folder plan; no explicit run API; scan all step folders each cycle; higher step number has selection priority.  
**Scale/Scope**: Same as 002 (multiple bases/channels); one media file processed at a time globally.

## Constitution Check

*No project-specific constitution file; follow Voicinator development guidelines and 002 patterns.*

## Project Structure

### Documentation (this feature)

```text
specs/013-auto-pipeline-processing/
├── plan.md              # This file
├── research.md          # Phase 0: scan interval, threading/scheduler choice
├── data-model.md        # Phase 1: discovery cycle, selection, idle
├── quickstart.md        # Phase 1: verify auto-processing
├── contracts/           # Phase 1 (optional: internal worker contract)
└── tasks.md             # Phase 2 (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/          # (existing) pipeline config, step plan
│   ├── services/        # (existing) pipeline discovery, move, run; + auto-run worker/scheduler
│   └── api/             # (existing) pipeline routes; remove or disable POST /api/pipeline/run
└── tests/
```

**Structure Decision**: Extend 002 backend only. Add a single entry point (e.g. `pipelineAutoRunService` or background thread) that: (1) runs a loop with configurable scan interval, (2) calls discovery across all step folders, (3) selects one file (highest step first), (4) runs the appropriate step for that file (reuse existing step processors and move), (5) sleeps when no work. Remove or gate POST /api/pipeline/run so it is not exposed when auto-processing is enabled.

## Complexity Tracking

*(None.)*
