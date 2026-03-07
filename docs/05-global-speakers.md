# Global speaker list (concise)

Central list of known speakers (voice embeddings) for consistent labels across files.

## Purpose

- Use embeddings as fingerprints; match new segments to enrolled speakers (e.g. cosine ≥ 0.7).
- Reduces DER ~10–20% when enrollment is good; use placeholders for unknowns; optional `--no-fingerprint` to skip DB and extractions.

## Principles

- **Enrollment:** 30–60 s clean, diverse audio per speaker; average multiple samples for stability; refresh over time (accent, aging).
- **Storage:** Vector DB (e.g. Qdrant or FAISS) with cosine distance; vector size = embedding dim (e.g. 192 for TitaNet); metadata (name, enrolled_at, etc.).
- **Query:** Similarity search; threshold &gt;0.7; assign name or placeholder; optional sample extraction for unknowns.

## Stack (local, Mac M2)

- **Embeddings:** NeMo TitaNet (same as diarization pipeline).
- **Vector DB:** Qdrant (e.g. `qdrant_client`); or in-process FAISS/NumPy; MPS fallback enabled.

## Creating and maintaining the list

- **Enroll:** 30–60 s mono 16 kHz per speaker; extract embeddings (TitaNet); average if multiple clips; upsert with unique ID and payload (name, date).
- **Update:** Recompute average with new samples; upsert.
- **Remove:** Delete by payload (e.g. name).
- **Maintenance:** Periodic similarity audit to merge duplicates; anonymize IDs; consent for stored data.

## Pipeline integration

1. After diarization: embeddings per segment or per cluster.
2. Query global list (e.g. search with threshold 0.7, limit 1).
3. Assign matched name or placeholder (Unknown_1, …); optionally extract samples.
4. If `--no-fingerprint`: skip query and sample extraction; keep diarization labels only.
5. For long files: process in chunks; average embeddings before query if needed.

## Best practices (summary)

| Aspect    | Tool / approach        | Note                          |
|----------|-------------------------|-------------------------------|
| Extraction | NeMo TitaNet           | 30–60 s clean; average multi  |
| Storage  | Qdrant / FAISS          | Cosine; store metadata        |
| Query    | Similarity search       | Threshold &gt;0.7; limit top   |
| Updates  | Recompute and upsert    | Quarterly or on new data      |
| Privacy  | Anonymize IDs           | Comply with data protection   |

See [original-research/global speaker handling.txt](../original-research/global%20speaker%20handling.txt) for setup and citations.
