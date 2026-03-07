# Implementation Plan: Inbox-to-Queue Web UI

**Branch**: `001-inbox-queue-web-ui` | **Date**: 2026-03-07 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/001-inbox-queue-web-ui/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Provide a local-only web UI so an operator can see all YouTube channel folders (from configured base paths), queue media from "Videos not transcribed" (inbox) into "Videos 1 to be transcribed" (queue) via "move 3", "move all", or explore-and-cherry-pick. The UI is tabbed per path (with optional tab names), supports one or two sister paths per tab (source/destination), and includes a media sub window for preview when viewing channel media. Lists use virtualization or pagination for scale (hundreds of channels, thousands of files). Technical approach: Python backend (config, filesystem scan, atomic move, logging) and a frontend (tabs, lists, media viewer) served from the same app; see research.md for stack choices.

## Technical Context

**Language/Version**: Python 3.x (e.g. 3.11+); version documented in run.sh and requirements.txt  
**Primary Dependencies**: See research.md; backend: Flask or FastAPI for API and static/template serving; frontend: HTML/CSS/JS (or light framework per research); libraries for path handling, config (e.g. TOML/JSON), logging  
**Storage**: Config file (paths, tab names, one or two paths per tab); no database; filesystem only for channel folders and file moves  
**Testing**: pytest for backend (config load, scan, move logic); optional frontend/contract tests for API  
**Target Platform**: macOS (M2); localhost; single operator; no authentication  
**Project Type**: Web application (backend API + frontend UI)  
**Performance Goals**: List and tab switch responsive; move operations complete without blocking UI; virtualization/pagination keeps UI usable with hundreds of channels and thousands of files  
**Constraints**: Local-only; config file or app-level settings for paths; move must be atomic or idempotent to avoid duplicate moves; paired folder moves with media file  
**Coding standards**: [docs/CODING_STANDARDS.md](../../docs/CODING_STANDARDS.md) — camelCase and Hungarian notation; table/column naming if any DB later; Allman braces; small functions/files; run.sh + requirements.txt  
**Scale/Scope**: Hundreds of channel folders; thousands of media files per list; virtualization or pagination required for channel list and per-channel file list

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution file (`.specify/memory/constitution.md`) is a template and not yet ratified; no formal gates are enforced. Align with project conventions: clear interfaces (API for list/move), testable backend, logging for move actions and failures.

## Project Structure

### Documentation (this feature)

```text
specs/001-inbox-queue-web-ui/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (inbox-queue API)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
run.sh                   # Entry point: venv, install from requirements.txt, run web app; Control-C stops
requirements.txt         # Python dependencies

backend/
├── src/
│   ├── models/          # Config, path/tab, channel/media DTOs (no DB)
│   ├── services/        # Config load, channel scan, file move, logging
│   └── api/             # HTTP endpoints for tabs, channels, files, move actions
└── tests/
    ├── contract/        # Optional API contract tests
    ├── integration/     # Config + filesystem integration tests
    └── unit/            # Service and model unit tests

frontend/
├── src/
│   ├── components/      # Tabs, channel list, file list, media subpanel, buttons
│   ├── pages/           # Main inbox-queue view, explore view
│   └── services/        # API client for backend
└── tests/               # Optional frontend tests
```

**Structure Decision**: Web application with separate backend and frontend under repo root. Backend serves API and static assets (or a dev server for frontend during development). Single entry point `run.sh` sets up venv and runs the app. Media subpanel behavior aligns with spec 010-media-viewer-subpanel (play/pause, volume, scrubber, jump forward/back).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

None at this time.
