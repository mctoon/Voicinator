# Python 3.x
"""
Configure logging to write to a log file and to console. Call from __main__ before starting the app.
"""
from __future__ import annotations

import logging
import sys

from backend.src.models.masterConfigModel import getLogPath


def configureLogging() -> str:
    """
    Configure root logger: log file (repo logs/voicinator.log or server.logPath) and console. Returns path to log file.
    """
    logPath = getLogPath().resolve()
    logPath.parent.mkdir(parents=True, exist_ok=True)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    fh = logging.FileHandler(logPath, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)
    root.addHandler(fh)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    root.addHandler(ch)
    root.info("Logging to file: %s", str(logPath))
    return str(logPath)
