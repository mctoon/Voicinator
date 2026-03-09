# Python 3.x
"""
Configure logging to write to a log file and to console. Call from __main__ before starting the app.
Uncaught exceptions (main thread and threads) are logged to the log file.
stderr is teed to the log file so third-party output (e.g. NeMo, werkzeug) is captured.
"""
from __future__ import annotations

import logging
import sys
import threading
import traceback
from pathlib import Path

from backend.src.models.masterConfigModel import getLogPath


class _StderrTee:
    """Write to both original stderr and the log file so console-only output is captured."""

    def __init__(self, original: object, logPath: str | Path) -> None:
        self._original = original
        self._file = open(logPath, "a", encoding="utf-8")

    def write(self, s: str) -> int:
        n = 0
        if s:
            self._original.write(s)
            try:
                self._file.write(s)
                self._file.flush()
            except OSError:
                pass
            n = len(s)
        return n

    def flush(self) -> None:
        self._original.flush()
        try:
            self._file.flush()
        except OSError:
            pass

    def writable(self) -> bool:
        return True

    def isatty(self) -> bool:
        return getattr(self._original, "isatty", lambda: False)()


def _logUncaught(excType: type[BaseException], excValue: BaseException, excTb: object) -> None:
    """Excepthook: log uncaught exception to file and console, then run default hook."""
    root = logging.getLogger()
    if root.handlers:
        root.critical(
            "Uncaught exception: %s\n%s",
            excValue,
            "".join(traceback.format_exception(excType, excValue, excTb)),
            exc_info=False,
        )
    sys.__excepthook__(excType, excValue, excTb)


def _threadExcepthook(args: threading.ExceptHookArgs) -> None:
    """Thread excepthook (Python 3.8+): log uncaught thread exception to file."""
    root = logging.getLogger()
    if root.handlers:
        root.critical(
            "Uncaught exception in thread %s: %s\n%s",
            args.thread.name if args.thread else "unknown",
            args.exc_value,
            "".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback)),
            exc_info=False,
        )


def configureLogging() -> str:
    """
    Configure root logger: log file (repo logs/voicinator.log or server.logPath) and console.
    Sets excepthook so uncaught exceptions are logged to the file. Returns path to log file.
    """
    logPath = getLogPath().resolve()
    logPath.parent.mkdir(parents=True, exist_ok=True)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    fh = logging.FileHandler(logPath, mode="w", encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)
    root.addHandler(fh)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    root.addHandler(ch)
    sys.excepthook = _logUncaught
    if hasattr(threading, "excepthook"):
        threading.excepthook = _threadExcepthook
    # Tee stderr to log file so NeMo, werkzeug, and other direct stderr output is captured
    try:
        sys.stderr = _StderrTee(sys.__stderr__, logPath)  # type: ignore[assignment]
    except OSError:
        pass
    root.info("Logging to file: %s", str(logPath))
    return str(logPath)
