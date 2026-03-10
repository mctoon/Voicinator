# Implementation Plan: Pipeline Summarize (Web UI config, LLMs, voicinator.toml)

**Branch**: `006-pipeline-summarize` | **Date**: 2026-03-09 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/006-pipeline-summarize/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add a configurable summarization step at the end of the pipeline (step 6 → "Videos 7 summarization done"). Summarization configuration is done in the web UI and persisted in `voicinator.toml`. The web UI defines reusable LLM definitions (local Ollama or remote with URL/API key); each summarization part selects an LLM from a dropdown and has a name and LLM instructions. Order of summarization parts in the UI determines order in the output file; the UI provides up/down reorder controls.

## Technical Context

**Language/Version**: Python 3.11+ (per run.sh; 3.10–3.13 for NeMo)  
**Primary Dependencies**: Flask, tomllib/tomli for voicinator.toml; existing pipeline services (step6_summarize currently stub)  
**Storage**: Filesystem only; config in repo-root `voicinator.toml` (no database)  
**Testing**: pytest (per project conventions); ruff check  
**Target Platform**: Mac M2, local/server (Flask web app)  
**Project Type**: Web application (backend Flask + frontend HTML/JS)  
**Performance Goals**: Summarization runs after transcript is ready; LLM latency depends on chosen model (Ollama local vs remote)  
**Constraints**: Config must be editable via web UI and round-trip to voicinator.toml; order of summarization parts preserved  
**Scale/Scope**: One config file; small set of LLM definitions and summarization parts; pipeline processes one item at a time through step 6

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution file (`.specify/memory/constitution.md`) is a template with no project-specific gates. Apply standard conventions: small functions, multiple smaller files, coding standards per user rules; no unjustified complexity.

## Project Structure

### Documentation (this feature)

```text
specs/006-pipeline-summarize/
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
│   ├── api/             # New or extended: routes for LLM config, summarization config (read/write voicinator.toml)
│   ├── models/          # Extend masterConfigModel for [llms], [pipeline.summarizations]; optional summarizationConfigModel
│   └── services/
│       └── pipeline/
│           └── step6_summarize.py   # Replace stub: read config, call selected LLM per part, write summary to step 6 folder
frontend/
└── src/
    ├── pages/           # New or extended: summarization config page (LLMs list, summarization parts list with reorder)
    └── services/       # API client for config endpoints
tests/
├── unit/
└── integration/
```

**Structure Decision**: Single backend + frontend (existing). New API routes and UI for LLM and summarization config; step6_summarize implements the pipeline step using that config. Config persisted in existing `voicinator.toml`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | — | — |
