# Python 3.x
"""
Pipeline API: GET config, GET discover, POST run, GET status per contracts/pipeline-api.md.
"""
from __future__ import annotations

import logging

from flask import Blueprint, jsonify, request

from backend.src.models.masterConfigModel import (
    getPipelineAutoProcessingEnabled,
    getPipelineUnknownSpeakersStepOverride,
)
from backend.src.models.pipelineStepPlan import (
    getStepFolderOrder,
    getFinalFolderName,
    getUnknownSpeakersStepName,
)
from backend.src.services.pipelineDiscoveryService import (
    getPipelineBasePathsResolved,
    discoverMediaInStep1,
)
from backend.src.services.pipelineRunService import runOnePass, getStatusByStep

logger = logging.getLogger(__name__)


def register(bp: Blueprint) -> None:
    @bp.route("/config", methods=["GET"])
    def getConfig():
        basePaths = getPipelineBasePathsResolved()
        stepFolders = getStepFolderOrder()
        override = getPipelineUnknownSpeakersStepOverride()
        unknownStep = getUnknownSpeakersStepName(override)
        return jsonify({
            "basePaths": basePaths,
            "stepFolders": stepFolders,
            "unknownSpeakersStepName": unknownStep,
            "finalFolderName": getFinalFolderName(),
        })

    @bp.route("/discover", methods=["GET"])
    def getDiscover():
        basePathFilter = request.args.get("basePath", "").strip() or None
        items = discoverMediaInStep1(basePathFilter)
        return jsonify({"items": items, "total": len(items)})

    @bp.route("/run", methods=["POST"])
    def postRun():
        if getPipelineAutoProcessingEnabled():
            return jsonify({
                "error": "Processing is automatic; no run trigger needed. Use discovery/status for visibility.",
            }), 410
        body = request.get_json(silent=True) or {}
        iLimit = body.get("limit")
        if iLimit is not None:
            try:
                iLimit = int(iLimit)
            except (TypeError, ValueError):
                iLimit = None
        result = runOnePass(iLimit)
        logger.info("POST pipeline/run result: %s", result)
        return jsonify(result)

    @bp.route("/status", methods=["GET"])
    def getStatus():
        byStep = getStatusByStep()
        return jsonify({"byStep": byStep})
