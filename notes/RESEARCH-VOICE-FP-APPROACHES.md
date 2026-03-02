# Voice Fingerprinting: Two Approaches Compared

**Date:** 2026-02-19  
**Researcher:** Toona  
**Topic:** WhisperX Integrated vs Modular (faster-whisper + separate speaker ID)

---

## Executive Summary

Two viable architectures for voice fingerprinting:

1. **APPROACH 1: WhisperX (Integrated)** - All-in-one solution with built-in speaker diarization
2. **APPROACH 2: Modular** - faster-whisper for transcription + separate speaker embedding tool

**Winner for Voice Fingerprinting Project:** **APPROACH 2 (Modular)** - More flexibility, better speaker recognition accuracy, reusable embeddings.

---

## Approach 1: WhisperX (Integrated)

### Architecture
```
Audio → WhisperX Pipeline:
    ├── VAD (Voice Activity Detection)
    ├── Whisper ASR (transcription)
    ├── wav2vec2 Alignment (word timestamps)
    ├── Pyannote 3.1 Diarization (speaker segments)
    └── Output: Speaker-labeled transcript
```

### How Speaker "Fingerprinting" Works in WhisperX
- Uses **pyannote/segmentation-3.0** model
- Extracts speaker embeddings from audio segments
- Performs **agglomerative clustering** to group similar voices
- Labels speakers as SPEAKER_00, SPEAKER_01, etc.
- **No persistent voice profiles** - speakers are anonymous per-file

### Pros
| Advantage | Details |
|-----------|---------|
| ✅ One-liner setup | `pip install whisperx` - single dependency |
| ✅ 70x real-time speed | With batching and GPU |
| ✅ Word-level timestamps | wav2vec2 forced alignment |
| ✅ Works out-of-box | HuggingFace integration |
| ✅ Good accuracy | Professional-grade transcription |

### Cons
| Disadvantage | Details |
|--------------|---------|
| ❌ **No true voice fingerprinting** | Speakers are anonymous per-file |
| ❌ Cannot match speakers across files | Each file gets new SPEAKER_XX labels |
| ❌ No embedding export | Can't save voice profiles for later matching |
| ❌ Locked to Pyannote 3.1 | Cannot swap embedding models |
| ❌ Higher memory usage | Loads both Whisper + wav2vec2 + Pyannote |
| ❌ Requires HuggingFace token | For Pyannote models |

### Code Example
```python
import whisperx
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
audio_file = "meeting.wav"

# 1. Load audio
audio = whisperx.load_audio(audio_file)

# 2. Transcribe with Whisper
model = whisperx.load_model("large-v2", device)
result = model.transcribe(audio)

# 3. Align words
tmp_model, align_metadata = whisperx.load_align_model(
    language_code=result["language"], 
    device=device
)
result = whisperx.align(
    result["segments"], 
    tmp_model, 
    align_metadata, 
    audio, 
    device
)

# 4. Speaker diarization (anonymous only)
diarize_model = whisperx.DiarizationPipeline(
    model_name="pyannote/speaker-diarization-3.1",
    device=device
)
diarize_segments = diarize_model(audio)
result = whisperx.assign_word_speakers(diarize_segments, result)

# Output: SPEAKER_00, SPEAKER_01 (anonymous per-file)
print(result["segments"])
```

---

## Approach 2: Modular (faster-whisper + Separate Speaker ID)

### Architecture
```
Audio → faster-whisper (transcription)
     ↓
Segments + Timestamps
     ↓
Speaker Embedding Model (Pyannote 3.1 / SpeechBrain ECAPA / NeMo TitaNet)
     ↓
Embedding Vector (192-512 dimensions)
     ↓
Voice Database (cosine similarity matching)
     ↓
Named Speaker Labels ("Chris", "Josh", "Unknown")
```

### Speaker Embedding Options

#### Option A: Pyannote 3.1 (Recommended)
```python
from pyannote.audio import Pipeline, Model, Inference

# Load embedding model
embedding_model = Model.from_pretrained("pyannote/embedding", 
                                        use_auth_token=HF_TOKEN)
inference = Inference(embedding_model, window="whole")

# Extract embedding for a speaker segment
embedding = inference.crop(audio_file, segment)
# embedding is a 512-dimensional vector

# Compare embeddings (cosine similarity)
from scipy.spatial.distance import cosine
similarity = 1 - cosine(embedding1, embedding2)
```

