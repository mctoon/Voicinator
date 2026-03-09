# Implementation Plan: Collect sister files into paired folder

**Branch**: `003-sister-files-into-folder` | **Date**: 2026-03-09 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/003-sister-files-into-folder/spec.md`

## Summary

When media and sister files (same base name, different extensions) sit in "Videos 1 to be transcribed" as siblings, the system creates a paired folder (same base name as the media file) and moves all sister files into it; the primary media file stays in the queue folder. No empty paired folder is created. Runs as part of or before pipeline discovery so layout is normalized before step 2. Reuses 002 pipeline step plan and discovery; extends backend only.

## Technical Context

**Language/Version**: Python 3.11+ (same as repo)  
**Dependencies**: Existing (pathlib, logging); no new packages.  
**Storage**: Filesystem only; queue folder = step 1 per 002.  
**Target**: Mac (M2); local.  
**Constraints**: Do not move primary media file; do not create empty paired folder; on name collision in paired folder, keep existing (do not overwrite).  
**Scope**: All configured base/channel step-1 folders.

## Integration

- **When**: Run collection before or during discovery of media in step 1. Preferred: when discovering step 1, for each media file found, run "collect sister files into paired folder" for that file, then include it in the discovery result. So both `GET /api/pipeline/discover` and pipeline run see normalized layout.
- **Where**: New service `sisterFilesCollectService`; call from `pipelineDiscoveryService.discoverMediaInStep1` (and optionally from `discoverMediaInAllSteps` for step 1 entries).
- **Sister definition**: Same directory as media, same stem (filename without extension), different path (exclude primary). Align with 001 moveService semantics (same stem; any extension/suffix).

## Project Structure

- **New**: `backend/src/services/sisterFilesCollectService.py` — collect sister files into paired folder for one media path; return (success, error_message).
- **Modified**: `backend/src/services/pipelineDiscoveryService.py` — before appending a step-1 media item, call collect service for that media path.

## Edge Cases (from spec)

- Paired folder already exists with some sister files: move only those sisters still in the queue folder into the paired folder.
- Name collision (sister in queue has same name as file already in paired folder): keep existing file in paired folder; do not overwrite.
- Read-only/locked sister file: report error; leave in place; other sisters may still be moved.
- No sister files: do not create paired folder.
