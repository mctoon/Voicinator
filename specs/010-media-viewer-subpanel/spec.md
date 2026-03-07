# Feature Specification: Media viewer subpanel in web interface

**Feature Branch**: `010-media-viewer-subpanel`  
**Created**: 2026-03-03  
**Status**: Draft  
**Input**: User description: "when viewing media files in the web interface always include the ability to view the media in a sub panel. With a scrubber, forward/back jump buttons, volume, etc."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Media always viewable in a subpanel (Priority: P1)

Whenever the user is viewing or working with a media file in the web interface (e.g. review view, unknown-speakers list, inbox queue, or any screen that presents a media file), the interface includes a subpanel where the user can watch or listen to that media. The media is not hidden or optional—it is always available in this subpanel so the user can reference the content while performing other actions (e.g. reading the transcript, identifying speakers, or selecting clips).

**Why this priority**: Core expectation: any place the web UI shows a media file, the user can view or play it in a dedicated subpanel without leaving the page or opening another tool.

**Independent Test**: Open any web UI view that displays or references a media file; verify a subpanel is present that shows or can play that media.

**Acceptance Scenarios**:

1. **Given** the user has opened a view that displays or references a media file (e.g. review view, file list with selection), **When** the view loads, **Then** a subpanel is visible that allows the user to view or play that media.
2. **Given** the user switches from one media file to another within the same view (e.g. selects a different file from a list), **When** the selection changes, **Then** the subpanel updates to show or play the newly selected media file.
3. **Given** the user is on a page that lists or references multiple media files, **When** the user selects a media file, **Then** the subpanel displays the selected media so the user can watch or listen without navigating away.

---

### User Story 2 - Playback controls: scrubber, jump buttons, volume (Priority: P1)

The media subpanel provides standard playback controls so the user can navigate and listen comfortably. These include: a scrubber (timeline or seek bar) to jump to any position in the media; forward and back jump buttons to skip ahead or back by a fixed amount (e.g. a few seconds or a configurable step); and a volume control (or mute) so the user can adjust or silence playback. Play and pause are available. The controls work for both video and audio-only media.

**Why this priority**: Without these controls, the user cannot efficiently review long files or align playback with transcript or speaker identification; scrubber and jump buttons are expected for any media viewer.

**Independent Test**: Open the media subpanel for a media file; use the scrubber to seek to a position; use forward and back buttons to jump; adjust volume; verify play and pause work. Repeat for a video file and an audio-only file.

**Acceptance Scenarios**:

1. **Given** the media subpanel is showing a media file, **When** the user drags or clicks on the scrubber, **Then** playback position moves to the selected point and the user can continue from there.
2. **Given** the media is playing or paused, **When** the user uses the forward jump button, **Then** the playback position advances by a consistent step (e.g. 5–15 seconds); when the user uses the back jump button, **Then** the position moves back by the same step.
3. **Given** the media subpanel is active, **When** the user adjusts the volume control, **Then** playback volume changes accordingly; the user can mute and unmute without losing the volume level.
4. **Given** the media is loaded in the subpanel, **When** the user uses play and pause, **Then** playback starts and stops as expected.
5. **Given** the media is audio-only (no video track), **When** the subpanel is shown, **Then** the same controls (scrubber, forward/back jump, volume, play/pause) are available and function for the audio stream.

---

### User Story 3 - Subpanel available in all media views (Priority: P2)

The media viewer subpanel is included in every part of the web interface where a media file is in context. This includes (but is not limited to): the review view (transcript and speaker identification), the unknown-speakers workflow, the inbox or queue when a file is selected, and any search or browse result when a media file is selected. There is no “view-only” or “list-only” mode where the user sees a reference to a media file but cannot play it in a subpanel on the same screen.

**Why this priority**: Consistency—users expect to see and control media whenever they are working with a file, regardless of which screen they are on.

**Independent Test**: Navigate to each type of view that shows or selects a media file; confirm each view includes the media subpanel with playback controls.

