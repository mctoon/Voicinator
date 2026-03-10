/**
 * Unknown speakers page: list files in step 5; transcript in transcript.txt style (sections by speaker and time);
 * play/pause at bottom; clicking speaker name opens identify popup (list, filter, Enter to create, skip).
 */
(function () {
  const fileListEl = document.getElementById('fileList');
  const segmentSectionEl = document.getElementById('segmentSection');
  const transcriptPanelEl = document.getElementById('transcriptPanel');
  const fullMediaEl = document.getElementById('fullMedia');
  const completeBtn = document.getElementById('completeBtn');
  const messageEl = document.getElementById('message');
  const backToListBtn = document.getElementById('backToListBtn');
  const identifyPopupEl = document.getElementById('identifyPopup');
  const identifyFilterEl = document.getElementById('identifyFilter');
  const identifySpeakerListEl = document.getElementById('identifySpeakerList');
  const identifySkipBtn = document.getElementById('identifySkipBtn');
  const identifyCancelBtn = document.getElementById('identifyCancelBtn');

  let currentMediaId = null;
  let currentSegmentId = null;
  let currentSegments = [];
  let speakersList = [];

  function showMessage(text, isError) {
    messageEl.textContent = text || '';
    messageEl.className = 'message' + (isError ? ' error' : '');
  }

  function escapeHtml(s) {
    if (s == null) return '';
    const div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }

  function formatTime(seconds) {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return m + ':' + (s < 10 ? '0' : '') + s;
  }

  function renderFileList(items) {
    if (!items || items.length === 0) {
      fileListEl.innerHTML = '<p>No videos need speaker identification.</p>';
      return;
    }
    fileListEl.innerHTML = items.map(function (item) {
      const filename = (item.mediaPath && item.mediaPath.split('/').pop()) || item.mediaId || 'Unknown';
      const channel = item.channelName || '';
      const label = channel ? escapeHtml(channel) + ' — ' + escapeHtml(filename) : escapeHtml(filename);
      return '<button type="button" class="file-item" data-media-id="' + escapeHtml(item.mediaId) + '">' + label + '</button>';
    }).join('');
    fileListEl.querySelectorAll('.file-item').forEach(function (btn) {
      btn.addEventListener('click', function () {
        selectFile(btn.dataset.mediaId);
      });
    });
  }

  function updateCompleteButtonState(segments) {
    if (!completeBtn) return;
    const allResolved = segments && segments.length > 0 && segments.every(function (s) { return s.speakerId; });
    completeBtn.disabled = !allResolved;
  }

  /** Group words by segmentId for transcript.txt-style sections. */
  function groupWordsBySegment(words) {
    const bySegment = {};
    (words || []).forEach(function (w) {
      const segId = w.segmentId || '';
      if (!bySegment[segId]) bySegment[segId] = [];
      bySegment[segId].push(w);
    });
    return bySegment;
  }

  /**
   * Render transcript in transcript.txt style: sections labeled by speaker and time.
   * Speaker name/label is clickable when unresolved; clicking section words starts playback.
   */
  function renderTranscript(words, segments) {
    currentSegments = segments || [];
    if (!words || words.length === 0) {
      transcriptPanelEl.innerHTML = '<p>No transcript.</p>';
      updateCompleteButtonState(currentSegments);
      return;
    }
    const wordsBySegment = groupWordsBySegment(words);
    const segmentOrder = (segments || []).slice();
    const htmlParts = [];
    segmentOrder.forEach(function (seg) {
      const segId = seg.segmentId || '';
      const segWords = wordsBySegment[segId] || [];
      const startTime = seg.start != null ? seg.start : (segWords[0] && segWords[0].start) || 0;
      const timeStr = formatTime(startTime);
      const displayName = seg.speakerId || seg.label || segId || 'Speaker';
      const isResolved = !!seg.speakerId;
      const suggested = seg.suggestedSpeakerName ? ' (suggested: ' + escapeHtml(seg.suggestedSpeakerName) + ')' : '';
      const speakerLineClass = isResolved ? 'speaker-label resolved' : 'speaker-label';
      const resolvedMarker = isResolved ? ' <span class="resolved-marker">✓</span>' : '';
      const speakerHtml = '<span class="' + speakerLineClass + '" data-segment-id="' + escapeHtml(segId) + '" data-start="' + startTime + '" data-resolved="' + (isResolved ? '1' : '0') + '">' + escapeHtml(displayName) + suggested + resolvedMarker + '</span>';
      const line1 = speakerHtml + ' ' + timeStr;
      const wordsHtml = segWords.map(function (w) {
        const start = Number(w.start);
        const end = Number(w.end || start);
        return '<span class="section-word" role="button" tabindex="0" data-start="' + start + '" data-end="' + end + '">' + escapeHtml(w.word) + '</span>';
      }).join(' ');
      htmlParts.push('<div class="transcript-section" data-segment-id="' + escapeHtml(segId) + '">' +
        '<div class="speaker-line">' + line1 + '</div>' +
        '<div class="section-words" data-start="' + startTime + '">' + wordsHtml + '</div></div>');
    });
    transcriptPanelEl.innerHTML = htmlParts.join('\n');

    transcriptPanelEl.querySelectorAll('.speaker-label:not(.resolved)').forEach(function (el) {
      el.addEventListener('click', function () {
        const segId = el.dataset.segmentId;
        if (!segId) return;
        currentSegmentId = segId;
        openIdentifyPopup();
      });
    });
    transcriptPanelEl.querySelectorAll('.section-words').forEach(function (el) {
      el.addEventListener('click', function (e) {
        var start;
        if (e.target && e.target.classList && e.target.classList.contains('section-word')) {
          start = parseFloat(e.target.dataset.start);
        } else {
          start = parseFloat(el.dataset.start);
        }
        if (fullMediaEl.src && !isNaN(start)) {
          fullMediaEl.currentTime = start;
          fullMediaEl.play();
        }
      });
    });
    updateCompleteButtonState(currentSegments);
  }

  function openIdentifyPopup() {
    if (!identifyPopupEl) return;
    identifyPopupEl.style.display = 'flex';
    identifyFilterEl.value = '';
    renderIdentifySpeakerList('');
    identifyFilterEl.focus();
    identifyFilterEl.addEventListener('keydown', onIdentifyFilterKeydown);
    identifySpeakerListEl.addEventListener('click', onIdentifyListClick);
  }

  function closeIdentifyPopup() {
    if (!identifyPopupEl) return;
    identifyPopupEl.style.display = 'none';
    identifyFilterEl.removeEventListener('keydown', onIdentifyFilterKeydown);
    identifySpeakerListEl.removeEventListener('click', onIdentifyListClick);
  }

  function renderIdentifySpeakerList(filterText) {
    const q = (filterText || '').trim().toLowerCase();
    const filtered = q
      ? speakersList.filter(function (s) {
          const name = (s.name || s.id || '').toLowerCase();
          return name.indexOf(q) !== -1;
        })
      : speakersList.slice();
    identifySpeakerListEl.innerHTML = filtered.map(function (s) {
      const name = s.name || s.id || '';
      return '<div role="option" class="identify-option" data-speaker-id="' + escapeHtml(s.id) + '" data-speaker-name="' + escapeHtml(name) + '">' + escapeHtml(name) + '</div>';
    }).join('');
  }

  function onIdentifyFilterKeydown(e) {
    if (e.key === 'Enter') {
      e.preventDefault();
      const typed = (identifyFilterEl.value || '').trim();
      const optionEl = identifySpeakerListEl.querySelector('[role="option"]');
      const firstMatch = optionEl ? (optionEl.dataset.speakerName || '').trim() : '';
      if (typed && firstMatch && firstMatch.toLowerCase() === typed.toLowerCase()) {
        doResolveExisting(optionEl.dataset.speakerId);
        return;
      }
      if (typed && !speakersList.some(function (s) { return (s.name || s.id || '').trim().toLowerCase() === typed.toLowerCase(); })) {
        doResolveNew(typed);
        return;
      }
    }
  }

  function onIdentifyListClick(e) {
    const option = e.target.closest('[role="option"]');
    if (!option) return;
    const speakerId = option.dataset.speakerId;
    if (speakerId) doResolveExisting(speakerId);
  }

  function doResolveExisting(speakerId) {
    if (!currentMediaId || !currentSegmentId || !speakerId) return;
    showMessage('Resolving…');
    postResolve({ mediaId: currentMediaId, segmentId: currentSegmentId, resolution: 'existing', speakerId: speakerId })
      .then(function (data) {
        closeIdentifyPopup();
        showMessage(data.assignedName ? 'Resolved as ' + data.assignedName : 'Resolved.');
        return getTranscript(currentMediaId);
      })
      .then(function (data) {
        renderTranscript(data.words, data.segments);
        showMessage('Resolved. Complete identification when all segments are resolved.');
      })
      .catch(function (err) {
        showMessage(err.message, true);
      });
  }

  function doResolveNew(name) {
    if (!currentMediaId || !currentSegmentId || !name || !name.trim()) return;
    showMessage('Resolving…');
    postResolve({ mediaId: currentMediaId, segmentId: currentSegmentId, resolution: 'new', name: name.trim() })
      .then(function (data) {
        closeIdentifyPopup();
        showMessage(data.assignedName ? 'Resolved as ' + data.assignedName : 'Resolved.');
        return getTranscript(currentMediaId);
      })
      .then(function (data) {
        renderTranscript(data.words, data.segments);
        showMessage('Resolved. Complete identification when all segments are resolved.');
      })
      .catch(function (err) {
        showMessage(err.message, true);
      });
  }

  function doResolvePlaceholder() {
    if (!currentMediaId || !currentSegmentId) return;
    showMessage('Resolving…');
    postResolve({ mediaId: currentMediaId, segmentId: currentSegmentId, resolution: 'placeholder' })
      .then(function (data) {
        closeIdentifyPopup();
        showMessage(data.assignedName ? 'Resolved as ' + data.assignedName : 'Resolved.');
        return getTranscript(currentMediaId);
      })
      .then(function (data) {
        renderTranscript(data.words, data.segments);
        showMessage('Resolved. Complete identification when all segments are resolved.');
      })
      .catch(function (err) {
        showMessage(err.message, true);
      });
  }

  function selectFile(mediaId) {
    currentMediaId = mediaId;
    currentSegmentId = null;
    segmentSectionEl.style.display = 'block';
    transcriptPanelEl.innerHTML = '';
    fullMediaEl.src = '';
    showMessage('Loading transcript and segments…');
    fullMediaEl.src = getMediaFileUrl(mediaId);
    getSpeakers().then(function (data) {
      speakersList = data.speakers || [];
    }).catch(function () { speakersList = []; });
    getTranscript(mediaId)
      .then(function (data) {
        renderTranscript(data.words, data.segments);
        showMessage('');
      })
      .catch(function (e) {
        showMessage(e.message || 'Failed to load. Use "Back to list" to return.', true);
      });
  }

  if (backToListBtn) {
    backToListBtn.addEventListener('click', function () {
      segmentSectionEl.style.display = 'none';
      currentMediaId = null;
      currentSegmentId = null;
      loadFiles();
    });
  }

  if (completeBtn) {
    completeBtn.addEventListener('click', function () {
      if (!currentMediaId || completeBtn.disabled) return;
      showMessage('Completing…');
      postComplete(currentMediaId)
        .then(function () {
          showMessage('Done. Returning to list.');
          segmentSectionEl.style.display = 'none';
          currentMediaId = null;
          currentSegmentId = null;
          loadFiles();
        })
        .catch(function (e) {
          showMessage(e.message, true);
        });
    });
  }

  if (identifyFilterEl) {
    identifyFilterEl.addEventListener('input', function () {
      renderIdentifySpeakerList(identifyFilterEl.value);
    });
  }
  if (identifySkipBtn) {
    identifySkipBtn.addEventListener('click', function () {
      doResolvePlaceholder();
    });
  }
  if (identifyCancelBtn) {
    identifyCancelBtn.addEventListener('click', function () {
      closeIdentifyPopup();
    });
  }

  function loadFiles() {
    showMessage('Loading…');
    getSpeakersFiles()
      .then(function (data) {
        renderFileList(data.items);
        showMessage(data.total === 0 ? 'No videos need speaker identification.' : '');
      })
      .catch(function (e) {
        showMessage(e.message, true);
      });
  }

  loadFiles();
})();
