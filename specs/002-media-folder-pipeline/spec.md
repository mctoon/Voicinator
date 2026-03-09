# Feature Specification: Local Media Folder Pipeline

**Feature Branch**: `002-media-folder-pipeline`  
**Created**: 2026-03-02  
**Status**: Draft  
**Input**: Media on local file system; multiple configured base folders; structure [YouTube Channel]/Videos not transcribed/; files move through numbered step folders; sister files in paired folder; transcript with per-word sub-second timing and Otter-style per-speaker TXT; unknown speakers to numbered folder; web UI to find those files, listen to speaker, and identify (existing speaker + add sample, new speaker with name, or unknown with placeholder).

---

## Clarifications

### Session 2026-03-07

- Q: If a second pipeline run is started before the first finishes, what should the system do? → A: Only one pipeline run at a time; reject or queue new runs until the current run finishes.
- Q: If the speaker database is not yet available at first release, how should "identify as existing" and "add sample" behave? → A: Full UI/API; stub implementation (all segments unknown; persist new/placeholder locally or in files until real DB exists).
- Q: Should the system log each pipeline run and each step outcome for operator debugging? → A: Yes; log each run start/end and each step outcome (success or failure) per file to a configurable log sink (e.g. file or stdout).
- Q: When the pipeline runs, process a bounded number of files per run or all files in step 1? → A: Always process all discovered files in step 1; no limit.
- Q: Must the unknown-speakers web UI include an explicit action to move a file to "Videos" after resolution? → A: Automatically move to the next step in the pipeline once all speakers have been identified (no explicit button required).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Process media from configured folders (Priority: P1)

The operator configures one or more base folders on the local file system. Under each base folder there are many channel folders, each named like a YouTube channel. Media is queued in "Videos 1 to be transcribed" (after being moved from "Videos not transcribed" via the inbox-queue web UI). The system discovers media in "Videos 1 to be transcribed", processes it through the defined sequence of step folders (Videos 2 audio extracted through Videos 7 summarization done, then Videos 8 export ready), and moves each file (and its paired assets folder) to the next step as work completes. When processing is fully complete, the media file is moved to the channel’s final "Videos" folder.

**Why this priority**: Core value is moving media through a clear, repeatable pipeline so operators know where each file is in the workflow.

**Independent Test**: Configure one base folder with one channel; place one media file in "Videos 1 to be transcribed"; run the pipeline; verify the file appears in the correct step folders in order and finally in "Videos".

**Acceptance Scenarios**:

1. **Given** one or more configured base folders, **When** the system runs, **Then** it discovers all "Videos 1 to be transcribed" paths under each base (pattern: [base]/[Channel Name]/Videos 1 to be transcribed/).
2. **Given** a media file in "Videos 1 to be transcribed", **When** a processing step completes for that file, **Then** the media file is moved to the next step folder (e.g. from Videos 3 transcribed to Videos 4 diarized) within the same channel.
3. **Given** a media file that has completed all processing steps with no unknown speakers, **When** the pipeline finishes, **Then** the media file is moved to [Channel Name]/Videos.
4. **Given** multiple base folders, **When** the system runs, **Then** it processes media from all configured bases according to the same folder rules.

---

### User Story 2 - Sister files and paired asset folder (Priority: P1)

A media file in "Videos 1 to be transcribed" (or in any step folder) may have sister files: same base filename with different extensions or suffixes (e.g. .srt, .description, .info.json). The system treats the primary media file and all sister files as one unit. All of these are accumulated into (or kept in) a single folder that has the same base name as the media file. This paired folder moves with the media file through every step (Videos 2 audio extracted through Videos 7 summarization done and Videos 8 export ready) and into the final "Videos" folder. Any new files produced during processing (e.g. transcripts, exports) are stored in this same paired folder.

**Why this priority**: Keeps all assets for a piece of media in one place and avoids losing metadata or sidecar files when moving through steps.

**Independent Test**: Place a media file and two sister files (same base name, different extensions) in "Videos 1 to be transcribed"; run pipeline; verify one folder named like the base name exists at each step and in "Videos", and contains the media, sister files, and new output files.

**Acceptance Scenarios**:

1. **Given** a media file and sister files (same base name, different extensions/suffixes) in "Videos 1 to be transcribed", **When** the system picks up the media file, **Then** it creates or uses a folder with the same base name as the media file and places (or keeps) the media and all sister files in that folder.
2. **Given** a media file and its paired folder at step N, **When** the file is moved to step N+1, **Then** the paired folder is moved to the same step N+1 location so it remains alongside the media file.
3. **Given** processing that produces new files (e.g. transcript, TXT), **When** those files are written, **Then** they are written into the paired folder for that media file.
4. **Given** a media file that reaches the final "Videos" folder, **When** the move occurs, **Then** the paired folder (with all contents) is also moved to the same channel’s "Videos" area so that the folder and media remain together.

