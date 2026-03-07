# Feature Specification: Speaker Voice Library

**Feature Branch**: `008-speaker-voice-library`  
**Created**: 2026-03-02  
**Status**: Draft  
**Input**: When an unidentified speaker is manually matched to an existing speaker, add the newly identified clips to that speaker's voice library. Each speaker has a library of clips used to identify them, usable later for retraining. Web interface to review a media file: transcript displayed with each speaker tagged; user can click individual words to play audio from that word. User can select a section of the transcript and export that section as a media clip (same quality as original, typically video) to an export folder; export folder is a web UI preference.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add new clips to existing speaker when matching (Priority: P1)

During manual speaker identification, when the user identifies an unknown segment as an existing speaker (e.g. "this is John Doe"), the system adds the newly identified clip or clips (the audio segments that were just attributed to that speaker) to that speaker's voice library. The voice library is the set of audio clips that have been used to identify or characterize that speaker, so that over time each speaker accumulates a library of samples. This supports better fingerprinting and future retraining.

**Why this priority**: Core behavior: matching to an existing speaker must update that speaker's library so the system improves with use.

**Independent Test**: In the unknown-speakers web UI, match one segment to an existing speaker; verify that the clip (or a reference to it) is added to that speaker's voice library and is visible or usable for that speaker.

**Acceptance Scenarios**:

1. **Given** the user has identified a segment (or cluster) as belonging to an existing speaker in the speaker database, **When** the user confirms the match, **Then** the system adds the newly identified clip(s) to that speaker's voice library.
2. **Given** a speaker's voice library, **When** the user or system inspects it, **Then** the library contains all clips that have been added via enrollment and all clips added when the user matched unknown segments to this speaker during manual identification.
3. **Given** multiple segments from the same media file matched to the same existing speaker, **When** the user confirms, **Then** the system adds each distinct clip (or the relevant audio segments) to that speaker's voice library.

---

### User Story 2 - Each speaker has a voice library (Priority: P1)

Every speaker in the system has a voice library: a collection of audio clips that were used to identify or characterize that speaker. Clips may come from initial enrollment (e.g. 30–60 s samples) and from later manual identification (when unknown segments are matched to this speaker). The library is stored durably so it can be used for fingerprint updates and, in the future, for retraining models.

**Why this priority**: The voice library is the data asset that enables "add to fingerprint" and future retraining; every speaker must have one.

**Independent Test**: Create or select a speaker; add one clip via manual match; verify the speaker's library contains that clip; verify the library persists and is associated with that speaker.

**Acceptance Scenarios**:

1. **Given** a speaker (enrolled or created), **When** the system stores that speaker, **Then** that speaker has an associated voice library (possibly empty at creation).
2. **Given** a speaker's voice library, **When** clips are added (via enrollment or manual match), **Then** the library retains those clips and they remain associated with that speaker.
3. **Given** a speaker's voice library, **When** a retraining or fingerprint-update process runs (in a later feature), **Then** the library can be used as the set of reference clips for that speaker. (This spec does not define the retraining process; it only requires that the library exists and is usable for that purpose.)

---

### User Story 3 - Web interface to review a media file with transcript and click-to-play (Priority: P2)

The system provides a web interface that allows the user to review a media file. The transcript is displayed with each speaker tagged (e.g. speaker name or label on each segment or word). The user can click on individual words in the transcript; when they do, the system plays the media file (audio or video) starting at that word's timestamp. This supports precise review and verification of speaker labels and content.

**Why this priority**: Supports manual identification and quality review; click-to-play by word makes it easy to verify and correct speaker assignments.

**Independent Test**: Open the web UI; open a media file with a transcript; verify the transcript shows speaker tags; click a word and verify playback starts at that word's position.

**Acceptance Scenarios**:

1. **Given** the user has access to the web interface, **When** the user selects a media file (e.g. from the unknown-speakers list or from search), **Then** the user can open a review view for that media file.
2. **Given** the review view for a media file that has a transcript, **When** the view loads, **Then** the transcript is displayed with each speaker tagged (e.g. speaker name or identifier visible for each segment or word).
3. **Given** the transcript is displayed, **When** the user clicks on an individual word, **Then** the system plays the media file (audio or video) starting at that word's timestamp (e.g. start time from word-level timing).
4. **Given** the review view, **When** the media file has unknown speakers, **Then** the user can perform speaker identification (match to existing, create new, or placeholder) as in the media-folder-pipeline spec; when matching to an existing speaker, the new clips are added to that speaker's voice library (User Story 1).

---

### User Story 4 - Export selected transcript section as media clip (Priority: P2)

The user can select a contiguous section of the transcript in the review view (e.g. by highlighting a range of words or segments). The user then chooses to export that section. The system uses the original media file (typically a video) and renders a clip that contains only the selected section, in the same quality as the original recording. The clip is written to an export folder on the file system. The export folder path is a web UI preference (configurable by the user in the web interface).

**Why this priority**: Enables users to extract and reuse portions of media (e.g. for highlights, clips, or training samples) without re-encoding or losing quality.

**Independent Test**: In the review view, select a 30-second span of the transcript; choose export; verify a clip file appears in the configured export folder and matches the selected time range and original quality.

**Acceptance Scenarios**:

