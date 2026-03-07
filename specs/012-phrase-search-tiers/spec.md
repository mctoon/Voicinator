# Feature Specification: Phrase Search Tiers (Exact, Approximate, Meaning-Based)

**Feature Branch**: `012-phrase-search-tiers`  
**Created**: 2026-03-07  
**Status**: Draft  
**Input**: Add search by exact phrases (including boolean word search: AND, OR, grouping; default AND for multiple words; optional & | !), approximate phrases, and fuzzy meaning-based phrases with speaker scoping (any, list, or one speaker); define data storage needed for each search tier aligned with the searchable voice database.

---

## Clarifications

### Session 2026-03-07

- Q: How should NOT behave in boolean word search? → A: NOT excludes segments that contain the negated term (e.g. "word1 NOT word2" → segments containing word1 and not containing word2).
- Q: What search response-time expectation should the spec set for typical use? → A: No explicit target; performance is implementation-defined and documented at release.
- Q: Should approximate (typo-tolerant) search support the same boolean operators as exact phrase search? → A: No; approximate search is phrase-only (no AND/OR/NOT or grouping); only exact phrase search has boolean.
- Q: How should the system order search results when there are multiple matches? → A: Order by relevance to the query (e.g. best match first); exact definition of relevance is implementation-defined.
- Q: How should the system handle a query that contains only NOT (no positive term)? → A: Invalid or rejected; the system requires at least one positive term and shows a clear message.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Search by exact phrase and boolean word search with speaker scope (Priority: P1)

The operator wants to find every place in the catalog where a specific phrase was said, optionally restricted to one speaker, a chosen list of speakers, or any speaker. The system supports entering a phrase and selecting speaker scope (any / these speakers / one speaker). In addition, the system supports **boolean word search**: the operator can combine words with AND, OR, and parentheses so that results match the intended logic (e.g. "word1 AND word2", "word1 OR word2", "(word1 OR word2) AND word3"). When the operator enters multiple words without specifying AND or OR, the system treats them as AND—so adding more words narrows the result list. Results expand only when OR is explicitly used. The system MAY accept programmer-friendly symbols for the same operators (e.g. & for AND, | for OR, ! for NOT) as an alternative to words. NOT excludes segments that contain the negated term (e.g. "word1 NOT word2" returns segments that contain word1 and do not contain word2). Results list matching segments with media, speaker, and position (e.g. timestamp or snippet) so the operator can open the recording at that point.

**Why this priority**: Exact phrase search is the foundation for "find where X was said" and aligns with the searchable voice database; boolean search lets operators narrow or broaden results predictably; speaker scoping is required for all search tiers.

**Independent Test**: Ingest at least two media items with known transcripts and speakers; search for a phrase that appears in one segment; restrict to one speaker; verify results show only that segment with correct media and speaker. Search for "word1 AND word2" and verify only segments containing both words appear; search for "word1 OR word2" and verify segments containing either word appear; search "word1 word2" (no operator) and verify AND behavior (both required). Repeat with "any speaker" and verify all matching segments appear.

**Acceptance Scenarios**:

