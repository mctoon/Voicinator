# Python 3.x
"""
Write path for summarization config: merge llms and pipeline.summarizations into voicinator.toml.
Uses tomli_w; atomic write (temp file then rename).
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from backend.src.models.masterConfigModel import (
    getMasterConfigPath,
    loadMasterConfig,
)

logger = logging.getLogger(__name__)


def writeSummarizationConfig(
    llmsList: list[dict[str, Any]],
    summarizationsList: list[dict[str, Any]],
) -> None:
    """
    Merge llms and summarizations (per-part systemPrompt and userPrompt) into master config and write voicinator.toml atomically.
    Other sections (server, inbox, pipeline.basePaths, etc.) are preserved from current file.
    Raises ValueError if validation fails; OSError on write failure.
    """
    path = getMasterConfigPath()
    cfg = loadMasterConfig()
    cfg["llms"] = _llmsToTomlShape(llmsList)
    pipeline = cfg.setdefault("pipeline", {})
    pipeline["summarizations"] = _summarizationsToTomlShape(summarizationsList)
    _writeConfigAtomically(path, cfg)


def _llmsToTomlShape(llmsList: list[dict]) -> list[dict]:
    """Convert API llms list to list of dicts for TOML. Remote: name derived as provider:model if missing."""
    out: list[dict] = []
    for item in llmsList:
        if not isinstance(item, dict):
            continue
        entry: dict = {}
        sType = (str(item.get("type") or "").strip().lower())
        if sType == "remote":
            provider = str(item.get("provider") or "").strip()
            model = str(item.get("model") or "").strip()
            entry["name"] = str(item.get("name") or "").strip() or f"{provider}:{model}"
            entry["type"] = "remote"
            entry["provider"] = provider
            apiKeyVal = item.get("apiKey")
            if apiKeyVal is not None and apiKeyVal is not True and str(apiKeyVal).strip():
                entry["apiKey"] = str(apiKeyVal).strip()
            entry["model"] = model
        else:
            if item.get("name") is not None:
                entry["name"] = str(item["name"]).strip()
            if item.get("type") is not None:
                entry["type"] = str(item["type"]).strip().lower()
            if item.get("baseUrl") is not None:
                entry["baseUrl"] = str(item["baseUrl"]).strip()
            if item.get("apiKey") is not None:
                entry["apiKey"] = str(item["apiKey"]).strip()
            if item.get("model") is not None:
                entry["model"] = str(item["model"]).strip()
        if entry.get("name") and entry.get("type"):
            out.append(entry)
    return out


def _summarizationsToTomlShape(summarizationsList: list[dict]) -> list[dict]:
    """Convert API summarizations list to list of dicts for TOML. Each part has systemPrompt and userPrompt."""
    out: list[dict] = []
    for item in summarizationsList:
        if not isinstance(item, dict):
            continue
        entry = {
            "name": str(item.get("name", "")).strip(),
            "llm": str(item.get("llm", "")).strip(),
            "systemPrompt": str(item.get("systemPrompt", "")).strip(),
            "userPrompt": str(item.get("userPrompt", "")).strip(),
        }
        if entry["name"] and entry["llm"]:
            out.append(entry)
    return out


def _stripNoneFromDict(d: dict) -> dict:
    """Return a copy of d with keys whose value is None removed. One level only."""
    return {k: v for k, v in d.items() if v is not None}


def _writeConfigAtomically(path: Path, cfg: dict) -> None:
    """Serialize cfg to TOML and write to path via temp file then rename."""
    try:
        import tomli_w
    except ImportError:
        raise RuntimeError("tomli_w is required to write voicinator.toml; add tomli-w to requirements.txt") from None
    # Build TOML-friendly structure. Omit None values (tomli_w cannot serialize them).
    doc: dict[str, Any] = {}
    if "server" in cfg:
        doc["server"] = _stripNoneFromDict(cfg["server"]) if isinstance(cfg["server"], dict) else cfg["server"]
    if "inbox" in cfg:
        doc["inbox"] = _stripNoneFromDict(cfg["inbox"]) if isinstance(cfg["inbox"], dict) else cfg["inbox"]
    pipeline = cfg.get("pipeline", {})
    if pipeline is not None and isinstance(pipeline, dict):
        doc["pipeline"] = _stripNoneFromDict(pipeline)
    if "llms" in cfg:
        doc["llms"] = cfg["llms"]
    tempPath = path.with_suffix(path.suffix + ".tmp")
    try:
        with open(tempPath, "wb") as f:
            tomli_w.dump(doc, f)
    except OSError as e:
        logger.exception("Failed to write voicinator.toml.tmp: %s", e)
        raise
    try:
        tempPath.replace(path)
    except OSError as e:
        logger.exception("Failed to replace voicinator.toml: %s", e)
        tempPath.unlink(missing_ok=True)
        raise
