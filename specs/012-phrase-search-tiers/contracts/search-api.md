# Contract: Search API (Phrase Search Tiers)

**Branch**: `012-phrase-search-tiers` | **Phase 1 output**

HTTP API contract for the three search tiers. Consumers (e.g. inbox/queue UI or future search UI) use these endpoints. Implementation may use FastAPI or equivalent; this document defines request/response shape and rules.

**Coding standards**: Implementation must follow [docs/CODING_STANDARDS.md](../../../docs/CODING_STANDARDS.md): camelCase (and Hungarian where appropriate) for code identifiers; Allman-style braces; small functions and files. Request/response field names on the wire may be snake_case for JSON API convention; map to camelCase/Hungarian in code (e.g. `speaker_scope` → `speakerScope`, `speaker_ids` → `iSpeakerIdsList`).

---

## Base

- **Base URL**: Implementation-defined (e.g. `http://localhost:8027/api` or under `/voicinator/` per project overview).
- **Common response**: JSON. Errors: appropriate HTTP status (400 invalid query, 404 not found, 500 server error) and a clear message body.

---

## Speaker scope (all tiers)

Query parameter or JSON body field:

| Name         | Type   | Values | Description |
|--------------|--------|--------|-------------|
| speaker_scope | string | `any`, `list`, `one` | How to filter by speaker |
| speaker_ids   | array  | Optional; required when scope is `list` or `one` | List of speaker IDs, or single ID for `one` |

- `any`: ignore speaker_ids.
- `list`: return only segments whose speaker_id is in speaker_ids.
- `one`: return only segments whose speaker_id equals the single ID in speaker_ids (length 1).

---

## Pagination (all tiers)

| Name   | Type | Default | Description |
|--------|------|---------|-------------|
| limit  | int  | e.g. 50 | Max results to return (upper bound configurable) |
| offset | int  | 0       | Skip this many results |

Response includes at least: `results` (array), `total` (optional, total matching count), and optionally `limit`, `offset` for client to request next page.

---

## 1. Exact phrase search (with boolean)

**Endpoint**: e.g. `POST /search/exact` or `GET /search/exact?q=...`

**Request**:
- `query` (string, required): Phrase and/or boolean expression. Multiple words without operator = AND. Supports AND, OR, NOT, parentheses; optional symbols &, \|, !.
- `speaker_scope`, `speaker_ids`: as above.
- `limit`, `offset`: as above.

**Validation**: If query contains only NOT (no positive term), return 400 with clear message.

**Response**: JSON object:
- `results`: array of search result items (segment_id, media_id, speaker_id, snippet, start_offset_ms, end_offset_ms, relevance).
- `total`: optional; total number of matches.
- `limit`, `offset`: echoed for pagination.

**Ordering**: By relevance (implementation-defined); best match first.

---

## 2. Approximate phrase search

**Endpoint**: e.g. `POST /search/approximate` or `GET /search/approximate?phrase=...`

**Request**:
- `phrase` (string, required): Single phrase; no boolean operators.
- `speaker_scope`, `speaker_ids`: as above.
- `limit`, `offset`: as above.
- Optional: `similarity_threshold` or equivalent (implementation-defined).

**Response**: Same shape as exact search: `results`, `total`, `limit`, `offset`. Each result: segment_id, media_id, speaker_id, snippet, start_offset_ms, end_offset_ms, relevance (e.g. similarity score).

**Ordering**: By relevance (e.g. similarity descending).

---

## 3. Meaning-based (semantic) search

**Endpoint**: e.g. `POST /search/meaning` or `POST /search/semantic`

**Request**:
- `query` (string, required): Natural-language topic or idea.
- `speaker_scope`, `speaker_ids`: as above.
- `limit`, `offset`: as above.

**Response**: Same shape as other tiers: `results`, `total`, `limit`, `offset`. Each result: segment_id, media_id, speaker_id, snippet, start_offset_ms, end_offset_ms, relevance (e.g. similarity score).

**Ordering**: By relevance (e.g. embedding similarity).

**Optional**: Synthesis endpoint (FR-007), e.g. `POST /search/meaning/synthesize` with `speaker_id`, `query` (topic), returning a synthesized summary for that speaker and topic. Contract can be added when the feature is implemented.

---

## Search result item (common)

Each element of `results`:

| Field            | Type   | Description |
|------------------|--------|--------------|
| segment_id       | string | Segment identity |
| media_id         | string | Media item identity |
| media_display    | string | Optional: path, title |
| speaker_id       | string | Speaker identity |
| speaker_display  | string | Optional: name |
| snippet          | string | Optional: text excerpt |
| start_offset_ms  | int    | Position in media |
| end_offset_ms    | int    | End of segment |
| relevance        | number | Implementation-defined score/rank |

---

## Contract tests

- **Exact**: Given stored segments, request with known phrase and speaker_scope; assert response shape and that only matching segments appear; test AND, OR, NOT, invalid (only NOT) → 400.
- **Approximate**: Given stored segments, request with typo or variation; assert results include expected segment(s) and response shape.
- **Meaning**: Given stored segments with embeddings, request by topic; assert results include relevant segment(s) and response shape.
- **Pagination**: Request with limit and offset; assert results length ≤ limit and ordering consistent.
- **Speaker scope**: For each tier, request with `one` and `list`; assert results restricted to given speaker(s).
