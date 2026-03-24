/**
 * LibraryRank — Main Frontend JS
 * Fetches data from Django JSON APIs and renders the leaderboard UI.
 */

'use strict';

// ── CONFIG ──
const ROLE_COLORS = {
  student: { bg: 'rgba(77,166,255,.18)', text: 'var(--blue)' },
  lecturer: { bg: 'rgba(61,224,138,.18)', text: 'var(--green)' },
  staff: { bg: 'rgba(255,145,77,.18)', text: 'var(--orange)' },
};
const BOOK_ICONS = { CS: '💻', Economics: '📈', Medicine: '🫀', Law: '⚖️', Engineering: '🏗️', Psychology: '🧠', Mathematics: '📐', Chemistry: '🧪', default: '📚' };

let currentDateFrom = document.getElementById('dateFrom')?.value;
let currentDateTo = document.getElementById('dateTo')?.value;
let currentSearch = document.getElementById('searchInput')?.value || '';
let currentTab = 'overview';
let searchTimer = null;

// ── INIT ──
document.addEventListener('DOMContentLoaded', () => {
  bindControls();
  loadTab('overview');
});

function bindControls() {
  // Tabs
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.dataset.tab;
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      document.getElementById(`panel-${tab}`)?.classList.add('active');
      currentTab = tab;
      loadTab(tab);
    });
  });

  // Search with debounce
  document.getElementById('searchInput')?.addEventListener('input', e => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      currentSearch = e.target.value;
      loadTab(currentTab);
    }, 350);
  });

  // Date filters
  ['dateFrom', 'dateTo'].forEach(id => {
    document.getElementById(id)?.addEventListener('change', e => {
      if (id === 'dateFrom') currentDateFrom = e.target.value;
      else currentDateTo = e.target.value;
      loadTab(currentTab);
    });
  });

  // Exports
  document.getElementById('btnExcelExport')?.addEventListener('click', () => {
    const url = `/export/excel/?date_from=${currentDateFrom}&date_to=${currentDateTo}`;
    window.location.href = url;
    showToast('📊', 'Downloading Excel...');
  });

  document.getElementById('btnPdfExport')?.addEventListener('click', () => {
    const url = `/export/pdf/?date_from=${currentDateFrom}&date_to=${currentDateTo}`;
    window.location.href = url;
    showToast('📄', 'Downloading PDF...');
  });

  // Modal close
  document.getElementById('modalOverlay')?.addEventListener('click', e => {
    if (e.target === e.currentTarget) closeModal();
  });
  document.getElementById('modalClose')?.addEventListener('click', closeModal);
}

// ── TAB LOADER ──
function loadTab(tab) {
  const params = new URLSearchParams({
    date_from: currentDateFrom,
    date_to: currentDateTo,
    q: currentSearch,
  });

  switch (tab) {
    case 'overview':   fetchOverview(params); break;
    case 'students':   fetchRole('student', params); break;
    case 'lecturers':  fetchRole('lecturer', params); break;
    case 'staff':      fetchRole('staff', params); break;
    case 'books':      fetchBooks(params); break;
    case 'faculties':  fetchFaculties(params); break;
  }
}

// ── API CALLS ──
async function fetchOverview(params) {
  try {
    const res = await fetch(`/api/overview/?${params}`);
    const data = await res.json();
    renderStats(data.stats);
    renderNominations(data.nominations);
    renderList('overviewList', data.leaderboard, null, true);
  } catch (e) { console.error(e); }
}

async function fetchRole(role, params) {
  try {
    const res = await fetch(`/api/pemustaka-teraktif/?role=${role}&${params}`);
    const data = await res.json();
    renderList(`list-${role}s-visitors`, data.top_pengunjung, role, false, 'visits', 'kunjungan');
    renderList(`list-${role}s-borrowers`, data.top_peminjam, role, false, 'books', 'buku');
  } catch (e) { console.error(e); }
}

async function fetchBooks(params) {
  try {
    const res = await fetch(`/api/books/?${params}`);
    const data = await res.json();
    renderBooks(data.books);
    renderBorrowers(data.borrowers);
  } catch (e) { console.error(e); }
}

