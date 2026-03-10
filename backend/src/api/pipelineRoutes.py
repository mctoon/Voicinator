# Python 3.x
"""
Pipeline API: GET config, GET discover, POST run, GET status per contracts/pipeline-api.md.
"""
from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request

from flask import Blueprint, jsonify, request

from backend.src.models.masterConfigModel import (
    getPipelineAutoProcessingEnabled,
    getPipelineChunkDurationDefaulted,
    getPipelineChunkDurationSeconds,
    getPipelineUnknownSpeakersStepOverride,
    getLlms,
    getSummarizations,
)
from backend.src.models.pipelineStepPlan import (
    getStepFolderOrder,
    getFinalFolderName,
    getUnknownSpeakersStepName,
)
from backend.src.services.pipelineDiscoveryService import (
    getPipelineBasePathsResolved,
    discoverMediaInStep1,
)
from backend.src.services.pipelineRunService import runOnePass, getStatusByStep

logger = logging.getLogger(__name__)


def _llmsForApi(llmsList: list[dict]) -> list[dict]:
    """Return LLM list for API; mask apiKey (omit or set to True if present)."""
    out: list[dict] = []
    for llm in llmsList:
        entry = dict(llm)
        if "apiKey" in entry and entry["apiKey"]:
            entry["apiKey"] = True
        out.append(entry)
    return out


def _validateSummarizationConfig(llmsList: list, summarizationsList: list) -> str | None:
    """Validate PUT body; return error string or None. Remote LLMs require provider and model; name is derived as provider:model."""
    from backend.src.models.llmProvidersModel import getProviderBaseUrl, loadLlmProviders
    providerNames = {p.get("name", "").strip() for p in loadLlmProviders() if p.get("name")}
    namesSeen: set[str] = set()
    for i, item in enumerate(llmsList):
        if not isinstance(item, dict):
            return f"llms[{i}] must be an object"
        sType = (str(item.get("type") or "").strip().lower())
        if sType not in ("ollama", "remote"):
            return f"llms[{i}]: type must be ollama or remote"
        if sType == "remote":
            provider = (item.get("provider") or "").strip()
            model = (item.get("model") or "").strip()
            if not provider:
                return f"llms[{i}]: provider is required for remote"
            if provider not in providerNames:
                return f"llms[{i}]: unknown provider '{provider}'"
            if not model:
                return f"llms[{i}]: model is required for remote"
            sName = (item.get("name") or "").strip() or f"{provider}:{model}"
        else:
            sName = (item.get("name") or "").strip()
            if not sName:
                return f"llms[{i}]: name is required for ollama"
        if sName in namesSeen:
            return f"llms: duplicate name '{sName}'"
        namesSeen.add(sName)
    llmNames = namesSeen
    for i, item in enumerate(summarizationsList):
        if not isinstance(item, dict):
            return f"summarizations[{i}] must be an object"
        sName = (item.get("name") or "").strip()
        sLlm = (item.get("llm") or "").strip()
        if not sName:
            return f"summarizations[{i}]: name is required"
        if not sLlm:
            return f"summarizations[{i}]: llm is required"
        if sLlm.lower().startswith("local:"):
            continue
        if sLlm not in llmNames:
            return f"summarizations[{i}]: llm '{sLlm}' must be 'Local:modelname' or a defined remote LLM"
    return None


def _fetchOllamaModels(baseUrl: str) -> list[str]:
    """Query Ollama GET /api/tags at baseUrl; return list of model names."""
    url = f"{baseUrl.rstrip('/')}/api/tags"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError) as e:
        logger.warning("Ollama tags request failed for %s: %s", url, e)
        return []
    models = data.get("models")
    if not isinstance(models, list):
        return []
    names: list[str] = []
    for m in models:
        if isinstance(m, dict) and m.get("name"):
            names.append(str(m["name"]).strip())
        elif isinstance(m, str):
            names.append(m.strip())
    return names


