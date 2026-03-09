# Python 3.x
"""
Pipeline speakers (unknown-speakers) API: list files in step 5, segments, segment audio,
resolve speaker, list speakers. Auto-move to Videos when all segments resolved.
Per contracts/unknown-speakers-api.md. Base URL: /api/pipeline/speakers.
"""
from __future__ import annotations

import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path

from flask import Blueprint, jsonify, request, send_file, Response

from backend.src.services.pipelineDiscoveryService import (
    getPipelineBasePathsResolved,
    discoverMediaInUnknownSpeakersStep,
    getMediaItemByMediaId,
)
from backend.src.services.pipeline.speakerResolver import (
    listSpeakers as resolverListSpeakers,
    matchSegment as resolverMatchSegment,
    resolveSegment as resolverResolveSegment,
)
from backend.src.services.pipeline.step4_diarize import SEGMENTS_JSON_FILENAME
from backend.src.services.pipelineMoveService import getNextStepDir, moveToNextStep
from backend.src.models.pipelineStepPlan import getStepFolderOrder, getFinalFolderName

logger = logging.getLogger(__name__)


def _segmentsPathForPairedFolder(sPairedFolderPath: str) -> Path:
    return Path(sPairedFolderPath) / SEGMENTS_JSON_FILENAME


def _loadSegmentsWithResolvedSpeakers(sPairedFolderPath: str, sMediaId: str) -> list[dict]:
    """Load segments.json from paired folder and set speakerId from resolver for each segment."""
    p = _segmentsPathForPairedFolder(sPairedFolderPath)
    segmentsList: list[dict] = []
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            segmentsList = data.get("segments") or []
        except Exception:
            pass
    result: list[dict] = []
    for seg in segmentsList:
        segId = seg.get("segmentId", "")
        start = float(seg.get("start", 0))
        end = float(seg.get("end", 0))
        speakerId = resolverMatchSegment(sMediaId, segId, start, end)
        out = {
            "segmentId": segId,
            "start": start,
            "end": end,
            "label": seg.get("label", ""),
            "speakerId": speakerId,
        }
        result.append(out)
    return result


def _allSegmentsResolved(sPairedFolderPath: str, sMediaId: str) -> bool:
    """True if every segment has a resolved speakerId from the resolver."""
    segments = _loadSegmentsWithResolvedSpeakers(sPairedFolderPath, sMediaId)
    if not segments:
        return True
    return all(seg.get("speakerId") for seg in segments)


def _moveFileThroughToVideos(sMediaPath: str, sPairedFolderPath: str) -> tuple[bool, str | None]:
    """Move media and paired folder from step 5 through step 6 -> 7 -> 8 -> Videos."""
    from backend.src.services.pipeline.step6_summarize import processStep6
    from backend.src.services.pipeline.step7_export import processStep7
    from backend.src.services.pipeline.step8_ready import processStep8

    stepOrder = getStepFolderOrder()
    finalName = getFinalFolderName()
    currentPath = sMediaPath
    currentPaired = sPairedFolderPath
    for stepName in stepOrder[5:]:  # 6, 7, 8
        nextDir = getNextStepDir(currentPath, currentPaired)
        if not nextDir:
            break
        nextStepName = Path(nextDir).name
        if nextStepName == stepOrder[5]:
            ok, err = processStep6(currentPath, currentPaired)
        elif nextStepName == stepOrder[6]:
            ok, err = processStep7(currentPath, currentPaired)
        elif nextStepName == stepOrder[7]:
            ok, err = processStep8(currentPath, currentPaired)
        else:
            ok, err = True, None
        if not ok:
            return False, err or "Step failed"
        ok, err = moveToNextStep(currentPath, currentPaired, nextDir)
        if not ok:
            return False, err or "Move failed"
        stem = Path(currentPath).stem
        currentPath = str(Path(nextDir) / Path(currentPath).name)
        currentPaired = str(Path(nextDir) / stem)
    # Final move to Videos
    nextDir = getNextStepDir(currentPath, currentPaired)
    if nextDir and Path(nextDir).name == finalName:
        ok, err = moveToNextStep(currentPath, currentPaired, nextDir)
        if not ok:
            return False, err or "Move to Videos failed"
    return True, None


