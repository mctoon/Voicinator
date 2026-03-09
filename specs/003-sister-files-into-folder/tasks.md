# Tasks: Collect sister files into paired folder (003)

**Input**: Design documents from `/specs/003-sister-files-into-folder/`  
**Prerequisites**: plan.md, spec.md

**Tests**: Not requested in the feature specification; no test tasks included.

## Path Conventions

- Extend existing `backend/` at repository root.

---

## Phase 1: Service and integration

- [x] T001 Implement sister-files collect service: given a media file path in the queue folder (step 1), find sister files (same stem, same directory, exclude primary); if at least one sister exists, create paired folder if missing and move sister files into it (keep existing on name collision); do not create empty paired folder; do not move primary; return (success, error_message) in backend/src/services/sisterFilesCollectService.py.
- [x] T002 Call collect service from step-1 discovery: in discoverMediaInStep1, for each media file found, call collectSisterFilesIntoPairedFolder(mediaPath) before appending to result; same for step-1 entries in discoverMediaInAllSteps in backend/src/services/pipelineDiscoveryService.py.
- [x] T003 Update STATUS.md with 003 status and run instructions (optional: set current focus to 003).

## Execution order

- T001 then T002; T003 can be done in parallel or after.
