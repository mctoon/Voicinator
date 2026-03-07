# Python 3.x
"""
Channel scan: given tab/paths, scan for dirs with both inbox and queue folders;
return ChannelFolder list; hide channels missing either path; support one or two paths per tab.
"""
from __future__ import annotations

from pathlib import Path

INBOX_DIR = "Videos not transcribed"
QUEUE_DIR = "Videos 1 to be transcribed"


def scanChannelsForTab(pathsList: list[str], sTabId: str) -> list[dict]:
    """
    Scan one or two base paths for channel folders. Each channel dir must contain
    both INBOX_DIR and QUEUE_DIR. When two paths, merge channels and set isSource.
    Returns list of channel dicts: channelName, basePath, inboxPath, queuePath, isSource, tabId.
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
            queuePath = entry / QUEUE_DIR
            if not inboxPath.is_dir() or not queuePath.is_dir():
                continue
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
