/**
 * Config page: Remote LLMs (provider dropdown, API key, fetch models, model dropdown; name = Provider:Model).
 * Summarization parts: LLM = Local:ModelName or remote name.
 */
(function () {
  let remoteLlmsList = [];
  let summarizationsList = [];
  let ollamaModelsList = [];
  let providersList = [];

  function showMessage(text, isError) {
    const el = document.getElementById('message');
    if (!el) return;
    el.textContent = text;
    el.style.color = isError ? '#c00' : '#060';
  }

  function loadConfig() {
    Promise.all([
      getPipelineConfig(),
      getOllamaModels().then((d) => (ollamaModelsList = d.models || [])),
      getLlmProviders().then((d) => (providersList = d.providers || [])),
    ])
      .then(([data]) => {
        const allLlms = Array.isArray(data.llms) ? data.llms : [];
        remoteLlmsList = allLlms.filter((x) => (x.type || '').toLowerCase() === 'remote').map((x) => ({ ...x }));
        summarizationsList = Array.isArray(data.summarizations)
          ? data.summarizations.map((x) => ({ ...x }))
          : [];
        summarizationsList.forEach((part) => {
          if ((part.llm || '').toLowerCase() === 'local') {
            part.llm = ollamaModelsList.length ? 'Local:' + ollamaModelsList[0] : (remoteLlmsList[0]?.name || '');
          }
          if (part.instructions != null && (part.systemPrompt == null && part.userPrompt == null)) {
            part.userPrompt = (part.instructions || '') + '\n\n{{TRANSCRIPT}}';
            part.systemPrompt = '';
          }
        });
        renderRemoteLlms();
        renderSummarizations();
      })
      .catch((e) => showMessage(e.message || 'Load failed', true));
  }

  function getLlmOptions() {
    const options = [];
    ollamaModelsList.forEach((m) => options.push({ value: 'Local:' + m, label: 'Local:' + m }));
    remoteLlmsList.forEach((l) => {
      const n = l.name || '';
      if (n) options.push({ value: n, label: n });
    });
    return options;
  }

  function renderRemoteLlms() {
    const container = document.getElementById('remoteLlmsContainer');
    if (!container) return;
    container.innerHTML = '';
    remoteLlmsList.forEach((llm, i) => {
      const div = document.createElement('div');
      div.className = 'config-row';
      const nameDisplay = document.createElement('span');
      nameDisplay.className = 'llm-name-display';
      nameDisplay.textContent = llm.name || (llm.provider && llm.model ? llm.provider + ':' + llm.model : '—');
      const providerSelect = document.createElement('select');
      providerSelect.dataset.index = String(i);
      providerSelect.dataset.field = 'provider';
      providerSelect.innerHTML = '<option value="">— provider —</option>';
      providersList.forEach((p) => {
        const opt = document.createElement('option');
        opt.value = p.name || '';
        opt.textContent = p.name || '';
        if ((llm.provider || '') === (p.name || '')) opt.selected = true;
        providerSelect.appendChild(opt);
      });
      const apiKey = document.createElement('input');
      apiKey.type = 'text';
      apiKey.placeholder = 'API key';
      apiKey.value = typeof llm.apiKey === 'string' ? llm.apiKey : '';
      apiKey.dataset.index = String(i);
      apiKey.dataset.field = 'apiKey';
      const fetchBtn = document.createElement('button');
      fetchBtn.type = 'button';
      fetchBtn.textContent = 'Fetch models';
      fetchBtn.dataset.index = String(i);
      fetchBtn.addEventListener('click', () => {
        collectRemoteFormValues();
        const r = remoteLlmsList[Number(fetchBtn.dataset.index)];
        if (!r || !(r.provider || '').trim()) {
          showMessage('Select a provider first.', true);
          return;
        }
        fetchBtn.disabled = true;
        fetchRemoteModels(r.provider, r.apiKey || '')
          .then((res) => {
            if (res.error) showMessage(res.error, true);
            else showMessage('Models loaded.');
            if (Array.isArray(res.models)) {
              r._models = res.models;
              renderRemoteLlms();
              renderSummarizations();
            }
          })
          .catch((e) => showMessage(e.message || 'Fetch failed', true))
          .finally(() => { fetchBtn.disabled = false; });
      });
      const modelSelect = document.createElement('select');
      modelSelect.dataset.index = String(i);
      modelSelect.dataset.field = 'model';
      modelSelect.innerHTML = '<option value="">— model —</option>';
      const modelList = llm._models || (llm.model ? [{ id: llm.model }] : []);
      modelList.forEach((m) => {
        const id = (m && m.id) || m;
        if (!id) return;
        const o = document.createElement('option');
        o.value = id;
        o.textContent = id;
        if ((llm.model || '') === id) o.selected = true;
        modelSelect.appendChild(o);
      });
      modelSelect.addEventListener('change', () => {
        const idx = Number(modelSelect.dataset.index);
        remoteLlmsList[idx] = remoteLlmsList[idx] || {};
        remoteLlmsList[idx].model = modelSelect.value.trim();
        const prov = remoteLlmsList[idx].provider || '';
        if (prov && remoteLlmsList[idx].model) remoteLlmsList[idx].name = prov + ':' + remoteLlmsList[idx].model;
        renderRemoteLlms();
        renderSummarizations();
      });
      const testBtn = document.createElement('button');
      testBtn.type = 'button';
      testBtn.textContent = 'Test';
      testBtn.dataset.index = String(i);
      testBtn.addEventListener('click', () => {
        collectRemoteFormValues();
        const r = remoteLlmsList[Number(testBtn.dataset.index)];
        if (!r) return;
        if (!(r.provider || '').trim()) {
          showMessage('Select a provider first.', true);
          return;
        }
        testLlm({ provider: r.provider, apiKey: (r.apiKey || '').trim() || undefined, model: (r.model || '').trim() || undefined })
          .then((res) => {
            if (res.success) showMessage('Test passed.');
            else showMessage(res.error || 'Test failed', true);
          })
          .catch((e) => showMessage(e.message || 'Test failed', true));
      });
      const removeBtn = document.createElement('button');
      removeBtn.type = 'button';
      removeBtn.textContent = 'Remove';
      removeBtn.dataset.index = String(i);
      removeBtn.addEventListener('click', () => {
        remoteLlmsList.splice(Number(removeBtn.dataset.index), 1);
        renderRemoteLlms();
        renderSummarizations();
      });
      providerSelect.addEventListener('change', () => {
        const idx = Number(providerSelect.dataset.index);
        remoteLlmsList[idx] = remoteLlmsList[idx] || {};
        remoteLlmsList[idx].provider = providerSelect.value.trim();
        remoteLlmsList[idx].name = '';
        remoteLlmsList[idx].model = '';
        renderRemoteLlms();
        renderSummarizations();
      });
      [apiKey].forEach((input) => {
        input.addEventListener('change', () => {
          const idx = Number(input.dataset.index);
          const field = input.dataset.field;
          remoteLlmsList[idx] = remoteLlmsList[idx] || {};
          remoteLlmsList[idx][field] = input.value.trim();
        });
      });
      div.append(nameDisplay, providerSelect, apiKey, fetchBtn, modelSelect, testBtn, removeBtn);
      container.appendChild(div);
    });
  }

  function renderSummarizations() {
    const container = document.getElementById('summarizationsContainer');
    if (!container) return;
    container.innerHTML = '';
    const llmOptions = getLlmOptions();
    summarizationsList.forEach((part, i) => {
      const div = document.createElement('div');
      div.className = 'config-row';
      const nameInput = document.createElement('input');
      nameInput.placeholder = 'Part name';
      nameInput.value = part.name || '';
      nameInput.dataset.index = String(i);
      nameInput.dataset.field = 'name';
      const llmSelect = document.createElement('select');
      llmSelect.dataset.index = String(i);
      llmSelect.dataset.field = 'llm';
      llmOptions.forEach((opt) => {
        const o = document.createElement('option');
        o.value = opt.value;
        o.textContent = opt.label;
        if ((part.llm || '') === opt.value) o.selected = true;
        llmSelect.appendChild(o);
      });
      if (!part.llm && llmOptions.length) {
        llmSelect.options[0].selected = true;
        part.llm = llmOptions[0].value;
      }
      const systemPromptLabel = document.createElement('label');
      systemPromptLabel.textContent = 'System prompt';
      const systemPrompt = document.createElement('textarea');
      systemPrompt.placeholder = 'Optional. e.g. You are a concise summarizer. Use {{TRANSCRIPT}} if needed.';
      systemPrompt.rows = 2;
      systemPrompt.value = part.systemPrompt || '';
      systemPrompt.dataset.index = String(i);
      systemPrompt.dataset.field = 'systemPrompt';
      const userPromptLabel = document.createElement('label');
      userPromptLabel.textContent = 'User prompt (use {{TRANSCRIPT}} for the transcript)';
      const userPrompt = document.createElement('textarea');
      userPrompt.placeholder = 'e.g. Summarize the following in one sentence.\n\n{{TRANSCRIPT}}';
      userPrompt.rows = 3;
      userPrompt.value = part.userPrompt || '';
      userPrompt.dataset.index = String(i);
      userPrompt.dataset.field = 'userPrompt';
      const upBtn = document.createElement('button');
      upBtn.type = 'button';
      upBtn.textContent = 'Up';
      upBtn.disabled = i === 0;
      upBtn.addEventListener('click', () => {
        if (i === 0) return;
        [summarizationsList[i - 1], summarizationsList[i]] = [summarizationsList[i], summarizationsList[i - 1]];
        renderSummarizations();
      });
      const downBtn = document.createElement('button');
      downBtn.type = 'button';
      downBtn.textContent = 'Down';
      downBtn.disabled = i === summarizationsList.length - 1;
      downBtn.addEventListener('click', () => {
        if (i >= summarizationsList.length - 1) return;
        [summarizationsList[i], summarizationsList[i + 1]] = [summarizationsList[i + 1], summarizationsList[i]];
        renderSummarizations();
      });
      const removeBtn = document.createElement('button');
      removeBtn.type = 'button';
      removeBtn.textContent = 'Remove';
      removeBtn.dataset.index = String(i);
      removeBtn.addEventListener('click', () => {
        summarizationsList.splice(Number(removeBtn.dataset.index), 1);
        renderSummarizations();
      });
      [nameInput, systemPrompt, userPrompt].forEach((input) => {
        input.addEventListener('change', () => {
          const idx = Number(input.dataset.index);
          const field = input.dataset.field;
          summarizationsList[idx] = summarizationsList[idx] || {};
          summarizationsList[idx][field] = input.value.trim();
        });
      });
      llmSelect.addEventListener('change', () => {
        const idx = Number(llmSelect.dataset.index);
        summarizationsList[idx] = summarizationsList[idx] || {};
        summarizationsList[idx].llm = llmSelect.value.trim();
      });
      div.append(nameInput, llmSelect, systemPromptLabel, systemPrompt, userPromptLabel, userPrompt, upBtn, downBtn, removeBtn);
      container.appendChild(div);
    });
  }

  function collectRemoteFormValues() {
    document.querySelectorAll('#remoteLlmsContainer input, #remoteLlmsContainer select').forEach((el) => {
      const idx = Number(el.dataset.index);
      const field = el.dataset.field;
      if (idx >= 0 && field && remoteLlmsList[idx]) remoteLlmsList[idx][field] = el.value.trim();
    });
  }

  function collectFormValues() {
    collectRemoteFormValues();
    document.querySelectorAll('#summarizationsContainer input, #summarizationsContainer select, #summarizationsContainer textarea').forEach((el) => {
      const idx = Number(el.dataset.index);
      const field = el.dataset.field;
      if (idx >= 0 && field && summarizationsList[idx]) summarizationsList[idx][field] = el.value.trim();
    });
  }

  function save() {
    collectFormValues();
    const llmsToSave = remoteLlmsList.map((l) => {
      const provider = (l.provider || '').trim();
      const model = (l.model || '').trim();
      const name = (l.name || '').trim() || (provider && model ? provider + ':' + model : '');
      return { name, type: 'remote', provider, apiKey: l.apiKey || '', model };
    });
    putSummarizationConfig({ llms: llmsToSave, summarizations: summarizationsList })
      .then(() => showMessage('Saved.'))
      .catch((e) => showMessage(e.message || 'Save failed', true));
  }

  document.getElementById('addRemoteLlmBtn')?.addEventListener('click', () => {
    remoteLlmsList.push({ name: '', type: 'remote', provider: '', apiKey: '', model: '' });
    renderRemoteLlms();
    renderSummarizations();
  });
  document.getElementById('addPartBtn')?.addEventListener('click', () => {
    const opts = getLlmOptions();
    summarizationsList.push({ name: '', llm: opts.length ? opts[0].value : '', systemPrompt: '', userPrompt: '{{TRANSCRIPT}}' });
    renderSummarizations();
  });
  document.getElementById('saveBtn')?.addEventListener('click', save);

  loadConfig();
})();
