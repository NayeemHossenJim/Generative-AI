/* Chat-style frontend logic for messenger-like UI */

const fileInput = document.getElementById('file-input');
const uploadsEl = document.getElementById('uploads');
const buildBtn = document.getElementById('build-btn');
const askBtn = document.getElementById('ask-btn');
const clearBtn = document.getElementById('clear-btn');
const questionEl = document.getElementById('question');
const responsesEl = document.getElementById('responses');
const apiUrlInput = document.getElementById('api-url');

let selectedFiles = [];
let lastBuildOk = false;

function now(){
  return new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});
}

function formatUploads(){
  uploadsEl.innerHTML = '';
  if(selectedFiles.length === 0){
    uploadsEl.innerHTML = '<p class="muted">No files selected</p>';
    buildBtn.disabled = true;
    return;
  }
  buildBtn.disabled = false;
  selectedFiles.forEach((f, idx) => {
    const div = document.createElement('div');
    div.className = 'upload-item';
    div.innerHTML = `
      <div>
        <div class="upload-name">${escapeHtml(f.name)}</div>
        <div class="muted">${formatBytes(f.size)}</div>
      </div>
      <div>
        <button class="ghost" data-idx="${idx}">Remove</button>
      </div>`;
    uploadsEl.appendChild(div);
  });
}

fileInput.addEventListener('change', (e)=>{
  selectedFiles = Array.from(e.target.files).filter(f => f.type === 'application/pdf');
  formatUploads();
});

uploadsEl.addEventListener('click', (e)=>{
  if(e.target.matches('button')){
    const idx = Number(e.target.getAttribute('data-idx'));
    selectedFiles.splice(idx, 1);
    formatUploads();
  }
});

function addMessage({who='bot', text='', sources=[]}){
  const li = document.createElement('li');
  li.className = 'message ' + (who === 'user' ? 'user' : 'bot');
  const meta = document.createElement('div');
  meta.className = 'meta';
  meta.textContent = who === 'user' ? `You • ${now()}` : `Bot • ${now()}`;
  const body = document.createElement('div');
  body.className = 'body';
  body.innerHTML = escapeHtml(text).replace(/\n/g, '<br/>');
  li.appendChild(meta);
  li.appendChild(body);
  if(Array.isArray(sources) && sources.length){
    const s = document.createElement('div');
    s.className = 'sources';
    s.innerHTML = '<strong>Sources</strong><br/>' + sources.map((c,i)=>`<div><em>Chunk ${i+1}:</em> ${escapeHtml(truncate(c.page_content || c, 300))}</div>`).join('');
    li.appendChild(s);
  }
  responsesEl.appendChild(li);
  responsesEl.scrollTop = responsesEl.scrollHeight;
}

buildBtn.addEventListener('click', async ()=>{
  const apiUrl = apiUrlInput.value.replace(/\/+$/, '');
  if(!apiUrl) return alert('Please provide the API endpoint URL');
  if(selectedFiles.length === 0) return alert('Please select at least one PDF');
  buildBtn.disabled = true; buildBtn.textContent = 'Building...'; lastBuildOk = false;
  try{
    // upload each file
    for(const file of selectedFiles){
      await uploadFile(apiUrl + '/upload', file);
    }
    // trigger build
    const r = await fetch(apiUrl + '/build', {method:'POST'});
    const j = await r.json();
    if(r.ok && j.ok){
      lastBuildOk = true; addMessage({who:'bot', text:'✅ Vector DB built successfully.'});
      askBtn.disabled = false;
    } else throw new Error(j.error || 'Build failed');
  }catch(err){
    addMessage({who:'bot', text:'Error: ' + err.message});
  }finally{ buildBtn.disabled = false; buildBtn.textContent = '🚀 Build'; }
});

askBtn.addEventListener('click', async ()=>{
  const apiUrl = apiUrlInput.value.replace(/\/+$/, '');
  const q = questionEl.value.trim();
  if(!q) return; if(!lastBuildOk) return alert('Please build the vector DB first');
  addMessage({who:'user', text:q});
  questionEl.value=''; askBtn.disabled = true; askBtn.textContent = 'Sending...';
  try{
    const resp = await fetch(apiUrl + '/query', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({question:q})});
    const j = await resp.json();
    if(resp.ok){ addMessage({who:'bot', text:j.answer || j.text || 'No answer', sources: j.context || []}); }
    else throw new Error(j.error || 'Query failed');
  }catch(err){ addMessage({who:'bot', text:'Error: ' + err.message}); }
  finally{ askBtn.disabled = false; askBtn.textContent = 'Send'; }
});

clearBtn.addEventListener('click', ()=>{ questionEl.value=''; });

async function uploadFile(url, file){
  const fd = new FormData(); fd.append('file', file, file.name);
  const res = await fetch(url, {method:'POST', body: fd});
  if(!res.ok){ const j = await res.json().catch(()=>({})); throw new Error(j.error || res.statusText); }
  return res.json();
}

// Utilities
function formatBytes(bytes){ if(bytes === 0) return '0 B'; const sizes = ['B','KB','MB','GB','TB']; const i = Math.floor(Math.log(bytes) / Math.log(1024)); return (bytes / Math.pow(1024, i)).toFixed(2) + ' ' + sizes[i]; }
function escapeHtml(s){ if(!s) return ''; return String(s).replace(/[&<>"']/g, function(m){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"}[m]; }); }
function truncate(s, n){ return s && s.length > n ? s.slice(0,n) + '…' : s; }

// Demo fallback button added to header area
(function demoFallback(){
  const btn = document.createElement('button');
  btn.className = 'ghost'; btn.textContent = 'Demo';
  btn.style.marginLeft = '8px';
  btn.addEventListener('click', ()=> addMessage({who:'bot', text:'This is a demo reply. Provide a backend API for real answers.'}));
  const right = document.querySelector('.chat-header .right');
  if(right) right.insertBefore(btn, right.firstChild);
})();
