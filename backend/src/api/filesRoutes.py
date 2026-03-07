# Python 3.x
"""GET /api/inbox/tabs/<tabId>/files?channelId=... — paginated file list. channelId in query to avoid slashes in path."""
from __future__ import annotations

import logging
from pathlib import Path

from flask import Blueprint, jsonify, request

from backend.src.services.configService import getConfigPath, getTabs
from backend.src.services.channelScanService import scanChannelsForTab, getChannelId
from backend.src.services.fileListService import listMediaFiles

logger = logging.getLogger(__name__)


def _normalizeChannelId(c: dict) -> str:
    """Stable channel id; normalize base path for comparison."""
    base = (c.get("basePath") or "").strip()
    if base:
        try:
            base = str(Path(base).resolve())
        except Exception:
            pass
    return f"{base}:{c.get('channelName', '')}"


def register(bp: Blueprint) -> None:
    @bp.route("/tabs/<tabId>/files", methods=["GET"])
    def getFilesRoute(tabId):
        channelId = request.args.get("channelId", "").strip()
        if not channelId:
            return jsonify({"error": "channelId required"}), 400
        sConfigPath = getConfigPath()
        tabsList = getTabs(sConfigPath)
        tabDict = next((t for t in tabsList if str(t.get("tabId")) == str(tabId)), None)
        if not tabDict:
            return jsonify({"error": "Tab not found"}), 404
        pathsList = tabDict.get("paths") or []
        channelsList = scanChannelsForTab(pathsList, str(tabId))
        channelIdNorm = None
        if ":" in channelId:
            pathPart, namePart = channelId.split(":", 1)
            try:
                channelIdNorm = f"{Path(pathPart).resolve()}:{namePart}"
            except Exception:
                channelIdNorm = channelId
        else:
            channelIdNorm = channelId
        def matches(c):
            if getChannelId(c) == channelId:
                return True
            if channelIdNorm and _normalizeChannelId(c) == channelIdNorm:
                return True
            return False
        channelDict = next((c for c in channelsList if matches(c)), None)
        if not channelDict:
            logger.warning("GET files tabId=%s channelId=%s channel not found", tabId, channelId)
            return jsonify({"error": "Channel not found"}), 404
        sInboxPath = channelDict.get("inboxPath") or ""
        logger.info("GET files tabId=%s channelId=%s inboxPath=%s", tabId, channelId, sInboxPath)
        iLimit = request.args.get("limit", default=100, type=int)
        iOffset = request.args.get("offset", default=0, type=int)
        iLimit = max(1, min(1000, iLimit))
        iOffset = max(0, iOffset)
        filesList, iTotal = listMediaFiles(sInboxPath, iLimit=iLimit, iOffset=iOffset)
        out = [
            {
                "filePath": f.get("filePath"),
                "displayName": f.get("displayName"),
                "pairedFolderPath": f.get("pairedFolderPath"),
                "durationSeconds": f.get("durationSeconds"),
            }
            for f in filesList
        ]
        return jsonify({"files": out, "total": iTotal, "limit": iLimit, "offset": iOffset})
