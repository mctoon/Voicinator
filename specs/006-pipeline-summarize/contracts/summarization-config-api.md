# Contract: Summarization config API (006)

Config for summarization is done in the web UI and stored in `voicinator.toml`. This contract defines the API for reading and writing LLM definitions and summarization parts. Base URL prefix: `/api/pipeline` (or as mounted in Flask).

---

## GET /api/pipeline/config (extended for 006)

Existing pipeline config (base paths, step folders, chunk duration, etc.) is unchanged. Response is extended with:

- **llms**: array of LLM definitions (order = display order in UI).
- **summarizations**: array of summarization parts (order = order in output file; UI uses this order and provides up/down reorder).

**Response** (200): JSON (existing fields plus):

```json
{
  "basePaths": ["/path/to/base1"],
  "stepFolders": ["Videos 1 to be transcribed", ...],
  "unknownSpeakersStepName": "Videos 5 needs speaker identification",
  "finalFolderName": "Videos",
  "chunkDurationSeconds": 30,
  "chunkDurationDefaulted": false,
  "llms": [
    {
      "name": "local",
      "type": "ollama",
      "baseUrl": "http://localhost:11434"
    },
    {
      "name": "cloud",
      "type": "remote",
      "baseUrl": "https://api.example.com/v1",
      "apiKey": "sk-..."
    }
  ],
  "summarizations": [
    {
      "name": "Clickbait-style title",
      "llm": "local",
      "instructions": "A single line, highly clickbait-style title with emojis and hashtags; maximum clickbait."
    },
    {
      "name": "One-sentence summary",
      "llm": "local",
      "instructions": "A single sentence summarizing the entire transcript; not clickbait, as useful as possible in one sentence."
    }
  ]
}
```

| Field (new) | Type | Description |
|-------------|------|-------------|
| `llms` | array | List of LLM definitions. Each object: `name` (string), `type` ("ollama" \| "remote"), `baseUrl` (string, optional for ollama), `apiKey` (string, optional), `model` (string, optional). |
| `summarizations` | array | List of summarization parts. Each object: `name` (string), `llm` (string, references `llms[].name`), `instructions` (string). Order of array = order in generated summary file. |

**Validation**: Backend may omit or mask `apiKey` in GET response for security (e.g. return `"apiKey": true` or omit); UI sends full value on PUT only.

---

## PUT /api/pipeline/summarization-config

Writes LLM definitions and summarization parts to `voicinator.toml`. Other sections (e.g. `[server]`, `[inbox]`, `pipeline.chunkDurationSeconds`) are preserved; only `llms` and `pipeline.summarizations` are updated.

**Body**: JSON

```json
{
  "llms": [
    { "name": "local", "type": "ollama", "baseUrl": "http://localhost:11434" },
    { "name": "cloud", "type": "remote", "baseUrl": "https://api.example.com/v1", "apiKey": "sk-..." }
  ],
  "summarizations": [
    { "name": "Clickbait-style title", "llm": "local", "instructions": "..." },
    { "name": "One-sentence summary", "llm": "local", "instructions": "..." }
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `llms` | array | yes | Full list of LLM definitions; replaces existing `[[llms]]` in config. |
| `summarizations` | array | yes | Full list of summarization parts; replaces existing pipeline summarizations. Order of array = order in file and in UI. |

**Validation**:
- Each LLM: `name` non-empty, unique; `type` one of `ollama`, `remote`; `baseUrl` required for `remote`.
- Each summarization: `name` non-empty; `llm` must match an LLM `name` in the same request; `instructions` present (may be empty string; behavior when empty is implementation-defined).

**Response** (200): JSON `{ "ok": true }` or same shape as GET /api/pipeline/config.

**Errors** (400): Invalid body or validation failure (e.g. duplicate LLM name, unknown `llm` reference). Response body: `{ "error": "description" }`.

**Errors** (500): File write failure (e.g. permissions, disk full).

---

## UI behavior (informative)

- **LLMs**: Listed in config order; each has short name, type, base URL (and API key for remote). UI allows add/edit/delete; reorder optional.
- **Summarizations**: Listed in order; each has name, LLM dropdown (from `llms`), instructions text. **Up/down buttons** change order; order is persisted on save and matches order in the generated summary file.
- **Persistence**: On save, UI sends full `llms` and `summarizations` to PUT /api/pipeline/summarization-config; backend writes to `voicinator.toml`.
