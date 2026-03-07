# Python 3.x
"""
Flask app and API route structure: blueprint for /api/inbox and error handling (400, 404, 500).
"""
from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify

from backend.src.api import tabsRoutes, channelsRoutes, moveRoutes, filesRoutes, mediaRoutes

# Static files: repo root frontend/src (parent of backend/src/api -> 3 levels up from api/)
_STATIC_ROOT = Path(__file__).resolve().parents[3] / "frontend" / "src"


def createApp() -> Flask:
    """Create and configure the Flask app; register blueprints."""
    app = Flask(__name__, static_folder=str(_STATIC_ROOT), static_url_path="")
    app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024

    inboxBp = __createInboxBlueprint()
    app.register_blueprint(inboxBp, url_prefix="/api/inbox")

    @app.errorhandler(400)
    def badRequest(err):
        return jsonify({"error": str(err.description) if hasattr(err, "description") else "Bad request"}), 400

    @app.errorhandler(404)
    def notFound(err):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def serverError(err):
        return jsonify({"error": "Internal server error"}), 500

    @app.route("/")
    def index():
        return app.send_static_file("pages/inboxPage.html")

    @app.route("/inbox")
    def inbox():
        return app.send_static_file("pages/inboxPage.html")

    @app.route("/explorePage.html")
    def explorePage():
        return app.send_static_file("pages/explorePage.html")

    return app


def __createInboxBlueprint():
    from flask import Blueprint
    bp = Blueprint("inbox", __name__)
    tabsRoutes.register(bp)
    channelsRoutes.register(bp)
    moveRoutes.register(bp)
    filesRoutes.register(bp)
    mediaRoutes.register(bp)
    return bp
