# Python 3.x
"""
Auto-run pipeline: discovery across all steps, priority selection, and background loop.
One file in progress at a time; scan interval configurable; sleep when idle.
"""
from __future__ import annotations

import logging
import threading
import time

from backend.src.models.masterConfigModel import (
    getPipelineAutoProcessingEnabled,
    getPipelineScanIntervalSeconds,
)
from backend.src.services.pipelineDiscoveryService import discoverMediaInAllSteps
from backend.src.services.pipelineRunService import runNextStepForOneFile

logger = logging.getLogger(__name__)

# One file in progress at a time (module-level lock)
_inProgressLock = threading.Lock()
_inProgress = False


def selectOneFileByPriority(candidatesList: list[dict]) -> dict | None:
    """
    Sort candidates by stepIndex descending (higher step first); return first item or None.
    candidatesList: list of dicts with at least "stepIndex" (0–7).
    """
    if not candidatesList:
        return None
    sortedList = sorted(candidatesList, key=lambda x: (-(x.get("stepIndex", 0)), x.get("mediaPath", "")))
    return sortedList[0]


def _runOneCycle() -> None:
    """One cycle: discover all steps, select one by priority, run one step for that file."""
    global _inProgress
    if not getPipelineAutoProcessingEnabled():
        return
    with _inProgressLock:
        if _inProgress:
            return
        _inProgress = True
    try:
        items = discoverMediaInAllSteps()
        chosen = selectOneFileByPriority(items)
        if not chosen:
            return
        mediaPath = chosen.get("mediaPath", "")
        pairedPath = chosen.get("pairedFolderPath")
        try:
            ok, err = runNextStepForOneFile(mediaPath, pairedPath)
            if not ok:
                logger.warning("Auto-run step failed for %s: %s", mediaPath, err)
        except Exception as e:
            logger.exception("Auto-run step error for %s: %s", mediaPath, e)
    finally:
        with _inProgressLock:
            _inProgress = False


def _loop() -> None:
    """Background loop: first scan immediately, then sleep(interval) -> cycle -> repeat."""
    interval = max(1, getPipelineScanIntervalSeconds())
    logger.info("Pipeline auto-run loop started (interval=%ds)", interval)
    # First discovery within one interval of startup (run first scan immediately)
    _runOneCycle()
    while True:
        time.sleep(interval)
        if not getPipelineAutoProcessingEnabled():
            continue
        _runOneCycle()


_thread: threading.Thread | None = None


def startAutoRunLoop() -> None:
    """Start the auto-run loop in a background daemon thread. Idempotent."""
    global _thread
    if not getPipelineAutoProcessingEnabled():
        logger.info("Pipeline auto-processing disabled; not starting loop.")
        return
    with _inProgressLock:
        if _thread is not None and _thread.is_alive():
            return
        _thread = threading.Thread(target=_loop, daemon=True, name="pipeline-auto-run")
        _thread.start()
    logger.info("Pipeline auto-run thread started.")
