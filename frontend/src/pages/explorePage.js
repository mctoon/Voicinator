/**
 * Explore view: fetch files for tabId/channelId, show file list with checkboxes,
 * Queue selected -> POST move queueSelected; Back does not call move API.
 */
(function () {
  const params = new URLSearchParams(window.location.search);
  const tabId = params.get('tabId');
  const channelId = params.get('channelId');
  const messageEl = document.getElementById('message');
  let selectedPaths = [];
  let currentOffset = 0;
  const limit = 100;

  function showMessage(text, isError) {
    if (!messageEl) return;
    messageEl.textContent = text;
    messageEl.className = 'message' + (isError ? ' error' : '');
  }

  document.getElementById('backBtn').addEventListener('click', () => {
    window.location.href = '/';
  });

  const mediaSubpanelApi = initMediaSubpanel('mediaSubpanel');

  function onSelectionChange(filePath, checked) {
    if (checked) selectedPaths.push(filePath);
    else selectedPaths = selectedPaths.filter(p => p !== filePath);
  }

  function onFileSelect(file) {
    if (mediaSubpanelApi && file && file.filePath) {
      mediaSubpanelApi.setMediaUrl(mediaUrl(file.filePath));
    }
  }

  async function loadFiles(offset) {
    currentOffset = offset;
    if (!tabId || !channelId) {
      showMessage('Missing tabId or channelId', true);
      return;
    }
    try {
      const data = await getFiles(tabId, channelId, limit, offset);
      const files = data.files || [];
      renderFileList(files, selectedPaths, onSelectionChange, onFileSelect);
      showMessage('');
    } catch (e) {
      showMessage(e.message || 'Failed to load files', true);
    }
  }

  async function queueSelected() {
    if (selectedPaths.length === 0) {
      showMessage('Select at least one file.', true);
      return;
    }
    try {
      showMessage('Queuing…');
      const result = await postMove({
        action: 'queueSelected',
        tabId,
        channelId,
        filePaths: selectedPaths,
      });
      showMessage(`Queued ${result.movedCount} file(s).`);
      selectedPaths = [];
      loadFiles(currentOffset);
    } catch (e) {
      showMessage(e.message || 'Queue failed', true);
    }
  }

  document.getElementById('queueSelectedBtn').addEventListener('click', queueSelected);
  loadFiles(0);
})();
