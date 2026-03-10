# Data Model: 007 Web UI to Identify Unknown Speakers

**Feature**: 007-webui-to-identify-unknown-speakers  
**Date**: 2026-03-10

This feature does not introduce a new database. All state is file-based: paired folders, segments.json, speaker_resolutions.json, and transcript files. The data model describes logical entities and file formats used or updated by the feature.

---

## 1. Entities (logical)

### 1.1 Video needing identification

- **Source**: Discovery over configured base paths; any media file in a folder named "Videos 5 needs speaker identification" (or config override).
- **Attributes**: mediaPath, pairedFolderPath, channelName, mediaId (opaque stable id for API).
- **Lifecycle**: Appears in list until moved to step 6 (or excluded when zero speakers and auto-moved).

### 1.2 Unidentified / resolved speaker (per video)

- **Source**: Diarization output in paired folder: `segments.json` with segmentId, start, end, label (e.g. SPEAKER_00), speakerId (null until resolved).
- **Resolved state**: Each segment’s speakerId is set by resolve action: existing (speakerId = known speaker id), new (speakerId = new speaker with user-typed name), or placeholder (speakerId = system-generated placeholder name, e.g. Unidentified-1).
- **Placeholder name**: Globally unique, no spaces, pattern Unidentified-<N>; stored in speaker resolver and used in transcript rewrite.

### 1.3 Speaker (existing, new, or placeholder)

- **Identity**: id (opaque) and name (user-typed or placeholder). Placeholder speakers use the same record shape as named speakers; only the name is system-generated (Unidentified-<N>).
- **Corpus of identified passages**: Set of references or clips for this speaker (per 008; 007 adds passages when user confirms identification, and when user chooses placeholder—same treatment). Stored in resolver or sidecar until 008 voice library exists. Placeholder speakers receive passage(s) from the current video in their corpus, same as named speakers.
- **Media-appearance linkage**: For future features (e.g. "all media this speaker appears in"), placeholder speakers are linked to media the same as named speakers; no distinction.

### 1.4 Transcript (in paired folder)

- **transcript.txt**: Human-readable; speaker lines + text. After identification, speaker labels are replaced with resolved names (or placeholders).
- **transcript_words.json**: Array of { word, start, end } (and optionally speaker/label per word after merge with segments). After identification, speaker labels in structure are replaced with resolved names.
- **Backup copies**: transcript_pre_speaker_id.txt, transcript_words_pre_speaker_id.json (or similar) created before overwrite.

---

## 2. File formats (in paired folder)

### 2.1 segments.json (existing; step 4 output)

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

- **speakerId**: null until resolved; then speaker id or placeholder name (e.g. "Unidentified-1"). Resolver stores mapping (mediaId + segmentId → speakerId/name).

### 2.2 transcript_words.json (existing; step 3 output)

- Array of objects: `{ "word": "...", "start": 0.0, "end": 0.5 }`. May include `"label"` or `"speakerId"` after merge with segments for display. After 007 update: speaker labels in any such fields are resolved names.

### 2.3 transcript.txt (existing; step 3 output)

- Otter-style: lines like "Speaker 1 0:00" then text. After 007 update: "Speaker 1" (and any other diarization labels) are replaced with resolved names (or placeholders) consistently with segments.

### 2.4 Speaker resolutions (resolver storage; existing)

- Resolver persists segment → speaker resolution (existing/new/placeholder). For placeholder, system generates and stores globally unique name (Unidentified-<N>) and creates a **full speaker record**: same structure as named speaker, with passage(s) from the current video added to that speaker's corpus. Global counter for N stored in same store (e.g. speaker_resolutions.json or companion file). Media-appearance linkage is maintained for placeholders the same as for named speakers.

---

## 3. State transitions

- **List**: Media in step 5 → listed; zero-speaker media excluded or auto-moved to step 6.
- **Per segment**: Unresolved (speakerId null) → Resolved (existing / new / placeholder).
- **Per video**: All segments resolved → User clicks Complete → Transcript backup + rewrite → Move to step 6 → Removed from list.

---

## 4. Validation rules (from spec)

- Placeholder names: no spaces; globally unique; pattern Unidentified-<N>.
- New speaker names: non-empty; duplicate display name allowed or not per product choice (spec says MAY NOT allow empty; validate and show message).
- Transcript update: only under paired folder paths; backup before overwrite; if transcript files missing, skip or create from segment/word data per research.
