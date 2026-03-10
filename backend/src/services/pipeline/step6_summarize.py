# Python 3.x
"""
Step 6: Summarization. Read transcript from paired folder, run configured summarization
parts (each with LLM + instructions), write one summary file into the paired folder.
Order of parts = config order. Empty or zero parts → skip with log; LLM errors → fail clearly.
All errors and summary write byte counts are appended to pipeline.log in the paired folder.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

from backend.src.models.masterConfigModel import getLlms, getSummarizations
from backend.src.services.mediaLogService import MediaLog
from backend.src.services.pipeline.llmClient import complete
from backend.src.services.pipeline.step3_transcribe import HUMAN_READABLE_TXT_FILENAME

logger = logging.getLogger(__name__)

SUMMARY_FILENAME = "summary.txt"


def _writeSummaryFile(
    pairedPath: Path,
    content: str,
    mediaLog: MediaLog,
) -> tuple[bool, str | None]:
    """
    Write summary.txt into paired folder. Creates dir if needed. Flushes to disk.
    Logs bytes_written (app count) and file_size_bytes (from filesystem) to pipeline.log.
    Returns (True, None) on success, (False, error_message) on failure.
    """
    pairedPath = pairedPath.resolve()
    pairedPath.mkdir(parents=True, exist_ok=True)
    summaryPath = pairedPath / SUMMARY_FILENAME
    bytesToWrite = len(content.encode("utf-8"))
    try:
        with open(summaryPath, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            try:
                os.fsync(f.fileno())
            except OSError:
                pass
        mediaLog.info(f"summary bytes_written={bytesToWrite}")
        try:
            fileSizeBytes = summaryPath.stat().st_size
            mediaLog.info(f"summary file_size_bytes={fileSizeBytes}")
        except OSError as e:
            errMsg = f"summary file_size error: {e}"
            mediaLog.error(errMsg)
            logger.warning("Step 6: %s", errMsg)
        logger.info("Step 6: wrote summary to %s", summaryPath)
        return True, None
    except OSError as e:
        errMsg = f"Failed to write summary: {e}"
        mediaLog.error(errMsg)
        logger.exception("Step 6: failed to write summary: %s", e)
        return False, errMsg


def processStep6(sMediaPath: str, sPairedFolderPath: str | None) -> tuple[bool, str | None]:
    """
    Generate summary from transcript in paired folder; write summary.txt into paired folder.
    Sends transcript to LLM multiple times per config (each part: different prompt); appends results.
    Returns (True, None) on success, (False, error_message) on failure.
    All errors and success are appended to pipeline.log in the paired folder.
    """
    mediaLog = MediaLog(sPairedFolderPath)
    mediaLog.info("Step 6 summarization start")
    if not sPairedFolderPath or not str(sPairedFolderPath).strip():
        mediaLog.error("Paired folder path missing")
        return False, "Paired folder path missing"
    pairedPath = Path(sPairedFolderPath).resolve()
    pairedPath.mkdir(parents=True, exist_ok=True)
    if not pairedPath.is_dir():
        err = f"Paired folder does not exist: {sPairedFolderPath}"
        mediaLog.error(err)
        return False, err
    transcriptPath = pairedPath / HUMAN_READABLE_TXT_FILENAME
    if not transcriptPath.is_file():
        logger.warning("Step 6: no transcript at %s; skipping summarization", transcriptPath)
        return _writeSummaryFile(pairedPath, "Summary skipped: no transcript found.\n", mediaLog)
    try:
        sTranscript = transcriptPath.read_text(encoding="utf-8", errors="replace").strip()
    except OSError as e:
        err = f"Failed to read transcript: {e}"
        mediaLog.error(err)
        logger.exception("Step 6: failed to read transcript at %s", transcriptPath)
        return False, err
    if not sTranscript:
        logger.warning("Step 6: empty transcript; skipping summarization")
        return _writeSummaryFile(pairedPath, "Summary skipped: transcript is empty.\n", mediaLog)
    try:
        summarizations = getSummarizations()
        llmsList = getLlms()
        llmByName = {llm.get("name", ""): llm for llm in llmsList if llm.get("name")}
    except Exception as e:
        err = f"Failed to load summarization config: {e}"
        mediaLog.error(err)
        logger.exception("Step 6: %s", e)
        return False, err
    if not summarizations:
        logger.info("Step 6: no summarization parts configured; skipping")
        return _writeSummaryFile(
            pairedPath,
            "Summary skipped: no summarization parts configured. Add parts in Config.\n",
            mediaLog,
        )
    try:
        partsList = _runSummarizationParts(summarizations, llmByName, sTranscript, mediaLog)
    except Exception as e:
        err = str(e)
        mediaLog.error(f"Step 6 summarization failed: {err}")
        logger.exception("Step 6: summarization failed: %s", e)
        return False, err
    if not partsList:
        logger.warning("Step 6: no parts produced output; writing minimal summary")
        partsList = ["(No summary sections generated.)\n"]
    ok, err = _writeSummaryFile(pairedPath, "\n".join(partsList), mediaLog)
    if ok:
        mediaLog.info("Step 6 summarization complete")
    return ok, err


TRANSCRIPT_PLACEHOLDER = "{{TRANSCRIPT}}"


def _substituteTranscript(sTemplate: str, sTranscript: str) -> str:
    """Replace {{TRANSCRIPT}} in sTemplate with the actual transcript."""
    return sTemplate.replace(TRANSCRIPT_PLACEHOLDER, sTranscript)


def _runSummarizationParts(
    summarizations: list,
    llmByName: dict,
    sTranscript: str,
    mediaLog: MediaLog,
) -> list[str]:
    """Run each summarization part (LLM call per config); append results. Logs LLM errors to pipeline.log.
    Each part has systemPrompt and userPrompt; {{TRANSCRIPT}} in either is replaced with the transcript.
    """
    partsList: list[str] = []
    for part in summarizations:
        sName = (part.get("name") or "").strip()
        sLlm = (part.get("llm") or "").strip()
        sSystemPrompt = (part.get("systemPrompt") or "").strip()
        sUserPrompt = (part.get("userPrompt") or "").strip()
        if not sLlm:
            continue
        if not sSystemPrompt and not sUserPrompt:
            logger.warning("Step 6: part '%s' has empty system and user prompt; skipping part", sName)
            continue
        if sLlm.lower().startswith("local:"):
            modelName = sLlm.split(":", 1)[1].strip() if ":" in sLlm else ""
            if not modelName:
                logger.warning("Step 6: part '%s' has invalid Local: llm; skipping part", sName)
                continue
            llmDict = {"type": "ollama", "baseUrl": "http://localhost:11434", "model": modelName}
        elif sLlm in llmByName:
            llmDict = dict(llmByName[sLlm])
            if llmDict.get("type") == "remote" and not llmDict.get("baseUrl") and llmDict.get("provider"):
                from backend.src.models.llmProvidersModel import getProviderBaseUrl
                baseUrl = getProviderBaseUrl(llmDict["provider"])
                if baseUrl:
                    llmDict["baseUrl"] = baseUrl
        else:
            logger.warning("Step 6: part '%s' references unknown LLM '%s'; skipping part", sName, sLlm)
            continue
        systemPrompt = _substituteTranscript(sSystemPrompt, sTranscript)
        userPrompt = _substituteTranscript(sUserPrompt, sTranscript)
        try:
            text = complete(llmDict, systemPrompt, userPrompt)
        except Exception as e:
            msg = f"Step 6: LLM failed for part '{sName}': {e}"
            mediaLog.error(msg)
            logger.warning("%s; skipping part", msg)
            partsList.append(f"## {sName}\n\n(Skipped: LLM error.)\n")
            continue
        if text:
            partsList.append(f"## {sName}\n\n{text}\n")
    return partsList