---

### User Story 3 - Transcript outputs: word-level timing and human-readable per-speaker (Priority: P1)

For each processed media file, the system produces (at least) two transcript outputs in the paired folder: (1) A transcript with per-word timings at the best precision available, to sub-second resolution. (2) A plain-text transcript formatted for human reading, with per-speaker content and paragraph-level speaker indications, similar to how Otter presents speaker-labeled transcripts.

**Why this priority**: Word-level timing enables downstream tools and search; human-readable per-speaker transcript is the main consumable output for reviewers.

**Independent Test**: Process one media file with two speakers; open the paired folder; verify one file contains word-level timestamps (sub-second) and another is a readable TXT with clear speaker labels at paragraph level.

**Acceptance Scenarios**:

1. **Given** a media file that has been fully transcribed and diarized, **When** outputs are written, **Then** a transcript file exists in the paired folder with every word (or token) associated with a start and end time at sub-second precision.
2. **Given** the same processed file, **When** outputs are written, **Then** a separate TXT file exists in the paired folder that presents the transcript by speaker with paragraph-level speaker indications (e.g. "Speaker A:" or speaker name followed by blocks of text), suitable for human reading.
3. **Given** the word-level transcript, **When** a user or tool inspects it, **Then** timing values are precise to at least one decimal place (e.g. seconds and tenths, or milliseconds) so that sub-second alignment is possible.

---

### User Story 4 - Unknown speakers: numbered holding folder (Priority: P2)

When a media file is transcribed and one or more speakers are not identified (unknown speakers), the file is not moved directly to the final "Videos" folder. Instead, it is moved to the designated step folder "Videos 5 needs speaker identification". The exact step number and folder name are specified in the processing folder plan. The paired folder moves with the media. This allows operators to review, enroll, or correct speaker identity before optionally moving the file to "Videos".  Any associated files needed for the fingerprinting are to be stored in the sidecar folder.

**Why this priority**: Ensures files needing speaker review are separated from fully complete files without blocking the pipeline.

**Independent Test**: Process a file that results in at least one unknown speaker; verify the media (and paired folder) end up in the designated unknown-speakers step folder, not in "Videos".

**Acceptance Scenarios**:

1. **Given** a media file that has been transcribed and diarized and at least one speaker is unknown, **When** the pipeline completes that file’s processing, **Then** the media file and its paired folder are moved to the configured unknown-speakers step folder (Videos 5 needs speaker identification), not to "Videos".
2. **Given** a media file in the unknown-speakers folder, **When** an operator later resolves or accepts speakers (out of scope of this spec), **Then** the file may be moved to "Videos" by the same or another process; the spec only requires that the pipeline places unknown-speaker files in the designated step folder.
3. **Given** a media file with all speakers identified, **When** the pipeline completes, **Then** the file is moved to "Videos" and never to the unknown-speakers step folder.

---

### User Story 5 - Web UI: Resolve unknown speakers (Priority: P2)

When media files are in the designated unknown-speakers step folder (Videos 5 needs speaker identification), the web UI surfaces these files so the operator can listen to each speaker segment and resolve identity. The user can: (1) Identify the speaker as an existing speaker in the database and add the current audio sample to that speaker's fingerprint; (2) Create a new speaker and assign a name; or (3) Mark the speaker as unknown and create a placeholder name. Once speakers are resolved, the media can be treated as complete (e.g. moved to "Videos" by this or another process).

**Why this priority**: Completes the pipeline by allowing operators to fix or accept unknown speakers without leaving the system; enables fingerprint growth and consistent naming.

**Independent Test**: Open web UI; verify it lists media from the unknown-speakers folder; play one speaker segment; resolve as existing speaker (or new or placeholder); verify the choice is persisted and the file can progress to "Videos".

**Acceptance Scenarios**:

1. **Given** one or more media files in the configured unknown-speakers step folder (Videos 5 needs speaker identification), **When** the user opens the web UI, **Then** the system discovers and lists these files (and their paired folders) across all configured base folders.
2. **Given** a listed media file with unknown speakers, **When** the user selects a speaker segment, **Then** the user can play or listen to that segment for the purpose of identification.
3. **Given** the user is listening to a speaker segment, **When** the user identifies that speaker as an existing speaker in the speaker database, **Then** the system adds the current audio sample to that speaker's fingerprint and associates the segment with that speaker.
4. **Given** the user is listening to a speaker segment, **When** the user creates a new speaker and provides a name, **Then** the system creates the new speaker and associates the segment with that speaker.
5. **Given** the user is listening to a speaker segment, **When** the user indicates the speaker is unknown, **Then** the system creates a placeholder speaker name for that speaker and associates the segment with it.
6. **Given** all unknown speakers for a media file have been resolved (existing, new, or placeholder), **When** the user completes resolution, **Then** the system automatically moves the media file and its paired folder to the next step in the pipeline (step 6 → 7 → 8 → Videos).

