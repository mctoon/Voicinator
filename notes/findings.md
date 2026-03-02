# Voice Fingerprinting Research - Master Findings

**Project:** Voice Transcription + Speaker Identification Research  
**Goal:** Become the world expert on local, privacy-preserving voice transcription with speaker identification

---

## 📊 EXECUTIVE SUMMARY

This document tracks significant findings in voice transcription and speaker identification technology, with focus on:
- Local/offline solutions (privacy-first)
- Mac M2 32GB compatibility
- Open-source tools and architectures
- Commercial alternatives for comparison

---

## 🏆 MAJOR BREAKTHROUGHS

### February 19, 2026 - PyAnnote Precision-2 Release
**Significance:** 28% accuracy improvement over open-source version

PyAnnote's Precision-2 model (released Sept 2025) represents the current state-of-the-art in speaker diarization:
- DER reduction from ~18% to ~12% on standard benchmarks
- 70% accuracy in speaker count prediction (vs 50% previously)
- Available via hosted API (no infrastructure needed)

**Implications:** Production-grade diarization is now accessible without managing GPU infrastructure.

---

## 🛠️ RECOMMENDED TOOL STACK

### For Mac M2 32GB - Local Processing

**Tier 1: Lightweight & Fast**
```
Transcription: whisper.cpp (base.en model)
Speaker ID:    whisper.cpp tinydiarize (SPEAKER_TURN)
LLM:           Ollama + llama3.2 (3B)
```
- Pros: Real-time performance, minimal battery impact
- Cons: Basic speaker separation only

**Tier 2: Balanced Accuracy**
```
Transcription: whisper.cpp (small.en model)  
Speaker ID:    Pyannote.audio Community-1
LLM:           Ollama + mistral (7B)
```
- Pros: Good accuracy, still local
- Cons: Slower processing, ~0.7x real-time

**Tier 3: Maximum Quality (Batch Processing)**
```
Transcription: Whisper large-v3
Speaker ID:    Pyannote Precision-2 (via API)
LLM:           Cloud or local llama3.3 (if 96GB+ RAM)
```
- Pros: Best possible accuracy
- Cons: Requires cloud for diarization or powerful GPU

---

## 📈 PERFORMANCE BENCHMARKS

### Speaker Diarization Error Rate (DER)
Lower is better - indicates % of time misattributed to wrong speaker

| Model | DER | Speed (RTF) | Best For |
|-------|-----|-------------|----------|
| NeMo Neural (MSDD) | 8.1% | 0.020 | Accuracy |
| Pyannote Precision-2 | ~12% | ~0.025 | Production API |
| NeMo Clustering | 10.3% | 0.010 | Speed |
| Pyannote Community-1 | ~17% | ~0.025 | Open source |
| Pyannote 3.1 (legacy) | 18.1% | 0.027 | Legacy apps |

### Whisper.cpp on Mac M2
| Model | Real-time Factor | Memory | Quality |
|-------|-----------------|--------|---------|
| tiny.en | 3-4x | ~50MB | Basic |
| base.en | 1.8x | ~150MB | Good |
| small.en | 0.7x | ~500MB | Very Good |
| medium.en | 0.35x | ~1.5GB | Excellent |
| large-v3 | <0.2x | ~3GB | Best |

---

## 🎯 KEY PROJECTS REFERENCE

### Transcription Engines

