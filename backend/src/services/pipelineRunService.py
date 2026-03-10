# Python 3.x
"""
Pipeline run: discover media in step 1, run step processors in order (stub: move only).
Step 5: if any unknown speaker -> move to step 5 and stop; else move to 6. Stub: treat as unknown.
"""
from __future__ import annotations

import logging
import time
from pathlib import Path

from backend.src.models.pipelineStepPlan import getFinalFolderName, getStepFolderOrder
from backend.src.services.pipelineDiscoveryService import (
    discoverMediaInStep1,
    getPipelineBasePathsResolved,
)
from backend.src.services.mediaLogService import MediaLog
from backend.src.services.pipelineMoveService import getNextStepDir, moveToNextStep
from backend.src.services.pipeline.step2_audio import processStep2
from backend.src.services.pipeline.step3_transcribe import processStep3
from backend.src.services.pipeline.step4_diarize import processStep4
from backend.src.services.pipeline.step5_speaker_id import hasAnyUnknownSpeaker, processStep5
from backend.src.services.pipeline.step6_summarize import processStep6
from backend.src.services.pipeline.step7_export import processStep7
from backend.src.services.pipeline.step8_ready import processStep8

logger = logging.getLogger(__name__)


def runNextStepForOneFile(
    sMediaPath: str,
    sPairedFolderPath: str | None,
) -> tuple[bool, str | None]:
    """
    Run one step for a single file: run step processor (if step 2 or 3), then move
    file and paired folder to the next step. Single file, one step only.
    Returns (success, error_message). Writes events to sidecar pipeline.log.
    """
    mediaLog = MediaLog(sPairedFolderPath)
    mediaLog.runStart(sMediaPath)

    if not sMediaPath or not Path(sMediaPath).exists():
        mediaLog.runFailed("Media path missing or does not exist")
        return False, "Media path missing or does not exist"
    nextDir = getNextStepDir(sMediaPath, sPairedFolderPath)
    if not nextDir:
        mediaLog.runFailed("No next step (file may already be in final folder)")
        return False, "No next step (file may already be in final folder)"
    stepOrder = getStepFolderOrder()
    nextStepName = Path(nextDir).name
    currentStepName = Path(sMediaPath).parent.name

    mediaLog.stepStart(nextStepName)
    t0 = time.perf_counter()
    try:
        if nextStepName == stepOrder[1]:
            ok, err = processStep2(sMediaPath, sPairedFolderPath)
        elif nextStepName == stepOrder[2]:
            ok, err = processStep3(sMediaPath, sPairedFolderPath)
        elif nextStepName == stepOrder[3]:
            ok, err = processStep4(sMediaPath, sPairedFolderPath)
        elif nextStepName == stepOrder[4]:
            ok, err = processStep5(sMediaPath, sPairedFolderPath)
        elif nextStepName == stepOrder[5]:
            ok, err = processStep5(sMediaPath, sPairedFolderPath)
        elif nextStepName == stepOrder[6]:
            ok, err = processStep6(sMediaPath, sPairedFolderPath)  # summarization for "Videos 7 summarization done"
        elif nextStepName == stepOrder[7]:
            ok, err = processStep7(sMediaPath, sPairedFolderPath)
        elif nextStepName == getFinalFolderName():
            ok, err = processStep8(sMediaPath, sPairedFolderPath)
        else:
            ok, err = True, None
    except Exception as e:
        logger.exception("Step %s failed for %s", nextStepName, sMediaPath)
        ok, err = False, str(e)
    durationSec = time.perf_counter() - t0
    mediaLog.stepEnd(nextStepName, ok, err, durationSec=durationSec)
    if not ok:
        mediaLog.runFailed(err or "Step processor failed", sPairedFolderPathOverride=sPairedFolderPath)
        return False, err or "Step processor failed"
    # Moving from step 5 to step 6: only if no unknown speakers
    if nextStepName == stepOrder[5]:
        hasUnknown, _ = hasAnyUnknownSpeaker(sMediaPath, sPairedFolderPath)
        if hasUnknown:
            mediaLog.runStoppedInStep5(
                "Unknown speakers; file remains in step 5",
                sPairedFolderPathOverride=sPairedFolderPath,
            )
            return False, "Unknown speakers; file remains in step 5"
    ok, err = moveToNextStep(sMediaPath, sPairedFolderPath, nextDir)
    newPaired = str(Path(nextDir) / Path(sMediaPath).stem)
    if ok:
        mediaLog.setPairedPath(newPaired)
    mediaLog.moveResult(ok, currentStepName, nextStepName, err)
    if not ok:
        mediaLog.runFailed(err or "Move failed", sPairedFolderPathOverride=sPairedFolderPath)
        return False, err or "Move failed"
    mediaLog.runComplete(nextDir, sPairedFolderPathOverride=newPaired)
    logger.info("Moved one step: %s -> %s", sMediaPath, nextDir)
    return True, None


