# Tasks: Automatic Pipeline Processing (013)

**Input**: Design documents from `/specs/013-auto-pipeline-processing/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not requested in the feature specification; no test tasks included.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies).
- **[Story]**: User story label (US1, US2) for story-phase tasks only.
- Include exact file paths in descriptions.

## Path Conventions

- Web app (per plan): extend existing `backend/` at repository root.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Config for scan interval and auto-processing; extend existing app.

- [X] T001 Add pipeline auto-run config: scanIntervalSeconds (default 60) and autoProcessingEnabled (default true for 013) in voicinator.toml and voicinator.toml.example; load in backend (e.g. backend/src/models/masterConfigModel.py).
- [X] T002 [P] Document new keys in voicinator.toml.example (pipeline.scanIntervalSeconds, pipeline.autoProcessingEnabled).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Discovery across all steps, single-file one-step run, and selection priority. No user story work until this phase is complete.

- [X] T003 Implement discoverMediaInAllSteps: scan all step folders (1–8) under configured bases/channels; return list of items each with mediaPath, pairedFolderPath, channelName, basePath, stepFolderName, stepIndex (0–7) in backend/src/services/pipelineDiscoveryService.py.
- [X] T004 Implement runNextStepForOneFile(mediaPath, pairedFolderPath): determine current step from media path parent, run the step processor for the next step (reuse STEP_PROCESSORS and move logic), move file and paired folder to next step; return (success, error_message). Single file, one step only. In backend/src/services/pipelineRunService.py (or backend/src/services/pipelineAutoRunService.py).
- [X] T005 Implement selectOneFileByPriority(candidatesList): sort by stepIndex descending (higher step first), return first item or None. In backend/src/services/pipelineAutoRunService.py.

**Checkpoint**: Discovery all-steps, one-step run, and selection logic ready for auto-run loop.

---

## Phase 3: User Story 1 – Media processed without manual trigger (P1) – MVP

**Goal**: Background loop discovers files, selects one (highest step first), runs one step for that file, sleeps when idle. No API or button to start processing. Discovery within 1 minute.

**Independent Test**: Place one media file in "Videos 1 to be transcribed"; do not call any API. Within 1 minute verify the file is discovered and processing has started; file moves through steps over time. When no files in any step, system sleeps (no busy-wait).

- [X] T006 [US1] Implement the auto-run loop in backend/src/services/pipelineAutoRunService.py: loop (sleep scanInterval → discoverMediaInAllSteps → selectOneFileByPriority → if selected run runNextStepForOneFile for that file only → repeat). Enforce one file in progress at a time (lock or in-progress flag). Sleep full interval when no work (FR-008b).
- [X] T007 [US1] Start the auto-run loop in a background thread when the Flask app starts; ensure loop starts within one interval of process start. In backend/src/api/app.py or backend/__main__.py (wherever the app is created and run).
- [X] T008 [US1] Ensure first discovery cycle runs within one scan interval of startup (e.g. run first scan immediately then enter sleep-after-cycle loop) so FR-001a and FR-005 are satisfied.

**Checkpoint**: User Story 1 done – automatic processing runs; no manual trigger required.

---

## Phase 4: User Story 2 – Consistent behavior across all steps (P2)

**Goal**: Every step folder (1–8) uses the same rule: file presence triggers that step’s processing. No special case for step 1.

**Independent Test**: Place a file in step 1 and a file in step 4; verify step 4 file is processed first (priority), then step 1 file in a later cycle. Verify both steps use the same discovery and processor path.

- [X] T009 [US2] Verify in pipelineAutoRunService that all step folders (1–8) are discovered by discoverMediaInAllSteps and that runNextStepForOneFile is used for every selected file regardless of step (no special-case branch for step 1 only) in backend/src/services/pipelineAutoRunService.py.

**Checkpoint**: User Story 2 – uniform behavior across steps; higher step priority confirmed.

---

## Phase 5: Remove explicit run API

**Purpose**: No "run now" API when automatic processing is enabled (FR-009).

- [X] T010 When autoProcessingEnabled is true, remove or disable POST /api/pipeline/run: either do not register the route or return 410 Gone (or 404) with a message that processing is automatic. Keep GET /api/pipeline/config, GET /api/pipeline/discover, GET /api/pipeline/status. In backend/src/api/pipelineRoutes.py.

---

## Phase 6: Polish & Cross-Cutting

**Purpose**: Validation and documentation.

- [X] T011 Run quickstart.md: verify app start, place file in step 1, confirm discovery within 1 minute and no POST run required; verify POST /api/pipeline/run returns 410/404 when auto is enabled.
- [X] T012 Update STATUS.md with 013 status, auto-processing behavior, and new config keys (scanIntervalSeconds, autoProcessingEnabled).

---

## Dependencies & Execution Order

- **Phase 1–2**: Must complete before any user story.
- **Phase 3 (US1)**: Depends on Phase 2; MVP = auto-run loop and thread start.
- **Phase 4 (US2)**: Depends on Phase 3; verification that all steps use same path.
- **Phase 5**: Depends on Phase 3 (auto must be running); disable POST run.
- **Phase 6**: After Phase 5 or in parallel with Phase 5.

## Implementation Strategy

- **MVP first**: Phase 1 + 2 + 3 (US1) so that placing a file in a step folder causes automatic processing within 1 minute without any API call.
- **Incremental**: Add US2 verification, then remove run API, then polish.

## Parallel Opportunities

- T001 and T002 can be done in parallel (config load vs example doc).
- T003, T004, T005 are sequential (T004 may depend on T003 for discovery shape; T005 depends on T003 output).
