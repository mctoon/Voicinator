# Python 3.x
"""
Move media file and paired folder from one pipeline step to the next.
Uses moveService so sidecar/sister semantics match 001.
"""
from __future__ import annotations

import logging
from pathlib import Path

from backend.src.services.moveService import moveFileAndPaired
from backend.src.models.pipelineStepPlan import (
    getNextStepFolder,
    getFinalFolderName,
    getStepFolderOrder,
)

logger = logging.getLogger(__name__)


def getChannelDirFromMediaPath(sMediaPath: str) -> Path | None:
    """Channel folder is parent of the step folder; step folder is parent of media file."""
    mediaPath = Path(sMediaPath)
    if not mediaPath.is_file():
        return None
    stepDir = mediaPath.parent
    channelDir = stepDir.parent
    return channelDir if channelDir.is_dir() else None


def getNextStepDir(sMediaPath: str, sPairedFolderPath: str | None) -> str | None:
    """
    Return the next step directory path for this media file.
    Current step = parent of media file; next step = channelDir / nextStepName.
    If current is last step (Videos 8 export ready), return channelDir / "Videos".
    """
    mediaPath = Path(sMediaPath)
    if not mediaPath.is_file():
        return None
    stepDir = mediaPath.parent
    channelDir = stepDir.parent
    currentStepName = stepDir.name
    order = getStepFolderOrder()
    if currentStepName == order[-1]:
        return str(channelDir / getFinalFolderName())
    nextName = getNextStepFolder(currentStepName)
    if not nextName:
        return None
    return str(channelDir / nextName)


def moveToNextStep(
    sMediaPath: str,
    sPairedFolderPath: str | None,
    sNextStepDir: str,
) -> tuple[bool, str | None]:
    """
    Move media file and paired folder to sNextStepDir (next step folder path).
    Returns (success, error_message). Uses moveService for sidecar/sister semantics.
    """
    return moveFileAndPaired(sMediaPath, sNextStepDir, sPairedFolderPath)
