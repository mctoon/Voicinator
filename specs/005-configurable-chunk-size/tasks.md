# Tasks: Configurable Chunk Size for Tuning

**Input**: Design documents from `/specs/005-configurable-chunk-size/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story. No separate test phase (tests not explicitly requested in spec).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 = Tune chunk size (P1), US2 = Safe and documented bounds (P2)

## Path Conventions

- **Backend**: `backend/src/` (models, api, services)
- **Tests**: `tests/` at repository root
- **Config**: `voicinator.toml` at repo root

---

## Phase 1: Foundational (Blocking)

**Purpose**: Config load and validation that both user stories depend on.

- [x] **T001** [US1][US2] Add chunk duration to pipeline config in `backend/src/models/masterConfigModel.py`: define `CHUNK_DURATION_MIN` (10), `CHUNK_DURATION_MAX` (120), `CHUNK_DURATION_DEFAULT` (30). In `loadMasterConfig()`, read `[pipeline].chunkDurationSeconds`; validate range 10–120; if missing, non-numeric, zero, negative, or out of range, use 30 and set a flag for “defaulted.” Return effective int and whether defaulted in pipeline dict (or add getter that computes effective value + defaulted).
- [x] **T002** [US1][US2] Add `getPipelineChunkDurationSeconds()` and `getPipelineChunkDurationDefaulted()` (or single getter returning tuple) in `backend/src/models/masterConfigModel.py`. Ensure invalid/out-of-range values log a warning and return default 30 with defaulted=True.

**Checkpoint**: Config can be read and validated; getters available for API and future step 3.

---

## Phase 2: User Story 1 – Tune Chunk Size for Different Audio (Priority: P1)

**Goal**: Operator can set chunk duration via config and see it take effect without code changes; default 30 when not set.

**Independent Test**: Set `chunkDurationSeconds` in voicinator.toml; call GET /api/pipeline/config; confirm response includes new value. Omit key; confirm 30 and defaulted indicator.

- [x] **T003** [US1] Extend GET `/api/pipeline/config` in `backend/src/api/pipelineRoutes.py`: include `chunkDurationSeconds` (int) and `chunkDurationDefaulted` (bool) in JSON response per `specs/005-configurable-chunk-size/contracts/pipeline-config-005.md`.
- [x] **T004** [P] [US1] Ensure `specs/005-configurable-chunk-size/quickstart.md` documents how to set `chunkDurationSeconds` in voicinator.toml and how to check effective value via GET /config (already drafted; verify and adjust if needed).

**Checkpoint**: US1 deliverable—configurable chunk duration via config and API; default 30 when absent.

---

## Phase 3: User Story 2 – Safe and Documented Bounds (Priority: P2)

**Goal**: Only values in 10–120 are used; out-of-range or invalid values are rejected with warning and fallback to 30; bounds are documented.

**Independent Test**: Set chunk duration below 10 and above 120; confirm system uses 30, logs warning, and GET /config returns `chunkDurationDefaulted: true`. Set valid value in range; confirm used and not defaulted.

- [x] **T005** [US2] Confirm validation in T001/T002 logs a clear warning when value is missing, invalid, or out of range (10–120), and that GET /config returns `chunkDurationDefaulted: true` in those cases.
- [x] **T006** [US2] Document supported range (10–120 seconds) and default (30) in `specs/005-configurable-chunk-size/quickstart.md` and in docstrings or inline comments where `getPipelineChunkDurationSeconds` / constants are defined in `backend/src/models/masterConfigModel.py`.

**Checkpoint**: US2 deliverable—range enforced, documented, and visible to operators via API and docs.

---

## Phase 4: Polish & Cross-Cutting

- [x] **T007** Run quickstart validation: follow steps in `specs/005-configurable-chunk-size/quickstart.md` (edit voicinator.toml, restart or reload, call GET /api/pipeline/config) and confirm behavior.
- [x] **T008** If pipeline docs (e.g. `docs/03-pipeline.md`) mention chunk size or 30 s, add a sentence that chunk duration is configurable via voicinator.toml `[pipeline].chunkDurationSeconds` (10–120 s, default 30).

---

## Dependencies & Execution Order

### Phase order

1. **Phase 1 (Foundational)** must be done first: T001, T002.
2. **Phase 2 (US1)**: T003, T004 — after Phase 1.
3. **Phase 3 (US2)**: T005, T006 — after Phase 1 (can overlap with Phase 2; T005 is verification of T001/T002).
4. **Phase 4 (Polish)**: T007, T008 — after Phases 2 and 3.

### Within phases

- T001 and T002: implement getters and validation in `masterConfigModel.py` (T002 depends on T001 if you split “load” vs “getter”).
- T003: single file change in `pipelineRoutes.py`.
- T004 and T006: docs only; can run in parallel with implementation.
- T007: manual or scripted check of quickstart.

### Optional later work (not in this task list)

- **Explicit chunking**: Research chose Option A (config + API only). If later implementing Option B (split long audio into chunks of `chunkDurationSeconds`, transcribe each, merge), add a new task that uses `getPipelineChunkDurationSeconds()` in or before step 3.

---

## Notes

- No new database or auth; no separate “Setup” phase beyond existing repo.
- Spec does not require tests to be written first; no test tasks included.
- Commit after each task or logical group; validate GET /config after T003.
