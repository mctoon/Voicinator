# Python 3.x
"""
Load master config (voicinator.toml) at repo base: server.port, optional inbox.configPath.
Pipeline chunk duration (chunkDurationSeconds): 10–120 s, default 30.
"""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


DEFAULT_PORT = 8027

# Chunk duration for splitting long audio (seconds). Range 10–120; default 30. See data-model.md.
CHUNK_DURATION_MIN = 10
CHUNK_DURATION_MAX = 120
CHUNK_DURATION_DEFAULT = 30


def getMasterConfigPath() -> Path:
    """Path to master config: repo root voicinator.toml (backend/src/models -> 3 levels up = repo root)."""
    try:
        root = Path(__file__).resolve().parents[3]
        return root / "voicinator.toml"
    except Exception:
        return Path.cwd() / "voicinator.toml"


def loadMasterConfig() -> dict:
    """
    Load voicinator.toml. Returns dict with server.port (int) and optional inbox.configPath (str).
    Missing file or keys use defaults: port 8027, no inbox path override.
    """
    path = getMasterConfigPath()
    result = {"server": {"port": DEFAULT_PORT}, "inbox": {}}
    if not path.exists():
        return result
    raw = path.read_text(encoding="utf-8")
    try:
        import tomllib
        data = tomllib.loads(raw)
    except ImportError:
        import tomli
        data = tomli.loads(raw)
    if not isinstance(data, dict):
        return result
    server = data.get("server")
    if isinstance(server, dict):
        if "port" in server:
            try:
                result["server"]["port"] = int(server["port"])
            except (TypeError, ValueError):
                pass
        if server.get("logPath"):
            result["server"]["logPath"] = str(server["logPath"]).strip()
    inbox = data.get("inbox")
    if isinstance(inbox, dict) and inbox.get("configPath"):
        result["inbox"]["configPath"] = str(inbox["configPath"]).strip()
    result["llms"] = _normalizeLlmsList(data.get("llms"))
    pipeline = data.get("pipeline")
    result["pipeline"] = {
        "basePaths": [],
        "unknownSpeakersStepName": None,
        "scanIntervalSeconds": 60,
        "autoProcessingEnabled": True,
        "chunkDurationSeconds": CHUNK_DURATION_DEFAULT,
        "chunkDurationDefaulted": True,
        "summarizations": _normalizeSummarizationsList(pipeline.get("summarizations") if isinstance(pipeline, dict) else None),
    }
    if isinstance(pipeline, dict):
        if "basePaths" in pipeline and isinstance(pipeline["basePaths"], list):
            result["pipeline"]["basePaths"] = [str(p).strip() for p in pipeline["basePaths"] if str(p).strip()]
        if pipeline.get("unknownSpeakersStepName"):
            result["pipeline"]["unknownSpeakersStepName"] = str(pipeline["unknownSpeakersStepName"]).strip()
        if "scanIntervalSeconds" in pipeline:
            try:
                result["pipeline"]["scanIntervalSeconds"] = int(pipeline["scanIntervalSeconds"])
            except (TypeError, ValueError):
                pass
        if "autoProcessingEnabled" in pipeline:
            result["pipeline"]["autoProcessingEnabled"] = bool(pipeline["autoProcessingEnabled"])
        # Chunk duration: 10–120 s, default 30. Invalid/missing → default + defaulted=True + log warning.
        raw_chunk = pipeline.get("chunkDurationSeconds")
        try:
            iVal = int(raw_chunk) if raw_chunk is not None else None
        except (TypeError, ValueError):
            iVal = None
        if iVal is not None and CHUNK_DURATION_MIN <= iVal <= CHUNK_DURATION_MAX:
            result["pipeline"]["chunkDurationSeconds"] = iVal
            result["pipeline"]["chunkDurationDefaulted"] = False
        else:
            if raw_chunk is not None:
                logger.warning(
                    "pipeline.chunkDurationSeconds invalid or out of range (min=%s, max=%s): %s; using default %s",
                    CHUNK_DURATION_MIN,
                    CHUNK_DURATION_MAX,
                    raw_chunk,
                    CHUNK_DURATION_DEFAULT,
                )
            result["pipeline"]["chunkDurationSeconds"] = CHUNK_DURATION_DEFAULT
            result["pipeline"]["chunkDurationDefaulted"] = True
    return result


def getServerPort() -> int:
    """Server port from master config or default."""
    cfg = loadMasterConfig()
    return cfg.get("server", {}).get("port", DEFAULT_PORT)


def getInboxConfigPathOverride() -> str | None:
    """Inbox config path from master config if set; otherwise None."""
    cfg = loadMasterConfig()
    return cfg.get("inbox", {}).get("configPath")


def getPipelineBasePaths() -> list[str]:
    """Pipeline base paths from master config [pipeline] basePaths. May be empty (then use inbox tab paths)."""
    cfg = loadMasterConfig()
    return list(cfg.get("pipeline", {}).get("basePaths", []))


def getPipelineUnknownSpeakersStepOverride() -> str | None:
    """Override for unknown-speakers step folder name from master config, or None."""
    cfg = loadMasterConfig()
    return cfg.get("pipeline", {}).get("unknownSpeakersStepName")


def getPipelineScanIntervalSeconds() -> int:
    """Seconds between discovery scans (default 60)."""
    cfg = loadMasterConfig()
    return cfg.get("pipeline", {}).get("scanIntervalSeconds", 60)


