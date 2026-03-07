/**
 * Media subpanel: video/audio element with play/pause, volume, scrubber (seek), jump forward/back.
 * Accepts media URL (stream endpoint). Shows clear message when playback fails (unsupported format).
 */
const JUMP_SECONDS = 10;

function initMediaSubpanel(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return null;
  container.innerHTML = '';
  const wrap = document.createElement('div');
  wrap.className = 'media-subpanel';
  const mediaEl = document.createElement('div');
  mediaEl.className = 'media-player-wrap';
  const video = document.createElement('video');
  video.controls = true;
  video.preload = 'metadata';
  video.crossOrigin = 'anonymous';
  const msgEl = document.createElement('p');
  msgEl.className = 'media-unsupported';
  msgEl.style.display = 'none';
  mediaEl.append(video, msgEl);

  const controls = document.createElement('div');
  controls.className = 'media-controls';
  const playBtn = document.createElement('button');
  playBtn.type = 'button';
  playBtn.textContent = 'Play';
  const volLabel = document.createElement('label');
  volLabel.textContent = 'Volume ';
  const volInput = document.createElement('input');
  volInput.type = 'range';
  volInput.min = 0;
  volInput.max = 100;
  volInput.value = 100;
  const scrubLabel = document.createElement('label');
  scrubLabel.textContent = ' Seek ';
  const scrubInput = document.createElement('input');
  scrubInput.type = 'range';
  scrubInput.min = 0;
  scrubInput.max = 100;
  scrubInput.value = 0;
  const backBtn = document.createElement('button');
  backBtn.type = 'button';
  backBtn.textContent = '-10s';
  const fwdBtn = document.createElement('button');
  fwdBtn.type = 'button';
  fwdBtn.textContent = '+10s';
  controls.append(playBtn, volLabel, volInput, scrubLabel, scrubInput, backBtn, fwdBtn);

  wrap.append(mediaEl, controls);
  container.appendChild(wrap);

  video.addEventListener('play', () => { playBtn.textContent = 'Pause'; });
  video.addEventListener('pause', () => { playBtn.textContent = 'Play'; });
  video.addEventListener('error', () => {
    msgEl.textContent = 'Playback not supported for this format. You can still queue the file.';
    msgEl.style.display = 'block';
  });
  video.addEventListener('loadedmetadata', () => {
    msgEl.style.display = 'none';
    scrubInput.max = video.duration || 100;
  });

  playBtn.addEventListener('click', () => {
    if (video.paused) video.play();
    else video.pause();
  });
  volInput.addEventListener('input', () => {
    video.volume = volInput.value / 100;
  });
  scrubInput.addEventListener('input', () => {
    if (video.duration) video.currentTime = (scrubInput.value / 100) * video.duration;
  });
  video.addEventListener('timeupdate', () => {
    if (video.duration) scrubInput.value = (video.currentTime / video.duration) * 100;
  });
  backBtn.addEventListener('click', () => {
    video.currentTime = Math.max(0, video.currentTime - JUMP_SECONDS);
  });
  fwdBtn.addEventListener('click', () => {
    video.currentTime = Math.min(video.duration || 0, video.currentTime + JUMP_SECONDS);
  });

  return {
    setMediaUrl(url) {
      msgEl.style.display = 'none';
      msgEl.textContent = '';
      video.src = url || '';
      video.load();
    },
    clear() {
      video.src = '';
      msgEl.style.display = 'none';
      msgEl.textContent = '';
    },
  };
}
