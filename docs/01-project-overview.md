# Project overview

**Name:** Voicinator  
**Tagline:** Voice fingerprinting and transcription (local, quality-first)

## Mission

- Transcribe audio/video at scale with high accuracy.
- Extract voice fingerprints and identify speakers across recordings.
- Build a searchable voice database (e.g. flat earth proponents across many YouTube videos).
- Run fully local on Mac M2; quality over speed; free software; English only.

## Architecture (quality-first stack)

1. **Audio input** → 2. **Whisper Large-v3 (ASR)** → 3. **NeMo Neural MSDD (diarization)** → 4. **TitaNet-Large (embeddings)** → 5. **Cosine similarity** → 6. **Voice DB (SQLite/PostgreSQL)**

## Key metrics

| Component    | Model             | Performance                          |
|-------------|-------------------|--------------------------------------|
| Transcription | Whisper Large-v3 | 2.1% WER clean, 17% noisy           |
| Speaker ID  | NeMo Neural MSDD  | 8.1% DER (much better than Pyannote) |
| Embeddings  | TitaNet-Large     | 192-dim, ~94% accuracy               |
| Speed       | faster-whisper    | 2–4× faster than stock Whisper      |

## Mission Control dashboard

- Dashboard: `http://localhost:8027/voicinator/`
- Status MD and API at same host; tracks research topics, action items, benchmarks, stats.

## Project structure (reference)

- Root: docs, original-research, notes, prototype-test, poc-test, resources, spec files.
- Mission Control app (separate): models, views, admin, templates, init_data.

## Research status (summary)

- Whisper and diarization comparison: done.
- Voice fingerprinting architecture and speaker embeddings: in progress.
- Mac M2 optimization and batch pipeline: pending.

See [original-research/README.md](../original-research/README.md) for full action items and stats.
