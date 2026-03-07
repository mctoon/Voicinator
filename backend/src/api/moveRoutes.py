# Python 3.x
"""POST /api/inbox/move — move3, moveAll, queueSelected."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from backend.src.services.configService import getConfigPath, getTabs
from backend.src.services.channelScanService import scanChannelsForTab, getChannelId
from backend.src.services.fileListService import listMediaFiles
from backend.src.services.moveService import moveBatch


def register(bp: Blueprint) -> None:
    @bp.route("/move", methods=["POST"])
    def moveRoute():
        data = request.get_json() or {}
        action = (data.get("action") or "").strip().lower()
        tabId = data.get("tabId")
        channelId = data.get("channelId")
        filePaths = data.get("filePaths") or []

        if not action or action not in ("move3", "moveall", "queueselected"):
            return jsonify({"error": "Invalid action"}), 400
        if not tabId:
            return jsonify({"error": "tabId required"}), 400
        if action == "queueselected" and not filePaths:
            return jsonify({"error": "filePaths required for queueSelected"}), 400

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

        sQueuePath = channelDict.get("queuePath") or ""
        if not sQueuePath:
            return jsonify({"success": False, "movedCount": 0, "errors": ["No queue path"]}), 200

        if action == "queueselected":
            sInboxPath = channelDict.get("inboxPath", "")
            filesList, _ = listMediaFiles(sInboxPath, iLimit=10000, iOffset=0)
            pathSet = set(filePaths)
            toMove = [f for f in filesList if f.get("filePath") in pathSet]
            iMoved, errorsList = moveBatch(toMove, sQueuePath)
            return jsonify({"success": len(errorsList) == 0, "movedCount": iMoved, "errors": errorsList})

        filesList, iTotal = listMediaFiles(channelDict.get("inboxPath", ""), iLimit=10000, iOffset=0)
        if action == "move3":
            toMove = filesList[:3]
        else:
            toMove = filesList
        iMoved, errorsList = moveBatch(toMove, sQueuePath)
        return jsonify({"success": len(errorsList) == 0, "movedCount": iMoved, "errors": errorsList})
