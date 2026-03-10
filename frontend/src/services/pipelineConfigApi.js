/**
 * Pipeline config API: GET config (includes llms, summarizations), PUT summarization-config.
 * Base URL: /api/pipeline
 */
const pipelineApiBase = '/api/pipeline';

async function getPipelineConfig() {
  const r = await fetch(`${pipelineApiBase}/config`);
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.error || 'Failed to fetch pipeline config');
  return data;
}

async function putSummarizationConfig(body) {
  const r = await fetch(`${pipelineApiBase}/summarization-config`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.error || 'Failed to save config');
  return data;
}

async function getOllamaModels(baseUrl) {
  const url = baseUrl
    ? `${pipelineApiBase}/ollama-models?baseUrl=${encodeURIComponent(baseUrl)}`
    : `${pipelineApiBase}/ollama-models`;
  const r = await fetch(url);
  const data = await r.json().catch(() => ({}));
  if (!r.ok) return { models: [] };
  return Array.isArray(data.models) ? data : { models: [] };
}

async function getLlmProviders() {
  const r = await fetch(`${pipelineApiBase}/llm-providers`);
  const data = await r.json().catch(() => ({}));
  if (!r.ok) return { providers: [] };
  return Array.isArray(data.providers) ? data : { providers: [] };
}

async function fetchRemoteModels(provider, apiKey) {
  const r = await fetch(`${pipelineApiBase}/remote-models`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ provider, apiKey: apiKey || '' }),
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) return { models: [], error: data.error };
  return { models: Array.isArray(data.models) ? data.models : [], error: data.error };
}

async function testLlm(body) {
  const r = await fetch(`${pipelineApiBase}/test-llm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await r.json().catch(() => ({}));
  return { ok: r.ok, error: data.error, success: data.ok === true };
}