async function fetchFaculties(params) {
  try {
    const res = await fetch(`/api/faculties/?${params}`);
    const data = await res.json();
    renderFaculties(data.faculties);
    renderFacultyBooks(data.faculties);
    renderTopPerFaculty(data.top_per_faculty);
  } catch (e) { console.error(e); }
}

async function fetchMemberDetail(memberId, role) {
  try {
    const params = new URLSearchParams({ date_from: currentDateFrom, date_to: currentDateTo });
    const res = await fetch(`/api/member/${memberId}/?${params}`);
    const data = await res.json();
    renderModal(data, role);
  } catch (e) { console.error(e); }
}

// ── RENDERERS ──

function renderStats(stats) {
  animateCounter('statVisitors', stats.total_visitors);
  animateCounter('statBooks', stats.total_books);
  animateCounter('statMembers', stats.active_members);
  animateCounter('statFaculties', stats.total_faculties);
}

function renderNominations(noms) {
  const container = document.getElementById('nominations');
  if (!container) return;

  const roleConfig = {
    student:  { label: '🎓 Top Student',  cls: 'students' },
    lecturer: { label: '👨‍🏫 Top Lecturer', cls: 'lecturers' },
    staff:    { label: '👔 Top Staff',     cls: 'staff' },
  };

  container.innerHTML = Object.entries(roleConfig).map(([role, cfg]) => {
    const n = noms[role];
    if (!n) return `<div class="nom-card ${cfg.cls}"><div class="nom-label">${cfg.label}</div><div class="empty-state"><div class="icon">📭</div><p>No data yet</p></div></div>`;
    const { bg, text } = ROLE_COLORS[role];
    return `
      <div class="nom-card ${cfg.cls}">
        <div class="nom-label">${cfg.label}</div>
        <div class="nom-trophy">🥇</div>
        <div class="nom-avatar-big" style="background:${bg};color:${text}">${n.initials}</div>
        <div class="nom-winner">${n.name}</div>
        <div class="nom-detail">${n.faculty}${n.title ? ' · ' + n.title : ''}</div>
        <div class="nom-stat" style="background:${bg.replace('.18)', '.08)')};border:1px solid ${bg.replace('.18)', '.25)')}">
          <strong style="color:${text}">${n.visits}</strong>
          <span>visits this period</span>
        </div>
      </div>`;
  }).join('');
}

function renderList(containerId, items, forceRole, showRoleTag = false, scoreKey = 'visits', scoreLabel = 'visits') {
  const el = document.getElementById(containerId);
  if (!el) return;

  if (!items.length) {
    el.innerHTML = `<div class="empty-state"><div class="icon">📭</div><p>No results found.</p></div>`;
    return;
  }

  el.innerHTML = items.map((p, i) => {
    const role = forceRole || p.role;
    const { bg, text } = ROLE_COLORS[role] || ROLE_COLORS.student;
    const rankEl = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : (i + 1);
    const rankCls = i === 0 ? 'top1' : i === 1 ? 'top2' : i === 2 ? 'top3' : '';
    const roleTag = showRoleTag ? `<span style="font-size:.68rem;padding:2px 6px;border-radius:20px;background:${bg};color:${text};font-weight:700;margin-left:6px">${role}</span>` : '';
    return `
      <div class="lb-item ${rankCls}" data-id="${p.id}" data-role="${role}">
        <div class="lb-rank ${rankCls}">${rankEl}</div>
        <div class="lb-avatar" style="background:${bg};color:${text}">${p.initials}</div>
        <div class="lb-info">
          <div class="lb-name">${p.name}${roleTag}</div>
          <div class="lb-sub">${p.sub || p.faculty || ''}</div>
        </div>
        <div class="lb-score-wrap">
          <div class="lb-score" style="color:${text}">${p[scoreKey]}</div>
          <div class="lb-score-label">${scoreLabel.toUpperCase()}</div>
        </div>
      </div>`;
  }).join('');

  // Bind click for modal
  el.querySelectorAll('.lb-item').forEach(item => {
    item.addEventListener('click', () => fetchMemberDetail(item.dataset.id, item.dataset.role));
  });

  // Stagger entrance animation
  el.querySelectorAll('.lb-item').forEach((item, i) => {
    item.style.opacity = '0';
    item.style.transform = 'translateY(10px)';
    setTimeout(() => {
      item.style.transition = 'opacity .3s ease, transform .3s ease';
      item.style.opacity = '1';
      item.style.transform = 'translateY(0)';
    }, i * 40);
  });
}

