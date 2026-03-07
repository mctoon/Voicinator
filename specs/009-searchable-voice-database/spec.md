# Feature Specification: Searchable Voice Database

**Feature Branch**: `009-searchable-voice-database`  
**Created**: 2026-03-02  
**Status**: Draft  
**Input**: Build a searchable voice database; associate each speaker with all the media they appear in; for each media item associate all the speakers present; search by speaker name (e.g. "all recordings where speaker X appears"); search by phrase/text across transcripts; list recordings by speaker, channel, or other criteria; use a locally hosted PostgreSQL database.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Search by speaker name (Priority: P1)

The operator wants to find every recording where a specific speaker appears. The system provides a way to search by speaker name (or placeholder). The result is a list of media items (recordings) that contain that speaker. Each result can be identified (e.g. by path, title, channel, date) so the operator can open or process it.

**Why this priority**: Core value of the voice database is answering "where does speaker X appear?" across the full catalog.

**Independent Test**: Add at least two processed media items with known speakers to the database; search by one speaker's name; verify the result list includes all and only the media where that speaker appears.

**Acceptance Scenarios**:

1. **Given** the voice database contains speakers and media with speaker associations, **When** the user searches by speaker name (exact or chosen from a list), **Then** the system returns a list of all media items where that speaker appears.
2. **Given** a speaker name that matches no media, **When** the user searches, **Then** the system returns an empty list (or clear "no results").
3. **Given** search results, **When** the user views the list, **Then** each media item is identifiable (e.g. by path, title, channel, or other criteria) so the user can locate or open the recording.

---

### User Story 2 - Search by phrase or text across transcripts (Priority: P1)

The operator wants to find recordings that contain a specific phrase or text in the transcript. The system provides a way to enter search text; it searches across stored transcripts and returns a list of media items whose transcript contains that phrase or text. Results may include context (e.g. snippet, timestamp) so the user can see where the match occurs.

**Why this priority**: Text search across transcripts is a primary use case for a searchable voice database (e.g. find all mentions of a topic).

**Independent Test**: Add at least two media items with different transcripts; search for a phrase that appears in only one; verify the result list contains that media and the match is visible (e.g. snippet or timestamp).

**Acceptance Scenarios**:

1. **Given** the voice database contains media with stored transcripts, **When** the user searches by phrase or text, **Then** the system returns a list of all media items whose transcript contains that text (substring or phrase match).
2. **Given** search results, **When** the user views them, **Then** each result indicates where the match occurs (e.g. snippet, timestamp, or segment reference) so the user can jump to that point in the recording if needed.
3. **Given** a search phrase that appears in no transcript, **When** the user searches, **Then** the system returns an empty list (or clear "no results").

---

### User Story 3 - List recordings by speaker, channel, or other criteria (Priority: P2)

The operator wants to browse or filter recordings by criteria such as speaker, channel (e.g. YouTube channel folder name), or other metadata. The system provides a way to list recordings filtered by one or more of these criteria. The operator can see which speakers appear in each recording and which recordings a speaker appears in.

**Why this priority**: Enables discovery and audit ("show me everything from channel X", "show me all recordings with speaker Y and Z").

**Independent Test**: Add media from two different channels with different speakers; list by channel A; verify only media from channel A appears; list by speaker S; verify only media containing S appears.

**Acceptance Scenarios**:

1. **Given** the voice database contains media with associated speakers and channel (or source) metadata, **When** the user requests a list filtered by speaker, **Then** the system returns all media items where that speaker appears.
2. **Given** the same database, **When** the user requests a list filtered by channel (or equivalent source identifier), **Then** the system returns all media items belonging to that channel.
3. **Given** the user requests a list with multiple criteria (e.g. speaker and channel), **Then** the system returns media that satisfy all selected criteria.
4. **Given** a media item in the list, **When** the user views it, **Then** the system shows all speakers associated with that media item.

---

### User Story 4 - Maintain speaker–media and media–speaker associations (Priority: P1)

When new media is processed and speakers are identified (or placeholders created), the system records which speakers appear in that media and adds that media to each of those speakers' sets. When a speaker is updated (e.g. name change, new enrollment), associations remain correct. For each media item, the system stores the set of speakers present; for each speaker, the system stores the set of media they appear in. These associations are the foundation for search and list-by-criteria.

**Why this priority**: Without correct associations, search and list results are wrong; this is the data model the rest of the feature depends on.

