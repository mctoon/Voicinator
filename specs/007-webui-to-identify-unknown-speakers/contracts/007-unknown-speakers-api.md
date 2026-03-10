# Contract: 007 Extensions to Unknown-Speakers API

**Feature**: 007-webui-to-identify-unknown-speakers  
**Base contract**: 002-media-folder-pipeline `contracts/unknown-speakers-api.md`  
**Base URL prefix**: `/api/pipeline/speakers`

This document describes API additions or changes required by feature 007. Existing endpoints (GET files, GET segments, GET segment-audio, POST resolve, GET speakers) remain as in the base contract unless noted below.

---

## 1. GET /api/pipeline/speakers/files (behavior change)

- **Zero-speaker handling**: When building the list, the server MAY exclude media files that have zero speakers (e.g. empty segments or no speech). Such files MUST be moved to "Videos 6 speakers matched" (by this API or by pipeline) so they do not remain in step 5. If excluded from the list, the response simply omits them; the server may perform the move when listing or via a separate mechanism.
- Response shape unchanged: `{ "items": [...], "total": N }`.

---

## 2. GET /api/pipeline/speakers/files/{mediaId}/transcript (NEW)

Returns transcript for the media file for display and click-to-play. Data comes from the paired folder: transcript_words.json and segments.json merged so that each word or span can be associated with a segment and resolved speaker name/label.

**Response** (200): JSON

```json
{
  "words": [
    { "word": "Hello", "start": 0.0, "end": 0.4, "segmentId": "seg-1", "speakerId": null }
  ],
  "segments": [
    { "segmentId": "seg-1", "start": 0.0, "end": 12.5, "label": "SPEAKER_00", "speakerId": null }
  ]
}
```

- **words**: Word-level timing; segmentId links to segments; speakerId null or resolved name (for display). Optional: suggestedSpeakerId / suggestedSpeakerName if resolver suggests a match.
- **segments**: Same as GET .../segments; may include suggestedSpeakerId, suggestedSpeakerName for suggested identification (FR-010).

**Response** (404): Transcript or media not found.

---

## 3. GET /api/pipeline/speakers/files/{mediaId}/play-at (NEW)

Streams or returns a URL for playing the media file starting at a given time (for click-to-play). Option A: Query `?start=<seconds>` returns a redirect or stream for the media from that offset. Option B: Client uses media URL and sets currentTime from transcript word/segment start; server only needs to serve the media file. Prefer B (client-side seek) to avoid extra streaming complexity; if server must support range requests, document byte-range behavior.

**Query**: `start` (float, seconds)  
**Response** (200): Media stream from start, or (200) media URL and client seeks. (404) if media invalid.

*Recommendation*: Serve media file URL (or existing segment-audio for segment-only playback). Client loads media and sets `currentTime = start` for click-to-play.

---

## 4. POST /api/pipeline/speakers/resolve (behavior change)

- **Placeholder resolution**: When `resolution` is `placeholder`, the client MAY omit `name`; the server MUST then (1) generate a globally unique placeholder name (e.g. Unidentified-1, Unidentified-2), (2) create a **full speaker record** (same as for a named speaker), (3) associate the segment with that speaker, and (4) add passage(s) from the current video to that speaker's corpus. Response MAY include the assigned name: `{ "ok": true, "assignedName": "Unidentified-1" }`. Placeholder speakers are first-class for corpus and future media-linking (per spec FR-005b, SC-007a).
- **Suggested identification**: When returning segments (GET segments or GET transcript), include optional `suggestedSpeakerId` / `suggestedSpeakerName` when the resolver has a suggestion. Client shows "Suggested: Alice"; on confirm, client sends resolve with existing + speakerId; server adds passage to that speaker's corpus (per FR-010).

---

## 5. POST /api/pipeline/speakers/files/{mediaId}/complete (NEW)

Called when the user clicks "Complete identification". All segments for the file MUST be resolved (existing, new, or placeholder).

**Server actions** (in order):

1. Verify all segments for this mediaId have a resolved speaker (speakerId set).
2. In the paired folder: copy transcript.txt and transcript_words.json to backup names (e.g. transcript_pre_speaker_id.txt, transcript_words_pre_speaker_id.json), then rewrite transcript.txt and transcript_words.json with all speaker labels replaced by resolved names (user names or placeholder names).
3. Move media file and paired folder from "Videos 5 needs speaker identification" to "Videos 6 speakers matched" for the same channel.
4. Return success.

**Response** (200): `{ "ok": true }`  
**Response** (400): Not all segments resolved, or transcript update failed (e.g. files missing).  
**Response** (404): mediaId invalid or file already moved.

---

## 6. GET /api/pipeline/speakers/files/{mediaId}/can-complete (optional)

Returns whether all segments are resolved so the client can enable/disable the "Complete identification" button.

**Response** (200): `{ "canComplete": true }` or `{ "canComplete": false }`

Can be derived from GET segments (all segments have speakerId); optional convenience endpoint.

---

## Summary of 007 API surface

| Item | Type | Description |
|------|------|-------------|
| GET files | Change | Exclude zero-speaker media; ensure they are moved to step 6 |
| GET files/{id}/transcript | New | Transcript words + segments for display and click-to-play |
| GET files/{id}/play-at | Optional | Play media from time; or client seeks on media URL |
| POST resolve | Change | Placeholder without name → server generates Unidentified-<N> |
| POST files/{id}/complete | New | Transcript backup+rewrite, then move to step 6 |
| GET files/{id}/can-complete | Optional | Whether all segments resolved |
