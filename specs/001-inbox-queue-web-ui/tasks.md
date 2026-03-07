# Tasks: Inbox-to-Queue Web UI

**Input**: Design documents from `/specs/001-inbox-queue-web-ui/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not requested in the feature specification; no test tasks included. Add contract or unit tests in a later pass if desired.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently.

## Format: `[ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks).
- **[Story]**: User story label (US1–US5) for story-phase tasks only.
- Include exact file paths in descriptions.

## Path Conventions

- **Web app** (per plan.md): `backend/`, `frontend/`, `run.sh`, `requirements.txt` at repository root.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure.

- [x] T001 Create project structure per plan: backend/src/models, backend/src/services, backend/src/api, backend/tests, frontend/src/components, frontend/src/pages, frontend/src/services at repo root.
- [x] T002 Create run.sh at repo root that creates/activates venv and installs from requirements.txt, then starts the web app; Control-C stops the app.
- [x] T003 Create requirements.txt at repo root with Flask and dependencies (e.g. path handling, TOML or JSON config); document Python version in run.sh.
- [x] T004 [P] Configure linting/formatting (e.g. ruff) for backend in backend/ or repo root.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Config, services, and API structure that all user stories depend on. No user story work until this phase is complete.

- [x] T005 [P] Implement TabConfig and config file load in backend/src/models/configModel.py (read TOML or JSON; tabs with optional name, one or two paths per tab).
- [x] T006 Implement config service that loads and exposes tabs (and optional reload) in backend/src/services/configService.py.
- [x] T007 Implement channel scan service: given tab/paths, scan filesystem for directories with both "Videos not transcribed" and "Videos 1 to be transcribed"; return ChannelFolder list; hide channels missing either path; support one or two paths per tab (merge channels, mark source vs destination) in backend/src/services/channelScanService.py.
- [x] T008 Implement media file list service: list media files in a channel inbox path, resolve paired folder (same base name) per data-model; support pagination (limit/offset) in backend/src/services/fileListService.py.
- [x] T009 Implement move service: atomic move (or copy-then-delete) of media file and paired folder from inbox to queue path; idempotent when destination exists or source missing; log each move and each failure in backend/src/services/moveService.py.
- [x] T010 Create Flask app and API route structure (e.g. blueprint for /api/inbox) and error handling (400, 404, 500) in backend/src/api/app.py or backend/src/api/routes.py.
- [x] T011 Add environment or default for config file path (e.g. INBOX_CONFIG env or default path under repo/settings) in backend config load.

**Checkpoint**: Foundation ready — user story implementation can begin.

---

## Phase 3: User Story 1 – List channel folders and queue media (Priority: P1) – MVP

**Goal**: Operator sees all channel folders (per configured path) and can "move 3" or "move all" per channel; can open explore for a channel.

**Independent Test**: Open web UI; verify channel folders are listed; move 3 files from one channel to "Videos 1 to be transcribed"; verify those files appear in the queue folder and are no longer in "Videos not transcribed".

### Implementation for User Story 1

- [x] T012 [P] [US1] Add ChannelFolder DTO (or dict shape) matching contract in backend/src/models/channelModel.py.
- [x] T013 [US1] Implement GET tabs endpoint (GET /api/inbox/tabs) returning tabId, tabName, pathCount per contracts/inbox-queue-api.md in backend/src/api/tabsRoutes.py or equivalent.
- [x] T014 [US1] Implement GET channels endpoint (GET /api/inbox/tabs/{tabId}/channels) with limit/offset; use channel scan service; return channels, total, limit, offset in backend/src/api/channelsRoutes.py or equivalent.
- [x] T015 [US1] Implement POST move endpoint (POST /api/inbox/move) for action move3 and moveAll (tabId, channelId); use move service; return success, movedCount, errors; validate channel belongs to tab in backend/src/api/moveRoutes.py or equivalent.
- [x] T016 [US1] Implement main inbox page: fetch tabs and channels (single tab for MVP), render channel list with pagination or virtualization; per-channel actions "Move 3", "Move all", "Explore" in frontend/src/pages/inboxPage.html (or .js) and frontend/src/components/channelList.js (or equivalent).
- [x] T017 [US1] Wire "Move 3" and "Move all" buttons to POST /api/inbox/move and refresh channel list or show feedback in frontend.
- [x] T018 [US1] Add empty state when no channel folders have inbox media (clear message per spec) in frontend.

**Checkpoint**: User Story 1 is functional: list channels, move 3, move all; explore navigates to explore view (file list in US2).

---

## Phase 4: User Story 2 – Explore and cherry-pick files (Priority: P2)