def register(bp: Blueprint) -> None:
    @bp.route("/speakers/files", methods=["GET"])
    def getFiles():
        items = discoverMediaInUnknownSpeakersStep()
        return jsonify({"items": items, "total": len(items)})

    @bp.route("/speakers/files/<mediaId>/segments", methods=["GET"])
    def getSegments(mediaId: str):
        item = getMediaItemByMediaId(mediaId)
        if not item:
            return jsonify({"error": "Not found"}), 404
        pairedPath = item.get("pairedFolderPath", "")
        segments = _loadSegmentsWithResolvedSpeakers(pairedPath, mediaId)
        return jsonify({"segments": segments})

    @bp.route("/speakers/segment-audio", methods=["GET"])
    def getSegmentAudio():
        mediaId = request.args.get("mediaId", "").strip()
        segmentId = request.args.get("segmentId", "").strip()
        item = getMediaItemByMediaId(mediaId)
        if not item:
            return jsonify({"error": "Not found"}), 404
        mediaPath = item.get("mediaPath", "")
        pairedPath = item.get("pairedFolderPath", "")
        segments = _loadSegmentsWithResolvedSpeakers(pairedPath, mediaId)
        seg = next((s for s in segments if s.get("segmentId") == segmentId), None)
        if not seg:
            return jsonify({"error": "Segment not found"}), 404
        start = float(seg.get("start", 0))
        end = float(seg.get("end", 0))
        # Prefer extracted audio.wav for consistent format
        from backend.src.services.pipeline.step2_audio import EXTRACTED_AUDIO_FILENAME
        audioPath = Path(pairedPath) / EXTRACTED_AUDIO_FILENAME
        if not audioPath.exists():
            audioPath = Path(mediaPath)
        if not audioPath.exists():
            return jsonify({"error": "Audio not found"}), 404
        # Validate path is under configured base paths
        bases = getPipelineBasePathsResolved()
        resolved = Path(audioPath).resolve()
        if not any(resolved.is_relative_to(Path(b).resolve()) for b in bases):
            return jsonify({"error": "Forbidden"}), 403
        duration = max(0.01, end - start)
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmpPath = tmp.name
            cmd = [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-i", str(audioPath), "-ss", str(start), "-t", str(duration),
                "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                tmpPath,
            ]
            subprocess.run(cmd, check=True, capture_output=True, timeout=30)
            with open(tmpPath, "rb") as f:
                data = f.read()
            try:
                os.unlink(tmpPath)
            except OSError:
                pass
            return Response(data, mimetype="audio/wav", headers={"Content-Disposition": "inline; filename=segment.wav"})
        except subprocess.CalledProcessError as e:
            logger.warning("ffmpeg segment extract failed: %s", e.stderr)
            return jsonify({"error": "Failed to extract segment audio"}), 500
        except FileNotFoundError:
            return jsonify({"error": "ffmpeg not found"}), 503
        except Exception as e:
            logger.exception("Segment audio failed")
            return jsonify({"error": str(e)}), 500

    @bp.route("/speakers/resolve", methods=["POST"])
    def postResolve():
        body = request.get_json(silent=True) or {}
        mediaId = (body.get("mediaId") or "").strip()
        segmentId = (body.get("segmentId") or "").strip()
        resolution = (body.get("resolution") or "").strip()
        speakerId = body.get("speakerId")
        if speakerId is not None:
            speakerId = str(speakerId).strip() or None
        name = body.get("name")
        if name is not None:
            name = str(name).strip() or None
        ok, err = resolverResolveSegment(mediaId, segmentId, resolution, speakerId, name)
        if not ok:
            return jsonify({"error": err or "Resolve failed"}), 400
        # Auto-move when all segments for this file are resolved
        item = getMediaItemByMediaId(mediaId)
        if item and _allSegmentsResolved(item.get("pairedFolderPath", ""), mediaId):
            moveOk, moveErr = _moveFileThroughToVideos(
                item.get("mediaPath", ""),
                item.get("pairedFolderPath", ""),
            )
            if moveOk:
                logger.info("Auto-moved %s to Videos (all resolved)", mediaId)
            else:
                logger.warning("Auto-move failed for %s: %s", mediaId, moveErr)
        return jsonify({"ok": True})

    @bp.route("/speakers/speakers", methods=["GET"])
    def getSpeakers():
        speakers = resolverListSpeakers()
        return jsonify({"speakers": speakers})

    @bp.route("/speakers/files/<mediaId>/move-to-videos", methods=["POST"])
    def postMoveToVideos(mediaId: str):
        item = getMediaItemByMediaId(mediaId)
        if not item:
            return jsonify({"error": "Not found"}), 404
        if not _allSegmentsResolved(item.get("pairedFolderPath", ""), mediaId):
            return jsonify({"error": "Not all segments resolved"}), 400
        ok, err = _moveFileThroughToVideos(
            item.get("mediaPath", ""),
            item.get("pairedFolderPath", ""),
        )
        if not ok:
            return jsonify({"error": err or "Move failed"}), 500
        return jsonify({"ok": True})
