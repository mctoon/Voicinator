# Data Model: Configurable Chunk Size (005)

## Entities

### Pipeline config (runtime)

Pipeline configuration is read from `voicinator.toml` at repo root. This feature adds one logical field to the existing `[pipeline]` section.

| Field                     | Type   | Source                    | Validation / notes |
|---------------------------|--------|---------------------------|---------------------|
| `chunkDurationSeconds`    | int    | `[pipeline].chunkDurationSeconds` | Optional. If present: must be in [10, 120]. If missing, invalid, or out of range: use default 30 and log warning. |

No new persistent storage. Config is read at runtime when pipeline runs or when GET `/api/pipeline/config` is called.

### Validation rules

- **Range**: 10 ≤ chunkDurationSeconds ≤ 120 (inclusive).
- **Default**: 30 when key is absent, not a number, zero, negative, or out of range.
- **Type**: Integer (float from TOML truncated or rounded per implementation; recommend int in TOML).

### Key terms

- **Chunk duration**: Length in seconds of each audio segment when long audio is split for transcription. Configurable; default 30 s. Used by preprocessing/chunking logic (and in the future by explicit split/merge in step 3).
- **Configuration**: `voicinator.toml`; `[pipeline]` section. Applied at runtime; no code change required to tune.

## State

No new state machines. Pipeline step flow unchanged. Effective chunk duration is derived on each read (no caching requirement; caching is an implementation detail).

## Relationships

- **Master config**: `voicinator.toml` → `server`, `inbox`, `pipeline`. `pipeline.chunkDurationSeconds` is a sibling to `basePaths`, `scanIntervalSeconds`, `unknownSpeakersStepName`, `autoProcessingEnabled`.
- **API**: GET `/api/pipeline/config` returns effective chunk duration (and optionally whether it was defaulted) for UI/operators.
