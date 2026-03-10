/**
 * Pipeline speakers (unknown-speakers) API. Base: /api/pipeline
 */
const pipelineBase = '/api/pipeline';

async function getSpeakersFiles() {
  const r = await fetch(`${pipelineBase}/speakers/files`);
  if (!r.ok) throw new Error('Failed to fetch files');
  return r.json();
}

async function getTranscript(mediaId) {
  const r = await fetch(`${pipelineBase}/speakers/files/${encodeURIComponent(mediaId)}/transcript`);
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.error || 'Transcript not found');
  return data;
}

function getMediaFileUrl(mediaId) {
  return `${pipelineBase}/speakers/files/${encodeURIComponent(mediaId)}/media`;
}

async function getSegments(mediaId) {
  const r = await fetch(`${pipelineBase}/speakers/files/${encodeURIComponent(mediaId)}/segments`);
  if (!r.ok) throw new Error('Failed to fetch segments');
  return r.json();
}

function getSegmentAudioUrl(mediaId, segmentId) {
  return `${pipelineBase}/speakers/segment-audio?mediaId=${encodeURIComponent(mediaId)}&segmentId=${encodeURIComponent(segmentId)}`;
}

async function postResolve(body) {
  const r = await fetch(`${pipelineBase}/speakers/resolve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.error || 'Resolve failed');
  return data;
}

async function getSpeakers() {
  const r = await fetch(`${pipelineBase}/speakers/speakers`);
  if (!r.ok) throw new Error('Failed to fetch speakers');
  return r.json();
}

async function postComplete(mediaId) {
  const r = await fetch(`${pipelineBase}/speakers/files/${encodeURIComponent(mediaId)}/complete`, {
    method: 'POST',
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.error || 'Complete failed');
  return data;
}

async function getCanComplete(mediaId) {
  const r = await fetch(`${pipelineBase}/speakers/files/${encodeURIComponent(mediaId)}/can-complete`);
  const data = await r.json().catch(() => ({}));
  return data.canComplete === true;
}

async function postMoveToVideos(mediaId) {
  const r = await fetch(`${pipelineBase}/speakers/files/${encodeURIComponent(mediaId)}/move-to-videos`, {
    method: 'POST',
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.error || 'Move failed');
  return data;
}