---

### Edge Cases

- What happens when a base folder or channel folder is missing or renamed? System MUST report or log the issue and MUST NOT corrupt or move files outside the defined structure.
- What happens when the same base filename appears in more than one channel? Each channel’s copy is treated independently; folder names and moves are scoped per channel.
- What happens when a paired folder already exists (e.g. from a previous run)? System MUST use that folder and add or update files in it rather than creating duplicates.
- What happens when a processing step fails mid-run? System MUST leave the file in the current step folder (or leave it in the previous step) so that re-runs can resume; no partial move to the next step without completing the step’s work.
- What happens when there are no sister files? The paired folder still exists (named after the media base name) and contains only the media file until processing adds outputs.
- What happens when the user closes the web UI without resolving all unknown speakers? The media file remains in the unknown-speakers folder until the user returns and completes resolution; no data is lost.
- What happens when the same speaker appears in multiple segments of one file? The user may resolve each segment; the system may offer to apply one resolution to all segments for the same diarization cluster.
- What happens when a pipeline run is requested while another run is in progress? The system MUST allow only one run at a time; MUST reject or queue the new request until the current run completes (see FR-016).

---

## Assumptions

- Transcription MUST use Whisper Large-v3. Diarization MUST use NeMo's Multi-Scale Diarization Decoder (MSDD). Pyannote is not to be used.
- A speaker database and voice fingerprinting capability exist (or will exist) in the system; this feature consumes them for "existing speaker" and "add sample to fingerprint."
- If the speaker database is not available at first release, the system MUST still offer the full web UI and API: a stub implementation MUST treat all segments as unknown and MUST persist resolutions (new speaker, placeholder) in local storage or files so that the flow works and can be wired to a real database later.
- The web UI is in scope for this feature; it is the primary way operators resolve unknown speakers.
- Moving a file from the unknown-speakers folder to "Videos" after resolution is automatic: once all speakers are resolved, the system moves the file through step 6 → 7 → 8 → Videos without requiring an explicit user action.

---

## Requirements *(mandatory)*

### Processing folder plan (numbers and names)

All paths are relative to a channel folder (e.g. `[Base Path]/[YouTube Channel]/`). The system MUST support the following folder names and order. Names are literal; the number indicates the step order.

| Step | Folder name | Purpose |
|------|-------------|--------|
| 0 (Inbox) | `Videos not transcribed` | Inbox: media and sister files; not yet queued for processing. |
| 1 (Queue) | `Videos 1 to be transcribed` | Queued: media here are picked up by the pipeline for processing. |
| 2 | `Videos 2 audio extracted` | Audio extracted from video and preprocessed (mono, 16 kHz, chunked). |
| 3 | `Videos 3 transcribed` | Whisper transcription done; word-level timestamps. |
| 4 | `Videos 4 diarized` | Diarization done (VAD, embeddings, clustering, MSDD); RTTM/segments. |
| 5 | `Videos 5 needs speaker identification` | Speaker identification: automatic match from global list; if any speaker is unknown, file stays here until user resolves in web UI. |
| 6 | `Videos 6 speakers matched` | All speakers have labels (matched, new, or placeholder); ready for summarization. |
| 7 | `Videos 7 summarization done` | Summarization complete; summary written to paired folder; ready for export. |
| 8 | `Videos 8 export ready` | Words aligned to speakers; transcript and exports written to paired folder. |
| Final | `Videos` | Complete: all processing done; media and paired folder stored here. |

**Processing flow:** Media moves 0 → 1 (user queues via web UI) → 2 → 3 → 4 → 5. At step 5: if all speakers are identified, move to 6 → 7 (summarization done) → 8 → Videos; if one or more speakers are unknown, the file remains in step 5 until the user resolves them in the web UI, then moves to 6 → 7 → 8 → Videos. The system MUST move media and its paired folder only between these folders and MUST NOT invent folder names outside this set. Step 5 is the designated unknown-speakers folder; configuration MAY allow a different step number or name to be used instead. Each pipeline run MUST process all media files currently discovered in "Videos 1 to be transcribed" (no per-run limit). 

### Functional Requirements

