# Specification: Voice Fingerprinting System

**Spec Version:** 1.0.0  
**Date:** 2026-02-19  
**Status:** Draft  
**Author:** Toona (AI Assistant)  
**Stakeholder:** MCToon (Michael Toon)  

---

## 1. Executive Summary

### 1.1 Project Overview
**Name:** Voiceinator
**Tagline:** Local voice transcription with speaker identification  

**Problem:** Existing solutions (Otter.ai, etc.) require cloud processing, subscription fees, and compromise privacy. No good local alternative exists for Mac users.

**Solution:** A privacy-first, locally-running voice transcription system with speaker diarization and voice fingerprinting, optimized for Mac M2 32GB.  Quality is the priority, speed is secondary.

### 1.2 Goals

**Primary:**
- Transcribe video and audio files locally with speaker labels
- Identify specific speakers across multiple recordings
- Run entirely on Mac M2 without cloud dependencies
- Use free software
- Support for hundreds of speakers
- Support for only English


### 1.3 Success Criteria

| Criteria | Measure |
|----------|---------|
| Transcription accuracy | >95% WER on clear audio |
| Speaker diarization | <10% DER (Diarization Error Rate) |
| Performance | 2x real-time on Mac M2 |
| Usability | Single-command operation |

---

## 2. Functional Requirements

### 2.1 Core Features (MVP - Phase 1)

#### FR-001: Audio File Ingesting
**Priority:** P0  
**Description:** Accept audio and video files in common formats  
**Formats:** MP3, WAV, M4A, FLAC, OGG, MP4, MOV, AVI, MKV  
**Max duration:** 12 hours
**Max file size:** None

#### FR-002: Automatic Transcription
**Priority:** P0  
**Description:** Convert speech to text with word-level timestamps  
**Language:** English only  
**Model:** Whisper Large-v3 
**Output format:** JSON with word timestamps

#### FR-003: Speaker Diarization
**Priority:** P0  
**Description:** Identify "who spoke when" without knowing speakers in advance  
**Output:** Speaker segments (Speaker A, B, C...)  
**Minimum segment:** 250ms  
**Model:** NeMo Neural (MSDD)
**Overlapping speech:** Handle if possible

#### FR-004: Voice Fingerprinting
**Priority:** P1  
**Description:** Create unique voice signatures for identified speakers  
**Storage:** SQLIte  database  
**Comparison:** Cosine similarity

#### FR-005: Export Results
**Priority:** P1  
**Formats:**
- JSON (full data)
- TXT (transcript with speaker labels)
- SRT (subtitles with speaker colors)
- CSV (word-level data)

### 2.2 Advanced Features (Phase 2)

#### FR-006: Batch Processing
**Priority:** P2  
**Description:** Scan folders for pending files and process them in order
**Parallelism:** 1 file at a time (memory constraint)  
**Progress tracking:** Yes

#### FR-007: Voice Comparison
**Priority:** P3  
**Description:** Compare voice across different recordings  
**Match score:** Similarity percentage  
**Threshold:** Configurable (default 0.85)

---

## 3. Non-Functional Requirements

### 3.1 Performance

| Metric | Requirement | Notes |
|--------|-------------|-------|
| Transcription speed | ≥2x real-time | Base model: better |
| Memory usage | ≤16GB RAM | Leave headroom for other apps |
| Disk space | ≤10GB for models | Models cached locally |
| Startup time | ≤10 seconds | Load models on first run |

### 3.2 Platform

**Target:** macOS 15+ (Apple Silicon)  
**Minimum:** Mac M2 with 16GB RAM  
**Recommended:** Mac M2/M3 with 32GB+ RAM  
**GPU:** Metal Performance Shaders (MPS) if available

### 3.3 Privacy & Security

- **No cloud processing** - all local
- **No telemetry** - no data collection
- **No network calls** - except model download (once)
- **File access** - only user-selected files

### 3.4 Usability

- **CLI:** Single command with sensible defaults
- **Web UI:** Browser-based interface
- **Progress:** Visual feedback for long operations
- **Errors:** Clear, actionable error messages

---

## 4. Technical Architecture

