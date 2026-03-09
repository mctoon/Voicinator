# Research: 002 Media Folder Pipeline

Decisions for implementation. Alternatives considered and rationale.

---

## 1. Transcription: engine and integration

**Decision**: Transcription MUST use **Whisper Large-v3** (local). Use a Python binding that supports the large-v3 model (e.g. `openai-whisper` or `faster-whisper`) for transcription and word-level timestamps; the model MUST be large-v3.

**Rationale**: Stakeholder requirement: transcription must use Whisper Large-v3. Spec requires sub-second word timing and local processing; Whisper large-v3 provides high quality and word-level segments.

**Alternatives considered**: Other Whisper sizes (rejected; Large-v3 required). Cloud APIs (rejected; local required). Other engines (Vosk, etc.) rejected; Whisper Large-v3 is mandated.

---

## 2. Diarization

**Decision**: Diarization MUST be done using **NeMo's Multi-Scale Diarization Decoder (MSDD)** (NVIDIA NeMo toolkit). Output: RTTM or equivalent segment list for downstream speaker identification. **Pyannote is not to be used.**

**Rationale**: Stakeholder requirement: diarization must use NeMo MSDD; Pyannote is explicitly excluded. NeMo MSDD provides multi-scale speaker diarization; integration is via NeMo Python APIs and model artifacts.

**Alternatives considered**: Pyannote.audio (rejected; not to be used). Other diarization libraries (rejected; MSDD required). External diarization service (rejected; local NeMo MSDD required).

---

## 3. Word-level transcript format

**Decision**: Store word-level transcript in the paired folder as JSON (or JSONL): each item has `word`, `start`, `end` (seconds, float). Optional: also write a standard format (e.g. SRT-like with word-level cues) if tools expect it.

**Rationale**: Sub-second precision; easy for downstream tools and for generating the human-readable transcript. JSON is parseable without custom parsers.

**Alternatives considered**: XML, custom TXT (harder to parse). SRT alone (segment-level only; word-level preferred).

---

## 4. Human-readable (Otter-style) transcript format

**Decision**: Plain TXT file in paired folder: speaker labels at paragraph level (e.g. "Speaker A:" or speaker name), then blocks of text. One paragraph per speaker turn or logical break.

**Rationale**: Spec asks for "per-speaker content and paragraph-level speaker indications, similar to Otter". TXT is universal and readable without tools.

**Alternatives considered**: Markdown (acceptable). HTML (heavier). Docx (out of scope for MVP).

---

## 5. Speaker database and fingerprinting

**Decision**: Define an internal interface (e.g. `SpeakerResolver` or adapter) with operations: list speakers, match segment to speaker (or return unknown), add sample to speaker, create new speaker, create placeholder. Implement a stub that returns "unknown" for all segments and persists resolutions (new speaker, placeholder) to local storage or files until a real speaker DB exists, so the full UI/API works and can be wired to the real DB later.

**Rationale**: Spec states "speaker database and voice fingerprinting capability exist (or will exist)"; clarification requires full UI/API with stub (all unknown; persist new/placeholder locally or in files). Interface allows 002 to progress; stub satisfies step-5 routing and resolution persistence.

**Alternatives considered**: Hard-coding a real DB (blocked until that system exists). Skipping speaker resolution (rejected; required for pipeline and UI). Hiding "existing speaker" / "add sample" until DB exists (rejected per clarification).

---

## 6. Pipeline execution model

**Decision**: Single-process orchestration: discover all "Videos 1 to be transcribed" under configured bases; for each media file (and paired folder), run steps 2 → 3 → 4 → 5 (or 6 → 7 → 8 → Videos) in order. Each run processes all discovered files in step 1 (no per-run limit). Only one pipeline run may execute at a time; reject or queue new run requests until the current run completes. Step failures leave file in current step and log (no partial move).

**Rationale**: Spec (clarifications) requires single run at a time (FR-016) and process all files per run (no limit). Deterministic location per file and no partial move on failure. Sequential steps simplify debugging and reuse 001 move semantics.

**Alternatives considered**: Parallel per-file (possible later; not required for MVP). Separate worker processes (defer). Optional limit per run (rejected per clarification).

---

## 7. Configuration

**Decision**: Reuse/extend existing config. Pipeline base paths: either same as inbox base paths (from tab config) or a separate list in master config (e.g. `voicinator.toml` `[pipeline] basePaths`). Step folder names from spec table; allow override for step 5 (unknown-speakers folder) via config.

**Rationale**: 001 already has base paths per tab; pipeline can use those or a dedicated list to avoid duplication. Single config source keeps bootstrap simple.

**Alternatives considered**: Separate pipeline config file (acceptable). Hard-coded folder names only (rejected; spec allows override for step 5).

---

## 8. Pipeline run concurrency

**Decision**: Only one pipeline run may execute at a time. When a run is requested while another is in progress, the system MUST reject the new request or queue it until the current run completes.

**Rationale**: Spec clarification (FR-016) avoids conflicting moves and simplifies recovery and logging.

**Alternatives considered**: Allow concurrent runs with locking (higher complexity). Allow concurrent runs without coordination (rejected; risk of duplicate work or conflicts).

---

## 9. Run and step logging

**Decision**: Log each pipeline run start and end, and each step outcome (success or failure) per file, to a configurable log sink (e.g. file or stdout). Use the same sink as 001 (e.g. master config `server.logPath`) or a dedicated pipeline log if configured.

**Rationale**: Spec clarification (FR-017) ensures operators can debug without inspecting the filesystem alone.

**Alternatives considered**: Log only failures (rejected per clarification). No additional logging (rejected).
