/**
 * Tab bar: one tab per item from GET /api/inbox/tabs; tab label = tabName or default.
 */
function renderTabBar(tabs, selectedTabId, onTabChange) {
  const container = document.getElementById('tabsContainer');
  if (!container) return;
  container.innerHTML = '';
  if (!tabs || tabs.length === 0) return;
  const bar = document.createElement('div');
  bar.className = 'tab-bar';
  tabs.forEach((tab) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'tab-btn' + (tab.tabId === selectedTabId ? ' active' : '');
    btn.textContent = tab.tabName || tab.tabId || 'Tab';
    btn.dataset.tabId = tab.tabId;
    btn.addEventListener('click', () => onTabChange(tab.tabId));
    bar.appendChild(btn);
  });
  container.appendChild(bar);
}