**Pros:**
- ✅ 512-dimensional embeddings
- ✅ Can save/load embeddings for voice database
- ✅ State-of-the-art accuracy (Pyannote 3.1)
- ✅ Works with custom speakers

**Cons:**
- ⚠️ Requires HuggingFace token
- ⚠️ Slightly slower than specialized models

#### Option B: SpeechBrain ECAPA-TDNN
```python
from speechbrain.pretrained import EncoderClassifier

classifier = EncoderClassifier.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb"
)

# Extract embedding
signal = read_audio(audio_file)
embedding = classifier.encode_batch(signal)
# embedding is 192-dimensional
```

**Pros:**
- ✅ 192-dimensional embeddings (smaller, faster)
- ✅ No token required
- ✅ Well-documented
- ✅ Good accuracy on VoxCeleb

**Cons:**
- ⚠️ Slightly lower accuracy than Pyannote 3.1
- ⚠️ More setup required

#### Option C: NeMo TitaNet (Best Accuracy)
```python
from nemo.collections.asr.models import EncDecSpeakerLabelModel

model = EncDecSpeakerLabelModel.from_pretrained(
    model_name="titanet_large"
)

# Extract embedding
embedding = model.get_embedding(audio_file)
# embedding is 192-dimensional
```

**Pros:**
- ✅ **Best accuracy** in benchmarks
- ✅ NVIDIA optimized
- ✅ Good for noisy audio

**Cons:**
- ⚠️ Requires NeMo installation (heavy)
- ⚠️ CUDA preferred

### Benchmark Results (Speaker Diarization Error Rate)

| Model | AMI (array) | AMI (headset) | VoxConverse | DIHARD III |
|-------|-------------|---------------|-------------|------------|
| NeMo TitaNet-Large | 26.8% | 36.7% | **Best** | 58.1% |
| Pyannote 3.1 | 32.9% | 45.4% | 54.6% | 60.1% |
| SpeechBrain ECAPA | ~35% | ~48% | ~55% | ~62% |

*Lower is better. Source: EDM 2025 research paper*

### Pros of Modular Approach
| Advantage | Details |
|-----------|---------|
| ✅ **True voice fingerprinting** | Save embeddings, match across files |
| ✅ **Named speakers** | "Chris said..." instead of SPEAKER_00 |
| ✅ **Swappable components** | Use best-in-class for each task |
| ✅ **2-4x faster transcription** | faster-whisper vs WhisperX base |
| ✅ **Lower memory** | Don't load wav2vec2 alignment |
| ✅ **Flexible deployment** | CPU-friendly with INT8 quantization |
| ✅ **No HuggingFace token** | If using SpeechBrain |

### Cons of Modular Approach
| Disadvantage | Details |
|--------------|---------|
| ⚠️ More complex setup | Multiple libraries to install |
| ⚠️ Manual timestamp alignment | Match diarization segments to transcript |
| ⚠️ Timecode sync issues | Different models = different timestamps |

### Code Example
```python
from faster_whisper import WhisperModel
from pyannote.audio import Model, Inference
from pyannote.core import Segment
import numpy as np
from scipy.spatial.distance import cosine

# 1. Transcribe with faster-whisper
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
segments, info = whisper_model.transcribe("meeting.wav")

transcript_segments = []
for segment in segments:
    transcript_segments.append({
        "start": segment.start,
        "end": segment.end,
        "text": segment.text
    })

# 2. Load speaker embedding model
embedding_model = Model.from_pretrained("pyannote/embedding")
inference = Inference(embedding_model, window="whole")

# 3. Extract embeddings for each segment
voice_db = {}  # speaker_name -> [embeddings]

for seg in transcript_segments:
    segment = Segment(seg["start"], seg["end"])
    embedding = inference.crop("meeting.wav", segment)
    
    # 4. Match against voice database
    best_match = None
    best_score = float('inf')
    
    for name, db_embeddings in voice_db.items():
        for db_emb in db_embeddings:
            score = cosine(embedding, db_emb)
            if score < best_score and score < 0.25:  # Threshold
                best_score = score
                best_match = name
    
    if best_match:
        seg["speaker"] = best_match
        voice_db[best_match].append(embedding)
    else:
        seg["speaker"] = f"SPEAKER_{len(voice_db)}"
        voice_db[seg["speaker"]] = [embedding]

# Output: Transcript with named speakers
for seg in transcript_segments:
    print(f"[{seg['speaker']}] {seg['text']}")
```

