# Python 3.x
"""
LLM client for summarization: Ollama (local) and OpenAI-compatible remote.
Calls one completion with system/user message and returns plain text.
"""
from __future__ import annotations

import json
import logging
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)

OLLAMA_DEFAULT_BASE = "http://localhost:11434"


def complete(llmDict: dict[str, Any], sSystemPrompt: str, sUserPrompt: str, sModel: str | None = None) -> str:
    """
    Run one completion; return generated text. Raises on error.
    llmDict: name, type (ollama|remote), baseUrl, optional apiKey, optional model.
    """
    sType = (llmDict.get("type") or "").strip().lower()
    if sType == "ollama":
        return _completeOllama(llmDict, sSystemPrompt, sUserPrompt, sModel)
    if sType == "remote":
        return _completeRemote(llmDict, sSystemPrompt, sUserPrompt, sModel)
    raise ValueError(f"Unknown LLM type: {sType}")


def testRemoteLlm(sBaseUrl: str, sApiKey: str | None = None, sModel: str | None = None) -> None:
    """
    Test a remote (OpenAI-compatible) LLM with a minimal request.
    Raises on failure (connection, auth, or invalid response).
    """
    d = {"type": "remote", "baseUrl": sBaseUrl.strip()}
    if sApiKey:
        d["apiKey"] = sApiKey.strip()
    d["model"] = (sModel or "").strip() or "gpt-4"
    _completeRemote(d, "You are helpful.", "Say OK", None)


def _completeOllama(
    llmDict: dict, sSystemPrompt: str, sUserPrompt: str, sModel: str | None,
) -> str:
    """Ollama: POST /api/generate or /api/chat with prompt."""
    baseUrl = (llmDict.get("baseUrl") or "").strip() or OLLAMA_DEFAULT_BASE
    model = sModel or (llmDict.get("model") or "").strip() or "llama3.2"
    url = f"{baseUrl.rstrip('/')}/api/chat"
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": sSystemPrompt},
            {"role": "user", "content": sUserPrompt},
        ],
        "stream": False,
    }
    return _postJson(url, body, headers=None)


def _completeRemote(
    llmDict: dict, sSystemPrompt: str, sUserPrompt: str, sModel: str | None,
) -> str:
    """
    OpenAI-compatible: use the official openai Python client so requests match OpenClaw and x.ai docs
    (same base_url, headers, and body shape). Avoids Cloudflare 1010 that can occur with raw urllib.
    """
    baseUrl = (llmDict.get("baseUrl") or "").strip()
    if not baseUrl:
        raise ValueError("remote LLM requires baseUrl")
    model = sModel or (llmDict.get("model") or "").strip() or "gpt-4"
    apiKey = (llmDict.get("apiKey") or "").strip() or None
    try:
        from openai import OpenAI
    except ImportError:
        logger.warning("openai package not installed; falling back to urllib for remote LLM")
        return _completeRemoteUrllib(llmDict, sSystemPrompt, sUserPrompt, sModel)
    client = OpenAI(
        api_key=apiKey or "not-set",
        base_url=baseUrl.rstrip("/"),
    )
    messages = [
        {"role": "system", "content": sSystemPrompt},
        {"role": "user", "content": sUserPrompt},
    ]
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=False,
    )
    content = (resp.choices[0].message.content if resp.choices else None) or ""
    return content.strip()


def _completeRemoteUrllib(
    llmDict: dict, sSystemPrompt: str, sUserPrompt: str, sModel: str | None,
) -> str:
    """Fallback when openai package is not installed."""
    baseUrl = (llmDict.get("baseUrl") or "").strip()
    model = sModel or (llmDict.get("model") or "").strip() or "gpt-4"
    url = f"{baseUrl.rstrip('/')}/chat/completions"
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": sSystemPrompt},
            {"role": "user", "content": sUserPrompt},
        ],
        "stream": False,
    }
    headers = {"Content-Type": "application/json"}
    if llmDict.get("apiKey"):
        headers["Authorization"] = f"Bearer {llmDict['apiKey']}"
    return _postJson(url, body, headers=headers)


def _postJson(url: str, body: dict, headers: dict | None) -> str:
    """POST JSON body; parse JSON response and return content from first choice (OpenAI shape) or message (Ollama)."""
    data = json.dumps(body).encode("utf-8")
    reqHeaders = {"Content-Type": "application/json", **(headers or {})}
    req = urllib.request.Request(url, data=data, headers=reqHeaders, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            respData = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        bodyRead = e.read().decode("utf-8") if e.fp else ""
        logger.exception("LLM request failed: %s %s", e.code, bodyRead)
        errMsg = f"LLM request failed: {e.code} {bodyRead}"
        if e.code == 403 and "1010" in bodyRead:
            errMsg += " (Cloudflare 1010: request may be blocked; try standard User-Agent or check network/proxy.)"
        raise RuntimeError(errMsg) from e
    except OSError as e:
        logger.exception("LLM request error: %s", e)
        raise RuntimeError(f"LLM request error: {e}") from e
    try:
        out = json.loads(respData)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"LLM response not JSON: {e}") from e
    # OpenAI shape: choices[0].message.content
    if isinstance(out, dict) and "choices" in out and out["choices"]:
        msg = out["choices"][0].get("message") or {}
        if isinstance(msg.get("content"), str):
            return msg["content"].strip()
    # Ollama chat shape: message.content
    if isinstance(out, dict) and "message" in out:
        msg = out["message"]
        if isinstance(msg.get("content"), str):
            return msg["content"].strip()
    raise RuntimeError("LLM response missing content")
