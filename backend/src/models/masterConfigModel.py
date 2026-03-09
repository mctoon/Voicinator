# Python 3.x
"""
Load master config (voicinator.toml) at repo base: server.port, optional inbox.configPath.
"""
from __future__ import annotations

from pathlib import Path


DEFAULT_PORT = 8027


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
    pipeline = data.get("pipeline")
    result["pipeline"] = {
        "basePaths": [],
        "unknownSpeakersStepName": None,
        "scanIntervalSeconds": 60,
        "autoProcessingEnabled": True,
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