1. **Given** the voice database contains segments with transcript text and speaker associations, **When** the user searches by exact phrase with scope "any speaker", **Then** the system returns all segments whose transcript contains that phrase, with media and speaker identified for each.
2. **Given** the same database, **When** the user searches by exact phrase and selects "one speaker", **Then** the system returns only segments containing the phrase that are attributed to that speaker.
3. **Given** the user selects "list of speakers", **When** the user searches by phrase, **Then** the system returns only segments containing the phrase where the speaker is one of the selected speakers.
4. **Given** search results, **When** the user views them, **Then** each result identifies the media item, the speaker, and where the match occurs (e.g. snippet or timestamp) so the user can locate or play that point.
5. **Given** the user enters multiple words without AND or OR (e.g. "word1 word2 word3"), **When** the user runs the search, **Then** the system treats the query as requiring all words (AND), so that adding more words narrows the result list.
6. **Given** the user enters a query with explicit OR (e.g. "word1 OR word2" or "word1 | word2" if supported), **When** the user runs the search, **Then** the system returns segments containing at least one of the specified words, so that results expand only when OR is explicitly used.
7. **Given** the user enters a query with AND and OR and grouping (e.g. "(word1 OR word2) AND word3"), **When** the user runs the search, **Then** the system applies the boolean logic correctly so that results match the grouped expression (e.g. segments that contain word3 and also contain either word1 or word2).
8. **Given** the system supports symbol alternatives for boolean operators (e.g. &, |, !), **When** the user enters a query using those symbols, **Then** the system interprets them as the corresponding boolean operator (e.g. & as AND, | as OR, ! as NOT) and returns results consistent with the word forms (AND, OR, NOT).
9. **Given** the user enters a query using NOT (e.g. "word1 NOT word2" or "word1 !word2"), **When** the user runs the search, **Then** the system returns only segments that contain the required term(s) and do not contain the negated term (e.g. segments containing word1 and not containing word2).

---

### User Story 2 - Search by approximate phrase with speaker scope (Priority: P2)

The operator wants to find segments that roughly match a phrase (e.g. minor typos, "quarterly revenues" vs "quarterly revenue"), again with optional restriction to any speaker, a list of speakers, or one speaker. The system supports approximate or typo-tolerant matching so that small variations still return relevant segments. Approximate search is phrase-only: it does not support boolean operators (AND, OR, NOT) or grouping; only exact phrase search supports those.

**Why this priority**: Approximate search reduces missed results when the user does not recall the exact wording or when transcriptions vary slightly.

**Independent Test**: Ingest media with a known phrase; search using a slightly different spelling or wording that means the same thing; verify the system returns the relevant segment(s); restrict to one speaker and verify scope is applied.

**Acceptance Scenarios**:

1. **Given** the voice database contains segments with transcript text and speaker associations, **When** the user searches with approximate phrase matching and scope "any speaker", **Then** the system returns segments that match the phrase within the supported tolerance (e.g. typo-tolerant or wording variation), with media and speaker identified.
2. **Given** the user selects one speaker or a list of speakers, **When** the user runs an approximate phrase search, **Then** results are limited to segments from the selected speaker(s) that match within tolerance.
3. **Given** search results, **When** the user views them, **Then** each result identifies the media item, the speaker, and where the match occurs so the user can locate or play that point.

---

### User Story 3 - Search by meaning (semantic / fuzzy meaning) with speaker scope (Priority: P2)

The operator wants to find segments where a topic or idea was discussed, even when the exact words differ (e.g. "pricing concerns" vs "worried about cost"). The system supports meaning-based or semantic search so that paraphrases and related wording are found. Speaker scope (any / list / one) applies. Optionally, the operator can ask for a synthesis or summary of what a chosen speaker said about a topic, using the same underlying retrieval restricted to that speaker.

**Why this priority**: Meaning-based search supports discovery by concept rather than exact wording; synthesis for one speaker is a natural extension for "what did X say about Y?"

**Independent Test**: Ingest media containing discussion of a topic using varied wording; search using a different paraphrase of that topic; verify relevant segments are returned; restrict to one speaker and verify only that speaker's segments appear; if synthesis is offered, request a summary for that speaker and topic and verify the output reflects retrieved segments.

**Acceptance Scenarios**:

1. **Given** the voice database contains segments with transcript text and speaker associations and supports meaning-based search, **When** the user searches by a natural-language query (e.g. topic or idea) with scope "any speaker", **Then** the system returns segments whose meaning is relevant to the query, with media and speaker identified.
2. **Given** the user selects one speaker or a list of speakers, **When** the user runs a meaning-based search, **Then** results are limited to segments from the selected speaker(s) that are relevant to the query.
3. **Given** meaning-based search results, **When** the user views them, **Then** each result identifies the media item, the speaker, and where the match occurs so the user can locate or play that point.
4. **Given** the system supports synthesis or summary for a speaker and topic, **When** the user requests a summary of what a chosen speaker said about a topic, **Then** the system retrieves relevant segments for that speaker and topic and presents a synthesized summary (or equivalent) so the user gets an answer without reading every segment.

