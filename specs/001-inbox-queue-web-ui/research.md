# Research: Inbox-to-Queue Web UI (001)

**Branch**: `001-inbox-queue-web-ui` | **Phase 0 output**

## 1. Backend web framework (Flask vs FastAPI)

**Decision**: Use **Flask** for the inbox-queue web app (API + optional server-rendered pages and static assets).

**Rationale**: Local-only, single-operator UI with no async I/O requirement for filesystem operations. Flask is lightweight, matches project docs ("Optional: Flask/Django for web UI") and keeps dependencies minimal. If the rest of Voicinator standardizes on FastAPI (e.g. 012), this feature can still be a Flask sub-app or later migrated; for a read-config/scan-dirs/move-files API, Flask is sufficient.

**Alternatives considered**: FastAPI — better for async and OpenAPI; overkill for this feature's scope. Django — heavier; rejected for a focused inbox UI.

---

## 2. Frontend approach (templates + JS vs SPA)

**Decision**: **Server-rendered HTML templates (Jinja2) plus vanilla JavaScript** for interactivity (tabs, lists, media subpanel, API calls for move actions). Use virtualization or pagination in the browser (e.g. list virtualization library or windowed list) for channel and file lists.

**Rationale**: Single codebase, no separate build step for a minimal frontend. Tabs and lists can be rendered server-side; JS fetches paginated or virtualized data and drives the media subpanel (e.g. `<video>`/`<audio>` with controls). Aligns with "small functions and files" and run.sh-only entry point.

**Alternatives considered**: Full SPA (React/Vue) — adds build tooling and complexity; not required for hundreds/thousands of rows if we use list virtualization in vanilla JS or a small library. HTMX — could simplify server-driven updates; acceptable alternative if the team prefers it later.

---

## 3. Config file format (paths, tab names, one or two paths per tab)

**Decision**: Use a **TOML or JSON** config file (e.g. `inbox_queue_config.toml` or under existing app config). Structure: list of tabs; each tab has optional display name and one or two paths (source, optional destination). Location: app-level settings dir or repo root; read at startup and on reload.

**Rationale**: Spec allows "config file or app-level settings"; TOML/JSON are easy to parse in Python (stdlib or PyPI). No database required. Path/tab editing can be in-app (future) or by editing the file.

**Alternatives considered**: YAML — also fine; TOML/JSON preferred for simplicity. Database for config — rejected; spec says config file.

---

## 4. Serving media for the subpanel (preview)

**Decision**: Backend exposes a **streaming or URL endpoint** that serves the selected media file (or a local file path the frontend can use with a `file://`-like URL only when same-origin or via a safe stream endpoint). Prefer **HTTP range request** streaming so the browser can play and seek without loading the whole file.

**Rationale**: Media files live on the local filesystem; the UI runs in the browser. Options: (1) Backend proxy that streams the file (safe, works from any origin); (2) static file mount with safe path validation. Streaming with Range support gives play/pause, scrubber, and jump without full download. Unsupported formats: show a clear message in the subpanel (per spec).

**Alternatives considered**: File input + object URL — only for uploads, not for arbitrary disk paths. Direct file:// — not available from browser for arbitrary paths; must go through backend.

---

## 5. Move operations: atomicity and idempotency

**Decision**: Implement move as **atomic rename (or copy-then-delete with error handling)** at OS level; detect "already moved" (destination exists or source missing) and treat as success (idempotent). For paired folder: move media file and paired folder in a defined order (e.g. folder first, then file) and roll back or log failure if one fails.

**Rationale**: Spec requires "move at most once; duplicate moves avoided (atomic or idempotent)". Python `shutil.move` or `os.rename` is atomic on same filesystem; cross-filesystem may require copy + delete. Log each move and each failure for operator visibility.

**Alternatives considered**: Lock files — unnecessary if we do a single atomic rename per file. Queue of moves — acceptable for "move 3" or "move all" to serialize and avoid races.

---

## 6. List virtualization / pagination

**Decision**: **Backend pagination** for channel list and for per-channel file list (e.g. `limit` + `offset` or cursor). **Frontend**: either simple pagination controls (prev/next, page size) or a virtualized list (only render visible rows) using a small library or custom scroll-based loading. Prefer virtualized list for "thousands of files" UX when scrolling a single channel's list.

**Rationale**: Spec requires "virtualization or pagination" for hundreds of channels and thousands of files. Backend pagination keeps response size bounded; frontend virtualization avoids rendering thousands of DOM nodes. Implementation can start with pagination and add virtualization for the file list if needed.

**Alternatives considered**: Load all — rejected for scale. Infinite scroll — acceptable variant of pagination/virtualization.
