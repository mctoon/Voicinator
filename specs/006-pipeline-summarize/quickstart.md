# Quickstart: Pipeline Summarize (006)

**Branch**: `006-pipeline-summarize` | **Date**: 2026-03-09

## Goal

Configure summarization in the web UI: define LLMs (Ollama or remote), define summarization parts (name, LLM, instructions), and reorder parts. Config is stored in `voicinator.toml`. The pipeline step 6 uses this config to generate a summary file in the step-6 folder (see pipeline layout in docs). To specify the summarization model: add LLMs in Summarization Config and assign one per part; that model is used when the part runs.

## Prerequisites

- Voicinator app running (e.g. `./run.sh`); Flask server and frontend available.
- For local summarization: Ollama installed and running (default `http://localhost:11434`) and a model pulled (e.g. `ollama pull llama3.2`).
- For remote: API base URL and API key for an OpenAI-compatible endpoint.

## Steps (after implementation)

1. **Open the summarization config UI**  
   Navigate to the summarization/config page in the web UI (e.g. from pipeline or settings).

2. **Define LLMs**  
   - Add an LLM: short name (e.g. "local"), type "Ollama", optional base URL (default localhost:11434).  
   - Add another: short name (e.g. "cloud"), type "Remote", base URL and API key.  
   - Save so `voicinator.toml` contains `[[llms]]` entries.

3. **Define summarization parts**  
   - Add parts with name, LLM (dropdown), and instructions (e.g. the five default sections from the spec).  
   - Use **up/down** to set order; this order is the order in the generated summary file.  
   - Save so `voicinator.toml` contains `[[pipeline.summarizations]]` (or equivalent).

4. **Run the pipeline**  
   - Ensure a file has completed through step 3 (transcript ready).  
   - Run pipeline; step 6 reads config, calls each LLM per part in order, writes one summary file into "Videos 7 summarization done".

5. **Verify**  
   - Check the step-6 folder for the media item for a summary file (e.g. `summary.txt`).  
   - Confirm content matches configured parts and order.

## Config file (voicinator.toml)

Example additions:

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

[[pipeline.summarizations]]
name = "Clickbait-style title"
llm = "local"
instructions = "A single line, highly clickbait-style title with emojis and hashtags."

[[pipeline.summarizations]]
name = "One-sentence summary"
llm = "local"
instructions = "A single sentence summarizing the entire transcript."
```

## API (reference)

- **GET /api/pipeline/config** — returns pipeline config including `llms` and `summarizations` (for UI).
- **PUT /api/pipeline/summarization-config** — body `{ "llms": [...], "summarizations": [...] }`; writes to `voicinator.toml`.

See `contracts/summarization-config-api.md` for full request/response and validation.
