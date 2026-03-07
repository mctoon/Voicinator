/**
 * File list with selection (checkboxes) and "Queue selected" button.
 */
function renderFileList(files, selectedPaths, onSelectionChange, onFileSelect) {
  const container = document.getElementById('fileList');
  const queueBtn = document.getElementById('queueSelectedBtn');
  if (!container) return;
  container.innerHTML = '';
  if (!files || files.length === 0) {
    container.innerHTML = '<p class="empty-state">No media files in this channel inbox.</p>';
    if (queueBtn) queueBtn.style.display = 'none';
    return;
  }
  if (queueBtn) queueBtn.style.display = 'inline-block';
  const set = new Set(selectedPaths || []);
  const ul = document.createElement('ul');
  ul.className = 'file-list';
  files.forEach((f) => {
    const li = document.createElement('li');
    li.className = 'file-item';
    const cb = document.createElement('input');
    cb.type = 'checkbox';
    cb.checked = set.has(f.filePath);
    cb.dataset.path = f.filePath;
    cb.addEventListener('change', () => onSelectionChange(f.filePath, cb.checked));
    const label = document.createElement('label');
    label.textContent = f.displayName || f.filePath;
    label.prepend(cb);
    li.appendChild(label);
    if (onFileSelect) {
      li.style.cursor = 'pointer';
      li.addEventListener('click', (ev) => { if (ev.target !== cb) onFileSelect(f); });
    }
    ul.appendChild(li);
  });
  container.appendChild(ul);
}
