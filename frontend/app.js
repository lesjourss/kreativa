// Helpers global
const $ = (s, el=document) => el.querySelector(s);
const $$ = (s, el=document) => [...el.querySelectorAll(s)];
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

async function api(path, {method='GET', body, token}={}) {
  const t = token || localStorage.getItem('token');
  const res = await fetch(path, {
    method,
    headers: {'Content-Type':'application/json', ...(t?{Authorization:'Bearer '+t}:{})},
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(()=>({}));
  if (!res.ok) throw new Error(data.error || 'Request gagal');
  return data;
}
// Upload file gambar (jpg/png/webp/gif, maks 5MB) -> return URL /uploads/...
async function uploadFile(file){
  const fd = new FormData(); fd.append('file', file);
  const t = localStorage.getItem('token');
  const res = await fetch('/api/upload', {method:'POST', headers:{...(t?{Authorization:'Bearer '+t}:{})}, body:fd});
  const data = await res.json().catch(()=>({}));
  if(!res.ok) throw new Error(data.error || 'Upload gagal');
  return data.url;
}
// Dipakai di onchange input file: upload lalu isi input URL target
async function pickUpload(fileInputId, urlInputId, msgId){
  const inp = document.getElementById(fileInputId);
  const file = inp && inp.files && inp.files[0];
  if(!file) return;
  if(msgId) document.getElementById(msgId).textContent = 'Mengupload...';
  try{
    document.getElementById(urlInputId).value = await uploadFile(file);
    if(msgId) document.getElementById(msgId).textContent = 'Upload OK ✓';
  }catch(e){ if(msgId) document.getElementById(msgId).textContent = e.message; else alert(e.message); }
}
function currentUser(){ try{return JSON.parse(localStorage.getItem('user')||'null')}catch{return null} }
function requireAuth(role){
  const u = currentUser();
  if(!u){ location.href='/auth.html'; return null; }
  if(role && u.role!==role && u.role!=='admin'){ alert('Halaman khusus '+role); location.href='/'; return null; }
  return u;
}
function navbar(){
  const u = currentUser();
  const links = $('#navLinks');
  if(!links) return;
  links.innerHTML = `
    <a href="/" class="small">Explore</a>
    ${u&&u.role==='creator'?'<a href="/dashboard-creator.html" class="small">Dashboard</a>':''}
    ${u&&u.role==='customer'?'<a href="/dashboard-customer.html" class="small">Pesanan Saya</a>':''}
    ${u?`<span class="small muted">${esc(u.name)} (${esc(u.role)})</span><button class="btn small ghost" onclick="localStorage.clear();location.href='/'">Logout</button>`
       :'<a href="/auth.html" class="btn small">Masuk / Daftar</a>'}`;
}
function statusBadge(s){
  const map={pending:'⏳ Pending',diterima:'✅ Diterima',dikerjakan:'🛠️ Dikerjakan',revisi:'🔁 Revisi',selesai:'🎉 Selesai',ditolak:'⛔ Ditolak',dibatalkan:'🚫 Dibatalkan'};
  return `<span class="badge ${s==='selesai'?'open':(s==='ditolak'||s==='dibatalkan')?'closed':'plan'}">${map[s]||s}</span>`;
}
function timeline(cur){
  const steps=['pending','diterima','dikerjakan','revisi','selesai'];
  const idx=steps.indexOf(cur);
  return `<div class="timeline">${steps.map((s,i)=>`<span class="step ${i<=idx?'on':''}">${s}</span>`).join('')}</div>`;
}
