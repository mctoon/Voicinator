/**
 * API client for inbox-queue backend. Base URL: /api/inbox
 */
const apiBase = '/api/inbox';

async function getTabs() {
  const r = await fetch(`${apiBase}/tabs`);
  if (!r.ok) throw new Error('Failed to fetch tabs');
  return r.json();
}

async function getChannels(tabId, limit = 50, offset = 0) {
  const params = new URLSearchParams({ limit, offset });
  const r = await fetch(`${apiBase}/tabs/${encodeURIComponent(tabId)}/channels?${params}`);
  if (!r.ok) throw new Error('Failed to fetch channels');
  return r.json();
}

async function postMove(body) {
  const r = await fetch(`${apiBase}/move`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.error || 'Move failed');
  return data;
}

async function getFiles(tabId, channelId, limit = 100, offset = 0) {
  const params = new URLSearchParams({ channelId, limit, offset });
  const r = await fetch(`${apiBase}/tabs/${encodeURIComponent(tabId)}/files?${params}`);
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.error || 'Failed to fetch files');
  return data;
}

function mediaUrl(path) {
  return `${apiBase}/media?path=${encodeURIComponent(path)}`;
}
