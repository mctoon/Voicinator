# Research: Configurable Chunk Size (005)

## 1. Configuration location and format

**Decision**: Add `chunkDurationSeconds` under `[pipeline]` in `voicinator.toml` (repo root). Same file and section already used for `basePaths`, `scanIntervalSeconds`, `autoProcessingEnabled`, and `unknownSpeakersStepName`.

**Rationale**: Single master config keeps pipeline tunables in one place; operators already edit `voicinator.toml` for base paths and scan interval. No new config file or env var required.

**Alternatives considered**: Separate pipeline config file (rejected: extra file); CLI-only flag (rejected: spec requires config so next run uses value without code changes); env var only (rejected: less discoverable than TOML).

---

## 2. Supported range for chunk duration

**Decision**: Enforce a range of **10–120 seconds**. Default **30 seconds**. Values below 10 or above 120 are rejected or warned; system falls back to default (30) when invalid.

**Rationale**: Spec states "e.g. 10–120 seconds" and requires a documented range. Ten seconds avoids tiny chunks that hurt Whisper context; 120 seconds caps memory and aligns with pipeline docs (e.g. 30 s with 5–10 s overlap). Default 30 matches current docs and faster-whisper’s typical window.

**Alternatives considered**: 5–300 s (rejected: very short chunks risk quality; very long increases memory); no max (rejected: spec requires documented bounds).

---

## 3. How chunk duration is used in the pipeline

**Decision**: (a) **Config and API first**: Add `chunkDurationSeconds` to config and to GET `/api/pipeline/config`. (b) **Chunking behavior**: Current step 3 passes the full extracted audio to faster-whisper in one call. faster-whisper uses an internal ~30 s window and does not expose a configurable chunk length. To honor “configurable chunk size” we have two options:

- **Option A (minimal)**: Add config and validation only; document that “chunk duration” is the intended segment length for any future or external preprocessing. Step 3 remains “whole file” until explicit chunking is implemented.
- **Option B (full)**: Implement explicit preprocessing: for audio longer than `chunkDurationSeconds`, split into segments of that length (with documented overlap, e.g. 5–10 s), run step 3 on each segment, then merge word-level timestamps. Use the configured value as segment length.

**Recommendation**: Implement **Option A** in this feature so that config, validation, and API are in place; document that explicit chunking (Option B) can be added in a follow-up and will use this setting. If the product owner prefers Option B in scope for 005, implementation will add splitting/merge logic in or before step 3.

**Rationale**: Spec requires “configurable chunk duration” and “splits the audio into segments of the configured duration.” Option A satisfies config and docs; Option B satisfies full end-to-end chunking. Deciding in planning avoids rework.

**Alternatives considered**: Rely on faster-whisper only (no config) — rejected: spec requires configurability. Implementing Option B only without config — rejected: config is mandatory.

---

## 4. Invalid or missing config behavior

**Decision**: If `chunkDurationSeconds` is missing or invalid (non-numeric, zero, negative, or outside 10–120): log a warning, use default **30** seconds. Do not abort the pipeline. Document this in config docs and in GET `/api/pipeline/config` (e.g. return effective value and a flag if defaulted).

**Rationale**: Spec: “When no value is provided or configuration is missing, the system MUST use 30 seconds.” For out-of-range values, spec allows “reject or warn and fall back to default.” Graceful fallback avoids breaking runs when the config file is edited incorrectly.

**Alternatives considered**: Abort on invalid value (rejected: spec allows fallback); ignore invalid and use previous value (rejected: “last valid” adds state; default is simpler).

---

## 5. Overlap and tolerance

**Decision**: Overlap (e.g. 5–10 s between chunks) remains out of scope for this feature; docs will state that chunk duration is the segment length and that overlap is fixed or configurable elsewhere. If explicit chunking (Option B) is implemented later, tolerance for “configured duration” (e.g. ±1 s or last segment shorter) will be documented in the same place as the range.

**Rationale**: Spec: “Overlap may be fixed or configurable elsewhere; this feature focuses on chunk size.”
