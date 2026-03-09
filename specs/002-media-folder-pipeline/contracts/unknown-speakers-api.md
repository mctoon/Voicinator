# Contract: Unknown-Speakers (Speaker Resolution) API

Web UI for media in "Videos 5 needs speaker identification": list files, get segments, play segment, resolve speaker. When all segments for a file are resolved, the system **automatically** moves the media and paired folder to the next step in the pipeline (step 6 → 7 → 8 → Videos); no explicit client action is required. Base URL prefix: `/api/pipeline/speakers` (or similar).

---

## GET /api/pipeline/speakers/files

Lists media files (and paired folder paths) in the configured unknown-speakers step folder, across all configured base paths.

**Response** (200): JSON

```json
{
  "items": [
    {
      "mediaPath": "/base/ChannelName/Videos 5 needs speaker identification/video.mp4",
      "pairedFolderPath": "/base/ChannelName/Videos 5 needs speaker identification/video",
      "channelName": "ChannelName",
      "mediaId": "opaque-id-or-stable-key"
    }
  ],
  "total": 1
}
```

`mediaId` is used in subsequent segment and resolve calls.

---

## GET /api/pipeline/speakers/files/{mediaId}/segments

Returns speaker segments for one media file. Segments come from diarization output (e.g. RTTM) in the paired folder.

**Response** (200): JSON

```json
{
  "segments": [
    {
      "segmentId": "seg-1",
      "start": 0.0,
      "end": 12.5,
      "label": "SPEAKER_00",
      "speakerId": null
    }
  ]
}
```

`speakerId` null or set when resolved. `segmentId` used for resolve and playback.

---

## GET /api/pipeline/speakers/segment-audio

Streams audio for a segment (for playback in UI). Safe path validation: only under configured base paths and within the media file.

**Query**: `mediaId`, `segmentId`, or `start` + `end` + `mediaPath` (implementation choice).

**Response** (200): Audio stream (e.g. audio/wav or audio/mpeg). Or 404 if segment/media invalid.

---

## POST /api/pipeline/speakers/resolve

Resolves a segment’s speaker: existing (add sample), new (create + name), or unknown (placeholder).

**Body**: JSON

```json
{
  "mediaId": "opaque-id",
  "segmentId": "seg-1",
  "resolution": "existing" | "new" | "placeholder",
  "speakerId": "existing-speaker-id",
  "name": "Display Name or Placeholder"
}
```

- `existing`: provide `speakerId`; system adds current segment sample to that speaker.
- `new`: provide `name`; system creates speaker and associates segment.
- `placeholder`: provide `name` (placeholder); system creates placeholder and associates segment.

**Response** (200): `{ "ok": true }` or (400) validation error.

---

## GET /api/pipeline/speakers/speakers

Lists known speakers (for "identify as existing" in UI). Optional; may be stubbed.

**Response** (200): JSON

```json
{
  "speakers": [
    { "id": "sp-1", "name": "Alice" }
  ]
}
```

---

## Automatic move when all resolved

When the last segment for a media file is resolved (via POST resolve), the server MUST automatically move the media and paired folder from step 5 through step 6 → 7 → 8 → Videos. The client need not call any separate "move" endpoint. Optionally, a **POST /api/pipeline/speakers/files/{mediaId}/move-to-videos** MAY be provided to trigger or retry the move (e.g. idempotent); if so, (200) when move succeeds, (400) if not all resolved or move failed.
