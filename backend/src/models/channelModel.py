# Python 3.x
"""
ChannelFolder DTO (dict shape) matching API contract: channelName, basePath, inboxPath,
queuePath, isSource, tabId.
"""
from __future__ import annotations


def channelToDict(sChannelName: str, sBasePath: str, sInboxPath: str, sQueuePath: str,
                  bIsSource: bool, sTabId: str) -> dict:
    """Build channel dict for API response per contracts/inbox-queue-api.md."""
    return {
        "channelName": sChannelName,
        "basePath": sBasePath,
        "inboxPath": sInboxPath,
        "queuePath": sQueuePath,
        "isSource": bIsSource,
        "tabId": sTabId,
    }


def getChannelIdFromDict(channelDict: dict) -> str:
    """Stable channel id: basePath + channel name."""
    return f"{channelDict.get('basePath', '')}:{channelDict.get('channelName', '')}"
