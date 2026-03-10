# Tasks: Web UI to Identify Unknown Speakers

**Input**: Design documents from `specs/007-webui-to-identify-unknown-speakers/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/  
**Contract**: [007-unknown-speakers-api.md](contracts/007-unknown-speakers-api.md) — tasks that implement API behavior cite the contract section (e.g. Contract §2) so contract changes can be traced to code.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story (US1–US4)
- Include exact file paths in descriptions

## Path Conventions

- Backend: `backend/src/` (api/, services/, pipeline/)
- Frontend: `frontend/src/` (pages/, services/)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No new project setup; ensure feature branch and docs are in place.

- [x] T001 Ensure feature branch 007-webui-to-identify-unknown-speakers and design docs (plan, spec, research, data-model, contracts) are available per specs/007-webui-to-identify-unknown-speakers/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Backend support for placeholder names (full speaker record + corpus), zero-speaker handling, and resolve behavior that all user stories depend on.

**Independent Test**: Placeholder: resolve with resolution=placeholder and no name returns assignedName Unidentified-N; full speaker record is created and passage(s) from current video are added to that speaker's corpus (same as named speaker); zero-speaker: media with empty segments excluded from list or moved to step 6.

- [x] T002 [P] Add globally unique placeholder name generation (pattern Unidentified-<N>, counter in resolver storage) in backend/src/services/pipeline/speakerResolver.py (Contract §4)
- [x] T003 Extend GET /api/pipeline/speakers/files to detect zero-speaker media (empty segments) and either exclude from list or move to step 6 in backend/src/api/pipelineSpeakersRoutes.py (Contract §1)
- [x] T004 When resolution is placeholder and name omitted, create full speaker record (same structure as named speaker), generate and store placeholder name, add passage(s) from current video to that speaker's corpus, associate segment with that speaker, and return assignedName in POST resolve in backend/src/api/pipelineSpeakersRoutes.py and backend/src/services/pipeline/speakerResolver.py (Contract §4)

**Checkpoint**: Placeholder names and zero-speaker behavior ready for UI and complete flow.

---

## Phase 3: User Story 1 - List all videos needing speaker identification (Priority: P1) — MVP

**Goal**: User sees a single list of all videos in "Videos 5 needs speaker identification" (channel + filename), can select one to open identification view. Zero-speaker videos excluded or auto-moved.

**Independent Test**: Put media in step 5 in one or more channels; open Unknown Speakers section; list shows each video with channel and filename; select one opens identification view. Zero-speaker file not in list.

- [x] T005 [P] [US1] Ensure list response includes channelName and mediaPath/filename for each item in backend/src/api/pipelineSpeakersRoutes.py (discoverMediaInUnknownSpeakersStep already returns these; verify response shape). FR-002: filename required; title optional if available. (Contract §1)
- [x] T006 [US1] Ensure frontend list displays channel name and media filename (and title if available, per FR-002) and empty state when no files in frontend/src/pages/unknownSpeakersPage.js and unknownSpeakersPage.html
- [x] T007 [US1] Ensure selecting a list item navigates to identification view (segment/transcript panel) in frontend/src/pages/unknownSpeakersPage.js

**Checkpoint**: User can open list and select a video to process.

---

## Phase 4: User Story 2 - Review transcript and click-to-play (Priority: P1)

**Goal**: Identification view shows transcript in transcript.txt style (sections labeled by speaker and time); play/pause and playback controls fixed at bottom so they do not scroll off; clicking any word starts playback at that word's start time (from transcript_words.json); clicking a section starts playback at that section's timestamp.

**Independent Test**: Select a video; transcript loads in speaker-and-time sections; play/pause stays at bottom when scrolling; click a word and playback starts at that word's start time; click a section and playback starts at that time.

- [x] T008 [P] [US2] Add GET /api/pipeline/speakers/files/{mediaId}/transcript returning words + segments (merge transcript_words.json and segments.json, attach segmentId/speakerId per word; each word has start/end from transcript_words.json) in backend/src/api/pipelineSpeakersRoutes.py (Contract §2)
- [x] T009 [US2] Add transcript panel in transcript.txt style: render sections by speaker and time (speaker label + timestamp + that section's text); speaker name/label in front of each section in frontend/src/pages/unknownSpeakersPage.html and unknownSpeakersPage.js (FR-003)
- [x] T009b [US2] Place play/pause and other playback controls at the bottom of the identification view so they remain fixed and do not scroll off screen when the user scrolls the transcript in frontend/src/pages/unknownSpeakersPage.html and unknownSpeakersPage.js (FR-003)
- [x] T010 [US2] Add click handler so that (a) clicking any word in the transcript sets media currentTime to that word's start time (from transcript data/transcript_words.json) and plays, and (b) clicking a section (segment or line) sets currentTime to section start and plays; ensure media element has source from media file in frontend/src/pages/unknownSpeakersPage.js (Contract §3: client-side seek, FR-003)
- [x] T011 [US2] Handle missing transcript or media with clear error message and way to return to list in frontend and backend (404 for transcript, FR-008) in backend/src/api/pipelineSpeakersRoutes.py and frontend/src/pages/unknownSpeakersPage.js (Contract §2 response)

**Checkpoint**: Transcript in transcript.txt style, controls at bottom, click-to-play works.

---

## Phase 5: User Story 3 - Resolve each unidentified speaker (Priority: P1)

**Goal**: Clicking a speaker name in the transcript opens an identify popup. Popup has: scrollable list of existing speakers; text field that narrows (filters) the list; Enter when typed name is unique creates new speaker and resolves; option to skip/not-identify. Assign to existing, create new (unique name + Enter), or decline (full speaker record with placeholder). Suggested identification when available; user can confirm or correct; on confirm add passage to speaker corpus.

**Independent Test**: Two unidentified speakers; click one speaker name in transcript, assign to existing from popup; click the other, type unique name and press Enter to create; verify both resolved. Repeat with skip/not identify; verify Unidentified-N and full speaker record. If suggestion shown, confirm and verify passage added.

- [x] T012 [P] [US3] Include optional suggestedSpeakerId and suggestedSpeakerName in GET segments and GET transcript when resolver has suggestion in backend/src/api/pipelineSpeakersRoutes.py and backend/src/services/pipeline/speakerResolver.py (Contract §2, §4)
- [x] T013 [US3] Add identify-by-click: clicking speaker name in transcript opens popup with (a) scrollable list of existing speakers, (b) text field that filters the list as user types, (c) Enter when typed name is unique creates new speaker and resolves that speaker, (d) skip/not-identify option; validate new-speaker name (non-empty; optional duplicate check); call POST resolve with resolution=placeholder or new/existing in frontend/src/pages/unknownSpeakersPage.html and unknownSpeakersPage.js (Contract §4, FR-004)
- [x] T014 [US3] Display suggested identification when present and allow confirm or change in frontend/src/pages/unknownSpeakersPage.js
- [x] T015 [US3] On confirm of suggested identification, ensure backend adds passage from current video to that speaker's corpus (resolver or sidecar) in backend/src/services/pipeline/speakerResolver.py. If 008 is not yet implemented: store passage reference in resolver/sidecar; 008 will persist to voice library. (Contract §4)
- [x] T016 [US3] Show resolved state per speaker in the transcript (and any list): checkmark, "Resolved" label, or non-clickable/disabled for that speaker name in frontend/src/pages/unknownSpeakersPage.js (FR-007a)

**Checkpoint**: Identify-by-click popup with list, filter, Enter-to-create, skip; placeholder and suggested ID supported.

---

## Phase 6: User Story 4 - Complete identification and move to step 6 (Priority: P1)

**Goal**: "Complete identification" button active when all speakers resolved; on click: backup transcript files, rewrite with speaker names, move media+paired folder to step 6, navigate back to list.

**Independent Test**: Resolve all speakers; Complete button enabled; click; transcript backup exists and new transcript has names; file in step 6; back on list without that video.

- [x] T017 [P] [US4] Add transcript backup-and-rewrite helper (copy transcript.txt and transcript_words.json to backup names, then rewrite with resolved speaker names from segments/resolver) in backend/src/services/pipeline/transcriptUpdateService.py—or inline in pipelineSpeakersRoutes.py if a separate module is not preferred; document the choice in quickstart. (Contract §5)
- [x] T018 [US4] Add POST /api/pipeline/speakers/files/{mediaId}/complete: verify all resolved, run transcript backup+rewrite, then move media and paired folder to step 6 (creating "Videos 6 speakers matched" folder if missing, per spec edge case) in backend/src/api/pipelineSpeakersRoutes.py (Contract §5)
- [x] T019 [US4] Add "Complete identification" button to identification view, disabled until all segments resolved, in frontend/src/pages/unknownSpeakersPage.html and unknownSpeakersPage.js
- [x] T020 [US4] On Complete click call POST complete and on success navigate back to list and refresh list in frontend/src/pages/unknownSpeakersPage.js
- [x] T021 [US4] Add GET can-complete or derive from segments so button enable/disable is correct in frontend/src/pages/unknownSpeakersPage.js (and optional backend endpoint if needed) (Contract §6)

**Checkpoint**: Full flow from list → identify → complete → back to list with transcript updated and file in step 6.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases, docs, and consistency. Performance (list load within 5 s, click-to-play within ~500 ms) is validated manually per plan Performance Goals; no separate automated verification task unless added here.

- [x] T022 [P] Handle concurrent complete (same video in two tabs): second request sees file already moved and returns 404 or no-op in backend/src/api/pipelineSpeakersRoutes.py (Contract §5)
- [x] T023 [P] When transcript files missing at complete, skip rewrite or create from segment/word data per research; log and do not overwrite arbitrary paths in backend transcript-update logic (Contract §5)
- [x] T024 [P] Add "Unknown Speakers" link to the left side of all existing pages (FR-012, US1 scenario 4); update quickstart and nav so section is discoverable; run quickstart.md validation for 007 flow in frontend layout/nav and quickstart.md
- [x] T025 Ensure empty list state shows message (no videos need identification) not error per spec edge case in frontend/src/pages/unknownSpeakersPage.js
- [x] T026 [P] Document navigate-away-without-completing behavior (whether resolutions are saved for later or single-session required) in quickstart.md or specs/007-webui-to-identify-unknown-speakers/ (per spec edge case)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: No dependencies.
- **Phase 2**: Depends on Phase 1. Blocks US1–US4.
- **Phase 3 (US1)**: Depends on Phase 2. Can start after T002–T004.
- **Phase 4 (US2)**: Depends on Phase 2. Can run parallel to Phase 3 after Phase 2.
- **Phase 5 (US3)**: Depends on Phase 2; uses resolve and segments. Can run after Phase 3/4.
- **Phase 6 (US4)**: Depends on Phase 2 and transcript/complete backend. After T008, T017, T018.
- **Phase 7**: After all story phases.

### User Story Dependencies

- **US1**: After Foundational. No dependency on US2–US4.
- **US2**: After Foundational. No dependency on US3–US4.
- **US3**: After Foundational; integrates with US2 (transcript view). Placeholder and suggested ID in resolver.
- **US4**: After Foundational; needs transcript endpoint (US2) and complete endpoint; frontend needs US2/US3 UI.

### Parallel Opportunities

- T002, T005, T008, T012, T017 can be parallelized where different files.
- Phases 3 and 4 can be done in parallel after Phase 2; Phase 5 after 3/4; Phase 6 after 4 and 5 backend.

---

## Implementation Strategy

### MVP First (US1 + minimal path)

1. Phase 1 + Phase 2.
2. Phase 3 (US1): List and select.
3. Phase 4 (US2): Transcript and click-to-play.
4. Phase 5 (US3): Resolve (existing, new, placeholder).
5. Phase 6 (US4): Complete button and transcript update + move.
6. Phase 7: Edge cases and docs.

### Incremental Delivery

- After Phase 3: User can open list and select a video.
- After Phase 4: User can read transcript and play from a point.
- After Phase 5: User can resolve all speakers (including placeholder).
- After Phase 6: User can complete and return to list with file in step 6 and transcript updated.

---

## Notes

- [P] = parallelizable (different files).
- [USn] = task belongs to that user story for traceability.
- Spec does not require TDD; no test tasks added unless you add them later.
- Paths: backend/src/..., frontend/src/... per plan.md.