**Independent Test**: Process one new media item with two speakers; verify the database shows that media linked to both speakers and each speaker linked to that media; search by each speaker and confirm the media appears.

**Acceptance Scenarios**:

1. **Given** a media item has been processed and speakers (or placeholders) have been assigned to segments, **When** the pipeline (or ingestion) completes, **Then** the system records an association between that media item and each distinct speaker that appears in it.
2. **Given** the database has speaker–media associations, **When** the user queries "all media for speaker X", **Then** the system returns exactly the set of media items associated with that speaker.
3. **Given** the database has media–speaker associations, **When** the user views a media item (e.g. in search or list results), **Then** the system shows all speakers associated with that media item.
4. **Given** a speaker is renamed or merged, **When** the update is applied, **Then** all existing media associations for that speaker remain correct (still point to the same speaker identity).

---

### Edge Cases

- What happens when the same speaker appears under two names (e.g. before and after resolution)? The system treats speaker identity as stable (e.g. by internal ID); search by current name returns all associated media. Merging duplicate speakers is out of scope for this spec unless explicitly added.
- What happens when search text is empty or very short? The system MAY reject very short queries or apply a minimum length; empty query returns no results or shows a helpful message.
- What happens when transcript text is not yet stored for a media item? Search by phrase returns only media that have transcript content stored; media with speakers but no transcript text do not appear in phrase-search results unless otherwise specified.
- What happens when there are thousands of results? The system SHOULD support pagination or a reasonable limit so the user can browse results; exact behavior (e.g. max page size) may be configured.

---

## Assumptions

- Processed media and speaker identities (from the media folder pipeline and speaker resolution) are ingested into the voice database by another process or by the same system; this feature specifies the searchable database and query behavior, not the ingestion trigger.
- "Channel" (or equivalent) is available as metadata for media (e.g. from the folder structure such as [YouTube Channel] or from configuration); the database stores it so list-by-channel is possible.
- Transcript text is stored for each media item (or per segment) so phrase search can run against it.
- The stakeholder has specified that the voice database be backed by a locally hosted PostgreSQL instance; implementation will use this for storage.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST maintain a voice database that stores speakers, media items, and the associations between them (each speaker linked to all media they appear in; each media item linked to all speakers present).
- **FR-002**: System MUST store transcript text (or equivalent) for each media item so that phrase or text search can be performed across transcripts.
- **FR-003**: System MUST support search by speaker name (or speaker identifier): given a speaker, return all media items where that speaker appears.
- **FR-004**: System MUST support search by phrase or text across transcripts: given search text, return all media items whose transcript contains that text, with indication of where the match occurs (e.g. snippet, timestamp).
- **FR-005**: System MUST support listing recordings filtered by one or more criteria, including at least: speaker, channel (or source). Other criteria (e.g. date, duration) MAY be supported.
- **FR-006**: For each media item returned in search or list results, the system MUST make visible the set of speakers associated with that media item.
- **FR-007**: For each speaker, the system MUST be able to return the set of media items associated with that speaker (used for "all recordings where speaker X appears").
- **FR-008**: System MUST run against a locally hosted database; the stakeholder has specified PostgreSQL as the backing store.

### Key Entities

- **Speaker**: A person or placeholder identified in the system; has a name (or placeholder name) and a stable identity; is associated with zero or more media items.
- **Media item**: A single recording (audio or video) that has been processed; has metadata (e.g. path, title, channel); is associated with transcript text and with a set of speakers who appear in it.
- **Voice database**: The persistent store that holds speakers, media items, transcript text, and speaker–media associations; supports search by speaker name, search by phrase/text, and list by criteria (speaker, channel, etc.).
- **Channel**: A source or container for media (e.g. YouTube channel name, folder name); stored as metadata on media items for filtering and listing.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can find all recordings where a given speaker appears by searching or listing by that speaker's name, and the result set is complete and correct for the data in the database.
- **SC-002**: Users can find all recordings that contain a given phrase or text in the transcript, and each result shows where the match occurs (e.g. snippet or timestamp).
- **SC-003**: Users can list recordings filtered by speaker, by channel, or by both; each listed item shows its associated speakers.
- **SC-004**: Speaker–media and media–speaker associations are maintained correctly when new media is ingested and when speaker data is updated, so that search and list results stay accurate.
- **SC-005**: The voice database runs entirely on the operator's local infrastructure and supports the above queries without requiring external or cloud services. (Stakeholder has specified use of a locally hosted PostgreSQL instance for the backing store.)
