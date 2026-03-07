# Python 3.x
"""GET /api/inbox/tabs/<tabId>/channels — paginated channel list."""
from __future__ import annotations

import logging

from flask import Blueprint, jsonify, request

from backend.src.services.configService import getConfigPath, getTabs
from backend.src.services.channelScanService import scanChannelsForTab

logger = logging.getLogger(__name__)


def register(bp: Blueprint) -> None:
    @bp.route("/tabs/<tabId>/channels", methods=["GET"])
    def getChannelsRoute(tabId):
        sConfigPath = getConfigPath()
        tabsList = getTabs(sConfigPath)
        tabDict = next((t for t in tabsList if str(t.get("tabId")) == str(tabId)), None)
        if not tabDict:
            logger.warning("GET channels tabId=%s tab not found", tabId)
            return jsonify({"error": "Tab not found"}), 404
        pathsList = tabDict.get("paths") or []
        channelsList = scanChannelsForTab(pathsList, str(tabId))
        logger.info("GET channels tabId=%s count=%s", tabId, len(channelsList))
        iLimit = request.args.get("limit", default=50, type=int)
        iOffset = request.args.get("offset", default=0, type=int)
        iLimit = max(1, min(500, iLimit))
        iOffset = max(0, iOffset)
        total = len(channelsList)
        sliceList = channelsList[iOffset : iOffset + iLimit]
        return jsonify({
            "channels": sliceList,
            "total": total,
            "limit": iLimit,
            "offset": iOffset,
        })
