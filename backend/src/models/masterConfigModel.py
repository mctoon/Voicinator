# Python 3.x
"""
Load master config (voicinator.toml) at repo base: server.port, optional inbox.configPath.
"""
from __future__ import annotations

from pathlib import Path


DEFAULT_PORT = 8027


def getMasterConfigPath() -> Path:
    """Path to master config: repo root voicinator.toml."""
    try:
        root = Path(__file__).resolve().parents[4]
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
    if isinstance(server, dict) and "port" in server:
        try:
            result["server"]["port"] = int(server["port"])
        except (TypeError, ValueError):
            pass
    inbox = data.get("inbox")
    if isinstance(inbox, dict) and inbox.get("configPath"):
        result["inbox"]["configPath"] = str(inbox["configPath"]).strip()
    return result


def getServerPort() -> int:
    """Server port from master config or default."""
    cfg = loadMasterConfig()
    return cfg.get("server", {}).get("port", DEFAULT_PORT)


def getInboxConfigPathOverride() -> str | None:
    """Inbox config path from master config if set; otherwise None."""
    cfg = loadMasterConfig()
    return cfg.get("inbox", {}).get("configPath")
