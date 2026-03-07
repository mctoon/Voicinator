# Feature Specification: Pipeline Summarize Step

**Feature Branch**: `006-pipeline-summarize`  
**Created**: 2025-03-03  
**Updated**: 2025-03-04  
**Status**: Draft  
**Input**: User description: "add another step in the pipeline: summarize. This uses a specified LLM to summarize the transcript, this will be another folder at the end of the pipeline." Extended: make summarization configurable—number of summarization parts and LLM instructions per part editable; development provides initial instructions for five default sections.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Summaries as Final Pipeline Output (Priority: P1)

When the transcription pipeline has produced a transcript for an audio file, the user or operator wants a short summary of that transcript without reading the full text. The system adds a summarization step at the end of the pipeline: it takes the completed transcript, uses a specified language model to generate a summary, and writes the summary into a dedicated folder that represents the final stage of the pipeline. So "transcript done" is followed by "summary done" in a predictable place.

**Why this priority**: Delivers the core value—summaries exist and are easy to find in a known pipeline folder.

**Independent Test**: Run the pipeline on a file through to completion; confirm a summary is produced and stored in the designated end-of-pipeline folder; open the summary and verify it reflects the transcript content.

**Acceptance Scenarios**:

1. **Given** a completed transcript from the pipeline, **When** the summarization step runs, **Then** a summary is generated from that transcript.
2. **Given** the pipeline has a defined final output stage, **When** summarization runs, **Then** summaries are written to a dedicated folder at the end of the pipeline (not mixed with raw transcripts or other stages).
3. **Given** the summarization step is enabled, **When** the pipeline completes for an item, **Then** the user can find both the transcript and its summary in the expected locations.

---

### User Story 2 - Configurable Summarization Model (Priority: P2)

The operator needs to choose which language model is used for summarization—for example, to balance cost, quality, speed, or privacy. The system must allow a "specified" or configured model so the same pipeline can be tuned or switched without code changes.

**Why this priority**: Enables tuning and flexibility; secondary to having summaries in the right place.

**Independent Test**: Set configuration to use one summarization model; run pipeline and confirm summary is produced. Change configuration to another model (or disable); run again and confirm behavior matches configuration.

**Acceptance Scenarios**:

1. **Given** configuration that specifies which language model to use for summarization, **When** the summarization step runs, **Then** the system uses that model to generate the summary.
2. **Given** the operator changes the specified model in configuration, **When** the next run executes, **Then** the new model is used for summarization.
3. **Given** summarization is disabled or not configured, **When** the pipeline runs, **Then** the step is skipped and no summary folder is written (or behavior is documented).

---

### User Story 3 - Configurable Summarization Parts and Instructions (Priority: P2)

The operator wants to control how the summary is structured: how many sections the summary has and what each section asks the language model to produce. Development delivers an initial set of summarization parts with pre-written LLM instructions, but the operator must be able to change the number of parts (add or remove sections) and edit the LLM instructions for each part so summaries can be tuned for different use cases (e.g. clickbait titles vs. sober overviews, or different content types).

**Why this priority**: Enables operators to adapt summary structure and tone without code changes; complements the configurable model (User Story 2).

**Independent Test**: Open summarization configuration; change the number of parts (e.g. add one, remove one); edit the instructions for one part; run the pipeline and confirm the generated summary reflects the configured parts and instructions.

**Acceptance Scenarios**:

1. **Given** summarization is enabled, **When** the operator views summarization configuration, **Then** the number of summarization parts and the LLM instructions for each part are visible and editable.
2. **Given** the operator adds or removes a summarization part, **When** the pipeline runs, **Then** the summary is generated using only the currently configured parts and their instructions.
3. **Given** the operator edits the LLM instructions for a part, **When** the pipeline runs, **Then** the summary output for that part reflects the updated instructions.
4. **Given** the system is first installed or reset to defaults, **When** the operator views summarization configuration, **Then** the initial set of summarization parts and instructions provided by development (see Initial summarization sections below) is available.

---

### Initial summarization sections (default)

Development delivers these five parts as the initial, editable default. Each part has associated LLM instructions that the operator can change.

1. **Clickbait-style title**: A single line, highly clickbait-style title with emojis and hashtags; maximum clickbait.
2. **One-sentence summary**: A single sentence summarizing the entire transcript; not clickbait, as useful as possible in one sentence.
3. **Paragraph overview**: A single paragraph overview of the transcript.
4. **Interesting passages**: If there are interesting parts—something novel or disagreement between participants—a short summary of the conflict or highlight with start/stop timestamps. Omitted when there is nothing notable to list.
5. **Section summary with timestamps**: A meaningful summary with timestamps for sections that stand out.

