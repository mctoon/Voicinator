/**
 * Renders channel list with per-channel actions: Move 3, Move all, Explore.
 * Uses pagination (limit/offset). getChannelId(channel) => basePath:channelName.
 */
function getChannelId(channel) {
  return `${channel.basePath}:${channel.channelName}`;
}

function renderChannelList(channels, total, limit, offset, onMove3, onMoveAll, onExplore) {
  const container = document.getElementById('channelList');
  if (!container) return;
  container.innerHTML = '';
  if (!channels || channels.length === 0) {
    container.innerHTML = '<p class="empty-state">No channel folders with inbox media found. Add channels under your configured paths with "Videos not transcribed" and "Videos 1 to be transcribed".</p>';
    return;
  }
  const ul = document.createElement('ul');
  ul.className = 'channel-list';
  channels.forEach((ch) => {
    const li = document.createElement('li');
    li.className = 'channel-item';
    const label = document.createElement('span');
    label.className = 'channel-name';
    label.textContent = ch.channelName;
    if (ch.isSource) label.classList.add('source');
    const actions = document.createElement('div');
    actions.className = 'channel-actions';
    const btn3 = document.createElement('button');
    btn3.type = 'button';
    btn3.textContent = 'Move 3';
    btn3.addEventListener('click', () => onMove3(ch));
    const btnAll = document.createElement('button');
    btnAll.type = 'button';
    btnAll.textContent = 'Move all';
    btnAll.addEventListener('click', () => onMoveAll(ch));
    const btnExplore = document.createElement('button');
    btnExplore.type = 'button';
    btnExplore.textContent = 'Explore';
    btnExplore.addEventListener('click', () => onExplore(ch));
    actions.append(btn3, btnAll, btnExplore);
    li.append(label, actions);
    ul.appendChild(li);
  });
  container.appendChild(ul);
  const pagination = document.getElementById('channelPagination');
  if (pagination) {
    const prev = offset > 0;
    const next = offset + channels.length < total;
    pagination.innerHTML = '';
    if (prev || next) {
      const prevBtn = document.createElement('button');
      prevBtn.type = 'button';
      prevBtn.textContent = 'Previous';
      prevBtn.disabled = !prev;
      prevBtn.addEventListener('click', () => window.inboxPageRef?.loadChannels(offset - limit));
      const nextBtn = document.createElement('button');
      nextBtn.type = 'button';
      nextBtn.textContent = 'Next';
      nextBtn.disabled = !next;
      nextBtn.addEventListener('click', () => window.inboxPageRef?.loadChannels(offset + limit));
      const info = document.createElement('span');
      info.textContent = `${offset + 1}-${Math.min(offset + limit, total)} of ${total}`;
      pagination.append(prevBtn, info, nextBtn);
    }
  }
}
