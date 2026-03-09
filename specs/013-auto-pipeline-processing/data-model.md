# Data Model: 013 Automatic Pipeline Processing

No new persistent data; behavior and in-memory state for discovery and single-file processing. Extends 002 pipeline (same folders, media, paired folder, step processors).

---

## Concepts

### Discovery cycle

- **Cycle**: One iteration of the background loop: (1) scan all pipeline step folders (1–8) under all configured base paths and channel folders for media files; (2) build a list of candidates (each with media path, paired folder path, step folder name, channel, base path); (3) if the list is empty, sleep for the scan interval and repeat from (1); (4) otherwise, select one candidate (see Selection), run that step for that file, then sleep for the scan interval and repeat from (1).
- **Scan interval**: Configurable duration (e.g. 60 s) between the start of one cycle and the start of the next. Ensures discovery within 1 minute (FR-001a) when interval ≤ 60 s.
- **In progress**: At most one media file is “in progress” at any time. No second file is started until the current file’s step has completed (move to next step or remain in step 5).

### Selection (priority)

- **Ordering**: Candidates are ordered by step number descending (step 8 first, then 7, …, then 1). Ties within the same step are broken by implementation (e.g. path sort or discovery order).
- **Choice**: The first candidate in that order is the one processed in this cycle. All others are left for a later cycle.

### Idle

- When a scan finds no media in any step folder, the system does not run any step processor; it sleeps until the next scheduled scan (no busy-wait).

---

## Reused from 002

- **Pipeline step folders**, **media file**, **paired folder**, **step processor**, **base path**, **channel folder**: Unchanged. Same folder names and step order as in 002.
- **Discovery**: Same notion of “media in a step folder” (primary media file extensions, paired folder = stem); 013 adds scanning all steps (1–8) each cycle instead of only step 1.

---

## Validation rules

- Do not process a second file while one is already in progress.
- Do not move files outside the defined step folders or invent folder names.
- On step failure, leave the file in the current step folder; next cycle may select it again (or another file with higher priority).
