# Feature Specification: Automatic Pipeline Processing

**Feature Branch**: `013-auto-pipeline-processing`  
**Created**: 2026-03-07  
**Status**: Draft  
**Input**: Each step of the pipeline automatically discovers files that need to be processed. There is no additional action needed for media files to get processed. There is no need for an API call to begin processing files; simply the existence of a media file in a pipeline folder will cause the processing to happen.

---

## Clarifications

### Session 2026-03-07

- Q: How soon must the system start processing after a media file appears in a pipeline step folder? → A: Within 1 minute.
- Q: When the system is already processing file(s) and a new media file appears in a pipeline step folder, what should happen? → A: Queue it; process it in the next discovery cycle after the current run finishes (one run at a time).
- Q: When automatic processing is enabled, should the explicit "run now" API (e.g. POST /api/pipeline/run) still be available? → A: No — remove it; processing is only ever automatic.
- Q: On each discovery cycle, which step folders should the system scan for media? → A: Scan all step folders (1 through 8) each cycle; run the processor for any folder that contains media.
- Q: When a discovery cycle finds media in more than one step folder, how should the system process them? → A: All folders are always scanned when the app is running. If no files have any processing to do, the system sleeps until the next scan. Only one media file is processed at a time across all folders. Higher numbered processing steps get priority (e.g. a file in step 4 is processed before a file in step 1).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Media is processed without any manual trigger (Priority: P1)

The operator (or another system) places a media file (and optional sister files) into a pipeline step folder—for example "Videos 1 to be transcribed". The system automatically discovers that file and runs the processing for that step. No button click, API call, or scheduled job is required. When the step completes, the file moves to the next step folder, where the same automatic discovery and processing applies. The operator never has to explicitly "start" the pipeline.

**Why this priority**: Core value is hands-off operation; media flows through the pipeline by virtue of being in the right folder.

**Independent Test**: Place one media file in "Videos 1 to be transcribed"; do not call any API or click any run button. Verify that within 1 minute the file is discovered and processing has started (and in due course the file is processed and moves to the next step folder). Repeat for a file placed in a later step folder and verify that step runs automatically.

**Acceptance Scenarios**:

1. **Given** a media file appears in "Videos 1 to be transcribed", **When** the system is running, **Then** the system discovers it and runs step 2 then step 3 (and subsequent steps) for that file without any external trigger.
2. **Given** a media file appears in "Videos 3 transcribed" (e.g. moved there manually or by a previous run), **When** the system is running, **Then** the system discovers it and runs step 4 (and later steps) for that file without any external trigger.
3. **Given** multiple media files in different step folders, **When** the system is running, **Then** each file is processed by the step that corresponds to the folder it is in, and no manual "run pipeline" action is required.
4. **Given** no media files in any pipeline step folder, **When** the system is running, **Then** no processing runs and no errors occur (idle behavior).

---

### User Story 2 - Consistent behavior across all pipeline steps (Priority: P2)

Every pipeline step (e.g. "Videos 1 to be transcribed" through "Videos 8 export ready") uses the same rule: presence of a media file in that step's folder causes the step's processing to run. There is no special case for "step 1" versus "step 4"; the operator experience is uniform.

**Why this priority**: Predictability and simplicity; operators do not need to remember which steps are automatic and which require a trigger.

**Independent Test**: For at least two different step folders (e.g. step 1 and step 4), place a file in each and verify that the corresponding step runs automatically in both cases.

**Acceptance Scenarios**:

1. **Given** any pipeline step folder that contains media files, **When** the system is running, **Then** the system runs the processor for that step for each file and, on success, moves the file (and paired folder) to the next step.
2. **Given** the same pipeline step definitions and folder names as the existing media-folder pipeline (002), **When** automatic processing is enabled, **Then** the same steps (transcription, diarization, speaker id, etc.) run; only the trigger changes from "explicit run" to "file presence".

---

### Edge Cases

- What happens when a file is added while the system is already processing another file? Only one media file is processed at a time globally. New files that appear during processing are discovered on the next scan and queued; they are processed in a later cycle, with higher-numbered steps having priority. New files MUST NOT be left unprocessed indefinitely.
- What happens when the system starts (e.g. app restart) and step folders already contain media? System MUST discover and process those files automatically after startup; no manual "run" required.
- What happens when a step fails for a file? File MUST remain in the current step folder; system MUST NOT move it to the next step until the step succeeds; re-discovery on a later cycle can retry.
- What happens when multiple base paths or channel folders contain files? System MUST discover and process media in all configured locations using the same automatic rule.