function renderPodium(containerId, items, role) {
  const el = document.getElementById(containerId);
  if (!el || items.length < 2) { if (el) el.innerHTML = ''; return; }

  const order = [1, 0, 2];
  const cls = ['second', 'first', 'third'];
  const heights = [80, 110, 56];
  const { bg, text } = ROLE_COLORS[role] || ROLE_COLORS.student;

  el.innerHTML = order.map((idx, pos) => {
    const p = items[idx];
    if (!p) return '';
    return `
      <div class="podium-item ${cls[pos]}" data-id="${p.id}" data-role="${role}">
        <div class="podium-avatar" style="background:${bg};color:${text}">
          ${cls[pos] === 'first' ? '<div class="podium-crown">👑</div>' : ''}
          ${p.initials}
        </div>
        <div class="podium-name">${p.name}</div>
        <div class="podium-score">${p.visits} visits</div>
        <div class="podium-base" style="height:${heights[pos]}px">${idx + 1}</div>
      </div>`;
  }).join('');

  el.querySelectorAll('.podium-item').forEach(item => {
    item.addEventListener('click', () => fetchMemberDetail(item.dataset.id, item.dataset.role));
  });
}

function renderBooks(booksData) {
  const el = document.getElementById('booksList');
  if (!el) return;
  const max = Math.max(...booksData.map(b => b.borrows), 1);
  el.innerHTML = booksData.map((b, i) => {
    const icon = BOOK_ICONS[b.category] || BOOK_ICONS.default;
    const pct = Math.round(b.borrows / max * 100);
    return `
      <div class="book-item">
        <div class="book-rank">${i + 1}</div>
        <div class="book-icon">${icon}</div>
        <div class="book-info">
          <div class="book-title">${b.title}</div>
          <div class="book-author">${b.author} · ${b.category}</div>
        </div>
        <div class="book-bar-wrap">
          <div class="book-bar-track"><div class="book-bar-fill" style="width:0%" data-pct="${pct}%"></div></div>
          <div class="book-count">${b.borrows}×</div>
        </div>
      </div>`;
  }).join('');
  setTimeout(() => {
    el.querySelectorAll('.book-bar-fill').forEach(bar => { bar.style.width = bar.dataset.pct; });
  }, 200);
}

function renderBorrowers(borrowers) {
  renderList('borrowerList', borrowers, null, false, 'books', 'buku');
}

function renderFaculties(faculties) {
  const el = document.getElementById('facultyBars');
  if (!el) return;
  const max = Math.max(...faculties.map(f => f.visitors), 1);
  el.innerHTML = faculties.map(f => `
    <div class="fac-row">
      <div class="fac-dot" style="background:${f.color}"></div>
      <div class="fac-name-label">${f.name}</div>
      <div class="fac-bar-track"><div class="fac-bar-fill" style="background:${f.color}" data-pct="${Math.round(f.visitors/max*100)}%"></div></div>
      <div class="fac-count" style="color:${f.color}">${f.visitors}</div>
    </div>`).join('');
  setTimeout(() => {
    el.querySelectorAll('.fac-bar-fill').forEach(bar => { bar.style.width = bar.dataset.pct; });
  }, 200);
}

