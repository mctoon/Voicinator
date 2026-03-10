# Feature Specification: Web UI to Identify Unknown Speakers

**Feature Branch**: `007-webui-to-identify-unknown-speakers`  
**Created**: 2026-03-10  
**Status**: Draft  
**Input**: Add a new section to the existing web UI that lists all media (videos) that have unidentified speakers. The list is built by searching across all YouTube channel folders for any "Videos 5 needs speaker identification" folder. The user selects a video to process: the transcript is presented like transcript.txt with sections labeled by speaker and time; play/pause controls are fixed at the bottom of the window so they do not scroll off. The user can click on any word in the transcript to play the audio starting at that word; word-level timing MUST be taken from transcript_words.json (or equivalent word-level data in the paired folder) so playback starts at the exact start time of the clicked word. There can be multiple unknown speakers in a video; the speaker name appears in front of each section, and clicking the speaker's name opens a popup to identify that speaker (scrollable list of existing speakers, a text field that narrows the list, Enter to create a new speaker when the typed name is unique, and an option to skip/not-identify). When all speakers are identified or declared not-to-be-identified, a "Complete identification" action is available; using it moves the video (and paired folder) to "Videos 6 speakers matched" and returns the user to the list. An "Unknown Speakers" link MUST appear on the left side of all existing pages so users can reach this section from anywhere in the app.

---

## Clarifications

### Session 2026-03-10

- Q: For videos that have no speakers (e.g. no speech in the video), should they wait for speaker identification? → A: No; move the video to step 6 immediately. No need to wait for speaker identification.
- Q: When a video is selected to process, if a speaker was already identified (e.g. while the video was in queue), how should the system behave? → A: If possible, indicate to the user that the speaker has been identified, allow the user to confirm (or correct) the identification, and upon confirmation add a selection from the current video to that speaker's corpus of identified passages.
- Q: After speakers have been identified, how should the transcript files be updated with the new speaker names? → A: Save the old transcript.txt and transcript_words.json with a different name (e.g. backup), then rewrite transcript.txt and transcript_words.json in the paired folder with the updated names of all the speakers.
- Q: When the user chooses not to identify a speaker, how should that speaker be named? → A: The system MUST generate a globally unique name (no spaces, not too long, readable) so that in the future the user can identify this speaker and all instances of this unique name can be updated with the correct name (e.g. find-replace). Example pattern: a fixed prefix plus a globally unique suffix (e.g. Unidentified-1, Unidentified-2).
- Q: When the user leaves a speaker unassigned or skipped, is a full speaker record created (corpus, media linking)? → A: Yes. A full speaker record is created as if the speaker had been named; only the name is auto-created with the globally unique placeholder. Audio samples (passages) from the current video are captured and added to that speaker's corpus the same as for a named speaker. Future features that link speakers to all media they appear in treat placeholder speakers the same as named speakers.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - List all videos needing speaker identification (Priority: P1)

The system adds a new section to the existing web UI that shows all media (videos) that have unidentified speakers. To build this list, the system searches across all configured YouTube channel folders and finds every file in any folder named "Videos 5 needs speaker identification". The user sees a single list of all such videos (e.g. with channel and filename so they can tell which video is which). The user can select a video from this list to start the identification workflow.

**Why this priority**: Without this list, the user cannot discover which videos need attention; it is the entry point for the feature.

**Independent Test**: Ensure at least one channel has a "Videos 5 needs speaker identification" folder with one or more media files; open the web UI; verify the new section appears and lists those videos; verify videos from multiple channels appear if present.

**Acceptance Scenarios**:

1. **Given** one or more configured base folders with channel folders underneath, **When** the system builds the list of videos needing speaker identification, **Then** it discovers every media file in any "Videos 5 needs speaker identification" folder under any channel in any configured base.
2. **Given** the web UI is open, **When** the user navigates to the new section, **Then** the user sees a list of all such videos (e.g. channel name and media filename or title) so they can choose which video to process.
3. **Given** the list is displayed, **When** the user selects a video, **Then** the user is taken to the identification view for that video (User Story 2).
4. **Given** the user is on any existing page of the web UI (e.g. inbox, pipeline, or other sections), **When** the user looks at the left side of the page, **Then** an "Unknown Speakers" link is visible and selecting it navigates to the list of videos needing speaker identification.

