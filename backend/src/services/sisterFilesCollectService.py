# Python 3.x
"""
Collect sister files (same base name as media, different extension) from the queue folder
into the paired folder. Primary media file stays in place. No empty paired folder created.
Per spec 003-sister-files-into-folder.
"""
from __future__ import annotations

import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


def _sisterFilesInDir(primaryPath: Path) -> list[Path]:
    """
    Files in the same directory as primary with the same stem (base name), excluding the primary.
    """
    if not primaryPath.is_file():
        return []
    parent = primaryPath.parent
    stem = primaryPath.stem
    result: list[Path] = []
    for entry in parent.iterdir():
        if entry.is_file() and entry != primaryPath and entry.stem == stem:
            result.append(entry)
    return result


def collectSisterFilesIntoPairedFolder(sMediaPath: str) -> tuple[bool, str | None]:
    """
    For a media file in the queue folder (e.g. step 1), move all sister files (same stem,
    same directory) into the paired folder (same stem as directory name). Primary media
    file is not moved. Paired folder is created only when there is at least one sister
    file to move. On name collision (file already in paired folder), keep existing (do not
    overwrite). Returns (success, error_message).
    """
    mediaPath = Path(sMediaPath)
    if not mediaPath.is_file():
        return True, None  # Idempotent: no media file, nothing to do

    sistersList = _sisterFilesInDir(mediaPath)
    if not sistersList:
        return True, None  # No sisters; do not create empty paired folder (FR-004)

    pairedDir = mediaPath.parent / mediaPath.stem
    pairedDir.mkdir(parents=True, exist_ok=True)
    errorsList: list[str] = []

    for sister in sistersList:
        destPath = pairedDir / sister.name
        if destPath.exists():
            logger.info("Keep existing in paired folder: %s", str(destPath))
            continue
        try:
            shutil.move(str(sister), str(destPath))
            logger.info("Moved sister into paired folder: %s -> %s", str(sister), str(destPath))
        except OSError as e:
            errorsList.append(f"{sister.name}: {e}")
            logger.warning("Could not move sister %s: %s", str(sister), e)
        except Exception as e:
            errorsList.append(f"{sister.name}: {e}")
            logger.exception("Move failure sister: %s -> %s", str(sister), str(destPath))

    if errorsList:
        return False, "; ".join(errorsList)
    return True, None