function renderFacultyBooks(faculties) {
  const el = document.getElementById('facultyBooks');
  if (!el) return;
  const sorted = [...faculties].sort((a, b) => b.books - a.books);
  const max = Math.max(...sorted.map(f => f.books), 1);
  el.innerHTML = sorted.map((f, i) => `
    <div class="book-item">
      <div class="book-rank">${i + 1}</div>
      <div class="book-icon" style="font-size:1rem">🏛️</div>
      <div class="book-info">
        <div class="book-title">${f.name}</div>
        <div class="book-author">${f.visitors} visitors</div>
      </div>
      <div class="book-bar-wrap">
        <div class="book-bar-track"><div class="book-bar-fill" style="background:${f.color};width:0%" data-pct="${Math.round(f.books/max*100)}%"></div></div>
        <div class="book-count">${f.books}×</div>
      </div>
    </div>`).join('');
  setTimeout(() => {
    el.querySelectorAll('.book-bar-fill').forEach(bar => { bar.style.width = bar.dataset.pct; });
  }, 300);
}

function renderTopPerFaculty(topList) {
  const el = document.getElementById('facultyTopStudents');
  if (!el) return;
  el.innerHTML = topList.map(t => {
    const { bg, text } = ROLE_COLORS[t.role] || ROLE_COLORS.student;
    return `
      <div class="book-item">
        <div class="lb-avatar" style="${bg ? `background:${bg};color:${text}` : ''};width:36px;height:36px;font-size:.85rem;flex-shrink:0">${t.initials}</div>
        <div class="book-info">
          <div class="book-title">${t.name}</div>
          <div class="book-author">${t.faculty}</div>
        </div>
        <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:.95rem;color:${text};flex-shrink:0">${t.visits}</div>
      </div>`;
  }).join('') || '<div class="empty-state"><div class="icon">📭</div><p>No data yet</p></div>';
}

