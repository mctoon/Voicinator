# Python 3.x
"""
Step 3: Transcription with Whisper Large-v3. Write word-level transcript (JSON) and
human-readable transcript (TXT) to paired folder. Uses faster-whisper with large-v3 model.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from backend.src.services.pipeline.step2_audio import EXTRACTED_AUDIO_FILENAME

logger = logging.getLogger(__name__)

# Output filenames in paired folder (per data-model and research)
WORD_LEVEL_JSON_FILENAME = "transcript_words.json"
HUMAN_READABLE_TXT_FILENAME = "transcript.txt"

# Whisper model name (Large-v3 per spec)
WHISPER_MODEL_SIZE = "large-v3"


def _ensurePairedFolder(sPairedFolderPath: str | None) -> Path | None:
    """Return Path to paired folder, creating it if missing; None if path is empty."""
    if not sPairedFolderPath or not sPairedFolderPath.strip():
        return None
    p = Path(sPairedFolderPath)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _writeWordLevelJson(pairedDir: Path, wordsList: list[dict]) -> None:
    """Write word-level transcript as JSON: [{"word": "...", "start": 0.0, "end": 0.5}, ...]."""
    outPath = pairedDir / WORD_LEVEL_JSON_FILENAME
    with open(outPath, "w", encoding="utf-8") as f:
        json.dump(wordsList, f, ensure_ascii=False, indent=2)


def _formatTimestamp(seconds: float) -> str:
    """Format seconds as Otter-style time offset: M:SS or H:MM:SS (e.g. 0:00, 1:05, 1:23:45)."""
    totalSec = int(round(seconds))
    if totalSec < 3600:
        minutes = totalSec // 60
        secs = totalSec % 60
        return f"{minutes}:{secs:02d}"
    hours = totalSec // 3600
    remainder = totalSec % 3600
    minutes = remainder // 60
    secs = remainder % 60
    return f"{hours}:{minutes:02d}:{secs:02d}"


def _writeHumanReadableTxt(pairedDir: Path, segmentsList: list[tuple[str, float, float]]) -> None:
    """
    Write human-readable transcript (TXT). Otter-style: speaker line with time offset then text.
    Format per segment: "Speaker 1 M:SS" (or H:MM:SS) on one line, transcript text on the next.
    Pre-diarization we use a single "Speaker 1" for all segments.
    segmentsList: list of (text, start, end) per segment.
    """
    outPath = pairedDir / HUMAN_READABLE_TXT_FILENAME
    lines: list[str] = []
    for seg in segmentsList:
        if isinstance(seg, tuple) and len(seg) >= 3:
            sText = (seg[0] or "").strip()
            startSec = float(seg[1])
        else:
            sText = (seg[0] if isinstance(seg, tuple) else seg).strip()
            startSec = 0.0
        if sText:
            timeStr = _formatTimestamp(startSec)
            lines.append(f"Speaker 1 {timeStr}")
            lines.append(sText)
            lines.append("")
    with open(outPath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def processStep3(sMediaPath: str, sPairedFolderPath: str | None) -> tuple[bool, str | None]:
    """
    Run step 3: transcribe media with Whisper Large-v3; write word-level JSON and
    human-readable TXT to paired folder. Returns (success, error_message).
    """
    if not sMediaPath or not Path(sMediaPath).exists():
        return False, "Media path missing or does not exist"
    pairedDir = _ensurePairedFolder(sPairedFolderPath)
    if not pairedDir:
        return False, "Paired folder path missing"

    # Prefer extracted audio from step 2 (mono 16 kHz) when present
    audioPath = pairedDir / EXTRACTED_AUDIO_FILENAME
    inputPath = str(audioPath) if audioPath.exists() else sMediaPath

    try:
        from faster_whisper import WhisperModel
    except ImportError as e:
        logger.error("faster_whisper not installed: %s", e)
        return False, "faster_whisper not installed; pip install faster-whisper"

    try:
        model = WhisperModel(WHISPER_MODEL_SIZE, device="auto", compute_type="auto")
        segments, _ = model.transcribe(inputPath, word_timestamps=True, language="en")
        wordsList: list[dict] = []
        segmentsList: list[tuple[str, float, float]] = []
        for seg in segments:
            if seg.text and seg.text.strip():
                segmentsList.append((seg.text.strip(), seg.start, seg.end))
            if getattr(seg, "words", None):
                for w in seg.words:
                    wordStr = getattr(w, "word", str(w)).strip()
                    if wordStr:
                        wordsList.append({
                            "word": wordStr,
                            "start": round(float(getattr(w, "start", 0.0)), 3),
                            "end": round(float(getattr(w, "end", 0.0)), 3),
                        })
        _writeWordLevelJson(pairedDir, wordsList)
        _writeHumanReadableTxt(pairedDir, segmentsList)
        logger.info("Step 3 (transcribe) wrote %s and %s for %s", WORD_LEVEL_JSON_FILENAME, HUMAN_READABLE_TXT_FILENAME, sMediaPath)
        return True, None
    except Exception as e:
        logger.exception("Step 3 (transcribe) failed for %s", sMediaPath)
        return False, str(e)
