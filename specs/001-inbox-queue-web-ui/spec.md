# Feature Specification: Inbox-to-Queue Web UI

**Feature Branch**: `001-inbox-queue-web-ui`  
**Created**: 2026-03-02  
**Status**: Draft  
**Input**: Media in "[YouTube channel]/Videos not transcribed" are not queued for processing; they must be moved to "[YouTube channel]/Videos 1 to be transcribed" before processing starts. The web UI lists all YouTube channel folders and offers: move 3 files, move all files, or explore to see all files and cherry-pick which to queue. When viewing the list of media for a channel, the user can view the media in a sub window with play/pause, volume, scrubbing, jump forward/back. The interface is tabbed so each configured path gets a tab (paths represent different types of YouTube channels); the user can name the tab when defining the path. A tab may have one path or two sister paths (source and destination): when two paths are configured, media from both are shown merged; queuing moves files from the source's "Videos not transcribed" to the destination's "Videos 1 to be transcribed", and the pipeline runs only in the destination folder.

---

## Clarifications

### Session 2026-03-07

- Q: Who can access the inbox-queue Web UI, and is authentication required? → A: Single operator, local-only (e.g. localhost or same machine); no authentication.
- Q: What should the UI show for empty, loading, or failure states? → A: Folders are on the local filesystem; there is no loading or network lag.
- Q: How many channel folders or media files are expected (affects pagination/virtualization)? → A: Hundreds of channels or thousands of files; require virtualization or pagination for lists.
- Q: Where does path configuration (base paths, tab names) live, and where is it edited? → A: Config file or app-level settings (read by this feature); path/tab editing may be in-app or via editing the file.
- Q: Should move actions and failures be logged or measurable? → A: Log move actions and failures (what moved, from/to, errors); no metrics dashboard required.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - List channel folders and queue media (Priority: P1)

The operator opens the web UI and sees a list of all YouTube channel folders (across configured base folders). For each channel, media files in "Videos not transcribed" are not yet queued for processing. The operator can move files from that inbox into "Videos 1 to be transcribed" so the pipeline will pick them up. The UI offers three ways to queue: move 3 files (quick batch), move all files (queue entire channel), or explore into a channel to see every file and cherry-pick which ones to queue.

**Why this priority**: Core value is giving the operator control over what gets processed and a clear two-stage flow (inbox vs queued).

**Independent Test**: Open web UI; verify channel folders are listed; move 3 files from one channel to "Videos 1 to be transcribed"; verify those files appear in the queue folder and are no longer in "Videos not transcribed".

**Acceptance Scenarios**:

1. **Given** one or more configured base folders, **When** the user opens the web UI, **Then** the system lists all channel folders (e.g. one entry per "[Base]/[YouTube channel]" that has a "Videos not transcribed" path).
2. **Given** the list of channel folders, **When** the user chooses to move 3 files for a channel, **Then** the system moves up to 3 media files (and their paired folders, if any) from that channel's "Videos not transcribed" to that channel's "Videos 1 to be transcribed".
3. **Given** the list of channel folders, **When** the user chooses to move all files for a channel, **Then** the system moves all media files (and their paired folders) from that channel's "Videos not transcribed" to that channel's "Videos 1 to be transcribed".
4. **Given** the list of channel folders, **When** the user chooses to explore a channel, **Then** the system shows all media files in that channel's "Videos not transcribed", and the user can select which ones to queue; when the user confirms, the system moves only the selected files (and their paired folders) to "Videos 1 to be transcribed".
5. **Given** files have been moved to "Videos 1 to be transcribed", **When** the processing pipeline runs, **Then** it discovers and processes only files in "Videos 1 to be transcribed", not files that remain in "Videos not transcribed".

---

### User Story 2 - Explore and cherry-pick files (Priority: P2)

The operator drills into a channel to see every media file in "Videos not transcribed". The UI shows enough information to identify each file (e.g. filename, duration if available). The operator selects one or more files and queues them; only the selected files are moved to "Videos 1 to be transcribed". Files not selected remain in the inbox.

