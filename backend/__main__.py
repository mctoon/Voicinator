# Python 3.x
"""Entry point for run.sh: starts the Flask inbox-queue app. Port from voicinator.toml."""
import logging

from backend.src.api.app import createApp
from backend.src.models.masterConfigModel import getServerPort

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")

if __name__ == "__main__":
    app = createApp()
    port = getServerPort()
    app.run(host="0.0.0.0", port=port, debug=False)
