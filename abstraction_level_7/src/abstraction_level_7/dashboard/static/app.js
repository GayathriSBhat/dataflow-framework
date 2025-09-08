/* static/app.js — simple SPA to drive the dashboard endpoints */
const $ = id => document.getElementById(id);

let autoTimer = null;
let currentTraceLimit = parseInt($('traceLimit').value, 10) || 50;

function prettyMs(sec) {
  return (sec * 1000).toFixed(3);
}

async function fetchJson(path) {
  try {
    const res = await fetch(path);
    if (!res.ok) {
      const txt = await res.text();
      try { return JSON.parse(txt); } catch(e){ return {__error: txt||res.statusText}; }
    }
    return await res.json();
  } catch (err) {
    return {__error: String(err)};
  }
}

/* Stats */
async function loadStats() {
  const data = await fetchJson('/stats');
  const updated = new Date().toLocaleTimeString();
  $('statsUpdated').textContent = updated;
  const tbody = $('statsBody');
  tbody.innerHTML = '';

  if (data.__error) {
    tbody.innerHTML = `<tr><td colspan="5" style="color:#ffbaba">Error: ${escapeHtml(data.__error)}</td></tr>`;
    return;
  }

  // compute max avg_time for scaling
  let maxAvg = 0;
  for (const [k,v] of Object.entries(data)) {
    if (v.avg_time > maxAvg) maxAvg = v.avg_time;
  }
  maxAvg = Math.max(maxAvg, 1e-6);

  for (const [name, stat] of Object.entries(data)) {
    const tr = document.createElement('tr');
    const avgMs = prettyMs(stat.avg_time);
    tr.innerHTML = `
      <td><strong>${escapeHtml(name)}</strong></td>
      <td>${stat.count}</td>
      <td>${avgMs}</td>
      <td style="color:${stat.errors>0? 'var(--err)':'var(--muted)'}">${stat.errors}</td>
      <td style="min-width:160px">
        <div style="background: rgba(255,255,255,0.03); padding:6px; border-radius:8px;">
          <div class="profile-bar" style="width:${Math.min(100, (stat.avg_time / maxAvg)*100)}%"></div>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  }
}

/* Traces */
async function loadTraces(limit=currentTraceLimit) {
  $('traceWarning').hidden = true;
  const path = `/trace?limit=${limit}`;
  const data = await fetchJson(path);
  const list = $('tracesList');
  list.innerHTML = '';
  if (data.__error) {
    $('traceWarning').hidden = false;
    $('traceWarning').textContent = `Trace error: ${data.__error}`;
    return;
  }
  if (!Array.isArray(data) || data.length === 0) {
    list.innerHTML = `<div class="small-meta">No traces in window.</div>`;
    return;
  }

  for (const t of data) {
    const item = document.createElement('div');
    item.className = 'trace-item';
    const created = new Date(t.created * 1000).toLocaleTimeString();
    const header = document.createElement('div');
    header.className = 'trace-header';
    header.innerHTML = `<div><strong>${escapeHtml(t.line_id)}</strong><div class="small-meta">${created}</div></div>
                        <div class="small-meta">${t.steps.length} steps</div>`;
    const stepsNode = document.createElement('div');
    stepsNode.className = 'trace-steps';
    const stepsText = t.steps.map(s => {
      const ts = new Date(s[0]*1000).toLocaleTimeString();
      return `${ts}  •  ${escapeHtml(s[1])}  →  ${escapeHtml(String(s[2]))}`;
    }).join('\n');
    stepsNode.textContent = stepsText;

    const copyBtn = document.createElement('button');
    copyBtn.textContent = 'Copy JSON';
    copyBtn.style.alignSelf = 'flex-end';
    copyBtn.onclick = () => {
      navigator.clipboard.writeText(JSON.stringify(t, null, 2));
      copyBtn.textContent = 'Copied';
      setTimeout(()=> copyBtn.textContent = 'Copy JSON', 1000);
    };

    item.appendChild(header);
    item.appendChild(stepsNode);
    item.appendChild(copyBtn);

    list.appendChild(item);
  }
}

/* Errors */
async function loadErrors(limit=50) {
  const data = await fetchJson(`/errors?limit=${limit}`);
  const list = $('errorsList');
  const empty = $('errorsEmpty');
  const badge = $('errorsBadge');
  const countSpan = $('errorsCount');

  // reset UI
  list.innerHTML = '';
  empty.hidden = true;
  badge.hidden = true;
  countSpan.textContent = '0';

  if (data.__error) {
    list.innerHTML = `<li class="error-item">Error loading: ${escapeHtml(data.__error)}</li>`;
    return;
  }

  if (!Array.isArray(data) || data.length === 0) {
    empty.hidden = false;
    countSpan.textContent = '0';
    return;
  }

  countSpan.textContent = data.length;
  badge.hidden = false;
  badge.textContent = data.length;

  for (const e of data) {
    const li = document.createElement('li');
    li.className = 'error-item';
    const ts = new Date(e.timestamp * 1000).toLocaleString();
    const payload = e.payload ? `<pre class="small-meta" style="white-space:pre-wrap;margin:6px 0 0;">${escapeHtml(JSON.stringify(e.payload, null, 2))}</pre>` : '';
    li.innerHTML = `<div style="display:flex;justify-content:space-between;align-items:center">
                      <div><strong>${escapeHtml(e.processor)}</strong> <span class="small-meta">${ts}</span></div>
                      <div class="small-meta">line: ${escapeHtml(e.line_id)}</div>
                    </div>
                    <div style="color:var(--err);font-family:monospace;word-break:break-word">${escapeHtml(e.error)}</div>
                    ${payload}`;
    list.appendChild(li);
  }
}

/* controls & init */
function setupControls() {
  $('refreshBtn').addEventListener('click', refreshAll);
  $('autoRefresh').addEventListener('change', toggleAuto);
  $('interval').addEventListener('change', () => {
    if ($('autoRefresh').checked) startAuto();
  });
  $('traceLimit').addEventListener('change', () => {
    currentTraceLimit = parseInt($('traceLimit').value, 10) || 50;
    loadTraces(currentTraceLimit);
  });
  $('traceSearch').addEventListener('input', (e) => {
    const q = e.target.value.trim().toLowerCase();
    document.querySelectorAll('.trace-item').forEach(node => {
      if (!q) { node.style.display = ''; return; }
      const text = node.textContent.toLowerCase();
      node.style.display = text.includes(q) ? '' : 'none';
    });
  });
}

async function refreshAll() {
  await Promise.all([loadStats(), loadTraces(currentTraceLimit), loadErrors(50)]);
}

function startAuto(){
  stopAuto();
  const interval = Math.max(1, parseInt($('interval').value, 10) || 3) * 1000;
  autoTimer = setInterval(refreshAll, interval);
}

function stopAuto(){
  if (autoTimer) { clearInterval(autoTimer); autoTimer = null; }
}

function toggleAuto(e){
  if (e.target.checked) startAuto(); else stopAuto();
}

function escapeHtml(s) {
  if (s == null) return '';
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

async function init(){
  setupControls();
  await refreshAll();
  if ($('autoRefresh').checked) startAuto();
}

init();
