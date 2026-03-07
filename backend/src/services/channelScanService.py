# Python 3.x
"""
Channel scan: given tab/paths, scan for dirs that have "Videos not transcribed" (inbox).
Eligibility requires only the inbox folder; queue path is derived and created on move if missing.
Support one or two paths per tab; when two paths, merge channels and set isSource.
"""
from __future__ import annotations

from pathlib import Path

INBOX_DIR = "Videos not transcribed"
QUEUE_DIR = "Videos 1 to be transcribed"


def scanChannelsForTab(pathsList: list[str], sTabId: str) -> list[dict]:
    """
    Scan one or two base paths for channel folders. A channel is included if it has
    INBOX_DIR; QUEUE_DIR need not exist (it is created on move). When two paths,
    merge channels and set isSource. Returns list of channel dicts: channelName,
    basePath, inboxPath, queuePath, isSource, tabId.
    """
    seenNames: set[str] = set()
    resultList: list[dict] = []
    isTwoPaths = len(pathsList) >= 2
    sPathSource = pathsList[0] if pathsList else ""
    sPathDest = pathsList[1] if len(pathsList) > 1 else ""

    for iPath, sBase in enumerate(pathsList):
        if not sBase:
            continue
        basePath = Path(sBase)
        if not basePath.is_dir():
            continue
        bIsSource = isTwoPaths and (sBase == sPathSource)
        for entry in basePath.iterdir():
            if not entry.is_dir():
                continue
            sChannelName = entry.name
            inboxPath = entry / INBOX_DIR
            if not inboxPath.is_dir():
                continue
            queuePath = entry / QUEUE_DIR
            key = f"{sBase}:{sChannelName}"
            if key in seenNames:
                continue
            seenNames.add(key)
            sQueuePath = str(queuePath)
            if bIsSource and sPathDest:
                destQueuePath = Path(sPathDest) / sChannelName / QUEUE_DIR
                sQueuePath = str(destQueuePath)
            resultList.append({
                "channelName": sChannelName,
                "basePath": sBase,
                "inboxPath": str(inboxPath),
                "queuePath": sQueuePath,
                "isSource": bIsSource,
                "tabId": sTabId,
            })
    return resultList


def getChannelId(channelDict: dict) -> str:
    """Stable channel id: basePath + channel name."""
    return f"{channelDict.get('basePath', '')}:{channelDict.get('channelName', '')}"
