# Data Model: Pipeline Summarize (006)

**Branch**: `006-pipeline-summarize` | **Date**: 2026-03-09

Config is stored in `voicinator.toml`. No database; filesystem only.

---

## Entities

### LLM (definition)

Represents a single LLM that can be selected for summarization.

| Field     | Type   | Required | Description |
|----------|--------|----------|-------------|
| name     | string | yes      | Short name (unique); used in UI dropdown and in summarization `llm` reference. |
| type     | string | yes      | `ollama` or `remote`. |
| baseUrl  | string | conditional | For `ollama`: optional (default `http://localhost:11434`). For `remote`: required (e.g. `https://api.example.com/v1`). |
| apiKey   | string | no       | For `remote` only; optional if endpoint does not require auth. |
| model    | string | no       | Optional model ID for endpoints that support multiple models. |

**Validation**:
- `name`: non-empty, unique among LLMs.
- `type`: exactly `ollama` or `remote`.
- `baseUrl`: when present, must be a valid URL; for `remote`, required.
- No relationship to other entities except by reference from SummarizationPart.

**Storage**: TOML array-of-tables `[[llms]]` in `voicinator.toml`. Order is display order in UI (e.g. for dropdown).

---

### SummarizationPart (one section of the summary)

One named section of the summary with its own LLM and instructions. Order in list = order in the generated summary file.

| Field       | Type   | Required | Description |
|------------|--------|----------|-------------|
| name       | string | yes      | Display name of this summarization (e.g. "Clickbait-style title"). |
| llm        | string | yes      | Short name of an LLM (must match an LLM in the `llms` list). |
| instructions | string | yes    | Instructions/prompt text sent to the LLM for this part. |

**Validation**:
- `name`: non-empty.
- `llm`: must reference an existing LLM by short name.
- `instructions`: non-empty recommended; empty may be allowed (behavior documented: skip part or use default).

**Storage**: TOML array-of-tables `[[pipeline.summarizations]]` in `voicinator.toml`. Array order = output order; UI up/down reorder updates this order.

**State**: No state machine; parts are static config. Pipeline step 6 reads the current list and runs each part in order.

---

## Config file layout (voicinator.toml)

- **Existing sections**: `[server]`, `[inbox]`, `[pipeline]` (existing keys such as `chunkDurationSeconds`, `basePaths`, etc.) unchanged.
- **New**: Top-level `[[llms]]` (array of LLM definitions).
- **New**: Under `[pipeline]`, `[[pipeline.summarizations]]` or equivalent array-of-tables for summarization parts (syntax may be `[[pipeline.summarizations]]` if supported, or a separate table array keyed by pipeline; see TOML spec for nested array-of-tables). If the TOML implementation does not support nested array-of-tables, use a single key such as `summarizations = [ { name = "...", llm = "...", instructions = "..." }, ... ]` (array of inline tables) to preserve order.

**Note**: TOML 1.0 allows `[[pipeline.summarizations]]` for array of tables under a parent table; verify with tomllib/tomli and tomli_w. If not supported, use `pipeline.summarizations` as an array of inline tables.

---

## Pipeline step 6 (summary output)

- **Input**: Completed transcript (from step 3) for the current media item; path to paired folder for step 6 ("Videos 7 summarization done").
- **Output**: One summary file (e.g. `summary.txt` or `summary.md`) in the step-6 folder for that item. Content = concatenation of each summarization part’s result, in config order.
- **Process**: For each part in `pipeline.summarizations` (in order): resolve `llm` to an LLM definition, call that LLM with `instructions` and the transcript (or relevant segment), append result to the summary. Empty or zero parts → skip step or write minimal/placeholder; behavior documented.

No separate entity for “run state”; step 6 is stateless per run and reads config at runtime.
