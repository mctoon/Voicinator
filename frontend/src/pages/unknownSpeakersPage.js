/**
 * Unknown speakers page: list files in step 5, load segments, play segment, resolve (existing/new/placeholder).
 * When all segments resolved, backend auto-moves file to Videos; no separate button required.
 */
(function () {
  const fileListEl = document.getElementById('fileList');
  const segmentSectionEl = document.getElementById('segmentSection');
  const segmentListEl = document.getElementById('segmentList');
  const segmentAudioEl = document.getElementById('segmentAudio');
  const existingSpeakerSelect = document.getElementById('existingSpeakerSelect');
  const newSpeakerNameEl = document.getElementById('newSpeakerName');
  const placeholderNameEl = document.getElementById('placeholderName');
  const resolveBtn = document.getElementById('resolveBtn');
  const messageEl = document.getElementById('message');

  let currentMediaId = null;
  let currentSegmentId = null;
  let speakersList = [];

  function showMessage(text, isError) {
    messageEl.textContent = text || '';
    messageEl.className = 'message' + (isError ? ' error' : '');
  }

  function renderFileList(items) {
    if (!items || items.length === 0) {
      fileListEl.innerHTML = '<p>No files in unknown-speakers step.</p>';
      return;
    }
    fileListEl.innerHTML = items.map(function (item) {
      const name = (item.mediaPath && item.mediaPath.split('/').pop()) || item.mediaId || 'Unknown';
      return '<button type="button" class="file-item" data-media-id="' + escapeHtml(item.mediaId) + '">' + escapeHtml(name) + '</button>';
    }).join('');
    fileListEl.querySelectorAll('.file-item').forEach(function (btn) {
      btn.addEventListener('click', function () {
        selectFile(btn.dataset.mediaId);
      });
    });
  }

  function escapeHtml(s) {
    if (s == null) return '';
    const div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }

  function renderSegmentList(segments) {
    if (!segments || segments.length === 0) {
      segmentListEl.innerHTML = '<p>No segments.</p>';
      return;
    }
    segmentListEl.innerHTML = segments.map(function (seg) {
      const resolved = seg.speakerId ? ' resolved' : '';
      return '<button type="button" class="segment-item' + resolved + '" data-segment-id="' + escapeHtml(seg.segmentId) + '" data-start="' + seg.start + '" data-end="' + seg.end + '">' +
        escapeHtml(seg.segmentId) + ' ' + seg.start.toFixed(1) + '–' + seg.end.toFixed(1) + (seg.speakerId ? ' (' + escapeHtml(seg.speakerId) + ')' : '') + '</button>';
    }).join('');
    segmentListEl.querySelectorAll('.segment-item').forEach(function (btn) {
      btn.addEventListener('click', function () {
        selectSegment(btn.dataset.segmentId, parseFloat(btn.dataset.start), parseFloat(btn.dataset.end));
      });
    });
  }

  function selectFile(mediaId) {
    currentMediaId = mediaId;
    currentSegmentId = null;
    segmentSectionEl.style.display = 'block';
    segmentListEl.innerHTML = '';
    segmentAudioEl.src = '';
    showMessage('Loading segments…');
    getSegments(mediaId)
      .then(function (data) {
        renderSegmentList(data.segments);
        showMessage('');
      })
      .catch(function (e) {
        showMessage(e.message, true);
      });
    loadSpeakersForSelect();
  }

  function selectSegment(segmentId, start, end) {
    currentSegmentId = segmentId;
    segmentListEl.querySelectorAll('.segment-item').forEach(function (el) {
      el.classList.toggle('selected', el.dataset.segmentId === segmentId);
    });
    const url = getSegmentAudioUrl(currentMediaId, segmentId);
    segmentAudioEl.src = url;
    segmentAudioEl.load();
  }

  function loadSpeakersForSelect() {
    getSpeakers()
      .then(function (data) {
        speakersList = data.speakers || [];
        existingSpeakerSelect.innerHTML = '<option value="">-- Select --</option>' +
          speakersList.map(function (s) {
            return '<option value="' + escapeHtml(s.id) + '">' + escapeHtml(s.name || s.id) + '</option>';
          }).join('');
      })
      .catch(function () {
        existingSpeakerSelect.innerHTML = '<option value="">-- Select --</option>';
      });
  }

  function getResolutionBody() {
    const resolution = document.querySelector('input[name="resolution"]:checked');
    const res = resolution ? resolution.value : '';
    if (res === 'existing') {
      const speakerId = existingSpeakerSelect.value;
      if (!speakerId) return null;
      return { mediaId: currentMediaId, segmentId: currentSegmentId, resolution: 'existing', speakerId: speakerId };
    }
    if (res === 'new') {
      const name = newSpeakerNameEl.value.trim();
      if (!name) return null;
      return { mediaId: currentMediaId, segmentId: currentSegmentId, resolution: 'new', name: name };
    }
    if (res === 'placeholder') {
      const name = placeholderNameEl.value.trim();
      if (!name) return null;
      return { mediaId: currentMediaId, segmentId: currentSegmentId, resolution: 'placeholder', name: name };
    }
    return null;
  }

  resolveBtn.addEventListener('click', function () {
    if (!currentMediaId || !currentSegmentId) {
      showMessage('Select a segment first.', true);
      return;
    }
    const body = getResolutionBody();
    if (!body) {
      showMessage('Choose resolution type and fill the field.', true);
      return;
    }
    showMessage('Resolving…');
    postResolve(body)
      .then(function () {
        showMessage('Resolved. Reloading segments…');
        return getSegments(currentMediaId);
      })
      .then(function (data) {
        renderSegmentList(data.segments);
        showMessage('Resolved. When all segments are resolved, the file will move to Videos automatically.');
        const allResolved = data.segments.length > 0 && data.segments.every(function (s) { return s.speakerId; });
        if (allResolved) {
          showMessage('All segments resolved. File will move to Videos automatically.');
          setTimeout(function () {
            loadFiles();
            segmentSectionEl.style.display = 'none';
          }, 1500);
        }
      })
      .catch(function (e) {
        showMessage(e.message, true);
      });
  });

  function loadFiles() {
    showMessage('Loading…');
    getSpeakersFiles()
      .then(function (data) {
        renderFileList(data.items);
        showMessage(data.total === 0 ? 'No files in unknown-speakers step.' : '');
      })
      .catch(function (e) {
        showMessage(e.message, true);
      });
  }

  loadFiles();
})();
