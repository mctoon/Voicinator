# Pipeline (concise)

End-to-end voice-to-text with speaker diarization, local on Mac M2.

## Overview

- **Core:** Whisper large-v3 (ASR) + NeMo MSDD (diarization); English; multiple speakers and overlap.
- **Audio:** Mono; chunk long files (e.g. 30 s with 5–10 s overlap).
- **Speakers:** Placeholder labels (Speaker_1, …) for unknowns; optional 5–10 s samples per speaker; flag to skip fingerprinting.
- **Execution:** Offline; free Python libs; Apple Silicon.

## Dependencies

- Python 3.10+; OpenAI Whisper (or faster-whisper); NeMo ASR (`nemo_toolkit[asr]`); pydub; librosa; FFmpeg (Homebrew).
- Mac M2: set MPS fallback for NeMo where needed.

## Input / output

- **Input:** Audio (e.g. WAV, MP3); any length; stereo allowed (converted to mono).
- **Output:** JSON or text with timestamped transcript, speaker labels, optional speaker sample clips.

## Pipeline steps

1. **Preprocess** – Load audio; convert to mono (e.g. average channels); 16 kHz, 16-bit; chunk &gt;30 s into 30 s segments with 5–10 s overlap; avoid cutting mid-word where possible.
2. **Transcribe** – Whisper large-v3, English-only; word-level timestamps per chunk; merge chunks and adjust timestamps in overlap regions.
3. **Diarize** – NeMo NeuralDiarizer (MSDD); VAD (MarbleNet), embeddings (TitaNet), clustering; RTTM with speaker segments and labels.
4. **Speaker handling** – Align Whisper segments to diarization; placeholders for unknowns; optionally extract 5–10 s samples per speaker; if `--no-fingerprint`, skip sample extraction.
5. **Post-process** – Merge chunks; resolve overlaps; format transcript (e.g. timestamped lines with speaker prefix); export JSON/text and optional samples directory.

## Config and flags

- **English-only** – Enforce in Whisper.
- **--no-fingerprint** – No sample extraction; keep placeholders only.
- **Tunables** – Chunk size, overlap, max speakers (MSDD can stay dynamic).

## Performance (M2)

- Whisper large-v3: ~1× real-time; “turbo” or faster-whisper for speed.
- NeMo MSDD: often 2–3× real-time (CPU/MPS fallback).
- Tune on varied audio (accents, noise).

## References

See [original-research/pipeline.txt](../original-research/pipeline.txt) for citations and implementation detail.