**Why this priority**: Enables precise control when the operator does not want to queue everything or exactly 3.

**Independent Test**: Explore into a channel that has 10 files; select 2; queue them; verify only those 2 are in "Videos 1 to be transcribed" and 8 remain in "Videos not transcribed".

**Acceptance Scenarios**:

1. **Given** the user has chosen to explore a channel, **When** the view loads, **Then** the system displays all media files currently in that channel's "Videos not transcribed".
2. **Given** the list of files in the channel, **When** the user selects a subset and confirms "queue selected", **Then** only the selected files (and their paired folders) are moved to "Videos 1 to be transcribed".
3. **Given** the user is in the explore view, **When** the user cancels or goes back without confirming, **Then** no files are moved.

---

### User Story 3 - Media sub window when viewing channel media list (Priority: P2)

When the user is viewing the list of media for a channel (e.g. in the explore view), the interface includes a sub window where the user can view or play the selected media. The sub window provides normal media viewing controls: play/pause, volume, scrubbing (seek bar), and jump forward/back. This lets the operator preview a file before deciding to queue it, without leaving the page.

**Why this priority**: Improves decision-making when cherry-picking; the operator can quickly confirm which file is which by playing it in the sub window.

**Independent Test**: Open the explore view for a channel with media files; select a file; verify a sub window appears or updates with that media and that play/pause, volume, scrubber, and jump forward/back work.

**Acceptance Scenarios**:

1. **Given** the user is viewing the list of media for a channel (explore view), **When** the view is shown, **Then** a sub window is available where the user can view or play media.
2. **Given** the user selects a media file from the channel list, **When** the selection changes, **Then** the sub window updates to show or play the selected media file.
3. **Given** the sub window is showing a media file, **When** the user uses the controls, **Then** play/pause, volume, scrubbing (seek), and jump forward/back function as expected so the user can preview the file.

---

### User Story 4 - Tabbed interface with named tabs per path (Priority: P2)

The interface is tabbed so that each configured base path gets its own tab. Paths represent different types of YouTube channels (e.g. different brands or categories). When the user defines or edits a path, they can assign a name to the tab so that the tab label is meaningful (e.g. "Main channel", "Shorts channel") instead of showing only a raw path.

**Why this priority**: With multiple configured paths, tabs keep each path's channels separate and named tabs make it clear which path the user is viewing.

**Independent Test**: Configure two base paths and give each a tab name; open the web UI; verify two tabs appear with the chosen names and each tab shows only the channel folders for that path.

**Acceptance Scenarios**:

1. **Given** the user has configured one or more base paths, **When** the user opens the inbox-queue web UI, **Then** the interface shows one tab per configured path, and the user can switch between tabs to see channel folders for each path.
2. **Given** the user is defining or editing a path, **When** the user sets a name for the tab, **Then** the system stores that name and displays it as the tab label (so the tab is identifiable without reading the full path).
3. **Given** a tab has no custom name, **When** the tab is displayed, **Then** the system MAY show the path or a default label so the tab is still distinguishable.

---

### User Story 5 - Two paths per tab (source and destination), merged list, queue to destination (Priority: P2)

A tab may be configured with two paths instead of one. When two paths are specified, they are "sister paths": the first is the "source" and the second is the "destination". Media files from both the source and the destination are presented in a single merged list for that tab (e.g. all channels under the source path and all under the destination path appear together or are clearly from the same tab). When the user queues files, files that are in the source path's "Videos not transcribed" (inbox) are moved to the destination path's "Videos 1 to be transcribed" (queue). The processing pipeline runs only in the destination path; the source path is never used for pipeline processing. This supports workflows where media is ingested or dropped in one location (source) and actually processed in another (destination).

**Why this priority**: Supports split ingest/process layouts (e.g. source = "to be processed" location, destination = pipeline location) without running the pipeline in the source.

