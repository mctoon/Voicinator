# Python 3.x
"""GET /api/inbox/media?path=... — stream media with safe path validation and Range support."""
from __future__ import annotations

import logging
import mimetypes
from pathlib import Path

from flask import Blueprint, request, Response, send_file

from backend.src.services.configService import getConfigPath, getTabs

logger = logging.getLogger(__name__)


def _mimetypeForPath(path: Path) -> str | None:
    """Guess mimetype from file extension for streaming."""
    guess, _ = mimetypes.guess_type(str(path), strict=False)
    return guess


def register(bp: Blueprint) -> None:
    @bp.route("/media", methods=["GET"])
    def streamMedia():
        sPath = request.args.get("path", "")
        logger.info("Media request: path=%s", sPath)
        if not sPath:
            logger.warning("Media request rejected: path required")
            return Response("path required", status=400)
        path = Path(sPath)
        if not path.is_file():
            logger.warning("Media request rejected: not a file path=%s", sPath)
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
        except Exception as e:
            logger.warning("Media request rejected: invalid path path=%s error=%s", sPath, e)
            return Response("Invalid path", status=403)

        def underBase(p: Path, base: Path) -> bool:
            try:
                return str(p).startswith(str(base))
            except Exception:
                return False

        if not any(underBase(pathResolved, base) for base in allowedBases if base.exists()):
            logger.warning("Media request rejected: path not under allowed bases path=%s allowed=%s", str(pathResolved), [str(b) for b in allowedBases])
            return Response("Forbidden", status=403)

        mimetype = _mimetypeForPath(pathResolved)
        logger.info("Serving media path=%s mimetype=%s", str(pathResolved), mimetype)
        return send_file(
            pathResolved,
            mimetype=mimetype,
            as_attachment=False,
            conditional=True,
        )
