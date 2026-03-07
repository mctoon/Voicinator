/**
 * Main inbox page: fetch tabs and channels (single tab for MVP), render channel list,
 * wire Move 3 / Move all / Explore; show feedback and empty state.
 */
(function () {
  const messageEl = document.getElementById('message');
  let currentTabId = null;
  let tabsCache = [];
  const limit = 50;
  let currentOffset = 0;

  function switchTab(tabId) {
    currentTabId = tabId;
    renderTabBar(tabsCache, currentTabId, switchTab);
    loadChannels(0);
  }

  function showMessage(text, isError) {
    if (!messageEl) return;
    messageEl.textContent = text;
    messageEl.className = 'message' + (isError ? ' error' : '');
  }

  async function loadTabs() {
    try {
      const data = await getTabs();
      const tabs = data.tabs || [];
      if (tabs.length === 0) {
        document.getElementById('channelList').innerHTML =
          '<p class="empty-state">No tabs configured. Create inbox_queue_config.toml (or set INBOX_CONFIG) with at least one tab and path(s). See inbox_queue_config.toml.example.</p>';
        document.getElementById('channelPagination').innerHTML = '';
        document.getElementById('tabsContainer').innerHTML = '';
        return;
      }
      tabsCache = tabs;
      currentTabId = tabs[0].tabId;
      renderTabBar(tabs, currentTabId, switchTab);
      loadChannels(0);
    } catch (e) {
      showMessage(e.message || 'Failed to load tabs', true);
    }
  }

  async function loadChannels(offset) {
    currentOffset = offset;
    if (currentTabId == null) return;
    try {
      const data = await getChannels(currentTabId, limit, offset);
      const channels = data.channels || [];
      const total = data.total ?? channels.length;
      renderChannelList(
        channels,
        total,
        data.limit ?? limit,
        data.offset ?? offset,
        (ch) => doMove(ch, 'move3'),
        (ch) => doMove(ch, 'moveAll'),
        (ch) => goExplore(ch)
      );
      showMessage('');
    } catch (e) {
      showMessage(e.message || 'Failed to load channels', true);
    }
  }

  async function doMove(channel, action) {
    const channelId = getChannelId(channel);
    try {
      showMessage('Moving…');
      const result = await postMove({
        action: action === 'move3' ? 'move3' : 'moveAll',
        tabId: currentTabId,
        channelId,
      });
      showMessage(`Moved ${result.movedCount} file(s).`);
      if (result.errors && result.errors.length) {
        showMessage(result.errors.join('; '), true);
      }
      loadChannels(currentOffset);
    } catch (e) {
      showMessage(e.message || 'Move failed', true);
    }
  }

  function goExplore(channel) {
    const channelId = getChannelId(channel);
    window.location.href = `/explorePage.html?tabId=${encodeURIComponent(currentTabId)}&channelId=${encodeURIComponent(channelId)}`;
  }

  window.inboxPageRef = { loadChannels };
  loadTabs();
})();
