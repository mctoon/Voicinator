# Contract: Inbox-Queue Web API (001)

**Branch**: `001-inbox-queue-web-ui` | **Phase 1 output**

HTTP API contract for the inbox-queue web UI. Backend serves this API and static/template assets. Implementation uses Flask (per research.md); this document defines request/response shape and rules.

**Coding standards**: Implementation follows [docs/CODING_STANDARDS.md](../../../docs/CODING_STANDARDS.md): camelCase and Hungarian where appropriate in code; Allman-style braces; small functions and files. JSON field names on the wire may be camelCase or snake_case; map consistently to code (e.g. `channel_name` → `sChannelName`).

---

## Base

- **Base URL**: Implementation-defined (e.g. `http://localhost:8027/inbox` or `/api/inbox`).
- **Common response**: JSON for API endpoints. Errors: appropriate HTTP status (400 invalid request, 404 not found, 409 conflict, 500 server error) with a clear message body.
- **Auth**: None; local-only, single operator.

---

## 1. Get tabs (config)

**Endpoint**: `GET /tabs` or `GET /api/inbox/tabs`

**Response**: JSON object with:
- `tabs`: array of tab objects.

**Tab object**:
| Field       | Type   | Description |
|------------|--------|-------------|
| tabId      | string | Stable id (e.g. index or slug) |
| tabName    | string | Display name (or default) |
| pathCount  | int    | 1 or 2 (one path vs source+destination) |

No request body. Empty list if config has no tabs.

---

## 2. Get channels (per tab, paginated)

**Endpoint**: `GET /tabs/{tabId}/channels` or `GET /api/inbox/tabs/{tabId}/channels`

**Query parameters**:
| Name   | Type | Default | Description |
|--------|------|---------|-------------|
| limit  | int  | e.g. 50 | Max channels to return |
| offset | int  | 0       | Skip this many |

**Response**: JSON object:
- `channels`: array of channel objects (see data-model ChannelFolder).
- `total`: optional; total channel count for this tab.
- `limit`, `offset`: echoed for pagination.

**Channel object**:
| Field         | Type   | Description |
|---------------|--------|-------------|
| channelName   | string | Directory name (channel name) |
| basePath     | string | Which configured path |
| inboxPath    | string | Full path to "Videos not transcribed" |
| queuePath    | string | Full path to "Videos 1 to be transcribed" |
| isSource     | bool   | True when tab has two paths and this channel is under source |
| tabId        | string | Tab this channel belongs to |

**Validation**: Only channels where both inbox and queue paths exist; 404 if tabId unknown.

---

## 3. Get files (per channel, paginated)

**Endpoint**: `GET /tabs/{tabId}/channels/{channelId}/files` or `GET /api/inbox/files`

**Query**: Either path-based (e.g. `inboxPath=...` and optional `tabId`) or `channelId` + `tabId`. Implementation may use channel key (e.g. base path + channel name) as channelId.

**Query parameters**:
| Name   | Type | Default | Description |
|--------|------|---------|-------------|
| limit  | int  | e.g. 100 | Max files to return |
| offset | int  | 0        | Skip this many |

**Response**: JSON object:
- `files`: array of media file objects (see data-model MediaFile).
- `total`: optional; total file count for this channel's inbox.
- `limit`, `offset`: echoed.

**Media file object**:
| Field           | Type   | Description |
|-----------------|--------|-------------|
| filePath        | string | Full path to media file |
| displayName     | string | Filename for UI |
| pairedFolderPath| string | Optional; paired folder path |
| durationSeconds | int    | Optional; if available |

**Validation**: 404 if channel or tab unknown; return only files in that channel's inbox path.

---

## 4. Move actions

**Endpoint**: `POST /api/inbox/move` (or equivalent)

**Request body** (JSON):
| Field      | Type   | Description |
|------------|--------|-------------|
| action     | string | `move3` \| `moveAll` \| `queueSelected` |
| tabId      | string | Tab context |
| channelId  | string | Channel (base path + channel name or stable id) |
| filePaths  | array  | Required for `queueSelected`: list of full file paths to move; ignored for move3/moveAll |

**Validation**: For `queueSelected`, at least one file path. Channel must exist and belong to tab. Paths must be under that channel's inbox path (and, when tab has two paths, source inbox).

**Response**: JSON object (MoveResult):
| Field     | Type   | Description |
|-----------|--------|-------------|
| success   | bool   | True if all requested moves succeeded (or idempotent already-moved) |
| movedCount| int    | Number of files (and paired folders) moved |
| errors    | array  | List of error strings; empty when success is true |

**Idempotency**: If file already in queue (destination exists or source missing), count as success and do not duplicate. Log each move and each failure.

**Status**: 200 with success true/false; 400 for invalid request; 409 if partial failure and client should retry (optional); 500 on server error.

---

## 5. Media stream (for subpanel preview)

**Endpoint**: `GET /api/inbox/media?path=...` or `GET /api/inbox/stream?path=...`

**Query parameters**:
| Name | Type   | Description |
|------|--------|-------------|
| path | string | URL-encoded full path to media file (or safe token) |

**Response**: Stream of file content with appropriate `Content-Type` (e.g. video/mp4, audio/mpeg). Support HTTP Range requests for seeking. Safe path validation: only serve files under configured base path(s); 403 or 404 for invalid path.

**Unsupported format**: If backend cannot stream or browser cannot play, frontend shows a clear message in subpanel (per spec).

---

## Contract tests (optional)

- **Tabs**: GET /tabs; assert response shape and that tab count matches config.
- **Channels**: GET channels for a known tab with limit/offset; assert shape and pagination.
- **Files**: GET files for a known channel; assert shape and that paths are under inbox.
- **Move**: POST move with move3 for a channel with ≥3 files; assert success and movedCount; verify files on disk in queue path. POST queueSelected with one file; assert success and idempotent on repeat.
- **Media stream**: GET media with valid path; assert 200 and stream; with path outside config, assert 403 or 404.
