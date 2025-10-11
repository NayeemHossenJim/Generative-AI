const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const state = {
  files: [],
  built: false,
  uploading: false,
  building: false,
};

function fmtTime(d = new Date()) {
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function addMessage(text, who = 'user') {
  const tpl = document.getElementById(who === 'user' ? 'bubble-user' : 'bubble-bot');
  const frag = tpl.content.cloneNode(true);
  frag.querySelector('.text').textContent = text;
  frag.querySelector('.time').textContent = fmtTime();
  $('#messages').appendChild(frag);
  $('#messages').scrollTop = $('#messages').scrollHeight;
}

async function api(path, opts = {}) {
  const res = await fetch(path, {
    headers: { 'Accept': 'application/json' },
    ...opts,
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || `Request failed: ${res.status}`);
  }
  const ct = res.headers.get('content-type') || '';
  if (ct.includes('application/json')) return res.json();
  return res.text();
}

function setStatus(text) { $('#status').textContent = text; }
function setBuildEnabled(enabled) { $('#build-btn').disabled = !enabled; }

// Upload PDFs
$('#file-input').addEventListener('change', async (e) => {
  const files = Array.from(e.target.files || []);
  if (!files.length) return;
  state.uploading = true;
  setBuildEnabled(false);
  setStatus('Uploading...');

  try {
    for (const f of files) {
      const fd = new FormData();
      fd.append('file', f, f.name);
      await api('/upload', { method: 'POST', body: fd });
    }
    state.files.push(...files.map(f => f.name));
    setStatus(`${state.files.length} file(s) ready. Click Build.`);
    setBuildEnabled(true);
  } catch (err) {
    console.error(err);
    setStatus(`Upload error: ${err.message}`);
  } finally {
    state.uploading = false;
  }
});

// Build vectors
$('#build-btn').addEventListener('click', async () => {
  if (state.building) return;
  state.building = true;
  setStatus('Building vector DB... This can take a minute.');
  setBuildEnabled(false);

  try {
    const res = await api('/build', { method: 'POST' });
    state.built = true;
    setStatus(res.message || 'Vector DB built.');
  } catch (err) {
    console.error(err);
    setStatus(`Build error: ${err.message}`);
  } finally {
    state.building = false;
  }
});

// Health check
$('#health-btn').addEventListener('click', async () => {
  try {
    const h = await api('/health');
    addMessage(`Health: ${JSON.stringify(h)}`, 'bot');
  } catch (err) {
    addMessage(`Health check failed: ${err.message}`, 'bot');
  }
});

// Send question
$('#composer').addEventListener('submit', async (e) => {
  e.preventDefault();
  const input = $('#question');
  const text = input.value.trim();
  if (!text) return;
  addMessage(text, 'user');
  input.value = '';

  try {
    const res = await api('/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: text }),
    });
    const answer = res.answer || 'No answer.';
    addMessage(answer, 'bot');
  } catch (err) {
    addMessage(`Error: ${err.message}`, 'bot');
  }
});

// Seed a hello message
addMessage('Hi! Upload your PDFs from the left, build the knowledge base, then ask a question here.', 'bot');
