# Quickstart: Configurable chunk size (005)

## What this feature does

You can set how long each audio “chunk” is (in seconds) when the pipeline processes long files for transcription. Default is 30 seconds. Changing it does not require code changes—only config.

## Config

Edit **voicinator.toml** at the repo root. Under `[pipeline]` add (or change):

```toml
[pipeline]
# ... existing keys (basePaths, scanIntervalSeconds, etc.) ...
chunkDurationSeconds = 30
```

- **Allowed range**: 10–120 (seconds).
- **Default**: If you omit `chunkDurationSeconds` or set an invalid value, the pipeline uses 30 and logs a warning.

## Example

```toml
[pipeline]
basePaths = ["/path/to/channels"]
chunkDurationSeconds = 20
```

Next pipeline run will use 20-second chunks (when explicit chunking is implemented). Until then, the value is read and exposed via the API; step 3 continues to pass full audio to faster-whisper.

## Checking the effective value

**GET /api/pipeline/config** returns `chunkDurationSeconds` and `chunkDurationDefaulted`. If `chunkDurationDefaulted` is true, the config was missing or invalid and 30 was used.

## Out of range

If you set e.g. `chunkDurationSeconds = 5` or `200`, the system will use 30 and set `chunkDurationDefaulted: true`. Check logs for the warning.