**Independent Test**: Configure one tab with two paths (source and destination); add a media file to a channel's "Videos not transcribed" under the source path; in the UI, queue that file; verify it appears in the destination path's "Videos 1 to be transcribed" and that the pipeline runs only under the destination path.

**Acceptance Scenarios**:

1. **Given** a tab is configured with two paths (source and destination), **When** the user views that tab, **Then** the list of media/channel folders shows content from both paths merged (or aggregated) so the user can see and queue from both.
2. **Given** the user queues a file that resides in the source path's "Videos not transcribed", **When** the queue action is confirmed, **Then** the system moves that file (and its paired folder) to the corresponding channel's "Videos 1 to be transcribed" under the destination path, not the source path.
3. **Given** two paths are configured (source and destination), **When** the processing pipeline runs, **Then** it discovers and processes only media in "Videos 1 to be transcribed" under the destination path; it MUST NOT run pipeline steps (transcription, diarization, etc.) in the source path.
4. **Given** a tab has only one path configured, **When** the user queues files, **Then** files move from that path's "Videos not transcribed" to that same path's "Videos 1 to be transcribed" (existing single-path behavior).

---

### Edge Cases

- What happens when a channel has fewer than 3 files? "Move 3 files" moves only the files that exist (up to 3).
- What happens when "Videos 1 to be transcribed" or "Videos not transcribed" is missing for a channel? The system MUST NOT create folders automatically in this feature; it MUST hide the channel so the operator is not misled.
- What happens when two operators queue the same file at the same time? The system MUST move the file at most once; duplicate moves are avoided (e.g. move is atomic or idempotent).
- What happens when a media file has a paired folder (same base name)? When moving the media file, the paired folder moves with it so they stay together.
- What happens when a tab has two paths and the same channel name exists under both source and destination? The system MUST treat them as the same logical channel for queuing: files from source "[Channel]" move to destination "[Channel]" "Videos 1 to be transcribed". Merged list display MUST make clear which path each file or channel belongs to when both paths are shown.
- What happens when the user has not named a tab? The system displays a default (e.g. path or "Path 1") so the tab is still usable.
- What happens when the selected media file cannot be played in the sub window (e.g. unsupported format)? The sub window shows a clear message; the user can still queue the file.
- What happens when there are no channel folders with inbox media? The UI shows an explicit empty state (e.g. a clear message that no channel folders have inbox media) so the user is not left with a blank list.

---

## Assumptions