def getPipelineAutoProcessingEnabled() -> bool:
    """Whether automatic pipeline processing is enabled (default True for 013)."""
    cfg = loadMasterConfig()
    return cfg.get("pipeline", {}).get("autoProcessingEnabled", True)


def getPipelineChunkDurationSeconds() -> int:
    """Effective chunk duration in seconds (10–120). Default 30 when missing or invalid."""
    cfg = loadMasterConfig()
    return cfg.get("pipeline", {}).get("chunkDurationSeconds", CHUNK_DURATION_DEFAULT)


def getPipelineChunkDurationDefaulted() -> bool:
    """True if config was missing or invalid and default 30 was used."""
    cfg = loadMasterConfig()
    return cfg.get("pipeline", {}).get("chunkDurationDefaulted", True)


def getLogPath() -> Path:
    """Log file path from master config [server] logPath or default repo_root/logs/voicinator.log."""
    cfg = loadMasterConfig()
    sPath = (cfg.get("server") or {}).get("logPath", "").strip()
    if sPath:
        return Path(sPath)
    try:
        root = Path(__file__).resolve().parents[3]
        return root / "logs" / "voicinator.log"
    except Exception:
        return Path.cwd() / "logs" / "voicinator.log"


def _normalizeLlmsList(raw: list | None) -> list[dict]:
    """Return list of LLM dicts (name, type, baseUrl or provider, apiKey?, model?) from [[llms]]."""
    if not isinstance(raw, list):
        return []
    out: list[dict] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        sName = (item.get("name") or "").strip()
        sType = (item.get("type") or "").strip().lower()
        if not sName or sType not in ("ollama", "remote"):
            continue
        entry: dict = {"name": sName, "type": sType}
        if item.get("baseUrl") is not None:
            entry["baseUrl"] = str(item["baseUrl"]).strip()
        elif sType == "ollama":
            entry["baseUrl"] = "http://localhost:11434"
        if item.get("provider") is not None:
            entry["provider"] = str(item["provider"]).strip()
        if item.get("apiKey") is not None:
            entry["apiKey"] = str(item["apiKey"]).strip()
        if item.get("model") is not None:
            entry["model"] = str(item["model"]).strip()
        out.append(entry)
    return out


def _normalizeSummarizationsList(raw: list | None) -> list[dict]:
    """Return list of summarization part dicts (name, llm, systemPrompt, userPrompt) from pipeline.summarizations.
    Legacy: if systemPrompt/userPrompt missing but instructions present, userPrompt = instructions + newline + {{TRANSCRIPT}}.
    """
    if not isinstance(raw, list):
        return []
    out: list[dict] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        sName = (item.get("name") or "").strip()
        sLlm = (item.get("llm") or "").strip()
        if not sName or not sLlm:
            continue
        sSystem = (item.get("systemPrompt") or "").strip()
        sUser = (item.get("userPrompt") or "").strip()
        sInstructions = (item.get("instructions") or "").strip()
        if not sSystem and not sUser and sInstructions:
            sUser = sInstructions + "\n\n{{TRANSCRIPT}}"
        out.append({"name": sName, "llm": sLlm, "systemPrompt": sSystem, "userPrompt": sUser})
    return out


def getLlms() -> list[dict]:
    """LLM definitions from voicinator.toml [[llms]]. Order = display order. Returns one default (Ollama local) when none configured."""
    cfg = loadMasterConfig()
    llms = list(cfg.get("llms", []))
    if llms:
        return llms
    return [{"name": "local", "type": "ollama", "baseUrl": "http://localhost:11434"}]


def getSummarizations() -> list[dict]:
    """Summarization parts from voicinator.toml pipeline.summarizations. Order = output order. Returns five defaults when none configured (per spec FR-008, SC-006)."""
    cfg = loadMasterConfig()
    parts = list(cfg.get("pipeline", {}).get("summarizations", []))
    if parts:
        return parts
    return _defaultSummarizationParts()


def _defaultSummarizationParts() -> list[dict]:
    """Five default summarization parts; each has systemPrompt and userPrompt. Use {{TRANSCRIPT}} in prompts for the transcript."""
    return [
        {"name": "Clickbait-style title", "llm": "local", "systemPrompt": "You are a concise summarizer. Output only the requested content, no preamble.", "userPrompt": "A single line, highly clickbait-style title with emojis and hashtags; maximum clickbait.\n\n{{TRANSCRIPT}}"},
        {"name": "One-sentence summary", "llm": "local", "systemPrompt": "You are a concise summarizer. Output only the requested content, no preamble.", "userPrompt": "A single sentence summarizing the entire transcript; not clickbait, as useful as possible in one sentence.\n\n{{TRANSCRIPT}}"},
        {"name": "Paragraph overview", "llm": "local", "systemPrompt": "You are a concise summarizer. Output only the requested content, no preamble.", "userPrompt": "A single paragraph overview of the transcript.\n\n{{TRANSCRIPT}}"},
        {"name": "Interesting passages", "llm": "local", "systemPrompt": "You are a concise summarizer. Output only the requested content, no preamble.", "userPrompt": "If there are interesting parts—something novel or disagreement between participants—a short summary of the conflict or highlight with start/stop timestamps. Omitted when there is nothing notable to list.\n\n{{TRANSCRIPT}}"},
        {"name": "Section summary with timestamps", "llm": "local", "systemPrompt": "You are a concise summarizer. Output only the requested content, no preamble.", "userPrompt": "A meaningful summary with timestamps for sections that stand out.\n\n{{TRANSCRIPT}}"},
    ]
