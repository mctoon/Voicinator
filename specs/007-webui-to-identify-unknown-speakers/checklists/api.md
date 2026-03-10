# API & Contract Requirements Checklist: 007 Web UI to Identify Unknown Speakers

**Purpose**: Validate that API and contract requirements are complete, clear, and consistent with the feature spec—unit tests for requirements, not for implementation.  
**Created**: 2026-03-10  
**Feature**: [spec.md](../spec.md)  
**Contract**: [contracts/007-unknown-speakers-api.md](../contracts/007-unknown-speakers-api.md)

---

## Contract–Spec Alignment

- [x] CHK001 Is the zero-speaker handling in the contract (exclude vs move to step 6) explicitly aligned with FR-009 and the spec edge case (zero speakers)? [Consistency, Spec §FR-009, Contract §1]
- [x] CHK002 Are the backup file names for transcript (e.g. transcript_pre_speaker_id.txt) specified in both spec and contract so implementation is unambiguous? [Clarity, Spec §FR-011, Contract §5]
- [x] CHK003 Is the order of operations at complete (verify all resolved → backup → rewrite → move) stated in requirements and in the contract in the same order? [Consistency, Spec §FR-006, FR-011, Contract §5]
- [x] CHK004 Is placeholder resolution (resolution=placeholder, optional name, server-generated Unidentified-N) traceable from FR-005b to the contract POST resolve behavior? [Traceability, Spec §FR-005b, Contract §4]
- [x] CHK005 Are suggested identification (suggestedSpeakerId / suggestedSpeakerName) and passage-to-corpus behavior required in both spec (FR-010) and contract (GET transcript, POST resolve)? [Completeness, Spec §FR-010, Contract §2, §4]

---

## API Response & Error Requirements

- [x] CHK006 Are all HTTP status codes and response shapes for the new/changed endpoints (transcript, complete, resolve placeholder) specified in requirements or contract? [Completeness, Contract §2, §4, §5]
- [x] CHK007 Are error response requirements defined for: transcript not found (404), media not found (404), complete when not all resolved (400), complete when file already moved (404)? [Coverage, Spec §FR-008, Edge Cases, Contract §2, §5]
- [x] CHK008 Is the optional GET can-complete (or client-derived from segments) documented as in-scope or out-of-scope so implementers know whether to build it? [Clarity, Contract §6]
- [x] CHK009 Are requirements for concurrent complete (same video, two tabs) stated so that 404 or no-op is an acceptable specified behavior? [Edge Case, Spec §Edge Cases, Contract §5]

---

## Request/Response Clarity

- [x] CHK010 Is the transcript response shape (words with start/end, segmentId, speakerId; segments with optional suggestedSpeakerId/suggestedSpeakerName) fully specified so clients can implement without ambiguity? [Clarity, Contract §2]
- [x] CHK011 Is play-at behavior (client seek vs server stream) or the decision (prefer client-side currentTime) documented in requirements or contract? [Clarity, Contract §3]
- [x] CHK012 Is the POST resolve response when placeholder is used (e.g. assignedName in response) specified so the UI can display the assigned placeholder name? [Clarity, Spec §FR-005b, Contract §4]
- [x] CHK013 Are requirements for missing transcript files at complete (skip vs create from segment data, no arbitrary path overwrite) aligned between spec edge case and contract (400 / transcript update failed)? [Consistency, Spec §Edge Cases, Contract §5]

---

## Dependencies & Assumptions

- [x] CHK014 Is the dependency on the base contract (002 unknown-speakers API: GET files, GET segments, POST resolve, GET speakers) documented so 007-only readers know what already exists? [Dependencies, Contract intro]
- [x] CHK015 Is the source of "existing speakers" (for assign-to-existing) documented as in-scope or out-of-scope in both spec and contract? [Assumption, Spec §Assumptions]

---

## Traceability

- [x] CHK016 Can each new or changed endpoint (GET transcript, POST complete, GET can-complete, POST resolve placeholder) be traced to at least one FR or user story? [Traceability, Spec §FR-003, FR-006, FR-007, FR-011]
- [x] CHK017 Are contract section numbers or IDs referenced in the implementation plan or tasks so that contract changes can be traced to code? [Traceability, Plan]

---

## Notes

- This checklist validates the **quality of API and contract requirements** (alignment with spec, completeness of responses/errors, clarity of shapes and behaviors), not whether the API is implemented correctly.
- Mark items complete when the spec or contract has been updated to address the question, or when the requirement is already clearly stated.
