# Requirements Quality Checklist: Pipeline Summarize (006)

**Purpose**: Validate that requirements are complete, clear, consistent, and measurable so implementation can proceed without ambiguity.
**Created**: 2026-03-09
**Feature**: [spec.md](../spec.md) | [plan.md](../plan.md)

**Note**: This checklist validates the quality of requirements (completeness, clarity, consistency), not implementation behavior.

---

## Requirement Completeness

- [ ] CHK001 Are all config fields for LLM definitions (name, type, baseUrl, apiKey, model) specified with required/optional and conditions? [Completeness, data-model.md]
- [ ] CHK002 Are all config fields for summarization parts (name, llm, instructions) specified and mapped to storage (voicinator.toml)? [Completeness, data-model.md, Spec §FR-006, FR-007]
- [ ] CHK003 Is the designated end-of-pipeline folder name explicitly specified (e.g. "Videos 7 summarization done")? [Completeness, Spec §FR-003]
- [ ] CHK004 Are the five default summarization sections fully described so development can implement defaults? [Completeness, Spec §FR-008, Initial summarization sections]
- [ ] CHK005 Is the contract for GET /api/pipeline/config extension (llms, summarizations) and PUT /api/pipeline/summarization-config fully specified with request/response and validation? [Completeness, contracts/summarization-config-api.md]

---

## Requirement Clarity

- [ ] CHK006 Is "order in UI = order in file" explicitly stated so implementers know display order must equal output order? [Clarity, plan.md, contracts]
- [ ] CHK007 Is "Ollama" vs "remote" LLM type defined with distinct fields (e.g. baseUrl optional for Ollama, required for remote)? [Clarity, research.md, data-model.md]
- [ ] CHK008 Is the summary output format (single file, concatenated parts) clearly specified? [Clarity, data-model.md Pipeline step 6]
- [ ] CHK009 Is "summarization disabled or not configured" defined (e.g. zero parts, no llms, or explicit flag) so skip behavior is unambiguous? [Clarity, Spec §FR-005, Edge cases]

---

## Requirement Consistency

- [ ] CHK010 Do spec FR-002 (configurable model) and data-model (LLM per part) align: each part selects one LLM by short name? [Consistency, Spec §FR-002, data-model SummarizationPart]
- [ ] CHK011 Are validation rules for PUT (duplicate LLM names, llm reference must exist) consistent between contract and data-model? [Consistency, contracts/summarization-config-api.md, data-model.md]
- [ ] CHK012 Is the pipeline step order (step 6 = summarization before step 7/8) consistent across spec, plan, and pipelineStepPlan? [Consistency, Spec FR-001, plan.md]

---

## Acceptance Criteria Quality

- [ ] CHK013 Can "summary is produced and stored in the designated folder" (US1) be verified objectively (path + file existence + content reflects transcript)? [Measurability, Spec User Story 1]
- [ ] CHK014 Can "new model is used for summarization" (US2) be verified (e.g. config change + next run uses new LLM)? [Measurability, Spec User Story 2]
- [ ] CHK015 Can "generated summary reflects the configured parts and instructions" (US3) be verified (order and content per part)? [Measurability, Spec User Story 3, FR-009]

---

## Scenario & Edge Case Coverage

- [ ] CHK016 Are requirements or documented behavior defined for empty transcript or too short to summarize? [Edge Case, Spec Edge cases]
- [ ] CHK017 Are requirements or documented behavior defined when the specified model is unavailable or returns an error? [Exception Flow, Spec Edge cases, SC-004]
- [ ] CHK018 Are requirements defined for zero summarization parts or all parts removed? [Edge Case, Spec Edge cases]
- [ ] CHK019 Are requirements defined for empty or invalid LLM instructions for a part? [Edge Case, Spec Edge cases]
- [ ] CHK020 Is behavior when end-of-pipeline folder does not exist or is not writable specified (create vs error)? [Exception Flow, Spec Edge cases]

---

## Dependencies & Assumptions

- [ ] CHK021 Is the assumption that transcript format is "whatever the pipeline produces" and step 6 consumes it as input explicitly stated? [Assumption, Spec Assumptions]
- [ ] CHK022 Are dependencies on existing pipeline steps (transcript available from step 3, step 6 folder name) documented? [Dependency, plan.md, pipelineStepPlan]

---

## Notes

- Check items off as completed: `[x]`
- Reference spec section or doc when resolving gaps (e.g. [Spec §FR-001])
- Resolve [Gap] or [Ambiguity] before implementation
