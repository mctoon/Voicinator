# Tasks: Local Media Folder Pipeline (002)

**Input**: Design documents from `/specs/002-media-folder-pipeline/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not requested in the feature specification; no test tasks included.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies).
- **[Story]**: User story label (US1–US5) for story-phase tasks only.
- Include exact file paths in descriptions.

## Path Conventions

- Web app (per plan): extend existing `backend/`, `frontend/` at repository root.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Pipeline config and step plan; extend existing app.

- [x] T001 [P] Add pipeline step plan (folder names and order per spec table) as constants or config in backend/src/models/pipelineStepPlan.py.
- [x] T002 Add pipeline config: base paths and optional step-5 override in voicinator.toml and voicinator.toml.example; load in backend (e.g. backend/src/models/masterConfigModel.py or new pipelineConfigModel.py).
- [X] T003 [P] Document pipeline dependencies: Whisper Large-v3 (transcription), NeMo MSDD (diarization); no Pyannote. Add to requirements.txt when implementing step 3/4 (optional stub-only MVP first).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Discovery and move-between-steps so pipeline can run. No user story work until this phase is complete.

- [x] T004 Implement pipeline discovery: list media files (and paired folder paths) in "Videos 1 to be transcribed" under all configured base paths in backend/src/services/pipelineDiscoveryService.py.
- [x] T005 Implement move-between-steps: given channel root, current step folder name, next step folder name, move primary media file and its paired folder (sidecar) to the next step folder; create next step folder if missing; reuse 001 move semantics (sidecar = folder named by media stem; sister files inside sidecar) in backend/src/services/pipelineMoveService.py (or extend moveService).
- [x] T006 Implement GET /api/pipeline/config returning basePaths, stepFolders, unknownSpeakersStepName, finalFolderName in backend/src/api/pipelineRoutes.py.
- [x] T007 Implement GET /api/pipeline/discover using pipeline discovery service in backend/src/api/pipelineRoutes.py.
- [x] T008 Register pipeline blueprint/routes in backend/src/api/app.py.

**Checkpoint**: Config and discover work; move-between-steps ready for orchestration.

---

## Phase 3: User Story 1 – Process media from configured folders (P1) – MVP

**Goal**: Run pipeline so media in step 1 is discovered and moved through step folders (2→3→4→5 or 6→7→8→Videos); step processors can be stubs that only move.

**Independent Test**: One base path, one channel, one media file in "Videos 1 to be transcribed"; run pipeline; verify file moves to step 2, then 3, 4, 5 (or through to Videos if no unknown speakers).

- [x] T009 [US1] Implement pipeline run orchestration: discover media in step 1; for each file, run step 2 then 3 then 4 then 5 (stub: each step moves file + paired folder to next step folder) in backend/src/services/pipelineRunService.py.
- [x] T010 [US1] Step 5 routing: if any speaker unknown, leave file in step 5; else move to step 6; stubs for steps 6–8 move to 7, 8, Videos in backend/src/services/pipelineRunService.py.
- [x] T011 [US1] Implement POST /api/pipeline/run: no per-run limit (process all discovered files); enforce single run at a time (reject e.g. 409 or queue until current completes); return processed, movedToStep5, movedToVideos, errors in backend/src/api/pipelineRoutes.py.
- [x] T012 [US1] Implement GET /api/pipeline/status returning counts by step (scan step folders under bases) in backend/src/api/pipelineRoutes.py.

**Checkpoint**: User Story 1 done – files move through steps; POST run and status work.

---

## Phase 4: User Story 2 – Sister files and paired folder (P1)

**Goal**: Paired folder (sidecar) holds media, sister files, and outputs; moves with media at every step.

**Independent Test**: Media + two sister files in step 1; run pipeline; verify one sidecar folder at each step and in Videos containing media, sister files, and (when implemented) transcript outputs.

- [x] T013 [US2] Ensure pipeline move-between-steps uses the same sidecar semantics as 001: create sidecar at destination if missing; move sister files and source paired contents into sidecar; move primary into step folder in backend/src/services/pipelineMoveService.py (or reuse moveService.moveFileAndPaired with appropriate paths).
- [x] T014 [US2] Ensure step processors (current and future) write outputs into the paired folder for the media file (contract only; implement when adding real steps).

**Checkpoint**: User Story 2 – paired folder and sister files move correctly through steps.

---

## Phase 5: User Story 3 – Transcript outputs (P1)

**Goal**: Word-level transcript (sub-second) and human-readable per-speaker TXT in paired folder.

**Independent Test**: Process one file through step 3 (transcription); verify paired folder contains word-level transcript and Otter-style TXT.

- [X] T015 [US3] Implement step 2 processor: audio extraction in backend/src/services/pipeline/step2_audio.py (or single pipelineSteps module).
- [x] T016 [US3] Implement step 3 processor: run Whisper Large-v3 (openai-whisper or faster-whisper with large-v3); write word-level transcript (JSON with word, start, end) to paired folder in backend/src/services/pipeline/step3_transcribe.py.  Do not stub, write the implementation!!!
- [x] T017 [US3] Write human-readable transcript (TXT, speaker labels + paragraph text) to paired folder from step 3 or 4 output in backend/src/services/pipeline/step3_transcribe.py or step4_diarize.py.  Do not stub, write the implementation!!!
- [x] T018 [US3] Integrate step 2 and step 3 into pipeline run service (replace stubs) in backend/src/services/pipelineRunService.py.  Do not stub, write the implementation!!!

**Checkpoint**: User Story 3 – transcription produces both transcript files in paired folder.

---

## Phase 6: User Story 4 – Unknown speakers to step 5 (P2)

**Goal**: When any speaker is unknown after diarization, move file (and paired folder) to "Videos 5 needs speaker identification", not to Videos.

**Independent Test**: Process file that yields at least one unknown speaker; verify it lands in step 5 folder.

- [x] T019 [US4] Implement step 4 processor: diarization using NeMo Multi-Scale Diarization Decoder (MSDD); output segments/RTTM to paired folder in backend/src/services/pipeline/step4_diarize.py. Do not use Pyannote.  Do not stub, write the implementation!!!
- [x] T020 [US4] Implement step 5 processor: speaker identification; call speaker resolver interface; if any unknown, move to step 5 folder and stop; else move to step 6 in backend/src/services/pipeline/step5_speaker_id.py.  Do not stub, write the implementation!!!
- [x] T021 [US4] Define speaker resolver interface (list speakers, match segment, add sample, create speaker, placeholder) and stub implementation (all unknown) in backend/src/services/speakerResolver.py or backend/src/services/pipeline/speakerResolver.py.  Do not stub, write the implementation!!!
- [x] T022 [US4] Integrate step 4 and step 5 into pipeline run service in backend/src/services/pipelineRunService.py.  Do not stub, write the implementation!!!

**Checkpoint**: User Story 4 – unknown speakers route to step 5; others progress to 6→7→8→Videos.

---

## Phase 7: User Story 5 – Web UI: Resolve unknown speakers (P2)

**Goal**: List media in step 5; play speaker segments; resolve as existing/new/placeholder; when all resolved, system automatically moves file through step 6→7→8→Videos (no explicit button).

**Independent Test**: Open unknown-speakers page; list files; play segment; resolve one; after all resolved, verify file is automatically moved to Videos.

- [x] T023 [US5] Implement GET /api/pipeline/speakers/files listing media in unknown-speakers step folder in backend/src/api/pipelineSpeakersRoutes.py.
- [x] T024 [US5] Implement GET /api/pipeline/speakers/files/{mediaId}/segments returning segments from RTTM/paired folder in backend/src/api/pipelineSpeakersRoutes.py.
- [x] T025 [US5] Implement GET /api/pipeline/speakers/segment-audio (or equivalent) to stream segment audio for playback in backend/src/api/pipelineSpeakersRoutes.py or mediaRoutes.
- [x] T026 [US5] Implement POST /api/pipeline/speakers/resolve and GET /api/pipeline/speakers/speakers (list) in backend/src/api/pipelineSpeakersRoutes.py.
- [x] T027 [US5] When all segments for a file are resolved, automatically move media and paired folder through step 6→7→8→Videos (trigger on last resolve or on commit); optional POST /api/pipeline/speakers/files/{mediaId}/move-to-videos for trigger/retry in backend/src/api/pipelineSpeakersRoutes.py.
- [x] T028 [US5] Register pipeline speakers routes in backend/src/api/app.py.
- [x] T029 [US5] Add unknown-speakers page and components: list files, segments, segment player, resolve (existing/new/placeholder) in frontend/src/pages/unknownSpeakersPage.html and frontend/src/components/.
- [x] T030 [US5] Wire frontend to pipeline speakers API (list, segments, segment audio, resolve); automatic move when all resolved (no separate move-to-videos button) in frontend/src/services/ and pages.

**Checkpoint**: User Story 5 – web UI for resolving unknown speakers; automatic move to Videos when all resolved.

---

## Phase 8: Polish & Cross-Cutting

**Purpose**: Steps 6–8 stubs, config override for step 5 name, logging, quickstart validation.

- [X] T031 Implement step 6–8 processors as stubs (move to 7, 8, Videos) or real summarization/export if in scope in backend/src/services/pipeline/.
- [X] T032 Support config override for unknown-speakers step folder name in pipeline config and step plan.
- [X] T033 Pipeline run and step logging per FR-017: log run start/end and each step outcome (success or failure) per file to configurable sink (file or stdout) in backend/src/services/pipelineRunService.py and pipelineMoveService.py.
- [X] T034 Run quickstart.md: verify config, discover, run, status, and (if implemented) unknown-speakers UI.
- [X] T035 Update STATUS.md with 002 status, run instructions, and any new config keys.

---

## Dependencies & Execution Order

- **Phase 1–2**: Must complete before any user story.
- **Phase 3 (US1)**: Depends on Phase 2; MVP = discovery + run with stub steps.
- **Phase 4 (US2)**: Depends on Phase 3; ensures move semantics match 001.
- **Phase 5 (US3)**: Depends on Phase 4; real step 2/3 (audio, transcribe).
- **Phase 6 (US4)**: Depends on Phase 5; step 4/5 (diarize, speaker id).
- **Phase 7 (US5)**: Depends on Phase 6; API and UI for speaker resolution.
- **Phase 8**: After all stories or in parallel with later stories.

## Implementation Strategy

- **MVP first**: Phase 1 + 2 + 3 (US1) so that "run pipeline" discovers and moves files through steps with stub processors. Validate with one file.
- **Incremental**: Add US2 (move semantics), then US3 (transcripts), then US4 (unknown speakers routing), then US5 (web UI).
