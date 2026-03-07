# Python 3.x
"""
Atomic move (or copy-then-delete) of media file and paired folder from inbox to queue;
idempotent when destination exists or source missing; log each move and each failure.
"""
from __future__ import annotations

import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


def moveFileAndPaired(
    sFilePath: str,
    sQueuePath: str,
    sPairedFolderPath: str | None,
) -> tuple[bool, str | None]:
    """
    Move media file and optional paired folder to queue path. Returns (success, error_message).
    Idempotent: if destination already exists or source missing, treat as success.
    """
    srcFile = Path(sFilePath)
    if not srcFile.exists():
        logger.info("Move idempotent: source missing %s", sFilePath)
        return True, None

    queueDir = Path(sQueuePath)
    queueDir.mkdir(parents=True, exist_ok=True)
    destFile = queueDir / srcFile.name
    if destFile.exists():
        logger.info("Move idempotent: destination exists %s", str(destFile))
        return True, None

    errorsList: list[str] = []
    pairedPath = Path(sPairedFolderPath) if sPairedFolderPath else None
    if pairedPath and pairedPath.is_dir():
        destPaired = queueDir / pairedPath.name
        if not destPaired.exists():
            try:
                shutil.move(str(pairedPath), str(destPaired))
                logger.info("Moved paired folder: %s -> %s", str(pairedPath), str(destPaired))
            except Exception as e:
                errorsList.append(f"Paired folder: {e}")
                logger.exception("Move failure paired folder: %s -> %s", str(pairedPath), str(destPaired))

    try:
        shutil.move(str(srcFile), str(destFile))
        logger.info("Moved file: %s -> %s", sFilePath, str(destFile))
    except Exception as e:
        errorsList.append(f"File: {e}")
        logger.exception("Move failure: %s -> %s", sFilePath, str(destFile))
        return False, "; ".join(errorsList)

    if errorsList:
        return False, "; ".join(errorsList)
    return True, None


def moveBatch(
    fileItemsList: list[dict],
    sQueuePath: str,
) -> tuple[int, list[str]]:
    """
    Move a batch of media files (each with filePath, pairedFolderPath) to sQueuePath.
    Returns (movedCount, errorsList).
    """
    iMoved = 0
    errorsList: list[str] = []
    for item in fileItemsList:
        sPath = item.get("filePath") or item.get("sFilePath")
        sPaired = item.get("pairedFolderPath") or item.get("sPairedFolderPath")
        if not sPath:
            continue
        ok, err = moveFileAndPaired(sPath, sQueuePath, sPaired)
        if ok:
            iMoved += 1
        elif err:
            errorsList.append(err)
    return iMoved, errorsList
