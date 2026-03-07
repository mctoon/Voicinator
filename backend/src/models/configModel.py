# Python 3.x
"""
TabConfig and config file load. Reads TOML or JSON; tabs have optional name and one or two paths.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def loadConfigFromPath(sConfigPath: str) -> list[dict[str, Any]]:
    """
    Load tabs from a config file (TOML or JSON). Returns list of tab dicts.

    Each tab dict has: tabName (optional str), path (str) or paths (list of 1 or 2 str).
    """
    path = Path(sConfigPath)
    if not path.exists():
        return []

    raw = path.read_text(encoding="utf-8")
    ext = path.suffix.lower()

    if ext == ".json":
        data = json.loads(raw)
    elif ext in (".toml", ".tml"):
        data = _loadToml(raw)
    else:
        return []

    tabsList = data.get("tabs") if isinstance(data, dict) else []
    if not isinstance(tabsList, list):
        return []

    resultList = []
    for i, tab in enumerate(tabsList):
        if not isinstance(tab, dict):
            continue
        normalized = _normalizeTab(tab, i)
        if normalized:
            resultList.append(normalized)
    return resultList


def _loadToml(raw: str) -> dict[str, Any]:
    """Load TOML string; use tomllib (3.11+) or tomli."""
    try:
        import tomllib
        return tomllib.loads(raw)
    except ImportError:
        import tomli
        return tomli.loads(raw)


def _normalizeTab(tabDict: dict[str, Any], iIndex: int) -> dict[str, Any] | None:
    """
    Normalize one tab: at least one path; optional name. Two paths => source, destination.
    """
    pathsList = tabDict.get("paths") or tabDict.get("pathList")
    if not pathsList and "path" in tabDict:
        pathsList = [tabDict["path"]]
    if not pathsList or not isinstance(pathsList, list):
        return None
    pathsList = [p for p in pathsList if isinstance(p, str) and p.strip()]
    if not pathsList:
        return None
    if len(pathsList) > 2:
        pathsList = pathsList[:2]
    sTabName = (tabDict.get("tabName") or tabDict.get("sTabName") or "").strip()
    if not sTabName and pathsList:
        sTabName = f"Path {iIndex + 1}"
    return {
        "tabId": str(iIndex),
        "tabName": sTabName,
        "pathCount": len(pathsList),
        "paths": pathsList,
    }
