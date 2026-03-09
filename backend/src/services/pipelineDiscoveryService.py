# Python 3.x
"""
Pipeline discovery: list media files in "Videos 1 to be transcribed" under configured base paths.
Base paths from master config [pipeline] basePaths; if empty, from inbox tab paths.
"""
from __future__ import annotations

from pathlib import Path

from backend.src.models.configModel import loadConfigFromPath
from backend.src.models.masterConfigModel import getPipelineBasePaths, getPipelineUnknownSpeakersStepOverride
from backend.src.models.pipelineStepPlan import getStepFolderOrder, getUnknownSpeakersStepName
from backend.src.services.configService import getConfigPath
from backend.src.services.sisterFilesCollectService import collectSisterFilesIntoPairedFolder

# Step 1 folder name (queue input for pipeline)
STEP1_NAME = "Videos 1 to be transcribed"

# Media extensions to consider as primary media
MEDIA_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".mp3", ".m4a", ".wav", ".flac"}


def getPipelineBasePathsResolved() -> list[str]:
    """
    Base paths for pipeline discovery: [pipeline] basePaths from master config;
    if empty, collect all paths from inbox tabs.
    """
    basePaths = getPipelineBasePaths()
    if basePaths:
        return [str(Path(p).resolve()) for p in basePaths if p]
    # Fallback: inbox tab paths
    sConfigPath = getConfigPath()
    tabsList = loadConfigFromPath(sConfigPath)
    seen: set[str] = set()
    resultList: list[str] = []
    for tab in tabsList:
        for sPath in (tab.get("paths") or []):
            if sPath and sPath not in seen:
                seen.add(sPath)
                resultList.append(str(Path(sPath).resolve()))
    return resultList


def discoverMediaInStep1(sBasePathFilter: str | None = None) -> list[dict]:
    """
    Discover media in "Videos 1 to be transcribed" under configured bases.
    Returns list of dicts: mediaPath, pairedFolderPath, channelName, basePath.
    If sBasePathFilter is set, only that base path is scanned.
    """
    bases = getPipelineBasePathsResolved()
    if sBasePathFilter:
        bases = [b for b in bases if b == sBasePathFilter or b == str(Path(sBasePathFilter).resolve())]
    stepOrder = getStepFolderOrder()
    step1Name = stepOrder[0] if stepOrder else STEP1_NAME
    resultList: list[dict] = []
    for sBase in bases:
        basePath = Path(sBase)
        if not basePath.is_dir():
            continue
        for channelDir in basePath.iterdir():
            if not channelDir.is_dir():
                continue
            step1Dir = channelDir / step1Name
            if not step1Dir.is_dir():
                continue
            sChannelName = channelDir.name
            for entry in step1Dir.iterdir():
                if entry.is_file() and entry.suffix.lower() in MEDIA_EXTENSIONS:
                    mediaPath = str(entry)
                    # 003: collect sister files into paired folder before discovery
                    collectSisterFilesIntoPairedFolder(mediaPath)
                    # Paired folder = same stem in same dir (sidecar)
                    pairedFolder = step1Dir / entry.stem
                    resultList.append({
                        "mediaPath": mediaPath,
                        "pairedFolderPath": str(pairedFolder),
                        "channelName": sChannelName,
                        "basePath": sBase,
                    })
    return resultList


def discoverMediaInAllSteps(sBasePathFilter: str | None = None) -> list[dict]:
    """
    Discover media in all pipeline step folders (1–8) under configured bases/channels.
    Returns list of dicts: mediaPath, pairedFolderPath, channelName, basePath,
    stepFolderName, stepIndex (0–7). If sBasePathFilter is set, only that base is scanned.
    """
    bases = getPipelineBasePathsResolved()
    if sBasePathFilter:
        bases = [b for b in bases if b == sBasePathFilter or b == str(Path(sBasePathFilter).resolve())]
    stepOrder = getStepFolderOrder()
    resultList: list[dict] = []
    for sBase in bases:
        basePath = Path(sBase)
        if not basePath.is_dir():
            continue
        for channelDir in basePath.iterdir():
            if not channelDir.is_dir():
                continue
            sChannelName = channelDir.name
            for stepIndex, stepName in enumerate(stepOrder):
                stepDir = channelDir / stepName
                if not stepDir.is_dir():
                    continue
                for entry in stepDir.iterdir():
                    if entry.is_file() and entry.suffix.lower() in MEDIA_EXTENSIONS:
                        mediaPath = str(entry)
                        # 003: collect sister files into paired folder in step 1
                        if stepIndex == 0:
                            collectSisterFilesIntoPairedFolder(mediaPath)
                        pairedFolder = stepDir / entry.stem
                        resultList.append({
                            "mediaPath": mediaPath,
                            "pairedFolderPath": str(pairedFolder),
                            "channelName": sChannelName,
                            "basePath": sBase,
                            "stepFolderName": stepName,
                            "stepIndex": stepIndex,
                        })
    return resultList


def discoverMediaInUnknownSpeakersStep(sBasePathFilter: str | None = None) -> list[dict]:
    """
    Discover media in the unknown-speakers step folder (step 5) under configured bases.
    Returns list of dicts: mediaPath, pairedFolderPath, channelName, basePath, mediaId.
    mediaId is a stable key for API (channelName|stem) for lookups.
    """
    override = getPipelineUnknownSpeakersStepOverride()
    step5Name = getUnknownSpeakersStepName(override)
    bases = getPipelineBasePathsResolved()
    if sBasePathFilter:
        bases = [b for b in bases if b == sBasePathFilter or b == str(Path(sBasePathFilter).resolve())]
    resultList: list[dict] = []
    for sBase in bases:
        basePath = Path(sBase)
        if not basePath.is_dir():
            continue
        for channelDir in basePath.iterdir():
            if not channelDir.is_dir():
                continue
            stepDir = channelDir / step5Name
            if not stepDir.is_dir():
                continue
            sChannelName = channelDir.name
            for entry in stepDir.iterdir():
                if entry.is_file() and entry.suffix.lower() in MEDIA_EXTENSIONS:
                    mediaPath = str(entry)
                    pairedFolder = stepDir / entry.stem
                    # Stable opaque key for API: channel|stem (unique per channel)
                    mediaId = f"{sChannelName}|{entry.stem}"
                    resultList.append({
                        "mediaPath": mediaPath,
                        "pairedFolderPath": str(pairedFolder),
                        "channelName": sChannelName,
                        "basePath": sBase,
                        "mediaId": mediaId,
                    })
    return resultList


def getMediaItemByMediaId(sMediaId: str) -> dict | None:
    """
    Return the discovery item (mediaPath, pairedFolderPath, channelName, basePath, mediaId)
    for the given mediaId, or None if not found. Scans unknown-speakers step.
    """
    items = discoverMediaInUnknownSpeakersStep()
    for item in items:
        if item.get("mediaId") == sMediaId:
            return item
    return None