- **FR-001**: System MUST read media locations from configuration that lists one or more base folders on the local file system.
- **FR-002**: System MUST discover input media for processing under each base folder using the structure: `[Base]/[Channel Name]/Videos 1 to be transcribed/`. "Channel Name" may be any folder name (e.g. YouTube channel name); there may be many such channel folders per base. (Media in "Videos not transcribed" is inbox only; it is moved to "Videos 1 to be transcribed" by the user via the inbox-queue web UI before the pipeline processes it.)
- **FR-003**: System MUST treat a "paired folder" as a folder whose name equals the base name of the media file (no extension). All sister files (same base name, any extension or suffix) and all generated outputs for that media MUST be stored in this paired folder.
- **FR-004**: System MUST move the media file and its paired folder together from one step folder to the next. When moving from "Videos 1 to be transcribed" (step 1) through steps 2, 3, 4, 5, 6, 7 (summarization done), 8 and finally to "Videos", the paired folder MUST always move to the same destination as the media file. (Movement from "Videos not transcribed" to "Videos 1 to be transcribed" is handled by the inbox-queue web UI.)
- **FR-005**: System MUST produce a transcript file with per-word (or per-token) timings at sub-second precision, stored in the paired folder.
- **FR-006**: System MUST produce a separate, human-readable transcript file (TXT) with per-speaker content and paragraph-level speaker indications (Otter-style), stored in the paired folder.
- **FR-007**: When processing results in one or more unknown speakers, system MUST move the media file and its paired folder to the designated unknown-speakers step folder (step 5: Videos 5 needs speaker identification), not to "Videos".
- **FR-008**: When processing results in all speakers identified, system MUST move the media file and its paired folder to the channel’s "Videos" folder.
- **FR-009**: System MUST support the exact folder names and step order defined in the Processing folder plan table above; configuration MAY allow overriding the unknown-speakers folder (step 5) name or step number.
- **FR-010**: Web UI MUST discover and list media files (and their paired folders) that reside in the configured unknown-speakers step folder, across all configured base folders.
- **FR-011**: Web UI MUST allow the user to play or listen to speaker segments from the media for the purpose of identification.
- **FR-012**: Web UI MUST allow the user to identify a segment's speaker as an existing speaker in the speaker database and to add the current audio sample to that speaker's fingerprint.
- **FR-013**: Web UI MUST allow the user to create a new speaker by providing a name and to associate the current segment (or cluster) with that new speaker.
- **FR-014**: Web UI MUST allow the user to mark a speaker as unknown and to create a placeholder speaker name for that speaker.
- **FR-015**: After all unknown speakers for a media file have been resolved (existing, new, or placeholder), the system MUST automatically move the media file and its paired folder to the next step in the pipeline (step 6 → 7 → 8 → Videos); no explicit "Move to Videos" action is required from the user.
- **FR-016**: Only one pipeline run may execute at a time; the system MUST reject or queue any new run request until the current run completes.
- **FR-017**: The system MUST log each pipeline run start and end, and each step outcome (success or failure) per file, to a configurable log sink (e.g. file or stdout) so operators can debug without inspecting the filesystem alone.

### Key Entities

- **Base folder**: A configured root path on the local file system under which channel folders (e.g. YouTube channel names) are found.
- **Channel folder**: A directory named for the source (e.g. channel); contains "Videos not transcribed", "Videos 1 to be transcribed", "Videos 2 audio extracted" through "Videos 7 summarization done", "Videos 8 export ready", and "Videos".
- **Media file**: Primary audio or video file to be transcribed; may have sister files.
- **Sister file**: File with the same base name as the media file but different extension or suffix; stored with the media in the paired folder.
- **Paired folder**: Folder with the same base name as the media file; holds the media file, all sister files, and all outputs for that media; moves with the media through step folders.
- **Step folder**: One of the processing step folders from the Processing folder plan (Videos 1 to be transcribed through Videos 7 summarization done and Videos 8 export ready, or Videos), used to represent processing stage and to hold media and paired folders.
- **Speaker**: A person or placeholder identified in the transcript; may be enrolled in the speaker database with a voice fingerprint, or unknown with a placeholder name.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Operators can configure multiple base folders and have the system discover and process media from all "Videos 1 to be transcribed" locations under those bases without manual path entry per channel.
- **SC-002**: Every processed media file ends in a deterministic location: either the channel’s "Videos" folder (all speakers known) or the designated unknown-speakers step folder (Videos 5 needs speaker identification), with its paired folder in the same location.
- **SC-003**: Transcript outputs are usable: word-level transcript supports sub-second timing lookups; human-readable transcript allows a reader to see who said what at paragraph granularity without opening structured data.
- **SC-004**: No media or sister files are lost when moving between steps; the paired folder always stays with the media file and contains all associated files at each step.
- **SC-005**: Operators can use the web UI to find media in the unknown-speakers folder, listen to speaker segments, and resolve each speaker as existing (with sample added), new (with name), or unknown (with placeholder), so that the file can progress to "Videos."