---

### User Story 4 - Store segment-level text and speaker association for all search tiers (Priority: P1)

The system stores transcript content at the segment level (each contiguous stretch of speech with one speaker) and associates each segment with exactly one speaker and one media item. This structure allows every search type (exact, approximate, meaning-based) to filter by speaker scope (any, list, or one) and to return media, speaker, and position. The same segment data supports full-text search for exact phrases, typo-tolerant or approximate matching, and meaning-based search (e.g. via semantic representation of segment text).

**Why this priority**: Without segment-level storage and speaker/media association, speaker-scoped search across the three tiers is not possible.

**Independent Test**: After ingestion of new media with multiple speakers, verify that segments are stored with text, speaker identity, and media identity; run one exact and one approximate search filtered to one speaker and confirm results are correctly limited to that speaker.

**Acceptance Scenarios**:

1. **Given** processed media with transcript and diarization, **When** the pipeline (or ingestion) completes, **Then** the system stores each segment with its transcript text, speaker identity, media identity, and timing so that search can operate per segment and filter by speaker and media.
2. **Given** stored segments, **When** any search (exact, approximate, or meaning-based) is run with a speaker scope, **Then** the system applies that scope by restricting results to segments whose speaker is in the selected set (any = no restriction, list = selected speakers, one = single speaker).
3. **Given** the searchable voice database, **When** the operator uses any of the three search types, **Then** the same segment and speaker–media data supports all of them so that scope and result shape are consistent.

---

### Edge Cases

- What happens when the user enters a very short or empty phrase? The system rejects empty queries or very short queries (e.g. below a minimum length) and returns no results or a clear message; minimum length may be configurable.
- What happens when the user enters invalid or ambiguous boolean syntax (e.g. unmatched parentheses, or mixed symbols and words in a way that is ambiguous)? The system either interprets according to defined rules and returns results, or returns a clear error or hint so the user can correct the query; behavior is consistent and documented.
- What happens when the query contains only NOT with no positive term (e.g. "NOT word2" alone)? The system treats it as invalid and rejects it with a clear message; at least one positive term (e.g. "word1 NOT word2") is required.
- What happens when a segment has no transcript text (e.g. non-speech or failed ASR)? Such segments are not returned by phrase or meaning-based search; they may still be associated with a speaker and media for listing purposes.
- What happens when meaning-based search or synthesis depends on an external service (e.g. embedding or language model)? The system behaves according to configuration and availability; if the service is unavailable, meaning-based search and synthesis either degrade gracefully (e.g. fallback to keyword) or show a clear message; operation remains local where required by the stakeholder.
- What happens when there are thousands of matching segments? The system supports pagination or a reasonable result limit so the user can browse results without overload; exact behavior may be configured.

---

## Assumptions

