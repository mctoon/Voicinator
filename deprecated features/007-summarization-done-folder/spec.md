# Feature Specification: Summarization-Done Folder in Pipeline

**Feature Branch**: `007-summarization-done-folder`  
**Created**: 2025-03-03  
**Status**: Draft  
**Input**: User description: "Between Videos 6 speakers matched and Videos 7 export ready add a folder for when the summarization is done."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - New Step Folder Between Speakers Matched and Export Ready (Priority: P1)

The media folder pipeline today moves files from "Videos 6 speakers matched" directly to "Videos 7 export ready". The user wants a dedicated folder in between for when summarization has completed. So after speakers are matched (step 6), the system runs summarization and then moves the media and its paired folder into this new folder; only after that does the file move to "Videos 7 export ready". Operators can see at a glance which files have finished summarization by looking at this folder.

**Why this priority**: Delivers the requested pipeline change—a visible, distinct stage for “summarization done” between speakers matched and export ready.

**Independent Test**: Run the pipeline on a file through step 6; enable summarization; after summarization completes, verify the file (and paired folder) is in the new step folder; then verify it moves to Videos 7 export ready and finally to Videos.

**Acceptance Scenarios**:

1. **Given** the pipeline with the new step folder defined between "Videos 6 speakers matched" and "Videos 7 export ready", **When** summarization completes for a media file, **Then** the media file and its paired folder are moved into this new folder (not directly to Videos 7).
2. **Given** a media file and its paired folder in the summarization-done folder, **When** the pipeline continues (e.g. export step runs), **Then** the file moves next to "Videos 7 export ready" and then to "Videos" as in the existing flow.
3. **Given** the processing folder plan, **When** an operator inspects the pipeline layout, **Then** the new folder appears in the documented order: after "Videos 6 speakers matched" and before "Videos 7 export ready".

---

### User Story 2 - Paired Folder and Summary Output Move Together (Priority: P2)

The paired folder (containing the media, transcript, and any generated summary) must move with the media file into and out of the summarization-done folder, so that summary and transcript stay with the media at every step.

**Why this priority**: Consistency with the rest of the pipeline; no lost outputs.

**Independent Test**: Process a file through summarization; confirm the paired folder (with summary inside) is in the summarization-done folder with the media file; after move to Videos 7 and then Videos, confirm the paired folder and contents are still with the media.

**Acceptance Scenarios**:

1. **Given** a media file and its paired folder in "Videos 6 speakers matched", **When** summarization completes and the file is moved to the summarization-done folder, **Then** the paired folder is moved to the same folder so it remains with the media file.
2. **Given** the summary is written into the paired folder (per pipeline summarization behavior), **When** the file is in the summarization-done folder, **Then** the summary is present in the paired folder at that location.

---

### Edge Cases

- What happens when summarization is disabled or not configured? The system MAY skip the summarization-done folder and move files directly from "Videos 6 speakers matched" to "Videos 7 export ready" (behavior documented), or MAY still create the folder and move files through it without running summarization.
- What happens when summarization fails for a file? The file remains in "Videos 6 speakers matched" (or in a designated error state); it does not move to the summarization-done folder until summarization succeeds (or retry policy is defined).
- What happens when the new folder is missing on disk? The system creates it when needed (as for other step folders) or reports a clear error so the operator can fix the path.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST add a new step folder to the media pipeline between "Videos 6 speakers matched" and "Videos 7 export ready" for the state "summarization done". The folder name MUST be documented in the processing folder plan (e.g. "Videos 6a summarization done" or equivalent).
- **FR-002**: When summarization completes for a media file, the system MUST move the media file and its paired folder from "Videos 6 speakers matched" into this new summarization-done folder before they are moved to "Videos 7 export ready".
- **FR-003**: The system MUST move the media file and its paired folder from the summarization-done folder to "Videos 7 export ready" when the next step runs, preserving the existing flow: summarization-done → Videos 7 export ready → Videos.
- **FR-004**: The paired folder MUST always move with the media file into and out of the summarization-done folder, so that transcript and summary remain with the media at every step.
- **FR-005**: The processing folder plan (or equivalent documentation) MUST be updated to include the new folder name and its position in the sequence: after step 6 (Videos 6 speakers matched) and before step 7 (Videos 7 export ready).

### Key Entities

- **Summarization-done folder**: The new step folder in the media pipeline that holds media and paired folders when summarization has completed; positioned between "Videos 6 speakers matched" and "Videos 7 export ready".
- **Processing folder plan**: The documented list of step folders and their order; after this feature, it includes the new folder between step 6 and step 7.

## Assumptions

- The existing media folder pipeline (e.g. as specified in 002-media-folder-pipeline) is in place: steps 1–7 and "Videos" with paired folders moving together. This feature extends that pipeline with one new step.
- Summarization is implemented elsewhere (e.g. 006-pipeline-summarize); this spec only adds the folder and the move behavior between step 6 and step 7.
- The exact folder name (e.g. "Videos 6a summarization done") may be configurable; the spec requires that the name and position are documented.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Files that have completed summarization appear in the new summarization-done folder (between Videos 6 and Videos 7) and then progress to Videos 7 and Videos as before.
- **SC-002**: Operators can identify which files have finished summarization by checking the summarization-done folder.
- **SC-003**: The paired folder (and its contents, including summary) stays with the media file when moving into and out of the summarization-done folder; no files are left behind.
- **SC-004**: The processing folder plan clearly shows the new folder and its position in the pipeline sequence.
