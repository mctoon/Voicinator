# Python 3.x
"""
MediaFile DTO (dict shape) matching contract: filePath, displayName, pairedFolderPath, durationSeconds.
"""
from __future__ import annotations


def mediaFileToDict(sFilePath: str, sDisplayName: str, sPairedFolderPath: str | None = None,
                    iDurationSeconds: int | None = None) -> dict:
    """Build media file dict for API response per contracts/inbox-queue-api.md."""
    return {
        "filePath": sFilePath,
        "displayName": sDisplayName,
        "pairedFolderPath": sPairedFolderPath,
        "durationSeconds": iDurationSeconds,
    }
