# Tasks: Pipeline Summarize (006)

**Input**: Design documents from `/specs/006-pipeline-summarize/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not requested in spec; no test tasks included.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Backend: `backend/src/` (api/, models/, services/pipeline/)
- Frontend: `frontend/src/` (pages/, services/)
- Config: repo root `voicinator.toml`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add dependency for writing TOML; no new project structure.

- [x] T001 Add tomli_w to requirements.txt for writing voicinator.toml (per research.md)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Config load/write and GET API so step 6 and UI can read llms and summarizations. No user story work until this phase is complete.

- [x] T002 [P] Extend masterConfigModel to load [[llms]] and pipeline summarizations from voicinator.toml in backend/src/models/masterConfigModel.py
- [x] T003 Implement write path for voicinator.toml: read full config, merge llms and pipeline.summarizations, write with tomli_w to temp file then rename (atomic) in backend/src/models/ or new backend/src/services/summarizationConfigService.py
- [x] T004 Extend GET /api/pipeline/config to include llms and summarizations in backend/src/api/pipelineRoutes.py (and ensure masterConfigModel getters are used)

**Checkpoint**: Config can be read and written; GET /api/pipeline/config returns llms and summarizations.

---

## Phase 3: User Story 1 - Summaries as Final Pipeline Output (Priority: P1) — MVP

**Goal**: Step 6 produces a summary file in "Videos 7 summarization done" from the transcript using configured parts and LLMs.

**Independent Test**: Run pipeline on a file through to step 6; confirm a summary file appears in the step-6 folder and reflects transcript content.

- [x] T005 [P] [US1] Implement LLM client (Ollama + OpenAI-compatible remote) in backend/src/services/pipeline/llmClient.py
- [x] T006 [US1] Implement step6_summarize in backend/src/services/pipeline/step6_summarize.py: load transcript, load config (llms + summarizations), for each part resolve LLM and call with instructions + transcript, concatenate results, write one summary file to step 6 folder
- [x] T007 [US1] Handle edge cases in step6_summarize: empty/zero summarizations skip or minimal output; empty transcript skip or placeholder; LLM unavailable or error fail clearly (per spec edge cases)

**Checkpoint**: User Story 1 is independently testable; pipeline produces summary in "Videos 7 summarization done".

---

## Phase 4: User Story 2 - Configurable Summarization Model (Priority: P2)

**Goal**: Operator can define LLMs (Ollama or remote) and select which LLM each summarization part uses via config; config persisted in voicinator.toml.

**Independent Test**: Define two LLMs in UI; assign one to a part; run pipeline and confirm that model is used. Change assignment; run again and confirm new model is used.

- [x] T008 [US2] Add PUT /api/pipeline/summarization-config in backend/src/api/pipelineRoutes.py (or new route module): validate body (llms + summarizations), call write service, return 200 or 400/500 per contracts/summarization-config-api.md
- [x] T009 [US2] Create summarization config page or section in frontend: list LLMs (name, type, baseUrl; add/edit/delete), and for each summarization part show LLM dropdown (from llms) in frontend/src/pages/ (e.g. summarizationConfigPage.html + .js)
- [x] T010 [US2] Add API client for GET /api/pipeline/config and PUT /api/pipeline/summarization-config in frontend/src/services/ (e.g. pipelineConfigApi.js or extend existing)

**Checkpoint**: User Story 2 testable; operator can change LLM per part and see effect on next run.

---

## Phase 5: User Story 3 - Configurable Summarization Parts and Instructions (Priority: P2)

**Goal**: Operator can add/remove/reorder summarization parts and edit name and LLM instructions per part; order in UI = order in file; five default parts available when none configured.

**Independent Test**: Add a part, remove a part, edit instructions, reorder with up/down; save; run pipeline and confirm summary reflects configured parts and order.

- [x] T011 [US3] Add up/down reorder controls for summarization parts in frontend; on save send full ordered list to PUT /api/pipeline/summarization-config in frontend/src/pages/ (summarization config page)
- [x] T012 [US3] When no summarizations in config, return or apply five default summarization parts (per spec "Initial summarization sections") in backend (masterConfigModel or summarizationConfigService) so new/reset installations have defaults

**Checkpoint**: User Stories 1–3 complete; operators can fully configure parts and instructions and reorder.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Security, docs, and validation.

- [x] T013 [P] Mask or omit apiKey in GET /api/pipeline/config response (per contract) in backend/src/api/pipelineRoutes.py or masterConfigModel
- [x] T014 Add route/link to summarization config page from main app (e.g. app.py route and nav) in backend/src/api/app.py and frontend
- [x] T015 Document summarization model and summary folder location (FR-004) in docs/ or quickstart.md
- [ ] T016 Run quickstart.md validation: manual check that config UI and step 6 produce expected summary

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: No dependencies.
- **Phase 2**: Depends on Phase 1 (tomli_w). Blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2 (config load; step 6 needs llms + summarizations).
- **Phase 4 (US2)**: Depends on Phase 2 (PUT and UI need config read/write).
- **Phase 5 (US3)**: Depends on Phase 4 (UI reorder and defaults build on config UI).
- **Phase 6**: Depends on Phases 3–5.

### User Story Dependencies

- **US1 (P1)**: After Phase 2; no dependency on US2/US3 (step 6 can run with config from file or defaults).
- **US2 (P2)**: After Phase 2; provides UI and API for LLM config.
- **US3 (P2)**: After US2; adds reorder and default parts.

### Parallel Opportunities

- T002 and T003 can be done in parallel (different concerns: load vs write).
- T005 (LLM client) is parallel within Phase 3.
- T013 (mask apiKey) is parallel in Phase 6.

---

## Parallel Example: Phase 2

```text
T002: Extend masterConfigModel to load llms and summarizations
T003: Implement write path (tomli_w, atomic) — can start after T001
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 (T001) → Phase 2 (T002–T004).
2. Phase 3 (T005–T007): LLM client + step6_summarize + edge cases.
3. Stop and validate: run pipeline through step 6; confirm summary file in "Videos 7 summarization done".

### Incremental Delivery

1. MVP (above) → summaries work with config from file (or defaults if implemented early).
2. Phase 4 → operators can define LLMs and assign per part in UI.
3. Phase 5 → operators can add/remove/reorder parts and edit instructions.
4. Phase 6 → polish and docs.

### Defaults

- T012 (five default parts) can be implemented in Phase 2 or Phase 5; Phase 5 keeps "config UI" work together.