def runOnePass(iLimit: int | None = None) -> dict:
    """
    Run one pipeline pass: discover media in step 1, process each through steps 2->...->5 or 6->7->8->Videos.
    Step 5: if any unknown speaker, file stays in step 5; else moves to 6->7->8->Videos.
    Returns dict: processed, movedToStep5, movedToVideos, errors.
    """
    logger.info("Pipeline run start (limit=%s)", iLimit)
    items = discoverMediaInStep1()
    if iLimit is not None and iLimit > 0:
        items = items[: iLimit]
    iProcessed = 0
    iMovedToStep5 = 0
    iMovedToVideos = 0
    errorsList: list[str] = []
    stepOrder = getStepFolderOrder()

    for item in items:
        mediaPath = item.get("mediaPath", "")
        pairedPath = item.get("pairedFolderPath")
        if not mediaPath or not Path(mediaPath).exists():
            continue
        mediaLog = MediaLog(pairedPath)
        mediaLog.runStart(mediaPath)
        try:
            currentPath = mediaPath
            currentPaired = pairedPath
            # Move through steps 2..8 then Videos; step 5->6 only if no unknown speakers
            for stepName in stepOrder[1:]:
                nextDir = getNextStepDir(currentPath, currentPaired)
                if not nextDir:
                    mediaLog.info("No next step; already at final folder or invalid state")
                    break
                nextStepName = Path(nextDir).name
                currentStepName = Path(currentPath).parent.name
                mediaLog.stepStart(nextStepName)
                t0 = time.perf_counter()
                try:
                    if nextStepName == stepOrder[1]:
                        ok, err = processStep2(currentPath, currentPaired)
                    elif nextStepName == stepOrder[2]:
                        ok, err = processStep3(currentPath, currentPaired)
                    elif nextStepName == stepOrder[3]:
                        ok, err = processStep4(currentPath, currentPaired)
                    elif nextStepName == stepOrder[4]:
                        ok, err = processStep5(currentPath, currentPaired)
                    elif nextStepName == stepOrder[5]:
                        ok, err = processStep5(currentPath, currentPaired)
                    elif nextStepName == stepOrder[6]:
                        ok, err = processStep6(currentPath, currentPaired)  # summarization
                    elif nextStepName == stepOrder[7]:
                        ok, err = processStep7(currentPath, currentPaired)
                    elif nextStepName == getFinalFolderName():
                        ok, err = processStep8(currentPath, currentPaired)
                    else:
                        ok, err = True, None
                except Exception as e:
                    logger.exception("Step %s failed for %s", nextStepName, currentPath)
                    ok, err = False, str(e)
                durationSec = time.perf_counter() - t0
                mediaLog.stepEnd(nextStepName, ok, err, durationSec=durationSec)
                if not ok:
                    errorsList.append(f"{currentPath}: {err}")
                    mediaLog.runFailed(
                        err or "Step processor failed",
                        sPairedFolderPathOverride=currentPaired,
                    )
                    break
                # Step 5 -> 6: move only if no unknown speakers; else leave in step 5
                if nextStepName == stepOrder[5]:
                    hasUnknown, _ = hasAnyUnknownSpeaker(currentPath, currentPaired)
                    if hasUnknown:
                        iMovedToStep5 += 1
                        iProcessed += 1
                        mediaLog.runStoppedInStep5(
                            "Unknown speakers; file remains in step 5",
                            sPairedFolderPathOverride=currentPaired,
                        )
                        break  # Leave file in step 5
                ok, err = moveToNextStep(currentPath, currentPaired, nextDir)
                if ok:
                    stem = Path(currentPath).stem
                    currentPath = str(Path(nextDir) / Path(currentPath).name)
                    currentPaired = str(Path(nextDir) / stem)
                    mediaLog.setPairedPath(currentPaired)
                mediaLog.moveResult(ok, currentStepName, nextStepName, err)
                if not ok:
                    errorsList.append(f"{currentPath}: {err}")
                    mediaLog.runFailed(
                        err or "Move failed",
                        sPairedFolderPathOverride=currentPaired,
                    )
                    break
                logger.info("Moved to %s: %s", stepName, currentPath)
            else:
                iMovedToVideos += 1
                iProcessed += 1
                mediaLog.runComplete(
                    str(Path(currentPath).parent),
                    sPairedFolderPathOverride=currentPaired,
                )
        except Exception as e:
            logger.exception("Pipeline run error for %s", mediaPath)
            errorsList.append(f"{mediaPath}: {e}")
            mediaLog.runFailed(str(e), sPairedFolderPathOverride=currentPaired)

    logger.info(
        "Pipeline run end: processed=%s movedToStep5=%s movedToVideos=%s errors=%s",
        iProcessed,
        iMovedToStep5,
        iMovedToVideos,
        len(errorsList),
    )
    return {
        "processed": iProcessed,
        "movedToStep5": iMovedToStep5,
        "movedToVideos": iMovedToVideos,
        "errors": errorsList,
    }


def getStatusByStep() -> dict[str, int]:
    """Scan configured bases and count media files per step folder. Returns dict stepName -> count."""
    bases = getPipelineBasePathsResolved()
    stepOrder = getStepFolderOrder()
    finalName = getFinalFolderName()
    result: dict[str, int] = {}
    for stepName in stepOrder:
        result[stepName] = 0
    result[finalName] = 0
    for sBase in bases:
        basePath = Path(sBase)
        if not basePath.is_dir():
            continue
        for channelDir in basePath.iterdir():
            if not channelDir.is_dir():
                continue
            for stepName in stepOrder:
                stepDir = channelDir / stepName
                if not stepDir.is_dir():
                    continue
                count = sum(1 for e in stepDir.iterdir() if e.is_file() and e.suffix.lower() in {".mp4", ".mkv", ".mov", ".avi", ".webm", ".mp3", ".m4a", ".wav", ".flac"})
                result[stepName] = result.get(stepName, 0) + count
            finalDir = channelDir / finalName
            if finalDir.is_dir():
                count = sum(1 for e in finalDir.iterdir() if e.is_file() and e.suffix.lower() in {".mp4", ".mkv", ".mov", ".avi", ".webm", ".mp3", ".m4a", ".wav", ".flac"})
                result[finalName] = result.get(finalName, 0) + count
    return result
