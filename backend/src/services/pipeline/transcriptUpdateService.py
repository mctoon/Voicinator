# Python 3.x
"""
Transcript update after speaker identification: backup then rewrite transcript.txt and
transcript_words.json with resolved speaker names. Per Contract §5 and research.md.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from backend.src.services.pipeline.step3_transcribe import (
    WORD_LEVEL_JSON_FILENAME,
    HUMAN_READABLE_TXT_FILENAME,
)
from backend.src.services.pipeline.step4_diarize import SEGMENTS_JSON_FILENAME
from backend.src.services.pipeline.speakerResolver import (
    listSpeakers,
    matchSegment,
)

logger = logging.getLogger(__name__)

BACKUP_TXT = "transcript_pre_speaker_id.txt"
BACKUP_JSON = "transcript_words_pre_speaker_id.json"


def _speakerIdToNameMap() -> dict[str, str]:
    """Build speakerId -> display name from resolver."""
    speakers = listSpeakers()
    return {s.get("id", ""): (s.get("name") or s.get("id") or "") for s in speakers if s.get("id")}


def _formatTimestamp(seconds: float) -> str:
    """Format seconds as M:SS or H:MM:SS."""
    s = int(seconds)
    if s >= 3600:
        return f"{s // 3600}:{(s % 3600) // 60:02d}:{s % 60:02d}"
    return f"{s // 60}:{s % 60:02d}"


def backupAndRewriteTranscripts(
    sPairedFolderPath: str,
    sMediaId: str,
) -> tuple[bool, str | None]:
    """
    Copy transcript.txt and transcript_words.json to backup names, then rewrite
    with resolved speaker names. Returns (success, error_message).
    """
    paired = Path(sPairedFolderPath)
    txtPath = paired / HUMAN_READABLE_TXT_FILENAME
    wordsPath = paired / WORD_LEVEL_JSON_FILENAME
    segPath = paired / SEGMENTS_JSON_FILENAME

    if not txtPath.exists() and not wordsPath.exists():
        return False, "Transcript files missing"

    idToName = _speakerIdToNameMap()

    # Load segments and resolved speaker per segment
    if not segPath.exists():
        return False, "segments.json missing"
    try:
        segData = json.loads(segPath.read_text(encoding="utf-8"))
        segmentsList = segData.get("segments") or []
    except Exception as e:
        logger.warning("Failed to load segments %s: %s", segPath, e)
        return False, "Failed to load segments"

    segmentIdToName: dict[str, str] = {}
    for seg in segmentsList:
        segId = seg.get("segmentId", "")
        start = float(seg.get("start", 0))
        end = float(seg.get("end", 0))
        speakerId = matchSegment(sMediaId, segId, start, end)
        name = (idToName.get(speakerId) or speakerId or seg.get("label", "")) if speakerId else seg.get("label", "Unknown")
        segmentIdToName[segId] = name

    # Backup
    if txtPath.exists():
        backupTxt = paired / BACKUP_TXT
        try:
            backupTxt.write_text(txtPath.read_text(encoding="utf-8"), encoding="utf-8")
        except Exception as e:
            return False, f"Backup transcript.txt failed: {e}"
    if wordsPath.exists():
        backupJson = paired / BACKUP_JSON
        try:
            backupJson.write_text(wordsPath.read_text(encoding="utf-8"), encoding="utf-8")
        except Exception as e:
            return False, f"Backup transcript_words.json failed: {e}"

    # Load words
    wordsList: list[dict] = []
    if wordsPath.exists():
        try:
            data = json.loads(wordsPath.read_text(encoding="utf-8"))
            wordsList = data if isinstance(data, list) else (data.get("words") or [])
            if not isinstance(wordsList, list):
                wordsList = []
        except Exception as e:
            return False, f"Failed to load transcript_words: {e}"

    # Assign speaker name per word by segment
    newWords: list[dict] = []
    for w in wordsList:
        start = float(w.get("start", 0))
        end = float(w.get("end", start))
        mid = (start + end) / 2
        segmentId = None
        for seg in segmentsList:
            if seg.get("start", 0) <= mid <= seg.get("end", 0):
                segmentId = seg.get("segmentId")
                break
        name = segmentIdToName.get(segmentId, "") if segmentId else ""
        newWords.append({
            "word": w.get("word", ""),
            "start": start,
            "end": end,
            "speakerId": name,
        })

    # Write new transcript_words.json
    try:
        wordsPath.write_text(json.dumps(newWords, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        return False, f"Write transcript_words.json failed: {e}"

    # Build and write transcript.txt by segment
    lines: list[str] = []
    for seg in segmentsList:
        segId = seg.get("segmentId", "")
        start = float(seg.get("start", 0))
        name = segmentIdToName.get(segId, "Unknown")
        segWords = [nw["word"] for nw in newWords if seg.get("start", 0) <= (nw["start"] + nw["end"]) / 2 <= seg.get("end", 0)]
        text = " ".join(segWords).strip()
        if text:
            lines.append(f"{name} {_formatTimestamp(start)}")
            lines.append(text)
            lines.append("")
    try:
        txtPath.write_text("\n".join(lines), encoding="utf-8")
    except Exception as e:
        return False, f"Write transcript.txt failed: {e}"

    logger.info("Transcripts updated in %s", sPairedFolderPath)
    return True, None
