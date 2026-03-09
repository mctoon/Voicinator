# Python 3.x
"""Entry point for run.sh: starts the Flask inbox-queue app. Port and log file from voicinator.toml."""
from backend.src.api.app import createApp
from backend.src.loggingConfig import configureLogging
from backend.src.models.masterConfigModel import getServerPort
from backend.src.services.pipelineAutoRunService import startAutoRunLoop

if __name__ == "__main__":
    configureLogging()
    app = createApp()
    startAutoRunLoop()
    port = getServerPort()
    app.run(host="0.0.0.0", port=port, debug=False)
