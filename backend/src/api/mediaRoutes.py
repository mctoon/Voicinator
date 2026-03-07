# Python 3.x
"""GET /api/inbox/media?path=... — stream media with safe path validation and Range support."""
from __future__ import annotations

from pathlib import Path

from flask import Blueprint, request, Response, send_file

from backend.src.services.configService import getConfigPath, getTabs


def register(bp: Blueprint) -> None:
    @bp.route("/media", methods=["GET"])
    def streamMedia():
        sPath = request.args.get("path", "")
        if not sPath:
            return Response("path required", status=400)
        path = Path(sPath)
        if not path.is_file():
            return Response("Not found", status=404)
        sConfigPath = getConfigPath()
        tabsList = getTabs(sConfigPath)
        allowedBases: set[Path] = set()
        for t in tabsList:
            for p in (t.get("paths") or []):
                if p:
                    allowedBases.add(Path(p).resolve())
        try:
            pathResolved = path.resolve()
        except Exception:
            return Response("Invalid path", status=403)
        def underBase(p: Path, base: Path) -> bool:
            try:
                return str(p).startswith(str(base))
            except Exception:
                return False
        if not any(underBase(pathResolved, base) for base in allowedBases if base.exists()):
            return Response("Forbidden", status=403)
        rangeHeader = request.headers.get("Range")
        if rangeHeader:
            return send_file(
                pathResolved,
                mimetype=None,
                as_attachment=False,
                conditional=True,
            )
        return send_file(pathResolved, mimetype=None, as_attachment=False)
