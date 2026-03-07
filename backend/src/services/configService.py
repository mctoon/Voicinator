# Python 3.x
"""
Config service: loads and exposes tabs (and optional reload).
Inbox config path: master config [inbox].configPath override, then INBOX_CONFIG env, then default.
"""
from __future__ import annotations

import os
from pathlib import Path

from backend.src.models.configModel import loadConfigFromPath
from backend.src.models.masterConfigModel import getInboxConfigPathOverride


def getTabs(sConfigPath: str) -> list[dict]:
    """Load config from path and return list of tab dicts (tabId, tabName, pathCount, paths)."""
    return loadConfigFromPath(sConfigPath)


def getConfigPath() -> str:
    """Resolve config file path: master config override, then INBOX_CONFIG env, then default."""
    sOverride = getInboxConfigPathOverride()
    if sOverride:
        path = Path(sOverride)
        if path.is_absolute() and path.exists():
            return sOverride
        try:
            root = Path(__file__).resolve().parents[4]
            candidate = root / sOverride
            if candidate.exists():
                return str(candidate)
        except Exception:
            pass
        return str(Path.cwd() / sOverride)
    sPath = os.environ.get("INBOX_CONFIG", "").strip()
    if sPath:
        return sPath
    try:
        root = Path(__file__).resolve().parents[4]
        for name in ("inbox_queue_config.toml", "inbox_queue_config.json", "settings/inbox_queue_config.toml"):
            candidate = root / name
            if candidate.exists():
                return str(candidate)
    except Exception:
        pass
    return str(Path.cwd() / "inbox_queue_config.toml")
