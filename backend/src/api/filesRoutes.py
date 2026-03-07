# Python 3.x
"""GET /api/inbox/tabs/<tabId>/channels/<channelId>/files — paginated file list."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from backend.src.services.configService import getConfigPath, getTabs
from backend.src.services.channelScanService import scanChannelsForTab, getChannelId
from backend.src.services.fileListService import listMediaFiles


def register(bp: Blueprint) -> None:
    @bp.route("/tabs/<tabId>/channels/<channelId>/files", methods=["GET"])
    def getFilesRoute(tabId, channelId):
        sConfigPath = getConfigPath()
        tabsList = getTabs(sConfigPath)
        tabDict = next((t for t in tabsList if str(t.get("tabId")) == str(tabId)), None)
        if not tabDict:
            return jsonify({"error": "Tab not found"}), 404
        pathsList = tabDict.get("paths") or []
        channelsList = scanChannelsForTab(pathsList, str(tabId))
        channelDict = next((c for c in channelsList if getChannelId(c) == channelId), None)
        if not channelDict:
            return jsonify({"error": "Channel not found"}), 404
        sInboxPath = channelDict.get("inboxPath") or ""
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