---

## Detailed Comparison

| Feature | WhisperX | Modular (faster-whisper + Pyannote) |
|---------|----------|-------------------------------------|
| **True voice fingerprinting** | ❌ No | ✅ Yes |
| **Speaker matching across files** | ❌ No | ✅ Yes |
| **Named speakers** | ❌ Anonymous | ✅ Named |
| **Embedding persistence** | ❌ No | ✅ Save/load |
| **Transcription speed** | 1x (baseline) | 2-4x faster |
| **Memory usage** | High (3 models) | Medium (2 models) |
| **Setup complexity** | Low | Medium |
| **Word-level timestamps** | ✅ Built-in | ⚠️ Manual alignment |
| **Speaker accuracy** | Good | Better (swappable models) |
| **Mac M2 compatibility** | ✅ Yes | ✅ Yes (INT8) |
| **Offline capable** | ✅ Yes | ✅ Yes |
| **Batch processing** | ✅ 70x | ✅ 10-20x |

---

## Voice Fingerprinting Workflow (Modular Approach)

### Phase 1: Enrollment
```python
# Record known speakers (30-60 seconds each)
enrollments = {
    "Chris": "chris_sample.wav",
    "Josh": "josh_sample.wav"
}

voice_db = {}
for name, audio_file in enrollments.items():
    embedding = inference(audio_file)
    voice_db[name] = embedding
    
# Save to disk
np.savez("voice_database.npz", **voice_db)
```

### Phase 2: Recognition
```python
# Load voice database
voice_db = dict(np.load("voice_database.npz"))

# Process new audio
for segment in new_audio_segments:
    embedding = inference.crop(audio_file, segment)
    
    # Find best match
    for name, db_emb in voice_db.items():
        similarity = 1 - cosine(embedding, db_emb)
        if similarity > 0.75:  # Threshold
            print(f"Identified as {name} ({similarity:.2f})")
```

---

## Recommendations

### For Voice Fingerprinting Project

**Use APPROACH 2 (Modular)** with this stack:

```
Transcription: faster-whisper (base or medium, INT8)
Speaker Embeddings: Pyannote 3.1 (512-dim)
Matching: Cosine similarity with threshold (0.75)
Database: NumPy arrays or SQLite with embeddings
```

**Why:**
- Can build a voice database of flat earthers
- Match speakers across multiple videos
- Name speakers ("Mark Sargent", "Joshua Swift")
- 2-4x faster transcription
- More accurate speaker identification

### When to Use WhisperX Instead

Use WhisperX if you only need:
- Anonymous speaker labels (SPEAKER_00, SPEAKER_01)
- One-time transcription without speaker matching
- Quick setup for single-file processing
- Word-level timestamps out-of-box

---

## Performance Estimates (Mac M2 32GB)

| Task | WhisperX | Modular (faster-whisper + Pyannote) |
|------|----------|-------------------------------------|
| 10-min audio transcription | ~60s | ~30s |
| Speaker diarization | ~20s | ~25s |
| Total processing | ~80s | ~55s |
| Memory usage | ~12GB | ~8GB |
| Speaker matching across files | ❌ | ✅ |

---

## Sources

1. WhisperX GitHub: https://github.com/m-bain/whisperX
2. faster-whisper GitHub: https://github.com/SYSTRAN/faster-whisper
3. Pyannote.audio GitHub: https://github.com/pyannote/pyannote-audio
4. SpeechBrain: https://speechbrain.github.io/
5. NVIDIA NeMo: https://github.com/NVIDIA/NeMo
6. BrassTranscripts WhisperX Tutorial
7. GoTranscript Pyannote Tutorial
8. EDM 2025 Research Paper (Speaker Diarization)
9. Gladia Speaker Identification Guide
10. Odyssey 2024: ECAPA2 Speaker Embeddings

---

*Research complete. Recommendation: Use modular approach for true voice fingerprinting with named speaker recognition.*