---

## Assumptions

- The existing pipeline step folder names and order (e.g. "Videos 1 to be transcribed" through "Videos 8 export ready", then "Videos") remain as defined in the media-folder pipeline (002). This feature adds automatic discovery and execution; it does not redefine steps.
- "Automatically" means the system periodically or continuously checks for media in pipeline step folders and runs the appropriate step processor when files are present. The exact mechanism (polling interval, file watcher, or worker loop) is an implementation choice.
- Only one media file is processed at a time across all folders; higher-numbered steps have priority when choosing the next file. When no files need processing, the system sleeps until the next scan. This avoids overlapping writes and move conflicts.
- Processing is triggered only by file presence in pipeline step folders. The system MUST NOT provide an explicit "run now" API or button for starting a pipeline run; removal of such an API (if present in the baseline pipeline) is in scope.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST automatically discover media files in each pipeline step folder (under configured base paths and channel folders) without requiring an explicit API call or user action to start processing. On each discovery cycle, the system MUST scan all step folders (steps 1 through 8) and run the step processor for any folder that contains media.
- **FR-001a**: Discovery of a media file (and the start of its step processing) MUST occur within 1 minute of the file being present in the step folder (or within 1 minute of system startup for files already present).
- **FR-002**: When a media file exists in a pipeline step folder, the system MUST run the step processor for that step for that file and, on success, move the file and its paired folder to the next step folder.
- **FR-003**: System MUST apply the same automatic discovery-and-process behavior to every pipeline step (e.g. steps 1 through 8 and transition to final "Videos" when applicable).
- **FR-004**: System MUST process media in all configured base paths and channel folders; no manual trigger per path or per channel is required.
- **FR-005**: On system startup or restart, the system MUST automatically discover and process any media already present in pipeline step folders (no "run once" required after boot). Discovery of existing files MUST occur within 1 minute of startup.
- **FR-006**: When a step processor fails for a file, the system MUST leave the file in the current step folder and MUST NOT move it to the next step until the step succeeds (retry on a later discovery cycle is allowed).
- **FR-007**: System MUST NOT require the operator to call an API (e.g. POST /api/pipeline/run) for media to be processed; processing MUST be triggered by the presence of media in the relevant folder.
- **FR-008**: Only one media file is processed at a time across all step folders and all bases/channels. When that file's step completes (and it is moved to the next step or remains in step 5), the next discovery cycle selects one file to process; no parallel processing of multiple media files.
- **FR-008a**: When selecting which file to process after a scan, the system MUST give priority to files in higher-numbered step folders (e.g. a file in step 4 is chosen before a file in step 1). This ensures files already partway through the pipeline progress before new queue entries.
- **FR-008b**: When a scan finds no media files that need processing (all folders empty or no work to do), the system MUST sleep until the next scheduled scan; no continuous busy-waiting.
- **FR-009**: System MUST NOT expose an explicit "run pipeline" or "run now" API or user action. Processing MUST be triggered solely by the presence of media in pipeline step folders (automatic discovery). Any existing such API from the baseline pipeline (002) MUST be removed or disabled when this feature is enabled.

### Key Entities

- **Pipeline step folder**: One of the defined step folders (e.g. "Videos 1 to be transcribed", "Videos 4 diarized") under a channel folder. Presence of a media file here triggers that step's processing.
- **Media file**: Primary audio or video file in a step folder; may have a paired folder (same stem) and sister files. The entity that is discovered and processed.
- **Step processor**: The logic that runs for a given step (e.g. transcribe, diarize, speaker id). Invoked automatically when a file is discovered in that step's folder.
- **Discovery**: The mechanism by which the system finds media files in step folders. Each discovery cycle scans all pipeline step folders (1 through 8) under all configured bases and channels; no user or API trigger is required for discovery to occur.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Operators can place a media file in a pipeline step folder and have it processed and moved to the next step without performing any other action (no API call, no button click).
- **SC-002**: After system restart, any media already in pipeline step folders is discovered within 1 minute and processed automatically without operator intervention.
- **SC-003**: Every pipeline step exhibits the same trigger rule: file presence in that step's folder causes that step's processing to run.
- **SC-004**: No media file remains indefinitely in a step folder solely because the operator did not trigger a "run"; automatic discovery and processing apply to all configured locations.
- **SC-005**: When multiple files across step folders could be processed, the system processes one file at a time and chooses the file in the highest-numbered step first (e.g. step 4 before step 1). When no files need processing, the system sleeps until the next scan instead of busy-waiting.
