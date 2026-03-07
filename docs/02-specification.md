# Specification (concise)

**Spec version:** 1.0.0 · **Status:** Draft

## Problem and solution

- **Problem:** Cloud transcription (e.g. Otter) is paid and not private; no good local option on Mac.
- **Solution:** Local transcription + speaker diarization + voice fingerprinting on Mac M2; quality-first, speed second.

## Goals

- Transcribe with speaker labels; identify speakers across files; Mac M2 only; free software; hundreds of speakers; English only.

## Success criteria

| Criteria        | Target        |
|----------------|---------------|
| Transcription  | &gt;95% accuracy (clear audio) |
| Diarization    | &lt;10% DER   |
| Performance    | ≥2× real-time on M2 |
| Usability      | Single-command operation |

## Functional requirements

**MVP (Phase 1)**  
- **FR-001** Audio ingest: MP3, WAV, M4A, FLAC, OGG, MP4, MOV, AVI, MKV; max 12 h.  
- **FR-002** Transcription: Whisper Large-v3, word timestamps, English, JSON.  
- **FR-003** Diarization: NeMo MSDD; segments (Speaker A/B/…); min 250 ms; handle overlap.  
- **FR-004** Voice fingerprinting: unique signatures, SQLite, cosine similarity.  
- **FR-005** Export: JSON, TXT, SRT, CSV.

**Phase 2**  
- **FR-006** Batch: scan folders, one file at a time, progress tracking.  
- **FR-007** Voice comparison: similarity score, configurable threshold (default 0.85).

## Non-functional requirements

- **Performance:** ≥2× real-time; ≤16 GB RAM; ≤10 GB models; startup ≤10 s.  
- **Platform:** macOS 15+ (Apple Silicon); min M2 16 GB; recommended 32 GB; MPS if available.  
- **Privacy:** No cloud, no telemetry, no network except one-time model download.  
- **Usability:** CLI with defaults; optional web UI; progress and clear errors.

## Tech stack (summary)

- Python 3.11+; Whisper (large-v3); NeMo MSDD; TitaNet (embeddings); Silero VAD; FAISS or Qdrant for vectors.
- Optional: Flask/Django for web UI.

## Data flow

Preprocess (e.g. 16 kHz mono) → VAD → ASR (Whisper) → Diarization (NeMo) → Embeddings → Align words to speakers → Export (JSON/TXT/SRT/CSV).

## Interfaces

- **CLI:** `transcribe`, `enroll`, `identify`, `speakers` (see original SPECIFICATION.md for full options).
- **Config:** `~/.voiceprint/config.yaml` (models, paths, performance, privacy).

## Data models (summary)

- **Transcription output:** metadata, speakers (id, name, enrolled, embedding_id, segments, time), transcript (speaker, start, end, text, words, confidence), diarization segments.
- **Speaker profile:** speaker_id, name, description, enrolled_at, samples count, embedding vector, optional voice_stats.

## Milestones (reference)

M1 Spec → M2 Core pipeline (ASR + diarization) → M3 Fingerprinting → M4 CLI → M5 MVP → M6 Web UI → M7 v1.0.

## Risks

- NeMo/Pyannote license changes; M2 performance; overlap/noise; model download; memory. See original SPECIFICATION.md for mitigations.
