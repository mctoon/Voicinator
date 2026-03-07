# 🎙️ Voicinator

**Voice Fingerprinting & Transcription Research Project**

Voicinator is a research initiative to build a voice fingerprinting system capable of identifying flat earth proponents ("flerfs") across thousands of YouTube videos.

---

## 🎯 Mission

Build a production-quality voice fingerprinting pipeline that can:
1. Transcribe thousands of flat earth videos with high accuracy
2. Extract unique voice fingerprints from speakers
3. Match voices across multiple videos
4. Build a searchable database of flat earth proponents

---

## 🏗️ Architecture

### Quality-First Stack (Recommended)

```
Audio Input
     ↓
Whisper Large-v3 (ASR)
     ↓
NeMo Neural MSDD (Speaker Diarization)
     ↓
TitaNet-Large (Speaker Embeddings)
     ↓
Cosine Similarity Matching
     ↓
Voice Database (SQLite/PostgreSQL)
```

### Key Metrics

| Component | Model | Performance |
|-----------|-------|-------------|
| **Transcription** | Whisper Large-v3 | 2.1% WER (clean), 17% WER (noisy) |
| **Speaker ID** | NeMo Neural MSDD | 8.1% DER (55% better than Pyannote) |
| **Embeddings** | TitaNet-Large | 192-dim, 94% accuracy |
| **Speed** | faster-whisper backend | 2-4x faster than original |

---

## 📊 Mission Control Dashboard

Access the real-time project dashboard:

- **🌐 Dashboard:** http://localhost:8027/voicinator/
- **📄 Status MD:** http://localhost:8027/voicinator/status.md
- **🔌 API:** http://localhost:8027/voicinator/api/status

### Dashboard Features

- **Research Topics:** Track progress across 6 research areas
- **Success Log:** Recent milestones and achievements
- **Action Items:** Prioritized todo list
- **Model Benchmarks:** Performance comparisons
- **Cool Discoveries:** Interesting findings
- **Project Stats:** Key metrics at a glance

---

## 📁 Project Structure

```
/Users/mctoon/.openclaw/workspace/research/voicinator/
├── README.md                    # This file
├── ALTERNATIVES.md              # Whisper variants comparison
├── QUALITY-REEVALUATION.md      # Quality-first analysis
├── RESEARCH-VOICE-FP-APPROACHES.md  # Voice fingerprinting approaches
├── SPECIFICATION.md             # Technical specification
├── TEST-RESULTS.md              # Prototype test results
├── poc-test/                    # Proof of concept files
│   ├── voice_profile.json
│   └── poc_results.json
└── daily-notes/                 # Research logs

Mission Control Django App:
/Volumes/2TB/Sync/openclaw/mission-control/voicinator/
├── models.py                    # Data models
├── views.py                     # Dashboard views
├── admin.py                     # Admin interface
├── templates/voicinator/        # Dashboard templates
└── init_data.py                 # Initial data script
```

---

## 🔬 Research Topics

| Topic | Phase | Progress | Status |
|-------|-------|----------|--------|
| Whisper Model Evaluation | Research | ✅ 100% | Complete |
| Speaker Diarization Comparison | Research | ✅ 100% | Complete |
| Voice Fingerprinting Architecture | Prototype | 60% | In Progress |
| Speaker Embedding Models | Research | 90% | Complete |
| Mac M2 Performance Optimization | Development | 40% | In Progress |
| Batch Processing Pipeline | Discovery | 10% | Pending |

---

## 🔥 Recent Successes

1. **Whisper Large-v3 Tested at 22x Real-time** - Prototype validated
2. **NeMo Neural 55% Better than Pyannote** - Critical accuracy finding
3. **Complete Whisper Alternatives Survey** - 7 variants documented
4. **Quality Stack Defined** - Architecture finalized
5. **2,063 Test Videos Discovered** - Dataset ready

---

## 📝 Action Items

### Critical
- [ ] Complete Voice Fingerprinting POC

### High Priority
- [ ] Install NeMo Toolkit
- [ ] Create Voice Database Schema

### Medium Priority
- [ ] Benchmark Processing Speed
- [ ] Document API for Voice Matching

### Low Priority
- [ ] Test Batch Processing 100 Videos

---

## 💎 Cool Discoveries

- **WhisperX Does 70x Real-time** - With batching and speaker diarization
- **NeMo TitaNet Best for Noisy Audio** - 26.8% DER vs 32.9% Pyannote
- **faster-whisper 4x Speed Improvement** - Same accuracy, much faster
- **Japanese Needs Longer Context** - DER improves from 15.7% to 6.7%
- **Distil-Whisper 6.3x Faster** - Only 1% WER difference

---

## 🛠️ Development

### Prerequisites

- Python 3.9+
- Mac M2 (or Linux with CUDA)
- 32GB RAM recommended
- FFmpeg

### Installation

```bash
cd /Volumes/2TB/Sync/openclaw/mission-control
source venv/bin/activate
pip install faster-whisper librosa numpy scipy
```

### Running Dashboard

```bash
venv/bin/python3 manage.py runserver 0.0.0.0:8027
```

### Initialize Data

```bash
venv/bin/python3 manage.py shell < voicinator/init_data.py
```

---

## 📚 Documentation

- **Whisper Variants:** See `ALTERNATIVES.md`
- **Quality Analysis:** See `QUALITY-REEVALUATION.md`
- **Voice Fingerprinting Approaches:** See `RESEARCH-VOICE-FP-APPROACHES.md`
- **Technical Spec:** See `SPECIFICATION.md`

---

## 🦞 The Flerf Whisperer

*"I am the Flerf Whisperer. I hear their voices across the flat earth videos, and I know who speaks."*

This project maintains the persona of the Flerf Whisperer - an expert researcher who tracks and documents flat earth proponents through their unique vocal signatures.

---

## 📊 Stats

- **Test Videos Available:** 2,063
- **Research Documents:** 4
- **Models Evaluated:** 12
- **Best WER:** 2.1%
- **Best DER:** 8.1%

---

## 🔮 Future

- Scale to full dataset (2,000+ videos)
- Build searchable voice database
- Create API for real-time voice matching
- Integrate with flerf.info wiki
- Automatic flat earth debate detection

---

*Part of the OpenClaw Mission Control ecosystem*
