# Voice Fingerprinting - Development Plan

**Project:** Voice Transcription with Speaker Identification  
**Platform:** Mac M2 32GB (local processing)  
**Approach:** Spec-driven development using Spec Kit  
**Status:** Research Phase Complete → Planning Phase

---

## Phase Overview

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 1. Research | Technical findings, tool evaluation | ✅ Complete |
| 2. Specification | Detailed spec using Spec Kit | 🔄 In Progress |
| 3. Prototype | MVP with core functionality | ⏳ Pending |
| 4. Development | Full implementation | ⏳ Pending |
| 5. Testing | Mac M2 performance validation | ⏳ Pending |
| 6. Deployment | Package/distribute | ⏳ Pending |

## Test Data Available

**Primary Test File:**
- Video: `/Volumes/2TB/Sync/Flat/Flerfs/C C/Videos/Think about it friday on our Flat-earth 2025-01-17.mp4`
- Transcript: `...2025-01-17.txt` (ground truth available)
- Speaker: Chris (Westchester County) - 16 min monologue
- Use: Single speaker ID, real-world audio quality testing

**Test Data Doc:** `TEST-DATA.md` (detailed scenarios & metrics)

---

## Specification Structure (Spec Kit)

### 1. Overview
- Project name and description
- Target platform (Mac M2 32GB)
- Core value proposition
- Success criteria

### 2. Functional Requirements

#### Core Features (MVP)
- [ ] Audio file upload (MP3, WAV, M4A)
- [ ] Automatic transcription (Whisper)
- [ ] Speaker diarization (identify "who spoke when")
- [ ] Voice fingerprinting (identify specific speakers)
- [ ] Export results (JSON, TXT, SRT)

#### Advanced Features (v2)
- [ ] Real-time processing (microphone input)
- [ ] Speaker enrollment/registration
- [ ] Voice comparison across multiple files
- [ ] Confidence scores per speaker
- [ ] Batch processing

### 3. Technical Architecture

#### Stack Selection
| Component | Primary Choice | Fallback |
|-----------|---------------|----------|
| ASR | Whisper (base/medium) | Whisper.cpp |
| Diarization | Pyannote.audio 3.1 | - |
| Embeddings | SpeechBrain ECAPA-TDNN | Resemblyzer |
| UI | Web-based (Django/Flask) | CLI |
| Storage | Local filesystem | SQLite |

#### Pipeline Design
```
Input Audio
    ↓
[Voice Activity Detection] → Remove silence
    ↓
[Speech Recognition] → Whisper → Raw transcript
    ↓
[Speaker Diarization] → Pyannote → Speaker segments
    ↓
[Voice Embedding] → ECAPA-TDNN → Speaker fingerprints
    ↓
[Clustering/Identification] → Group by speaker
    ↓
[Alignment] → Match words to speakers
    ↓
Output: Labeled transcript + speaker profiles
```

### 4. Performance Requirements

#### Mac M2 32GB Targets
| Metric | Target | Stretch |
|--------|--------|---------|
| Transcription speed | 1x real-time | 2x real-time |
| Diarization overhead | <50% of ASR time | <30% |
| Memory usage | <16GB | <8GB |
| File size limit | 4 hours | 8 hours |

### 5. Interface Design

#### CLI Interface
```bash
voice-fp transcribe audio.mp3 --speakers 2 --output results.json
voice-fp enroll --name "John" --samples john_samples/
voice-fp identify audio.mp3 --database speakers.db
```

#### Web Interface
- Upload page with drag-and-drop
- Progress tracking for long files
- Speaker timeline visualization
- Download/export options
- Speaker management panel

### 6. Data Model

```
Session
├── audio_file (path, duration, format)
├── transcription (words with timestamps)
├── speakers []
│   ├── speaker_id
│   ├── voice_embedding (vector)
│   ├── segments []
│   └── confidence_score
└── metadata (processing time, model versions)
```

### 7. Testing Strategy

- Unit tests for each pipeline stage
- Integration tests with sample audio
- Performance benchmarks on Mac M2
- Accuracy evaluation against ground truth

### 8. Deployment

- Python package (pip install)
- Docker container (optional)
- Homebrew formula (stretch goal)

---

## Research Summary (For Spec)

### Key Findings to Include

1. **WhisperX** is the proven baseline (70x real-time with diarization)
2. **Pyannote.audio 3.1** is SOTA for speaker diarization
3. **SpeechBrain ECAPA-TDNN** best for voice embeddings
4. **Mac M2 32GB** can run base/medium models at real-time
5. **"Name of the..."** project proves full-stack is viable

### Technical Risks

| Risk | Mitigation |
|------|------------|
| Pyannote requires HF auth | Document setup process |
| Large model = slow on M2 | Use base/medium, quantize if needed |
| Speaker overlap handling | Use pyannote 3.1 overlapping speech support |
| Memory limits on 32GB | Stream processing, batch size limits |

---

## Next Steps

1. **Create Spec Kit specification** (markdown format)
2. **Define MVP scope** (cut features to ship faster)
3. **Set up project structure**
4. **Begin prototype** with WhisperX + Pyannote

---

## Open Questions for Spec

1. CLI-only or web UI for MVP?
2. Real-time processing required or batch-only?
3. Speaker enrollment database scope?
4. Export formats priority?

*Ready to write the full specification when you are.*
