# Data Model: Phrase Search Tiers (012)

**Branch**: `012-phrase-search-tiers` | **Phase 1 output**

Entities and storage shape to support exact, approximate, and meaning-based search with speaker scope. Builds on the searchable voice database (009): media, speakers, and their associations.

**Database naming**: Table and column names follow [docs/CODING_STANDARDS.md](../../docs/CODING_STANDARDS.md): table names `t` + camelCase (e.g. `tSegment`); column names type prefix + camelCase (`s` string, `i` int/PK/FK, `l` 64-bit ms since epoch); index names `idx_` + table + column(s).

---

## Entities

### Segment

Atomic unit for all three search tiers. One contiguous stretch of speech by one speaker in one media item.

| Attribute (logical) | DB column          | Type / Notes |
|---------------------|--------------------|---------------|
| id                  | `id`               | Primary key (integer) |
| media_id            | `iMediaId`         | FK to tMedia; exactly one per segment |
| speaker_id          | `iSpeakerId`       | FK to tSpeaker; exactly one per segment |
| transcript_text     | `sTranscriptText`  | TEXT; required for exact and approximate search |
| start_offset_ms     | `lStartOffsetMs`   | 64-bit integer, ms in media |
| end_offset_ms       | `lEndOffsetMs`     | 64-bit integer, ms in media |
| embedding           | (optional column)  | Vector for meaning-based search (pgvector); null if not computed |

**Validation**: sTranscriptText may be empty (e.g. non-speech); such segments are excluded from phrase and meaning-based search per spec. Each segment has exactly one speaker and one media.

**Storage**: Table **tSegment**; one row per segment. For full-text (exact): store `tsvector` (generated column or separate FTS column) from `sTranscriptText`. For approximate: same text column with pg_trgm index. For meaning: same table, optional vector column (pgvector). Indexes: e.g. `idx_tSegment_sTranscriptText`, `idx_tSegment_iSpeakerId`, `idx_tSegment_iMediaId` (and FTS/trigram/vector indexes per implementation).

---

### Media

From 009; referenced by segments. Identity and metadata for a recording. Table **tMedia**; column naming per 009 and CODING_STANDARDS (e.g. `id`, `sFolderPath`, `sChannelId` as applicable).

| Attribute | DB column (examples) | Type / Notes |
|-----------|----------------------|--------------|
| id        | `id`                 | Primary key |
| (other)   | per 009              | path, title, channel, etc. (Hungarian + camelCase: sFolderPath, sChannelId, etc.) |

No new attributes required for 012; tSegment.iMediaId references tMedia.

---

### Speaker

From 009; referenced by segments. Stable identity for speaker scope. Table **tSpeaker**; column naming per 009 and CODING_STANDARDS.

| Attribute | DB column (examples) | Type / Notes |
|-----------|----------------------|--------------|
| id        | `id`                 | Primary key (stable; used for "list of speakers" and "one speaker" scope) |
| (other)   | per 009              | name, placeholder, etc. (e.g. sName) |

No new attributes required for 012; tSegment.iSpeakerId references tSpeaker.

---

## Speaker scope (filter, not stored)

Applied at query time to all three tiers.

| Value        | Meaning |
|--------------|--------|
| any          | No filter on speaker |
| list         | speaker_ids = [id1, id2, ...] |
| one          | speaker_id = single id |

Stored as query parameters; not an entity.

---

## Search result (output shape)

Per FR-006: each match identifies media, speaker, and location. Same shape for exact, approximate, and meaning-based.

| Field           | Type / Notes |
|-----------------|--------------|
| segment_id      | Identity of the matching segment |
| media_id        | Media item (for link/open recording) |
| media_display   | Optional: path, title, or other display info from Media |
| speaker_id      | Speaker of the segment |
| speaker_display | Optional: name or placeholder from Speaker |
| snippet         | Optional: text excerpt around match |
| start_offset_ms | Position in media (e.g. for seek) |
| end_offset_ms   | End of segment in media |
| relevance       | Implementation-defined (e.g. rank, score) for ordering |

**Pagination**: Result set supports limit + offset (or cursor) per FR-008.

---

## Relationships

- **Segment** → **Media**: many-to-one (many segments per media).
- **Segment** → **Speaker**: many-to-one (many segments per speaker).
- **Media** ↔ **Speaker**: many-to-many via segments (from 009); 012 does not change that, only adds segment-level search.

---

## State transitions

- **Segment lifecycle**: Created when transcript/diarization is ingested; transcript_text and optional embedding updated if re-processed; no explicit "deleted" state required for search (soft-delete or cascade per 009).
- **Search**: Stateless; scope and tier are query parameters; no stored "search state" beyond session if UI caches results.

---

## Indexes (implementation guidance)

Use naming `idx_` + table + column(s) per CODING_STANDARDS (e.g. `idx_tSegment_sTranscriptText`).

- **Exact**: GIN index on `to_tsvector('english', tSegment.sTranscriptText)` (or equivalent).
- **Approximate**: GIN or GiST trigram index on `tSegment.sTranscriptText` (pg_trgm).
- **Meaning**: pgvector index (e.g. HNSW or IVFFlat) on segment vector column when present.
- **Speaker scope**: B-tree on `tSegment.iSpeakerId`, `tSegment.iMediaId` for filters.
