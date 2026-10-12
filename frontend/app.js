// ==========================================
// KREATIVA - HELPER & UTILS GLOBAL
// ==========================================
const $ = (s, el=document) => el.querySelector(s); const $$ = (s, el=document) => [...el.querySelectorAll(s)];
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const rupiah = (n) => 'Rp ' + Number(n||0).toLocaleString('id-ID');
const fmtDate = (s) => String(s||'').slice(0,16);

// Client API Helper
async function api(path, {method='GET', body, token}={}) {
  const t = token || getToken();
  const res = await fetch(path, {
    method,
    headers: {'Content-Type':'application/json', ...(t?{Authorization:'Bearer '+t}:{})},
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(()=>({}));
  if (res.status===401 && t && !path.startsWith('/api/auth/')) {
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('user');
    alert('Sesi habis, silakan login lagi.'); location.href='/auth.html';
    throw new Error('Sesi habis');
  }
  if (!res.ok) throw new Error(data.error || `Request gagal (${res.status})`);
  return data;
}

// Guard Tombol (Mencegah Klik Ganda)
async function guard(btn, fn){
  if(btn.dataset.busy) return;
  btn.dataset.busy='1'; const old=btn.textContent; btn.disabled=true; btn.textContent='Memproses...';
  try{ return await fn(); }catch(e){ alert(e.message); }
  finally{ btn.disabled=false; btn.textContent=old; delete btn.dataset.busy; }
}

// Kompres Gambar sebelum Upload
async function shrinkImage(file, maxSide=1600, quality=.85){
  if(!/^image\/(jpeg|png|webp)$/.test(file.type) || file.size < 3.5*1024*1024) return file;
  try{
    const bmp = await createImageBitmap(file);
    const r = Math.min(1, maxSide/Math.max(bmp.width,bmp.height));
    const c = document.createElement('canvas'); c.width=Math.round(bmp.width*r); c.height=Math.round(bmp.height*r);
    c.getContext('2d').drawImage(bmp,0,0,c.width,c.height);
    const blob = await new Promise(ok=>c.toBlob(ok,'image/jpeg',quality));
    return blob && blob.size < file.size ? new File([blob], file.name.replace(/\.\w+$/,'')+'.jpg', {type:'image/jpeg'}) : file;
  }catch{ return file; }
}

// Upload File Gambar ke Backend / Supabase
async function uploadFile(file){
  file = await shrinkImage(file);
  const fd = new FormData(); fd.append('file', file);
  const t = getToken();
  const res = await fetch('/api/upload', {method:'POST', headers:t?{Authorization:'Bearer '+t}:{}, body:fd});
  const data = await res.json().catch(()=>({}));
  if(!res.ok) throw new Error(data.error || (res.status===413 ? 'File terlalu besar (maks 4MB)' : `Upload gagal (${res.status})`));
  return data.url;
}

async function pickUpload(fileId, urlId, msgId){
  const f = $('#'+fileId).files[0]; if(!f) return;
  const msg = msgId ? $('#'+msgId) : null;
  if(msg) msg.textContent = 'Mengupload...';
  try{
    const url = await uploadFile(f);
    $('#'+urlId).value = url;
    const pv = $('#'+urlId+'Prev');
    if(pv){ pv.src=url; pv.style.display='block'; }
    if(msg) msg.textContent = 'Upload OK ✓';
  }catch(e){
    if(msg) msg.textContent = '❌ '+e.message;
    else alert(e.message);
  }
}

// Session Management (Tab-Isolated)
// Mengutamakan sessionStorage agar tiap tab browser terisolasi dan bisa login role berbeda (creator & customer) tanpa tabrakan.
function getToken(){
  let t = sessionStorage.getItem('token');
  if(!t){
    t = localStorage.getItem('token');
    if(t){
      sessionStorage.setItem('token', t);
      const u = localStorage.getItem('user');
      if(u) sessionStorage.setItem('user', u);
    }
  }
  return t || '';
}

function currentUser(){
  try{
    let u = sessionStorage.getItem('user');
    if(!u){
      u = localStorage.getItem('user');
      if(u){
        sessionStorage.setItem('user', u);
        const t = localStorage.getItem('token');
        if(t) sessionStorage.setItem('token', t);
      }
    }
    return JSON.parse(u || 'null');
  }catch{
    return null;
  }
}

function saveSession(d){
  if(!d || !d.token) return;
  // Simpan di tab aktif (terisolasi per tab)
  sessionStorage.setItem('token', d.token);
  sessionStorage.setItem('user', JSON.stringify(d.user));
  // Simpan juga di localStorage sebagai default saat buka tab kosong baru
  localStorage.setItem('token', d.token);
  localStorage.setItem('user', JSON.stringify(d.user));
}

function logout(){
  sessionStorage.removeItem('token');
  sessionStorage.removeItem('user');
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  location.href='/';
}

function requireAuth(role){
  const u = currentUser();
  if(!u){
    location.href='/auth.html';
    return null;
  }
  if(role && u.role!==role && u.role!=='admin'){
    alert(role==='creator' ? 'Halaman ini khusus creator.' : 'Halaman ini khusus customer.');
    location.href='/';
    return null;
  }
  return u;
}

function goBack(){
  if(history.length>1 && document.referrer.startsWith(location.origin)) history.back();
  else location.href='/';
}

async function openStore(){
  if(!confirm('Aktifkan akun creator?\n\nAkunmu akan menjadi akun creator (untuk menjual jasa).')) return;
  try{
    saveSession(await api('/api/me/become-creator',{method:'POST'}));
    location.href='/dashboard-creator.html#profil';
  }catch(e){
    alert(e.message);
  }
}

// Subnav Creator
const CREATOR_MENU=[['orders','Pesanan'],['jasa','Layanan & Paket'],['portofolio','Portofolio'],['booster','Booster'],['profil','Profil Toko']];

function markSubnav(){
  const k = location.hash.slice(1) || 'orders';
  const onDash = location.pathname.includes('dashboard-creator');
  $$('.subnav a[data-k]').forEach(a=>a.classList.toggle('on', onDash && a.dataset.k===k));
}

// Render Navigation Bar
function navbar(){
  const u = currentUser();
  const links = $('#navLinks') || $('.links'); 
  if(!links) return;
  
  const home = location.pathname==='/' || location.pathname==='/index.html';
  
  if(!home && !$('#backBtn')){
    const navInner = $('.nav-inner');
    if(navInner) navInner.insertAdjacentHTML('afterbegin','<button id="backBtn" class="btn small ghost" onclick="goBack()">← Kembali</button>');
  }
  
  links.innerHTML = `
    <a href="/" class="small">Explore</a>
    <a href="/creators.html" class="small">Cari Creator</a>
    ${u && u.role === 'customer' ? '<a href="/dashboard-customer.html" class="small">Pesanan Saya</a>' : ''}
    ${u && u.role === 'admin' ? '<a href="/dashboard-admin.html" class="small">Admin</a>' : ''}
    ${u ? `<a href="/account.html" class="small">${esc(u.name)}</a>` : ''}
    ${u && u.role === 'customer' ? '<button class="btn small ghost" onclick="openStore()">Buka Lapak</button>' : ''}
    ${u ? '<button class="btn small ghost" onclick="logout()">Logout</button>' : '<a href="/auth.html" class="btn small" style="color:#ffffff">Masuk / Daftar</a>'}
  `;
    
  if(u && u.role==='creator' && !$('.subnav')){
    const nav = $('.nav');
    if(nav){
      nav.insertAdjacentHTML('afterend', `<div class="subnav"><div class="subnav-inner">
        ${CREATOR_MENU.map(([k,l])=>`<a data-k="${k}" href="/dashboard-creator.html#${k}">${l}</a>`).join('')}
        <a href="/store.html?creator=${u.id}">Lihat Toko</a></div></div>`);
      markSubnav();
    }
  }
}
window.addEventListener('hashchange', markSubnav);

// Status Badge Helpers
const STATUS_LABEL={pending:'Menunggu',diterima:'Diterima',dikerjakan:'Dikerjakan',revisi:'Revisi',dikirim:'Hasil Dikirim',selesai:'Selesai',ditolak:'Ditolak',dibatalkan:'Dibatalkan'};
function statusBadge(s){
  const cls = s==='selesai'?'open':(s==='ditolak'||s==='dibatalkan')?'closed':s==='dikirim'?'boost':'plan';
  return `<span class="badge ${cls}"><span class="badge-dot" style="background:currentColor"></span>${STATUS_LABEL[s]||s}</span>`;
}

const PAY_STATUS_LABEL = {
  unpaid: 'Belum Bayar',
  verifying: 'Verifikasi Admin',
  paid: 'Lunas',
  rejected: 'Ditolak'
};

function payStatusBadge(s) {
  const cls = s === 'paid' ? 'open' : (s === 'verifying' ? 'boost' : 'closed');
  return `<span class="badge ${cls}"><span class="badge-dot" style="background:currentColor"></span>${PAY_STATUS_LABEL[s] || s}</span>`;
}

function timeline(cur){
  const steps=[['pending','Menunggu'],['diterima','Diterima'],['dikerjakan','Dikerjakan'],['dikirim','Hasil Dikirim'],['selesai','Selesai']];
  const idx = cur==='revisi' ? 2 : steps.findIndex(s=>s[0]===cur);
  return `<div class="timeline">${steps.map(([k,l],i)=>`<span class="step ${i<=idx?'on':''}">${l}</span>`).join('')}${cur==='revisi'?'<span class="step on">Sedang Revisi</span>':''}</div>`;
}

// Inisialisasi otomatis saat dokumen siap
document.addEventListener('DOMContentLoaded', () => {
  navbar();
});