- The inbox-queue Web UI is single-operator, local-only (e.g. localhost or same machine); no authentication is required for this feature.
- Path configuration and media folders are on the local filesystem; the UI does not rely on a remote backend or network, so there is no network loading or network failure to handle.
- Scale: hundreds of channel folders and thousands of media files are in scope; lists (channel list and per-channel media list) MUST support virtualization or pagination so the UI remains usable at that scale.
- Base folders and channel layout (e.g. "[Base]/[Channel]/Videos not transcribed" and "[Channel]/Videos 1 to be transcribed") are stored in a config file or app-level settings; this feature reads that configuration. Path/tab editing may be in-app (e.g. settings screen) or by editing the config file. Path configuration supports one or two paths per tab; when two are used, the first is source and the second is destination.
- "Media file" and "paired folder" follow the same definitions as in the media folder pipeline (002-media-folder-pipeline): primary audio/video file and optional folder of same base name containing sister files and outputs.
- The processing pipeline only picks up files from "Videos 1 to be transcribed", not from "Videos not transcribed". When a tab has source and destination paths, the pipeline runs only under the destination path.
- Tab names are stored with the path configuration and displayed as the tab label; if no name is set, a default (path or ordinal) is shown.
- The media sub window in the channel media list uses the same control expectations as the general media viewer (010-media-viewer-subpanel): play/pause, volume, scrubber, jump forward/back.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST list all channel folders that contain a "Videos not transcribed" path, across all configured base folders, so the user can see every channel that has inbox media.
- **FR-002**: System MUST provide an option to "move 3 files" per channel: when the user selects it, the system moves up to 3 media files (and their paired folders) from that channel's "Videos not transcribed" to that channel's "Videos 1 to be transcribed".
- **FR-003**: System MUST provide an option to "move all files" per channel: when the user selects it, the system moves all media files (and their paired folders) from that channel's "Videos not transcribed" to that channel's "Videos 1 to be transcribed".
- **FR-004**: System MUST provide an "explore" option per channel that shows all media files in that channel's "Videos not transcribed".
- **FR-005**: In the explore view, the user MUST be able to select one or more files and trigger "queue selected"; the system MUST then move only the selected media files (and their paired folders) to that channel's "Videos 1 to be transcribed".
- **FR-006**: When moving a media file, the system MUST move its paired folder (folder with same base name as the media file) to the same destination so they remain together.
- **FR-007**: Processing pipeline MUST treat only "Videos 1 to be transcribed" as the queue for processing; files in "Videos not transcribed" MUST NOT be picked up for processing by default.
- **FR-008**: When the user is viewing the list of media for a channel (explore view), the system MUST provide a sub window where the user can view or play the selected media, with controls for play/pause, volume, scrubbing (seek), and jump forward/back.
- **FR-009**: The interface MUST be tabbed so that each configured path has its own tab; the user MUST be able to name the tab when defining or editing the path, and that name MUST be displayed as the tab label.
- **FR-010**: The system MUST allow configuring one or two paths per tab. When two paths are configured, the first is the "source" and the second is the "destination". Media from both paths MUST be presented in a merged list for that tab.
- **FR-011**: When a tab has two paths (source and destination), queuing a file from the source path's "Videos not transcribed" MUST move that file (and its paired folder) to the destination path's corresponding channel "Videos 1 to be transcribed". The processing pipeline MUST run only in the destination path and MUST NOT process files or run pipeline steps in the source path.
- **FR-012**: The channel list and the per-channel media list (explore view) MUST use virtualization or pagination so that hundreds of channels and thousands of media files can be displayed without degrading usability.
- **FR-013**: The system MUST log move actions (what was moved, from path, to path) and move failures (error reason); no metrics dashboard or aggregated counts are required for this feature.

### Key Entities

- **Channel folder**: A directory representing a source (e.g. YouTube channel); contains "Videos not transcribed" (inbox) and "Videos 1 to be transcribed" (queue).
- **Media file**: Primary audio or video file; may have a paired folder of the same base name.
- **Paired folder**: Folder with same base name as the media file; holds the media and sister files; moves with the media when queued.
- **Configured path (base path)**: A root path under which channel folders (e.g. "[Channel]/Videos not transcribed") are discovered; each path may have an optional tab name. A tab may have one path or two sister paths (source and destination).
- **Source path / destination path**: When a tab has two paths, the first is the source (inbox only; files queued from here move to the destination); the second is the destination (queue and pipeline run here only).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Operators can see all channel folders with inbox media in one place and choose to queue 3 files, all files, or cherry-pick after exploring, without using the file system directly.
- **SC-002**: Only files that have been explicitly moved to "Videos 1 to be transcribed" (via this UI or an equivalent action) are eligible for processing; files left in "Videos not transcribed" are not processed.
- **SC-003**: No media or paired folders are lost or split when moving; each moved media file and its paired folder remain together in "Videos 1 to be transcribed".
- **SC-004**: When viewing the list of media for a channel, operators can preview a selected file in a sub window using play/pause, volume, scrubbing, and jump forward/back without leaving the page.
- **SC-005**: When multiple paths are configured, each path has its own tab and tabs can be named by the user so different channel types (e.g. different YouTube channels) are easy to distinguish.
- **SC-006**: When a tab is configured with source and destination paths, queued files move from source inbox to destination queue and the pipeline runs only in the destination path; the merged list shows media from both paths so the operator can queue from either.
