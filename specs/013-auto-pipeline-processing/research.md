# Research: 013 Automatic Pipeline Processing

Decisions for implementation. Alternatives considered and rationale.

---

## 1. Discovery scan interval

**Decision**: Use a configurable scan interval (e.g. 30 seconds or 60 seconds). Default 60 seconds so that "within 1 minute" (FR-001a) is met without requiring sub-minute polling. Implementation MUST allow override (e.g. in `voicinator.toml` under `[pipeline] scanIntervalSeconds`) so operators can tighten to 30 s if desired.

**Rationale**: Spec requires discovery within 1 minute. A fixed 60 s interval guarantees that; 30 s improves responsiveness at slightly more CPU. Configurable keeps the spec testable and allows tuning.

**Alternatives considered**: File watcher (e.g. watchdog) — avoids polling but adds dependency and can be complex across many bases/channels; defer to optional later. Sub-minute fixed interval only — no config needed but less flexible; rejected in favor of config with safe default.

---

## 2. Background execution model

**Decision**: Run the discovery-and-process loop in a background thread started when the Flask app (or main process) starts. Loop: sleep(interval) → discover all step folders → if any media, select one (highest step priority) → run that step for that file → repeat. When no media, sleep until next cycle. Use a single lock or "in progress" flag so only one file is ever in processing (no parallel step execution).

**Rationale**: 002 already has synchronous step processors and move logic; reusing them from a single thread avoids re-entrancy and move conflicts. No need for a separate worker process or queue broker for "one file at a time."

**Alternatives considered**: Separate worker process — clearer isolation but more deployment complexity; rejected for MVP. Async/await event loop — possible but 002 step processors are blocking (Whisper, etc.); keeping a dedicated thread is simpler. Celery/Redis — overkill for single-machine, one-file-at-a-time processing; rejected.

---

## 3. Selection order (priority)

**Decision**: When multiple files are discovered across step folders, sort candidates by step number descending (step 8 first, then 7, …, then 1). Within the same step, order is implementation-defined (e.g. by path or discovery order). Pick one file and process only that file’s current step; then on the next cycle, that file may appear in the next folder and be selected again (or another file in a higher step may be chosen).

**Rationale**: Spec requires "higher numbered processing steps get priority." Descending step order implements that; same-step tie-break is unspecified and can stay simple.

**Alternatives considered**: Ascending (step 1 first) — contradicts spec. Per-channel round-robin with step priority — adds complexity without spec requirement; defer.

---

## 4. Removal of explicit run API

**Decision**: When automatic processing is enabled (e.g. config flag or default for 013), do not register or do not implement POST /api/pipeline/run (or return 410 Gone / 404 with a message that processing is automatic). GET /api/pipeline/config, GET /api/pipeline/discover, and GET /api/pipeline/status remain available for operator visibility and debugging.

**Rationale**: Spec FR-009 requires no "run now" API; removing or disabling the existing POST run endpoint satisfies that while keeping read-only API for status and discovery.

**Alternatives considered**: Keep POST but have it no-op — could confuse operators; prefer explicit removal or clear error. Feature flag to toggle auto vs manual — spec says processing is only automatic; no flag required for MVP (flag could be added later if product needs both modes).

---

## 5. Startup and idle behavior

**Decision**: Start the background discovery loop as soon as the app (or pipeline component) is ready. First scan occurs within one interval of startup (e.g. within 60 s). When a scan finds no media in any step folder, the thread sleeps for the full scan interval before scanning again; no busy-wait or tight loop.

**Rationale**: Meets FR-005 (discover within 1 minute of startup) and FR-008b (sleep when no work). Single interval drives both "how often we look" and "how long we sleep when idle."

**Alternatives considered**: Immediate first scan then interval — acceptable and may be preferable (discover at T=0); implementation can do first scan before entering sleep loop. Variable interval when busy — spec does not require different rate when busy; keep one interval for simplicity.
