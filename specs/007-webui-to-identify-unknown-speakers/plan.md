# Implementation Plan: Web UI to Identify Unknown Speakers

**Branch**: `007-webui-to-identify-unknown-speakers` | **Date**: 2026-03-10 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/007-webui-to-identify-unknown-speakers/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add a new section to the existing Voicinator web UI that lists all media files in "Videos 5 needs speaker identification" across all channel folders. An "Unknown Speakers" link MUST appear on the left side of all existing pages so users can reach this section from anywhere. The user selects a video to process: the identification view shows the transcript in **transcript.txt style** (sections labeled by speaker and time); **play/pause and playback controls are fixed at the bottom** of the window so they do not scroll off. The user can **click any word** in the transcript to play audio starting at that word; word-level timing MUST come from **transcript_words.json** (GET transcript returns words with start/end from that file). Each section has the speaker name or label in front; **clicking the speaker's name** opens a **popup** to identify that speaker: scrollable list of existing speakers, a text field that narrows (filters) the list, **Enter to create a new speaker** when the typed name is unique, and an option to **skip/not-identify**. When the user chooses not to identify, a full speaker record is created with a globally unique placeholder name (e.g. Unidentified-1); passage(s) are added to that speaker's corpus and placeholders are treated like named speakers. When the system suggests an existing identification, the user can confirm or correct; on confirmation, passage(s) from the current video are added to that speaker's corpus. When all speakers are resolved, "Complete identification" is active; using it updates transcript files (backup then rewrite with speaker names), moves the media and paired folder to "Videos 6 speakers matched", and navigates back to the list. Videos with zero speakers are moved to step 6 immediately. Technical approach: extend backend `pipelineSpeakersRoutes` and `speakerResolver`; transcript endpoint already returns words with start/end from transcript_words.json; extend frontend `unknownSpeakersPage` with transcript.txt-style panel, bottom-fixed playback controls, **click-any-word** (use word start from transcript data), click-speaker-name → identify popup (list, filter, Enter-to-create, skip), and Complete flow; add "Unknown Speakers" to the left navigation on all pages.

## Technical Context

**Language/Version**: Python 3.11+ (backend), JavaScript (frontend; no framework)  
**Primary Dependencies**: Flask (backend), existing pipeline services (step3/step4 output: transcript_words.json, transcript.txt, segments.json), pathlib, JSON/file I/O  
**Storage**: Filesystem only—paired folders (transcript.txt, transcript_words.json, segments.json), speaker_resolutions.json (resolver), no database  
**Testing**: pytest (backend), manual/browser (frontend); contract tests for API  
**Target Platform**: Local Mac (M2); Flask serves API and static frontend  
**Project Type**: Web application (backend + frontend)  
**Performance Goals**: List and segment load within 5 seconds; click-to-play starts within ~500 ms. Implementation guidance; validation is manual unless a Phase 7 verification task is added.  
**Constraints**: Read/write only under configured pipeline base paths; transcript update must backup before overwrite  
**Scale/Scope**: Hundreds of videos per base; tens of segments per video; placeholder names globally unique (monotonic counter or equivalent); placeholder speakers are first-class (full record, corpus, media-appearance linkage)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution file (`.specify/memory/constitution.md`) is a template with no project-specific principles ratified. Apply standard conventions: small functions, multiple smaller files, coding standards per user rules and docs/CODING_STANDARDS.md; no unjustified complexity. No formal gates; proceed with plan.

## Project Structure

### Documentation (this feature)

```text
specs/007-webui-to-identify-unknown-speakers/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan)
├── data-model.md        # Phase 1 output (/speckit.plan)
├── quickstart.md        # Phase 1 output (/speckit.plan)
├── contracts/           # Phase 1 output (/speckit.plan)
│   └── 007-unknown-speakers-api.md   # 007 extensions to unknown-speakers API
└── tasks.md             # Phase 2 output (/speckit.tasks - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   └── pipelineSpeakersRoutes.py   # Extend: transcript GET, complete POST, zero-speaker handling
│   ├── models/
│   ├── services/
│   │   ├── pipelineDiscoveryService.py # Already discovers step-5 media; may add zero-speaker filter/move
│   │   ├── pipelineMoveService.py
│   │   └── pipeline/
│   │       ├── speakerResolver.py      # Extend: placeholder name generation (global unique), full speaker record + corpus for placeholder, suggested ID
│   │       └── step4_diarize.py        # segments.json
│   └── ...
└── tests/

frontend/
├── src/
│   ├── pages/
│   │   ├── unknownSpeakersPage.html    # Extend: transcript.txt-style panel, bottom-fixed controls, click-any-word, click-speaker-name popup, Complete button
│   │   └── unknownSpeakersPage.js
│   ├── services/
│   │   └── pipelineSpeakersApi.js      # Extend: transcript, play-at-time, complete, suggested ID
│   └── ...   # Shared layout/nav: add "Unknown Speakers" link on left for all pages
└── ...
```

**Structure Decision**: Existing Voicinator layout is backend (Flask + services) + frontend (HTML/JS). Feature 007 extends both: API and services for transcript (words with start/end from transcript_words.json), complete identification, placeholder names (full speaker record and corpus), and transcript rewrite; frontend: transcript.txt-style display, bottom-fixed play/pause, click-any-word (word start from transcript data), identify-by-click popup (list, filter, Enter-to-create, skip), Complete button, and "Unknown Speakers" in left nav on all pages.

### Contract traceability

**Contract**: [contracts/007-unknown-speakers-api.md](contracts/007-unknown-speakers-api.md). When the contract changes, update the implementation areas below and the tasks that cite each section.

| Contract section | Endpoint / behavior | Implementation area | Tasks |
|------------------|---------------------|---------------------|-------|
| §1 | GET files (zero-speaker handling) | pipelineSpeakersRoutes.py, pipelineDiscoveryService | T003, T005 |
| §2 | GET files/{id}/transcript | pipelineSpeakersRoutes.py | T008, T012 |
| §3 | GET files/{id}/play-at (or client seek) | pipelineSpeakersRoutes.py (optional), frontend currentTime | T010 |
| §4 | POST resolve (placeholder, suggested ID) | pipelineSpeakersRoutes.py, speakerResolver.py | T002, T004, T012, T013, T015 |
| §5 | POST files/{id}/complete | pipelineSpeakersRoutes.py, transcript backup/rewrite | T017, T018, T022, T023 |
| §6 | GET files/{id}/can-complete (optional) | pipelineSpeakersRoutes.py (optional) | T021 |

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

Not applicable; no violations.
