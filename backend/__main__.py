# Python 3.x
"""Entry point for run.sh: starts the Flask inbox-queue app."""
import logging

from backend.src.api.app import createApp

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")

if __name__ == "__main__":
    app = createApp()
    app.run(host="0.0.0.0", port=8027, debug=False)
