# Feature Specification: MarbleNet VAD and RTTM Diarization Output

**Feature Branch**: `004-marblenet-vad-rttm`  
**Created**: 2025-03-03  
**Status**: Draft  
**Input**: User description: "use MarbleNet VAD for VAD. Diarization output: RTTM (e.g. NeMo pred_rttms); parsed to (speaker, start, end) for alignment"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Accurate Speaker Segments for Transcription (Priority: P1)

When audio is processed for transcription, the system identifies where speech occurs and who is speaking so that the final transcript shows the correct speaker for each segment. A single, consistent voice-activity detector (MarbleNet) is used so behavior is predictable and aligned with the diarization pipeline. The diarization result is produced in a standard format (RTTM) and converted into speaker segments (speaker, start, end) so they can be aligned with the transcribed words.

**Why this priority**: Without a defined VAD and output format, different components can drift (e.g. one doc saying Silero, another MarbleNet), and downstream alignment can fail or be ambiguous. Defining MarbleNet and RTTM ensures the pipeline and documentation agree and that speaker labels attach correctly to text.

**Independent Test**: Run diarization on a short multi-speaker file; confirm voice activity is detected by the chosen VAD; confirm diarization output is in RTTM; confirm segments are available as (speaker, start, end) and align correctly with the transcript.

**Acceptance Scenarios**:

1. **Given** an audio file, **When** the system runs voice activity detection, **Then** MarbleNet VAD is used to determine speech vs non-speech regions.
2. **Given** diarization has run, **When** the system produces diarization output, **Then** the output is in RTTM format (e.g. compatible with NeMo pred_rttms).
3. **Given** RTTM output exists, **When** the system prepares data for alignment, **Then** segments are parsed into (speaker, start, end) and used to align speakers to transcribed words.

---

### User Story 2 - Interoperable Diarization Output (Priority: P2)

Stakeholders and downstream tools may consume diarization results. Using the standard RTTM format allows the same output to be read by other tools, used for scoring (e.g. DER), or archived without custom parsers.

**Why this priority**: Enables reuse and evaluation; secondary to correct behavior in the main pipeline.

**Independent Test**: Produce RTTM from the system; verify it can be read by a standard RTTM parser or evaluation tool and yields (speaker, start, end) segments.

**Acceptance Scenarios**:

1. **Given** diarization output, **When** a consumer reads the output, **Then** it conforms to RTTM so standard tools can parse it.
2. **Given** parsed segments, **When** alignment is performed, **Then** each segment has speaker identity and start/end times suitable for attaching to transcript segments.

---

### Edge Cases

- What happens when the VAD model (MarbleNet) is unavailable or misconfigured? The system should fail clearly or fall back in a documented way.
- What happens when RTTM is malformed or empty? Parsing should report an error or empty segments rather than producing incorrect alignment.
- How does the system handle very short segments (e.g. below a minimum duration)? Alignment logic should have defined behavior (e.g. merge or drop) per product rules.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST use MarbleNet for voice activity detection (VAD) within the diarization pipeline.
- **FR-002**: The system MUST produce diarization output in RTTM format (e.g. as produced in NeMo pred_rttms or equivalent).
- **FR-003**: The system MUST parse RTTM diarization output into segments represented as (speaker, start, end) for use in alignment.
- **FR-004**: The system MUST use these parsed (speaker, start, end) segments to align speaker labels to the transcribed words or segments.
- **FR-005**: Documentation and specification MUST state MarbleNet as the VAD used for diarization and RTTM as the diarization output format, so that pipeline and spec are aligned.

### Key Entities

- **Voice activity detection (VAD)**: Decides which parts of the audio contain speech; the system uses MarbleNet for this role in diarization.
- **RTTM (Rich Transcription Time Marked)**: Standard text format for diarization output; one line per speaker segment with file, channel, start, duration, and speaker id.
- **Speaker segment**: A tuple (speaker, start, end) derived from RTTM, used to assign speaker labels to transcript segments during alignment.

## Assumptions

- NeMo (or equivalent) is the source of diarization output; RTTM is the chosen interchange format (e.g. pred_rttms).
- MarbleNet is available and supported in the diarization stack; no requirement to support multiple VAD backends for this feature.
- Alignment of (speaker, start, end) to words is implemented elsewhere; this feature only requires that segments are produced in that form.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All voice activity used for diarization is produced by MarbleNet VAD (no mixed or undocumented VAD in that path).
- **SC-002**: Diarization output is valid RTTM that can be parsed by a standard RTTM reader into (speaker, start, end) segments.
- **SC-003**: Aligned transcript shows correct speaker labels for each segment according to the parsed diarization segments.
- **SC-004**: Pipeline documentation and product specification agree on VAD (MarbleNet) and diarization output format (RTTM).
