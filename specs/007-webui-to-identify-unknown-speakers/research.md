# Research: 007 Web UI to Identify Unknown Speakers

**Feature**: 007-webui-to-identify-unknown-speakers  
**Date**: 2026-03-10

## 1. Transcript display and click-to-play

**Decision**: Use existing `transcript_words.json` (word-level start/end) and `transcript.txt` (human-readable) in the paired folder. For click-to-play, serve transcript as JSON (words with start/end and segment/speaker label); frontend plays media (video/audio) at requested start time via HTMLMediaElement.currentTime. If word-level does not include speaker per word, map segment time ranges from `segments.json` to words so each word can be tagged with segment label (and thus resolved speaker name).

**Rationale**: step3 already produces transcript_words.json and transcript.txt; step4 produces segments.json with start/end per segment. Aligning words to segments is a single pass (word falls in segment range). No new transcription or diarization needed.

**Alternatives considered**: Streaming audio clips per segment only—rejected because spec requires "click on section of transcript" to play from that point; full media playback at timestamp is simpler and matches spec.

---

## 2. Transcript update after speaker identification (backup then rewrite)

**Decision**: Before rewriting, copy `transcript.txt` → e.g. `transcript_pre_speaker_id.txt` and `transcript_words.json` → e.g. `transcript_words_pre_speaker_id.json` in the same paired folder. Then write new transcript.txt and transcript_words.json with all speaker labels (diarization labels like SPEAKER_00) replaced by resolved names (user-typed name or system-generated placeholder, e.g. Unidentified-1). Use segment-to-name mapping from resolver/resolutions for this media file.

**Rationale**: Spec requires "save the old ... with a different name" then "rewrite ... with the updated names". Fixed backup suffix keeps one backup per "pre identification" state; avoids unbounded history.

**Alternatives considered**: Versioned names (transcript_1.txt, transcript_2.txt)—rejected as spec says "different name" and single backup is sufficient for recovery.

---

## 3. Globally unique placeholder names (no spaces, find-replace friendly)

**Decision**: Generate placeholder names with pattern `Unidentified-<N>` where N is a globally unique integer (monotonically increasing counter stored in the same store as speaker resolutions, e.g. in speaker_resolutions.json or a small state file). No spaces; hyphen allowed for readability. Alternative: `Unidentified_<N>` if hyphen is reserved elsewhere. Ensure counter is read-increment-write under a lock or single process so two "not identify" actions do not get the same N.

**Rationale**: Spec requires globally unique, no spaces, not too long, readable; future find-replace across transcripts and stored data. Prefix + number is short and easy to grep/replace.

**Alternatives considered**: UUID—rejected as too long and less readable. Per-video counter—rejected because spec requires global uniqueness so the same placeholder name can appear in multiple files and be updated everywhere when later identified.

---

## 4. Zero-speaker videos (move to step 6 immediately)

**Decision**: When building the list of videos needing identification, optionally detect "zero speakers" (e.g. segments.json empty or no segments) and either (a) exclude from list and trigger move to step 6 in same request, or (b) have pipeline (step 5 or earlier) not move files with zero segments into step 5, instead moving them directly to step 6. Prefer (b) at pipeline so step-5 folder only ever contains files that actually need identification; if (b) is not feasible, implement (a) in list API or a small background step when listing.

**Rationale**: Spec says move to step 6 immediately; no manual identification. Keeping zero-speaker files out of step 5 avoids showing them in the UI at all.

**Alternatives considered**: Show in list with "No speakers" badge and auto-complete—adds UI complexity; moving at pipeline or at list time is simpler.

---

## 5. Suggested identification (already identified while in queue)

**Decision**: When loading segments for a media file, for each segment the resolver may already have a suggested or resolved speaker (e.g. from a previous session or from fingerprint match). Expose this in GET segments as optional `suggestedSpeakerId` / `suggestedSpeakerName` and in GET speakers list. Frontend shows "Suggested: Alice" and lets user confirm or change. On confirm, add passage(s) from current video to that speaker's corpus (per 008 voice library; if 008 not implemented, store in same resolver or sidecar structure so that when 008 is implemented the data is available).

**Rationale**: Spec FR-010 and acceptance scenario: indicate to user, allow confirm/correct, on confirm add to corpus. Reuse existing resolver storage for "matched" state; suggested can be same as resolved from another file.

**Alternatives considered**: No suggestion until 008—rejected because spec requires "if possible, indicate ... and allow user to confirm".

---

## 6. Complete identification button and transcript update order

**Decision**: Client calls a new endpoint e.g. POST /api/pipeline/speakers/files/{mediaId}/complete. Server (1) verifies all segments resolved, (2) updates transcript files in paired folder (backup then rewrite with names), (3) moves media + paired folder to "Videos 6 speakers matched", (4) returns success. Client then navigates back to list. Keep optional auto-move on last resolve (002 contract) for backward compatibility; when client uses Complete button, server still does transcript update then move.

**Rationale**: Spec requires explicit "Complete identification" control and that transcript files are updated before/upon completion. Single POST keeps atomicity on server.

**Alternatives considered**: Client triggers move only, server does transcript update on move—acceptable if server always runs transcript update when moving from step 5 to 6; explicit complete endpoint is clearer and allows one place to enforce "all resolved" and backup-then-rewrite.

---

## 7. Placeholder speaker as full speaker record (corpus, media linking)

**Decision**: When the user chooses not to identify a speaker (placeholder), the system creates a **full speaker record** identical in structure to a named speaker: same storage (resolver/sidecar), same corpus (passage(s) from the current video are added to that speaker's corpus), and same linkage for future features (e.g. "all media this speaker appears in"). Only the display name is auto-generated (Unidentified-<N>). No second-class or stub record.

**Rationale**: Spec clarification: placeholder speakers must be first-class so that (1) audio samples are still captured and added to corpus (voice library / fingerprinting), and (2) future features that link speakers to media treat placeholders the same as named speakers (e.g. bulk rename when later identified).

**Alternatives considered**: Placeholder as "segment-only" with no corpus or media link—rejected because spec requires full record and same treatment as named speaker for corpus and future media-linking.