# Known Grok (x.ai) language model IDs when GET /v1/models and /v1/language-models return 403.
# x.ai often restricts model listing to Management API keys; chat keys can still use these models.
# From https://docs.x.ai/docs/models (text/language models only).
GROK_FALLBACK_MODEL_IDS = [
    "grok-4-1-fast-reasoning",
    "grok-4-1-fast-non-reasoning",
    "grok-4-fast-reasoning",
    "grok-4-fast-non-reasoning",
    "grok-code-fast-1",
    "grok-4-0709",
    "grok-3",
    "grok-3-mini",
]


def _parseModelsResponse(data: dict) -> list[dict]:
    """Extract list of { id: modelId } from OpenAI-style or x.ai response."""
    items = data.get("data") if isinstance(data, dict) else None
    if not isinstance(items, list):
        return []
    out: list[dict] = []
    for m in items:
        if isinstance(m, dict) and m.get("id"):
            out.append({"id": str(m["id"]).strip()})
    return out


def _isGrokProvider(provider: str, baseUrl: str) -> bool:
    """True if this is x.ai / Grok (use fallback model list when API returns 403)."""
    return provider.strip().lower() == "grok" or "api.x.ai" in (baseUrl or "")


def _fetchRemoteModels(baseUrl: str, apiKey: str, provider: str = "") -> tuple[list[dict], str | None]:
    """GET baseUrl/models (OpenAI-style). Returns (models, error). On success error is None."""
    base = baseUrl.rstrip("/")
    urlsToTry: list[str] = [f"{base}/models"]
    if _isGrokProvider(provider, base):
        urlsToTry.append(f"{base}/language-models")
    lastErr: str | None = None
    for url in urlsToTry:
        req = urllib.request.Request(url, method="GET")
        if apiKey:
            req.add_header("Authorization", f"Bearer {apiKey}")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            models = _parseModelsResponse(data) if isinstance(data, dict) else []
            return (models, None)
        except urllib.error.HTTPError as e:
            lastErr = f"{e.code} {e.reason}"
            if e.code == 403 and url == urlsToTry[0] and len(urlsToTry) > 1:
                continue  # try next URL
            if e.code == 403 and _isGrokProvider(provider, base):
                break  # use fallback list below instead of returning error
            logger.warning("Remote models request failed for %s: %s", url, e)
            return ([], lastErr)
        except (urllib.error.URLError, json.JSONDecodeError, OSError) as e:
            logger.warning("Remote models request failed for %s: %s", url, e)
            return ([], str(e))
    # All URLs failed (e.g. Grok 403 on both). For Grok, return static list so user can still pick a model.
    if _isGrokProvider(provider, base) and lastErr:
        logger.info("Using fallback Grok model list (API returned %s)", lastErr)
        return ([{"id": mid} for mid in GROK_FALLBACK_MODEL_IDS], None)
    return ([], lastErr or "Could not list models (tried allowed endpoints).")