| Project | Stars | Language | Best Feature |
|---------|-------|----------|--------------|
| [whisper.cpp](https://github.com/ggml-org/whisper.cpp) | 35k+ | C++ | Apple Silicon optimization |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | 15k+ | Python | CTranslate2 acceleration |
| [WhisperX](https://github.com/m-bain/whisperX) | 20k+ | Python | Word-level timestamps + diarization |
| [Handy](https://github.com/cjpais/Handy) | 14k+ | Rust/TS | Complete offline STT |
| [RealtimeSTT](https://github.com/KoljaB/RealtimeSTT) | 9.4k+ | Python | Low-latency + wake word |

### Speaker Diarization

| Project | Stars | Type | Notes |
|---------|-------|------|-------|
| [Pyannote.audio](https://github.com/pyannote/pyannote-audio) | 11k+ | Python | Research-grade, SOTA models |
| [vo-id](https://github.com/CiscoDevNet/vo-id) | 200+ | Python | Cisco's voice fingerprinting |
| [FluidAudio](https://github.com/FluidInference/FluidAudio) | 1.5k+ | Swift | CoreML on-device |
| whisper.cpp tinydiarize | N/A | C++ | Lightweight speaker turns |

### Complete Solutions

| Project | Stars | Stack | Use Case |
|---------|-------|-------|----------|
| [noScribe](https://github.com/kaixxx/noScribe) | 1.8k | Whisper+Pyannote | GUI transcription |
| [Meetily](https://github.com/zackriya/meetily) | New | Whisper+Ollama | Meeting notes |
| [ollama-voice-mac](https://github.com/apeatling/ollama-voice-mac) | 515 | Whisper+Ollama | Voice assistant |

---

## 💡 ARCHITECTURAL PATTERNS

### Pattern 1: Pipeline Architecture
```
Audio → VAD → Transcription → Diarization → LLM Enrichment
        ↓         ↓              ↓               ↓
     (silero)  (whisper)    (pyannote)    (summarization)
```
- Best for: Maximum flexibility
- Tools: Modular, swappable components
- Complexity: High

### Pattern 2: All-in-One Container
```
Meetily / similar platforms
```
- Best for: Quick deployment
- Tools: Docker-based
- Complexity: Low

### Pattern 3: Edge/On-Device
```
FluidAudio / iOS CoreML approach
```
- Best for: Privacy-critical, mobile
- Tools: CoreML, ANE
- Complexity: Medium

---

## ⚠️ KNOWN LIMITATIONS

### Mac M2 Specific
1. No CUDA acceleration (Apple Silicon uses Metal/CoreML)
2. PyTorch MPS backend missing some operators for Whisper
3. Full diarization is CPU-bound and slower than GPU
4. Memory pressure when running large LLM + large Whisper simultaneously

### General
1. Speaker diarization accuracy degrades with:
   - Heavy overlapping speech
   - Many speakers (6+)
   - Poor audio quality
   - Similar-sounding speakers
2. Japanese language particularly challenging for diarization
3. Real-time diarization still largely unsolved (batch processing preferred)

---

## 🔮 EMERGING TRENDS

1. **Unified Speech Models** - Moving beyond pipeline approach to end-to-end speech-to-text with built-in speaker ID
2. **Quantization** - 1-bit and 1.58-bit quantization (BitNet) enabling larger models on smaller hardware
3. **Neural Speech-to-Speech** - Direct audio→audio models without text intermediate
4. **On-Device Optimization** - CoreML, ANE, and mobile-optimized architectures
5. **Streaming Diarization** - Real-time speaker identification (still experimental)

---

## 📋 TESTING CHECKLIST

For evaluating new voice transcription solutions:

- [ ] Accuracy on noisy audio
- [ ] Speaker count accuracy (2, 4, 6+ speakers)
- [ ] Overlapping speech handling
- [ ] Processing speed (real-time factor)
- [ ] Memory usage
- [ ] Battery impact (for laptops)
- [ ] Language support quality
- [ ] Timestamp accuracy
- [ ] Integration complexity
- [ ] Cost (API vs local compute)

---

## 📝 RESEARCH LOG

| Date | Key Finding | Source |
|------|-------------|--------|
| 2026-02-19 | PyAnnote Precision-2 released (+28% accuracy) | pyannote.ai |
| 2026-02-19 | whisper.cpp tinydiarize feature discovered | github.com |
| 2026-02-19 | Meetily v0.0.5 released | dev.to |
| 2026-02-19 | NeMo MSDD benchmarked at 8.1% DER | voice-ping.com |

---

*Last Updated: February 19, 2026*
*Next Review: February 20, 2026*
