# Python 3.x
"""
Pipeline step folder names and order per spec (002). All paths relative to channel folder.
"""
from __future__ import annotations

# Step order: 1 = queue input, 2–8 = processing, then final "Videos"
STEP_FOLDERS: list[str] = [
    "Videos 1 to be transcribed",
    "Videos 2 audio extracted",
    "Videos 3 transcribed",
    "Videos 4 diarized",
    "Videos 5 needs speaker identification",
    "Videos 6 speakers matched",
    "Videos 7 summarization done",
    "Videos 8 export ready",
]

FINAL_FOLDER: str = "Videos"

# Default unknown-speakers step (index 4 = step 5)
DEFAULT_UNKNOWN_SPEAKERS_STEP_NAME: str = "Videos 5 needs speaker identification"


def getStepFolderOrder() -> list[str]:
    """Return ordered list of step folder names (1 through 8)."""
    return list(STEP_FOLDERS)


def getNextStepFolder(currentStepName: str) -> str | None:
    """
    Return the next step folder name after currentStepName, or None if current is last step.
    """
    order = getStepFolderOrder()
    try:
        i = order.index(currentStepName)
    except ValueError:
        return None
    if i + 1 >= len(order):
        return None
    return order[i + 1]


def getFinalFolderName() -> str:
    """Return the final destination folder name (Videos)."""
    return FINAL_FOLDER


def getUnknownSpeakersStepName(override: str | None = None) -> str:
    """Return the unknown-speakers step folder name (config override or default)."""
    if override and override.strip():
        return override.strip()
    return DEFAULT_UNKNOWN_SPEAKERS_STEP_NAME
