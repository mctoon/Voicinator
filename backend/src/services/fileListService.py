# Python 3.x
"""
List media files in a channel inbox path; resolve paired folder (same base name);
support pagination (limit/offset).
"""
from __future__ import annotations

from pathlib import Path

# Common media extensions
MEDIA_EXTENSIONS = {".mp4", ".mkv", ".webm", ".mov", ".avi", ".m4a", ".mp3", ".wav", ".flac", ".ogg"}


def listMediaFiles(sInboxPath: str, iLimit: int = 100, iOffset: int = 0) -> tuple[list[dict], int]:
    """
    List media files in inbox path. Each item has filePath, displayName, pairedFolderPath (optional).
    Returns (sliced list, total count).
    """
    inbox = Path(sInboxPath)
    if not inbox.is_dir():
        return [], 0

    filesList: list[dict] = []
    for entry in sorted(inbox.iterdir(), key=lambda e: e.name.lower()):
        if entry.is_file() and entry.suffix.lower() in MEDIA_EXTENSIONS:
            sFilePath = str(entry.resolve())
            sDisplayName = entry.name
            paired = _resolvePairedFolder(entry)
            filesList.append({
                "filePath": sFilePath,
                "displayName": sDisplayName,
                "pairedFolderPath": str(paired) if paired else None,
                "durationSeconds": None,
            })
        elif entry.is_dir():
            continue

    iTotal = len(filesList)
    sliceList = filesList[iOffset : iOffset + iLimit]
    return sliceList, iTotal


def _resolvePairedFolder(filePath: Path) -> Path | None:
    """Return folder with same base name as file if it exists."""
    stem = filePath.stem
    parent = filePath.parent
    paired = parent / stem
    return paired if paired.is_dir() else None
