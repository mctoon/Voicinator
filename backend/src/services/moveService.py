# Python 3.x
"""
Atomic move of media file, sidecar (paired) folder, and sister files (same prefix) from inbox to queue.
Sister files go into the sidecar folder; sidecar is created if it does not exist. Idempotent; log each move and failure.
"""
from __future__ import annotations

import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


def _sisterFilesForPrimary(primaryPath: Path) -> list[Path]:
    """
    All files in the same directory whose name starts with the primary's stem (filename without extension).
    Excludes the primary itself and directories.
    """
    if not primaryPath.is_file():
        return []
    parent = primaryPath.parent
    stem = primaryPath.stem
    result: list[Path] = []
    for entry in parent.iterdir():
        if entry.is_file() and entry != primaryPath and entry.name.startswith(stem):
            result.append(entry)
    return result


def moveFileAndPaired(
    sFilePath: str,
    sQueuePath: str,
    sPairedFolderPath: str | None,
) -> tuple[bool, str | None]:
    """
    Move media file to queue dir; create sidecar folder (queueDir/stem) if missing; move sister files and
    source paired folder contents into sidecar. Returns (success, error_message). Idempotent when destination exists.
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

    stem = srcFile.stem
    sidecarDir = queueDir / stem
    sidecarDir.mkdir(parents=True, exist_ok=True)
    logger.info("Sidecar folder ensured: %s", str(sidecarDir))

    errorsList: list[str] = []

    pairedPath = Path(sPairedFolderPath) if sPairedFolderPath else None
    if pairedPath and pairedPath.is_dir():
        for entry in list(pairedPath.iterdir()):
            destEntry = sidecarDir / entry.name
            if destEntry.exists():
                logger.info("Move idempotent: sidecar entry exists %s", str(destEntry))
                continue
            try:
                shutil.move(str(entry), str(destEntry))
                logger.info("Moved into sidecar: %s -> %s", str(entry), str(destEntry))
            except Exception as e:
                errorsList.append(f"Paired entry {entry.name}: {e}")
                logger.exception("Move failure into sidecar: %s -> %s", str(entry), str(destEntry))
        try:
            if pairedPath.exists() and not any(pairedPath.iterdir()):
                pairedPath.rmdir()
                logger.info("Removed empty source paired folder: %s", str(pairedPath))
        except Exception as e:
            logger.warning("Could not remove source paired folder %s: %s", str(pairedPath), e)

    for sister in _sisterFilesForPrimary(srcFile):
        destSister = sidecarDir / sister.name
        if destSister.exists():
            logger.info("Move idempotent: sister destination exists %s", str(destSister))
            continue
        try:
            shutil.move(str(sister), str(destSister))
            logger.info("Moved sister file into sidecar: %s -> %s", str(sister), str(destSister))
        except Exception as e:
            errorsList.append(f"Sister {sister.name}: {e}")
            logger.exception("Move failure sister: %s -> %s", str(sister), str(destSister))

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