**Goal**: Operator drills into a channel to see all media files in inbox; selects one or more and queues only selected; cancel/back moves nothing.

**Independent Test**: Explore into a channel with 10 files; select 2; queue them; verify only those 2 are in "Videos 1 to be transcribed" and 8 remain in "Videos not transcribed".

### Implementation for User Story 2

- [x] T019 [P] [US2] Add MediaFile DTO (or dict shape) matching contract in backend/src/models/mediaFileModel.py.
- [x] T020 [US2] Implement GET files endpoint (GET /api/inbox/tabs/{tabId}/channels/{channelId}/files or path-based) with limit/offset; use file list service; return files, total, limit, offset in backend/src/api/filesRoutes.py or equivalent.
- [x] T021 [US2] Extend POST move endpoint to support action queueSelected with filePaths array; validate paths under channel inbox in backend/src/api/moveRoutes.py.
- [x] T022 [US2] Implement explore view page: given tabId and channelId (or channel context), fetch files list with pagination/virtualization; display file list with selection (e.g. checkboxes) and "Queue selected" button in frontend/src/pages/explorePage.html and frontend/src/components/fileList.js.
- [x] T023 [US2] Wire "Queue selected" to POST /api/inbox/move with action queueSelected and selected file paths; on success refresh file list or return to channel list.
- [x] T024 [US2] Ensure cancel/back from explore view moves no files (no API call on cancel).

**Checkpoint**: User Stories 1 and 2 work: list channels, move 3/move all, explore, cherry-pick queue.

---

## Phase 5: User Story 3 – Media sub window when viewing channel media list (Priority: P2)

**Goal**: In explore view, a sub window shows the selected media with play/pause, volume, scrubber, jump forward/back.

**Independent Test**: Open explore view for a channel with media; select a file; verify sub window shows that media and play/pause, volume, scrubber, jump forward/back work.

### Implementation for User Story 3

- [x] T025 [US3] Implement GET media stream endpoint (GET /api/inbox/media?path=...) with safe path validation (only under configured base paths); stream file with Content-Type and HTTP Range support for seeking in backend/src/api/mediaRoutes.py.
- [x] T026 [US3] Add media subpanel component: video/audio element with play/pause, volume, scrubber (seek), jump forward/back; accepts media URL (stream endpoint) in frontend/src/components/mediaSubpanel.js (or equivalent).
- [x] T027 [US3] Integrate media subpanel into explore view: on file selection, set media URL to stream endpoint for selected file; update subpanel when selection changes in frontend/src/pages/explorePage.
- [x] T028 [US3] Handle unsupported format: subpanel shows clear message when playback fails; user can still queue the file.

**Checkpoint**: Explore view has working media preview subpanel.

---

## Phase 6: User Story 4 – Tabbed interface with named tabs per path (Priority: P2)

**Goal**: One tab per configured path; tab label is configured name or default (path or "Path 1"); switching tabs shows only that path’s channels.

**Independent Test**: Configure two base paths with tab names; open web UI; verify two tabs with chosen names and each tab shows only that path’s channel folders.

### Implementation for User Story 4

- [x] T029 [P] [US4] Add tab bar component that renders one tab per item from GET /api/inbox/tabs; tab label = tabName or default in frontend/src/components/tabBar.js.
- [x] T030 [US4] Wire tab bar to main view: on tab change, fetch channels for selected tabId and display channel list for that tab only in frontend/src/pages/inboxPage.
- [x] T031 [US4] Ensure explore view and move actions pass tabId so channel/file context is correct when multiple tabs exist.

**Checkpoint**: Tabbed UI with named tabs; each tab shows its own channel list.

---

## Phase 7: User Story 5 – Two paths per tab (source and destination), merged list, queue to destination (Priority: P2)

**Goal**: A tab can have two paths (source and destination); channel list merges both; queuing from source inbox moves files to destination queue; pipeline runs only in destination.

**Independent Test**: Configure one tab with source and destination paths; add a file to source channel inbox; queue it in UI; verify it appears in destination channel "Videos 1 to be transcribed".

### Implementation for User Story 5

- [x] T032 [US5] Ensure channel scan service merges channels from both paths when tab has two paths; set isSource (or equivalent) per channel; same channel name under both paths treated as same logical channel for move destination in backend/src/services/channelScanService.py.
- [x] T033 [US5] Ensure move service resolves destination queue path from tab config (destination path’s "Videos 1 to be transcribed" for that channel) when tab has two paths in backend/src/services/moveService.py.
- [x] T034 [US5] In channel and file list UI, indicate which path each channel/file belongs to (source vs destination) when tab has two paths in frontend/src/components/channelList.js and fileList.js.
- [x] T035 [US5] Verify move 3, move all, and queue selected from source channel move to destination path’s queue (not source) in backend and frontend.

