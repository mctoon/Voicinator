# Python 3.x
"""
Step 5: Speaker identification. Read segments from paired folder; call speaker resolver;
if any segment is unknown, leave file in step 5 (unknown-speakers folder); else move to step 6.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from backend.src.services.pipeline.speakerResolver import matchSegment

logger = logging.getLogger(__name__)

SEGMENTS_JSON_FILENAME = "segments.json"


def _loadSegments(sPairedFolderPath: str | None) -> list[dict]:
    """Load segments from paired folder segments.json. Returns list of segment dicts."""
    if not sPairedFolderPath:
        return []
    p = Path(sPairedFolderPath) / SEGMENTS_JSON_FILENAME
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data.get("segments", [])
    except Exception:
        return []


def _mediaIdFromMediaPath(sMediaPath: str) -> str:
    """Stable mediaId for resolver (channelName|stem) to match API and discovery."""
    p = Path(sMediaPath)
    if not p.parent or not p.parent.parent:
        return p.stem
    channelName = p.parent.parent.name
    return f"{channelName}|{p.stem}"


def hasAnyUnknownSpeaker(sMediaPath: str, sPairedFolderPath: str | None) -> tuple[bool, str | None]:
    """
    Return True if any segment is unresolved (unknown). Uses speaker resolver to match each segment.
    Returns (has_unknown, error_message). mediaId format: channelName|stem (matches API).
    """
    segments = _loadSegments(sPairedFolderPath)
    if not segments:
        return False, None  # No segments -> no unknown
    mediaId = _mediaIdFromMediaPath(sMediaPath)
    for seg in segments:
        segId = seg.get("segmentId", "")
        start = float(seg.get("start", 0))
        end = float(seg.get("end", 0))
        speakerId = matchSegment(mediaId, segId, start, end)
        if speakerId is None:
            return True, None  # At least one unknown
    return False, None


def processStep5(sMediaPath: str, sPairedFolderPath: str | None) -> tuple[bool, str | None]:
    """
    Run step 5: speaker identification. If any unknown speaker, do not move (caller leaves in step 5).
    This processor only reports; orchestration decides move. Returns (success, error_message).
    Success means "step completed"; hasAnyUnknownSpeaker tells orchestration whether to move to 6 or stay in 5.
    """
    if not sMediaPath or not Path(sMediaPath).exists():
        return False, "Media path missing or does not exist"
    logger.debug("Step 5 (speaker id) checked for %s", sMediaPath)
    return True, None