---

### User Story 2 - Review transcript and click-to-play (Priority: P1)

When the user selects a video to process, the system presents the transcript for that video in the same style as transcript.txt: sections labeled by speaker and time (e.g. "Speaker A 0:00" followed by that speaker's text). The user can read the transcript and click on any word to play the audio starting at that word. Word-level timing MUST come from transcript_words.json (or equivalent word-level data in the paired folder) so that playback starts at the exact start time of the clicked word. The user can also click on a section (e.g. segment or line) to start playback at that point. Play/pause controls (and any other playback controls) are placed at the bottom of the window so they remain visible and do not scroll off screen when the user scrolls the transcript.

**Why this priority**: Listening at specific points—including from any word—is essential for verifying which speaker said what and for making correct assignments; exact word timing from transcript_words.json enables precise playback; stable controls avoid losing access to play/pause while scrolling.

**Independent Test**: Select a video from the list; verify the transcript loads in speaker-and-time sections; verify play/pause stays at the bottom when scrolling; click a word and verify playback starts at that word's start time (using timing from transcript_words.json); click a section and verify playback starts at the corresponding time.

**Acceptance Scenarios**:

1. **Given** the user has selected a video from the list of videos needing identification, **When** the identification view loads, **Then** the transcript for that video is displayed in transcript.txt style: sections labeled by speaker and time (e.g. speaker label and timestamp followed by that section's text), using data from the video's paired folder or sidecar.
2. **Given** the identification view is displayed, **When** the user scrolls the transcript, **Then** play/pause (and any other playback) controls remain fixed at the bottom of the window and do not scroll off screen.
3. **Given** the transcript is displayed with word-level timing from transcript_words.json (or equivalent), **When** the user clicks on any word in the transcript, **Then** the system plays the media file starting at that word's start time (the exact timing for that word from the word-level data).
4. **Given** the transcript is displayed, **When** the user clicks on a section of the transcript (e.g. a segment or line), **Then** the system plays the media file starting at the timestamp for that section.
5. **Given** the user is in the identification view, **When** the transcript or media is unavailable (e.g. missing file), **Then** the system shows a clear message and does not leave the user in a broken state.

---

### User Story 3 - Resolve each unidentified speaker (Priority: P1)

There can be multiple unknown speakers in a video. The transcript is shown with each section labeled by speaker (and time); the speaker name or label appears in front of each section. Clicking on the speaker's name for a section opens a popup (or control) to identify that speaker. The popup MUST include: (1) A scrollable list of existing speakers from which the user can choose to assign this speaker; (2) A text field in which the user can type a name to narrow (filter) the list of existing speakers; (3) If the typed name is not in the list and is treated as totally unique, pressing Enter MUST create a new speaker with that name and resolve this section's speaker as that new speaker; (4) An option to skip/not-identify that speaker (e.g. "Skip" or "Do not identify"). Once the user has assigned to an existing speaker, created a new speaker (by typing a unique name and Enter), or chosen not to identify, that speaker is considered resolved for this video.

**Why this priority**: Resolving each unknown speaker is the core task; identify-by-click in context (next to that speaker's text), with list + filter + create-on-unique-Enter and skip, covers the necessary outcomes.

**Independent Test**: Open a video with two unidentified speakers; click one speaker name in the transcript and assign to an existing speaker from the popup; click the other and type a new unique name and press Enter to create; verify both resolved. Repeat with "skip/not identify" and verify the speaker is treated as resolved for completion.

**Acceptance Scenarios**:

1. **Given** the identification view for a video with one or more unidentified speakers, **When** the transcript is displayed, **Then** each section is labeled by speaker (and time) and the speaker name or label is shown in front of that section so the user can click it to identify that speaker.
2. **Given** the user clicks on a speaker name in the transcript, **When** the popup opens, **Then** the user sees: a scrollable list of existing speakers; a text field that narrows (filters) that list as the user types; the ability to press Enter when the typed name is unique to create a new speaker and resolve this one; and an option to skip/not-identify that speaker.
3. **Given** the user types a name in the popup that does not match any existing speaker (totally unique), **When** the user presses Enter, **Then** the system creates a new speaker with that name and resolves the clicked speaker as that new speaker for this video.
4. **Given** the user selects "skip" or "not identify" in the popup, **Then** the system creates a full speaker record (as for a named speaker) with an auto-assigned globally unique placeholder name (no spaces, readable, e.g. Unidentified-1); that speaker is considered resolved. The same placeholder name is used for all segments attributed to that speaker. Passage(s) from the current video are added to that speaker's corpus, and the speaker is linked to media for future features the same as a named speaker.
5. **Given** the user has resolved a speaker (assigned, created, or declined), **When** the user inspects the transcript or list, **Then** that speaker is clearly indicated as resolved (e.g. checkmark, "Resolved" label, or non-clickable/disabled for that speaker) so the user can see progress toward completing identification.
6. **Given** the identification view for a video, **When** the system can determine that an unidentified speaker has already been identified (e.g. while the video was in queue—by matching to an existing speaker), **Then** the system indicates this to the user (e.g. suggested identification) and allows the user to confirm or correct; upon user confirmation, the system adds the relevant passage(s) from the current video to that speaker's corpus of identified passages (e.g. voice library).

---

### User Story 4 - Complete identification and move to "Videos 6 speakers matched" (Priority: P1)

When every unidentified speaker for the selected video has been resolved (either identified as existing, created with a name, or declared not-to-be-identified), a "Complete identification" control (e.g. button) becomes active. When the user selects it, the system moves the media file and its paired folder from "Videos 5 needs speaker identification" to the appropriate "Videos 6 speakers matched" folder for that channel. The user is then navigated back to the list of videos needing identification; the video just completed no longer appears in that list because it is no longer in a "Videos 5 needs speaker identification" folder.

**Why this priority**: Completing the workflow and moving the file to the next pipeline step is the expected outcome; returning to the list keeps the user in the same workflow.

**Independent Test**: Resolve all speakers for a video (mix of assign, create, and decline); verify "Complete identification" is enabled; click it and verify the file (and paired folder) move to "Videos 6 speakers matched" for that channel and the UI returns to the list with that video removed.

**Acceptance Scenarios**:

1. **Given** the identification view for a video, **When** at least one speaker remains unresolved, **Then** the "Complete identification" control is inactive or hidden (or clearly disabled with reason).
2. **Given** all unidentified speakers have been resolved (assigned, created, or declined), **When** the user inspects the UI, **Then** the "Complete identification" control is active and selectable.
3. **Given** all speakers are resolved and the user selects "Complete identification", **When** the system processes the action, **Then** the media file and its paired folder are moved from the channel’s "Videos 5 needs speaker identification" folder to that same channel’s "Videos 6 speakers matched" folder.
4. **Given** the move has completed successfully, **When** the user is returned to the list view, **Then** the user sees the list of videos still needing identification (the completed video no longer appears), and the user can select another video to process.
5. **Given** the user has completed identification for a video (all speakers resolved and move to "Videos 6 speakers matched"), **When** the system finalizes the identification, **Then** the system saves the existing transcript files (e.g. transcript.txt and transcript_words.json) in the paired folder under a different name (e.g. backup) and rewrites transcript.txt and transcript_words.json with the updated speaker names applied throughout.

---

### Edge Cases

- What happens when no "Videos 5 needs speaker identification" folders exist or all are empty? The list is empty; the UI shows an empty state (e.g. message that no videos need identification) rather than an error.
- What happens when the user selects a video whose transcript or media file has been deleted or moved outside the pipeline? The system shows a clear error (e.g. file not found) and allows the user to go back to the list; the file may remain in the list until it is removed from the folder or the list is refreshed.
- What happens when the user refreshes the list after completing a video? The list reflects the current state of the file system; the completed video no longer appears because it is now in "Videos 6 speakers matched".
- What happens when two users (or the same user in two tabs) complete identification for the same video? The system moves the file once; the second completion attempt should either see the file already moved (and show an appropriate message or redirect) or safely no-op so that duplicate moves or inconsistent state are avoided.
- What happens when the user creates a new speaker with an empty or duplicate name? The system MAY NOT allow empty or duplicate display names; it MUST validate and show a clear message so the user can correct.
- What happens when the user later identifies a speaker that was left as "not identified"? The placeholder name (e.g. Unidentified-42) is globally unique and can be found and replaced across transcript files and any stored references so that all instances are updated with the correct name; the exact bulk-update flow is out of scope for this spec but the naming method enables it.
- What happens when "Videos 6 speakers matched" does not exist for that channel? The system MUST create the folder (or use the configured step folder for "speakers matched") so the move can succeed; behavior MUST be consistent with the pipeline folder plan (e.g. 002-media-folder-pipeline).
- What happens when the user navigates away without completing identification? No move occurs; the video remains in "Videos 5 needs speaker identification"; any resolutions (assignments, new speakers, declines) may be saved so the user can return and finish later, or the system may require completing in one session. Implementation MUST document this behavior (e.g. in quickstart or developer docs).
- What happens when a video has no speakers (e.g. no speech in the content)? The system MUST move the video (and its paired folder) to "Videos 6 speakers matched" immediately; no manual speaker identification is required. Such videos may be moved by the pipeline before they appear in the list, or the UI may exclude them from the list / auto-move them when discovered.
- What happens when the system suggests an existing speaker for an unidentified speaker but the user disagrees? The user can correct the identification (choose a different existing speaker, create new, or decline); only upon user confirmation is the suggested speaker treated as resolved and are passages from the current video added to that speaker's corpus of identified passages.
- What happens when transcript files (transcript.txt, transcript_words.json) are missing at the time of updating? The system MUST NOT overwrite arbitrary paths; if the files are absent, the system MAY skip the transcript update and log it, or MAY create the updated files from segment/word data and resolutions. The choice (skip vs create) is an implementation decision documented in research.md; see tasks.md T023.

---

## Assumptions

- The pipeline folder layout and names ("Videos 5 needs speaker identification", "Videos 6 speakers matched") are as defined in the media-folder-pipeline (e.g. 002); channel structure is [base]/[Channel Name]/[step folder]/.
- Transcript and diarization data (including segment/speaker labels and timings) are stored in the paired folder or sidecar for each media file and are available to the web UI.
- "Existing speakers" are those already known to the system (e.g. from a speaker database or local store per 002); the exact source is out of scope for this spec.
- The existing web UI can be extended with a new section and new views without redefining the whole app.
- Playback uses the original media file (or an extracted audio track) at the correct path; the system has read access to media in the pipeline folders.
- Videos with no speakers (e.g. no speech) are moved to "Videos 6 speakers matched" immediately by the pipeline or when discovered by the UI; they do not require manual speaker identification.
- Transcript files in the paired folder are named transcript.txt (human-readable) and transcript_words.json (word-level with timings); after speaker identification is completed, these are updated with speaker names by first saving the originals under a different name, then writing the updated versions. Word-level start (and end) times in transcript_words.json are used so the user can click any word in the transcript to start playback at that word's exact start time.
- Placeholder names for "not identified" speakers use a fixed prefix and a globally unique suffix, with no spaces, so they are readable and easy to find-replace when the speaker is later identified (e.g. Unidentified-1, Unidentified-2). A full speaker record is created for each placeholder speaker (same as for a named speaker); passages are added to that speaker's corpus, and future features that link speakers to media treat placeholders the same as named speakers.
- Navigate-away behavior (whether resolutions are saved for later or single-session is required) MUST be documented in quickstart or developer docs; see Edge Cases and tasks.md T026.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a new section in the existing web UI that lists all media files (videos) that need speaker identification. The list MUST be built by discovering every "Videos 5 needs speaker identification" folder under any channel in any configured base folder and including every media file in those folders.
- **FR-002**: The list MUST be presented so the user can identify each video (e.g. by channel name and media filename or title) and select one to process.
- **FR-003**: When the user selects a video from the list, the system MUST open an identification view that displays the transcript in the same style as transcript.txt (sections labeled by speaker and time). The view MUST support playback of the media when the user clicks any word in the transcript: playback MUST start at that word's start time, using the exact word-level timing from transcript_words.json (or equivalent word-level data in the paired folder). The view MUST also support playback when the user clicks a section (e.g. segment or line). Play/pause and other playback controls MUST be placed at the bottom of the window so they do not scroll off screen when the user scrolls the transcript.
- **FR-004**: The identification view MUST show the transcript with each section labeled by speaker (and time); the speaker name or label appears in front of each section. Clicking a speaker name MUST open a popup (or control) to identify that speaker. The popup MUST include: (a) a scrollable list of existing speakers to assign to; (b) a text field that narrows (filters) the list as the user types; (c) when the typed name is not in the list and is treated as totally unique, pressing Enter MUST create a new speaker with that name and resolve that speaker for this video; (d) an option to skip/not-identify that speaker. Once the user has assigned to an existing speaker, created a new speaker (unique name + Enter), or chosen not to identify, that speaker is considered resolved for this video.
- **FR-005**: When the user creates a new speaker, the user MUST be able to type the speaker’s name; the system MUST store that name as the identity of the new speaker.
- **FR-005b**: When the user chooses not to identify a speaker, the system MUST create a full speaker record (as if the speaker had been named) with an auto-generated globally unique placeholder name. The name MUST contain no spaces, MUST be readable, and MUST be unique across the system. Length is bounded by the pattern (fixed prefix plus decimal integer, e.g. Unidentified-1) and MUST NOT exceed 64 characters so that future identification can update all instances of this name (e.g. find-replace across transcripts and stored data). Example pattern: a fixed prefix plus a globally unique suffix (e.g. Unidentified-1, Unidentified-2). The system MUST add passage(s) from the current video to that speaker's corpus and MUST treat the speaker as first-class for future features (e.g. linking speakers to all media they appear in), same as a named speaker.
- **FR-006**: When every unidentified speaker for the video has been resolved (assigned, created, or declined), a "Complete identification" control MUST become active. When the user selects it, the system MUST move the media file and its paired folder from that channel’s "Videos 5 needs speaker identification" folder to that channel’s "Videos 6 speakers matched" folder, and MUST navigate the user back to the list of videos needing identification. (The control’s enabled/disabled state is defined in FR-007.)
- **FR-007**: The "Complete identification" control MUST be inactive or disabled until all unidentified speakers for the current video have been resolved. (When all are resolved, it becomes active per FR-006.)
- **FR-007a**: For each resolved speaker (in the transcript or any list), the system MUST show at least one of: a checkmark, a "Resolved" label, or a non-clickable/disabled identify control for that speaker, so that progress toward completing identification is testable.
- **FR-008**: If the transcript or media file for the selected video is missing or unavailable, the system MUST show a clear error and MUST allow the user to return to the list without leaving the UI in a broken state.
- **FR-009**: Videos with no speakers (e.g. no speech in the content) MUST NOT require manual speaker identification. The system MUST move such videos (and their paired folders) to "Videos 6 speakers matched" immediately—either when the pipeline determines there are no speakers (so they never remain in "Videos 5 needs speaker identification") or when the UI or list-building logic discovers the video has zero speakers (e.g. exclude from list and move to step 6).
- **FR-010**: When the user selects a video to process and the system can determine that one or more unidentified speakers have already been identified (e.g. matched to an existing speaker while the video was in queue), the system MUST indicate this to the user (e.g. suggested identification) and MUST allow the user to confirm or correct. Upon user confirmation of the identification, the system MUST add the relevant passage(s) from the current video to that speaker's corpus of identified passages (e.g. voice library usable for fingerprinting or retraining).
- **FR-011**: After all speakers for a video have been identified (and before or when the media is moved to "Videos 6 speakers matched"), the system MUST update the transcript files in the paired folder with the resolved speaker names. The system MUST save the existing transcript.txt and transcript_words.json under a different name (e.g. backup), then MUST rewrite transcript.txt and transcript_words.json so that all speaker labels are replaced with the updated names (resolved speaker names or placeholders for "not identified").
- **FR-012**: An "Unknown Speakers" link MUST appear on the left side of all existing pages of the web UI so that users can navigate to the list of videos needing speaker identification from anywhere in the app.

### Key Entities

- **Videos needing identification**: The set of media files that appear in any "Videos 5 needs speaker identification" folder under any configured channel; these are the items shown in the new list section.
- **Identification view**: The screen where the user sees the transcript in transcript.txt style (sections by speaker and time), with play/pause and playback controls fixed at the bottom; the user can click any word to play from that word's start time (using transcript_words.json word-level timing) or click a section to start playback; the user clicks speaker names to open the identify popup (scrollable list of existing speakers, filter field, Enter to create when unique, skip option); includes the "Complete identification" action when all speakers are resolved.
- **Unidentified speaker**: A speaker label (e.g. from diarization) for the current video that has not yet been assigned to an existing speaker, created as a new speaker with a name, or explicitly declined.
- **Resolved speaker**: For this video, a speaker that has been assigned to an existing speaker, created as a new speaker with a name, or marked as not-to-be-identified (and given a system-generated globally unique placeholder name). In all three cases the system maintains a full speaker record; placeholder speakers receive the same treatment as named speakers (corpus, media linking).
- **Placeholder name**: A system-generated name for a speaker the user chose not to identify; globally unique, no spaces, readable, length bounded by pattern Unidentified-<N> (e.g. Unidentified-1); enables future bulk update when the speaker is later identified. The speaker is stored as a full record with corpus and media-appearance linkage, same as a named speaker.
- **Existing speaker**: A speaker already known to the system (e.g. in the speaker database or local store), whom the user can assign to an unidentified speaker.
- **Speaker's corpus of identified passages**: The set of audio or transcript passages associated with a speaker that have been used to identify or characterize them (e.g. voice library). When the user confirms an identification (including a system-suggested one), or when the user chooses not to identify (placeholder), passage(s) from the current video are added to this corpus for that speaker. Placeholder speakers receive the same corpus treatment as named speakers.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can open the web UI and see a single list of all videos that need speaker identification, built from all "Videos 5 needs speaker identification" folders across all configured channel folders.
- **SC-002**: Users can select a video from the list, see its transcript in transcript.txt style (sections by speaker and time) with play/pause at the bottom, and click any word (or a section) to start playback at that word's or section's time, using word-level timing from transcript_words.json for words; controls do not scroll off screen.
- **SC-003**: Users can resolve every unidentified speaker by clicking the speaker name in the transcript to open the identify popup (list, filter, Enter to create when unique, skip); the UI clearly shows which speakers are resolved.
- **SC-003a**: From any existing page, users see an "Unknown Speakers" link on the left and can use it to reach the list of videos needing speaker identification.
- **SC-004**: When all speakers are resolved, the user can use "Complete identification" to move the video (and paired folder) to "Videos 6 speakers matched" and is returned to the list; the completed video no longer appears in the list.
- **SC-005**: No video is moved to "Videos 6 speakers matched" until every unidentified speaker for that video has been resolved (assigned, created, or declined)—or the video has no speakers, in which case it is moved to step 6 immediately; the "Complete identification" action is only available when all speakers are resolved (or there are none).
- **SC-006**: When the system can suggest an existing identification for an unidentified speaker (e.g. because the speaker was identified while the video was in queue), the user sees the suggestion and can confirm or correct; upon confirmation, passage(s) from the current video are added to that speaker's corpus of identified passages.
- **SC-007a**: When the user chooses not to identify a speaker (placeholder), the system creates a full speaker record with that placeholder name, adds passage(s) from the current video to that speaker's corpus, and treats the speaker the same as a named speaker for future features (e.g. linking speakers to all media they appear in).
- **SC-007**: After speaker identification is completed for a video, the transcript files (transcript.txt and transcript_words.json) in the paired folder are updated with the resolved speaker names; the previous versions are kept under a different name before the updated files are written.
