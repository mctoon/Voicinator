# Python 3.x
"""
Step 2: Audio extraction. Extract audio from media (video or audio) and write to paired folder
as mono 16 kHz 16-bit WAV for Whisper. Uses ffmpeg (subprocess).
"""
from __future__ import annotations

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

# Output filename in paired folder (mono, 16 kHz, 16-bit WAV per pipeline docs)
EXTRACTED_AUDIO_FILENAME = "audio.wav"

# Target format for Whisper / downstream: mono, 16 kHz, 16-bit PCM
SAMPLE_RATE_HZ = 16000
CHANNELS = 1


def _runFfmpegExtract(sInputPath: str, sOutputPath: str) -> tuple[bool, str | None]:
    """
    Run ffmpeg to extract audio: -vn (no video), mono, 16 kHz, 16-bit PCM WAV.
    Returns (success, error_message). Requires ffmpeg on PATH.
    """
    cmd = [
        "ffmpeg",
        "-y",  # overwrite output
        "-i", sInputPath,
        "-vn",  # no video
        "-acodec", "pcm_s16le",
        "-ar", str(SAMPLE_RATE_HZ),
        "-ac", str(CHANNELS),
        "-hide_banner", "-loglevel", "error",
        sOutputPath,
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600,
        )
        if result.returncode != 0:
            err = (result.stderr or result.stdout or "").strip() or "ffmpeg failed"
            return False, err
        return True, None
    except FileNotFoundError:
        return False, "ffmpeg not found; install with e.g. brew install ffmpeg"
    except subprocess.TimeoutExpired:
        return False, "ffmpeg timed out"
    except Exception as e:
        return False, str(e)


def processStep2(sMediaPath: str, sPairedFolderPath: str | None) -> tuple[bool, str | None]:
    """
    Run step 2: extract audio from media and write to paired folder as audio.wav
    (mono, 16 kHz, 16-bit). Returns (success, error_message).
    """
    if not sMediaPath or not Path(sMediaPath).exists():
        return False, "Media path missing or does not exist"
    if not sPairedFolderPath or not sPairedFolderPath.strip():
        return False, "Paired folder path missing"

    pairedDir = Path(sPairedFolderPath)
    pairedDir.mkdir(parents=True, exist_ok=True)
    outPath = pairedDir / EXTRACTED_AUDIO_FILENAME

    ok, err = _runFfmpegExtract(sMediaPath, str(outPath))
    if not ok:
        logger.warning("Step 2 (audio extraction) failed for %s: %s", sMediaPath, err)
        return False, err
    if not outPath.exists():
        return False, "ffmpeg did not produce output file"
    logger.info("Step 2 (audio extraction) wrote %s for %s", outPath, sMediaPath)
    return True, None
