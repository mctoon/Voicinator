# Feature Specification: Collect sister files into paired folder

**Feature Branch**: `003-sister-files-into-folder`  
**Created**: 2026-03-03  
**Status**: Draft  
**Input**: User description: "commonly the media file and sisters files residing in the 'Videos to be transcribed' folder will not have all the sister files in a sub folder. When this is the case, move all the sister files except for the video file into the folder."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Collect sister files when they are in the queue folder (Priority: P1)

When a media file and its sister files (same base name, different extensions or suffixes, e.g. .srt, .description, .info.json) are placed in the "Videos 1 to be transcribed" folder, they often sit in that folder as sibling files rather than with the sister files inside a paired subfolder. In that case, the system creates a folder with the same base name as the media file (the paired folder) and moves all sister files into that folder. The primary media file remains in the queue folder. After this step, the media file and its paired folder (containing the sister files) are in the expected layout so the rest of the pipeline can treat them as one unit.

**Why this priority**: This is the core behavior: ensuring that whenever media and sister files arrive in the queue without a paired folder layout, the system normalizes the layout by collecting sister files into the paired folder.

**Independent Test**: Place a media file (e.g. video.mp4) and two sister files (e.g. video.srt, video.info.json) directly in "Videos 1 to be transcribed" with no subfolder; run the step (or pipeline discovery); verify a folder named like the media base name exists, contains the two sister files, and the video file remains in the queue folder.

**Acceptance Scenarios**:

1. **Given** a media file and one or more sister files (same base name, different extensions/suffixes) in "Videos 1 to be transcribed" and no existing paired folder for that media file, **When** the system processes or discovers that media file, **Then** it creates a folder with the same base name as the media file and moves all sister files into that folder, and the media file remains in "Videos 1 to be transcribed".
2. **Given** a media file and sister files in "Videos 1 to be transcribed" where a paired folder already exists and already contains some or all sister files, **When** the system runs, **Then** it moves any sister files that are still in the queue folder (outside the paired folder) into the paired folder, and the media file remains in the queue folder.
3. **Given** only a media file in "Videos 1 to be transcribed" (no sister files), **When** the system runs, **Then** it does not create an empty paired folder; creation of a paired folder occurs only when there is at least one sister file to move into it.

---

### User Story 2 - Do not move the primary media file (Priority: P1)

The primary media file (the video or main audio file that defines the base name) must remain in the queue folder and must not be moved into the paired folder. Only files that are sister files (same base name, different extension/suffix) are moved into the paired folder.

**Why this priority**: The user explicitly required that the video file stay out of the folder; the paired folder is for sister files and later pipeline outputs, not for the primary media file in this layout.

**Independent Test**: Place a media file and sister files in the queue folder; run the step; verify the media file is still in "Videos 1 to be transcribed" and only sister files are inside the paired folder.

**Acceptance Scenarios**:

1. **Given** a media file and sister files in "Videos 1 to be transcribed", **When** the system moves sister files into the paired folder, **Then** the primary media file is not moved and remains in "Videos 1 to be transcribed".
2. **Given** a primary media file that is the only file with that base name (no sister files), **When** the system runs, **Then** the media file is left unchanged in the queue folder.

---

### Edge Cases

- What happens when the paired folder already exists and contains files with the same names as sister files in the queue folder? The system MUST avoid overwriting without a defined strategy (e.g. overwrite, keep existing, or rename incoming); behavior SHOULD be documented. [Assumption: overwrite or keep-existing is acceptable; prefer not overwriting by default.]
- What happens when a sister file is read-only or locked? The system SHOULD report an error and leave that file in place rather than failing the whole operation; other sister files MAY still be moved.
- What happens when the queue folder is "Videos not transcribed" versus "Videos 1 to be transcribed"? This feature applies to the folder where the pipeline picks up media for processing (e.g. "Videos 1 to be transcribed"). If the same layout is desired in "Videos not transcribed", that MAY be a separate step or configuration; this spec focuses on the queue folder used by the media folder pipeline.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: When the system discovers or processes a media file in "Videos 1 to be transcribed" and one or more sister files (same base name, different extension or suffix) exist in the same folder and are not already inside a paired folder, the system MUST create a paired folder (same base name as the media file) if it does not exist and MUST move all such sister files into that paired folder.
- **FR-002**: The system MUST NOT move the primary media file into the paired folder; the media file MUST remain in "Videos 1 to be transcribed".
- **FR-003**: When a paired folder already exists for the media file, the system MUST move any sister files that are still in the queue folder (outside the paired folder) into the paired folder.
- **FR-004**: The system MUST NOT create an empty paired folder when there are no sister files; a paired folder is created only when there is at least one sister file to move into it.
- **FR-005**: Sister files are defined as files in the same directory as the media file that share the same base name (filename without extension) and have a different extension or suffix (e.g. .srt, .description, .info.json); the primary media file is identified by configured or inferred primary extension (e.g. video/audio formats) and is excluded from being moved.

### Key Entities

- **Media file**: The primary video or audio file (e.g. .mp4, .mkv, .wav) that defines the base name and is the unit of processing; it remains in the queue folder.
- **Sister file**: A file in the same directory as the media file with the same base name and a different extension or suffix (e.g. .srt, .info.json, .description); these are moved into the paired folder.
- **Paired folder**: A folder with the same base name as the media file, used to hold sister files and pipeline outputs; created when needed and moved with the media file through pipeline steps.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Operators can drop a media file and sister files into the queue folder in any layout; after the system runs, all sister files are inside the paired folder and the media file remains in the queue folder, with no manual moving required.
- **SC-002**: When sister files are already in a paired folder, the system does not duplicate or move them out; when some sister files are outside, only those are moved in, and the operation completes without data loss.
- **SC-003**: The behavior is consistent across all configured base folders and channel folders that use "Videos 1 to be transcribed" as the queue folder.

## Assumptions

- The queue folder name is "Videos 1 to be transcribed" as defined in the media folder pipeline (002-media-folder-pipeline). If the pipeline uses a different name for the same concept, the system uses that folder.
- Primary media file format is determined by configuration or by a known set of extensions (e.g. .mp4, .mkv, .mov, .wav, .m4a); all other files with the same base name are treated as sister files.
- This feature runs as part of or before the step that discovers media in "Videos 1 to be transcribed" so that the paired folder exists before subsequent pipeline steps.
- If a name collision occurs (sister file in queue has same name as file already in paired folder), the default is to preserve the existing file in the paired folder and not overwrite; the exact strategy can be configured or documented in implementation.
