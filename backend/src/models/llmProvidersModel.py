# Python 3.x
"""
Load llm_providers.toml at repo root: list of { name, baseUrl } for remote LLM providers.
"""
from __future__ import annotations

from pathlib import Path

from backend.src.models.masterConfigModel import getMasterConfigPath


def getLlmProvidersPath() -> Path:
    """Path to llm_providers.toml (repo root, next to voicinator.toml)."""
    return getMasterConfigPath().parent / "llm_providers.toml"


def loadLlmProviders() -> list[dict]:
    """
    Load llm_providers.toml. Returns list of { "name": str, "baseUrl": str }.
    Missing file or invalid content returns empty list.
    """
    path = getLlmProvidersPath()
    if not path.exists():
        return []
    raw = path.read_text(encoding="utf-8")
    try:
        import tomllib
        data = tomllib.loads(raw)
    except ImportError:
        import tomli
        data = tomli.loads(raw)
    except Exception:
        return []
    if not isinstance(data, dict):
        return []
    raw_list = data.get("providers")
    if not isinstance(raw_list, list):
        return []
    out: list[dict] = []
    for item in raw_list:
        if not isinstance(item, dict):
            continue
        name = (item.get("name") or "").strip()
        baseUrl = (item.get("baseUrl") or "").strip()
        if name and baseUrl:
            out.append({"name": name, "baseUrl": baseUrl})
    return out


def getProviderBaseUrl(providerName: str) -> str | None:
    """Return baseUrl for the given provider name, or None if not found."""
    for p in loadLlmProviders():
        if (p.get("name") or "").strip() == providerName.strip():
            return (p.get("baseUrl") or "").strip()
    return None
