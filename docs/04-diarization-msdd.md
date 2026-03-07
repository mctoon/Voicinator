# Diarization: NeMo MSDD (concise)

NeMo’s Multi-Scale Diarization Decoder (MSDD) for “who spoke when,” including overlap.

## Role of MSDD

- **Pipeline:** VAD (e.g. MarbleNet) → speaker embeddings (TitaNet) → clustering → **MSDD refinement** (multi-scale).
- **Benefits:** Fine resolution (~0.25 s); overlap handling; good DER (e.g. ~4% telephonic, ~1% meeting in benchmarks).
- **Limits:** Pairwise design (max 2 per decision, combined for more); tune for &gt;8 speakers or heavy noise.

## Setup

- Install: `nemo_toolkit[asr]`; PyTorch 2.0+ (GPU preferred; CPU/Apple Silicon slower).
- Models: e.g. `diar_msdd_telephonic` from NGC/Hugging Face.
- Data: 16 kHz mono WAV; manifest (JSON with paths/metadata) for inference.

## Configuration (YAML)

- **Sections:** diarizer (manifest, out_dir, speaker_embeddings, clustering, msdd_model), vad.
- **Embeddings:** model_path e.g. `titanet_large`; window_length_in_sec (e.g. [1.5, 1.0, 0.5]); shift_length_in_sec (e.g. half of windows); multiscale_weights.
- **Clustering:** oracle_num_speakers false; max_num_speakers (e.g. 8).
- **MSDD:** model_path e.g. `diar_msdd_telephonic`; sigmoid_threshold (e.g. [0.7, 1.0]).
- **VAD:** model_path e.g. `vad_multilingual_marblenet`; onset/offset (e.g. 0.8 / 0.6).

Load config with OmegaConf; instantiate NeuralDiarizer with that config.

## Inference

- Create manifest from audio path (filepath, offset, duration, label, num_speakers).
- Run diarizer; read RTTM from output dir (e.g. `pred_rttms/*.rttm`).
- RTTM format: SPEAKER file channel start dur NA NA spk_id NA NA.
- Parse to (speaker, start, end) segments for alignment with ASR.

## Tuning (summary)

| Area              | Parameters              | Typical use              |
|-------------------|-------------------------|--------------------------|
| Multi-scale       | window_length_in_sec    | [1.5, 1.0, 0.5]          |
|                   | shift_length_in_sec     | half of windows          |
| MSDD              | weighting_scheme        | conv_scale_weight        |
|                   | context_vector_type     | cos_sim                  |
| VAD               | onset / offset          | 0.8 / 0.6 (lower if noisy) |
| Clustering        | max_num_speakers        | 8–20 by use case         |
| Inference         | sigmoid_threshold       | [0.7, 1.0]               |

## Integration

- **Transcription app:** Diarize → transcribe (e.g. Whisper) → align segments to speakers.
- **Batch:** One audio file at a time; reuse same config and model.
- **Optimization:** emb_batch_size; multi-GPU if available; evaluate DER (e.g. pyannote.metrics).

## Troubleshooting

- High DER: adjust VAD or add scales.
- Memory: reduce scales or batch size.
- Overlaps: do not ignore overlap in scoring.

See [original-research/NeMo MSDD implementation guide.md](../original-research/NeMo%20MSDD%20implementation%20guide.md) for code snippets and citations.
