# Feature Specification: Atomic Pipeline Moves, SRT Output, and Speaker-Resolution Context

**Feature Branch**: `011-atomic-srt-speaker-context`  
**Created**: 2026-03-04  
**Status**: Draft  
**Input**: (1) In the media-folder pipeline, file moves must behave like atomic operations: when a new file is discovered in a folder, the next processing step waits a short delay then checks the previous pipeline folder for sister folder/files before acting. (2) When outputting transcript files, also output an SRT file for on-screen subtitles; if an SRT already exists, rename the old one and replace with the new one. (3) For resolving unknown speakers in the web UI, when the user is presented an unknown speaker they need context: display the surrounding transcript tagged with speaker names; the user can click a word and use a play/pause control to start playback at that point.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Atomic-like moves across pipeline steps (Priority: P1)

When media files (and their paired folders with sister files) are moved from one pipeline step folder to the next, the move is not a single atomic operation—multiple files and a folder are moved. A downstream step that discovers a new file in its folder must not assume the move is complete. The system simulates atomicity by having each step, when it first discovers a new file in its folder, wait a short delay (a few seconds), then check the previous pipeline folder to ensure no sister files or the paired folder remain there before starting work. Only when the previous folder no longer contains assets for that media does the step proceed.

**Why this priority**: Prevents processing from acting on incomplete moves (e.g. media in step N+1 but paired folder still in step N), avoiding duplicate work, corrupted state, or lost files.

**Independent Test**: Trigger a move from step N to N+1; while the move is in progress, have the step N+1 watcher run; verify it waits, then checks the previous folder, and only starts processing after the move is complete (no sister files or paired folder left in step N).

**Acceptance Scenarios**:

1. **Given** a processing step that watches a pipeline folder for new media, **When** it discovers a new file in its folder, **Then** it waits a configured short delay (e.g. a few seconds) before performing any work for that file.
2. **Given** the step has waited after discovering a new file, **When** it proceeds, **Then** it checks the previous pipeline folder (the folder from which the file was moved) for the presence of the paired folder or any sister files for that media; if any remain, it does not start processing and may re-check after a further delay or back off.
3. **Given** the previous folder no longer contains the paired folder or sister files for that media, **When** the step has completed its check, **Then** it may proceed with processing for that file.
4. **Given** the delay and check are configurable, **When** an operator adjusts them, **Then** the system uses the configured values so that slow file systems or large moves can be accommodated.

---

### User Story 2 - SRT output for subtitles (Priority: P1)

When the system outputs transcript files for a processed media file, it also produces an SRT file suitable for on-screen subtitles (e.g. in video players or editors). The SRT is written to the same paired folder as the other transcript outputs. If an SRT file with the same base name already exists in that folder (e.g. from a previous run or from an external source), the system renames the existing SRT (e.g. with a backup or timestamp suffix) and then writes the new SRT in its place, so the canonical subtitle file is always the newly generated one.

**Why this priority**: Enables subtitles in video workflows without overwriting user data silently; operators can add on-screen subtitles when desired.

**Independent Test**: Process a media file that has no existing SRT; verify an SRT appears in the paired folder. Process again or add a pre-existing SRT with the same base name; verify the old SRT is renamed and a new SRT is written.

**Acceptance Scenarios**:

1. **Given** a media file that has been transcribed and has word- or segment-level timing, **When** transcript outputs are written, **Then** an SRT file (same base name as the media, .srt extension) is produced in the paired folder, with content suitable for on-screen subtitles.
2. **Given** the paired folder already contains an SRT file with the same base name as the media, **When** the system writes a new SRT for that media, **Then** the existing SRT is renamed (e.g. to a backup name such as base name plus suffix like .srt.bak or timestamp) so it is preserved, and the new SRT is written as the primary .srt file.
3. **Given** no existing SRT in the paired folder, **When** the system writes transcript outputs, **Then** the new SRT is written without requiring a rename step.
4. **Given** the new SRT file, **When** a user or tool opens it, **Then** it conforms to standard SRT format so that common video players and subtitle tools can display it.

---

### User Story 3 - Resolve unknown speakers: transcript context and word-level playback (Priority: P2)

When the user is resolving unknown speakers in the web UI (User Story 5 of the media-folder-pipeline spec), they are presented with an unknown speaker. To make identification easier, the UI shows context: the surrounding transcript text tagged with speaker names (or labels) so the user can see what was said before and after by whom. The user can click on a word in that transcript; a play/pause control (e.g. next to the transcript or in a media control area) then starts playback of the media at the timestamp for that word, so the user can hear the exact moment in context.

**Why this priority**: Reduces guesswork when matching voices to speakers; the user sees and hears the relevant segment without hunting through the whole file.

**Independent Test**: Open the resolve-unknown-speakers view for a file with unknown speakers; verify the UI shows surrounding transcript with speaker tags; click a word and use play/pause; verify playback starts at that word’s time.

**Acceptance Scenarios**:

