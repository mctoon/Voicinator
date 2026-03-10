# Python 3.x
"""
Per-media pipeline log in the sidecar (paired) folder. All processing events for one
media file are written to pipeline.log in that folder: run start/end, step start/end,
moves, errors. Uses timestamps (UTC ISO8601) and one line per event.
"""
from __future__ import annotations

import logging
import os
from datetime import timezone
from pathlib import Path

logger = logging.getLogger(__name__)


LOG_FILENAME = "pipeline.log"


def getMediaLogPath(sPairedFolderPath: str | None) -> Path | None:
    """
    Return path to the per-media log file in the sidecar folder.
    Returns None if sPairedFolderPath is empty. Does not create the file or directory.
    """
    if not sPairedFolderPath or not sPairedFolderPath.strip():
        return None
    return Path(sPairedFolderPath).resolve() / LOG_FILENAME


def _timestamp() -> str:
    """Current UTC time as ISO8601 with milliseconds."""
    from datetime import datetime
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _writeLine(logPath: Path, level: str, message: str) -> None:
    """Append one line to the log file; create parent dirs if needed; flush to disk."""
    logPath.parent.mkdir(parents=True, exist_ok=True)
    line = f"{_timestamp()} [{level}] {message}\n"
    with open(logPath, "a", encoding="utf-8") as f:
        f.write(line)
        f.flush()
        try:
            os.fsync(f.fileno())
        except OSError:
            pass


class MediaLog:
    """
    Writes pipeline events to pipeline.log in the sidecar (paired) folder.
    Update paired path after a move so subsequent writes go to the new location
    (the sidecar and its log file move with the media).
    """

    def __init__(self, sPairedFolderPath: str | None) -> None:
        self._sPairedFolderPath = (sPairedFolderPath or "").strip() or None

    def setPairedPath(self, sPairedFolderPath: str | None) -> None:
        """Update the sidecar path (e.g. after move to next step)."""
        self._sPairedFolderPath = (sPairedFolderPath or "").strip() or None

    def _log(self, level: str, message: str) -> None:
        logPath = getMediaLogPath(self._sPairedFolderPath)
        if logPath is None:
            return
        try:
            _writeLine(logPath, level, message)
        except OSError as e:
            logger.warning(
                "Per-media log write failed path=%s: %s",
                logPath,
                e,
                exc_info=False,
            )

    def info(self, message: str) -> None:
        self._log("INFO", message)

    def error(self, message: str) -> None:
        self._log("ERROR", message)

    def runStart(self, sMediaPath: str) -> None:
        self.info(f"Pipeline run start media={sMediaPath}")

    def _logToPath(self, logPath: Path, level: str, message: str) -> None:
        """Write one line to a specific path (used for summary when path must be explicit)."""
        if logPath is None:
            return
        try:
            _writeLine(logPath, level, message)
        except OSError as e:
            logger.warning(
                "Per-media log write failed path=%s: %s",
                logPath,
                e,
                exc_info=False,
            )

    def runComplete(self, sDestination: str, sPairedFolderPathOverride: str | None = None) -> None:
        msg = f"Pipeline run complete destination={sDestination}"
        if sPairedFolderPathOverride:
            p = getMediaLogPath(sPairedFolderPathOverride)
            if p is not None:
                self._logToPath(p, "INFO", msg)
                return
        self.info(msg)

    def runFailed(self, reason: str, sPairedFolderPathOverride: str | None = None) -> None:
        msg = f"Pipeline run failed reason={reason}"
        if sPairedFolderPathOverride:
            p = getMediaLogPath(sPairedFolderPathOverride)
            if p is not None:
                self._logToPath(p, "ERROR", msg)
                return
        self.error(msg)

    def runStoppedInStep5(self, reason: str, sPairedFolderPathOverride: str | None = None) -> None:
        msg = f"Pipeline run stopped in step 5 (unknown speakers) reason={reason}"
        if sPairedFolderPathOverride:
            p = getMediaLogPath(sPairedFolderPathOverride)
            if p is not None:
                self._logToPath(p, "INFO", msg)
                return
        self.info(msg)

    def stepStart(self, stepName: str) -> None:
        self.info(f"step_start step={stepName}")

    def stepEnd(
        self,
        stepName: str,
        success: bool,
        detail: str | None = None,
        durationSec: float | None = None,
    ) -> None:
        msg = f"step_end step={stepName} success={success}"
        if durationSec is not None:
            msg += f" duration_sec={durationSec:.2f}"
        if detail:
            msg += f" detail={detail}"
        if success:
            self.info(msg)
        else:
            self.error(msg)

    def moveResult(self, success: bool, sFromStep: str, sToStep: str, err: str | None = None) -> None:
        if success:
            self.info(f"move from={sFromStep} to={sToStep} success=true")
        else:
            self.error(f"move from={sFromStep} to={sToStep} success=false error={err or 'unknown'}")