**Acceptance Scenarios**:

1. **Given** the user is in the review view (e.g. transcript with speaker tags), **When** the view is open, **Then** the media subpanel is present and shows the same media file being reviewed.
2. **Given** the user is in the unknown-speakers or speaker-identification workflow, **When** a media file is in context, **Then** the media subpanel is present so the user can listen while identifying speakers.
3. **Given** the user is in a list or queue view (e.g. inbox, “to be transcribed”), **When** the user selects a media file from the list, **Then** the media subpanel appears or updates to show that file with full playback controls.

---

### Edge Cases

- What happens when the media file is very long (e.g. hours)? The scrubber and jump buttons remain usable; the system may show position and duration in a human-readable form (e.g. time codes). Performance of seeking is acceptable for typical use (e.g. seek within a few seconds).
- What happens when the selected item is not playable (e.g. unsupported format or corrupted file)? The subpanel shows a clear message that the media cannot be played (and does not leave the user with a blank or broken control set). Other parts of the UI remain usable.
- What happens when the user has multiple tabs or windows open with different media? Each view shows the media relevant to that context; no requirement for syncing playback across tabs.
- What happens for audio-only files? The subpanel still displays (e.g. with a static or minimal visual) and all controls (scrubber, jump, volume, play/pause) apply to the audio track.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Whenever the web interface presents or references a media file in a view (e.g. review view, unknown-speakers workflow, queue or list with selection), the system MUST provide a subpanel in that view where the user can view or play the media.
- **FR-002**: The media subpanel MUST include a scrubber (seek bar or timeline) so the user can move playback to any position in the media.
- **FR-003**: The media subpanel MUST include forward and back jump buttons that advance or rewind playback by a consistent, configurable or reasonable default step (e.g. 10 seconds).
- **FR-004**: The media subpanel MUST include a volume control (and optionally mute) so the user can adjust or silence playback.
- **FR-005**: The media subpanel MUST support play and pause so the user can start and stop playback.
- **FR-006**: When the user changes the selected media file within a view (e.g. selects a different file from a list), the subpanel MUST update to show or play the newly selected media.
- **FR-007**: The same playback controls (scrubber, jump buttons, volume, play/pause) MUST be available and functional for both video and audio-only media.
- **FR-008**: If the media cannot be played (e.g. unsupported format or error), the subpanel MUST display a clear, user-friendly message instead of failing silently or showing broken controls.

### Key Entities

- **Media file**: A video or audio file (e.g. from the pipeline or queue) that the user can select and play in the web interface.
- **Subpanel**: A dedicated area within a web view that displays the selected media and its playback controls, so the user can watch or listen without leaving the current page.
- **Playback controls**: Scrubber (seek), forward/back jump buttons, volume (and mute), and play/pause—all available whenever media is shown in the subpanel.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In every web view where a media file is in context, the user can see and play that media in a subpanel on the same screen, without opening another application or tab for playback.
- **SC-002**: Users can seek to any position using the scrubber, and jump forward or back using the buttons, and adjust volume, so that reviewing and aligning with transcript or speaker segments is efficient (e.g. typical seek or jump completes within a few seconds).
- **SC-003**: Playback controls behave consistently for video and audio-only files, and the subpanel is present in review, unknown-speakers, queue/list, and any other view that shows or selects a media file.

## Assumptions

- “Subpanel” means a distinct area within the same page or view (e.g. a panel beside or below the main content), not a separate window or application.
- Forward/back jump step size may be fixed (e.g. 10 seconds) or configurable; a reasonable default is sufficient for the spec.
- The web interface already has one or more views that display or reference media files (e.g. from 002-media-folder-pipeline, 008-speaker-voice-library, 001-inbox-queue-web-ui); this feature adds the media viewer subpanel and controls to those views.
- Supported media formats are those already supported by the pipeline or ingest; the subpanel is not required to support formats the system does not otherwise handle.