1. **Given** the user is presented with an unknown speaker in the resolve-unknown-speakers flow, **When** the view is shown, **Then** the system displays surrounding transcript text with speaker names or labels so the user has context for who said what near that speaker’s segments.
2. **Given** the transcript is displayed with speaker tags, **When** the user clicks on a word in the transcript, **Then** the system records that word’s timestamp (or the start of the segment containing that word) as the intended playback start point.
3. **Given** the user has selected a word (or the system has a start point), **When** the user activates the play/pause control, **Then** playback of the media begins at that point (or toggles pause if already playing).
4. **Given** the user is listening to a segment, **When** they need more context, **Then** they can click another word and use play/pause again to jump to that point and continue identification.

---

### Edge Cases

- What happens when the previous pipeline folder is on a slow or network drive? The configured delay and optional re-check/back-off allow the system to wait until the move is complete; if the move never completes (e.g. failure), the step does not process incomplete data.
- What happens when the existing SRT is locked or read-only? The system MUST handle the failure gracefully: report or log the issue, and MUST NOT overwrite the file without renaming; the operator can resolve permissions or rename manually.
- What happens when there is no word-level timing for a segment? For SRT, the system uses the best available timing (e.g. segment start/end); for word-click playback, the system uses segment start if word-level timing is missing for that word.
- What happens when the user clicks a word in the transcript but the media is not yet loaded? The system sets the start point and when the user presses play, playback begins at that point once the media is ready.
- What happens when multiple pipeline steps discover the same file (e.g. race)? The atomicity behavior (wait and check previous folder) ensures no step proceeds until the move is complete; only one step folder should contain the file and paired folder at a time.

---

## Assumptions

- The "previous pipeline folder" for a given step is well-defined (e.g. the step folder that immediately precedes the current one in the processing folder plan).
- Sister files and paired folder are defined as in the media-folder-pipeline spec (002); the check for "move complete" means the previous folder no longer contains the paired folder or sister files for that media base name.
- SRT format is the standard SubRip format (numbered sequences, timecodes, text lines).
- The resolve-unknown-speakers web UI is the same as in spec 002 (User Story 5); this feature adds context (surrounding transcript with speaker tags) and word-click playback.
- Renaming the existing SRT uses a deterministic scheme (e.g. .srt.bak or timestamp) so the operator can identify and restore the old file if needed.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: When a pipeline step discovers a new file in its folder, the system MUST wait a configured short delay (default on the order of a few seconds) before performing any processing for that file.
- **FR-002**: After the delay, the system MUST check the previous pipeline folder (the step folder from which the file was moved) for the presence of the paired folder or any sister files for that media; it MUST NOT start processing until that folder no longer contains those assets.
- **FR-003**: The delay duration and whether to re-check (and back-off) if the previous folder still has assets MUST be configurable so operators can tune for their file system and move behavior.
- **FR-004**: When the system writes transcript outputs for a processed media file, it MUST also produce an SRT file in the paired folder, with the same base name as the media and .srt extension, suitable for on-screen subtitles.
- **FR-005**: If an SRT file with that base name already exists in the paired folder, the system MUST rename the existing SRT (e.g. to a backup or timestamped name) before writing the new SRT, so the new file becomes the primary .srt and the old one is preserved.
- **FR-006**: The new SRT content MUST conform to standard SRT format so common players and tools can use it.
- **FR-007**: In the resolve-unknown-speakers web UI, when the user is presented with an unknown speaker, the system MUST display surrounding transcript text with speaker names or labels so the user has context.
- **FR-008**: The transcript display MUST allow the user to click on a word (or token) to set a playback start point.
- **FR-009**: A play/pause control MUST be available so that when the user activates it, playback of the media starts at the selected word’s timestamp (or toggles pause if already playing).

### Key Entities

- **Pipeline step folder**: A folder in the processing folder plan (e.g. Videos 2 audio extracted through Videos 8 export ready) where media and paired folders reside during processing.
- **Previous pipeline folder**: The step folder that immediately precedes the current step in the processing order; the source of the move into the current folder.
- **Paired folder / sister files**: As in spec 002: folder with same base name as the media file; sister files share the base name with different extensions; all move together.
- **SRT file**: A SubRip-format subtitle file (.srt) in the paired folder, used for on-screen subtitles; one per media file, with backup created when replacing an existing SRT.
- **Surrounding transcript**: A portion of the transcript (before and after the segment in focus) with speaker tags, shown in the resolve-unknown-speakers UI for context.
- **Playback start point**: A timestamp (e.g. word-level or segment-level) set by clicking a word; used when the user presses play to begin playback at that point.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: No pipeline step starts processing a file until the move from the previous folder is complete (paired folder and sister files no longer in the previous folder), so that incomplete moves do not cause duplicate work or data inconsistency.
- **SC-002**: Every processed media file that produces transcript outputs has a corresponding SRT file in the paired folder; when an SRT already existed, the old file is renamed and preserved and the new SRT is the primary file.
- **SC-003**: Operators can use the resolve-unknown-speakers UI with transcript context and word-click playback to identify speakers more quickly: they see who said what nearby and can jump to and play from a specific word.
- **SC-004**: The delay and move-complete check are configurable so that different environments (local vs network storage, large vs small moves) can be tuned without code changes.