- Implementation follows project [docs/CODING_STANDARDS.md](../../docs/CODING_STANDARDS.md) (naming, DB table/column conventions, Python style, run.sh + requirements.txt, small functions/files).
- The searchable voice database (see feature 009) exists and stores media, speakers, and their associations; this feature extends it with three search tiers and segment-level storage requirements for phrase and meaning-based search.
- Transcript and diarization output from the pipeline provides segment-level text and speaker per segment; ingestion into the database preserves that granularity.
- "Speaker" is a stable identity (e.g. by internal id); scope "list of speakers" and "one speaker" refer to that identity.
- Channel or other media metadata remains as in the searchable voice database for listing and filtering; no change to that model is required for phrase search tiers.
- Storage technology (e.g. full-text index, typo-tolerant index, semantic or vector index) is chosen at implementation time; this spec states required capabilities and data shape, not the specific technology.
- For boolean word search, AND and OR and parentheses are required; symbol alternatives (&, |, !) are optional and, if supported, are equivalent to the word forms.
- Search performance (e.g. response time for typical queries) has no explicit target in this spec; it is implementation-defined and documented at release.
- Boolean operators (AND, OR, NOT, grouping) apply only to exact phrase search; approximate and meaning-based search do not support boolean query syntax.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support search by exact phrase across stored transcripts, with results restricted by speaker scope (any speaker, a list of speakers, or one speaker). For exact phrase search, the system MUST support boolean word search: AND, OR, and parentheses for grouping (e.g. "(word1 OR word2) AND word3"). When the user enters multiple words without specifying AND or OR, the system MUST treat them as AND so that adding more words narrows the result list; results expand only when OR is explicitly used. The system MAY accept symbol alternatives for boolean operators (e.g. & for AND, | for OR, ! for NOT). When NOT is used, the system MUST exclude segments that contain the negated term (e.g. "word1 NOT word2" returns segments containing word1 and not containing word2). A query that contains only NOT with no positive term (e.g. "NOT word2" alone) is invalid; the system MUST reject it with a clear message and require at least one positive term.
- **FR-002**: System MUST support search by approximate phrase (typo-tolerant or minor wording variation) across stored transcripts, with the same speaker scope options as exact phrase search. Approximate search is phrase-only; boolean operators (AND, OR, NOT, grouping) apply only to exact phrase search.
- **FR-003**: System MUST support meaning-based (semantic) search so that queries by topic or idea return segments with related content even when wording differs, with the same speaker scope options.
- **FR-004**: System MUST store transcript text at segment level and associate each segment with exactly one speaker and one media item so that all search types can filter by speaker and return media and position.
- **FR-005**: For each search type, system MUST allow the operator to choose speaker scope: any speaker, a selected list of speakers, or a single speaker.
- **FR-006**: Search results MUST identify for each match the media item, the speaker, and the location of the match (e.g. snippet or timestamp) so the operator can open or play the recording at that point. Results MUST be ordered by relevance to the query (e.g. best match first); how relevance is defined is implementation-defined.
- **FR-007**: System MAY support synthesis or summary of what a chosen speaker said about a topic, by retrieving meaning-based (or other) matches for that speaker and topic and presenting a synthesized answer; if supported, this MUST respect speaker scope (one speaker).
- **FR-008**: System MUST support pagination or a reasonable result limit for search so that large result sets are manageable.

### Key Entities

- **Segment**: A contiguous stretch of speech attributed to one speaker in one media item; has transcript text, start/end timing, and associations to one speaker and one media item; is the atomic unit for all three search tiers.
- **Speaker scope**: The filter applied to search results—any speaker (no filter), a list of selected speakers, or one speaker; applied uniformly to exact, approximate, and meaning-based search.
- **Search tier**: One of exact phrase, approximate phrase, or meaning-based (semantic) search; each operates over the same segment data with the same speaker scoping.
- **Boolean query (exact phrase)**: A query that combines words with AND, OR, NOT, and parentheses; multiple words without an operator are treated as AND so that results narrow; OR is explicit so that results expand only when the user requests it; NOT excludes segments containing the negated term. Optional symbol forms (&, |, !) may be supported as alternatives to AND, OR, NOT.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Operators can find every segment containing a given exact phrase (including boolean word combinations with AND, OR, and grouping), optionally restricted to one or more speakers; multiple words default to AND (narrowing results) unless OR is explicit; each result shows which media and speaker and where the match occurs.
- **SC-002**: Operators can find segments that roughly match a phrase (typo-tolerant or wording variation), with the same speaker scope and result shape as exact phrase search.
- **SC-003**: Operators can find segments by meaning or topic (paraphrases and related wording), with the same speaker scope and result shape; optionally, operators can request a synthesized summary for one speaker and topic.
- **SC-004**: Segment-level transcript text and speaker–media association are stored so that exact, approximate, and meaning-based search all use the same data and speaker scoping behaves consistently across tiers.
- **SC-005**: Search result sets are manageable (e.g. paginated or limited) so that operators can browse results without system or usability overload.
