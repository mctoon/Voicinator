# Python 3.x
"""
Speaker resolver interface: list speakers, match segment to speaker (or unknown),
add sample, create speaker, create placeholder. Stub implementation persists
to local JSON file until real speaker DB exists.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Storage file: resolutions (mediaId -> segmentId -> speakerId) and speakers list
_STORAGE_FILENAME = "speaker_resolutions.json"


def _getStoragePath() -> Path:
    """Path to speaker resolutions JSON (repo root / data / speaker_resolutions.json)."""
    try:
        # backend/src/services/pipeline -> repo root = parents[4]
        root = Path(__file__).resolve().parents[4]
    except Exception:
        root = Path.cwd()
    dataDir = root / "data"
    dataDir.mkdir(parents=True, exist_ok=True)
    return dataDir / _STORAGE_FILENAME


def _loadStorage() -> tuple[dict[str, dict[str, str]], list[dict]]:
    """Load resolutions map (mediaId -> {segmentId: speakerId}) and speakers list. Thread-unsafe."""
    path = _getStoragePath()
    resolutionsMap: dict[str, dict[str, str]] = {}
    speakersList: list[dict] = []
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            resolutionsMap = data.get("resolutions") or {}
            if not isinstance(resolutionsMap, dict):
                resolutionsMap = {}
            else:
                resolutionsMap = {k: dict(v) if isinstance(v, dict) else {} for k, v in resolutionsMap.items()}
            speakersList = data.get("speakers") or []
            if not isinstance(speakersList, list):
                speakersList = []
        except Exception as e:
            logger.warning("Could not load speaker storage %s: %s", path, e)
    return resolutionsMap, speakersList


def _saveStorage(resolutionsMap: dict[str, dict[str, str]], speakersList: list[dict]) -> None:
    """Save resolutions and speakers to JSON. Thread-unsafe."""
    path = _getStoragePath()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"resolutions": resolutionsMap, "speakers": speakersList}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def listSpeakers() -> list[dict]:
    """Return list of known speakers: [{\"id\": \"...\", \"name\": \"...\"}, ...]. From local storage."""
    _, speakersList = _loadStorage()
    return list(speakersList)


def matchSegment(sMediaId: str, sSegmentId: str, fStart: float, fEnd: float) -> str | None:
    """
    Match a segment to a known speaker. Returns speaker id or None (unknown).
    Looks up persisted resolutions from resolveSegment().
    """
    resolutionsMap, _ = _loadStorage()
    byMedia = resolutionsMap.get(sMediaId)
    if not byMedia:
        return None
    return byMedia.get(sSegmentId)


def addSampleToSpeaker(sSpeakerId: str, sMediaPath: str, fStart: float, fEnd: float) -> tuple[bool, str | None]:
    """Add segment audio as sample for speaker. Returns (success, error_message). Stub: (True, None)."""
    return True, None


def createSpeaker(sName: str) -> tuple[str | None, str | None]:
    """Create new speaker with display name. Returns (speaker_id, error_message). Persisted to local storage."""
    speakerId = "stub-" + sName.replace(" ", "_").replace("\t", "_")[: 64]
    _, speakersList = _loadStorage()
    if any(s.get("id") == speakerId for s in speakersList):
        return speakerId, None
    resolutionsMap, _ = _loadStorage()
    speakersList = list(speakersList)
    speakersList.append({"id": speakerId, "name": sName[: 256]})
    _saveStorage(resolutionsMap, speakersList)
    return speakerId, None


def createPlaceholder(sName: str) -> tuple[str | None, str | None]:
    """Create placeholder speaker. Returns (speaker_id, error_message). Persisted to local storage."""
    placeholderId = "stub-placeholder-" + sName.replace(" ", "_").replace("\t", "_")[: 64]
    _, speakersList = _loadStorage()
    if any(s.get("id") == placeholderId for s in speakersList):
        return placeholderId, None
    resolutionsMap, _ = _loadStorage()
    speakersList = list(speakersList)
    speakersList.append({"id": placeholderId, "name": sName[: 256]})
    _saveStorage(resolutionsMap, speakersList)
    return placeholderId, None


def resolveSegment(
    sMediaId: str,
    sSegmentId: str,
    sResolution: str,
    sSpeakerId: str | None = None,
    sName: str | None = None,
) -> tuple[bool, str | None]:
    """
    Resolve a segment: existing (speakerId), new (name), or placeholder (name).
    Persist resolution so matchSegment() returns this speaker for this segment.
    Returns (success, error_message).
    """
    if not sMediaId or not sSegmentId or not sResolution:
        return False, "mediaId, segmentId, and resolution are required"
    resolution = sResolution.strip().lower()
    speakerId: str | None = None
    if resolution == "existing":
        if not sSpeakerId or not sSpeakerId.strip():
            return False, "speakerId required for existing"
        speakerId = sSpeakerId.strip()
    elif resolution in ("new", "placeholder"):
        name = (sName or "").strip()
        if not name:
            return False, "name required for new or placeholder"
        if resolution == "new":
            sid, err = createSpeaker(name)
        else:
            sid, err = createPlaceholder(name)
        if err:
            return False, err
        speakerId = sid
    else:
        return False, "resolution must be existing, new, or placeholder"

    resolutionsMap, speakersList = _loadStorage()
    byMedia = resolutionsMap.setdefault(sMediaId, {})
    byMedia[sSegmentId] = speakerId or ""
    resolutionsMap[sMediaId] = byMedia
    _saveStorage(resolutionsMap, speakersList)
    logger.debug("Resolved segment mediaId=%s segmentId=%s -> speakerId=%s", sMediaId, sSegmentId, speakerId)
    return True, None