1. **Given** the user is in the review view with a transcript and word-level (or segment-level) timings, **When** the user selects a contiguous section of the transcript, **Then** the user can invoke an action to export that section as a media clip.
2. **Given** the user has selected a section and chosen to export, **When** the system processes the request, **Then** the system uses the original media file and produces a clip that contains only the selected time range, in the same quality as the original recording (e.g. same codec, resolution, bitrate for video; same sample rate for audio).
3. **Given** the clip is produced, **When** the system saves it, **Then** the clip is written to the export folder that the user has configured in the web UI preferences.
4. **Given** the web UI has a preferences or settings area, **When** the user sets the export folder, **Then** the system stores that path and uses it for subsequent export operations until the user changes it.

---

### Edge Cases

- What happens when the same clip is matched to the same speaker twice? The system SHOULD avoid storing duplicate clips in the voice library (e.g. by content hash or segment identity); duplicate entries are not required.
- What happens when a speaker is merged or deleted? The voice library for the removed or merged speaker is handled according to data-retention and merge policy; this spec does not define merge/delete behavior beyond requiring that each speaker has a library while they exist.
- What happens when storage for clips is limited? The system MAY apply retention or quota rules (e.g. max clips per speaker, or max total size); such rules are out of scope for this spec unless added later.
- What happens when the user cancels the match before confirming? No clip is added to any speaker's library.
- What happens when the export folder is not set or invalid? The system MUST prompt the user to set a valid export folder or MUST show a clear error and not overwrite arbitrary locations.
- What happens when the selected transcript section is empty or a single word? The system MAY allow export (producing a very short clip) or MAY enforce a minimum duration; behavior should be consistent and predictable.
- What happens when the original media file is missing or moved? The system MUST report an error and MUST NOT create a clip from stale or missing source media.

---

## Assumptions

- Manual speaker identification (match to existing, create new, placeholder) is implemented as in 002-media-folder-pipeline; this feature adds the behavior of updating the existing speaker's voice library when a match is confirmed.
- "Clip" means the audio segment(s) corresponding to the segment or cluster the user identified (e.g. 5–10 s or the diarized segment); the system may store the raw audio, a reference to it, or both.
- Voice libraries are used later for retraining; the retraining process itself is out of scope for this spec.
- The original media file (typically video) is available at a path the system can read; export uses that file to render the clip (same quality means no unnecessary re-encoding or downscaling).
- Word-level (or segment-level) timestamps are available in the transcript so that click-to-play and section export can use accurate start/end times.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: When the user, during manual speaker identification, matches an unidentified segment (or cluster) to an existing speaker and confirms, the system MUST add the newly identified clip(s) to that speaker's voice library.
- **FR-002**: Each speaker MUST have an associated voice library: a durable collection of audio clips that have been used to identify or characterize that speaker (from enrollment and from manual match events).
- **FR-003**: The system MUST retain clips added to a speaker's voice library so that they remain available for fingerprint updates and for future use in retraining.
- **FR-004**: The system MUST provide a web interface that allows the user to open and review a media file; the review view MUST display the transcript with each speaker tagged and MUST support speaker identification when the file has unknown speakers; when the user matches a segment to an existing speaker, the system MUST add the new clip(s) to that speaker's voice library (FR-001).
- **FR-005**: In the review view, when the user clicks on an individual word in the transcript, the system MUST play the media file (audio or video) starting at that word's timestamp (using word-level or segment-level timing).
- **FR-006**: In the review view, the user MUST be able to select a contiguous section of the transcript and choose to export that section; the system MUST produce a media clip from the original media file that contains only the selected time range, in the same quality as the original recording, and MUST write the clip to the user-configured export folder.
- **FR-007**: The web UI MUST provide a preference (e.g. in settings) for the export folder path; the system MUST use that path for export operations and MUST persist the preference until the user changes it.
- **FR-008**: The voice library for a speaker MUST be queryable or inspectable (e.g. to list clips, count, or export for retraining) so that downstream processes (e.g. retraining) can use it. The exact API or UI for querying is not specified here.

### Key Entities

- **Speaker**: An identified or placeholder person; has a name and a voice library.
- **Voice library**: The set of audio clips associated with a speaker that were used to identify or characterize them; grows when enrollment clips are added and when the user matches unknown segments to this speaker during manual identification; usable for fingerprint updates and retraining.
- **Clip**: An audio segment (or reference to it) stored in a speaker's voice library; corresponds to a segment or cluster that was attributed to that speaker via enrollment or manual match.
- **Review view**: The web UI view in which the user reviews a media file; displays the transcript with speaker tags; supports click-to-play from a word; supports selecting a transcript section and exporting it as a media clip; supports speaker identification; when the user matches to an existing speaker, triggers addition of new clips to that speaker's voice library.
- **Export folder**: A file-system path configured by the user in the web UI preferences; used as the destination for exported media clips (transcript-section exports).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: When a user matches an unidentified segment to an existing speaker and confirms, the clip(s) for that segment are added to that speaker's voice library in 100% of cases (no silent failures).
- **SC-002**: Every speaker has an associated voice library; clips added via enrollment or manual match persist and remain associated with that speaker.
- **SC-003**: The voice library for any speaker can be used (by a later process or feature) as the set of reference clips for that speaker (e.g. for retraining); the system does not discard or lose clips without an explicit retention policy.
- **SC-004**: Users can open a media file in a web review view, see the transcript with speaker tags, click a word to play from that word, and perform speaker identification; when they match to an existing speaker, the new clips are added to that speaker's voice library as in SC-001.
- **SC-005**: Users can select a section of the transcript in the review view and export that section as a media clip in the same quality as the original; the clip is saved to the user-configured export folder.
- **SC-006**: The export folder is configurable in the web UI and is used consistently for transcript-section exports.
