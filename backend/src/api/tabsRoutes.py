# Python 3.x
"""GET /api/inbox/tabs — return tabId, tabName, pathCount per contract."""
from __future__ import annotations

from flask import Blueprint, jsonify

from backend.src.services.configService import getConfigPath, getTabs


def register(bp: Blueprint) -> None:
    @bp.route("/tabs", methods=["GET"])
    def getTabsRoute():
        sConfigPath = getConfigPath()
        tabsList = getTabs(sConfigPath)
        out = [
            {"tabId": t.get("tabId", ""), "tabName": t.get("tabName", ""), "pathCount": t.get("pathCount", 1)}
            for t in tabsList
        ]
        return jsonify({"tabs": out})