// ── MODAL ──
function renderModal(data, role) {
  const { bg, text } = ROLE_COLORS[role] || ROLE_COLORS.student;
  const borrows = data.recent_borrows || [];
  const badges = data.badges || [];

  const shareText = encodeURIComponent(`Saya baru saja meraih prestasi di LibraryRank Universitas! Cek profil ${data.name} dengan ${data.visits_total} kunjungan.`);
  const shareUrl = encodeURIComponent(window.location.origin);

  document.getElementById('modalBody').innerHTML = `
    <div id="captureCard" style="padding:24px 10px 10px; border-radius:12px; background:var(--surface); text-align:center;">
      <div class="modal-avatar" style="background:${bg};color:${text};margin:0 auto 12px;width:72px;height:72px;font-size:1.8rem;line-height:72px;">${data.initials}</div>
      <div class="modal-name">${data.name}</div>
      <div class="modal-sub">${data.id} · ${data.faculty || data.department || ''} ${data.year ? '· ' + data.year : ''}</div>
      
      <div class="modal-stats" style="margin-top:20px; display:flex; justify-content:center; gap:16px;">
        <div class="modal-stat"><strong style="color:${text}">${data.visits_total}</strong><span>Total Visits</span></div>
        <div class="modal-stat"><strong style="color:var(--purple)">${data.books_total}</strong><span>Total Books</span></div>
        <div class="modal-stat"><strong style="color:var(--orange)">${data.streak}</strong><span>Day Streak 🔥</span></div>
      </div>

      ${badges.length ? `
      <div class="modal-badges" style="margin-top:24px; text-align:left; padding:0 10px;">
        <h4 style="margin-bottom:12px;font-size:.85rem;color:var(--muted);text-transform:uppercase;letter-spacing:1px;text-align:center;">🏆 Prestasi / Badges</h4>
        <div style="display:flex; flex-direction:column; gap:10px;">
          ${badges.map(b => `
            <div style="display:flex; align-items:center; gap:12px; padding:12px; border-radius:10px; border:1px solid var(--border); background:rgba(255,255,255,0.02)">
              <div style="font-size:1.8rem; width:48px; height:48px; display:flex; align-items:center; justify-content:center; background:${b.image_url ? 'none' : b.color+'20'}; border-radius:50%;flex-shrink:0;">
                ${b.image_url ? `<img src="${b.image_url}" alt="${b.name}" style="width:100%; height:100%; object-fit:contain;">` : b.icon}
              </div>
              <div style="flex:1;">
                <div style="font-weight:700; color:var(--text); font-size:1rem; margin-bottom:2px;">${b.name}</div>
                <div style="font-size:.8rem; color:var(--muted);">${b.desc}</div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>` : ''}
    </div>

    <!-- Share Buttons -->
    <div class="modal-share" style="margin-top:20px; padding-top:20px; border-top:1px solid var(--border);">
      <h4 style="margin-bottom:12px;font-size:.85rem;color:var(--muted);text-align:center;">📢 Share Pencapaianmu</h4>
      <div style="display:flex; justify-content:center; gap:8px; flex-wrap:wrap;">
        <a href="https://twitter.com/intent/tweet?text=${shareText}&url=${shareUrl}" target="_blank" style="padding:8px 14px; border-radius:20px; background:#1DA1F2; color:#fff; text-decoration:none; font-size:.8rem; font-weight:700;">🐦 Twitter</a>
        <a href="https://www.facebook.com/sharer/sharer.php?u=${shareUrl}&quote=${shareText}" target="_blank" style="padding:8px 14px; border-radius:20px; background:#1877F2; color:#fff; text-decoration:none; font-size:.8rem; font-weight:700;">📘 Facebook</a>
        <a href="https://api.whatsapp.com/send?text=${shareText}%20${shareUrl}" target="_blank" style="padding:8px 14px; border-radius:20px; background:#25D366; color:#fff; text-decoration:none; font-size:.8rem; font-weight:700;">💬 WhatsApp</a>
        <button onclick="downloadIGStory()" style="padding:8px 14px; border-radius:20px; background:linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888); color:#fff; border:none; cursor:pointer; font-size:.8rem; font-weight:700;">📸 IG Story</button>
      </div>
    </div>
  `;
  openModal();
}

async function downloadIGStory() {
  showToast('📸', 'Generating Story Image...', 2000);
  const card = document.getElementById('captureCard');
  if (!card) return;
  try {
    const canvas = await html2canvas(card, { 
      backgroundColor: '#151723', // matching theme background roughly
      scale: 2, 
      logging: false 
    });
    const link = document.createElement('a');
    link.download = 'LibraryRank_Achievement.jpg';
    link.href = canvas.toDataURL('image/jpeg', 0.9);
    link.click();
    showToast('✅', 'Image Downloaded! Share to Story.', 4000);
  } catch (e) {
    console.error(e);
    showToast('❌', 'Gagal memuat gambar', 3000);
  }
}

function openModal() {
  document.getElementById('modalOverlay').classList.add('open');
}
function closeModal() {
  document.getElementById('modalOverlay').classList.remove('open');
}

// ── UTILS ──
function animateCounter(id, target) {
  const el = document.getElementById(id);
  if (!el) return;
  const start = parseInt(el.textContent.replace(/,/g, '')) || 0;
  const step = (target - start) / 50;
  let cur = start;
  const t = setInterval(() => {
    cur = Math.min(cur + Math.abs(step), target);
    el.textContent = Math.round(cur).toLocaleString();
    if (Math.round(cur) >= target) clearInterval(t);
  }, 18);
}

function showToast(icon, msg, duration = 3000) {
  const el = document.getElementById('toast');
  document.getElementById('toastIcon').textContent = icon;
  document.getElementById('toastMsg').textContent = msg;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), duration);
}

// ── LIVE RANK SHUFFLE DEMO ──
// Every 10s, briefly animate two rows swapping in the student list to show "live" feel.
setInterval(() => {
  const list = document.getElementById('list-students-visitors');
  if (!list || currentTab !== 'students') return;
  const items = [...list.querySelectorAll('.lb-item')];
  if (items.length < 4) return;
  const i = Math.floor(Math.random() * (items.length - 1));
  items[i].classList.add('rank-down');
  items[i + 1].classList.add('rank-up');
  setTimeout(() => {
    items[i].classList.remove('rank-down');
    items[i + 1].classList.remove('rank-up');
  }, 1200);
}, 10000);