### 4.1 System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    VoicePrint Pro                           │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   CLI    │  │  Web UI  │  │          │  │  Export  │   │
│  │ Interface│  │          │  │          │  │  Modules │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       └──────────────┴──────────────┴──────────────┘        │
│                         │                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Processing Pipeline                      │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │  │
│  │  │   VAD    │→ │  ASR     │→ │ Diarization│         │  │
│  │  │(Silero)  │  │(Whisper) │  │(NeMo Neural │         │  │
│  │  └──────────┘  └──────────┘  └──────────┘          │  │
│  │       ↓              ↓              ↓                │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │     Speaker Embedding (SpeechBrain)            │ │  │
│  │  │     Voice Fingerprinting & Clustering          │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Data Layer                               │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │  │
│  │  │  Audio   │  │  Models  │  │  Results │          │  │
│  │  │  Files   │  │  (Cache) │  │  (JSON)  │          │  │
│  │  └──────────┘  └──────────┘  └──────────┘          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.11+ |
| ASR | OpenAI Whisper | base/medium |
| Diarization | NeMo Neural (MSDD) | Most recent |
| Embeddings | SpeechBrain | ECAPA-TDNN |
| VAD | Silero-VAD | 4.0 |
| UI (opt) | Flask/Django | Latest |
| Vector DB | FAISS | CPU version |
| Packaging | PyInstaller/Homebrew | - |

### 4.3 Data Flow

```
1. Input: audio.mp3 (30 minutes)
          ↓
2. Preprocess: Convert to 16kHz WAV
          ↓
3. VAD: Remove silence (save 10-20% time)
          ↓
4. ASR: Whisper transcribes → words.json
          ↓
5. Diarization: Pyannote segments → speakers.json
          ↓
6. Embedding: Extract voice fingerprints → embeddings.json
          ↓
7. Alignment: Match words to speakers → transcript.json
          ↓
8. Export: Generate TXT, SRT, CSV files
```

### 4.4 File Structure

```
voiceprint/
├── voiceprint/              # Main package
│   ├── __init__.py
│   ├── cli.py              # Command line interface
│   ├── transcribe.py       # ASR pipeline
│   ├── diarize.py          # Speaker diarization
│   ├── embed.py            # Voice embeddings
│   ├── align.py            # Word-speaker alignment
│   ├── export.py           # Output formatters
│   └── web/                # Optional web UI
│       ├── __init__.py
│       ├── app.py
│       └── templates/
├── models/                 # Downloaded models (gitignored)
├── tests/                  # Test suite
├── docs/                   # Documentation
├── requirements.txt
├── setup.py
├── README.md
└── Makefile
```

---

## 5. Interface Specification

### 5.1 CLI Commands

#### Transcribe
```bash
voiceprint transcribe <audio_file> [options]

Options:
  --model {base,medium,large}    Whisper model size (default: medium)
  --speakers N                   Expected speaker count (default: auto)
  --output DIR                   Output directory (default: ./output)
  --format {json,txt,srt,csv}    Output format (default: all)
  --language LANG                Audio language (default: auto-detect)
  --enroll SPEAKER_NAME          Enroll speakers for identification
```

**Example:**
```bash
voiceprint transcribe meeting.mp3 --model medium --speakers 4 --output ./results
```

#### Enroll
```bash
voiceprint enroll --name <speaker_name> <sample_files...>

Options:
  --name         Speaker name/ID (required)
  --description  Optional description
```

**Example:**
```bash
voiceprint enroll --name "John Doe" john_sample1.mp3 john_sample2.mp3
```

#### Identify
```bash
voiceprint identify <audio_file> --database <speaker_db>

Options:
  --database PATH    Path to speaker database
  --threshold FLOAT  Similarity threshold (default: 0.85)
```

#### List Speakers
```bash
voiceprint speakers [--database PATH]
```

### 5.2 Configuration File

`~/.voiceprint/config.yaml`:
```yaml
models:
  whisper: medium
  diarization: pyannote/speaker-diarization-3.1
  embedding: speechbrain/spkrec-ecapa-voxceleb

paths:
  models: ~/.voiceprint/models
  cache: ~/.voiceprint/cache
  output: ~/Documents/VoicePrint

performance:
  batch_size: 16
  num_workers: 4
  use_mps: true  # Metal Performance Shaders

privacy:
  telemetry: false
  auto_update: false
```

---

## 6. Data Models

### 6.1 Transcription Output (JSON)

```json
{
  "metadata": {
    "filename": "meeting.mp3",
    "duration": 1800.5,
    "language": "en",
    "model": "whisper-medium",
    "processed_at": "2026-02-19T10:30:00Z",
    "processing_time": 1200.0
  },
  "speakers": [
    {
      "id": "SPEAKER_00",
      "name": "John Doe",
      "enrolled": true,
      "embedding_id": "emb_001",
      "segments": 12,
      "total_time": 450.2
    },
    {
      "id": "SPEAKER_01",
      "name": null,
      "enrolled": false,
      "segments": 8,
      "total_time": 320.5
    }
  ],
  "transcript": [
    {
      "speaker": "SPEAKER_00",
      "start": 0.0,
      "end": 3.2,
      "text": "Welcome to the meeting everyone.",
      "words": [
        {"word": "Welcome", "start": 0.0, "end": 0.5, "confidence": 0.98},
        {"word": "to", "start": 0.5, "end": 0.7, "confidence": 0.99},
        ...
      ],
      "confidence": 0.95
    }
  ],
  "diarization": {
    "model": "pyannote/speaker-diarization-3.1",
    "segments": [
      {"speaker": "SPEAKER_00", "start": 0.0, "end": 45.2},
      {"speaker": "SPEAKER_01", "start": 45.5, "end": 78.3}
    ]
  }
}
```

### 6.2 Speaker Profile

```json
{
  "speaker_id": "john_doe_001",
  "name": "John Doe",
  "description": "CEO, speaks slowly",
  "enrolled_at": "2026-02-19T10:00:00Z",
  "samples": 3,
  "embedding": [0.023, -0.156, ...],  // 192-dim vector
  "voice_stats": {
    "pitch_mean": 125.5,
    "pitch_std": 15.2,
    "speaking_rate": 2.3
  }
}
```

---

## 7. Testing Strategy

### 7.1 Unit Tests
- Test each pipeline component independently
- Mock external dependencies
- 80% code coverage target

### 7.2 Integration Tests
- Full pipeline with sample audio files
- Test all export formats
- Error handling scenarios

### 7.3 Performance Tests
- Benchmark on Mac M2 with test files (30min, 1hr, 4hr)
- Memory profiling
- Compare base vs medium models

### 7.4 Accuracy Tests
- WER (Word Error Rate) on LibriSpeech
- DER (Diarization Error Rate) on AMI corpus
- Speaker identification accuracy

---

## 8. Milestones

| Milestone | Deliverable | ETA | Status |
|-----------|-------------|-----|--------|
| M1 | Spec complete | Feb 20 | 🔄 In Progress |
| M2 | Core pipeline (ASR+Diarization) | Feb 25 | ⏳ Pending |
| M3 | Voice fingerprinting | Mar 1 | ⏳ Pending |
| M4 | CLI complete | Mar 5 | ⏳ Pending |
| M5 | MVP release | Mar 10 | ⏳ Pending |
| M6 | Web UI | Mar 20 | ⏳ Pending |
| M7 | v1.0 release | Apr 1 | ⏳ Pending |

---

## 9. Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Pyannote license changes | High | Low | Cache models, monitor license |
| Mac M2 performance <1x | High | Medium | Optimize with MPS, quantize models |
| Speaker overlap hurts accuracy | Medium | Medium | Use pyannote 3.1 overlap handling |
| Model download failures | Medium | Medium | Mirror models, offline install option |
| Memory limits on 32GB | Medium | Low | Stream processing, clear cache |

---

## 10. Open Questions

1. **CLI vs Web UI priority?** Recommend CLI first, web UI as v2
2. **Real-time required for MVP?** Recommend no - batch processing first
3. **Speaker enrollment scope?** Start simple (3-5 samples), enhance later
4. **Export format priority?** JSON (full data) + TXT (readable) for MVP

---

## 11. Appendix

### A. Model Licenses
- Whisper: MIT (OpenAI)
- Pyannote: CC BY-NC-SA 4.0 (academic/non-commercial)
- SpeechBrain: Apache 2.0

### B. References
- Whisper paper: arXiv:2212.04356
- Pyannote 3.1: github.com/pyannote/pyannote-audio
- ECAPA-TDNN: arXiv:2005.07143

---

*Specification v1.0.0 - Ready for review*
