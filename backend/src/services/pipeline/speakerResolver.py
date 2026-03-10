# Python 3.x
"""
Speaker resolver interface: list speakers, match segment to speaker (or unknown),
add sample, create speaker, create placeholder. Stub implementation persists
to local JSON file until real speaker DB exists.
007: Placeholder without name → server generates Unidentified-<N>; full speaker record
and passage storage for corpus (008 voice library).
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Storage file: resolutions (mediaId -> segmentId -> speakerId), speakers list, placeholder counter, passages
_STORAGE_FILENAME = "speaker_resolutions.json"
_PLACEHOLDER_PREFIX = "Unidentified-"


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


def _loadStorage() -> tuple[dict[str, dict[str, str]], list[dict], int, dict[str, list[dict]]]:
    """Load resolutions, speakers list, placeholder counter, and passages. Thread-unsafe."""
    path = _getStoragePath()
    resolutionsMap: dict[str, dict[str, str]] = {}
    speakersList: list[dict] = []
    placeholderCounter = 0
    passagesMap: dict[str, list[dict]] = {}
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
            placeholderCounter = int(data.get("placeholderCounter") or 0)
            passagesMap = data.get("passages") or {}
            if not isinstance(passagesMap, dict):
                passagesMap = {}
            else:
                passagesMap = {k: list(v) if isinstance(v, list) else [] for k, v in passagesMap.items()}
        except Exception as e:
            logger.warning("Could not load speaker storage %s: %s", path, e)
    return resolutionsMap, speakersList, placeholderCounter, passagesMap


def _saveStorage(
    resolutionsMap: dict[str, dict[str, str]],
    speakersList: list[dict],
    placeholderCounter: int = 0,
    passagesMap: dict[str, list[dict]] | None = None,
) -> None:
    """Save resolutions, speakers, placeholder counter, and passages to JSON. Thread-unsafe."""
    path = _getStoragePath()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "resolutions": resolutionsMap,
        "speakers": speakersList,
        "placeholderCounter": placeholderCounter,
    }
    if passagesMap is not None:
        payload["passages"] = passagesMap
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def listSpeakers() -> list[dict]:
    """Return list of known speakers: [{\"id\": \"...\", \"name\": \"...\"}, ...]. From local storage."""
    _, speakersList, _, _ = _loadStorage()
    return list(speakersList)


def matchSegment(sMediaId: str, sSegmentId: str, fStart: float, fEnd: float) -> str | None:
    """
    Match a segment to a known speaker. Returns speaker id or None (unknown).
    Looks up persisted resolutions from resolveSegment().
    """
    resolutionsMap, _, _, _ = _loadStorage()
    byMedia = resolutionsMap.get(sMediaId)
    if not byMedia:
        return None
    return byMedia.get(sSegmentId)


def addSampleToSpeaker(
    sSpeakerId: str,
    sMediaId: str,
    sSegmentId: str,
    fStart: float,
    fEnd: float,
) -> tuple[bool, str | None]:
    """
    Add passage (segment reference) to speaker's corpus for 008 voice library.
    Stores in passages map: speakerId -> list of {mediaId, segmentId, start, end}.
    Returns (success, error_message).
    """
    if not sSpeakerId or not sMediaId or not sSegmentId:
        return False, "speakerId, mediaId, segmentId required"
    resolutionsMap, speakersList, placeholderCounter, passagesMap = _loadStorage()
    passageList = passagesMap.setdefault(sSpeakerId, [])
    passageList.append({
        "mediaId": sMediaId,
        "segmentId": sSegmentId,
        "start": fStart,
        "end": fEnd,
    })
    passagesMap[sSpeakerId] = passageList
    _saveStorage(resolutionsMap, speakersList, placeholderCounter, passagesMap)
    return True, None


def generateNextPlaceholderName() -> str:
    """
    Generate next globally unique placeholder name (Unidentified-<N>). Increments counter in storage.
    Per spec: no spaces, readable, globally unique. Max 64 chars (prefix + decimal).
    """
    resolutionsMap, speakersList, placeholderCounter, passagesMap = _loadStorage()
    placeholderCounter += 1
    name = f"{_PLACEHOLDER_PREFIX}{placeholderCounter}"
    _saveStorage(resolutionsMap, speakersList, placeholderCounter, passagesMap)
    return name


def createSpeaker(sName: str) -> tuple[str | None, str | None]:
    """Create new speaker with display name. Returns (speaker_id, error_message). Persisted to local storage."""
    safeName = (sName or "").replace(" ", "_").replace("\t", "_")[: 64]
    speakerId = "stub-" + safeName if safeName else "stub-unnamed"
    resolutionsMap, speakersList, nCounter, passagesMap = _loadStorage()
    if any(s.get("id") == speakerId for s in speakersList):
        return speakerId, None
    speakersList = list(speakersList)
    speakersList.append({"id": speakerId, "name": (sName or "")[: 256]})
    _saveStorage(resolutionsMap, speakersList, nCounter, passagesMap)
    return speakerId, None


def createPlaceholder(sName: str) -> tuple[str | None, str | None]:
    """Create placeholder speaker (full record, same as named). Returns (speaker_id, error_message)."""
    safeName = (sName or "").replace(" ", "_").replace("\t", "_")[: 64]
    placeholderId = "stub-placeholder-" + safeName if safeName else "stub-placeholder-unnamed"
    resolutionsMap, speakersList, nCounter, passagesMap = _loadStorage()
    if any(s.get("id") == placeholderId for s in speakersList):
        return placeholderId, None
    speakersList = list(speakersList)
    speakersList.append({"id": placeholderId, "name": (sName or "")[: 256]})
    _saveStorage(resolutionsMap, speakersList, nCounter, passagesMap)
    return placeholderId, None


def resolveSegment(
    sMediaId: str,
    sSegmentId: str,
    sResolution: str,
    sSpeakerId: str | None = None,
    sName: str | None = None,
    fSegmentStart: float | None = None,
    fSegmentEnd: float | None = None,
) -> tuple[bool, str | None, str | None]:
    """
    Resolve a segment: existing (speakerId), new (name), or placeholder (name optional).
    For placeholder with no name, server generates Unidentified-<N>. Full speaker record
    and passage added to corpus (007). Persist resolution so matchSegment() returns this speaker.
    Returns (success, error_message, assignedName). assignedName set when placeholder name was generated.
    """
    if not sMediaId or not sSegmentId or not sResolution:
        return False, "mediaId, segmentId, and resolution are required", None
    resolution = sResolution.strip().lower()
    speakerId: str | None = None
    assignedName: str | None = None
    if resolution == "existing":
        if not sSpeakerId or not sSpeakerId.strip():
            return False, "speakerId required for existing", None
        speakerId = sSpeakerId.strip()
    elif resolution == "new":
        name = (sName or "").strip()
        if not name:
            return False, "name required for new", None
        sid, err = createSpeaker(name)
        if err:
            return False, err, None
        speakerId = sid
    elif resolution == "placeholder":
        name = (sName or "").strip()
        if not name:
            name = generateNextPlaceholderName()
            assignedName = name
        sid, err = createPlaceholder(name)
        if err:
            return False, err, None
        speakerId = sid
    else:
        return False, "resolution must be existing, new, or placeholder", None

    resolutionsMap, speakersList, nCounter, passagesMap = _loadStorage()
    byMedia = resolutionsMap.setdefault(sMediaId, {})
    byMedia[sSegmentId] = speakerId or ""
    resolutionsMap[sMediaId] = byMedia
    _saveStorage(resolutionsMap, speakersList, nCounter, passagesMap)

    # Add passage to speaker's corpus (007: on confirm for existing/new/placeholder; 008 will use)
    if speakerId and fSegmentStart is not None and fSegmentEnd is not None:
        addSampleToSpeaker(speakerId, sMediaId, sSegmentId, fSegmentStart, fSegmentEnd)

    logger.debug("Resolved segment mediaId=%s segmentId=%s -> speakerId=%s", sMediaId, sSegmentId, speakerId)
    return True, None, assignedName
