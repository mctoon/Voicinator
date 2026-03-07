# Data Model: Inbox-to-Queue Web UI (001)

**Branch**: `001-inbox-queue-web-ui` | **Phase 1 output**

Entities and data shapes for the inbox-queue feature. No database: config file plus in-memory DTOs for API responses. Naming follows [docs/CODING_STANDARDS.md](../../docs/CODING_STANDARDS.md) (camelCase, Hungarian prefixes where applicable).

---

## Master config (bootstrap, repo base)

Single file at repository base (e.g. `voicinator.toml`) used to bootstrap the app. Loaded first.

| Section / key   | Purpose |
|-----------------|---------|
| `[server]`      | Web server options |
| `server.port`  | Port number (integer); default e.g. 8027 |
| `[inbox]`      | Optional; inbox-queue feature |
| `inbox.configPath` | Optional path to inbox tabs config; if missing, use INBOX_CONFIG env or default path |

**Validation**: If file missing, use defaults (port 8027, inbox path per existing rules). Format TOML.

---

## Config (file-backed, inbox tabs)

Loaded at startup (and optionally on reload). Path from master config, env, or default. Format TOML or JSON per research.md.

### TabConfig

One tab in the UI. Either one path (single path) or two paths (source and destination).

| Attribute (logical) | Config key / in-memory | Type / Notes |
|---------------------|------------------------|---------------|
| display name         | `tabName` or `sTabName` | String; optional; shown as tab label |
| path(s)             | `paths` or `pathList`   | List of 1 or 2 path strings (sPathSource, sPathDestination when two) |
| path (single)       | `path`                  | Single string when only one path |

**Validation**: At least one path; if two paths, first is source, second is destination. Empty or missing tab name → use default (e.g. path or "Path 1").

### Config file shape (logical)

- **tabs**: List of TabConfig (each with optional name, one or two paths).
- **config file path**: App-level settings dir or repo root; exact key names in implementation.

---

## In-memory / API entities

### ChannelFolder

A directory representing a channel (e.g. YouTube channel) under a base path. Has inbox path "Videos not transcribed" and queue path "Videos 1 to be transcribed". When tab has two paths, channel can be from source or destination; same logical channel name may exist under both.

| Attribute (logical) | Variable / JSON field | Type / Notes |
|---------------------|------------------------|---------------|
| channel name        | `sChannelName`         | String; directory name under base path |
| base path           | `sBasePath`            | String; which configured path this channel belongs to |
| inbox path          | `sInboxPath`           | Full path to "Videos not transcribed" |
| queue path          | `sQueuePath`           | Full path to "Videos 1 to be transcribed" |
| source vs destination | `bIsSource`          | Boolean; when tab has two paths, true if this channel is under source path |
| tab id / index      | `iTabIndex` or `sTabId` | Identifies which tab this channel is shown under |

**Validation**: Only include channel folders where both inbox and queue paths exist on disk; do not create folders. Hide channel if either path is missing.

### MediaFile

A media file in a channel's inbox (or queue). May have a paired folder (same base name).

| Attribute (logical) | Variable / JSON field | Type / Notes |
|---------------------|------------------------|---------------|
| file path           | `sFilePath`            | Full path to primary audio/video file |
| display name        | `sDisplayName`         | Filename or basename for UI |
| paired folder path  | `sPairedFolderPath`    | Optional; folder with same base name; move with file when queuing |
| duration            | `iDurationSeconds` or `lDurationMs` | Optional; if available for UI (e.g. from metadata) |

**Validation**: When moving, move media file and paired folder together; if paired folder exists, include it in move operation.

### MoveResult (API response)

Result of a single move or batch move.

| Attribute (logical) | Variable / JSON field | Type / Notes |
|---------------------|------------------------|---------------|
| success             | `bSuccess`             | Boolean |
| moved count         | `iMovedCount`          | Number of files (and paired folders) moved |
| errors              | `errorsList` or `sErrorMessage` | List of error messages or single message for failure |

**Logging**: Per spec, log each move (what moved, from path, to path) and each failure (error reason).

---

## State transitions (move flow)

1. **List channels** (per tab): Scan configured path(s); for each directory under path that has both "Videos not transcribed" and "Videos 1 to be transcribed", emit ChannelFolder. When two paths, merge channels from both; mark source vs destination.
2. **List files** (per channel): List media files in channel's inbox path; for each file, resolve paired folder (same base name); emit MediaFile list (paginated or virtualized).
3. **Move 3 / move all / queue selected**: For each selected file (or up to 3, or all): atomic move (or copy-then-delete) of media file and paired folder from inbox path to queue path. When tab has source + destination, move from source inbox to destination queue. Idempotent: if already moved, treat as success. Log success and failures.

---

## No database

This feature does not introduce database tables. Config is file-based; ChannelFolder and MediaFile are derived from filesystem and returned as API DTOs. If future features need a DB (e.g. move history), that would be a separate spec.
