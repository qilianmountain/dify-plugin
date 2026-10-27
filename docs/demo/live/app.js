(() => {
  const root = document.getElementById('ba-dify-review');
  const el = id => root.querySelector('#' + id);
  const configs = {};
  let tools = [], toolName = 'run_my_bot', busy = false, output = null, error = '', state = 'idle';
  let activeTab = 'settings', duration = 0;
  const tool = () => tools.find(item => item.name === toolName);
  const config = () => configs[toolName] ||= {targetId: '', operation: 'run', input: '{}', timeout: '600', options: [], loaded: false};
  const escape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const icons = () => window.lucide?.createIcons({attrs: {width: 16, height: 16}});

  function stash() {
    Object.assign(config(), {targetId: el('ba-bot').value, operation: el('ba-operation').value,
      input: el('ba-input').value, timeout: el('ba-timeout').value});
  }

  function setTab(tab) {
    activeTab = tab;
    el('ba-settings-panel').hidden = tab !== 'settings';
    el('ba-result-panel').hidden = tab !== 'result';
    el('ba-tab-settings').setAttribute('aria-selected', String(tab === 'settings'));
    el('ba-tab-result').setAttribute('aria-selected', String(tab === 'result'));
  }

  function highlight(line) {
    let html = '', offset = 0;
    const pattern = /"(?:\\.|[^"\\])*"|\b(?:true|false|null)\b|-?\b\d+(?:\.\d+)?\b/g;
    for (const match of line.matchAll(pattern)) {
      html += escape(line.slice(offset, match.index));
      const kind = match[0][0] === '"' ? (line.slice(match.index + match[0].length).trimStart().startsWith(':') ? 'key' : 'string') : 'literal';
      html += '<span class="ba-json-' + kind + '">' + escape(match[0]) + '</span>';
      offset = match.index + match[0].length;
    }
    return html + escape(line.slice(offset));
  }

  function renderResult() {
    if (state === 'idle') {
      el('ba-run-result').innerHTML = '<div class="ba-empty"><i data-lucide="flask-conical"></i><strong>No runs yet</strong><p>Select a target, then click Run this step.</p></div>';
    } else {
      const label = state === 'running' ? 'Running' : state === 'failed' ? 'Failed' : 'Succeeded';
      let html = '<div class="ba-native-status" data-tone="' + (state === 'failed' ? 'error' : state === 'running' ? 'running' : 'success') + '"><strong>' + label + '</strong><small>' + (state === 'running' ? 'Waiting for the live API response' : duration.toFixed(2) + 's · Live API') + '</small></div>';
      if (error) html += '<div class="ba-inline-error" role="alert">' + escape(error) + '</div>';
      if (output) {
        const text = JSON.stringify(output, null, 2);
        html += '<div class="ba-native-editor"><div class="ba-editor-header"><span>Output</span><button type="button" class="ba-editor-copy" aria-label="Copy full output" id="ba-copy-output"><i data-lucide="copy"></i></button></div><pre class="ba-editor-code" id="ba-native-output" role="textbox" aria-label="Output JSON, read-only" aria-readonly="true" aria-multiline="true">';
        html += text.split('\n').map((line, i) => '<span class="ba-code-line"><span class="ba-line-number" aria-hidden="true">' + (i+1) + '</span><span class="ba-line-content">' + highlight(line) + '</span></span>').join('');
        html += '</pre></div>';
      }
      el('ba-run-result').innerHTML = html;
    }
    icons();
  }

  function refresh() {
    root.dataset.state = state;
    root.dataset.scope = 'node';
    el('ba-node-status').textContent = state === 'idle' ? 'Not Run' : state === 'running' ? 'Running' : state === 'failed' ? 'Failed' : 'Succeeded';
    el('ba-downstream-status').textContent = 'Not Run';
    el('ba-tab-result').querySelector('.ba-run-indicator').hidden = state === 'idle';
    root.querySelectorAll('#ba-config-form input,#ba-config-form select,#ba-config-form textarea,#ba-config-form button,#ba-tool-picker button,#ba-demo-connection input,#ba-demo-connection button').forEach(item => item.disabled = busy);
    ['ba-top-run','ba-step-run'].forEach(id => el(id).disabled = busy || !tool());
    renderResult();
  }

  function botOptions() {
    const current = config();
    const placeholder = document.createElement('option');
    placeholder.value = '';
    placeholder.textContent = current.loaded ? 'Select a target' : 'Load the lists in the demo connection above';
    el('ba-bot').replaceChildren(placeholder, ...current.options.map(option => {
      const node = document.createElement('option');
      node.value = option.value;
      node.textContent = option.label + ' · ' + option.value;
      return node;
    }));
    el('ba-bot').value = current.targetId;
    const targetHelp = toolName === 'run_my_bot' ? 'Select one of your custom Bots.' : 'Select a BrowserAct official template.';
    el('ba-bot-help').title = targetHelp;
    el('ba-bot-help').setAttribute('aria-label', targetHelp);
  }

  function renderTool() {
    const current = config(), meta = tool();
    el('ba-tool-picker').replaceChildren(...tools.map(item => {
      const button = document.createElement('button');
      button.type = 'button'; button.className = 'ba-button'; button.textContent = item.label;
      button.setAttribute('aria-pressed', String(item.name === toolName));
      button.addEventListener('click', () => switchTool(item.name));
      return button;
    }));
    root.querySelector('.ba-selected-node .ba-node-heading strong').textContent = meta?.label || 'BrowserAct';
    el('ba-canvas-node').setAttribute('aria-label', 'Select the ' + (meta?.label || 'BrowserAct') + ' node');
    root.querySelector('.ba-output-node .ba-variable span:nth-child(2)').textContent = (meta?.label || 'BrowserAct') + ' / json';
    root.querySelector('.ba-panel-heading strong').textContent = meta?.label || 'BrowserAct';
    root.querySelector('.ba-panel').setAttribute('aria-label', (meta?.label || 'BrowserAct') + ' Node Configuration');
    el('ba-operation').value = current.operation;
    el('ba-target-label').textContent = toolName === 'run_my_bot' ? 'Bot' : 'Template';
    el('ba-input').value = current.input;
    el('ba-timeout').value = current.timeout;
    el('ba-timeout').required = false;
    botOptions(); refresh(); icons();
  }

  async function request(action, parameters = {}) {
    const seconds = parameters.operation === 'run' ? parameters.timeout + 45 : 45;
    let response;
    try {
      response = await fetch('/api/tools/' + toolName + '/' + action, {
        method: 'POST', headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + el('ba-key').value.trim()},
        body: JSON.stringify(parameters), signal: AbortSignal.timeout(seconds * 1000)
      });
    } catch {
      throw new Error('The local request failed or timed out. ' + (parameters.operation === 'run' ? 'The remote task may have started or may still be running. Check BrowserAct first.' : 'No task was created.'));
    }
    const data = await response.json();
    const last = data.api_calls?.at(-1);
    if (last) el('ba-api-evidence').textContent = last.method + ' ' + last.path + ' → HTTP ' + last.status + ' · ' + new Date().toLocaleTimeString();
    if (!response.ok) throw new Error(data.error || 'HTTP ' + response.status);
    return data;
  }

  async function loadOptions() {
    if (busy || !tool()) return;
    if (!el('ba-key').value.trim()) { error = 'Enter your BrowserAct API Key first.'; state = 'failed'; setTab('result'); refresh(); return; }
    busy = true; error = ''; output = null; state = 'idle'; refresh();
    el('ba-bot-help').title = 'Loading lists from the live API…';
    try {
      const data = await request('options');
      config().options = data.options; config().loaded = true;
      if (!data.options.some(item => item.value === config().targetId)) config().targetId = '';
      root.querySelector('.ba-connected').textContent = 'API Connected';
      botOptions();
    } catch (failure) {
      config().options = []; config().loaded = false; config().targetId = '';
      botOptions(); error = failure.message; state = 'failed'; setTab('result');
      root.querySelector('.ba-connected').textContent = 'Connection Failed';
    } finally { busy = false; renderTool(); }
  }

  async function switchTool(name) {
    if (busy || name === toolName) return;
    stash(); toolName = name; state = 'idle'; output = null; error = ''; setTab('settings'); renderTool();
    if (el('ba-key').value.trim() && !config().loaded) await loadOptions();
  }

  async function run() {
    if (busy) return;
    stash(); error = ''; output = null;
    if (!el('ba-key').value.trim() || !config().targetId) {
      error = 'Connect to the API and select a target first.'; state = 'failed'; setTab('result'); refresh(); return;
    }
    const parameters = {operation: config().operation, target_id: config().targetId};
    if (parameters.operation === 'run') {
      parameters.timeout = Number(config().timeout);
      if (!Number.isInteger(parameters.timeout) || parameters.timeout <= 0) {
        error = 'Wait Timeout must be a positive integer in seconds.'; state = 'failed'; setTab('result'); refresh(); return;
      }
      parameters.input_json = config().input;
    }
    busy = true; state = 'running'; setTab('result'); refresh();
    root.querySelector('.ba-panel-heading').scrollIntoView({block:'start',behavior:'auto'});
    const start = performance.now();
    try {
      const data = await request('invoke', parameters);
      output = data.result; state = parameters.operation === 'view' ? 'parameters' : 'finished';
    } catch (failure) { error = failure.message; state = 'failed'; }
    finally { duration = (performance.now() - start) / 1000; busy = false; refresh(); }
  }

  el('ba-connect').addEventListener('click', loadOptions);
  ['ba-top-run','ba-step-run'].forEach(id => el(id).addEventListener('click', run));
  el('ba-config-form').addEventListener('submit', event => { event.preventDefault(); run(); });
  ['ba-operation','ba-bot','ba-timeout','ba-input'].forEach(id => el(id).addEventListener('change', () => {
    stash(); output = null; error = ''; state = 'idle'; refresh();
  }));
  el('ba-key').addEventListener('input', () => {
    for (const item of Object.values(configs)) Object.assign(item, {loaded:false, options:[], targetId:''});
    root.querySelector('.ba-connected').textContent = 'Not Connected';
    output = null; error = ''; state = 'idle'; botOptions(); refresh();
  });
  el('ba-tab-settings').addEventListener('click', () => setTab('settings'));
  el('ba-tab-result').addEventListener('click', () => setTab('result'));
  el('ba-canvas-node').addEventListener('click', () => setTab('settings'));
  el('ba-run-result').addEventListener('click', async event => {
    const button = event.target.closest('#ba-copy-output');
    if (!button || !output) return;
    try {
      await navigator.clipboard.writeText(JSON.stringify(output, null, 2));
      button.innerHTML = '<i data-lucide="copy-check"></i>'; icons();
      setTimeout(() => { if(button.isConnected) {button.innerHTML = '<i data-lucide="copy"></i>'; icons();} }, 2000);
    } catch { button.textContent = 'Select and copy manually'; }
  });
  fetch('/api/tools').then(response => response.json()).then(data => {
    tools = data.tools; renderTool();
  }).catch(() => {
    error = 'Could not load local tools. Check the demo service.'; state = 'failed'; setTab('result'); refresh();
  });
})();