---

### Edge Cases

- What happens when the transcript is empty or too short to summarize? System either skips summarization with a clear indication or produces a minimal/placeholder summary; behavior is documented.
- What happens when the specified model is unavailable or returns an error? System fails clearly or retries according to documented behavior; the user or operator can see that the summarize step did not succeed.
- What happens when the end-of-pipeline folder does not exist or is not writable? System creates it if possible or reports a clear error so the operator can fix permissions or path.
- What happens when the operator sets the number of summarization parts to zero or removes all parts? System either skips summarization (with a clear indication) or treats it as “no sections” and produces a minimal or empty summary; behavior is documented.
- What happens when LLM instructions for a part are empty or invalid? System either uses a safe default for that part, skips that part, or reports a validation error so the operator can fix configuration; behavior is documented.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST add a summarization step to the pipeline that runs after transcript output is available and before the pipeline is considered complete for that item.
- **FR-002**: The system MUST use a specified (configurable) language model to generate summaries from the transcript; the model MUST be selectable via configuration so the process can be tuned or switched.
- **FR-003**: The system MUST write summarization output to a dedicated folder that is the final stage of the pipeline (a distinct folder at the end of the pipeline, not shared with transcript or earlier stages).
- **FR-004**: The system MUST document how to specify the summarization model and where the summary folder is located in the pipeline layout.
- **FR-005**: When summarization is configured and the transcript exists, the system MUST produce a summary and place it in the designated folder; when summarization is disabled or not configured, the pipeline MAY skip this step (behavior documented).
- **FR-006**: The system MUST allow the operator to configure the number of summarization parts (add or remove sections) so that the summary structure can be adapted without code changes.
- **FR-007**: The system MUST allow the operator to view and edit the LLM instructions for each summarization part so that the prompt or guidance for each section can be tuned.
- **FR-008**: The system MUST ship with an initial set of summarization parts and LLM instructions (the five default sections described in this spec); these MUST be editable and the number of parts MUST be changeable by the operator.
- **FR-009**: When the pipeline runs, the system MUST generate the summary using only the currently configured parts and their current LLM instructions.

### Key Entities

- **Summarization step**: A pipeline stage that takes the completed transcript as input and produces a summary; runs after transcription (and any prior steps) and outputs to the final pipeline folder.
- **Specified LLM**: The language model used for summarization; identified by configuration (e.g. name, endpoint, or profile) so operators can choose and change it.
- **End-of-pipeline folder**: The dedicated output location for summaries; represents the last stage of the pipeline so users know where to find final summary output.
- **Summarization part**: A named section of the summary (e.g. title, one-sentence summary, overview); has an order and associated LLM instructions that tell the model what to produce for that section.
- **LLM instructions (per part)**: The editable prompt or guidance for one summarization part; development provides initial text for each default part; the operator can change this text to alter what the model outputs for that section.

## Assumptions

- The pipeline already has a well-defined sequence (e.g. ingest → transcribe → diarize → …); summarization is appended as the last step.
- "Specified LLM" means the model is configured (e.g. by name or endpoint); the spec does not mandate a specific provider or API.
- One summary per transcript (or per pipeline item) is sufficient; multi-format or multi-model summaries are out of scope unless later specified.
- The transcript format passed to the summarization step is whatever the pipeline produces (e.g. plain text or structured); the summarization step consumes it as input.
- The five initial summarization sections (clickbait title, one-sentence summary, paragraph overview, interesting passages, section summary with timestamps) are the default content provided by development; operators can add, remove, reorder, or edit parts and their instructions.
- “Editable” means the operator can change the number of parts and the text of the LLM instructions through configuration (e.g. config file or UI); the spec does not mandate how configuration is presented (file vs. UI).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every pipeline run that completes transcription and has summarization enabled produces a summary in the designated end-of-pipeline folder.
- **SC-002**: Operators can change which language model is used for summarization via configuration and see the change take effect on the next run.
- **SC-003**: Users can locate summary output in a single, documented folder that is clearly the final stage of the pipeline.
- **SC-004**: When the specified model is unavailable or the step fails, the system reports the failure clearly so operators can fix configuration or connectivity.
- **SC-005**: Operators can change the number of summarization parts and the LLM instructions for each part via configuration and see the updated structure and content reflected in the next generated summary.
- **SC-006**: New or reset installations present the five default summarization sections with their initial LLM instructions so operators can use or edit them without creating content from scratch.
