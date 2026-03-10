# Research: Pipeline Summarize (006)

**Branch**: `006-pipeline-summarize` | **Date**: 2026-03-09

## 1. LLM configuration (Ollama vs remote)

**Decision**: Support two LLM kinds in config and web UI:

- **Ollama (local)**  
  - Identified by type `ollama`.  
  - Fields: short name (required), optional base URL (default `http://localhost:11434`).  
  - No API key; Ollama is typically unauthenticated locally.

- **Remote (OpenAI-compatible)**  
  - Identified by type `remote` (or `openai_compatible`).  
  - Fields: short name (required), base URL (required, e.g. `https://api.example.com/v1`), API key (optional for some endpoints).  
  - Optional: model ID if the endpoint supports multiple models.

**Rationale**: Matches user requirement (“local ollama LLMs or remote LLMs with a URL and API key”). Ollama uses a fixed default port; remote endpoints vary and often need a key. Using a “type” + shared “short name” keeps one list of LLMs with a simple dropdown in the UI.

**Alternatives considered**: Single “endpoint + key” shape for both (Ollama with empty key). Rejected to keep “no key needed” explicit for Ollama and to allow future Ollama-specific options (e.g. model name) without overloading remote config.

---

## 2. TOML schema for LLMs and summarization parts in voicinator.toml

**Decision**: Store in `voicinator.toml`:

- **`[llms]` or `[[llms]]`**  
  Use an **array of tables** so each LLM has a clear block and order is explicit:

  ```toml
  [[llms]]
  name = "local"
  type = "ollama"
  baseUrl = "http://localhost:11434"

  [[llms]]
  name = "cloud"
  type = "remote"
  baseUrl = "https://api.openai.com/v1"
  apiKey = "sk-..."
  # optional: model = "gpt-4"
  ```

- **Summarization parts**  
  Store under pipeline as an **array of tables** so order is preserved and matches UI order (and up/down reorder):

  ```toml
  [pipeline]
  chunkDurationSeconds = 20
  # ... existing keys ...

  [[pipeline.summarizations]]
  name = "Clickbait-style title"
  llm = "local"
  instructions = "A single line, highly clickbait-style title with emojis and hashtags; maximum clickbait."

  [[pipeline.summarizations]]
  name = "One-sentence summary"
  llm = "local"
  instructions = "A single sentence summarizing the entire transcript; not clickbait, as useful as possible in one sentence."
  ```

**Rationale**: TOML array-of-tables preserves order and is easy to read. “Order in UI = order in file” is satisfied by writing the list in display order. Reference by `llm` short name keeps summarization config independent of LLM implementation details.

**Alternatives considered**: Inline tables or a single table with numeric keys (e.g. `summarization_1`). Rejected in favor of array-of-tables for clarity and to avoid key ordering issues.

---

## 3. Writing voicinator.toml from the web UI (Python)

**Decision**: Use **tomli_w** to write the full config after merging in-memory changes. Read with **tomllib** (or **tomli** on older Python); merge new or updated `llms` and `pipeline.summarizations`; write with **tomli_w.dump()** to a temp file then rename to `voicinator.toml` for atomicity.

**Rationale**: Project already uses tomllib/tomli for reading. tomli_w is the standard write counterpart, supports round-trip of structure, and keeps the implementation simple. Atomic write (temp + rename) avoids corruption if the process is interrupted.

**Alternatives considered**: tomlkit for comment-preserving edits. Rejected for initial implementation to avoid extra dependency and to keep the write path simple; we can switch if we need to preserve existing comments in edited sections.

**Caveat**: Writing the whole file with tomli_w will not preserve comments or key order in sections we don’t explicitly represent; only structure is round-tripped. Acceptable for a single master config file that the app owns.
