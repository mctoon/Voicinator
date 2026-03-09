# Contract: Pipeline API

Pipeline discovery, run, and status. Base URL prefix: `/api/pipeline` (or as mounted in Flask). **Only one pipeline run may execute at a time**; if a run is requested while another is in progress, the server MUST reject (e.g. 409 Conflict or 503) or queue the request until the current run completes. Each run processes **all** discovered files in step 1 (no per-run limit).

---

## GET /api/pipeline/config

Returns pipeline configuration (base paths, step folder names, unknown-speakers step).

**Response** (200): JSON

```json
{
  "basePaths": ["/path/to/base1", "/path/to/base2"],
  "stepFolders": ["Videos 1 to be transcribed", "Videos 2 audio extracted", ...],
  "unknownSpeakersStepName": "Videos 5 needs speaker identification",
  "finalFolderName": "Videos"
}
```

---

## GET /api/pipeline/discover

Discovers media in "Videos 1 to be transcribed" under all configured base paths. Does not run processing.

**Query**: Optional `basePath` to limit to one base.

**Response** (200): JSON

```json
{
  "items": [
    {
      "mediaPath": "/base/ChannelName/Videos 1 to be transcribed/video.mp4",
      "pairedFolderPath": "/base/ChannelName/Videos 1 to be transcribed/video",
      "channelName": "ChannelName",
      "basePath": "/base"
    }
  ],
  "total": 1
}
```

---

## POST /api/pipeline/run

Runs one pipeline pass: discover all media in step 1, process each file through steps (2 → … → 5 or 6→7→8→Videos). Processes all discovered files (no limit). If another run is in progress, returns 409 Conflict (or 503) or queues; when run starts, execute synchronously or in a single worker.

**Body**: Optional (e.g. `{}`). No `limit` parameter; each run processes all discovered files.

**Response** (200): JSON

```json
{
  "processed": 2,
  "movedToStep5": 1,
  "movedToVideos": 1,
  "errors": []
}
```

---

## GET /api/pipeline/status

Returns high-level status: counts of files per step (optional; may require scanning).

**Response** (200): JSON

```json
{
  "byStep": {
    "Videos 1 to be transcribed": 5,
    "Videos 2 audio extracted": 0,
    "Videos 5 needs speaker identification": 2,
    "Videos": 10
  }
}
```
