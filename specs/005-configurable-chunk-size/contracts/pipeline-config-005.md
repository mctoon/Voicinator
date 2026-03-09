# Contract: Pipeline config extension (005 – chunk duration)

Extends **GET /api/pipeline/config** (see specs/002-media-folder-pipeline/contracts/pipeline-api.md). Base URL prefix: `/api/pipeline` (or as mounted in Flask).

---

## GET /api/pipeline/config (extended)

Returns pipeline configuration including chunk duration for tuning. Existing fields unchanged; new fields added.

**Response** (200): JSON

```json
{
  "basePaths": ["/path/to/base1", "/path/to/base2"],
  "stepFolders": ["Videos 1 to be transcribed", "Videos 2 audio extracted", ...],
  "unknownSpeakersStepName": "Videos 5 needs speaker identification",
  "finalFolderName": "Videos",
  "chunkDurationSeconds": 30,
  "chunkDurationDefaulted": false
}
```

| Field                    | Type    | Description |
|--------------------------|--------|-------------|
| `chunkDurationSeconds`   | int    | Effective chunk duration in seconds (10–120). Used when splitting long audio for transcription. Default 30 when missing or invalid. |
| `chunkDurationDefaulted`| boolean| If true, config was missing or invalid and default 30 was used. Allows UI to show a warning. |

**Validation**: Values outside 10–120 or non-numeric in config result in default 30 and `chunkDurationDefaulted: true`.