**Checkpoint**: Two-path tabs work: merged list, queue to destination only.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Logging, edge cases, and validation across all stories.

- [x] T036 Ensure move actions and failures are logged (what moved, from path, to path; error reason) per FR-013 in backend/src/services/moveService.py and/or API layer.
- [x] T037 [P] Add explicit empty state when no tabs or config missing (e.g. message to configure paths) in frontend.
- [x] T038 Validate edge cases: move 3 with fewer than 3 files moves only existing; channel hidden only when inbox missing (queue may be missing; created on move); idempotent move (already moved counts as success); paired folder moves with media in move service and API.
- [x] T039 Run quickstart.md: run.sh, open UI, verify tabs, channels, move 3, explore, media subpanel, and two-path behavior if configured.
- [x] T040 [P] Create master config file at repo base (voicinator.toml) with [server] port and optional [inbox] configPath; add voicinator.toml.example at repo root.
- [x] T041 Load master config in backend (backend/src/models/masterConfigModel.py or configModel), use server.port in backend/__main__.py and optional inbox.configPath in backend/src/services/configService.py for bootstrap.
- [x] T042 Eligibility: list channel if it has only "Videos not transcribed" (inbox); remove requirement for "Videos 1 to be transcribed" in backend/src/services/channelScanService.py.
- [x] T043 Pipeline folders: ensure queue path (and parents) are created when moving if they do not exist in backend/src/services/moveService.py (mkdir parents exist_ok).
- [x] T044 Move sister files (same prefix): when moving a media file, discover and move all files in same directory whose name starts with primary's stem (e.g. .info.json, -thumb.jpg) in backend/src/services/moveService.py.
- [x] T045 Create sidecar folder at destination if missing; move sister files and source paired folder contents into sidecar (not next to primary) in backend/src/services/moveService.py.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2.
- **Phase 4 (US2)**: Depends on Phase 3 (explore view builds on channel list and move API).
- **Phase 5 (US3)**: Depends on Phase 4 (media subpanel in explore view).
- **Phase 6 (US4)**: Depends on Phase 3 (tabs wrap existing channel list).
- **Phase 7 (US5)**: Depends on Phase 2 and Phase 6 (two-path logic in services and UI).
- **Phase 8 (Polish)**: Depends on completion of desired user stories.

### User Story Dependencies

- **US1 (P1)**: After Foundational only; no other story required.
- **US2 (P2)**: Builds on US1 (explore entry and file list/move selected).
- **US3 (P2)**: Builds on US2 (subpanel in explore view).
- **US4 (P2)**: Can follow US1; adds tabs to existing channel list.
- **US5 (P2)**: Builds on Foundational + US4; extends scan and move for two paths.

### Parallel Opportunities

- Phase 1: T004 [P] can run in parallel with T001–T003 after structure exists.
- Phase 2: T005 [P], T010 can be done in parallel where different files.
- Within US1: T012 [P] can run in parallel with other model/route work.
- US4 tab bar (T029 [P]) can be built in parallel with US5 backend changes (T032–T033) if different files.

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Complete Phase 1: Setup.  
2. Complete Phase 2: Foundational.  
3. Complete Phase 3: User Story 1.  
4. Stop and validate: list channels, move 3, move all, navigate to explore (explore view can be minimal until US2).  
5. Demo or deploy.

### Incremental Delivery

1. Setup + Foundational → foundation ready.  
2. US1 → MVP: list channels, move 3, move all.  
3. US2 → Explore and cherry-pick.  
4. US3 → Media subpanel in explore.  
5. US4 → Tabbed UI with names.  
6. US5 → Two paths per tab, queue to destination.  
7. Polish (Phase 8).

### Suggested MVP Scope

- Phases 1, 2, and 3 (through T018).  
- Single-tab UI acceptable for MVP; US4 adds multi-tab.

---

## Summary

| Phase        | Task range | Count |
|-------------|------------|-------|
| Setup       | T001–T004  | 4     |
| Foundational| T005–T011  | 7     |
| US1 (P1)    | T012–T018  | 7     |
| US2 (P2)    | T019–T024  | 6     |
| US3 (P2)    | T025–T028  | 4     |
| US4 (P2)    | T029–T031  | 3     |
| US5 (P2)    | T032–T035  | 4     |
| Polish      | T036–T044  | 9     |
| **Total**   |            | **44**|

**Format validation**: All tasks use checklist format `- [ ] [TaskID] [P?] [Story?] Description with file path`.  
**Independent test criteria**: Each user story phase includes an Independent Test from spec.md.