def register(bp: Blueprint) -> None:
    @bp.route("/config", methods=["GET"])
    def getConfig():
        basePaths = getPipelineBasePathsResolved()
        stepFolders = getStepFolderOrder()
        override = getPipelineUnknownSpeakersStepOverride()
        unknownStep = getUnknownSpeakersStepName(override)
        llms = _llmsForApi(getLlms())
        summarizations = getSummarizations()
        return jsonify({
            "basePaths": basePaths,
            "stepFolders": stepFolders,
            "unknownSpeakersStepName": unknownStep,
            "finalFolderName": getFinalFolderName(),
            "chunkDurationSeconds": getPipelineChunkDurationSeconds(),
            "chunkDurationDefaulted": getPipelineChunkDurationDefaulted(),
            "llms": llms,
            "summarizations": summarizations,
        })

    @bp.route("/summarization-config", methods=["PUT"])
    def putSummarizationConfig():
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return jsonify({"error": "JSON body required"}), 400
        llmsList = body.get("llms")
        summarizationsList = body.get("summarizations")
        if not isinstance(llmsList, list) or not isinstance(summarizationsList, list):
            return jsonify({"error": "llms and summarizations must be arrays"}), 400
        err = _validateSummarizationConfig(llmsList, summarizationsList)
        if err:
            return jsonify({"error": err}), 400
        try:
            from backend.src.services.summarizationConfigService import writeSummarizationConfig
            writeSummarizationConfig(llmsList, summarizationsList)
        except (ValueError, OSError) as e:
            logger.exception("Failed to write summarization config: %s", e)
            return jsonify({"error": str(e)}), 500
        except Exception as e:
            logger.exception("Unexpected error writing summarization config: %s", e)
            return jsonify({"error": str(e)}), 500
        return jsonify({"ok": True})

    @bp.route("/ollama-models", methods=["GET"])
    def getOllamaModels():
        """Return list of model names from local Ollama instance (GET /api/tags)."""
        baseUrl = request.args.get("baseUrl", "").strip() or "http://localhost:11434"
        models = _fetchOllamaModels(baseUrl)
        return jsonify({"models": models})

    @bp.route("/llm-providers", methods=["GET"])
    def getLlmProviders():
        """Return list of remote LLM providers (name, baseUrl) from llm_providers.toml."""
        from backend.src.models.llmProvidersModel import loadLlmProviders
        providers = loadLlmProviders()
        return jsonify({"providers": providers})

    @bp.route("/remote-models", methods=["POST"])
    def postRemoteModels():
        """Fetch model list from a provider via GET /v1/models. Body: { provider, apiKey }."""
        body = request.get_json(silent=True) or {}
        provider = (body.get("provider") or "").strip()
        apiKey = (body.get("apiKey") or "").strip()
        if not provider:
            return jsonify({"error": "provider is required"}), 400
        from backend.src.models.llmProvidersModel import getProviderBaseUrl
        baseUrl = getProviderBaseUrl(provider)
        if not baseUrl:
            return jsonify({"error": f"Unknown provider: {provider}"}), 400
        models, fetchError = _fetchRemoteModels(baseUrl, apiKey, provider)
        out = {"models": models}
        if fetchError:
            out["error"] = fetchError
        return jsonify(out)

    @bp.route("/test-llm", methods=["POST"])
    def postTestLlm():
        """Test a remote LLM. Body: { provider, apiKey, model } (provider required; model optional). Returns { ok: true } or { error: ... }."""
        body = request.get_json(silent=True) or {}
        provider = (body.get("provider") or "").strip()
        baseUrl = (body.get("baseUrl") or "").strip()
        if not baseUrl and provider:
            from backend.src.models.llmProvidersModel import getProviderBaseUrl
            baseUrl = getProviderBaseUrl(provider) or ""
        if not baseUrl:
            return jsonify({"error": "provider (or baseUrl) is required"}), 400
        apiKey = (body.get("apiKey") or "").strip() or None
        model = (body.get("model") or "").strip() or None
        try:
            from backend.src.services.pipeline.llmClient import testRemoteLlm
            testRemoteLlm(baseUrl, apiKey, model)
        except Exception as e:
            logger.warning("Test LLM failed: %s", e)
            return jsonify({"error": str(e)}), 200
        return jsonify({"ok": True})

    @bp.route("/discover", methods=["GET"])
    def getDiscover():
        basePathFilter = request.args.get("basePath", "").strip() or None
        items = discoverMediaInStep1(basePathFilter)
        return jsonify({"items": items, "total": len(items)})

    @bp.route("/run", methods=["POST"])
    def postRun():
        if getPipelineAutoProcessingEnabled():
            return jsonify({
                "error": "Processing is automatic; no run trigger needed. Use discovery/status for visibility.",
            }), 410
        body = request.get_json(silent=True) or {}
        iLimit = body.get("limit")
        if iLimit is not None:
            try:
                iLimit = int(iLimit)
            except (TypeError, ValueError):
                iLimit = None
        result = runOnePass(iLimit)
        logger.info("POST pipeline/run result: %s", result)
        return jsonify(result)

    @bp.route("/status", methods=["GET"])
    def getStatus():
        byStep = getStatusByStep()
        return jsonify({"byStep": byStep})
