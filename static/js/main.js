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
const BOOK_ICONS = { CS: '<span class="material-icons-outlined">computer</span>', Economics: '<span class="material-icons-outlined">trending_up</span>', Medicine: '<span class="material-icons-outlined">favorite</span>', Law: '<span class="material-icons-outlined">gavel</span>', Engineering: '<span class="material-icons-outlined">architecture</span>', Psychology: '<span class="material-icons-outlined">psychology</span>', Mathematics: '<span class="material-icons-outlined">straighten</span>', Chemistry: '<span class="material-icons-outlined">science</span>', default: '<span class="material-icons-outlined">library_books</span>' };
const getBadgeIconHtml = (icon) => {
  const badgeMap = {
    '🥇': '<span class="material-icons-outlined" style="color:#FFB800; font-size: 1.8rem;">workspace_premium</span>',
    '🥈': '<span class="material-icons-outlined" style="color:#94A3B8; font-size: 1.8rem;">workspace_premium</span>',
    '🥉': '<span class="material-icons-outlined" style="color:#CD7C4A; font-size: 1.8rem;">workspace_premium</span>',
    '📚': '<span class="material-icons-outlined" style="color:#8B5CF6; font-size: 1.8rem;">library_books</span>',
  };
  return badgeMap[icon] || icon;
};

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
      updateQuickSearch(currentSearch);
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
    showToast('<span class="material-icons-outlined" style="color:var(--green)">analytics</span>', 'Downloading Excel...');
  });

  document.getElementById('btnPdfExport')?.addEventListener('click', () => {
    const url = `/export/pdf/?date_from=${currentDateFrom}&date_to=${currentDateTo}`;
    window.location.href = url;
    showToast('<span class="material-icons-outlined" style="color:var(--red)">description</span>', 'Downloading PDF...');
  });

  // Modal close
  document.getElementById('modalOverlay')?.addEventListener('click', e => {
    if (e.target === e.currentTarget) closeModal();
  });
  document.getElementById('modalClose')?.addEventListener('click', closeModal);

  // Panduan Click
  document.getElementById('btnPanduan')?.addEventListener('click', e => {
    e.preventDefault();
    openPanduanModal();
  });

  // Merch Slide Click (Redeem)
  document.querySelectorAll('.merch-slide').forEach(slide => {
    slide.addEventListener('click', () => {
      const id = slide.dataset.id;
      const name = slide.dataset.name;
      const cost = slide.dataset.cost;
      const stock = slide.dataset.stock;
      openRedeemModal(id, name, cost, stock);
    });
  });
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
    renderList('overviewList', data.leaderboard, null, true, 'visits', 'XP');
    if (typeof Chart !== 'undefined') renderChart(data);
  } catch (e) { console.error(e); }
}

async function updateQuickSearch(q) {
  const quickCard = document.getElementById('searchResultQuick');
  if (!quickCard) return;
  if (!q || q.length < 3) {
    quickCard.style.display = 'none';
    return;
  }
  
  try {
    const params = new URLSearchParams({ q: q });
    const res = await fetch(`/api/overview/?${params}`);
    const data = await res.json();
    if (data.leaderboard && data.leaderboard.length > 0) {
      const p = data.leaderboard[0];
      
      // If we find an exact match on NIM or Name, or just show the top result if it's very relevant
      // We will just show the top result if it exists.
      document.getElementById('quickName').textContent = p.name;
      document.getElementById('quickFaculty').textContent = p.id + ' • ' + (p.faculty || '');
      document.getElementById('quickXP').textContent = p.visits + ' XP';
      document.getElementById('quickAvatar').textContent = p.initials;
      
      const role = p.role || 'student';
      const { bg, text } = ROLE_COLORS[role] || ROLE_COLORS.student;
      document.getElementById('quickAvatar').style.background = bg;
      document.getElementById('quickAvatar').style.color = text;
      
      quickCard.style.display = 'flex';
      quickCard.onclick = () => fetchMemberDetail(p.id, role);
      quickCard.style.cursor = 'pointer';
      
      // Hover effect
      quickCard.onmouseenter = () => quickCard.style.transform = 'translateY(-2px)';
      quickCard.onmouseleave = () => quickCard.style.transform = 'translateY(0)';
    } else {
      quickCard.style.display = 'none';
    }
  } catch(e) {}
}

async function fetchRole(role, params) {
  try {
    const res = await fetch(`/api/pemustaka-teraktif/?role=${role}&${params}`);
    const data = await res.json();
    renderList(`list-${role}-xp`, data.top_xp, role, false, 'total_p', 'XP');
    renderList(`list-${role}-visitors`, data.top_pengunjung, role, false, 'visits', 'Kedatangan');
    renderList(`list-${role}-borrowers`, data.top_peminjam, role, false, 'books', 'Buku');
    renderList(`list-${role}-seminar`, data.top_seminar, role, false, 'visits', 'Seminar');
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

let overviewChartInstance = null;

function renderChart(data) {
  const ctx = document.getElementById('overviewChart');
  if (!ctx) return;
  
  let dataPoints = data.daily_visits;
  if (!dataPoints || dataPoints.length !== 7) {
    // Fallback if not provided or wrong format (Monday to Saturday randomized, Sunday is 0)
    const stats = data.stats || {};
    const total = stats.total_visitors || 500;
    dataPoints = Array.from({length: 6}, () => Math.floor((Math.random() * 0.3 + 0.1) * (total / 6)));
    dataPoints.push(0); // Sunday is always 0
  }
  
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const textColor = isDark ? '#94A3B8' : '#64748B';
  const gridColor = isDark ? '#334155' : '#E2E8F0';

  if (overviewChartInstance) overviewChartInstance.destroy();
  
  overviewChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min'],
      datasets: [{
        label: 'Kunjungan Harian',
        data: dataPoints,
        borderColor: 'var(--primary, #818CF8)',
        backgroundColor: 'rgba(129, 140, 248, 0.15)',
        fill: true,
        tension: 0.4,
        borderWidth: 3,
        pointBackgroundColor: 'var(--primary, #818CF8)',
        pointBorderColor: 'var(--surface, #fff)',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, grid: { color: gridColor }, ticks: { color: textColor } },
        x: { grid: { display: false }, ticks: { color: textColor } }
      }
    }
  });
}

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
    student:  { label: '<span class="material-icons-outlined" style="vertical-align: middle; margin-right: 4px; font-size: 1.15rem; color: var(--gold);">school</span> Top Student',  cls: 'students' },
    lecturer: { label: '<span class="material-icons-outlined" style="vertical-align: middle; margin-right: 4px; font-size: 1.15rem; color: var(--gold);">person</span> Top Lecturer', cls: 'lecturers' },
    staff:    { label: '<span class="material-icons-outlined" style="vertical-align: middle; margin-right: 4px; font-size: 1.15rem; color: var(--gold);">work</span> Top Staff',     cls: 'staff' },
  };

  container.innerHTML = Object.entries(roleConfig).map(([role, cfg]) => {
    const n = noms[role];
    if (!n) return `<div class="nom-card ${cfg.cls}"><div class="nom-label">${cfg.label}</div><div class="empty-state"><div class="icon"><span class="material-icons-outlined" style="font-size: 2.2rem; color: var(--muted); display: block; margin-bottom: 8px;">inbox</span></div><p>No data yet</p></div></div>`;
    const { bg, text } = ROLE_COLORS[role];
    return `
      <div class="nom-card ${cfg.cls}">
        <div class="nom-label">${cfg.label}</div>
        <div class="nom-trophy"><span class="material-icons-outlined" style="font-size: 1.8rem; color: var(--gold);">workspace_premium</span></div>
        <div class="nom-avatar-big" style="background:${bg};color:${text}">${n.initials}</div>
        <div class="nom-winner">${n.name}</div>
        <div class="nom-detail">${n.faculty}${n.title ? ' · ' + n.title : ''}</div>
        <div class="nom-stat" style="background:${bg.replace('.18)', '.08)')};border:1px solid ${bg.replace('.18)', '.25)')}">
          <strong style="color:${text}">${n.visits}</strong>
          <span>XP this period</span>
        </div>
      </div>`;
  }).join('');
}

function renderList(containerId, items, forceRole, showRoleTag = false, scoreKey = 'visits', scoreLabel = 'visits') {
  const el = document.getElementById(containerId);
  if (!el) return;

  if (!items.length) {
    el.innerHTML = `<div class="empty-state"><div class="icon"><span class="material-icons-outlined" style="font-size: 2.2rem; color: var(--muted); display: block; margin-bottom: 8px;">inbox</span></div><p>No results found.</p></div>`;
    return;
  }

  el.innerHTML = items.map((p, i) => {
    const role = forceRole || p.role;
    const { bg, text } = ROLE_COLORS[role] || ROLE_COLORS.student;
    const rankEl = i === 0 ? '<span class="material-icons-outlined">workspace_premium</span>' : i === 1 ? '<span class="material-icons-outlined">workspace_premium</span>' : i === 2 ? '<span class="material-icons-outlined">workspace_premium</span>' : (i + 1);
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
          ${cls[pos] === 'first' ? '<div class="podium-crown"><span class="material-icons-outlined" style="font-size: 1.4rem; color: var(--gold);">emoji_events</span></div>' : ''}
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
      <div class="book-icon" style="display:flex; align-items:center;"><span class="material-icons-outlined" style="font-size: 1.1rem; color: var(--gold);">account_balance</span></div>
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
  }).join('') || '<div class="empty-state"><div class="icon"><span class="material-icons-outlined" style="font-size: 2.2rem; color: var(--muted); display: block; margin-bottom: 8px;">inbox</span></div><p>No data yet</p></div>';
}

// ── MODAL ──
function renderModal(data, role) {
  const { bg, text } = ROLE_COLORS[role] || ROLE_COLORS.student;
  const borrows = data.recent_borrows || [];
  const badges = data.badges || [];

  const shareText = encodeURIComponent(`Saya baru saja meraih prestasi di LibraryRank Universitas! Cek profil ${data.name} dengan total XP ${data.visits_total}.`);
  const shareUrl = encodeURIComponent(window.location.origin);
  const lvl = data.level || { name: 'Visitor', progress_perc: 0, current_xp: 0, max_xp: 100, color: '#95a5a6' };

  document.getElementById('modalBody').innerHTML = `
    <div id="captureCard" style="padding:24px 10px 10px; border-radius:12px; background:var(--surface); text-align:center;">
      <div class="modal-avatar" style="border: 3px solid ${lvl.color}; background:${bg};color:${text};margin:0 auto 12px;width:72px;height:72px;font-size:1.8rem;line-height:66px;">${data.initials}</div>
      <div class="modal-name">${data.name}</div>
      <div class="modal-sub">${data.id} · ${data.faculty || data.department || ''} ${data.year ? '· ' + data.year : ''}</div>
      
      <div style="margin: 16px auto 0; max-width: 80%;">
        <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:6px; font-size:0.8rem; font-weight:700;">
          <span style="color:${lvl.color}; text-transform:uppercase; font-size:11px; letter-spacing:1px">${lvl.name}</span>
          <span style="color:var(--text); font-size:11px">${lvl.current_xp} / ${lvl.max_xp == lvl.current_xp ? 'MAX' : lvl.max_xp} XP</span>
        </div>
        <div style="height:8px; border-radius:4px; background:var(--border); overflow:hidden;">
          <div style="height:100%; width:${lvl.progress_perc}%; background:${lvl.color}; transition: width 1s ease;"></div>
        </div>
      </div>
      
      <div class="modal-stats" style="margin-top:20px; display:flex; justify-content:center; gap:16px;">
        <div class="modal-stat"><strong style="color:${text}">${data.visits_total}</strong><span>Total Visits</span></div>
        <div class="modal-stat"><strong style="color:var(--purple)">${data.books_total}</strong><span>Total Books</span></div>
        <div class="modal-stat"><strong style="color:var(--orange)">${data.streak}</strong><span>Day Streak <span class="material-icons-outlined" style="vertical-align: middle; color: var(--orange); font-size: 1.1rem;">local_fire_department</span></span></div>
      </div>

      ${badges.length ? `
      <div class="modal-badges" style="margin-top:24px; text-align:left; padding:0 10px;">
        <h4 style="margin-bottom:12px;font-size:.85rem;color:var(--muted);text-transform:uppercase;letter-spacing:1px;text-align:center;"><span class="material-icons-outlined" style="vertical-align: middle; color: var(--gold); font-size: 1.1rem; margin-right: 4px;">emoji_events</span> Prestasi / Badges</h4>
        <div style="display:flex; flex-direction:column; gap:10px;">
          ${badges.map(b => `
            <div style="display:flex; align-items:center; gap:12px; padding:12px; border-radius:10px; border:1px solid var(--border); background:rgba(47,49,133,0.04)">
              <div style="font-size:1.8rem; width:48px; height:48px; display:flex; align-items:center; justify-content:center; background:${b.image_url ? 'none' : b.color+'20'}; border-radius:50%;flex-shrink:0;">
                ${b.image_url ? `<img src="${b.image_url}" alt="${b.name}" style="width:100%; height:100%; object-fit:contain;">` : getBadgeIconHtml(b.icon)}
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
      <h4 style="margin-bottom:12px;font-size:.85rem;color:var(--muted);text-align:center;"><span class="material-icons-outlined" style="vertical-align: middle; color: var(--gold); font-size: 1.1rem; margin-right: 4px;">campaign</span> Share Pencapaianmu</h4>
      <div style="display:flex; justify-content:center; gap:8px; flex-wrap:wrap;">
        <a href="https://twitter.com/intent/tweet?text=${shareText}&url=${shareUrl}" target="_blank" style="display:inline-flex; align-items:center; padding:8px 14px; border-radius:20px; background:#1DA1F2; color:#fff; text-decoration:none; font-size:.8rem; font-weight:700;"><span class="material-icons-outlined" style="font-size: 0.9rem; margin-right: 4px;">send</span> Twitter</a>
        <a href="https://www.facebook.com/sharer/sharer.php?u=${shareUrl}&quote=${shareText}" target="_blank" style="display:inline-flex; align-items:center; padding:8px 14px; border-radius:20px; background:#1877F2; color:#fff; text-decoration:none; font-size:.8rem; font-weight:700;"><span class="material-icons-outlined" style="font-size: 0.9rem; margin-right: 4px;">facebook</span> Facebook</a>
        <a href="https://api.whatsapp.com/send?text=${shareText}%20${shareUrl}" target="_blank" style="display:inline-flex; align-items:center; padding:8px 14px; border-radius:20px; background:#25D366; color:#fff; text-decoration:none; font-size:.8rem; font-weight:700;"><span class="material-icons-outlined" style="font-size: 0.9rem; margin-right: 4px;">chat</span> WhatsApp</a>
        <button onclick="downloadIGStory()" style="display:inline-flex; align-items:center; padding:8px 14px; border-radius:20px; background:linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888); color:#fff; border:none; cursor:pointer; font-size:.8rem; font-weight:700;"><span class="material-icons-outlined" style="font-size: 0.9rem; margin-right: 4px;">photo_camera</span> IG Story</button>
      </div>
    </div>
  `;
  openModal();
}

async function downloadIGStory() {
  showToast('<span class="material-icons-outlined">photo_camera</span>', 'Generating Story Image...', 2000);
  const card = document.getElementById('captureCard');
  if (!card) return;
  try {
    const canvas = await html2canvas(card, { 
      backgroundColor: '#282A6A', // matching theme background roughly
      scale: 2, 
      logging: false 
    });
    const link = document.createElement('a');
    link.download = 'LibraryRank_Achievement.jpg';
    link.href = canvas.toDataURL('image/jpeg', 0.9);
    link.click();
    showToast('<span class="material-icons-outlined">check_circle</span>', 'Image Downloaded! Share to Story.', 4000);
  } catch (e) {
    console.error(e);
    showToast('<span class="material-icons-outlined">cancel</span>', 'Gagal memuat gambar', 3000);
  }
}

function openModal() {
  document.getElementById('modalOverlay').classList.add('open');
}
function closeModal() {
  document.getElementById('modalOverlay').classList.remove('open');
}

function openPanduanModal() {
  const container = document.getElementById('modalBody');
  if (!container) return;

  container.innerHTML = `
    <div class="guide-modal-wrapper" style="text-align:left; padding: 10px 5px;">
      <h2 style="display:flex; align-items:center; gap:8px; margin-bottom:16px; font-size:1.4rem; color:var(--text); font-weight:800;">
        <span class="material-icons-outlined" style="color:var(--gold); font-size:1.8rem;">menu_book</span>
        Panduan Leaderboard LibraryRank
      </h2>
      
      <!-- Tab Menu Modal -->
      <div class="guide-tabs" style="display:flex; border-bottom:2px solid var(--border); margin-bottom:18px; gap:4px; overflow-x:auto; padding-bottom:2px;">
        <button class="guide-tab-btn active" data-guide-tab="about" style="flex:1; padding:10px 6px; border:none; background:none; font-family:'Inter',sans-serif; font-size:0.85rem; font-weight:700; color:var(--gold); border-bottom:3px solid var(--gold); cursor:pointer; text-align:center; transition:all 0.2s; white-space:nowrap;"><span class="material-icons-outlined" style="font-size:0.95rem; vertical-align:middle; margin-right:4px;">menu_book</span> Tentang</button>
        <button class="guide-tab-btn" data-guide-tab="points" style="flex:1; padding:10px 6px; border:none; background:none; font-family:'Inter',sans-serif; font-size:0.85rem; font-weight:700; color:var(--muted); border-bottom:3px solid transparent; cursor:pointer; text-align:center; transition:all 0.2s; white-space:nowrap;"><span class="material-icons-outlined" style="font-size:0.95rem; vertical-align:middle; margin-right:4px;">trending_up</span> Poin (XP)</button>
        <button class="guide-tab-btn" data-guide-tab="badges" style="flex:1; padding:10px 6px; border:none; background:none; font-family:'Inter',sans-serif; font-size:0.85rem; font-weight:700; color:var(--muted); border-bottom:3px solid transparent; cursor:pointer; text-align:center; transition:all 0.2s; white-space:nowrap;"><span class="material-icons-outlined" style="font-size:0.95rem; vertical-align:middle; margin-right:4px;">workspace_premium</span> Badges</button>
        <button class="guide-tab-btn" data-guide-tab="levels" style="flex:1; padding:10px 6px; border:none; background:none; font-family:'Inter',sans-serif; font-size:0.85rem; font-weight:700; color:var(--muted); border-bottom:3px solid transparent; cursor:pointer; text-align:center; transition:all 0.2s; white-space:nowrap;"><span class="material-icons-outlined" style="font-size:0.95rem; vertical-align:middle; margin-right:4px;">military_tech</span> Levels</button>
      </div>

      <!-- Tab Content Modal -->
      <div class="guide-panels">
        <!-- 1. TENTANG -->
        <div class="guide-panel active" id="gpanel-about" style="display:block;">
          <p style="font-size:0.92rem; line-height:1.6; color:var(--text); margin-bottom:12px;">
            Selamat datang di <strong>LibraryRank</strong>, platform gamifikasi resmi Perpustakaan UMS! Platform ini dirancang khusus untuk mengapresiasi keaktifan kunjungan fisik, literasi, peminjaman buku, serta keikutsertaan event ilmiah dari para civitas akademika (Mahasiswa, Dosen, &amp; Tendik/Staff).
          </p>
          <div style="background:rgba(255,184,0,0.06); border-left:4px solid var(--gold); padding:12px; border-radius:4px; margin-top:14px; font-size:0.85rem; line-height:1.5; color:var(--text);">
            <strong style="color:var(--gold); display:block; margin-bottom:4px; font-size:0.9rem;"><span class="material-icons-outlined" style="font-size: 1.1rem; vertical-align: middle; color: var(--gold); margin-right: 4px;">track_changes</span> Misi Utama Kami:</strong>
            Membangun atmosfer akademik yang kompetitif dan menyenangkan, serta memotivasi minat baca melalui perolehan poin prestasi, lencana kehormatan (badges), dan reward eksklusif perpustakaan.
          </div>
        </div>

        <!-- 2. POIN (XP) -->
        <div class="guide-panel" id="gpanel-points" style="display:none;">
          <p style="font-size:0.9rem; color:var(--muted); margin-bottom:14px;">Dapatkan poin XP (Experience Points) dari setiap aktivitas keaktifan Anda di perpustakaan:</p>
          <div style="display:flex; flex-direction:column; gap:10px;">
            <div style="display:flex; align-items:center; justify-content:space-between; padding:12px; border-radius:10px; border:1px solid var(--border); background:rgba(77,166,255,0.05);">
              <div style="display:flex; align-items:center; gap:10px;">
                <span style="font-size:1.5rem; display:flex; align-items:center;"><span class="material-icons-outlined" style="font-size:1.6rem; color: var(--blue);">directions_walk</span></span>
                <div>
                  <strong style="display:block; font-size:0.92rem; color:var(--text);">Kunjungan Fisik (Gate Scan)</strong>
                  <span style="font-size:0.78rem; color:var(--muted);">Terdeteksi otomatis saat memindai kartu di pintu masuk.</span>
                </div>
              </div>
              <strong style="color:var(--blue); font-size:1.1rem;">+10 XP</strong>
            </div>

            <div style="display:flex; align-items:center; justify-content:space-between; padding:12px; border-radius:10px; border:1px solid var(--border); background:rgba(61,224,138,0.05);">
              <div style="display:flex; align-items:center; gap:10px;">
                <span style="font-size:1.5rem; display:flex; align-items:center;"><span class="material-icons-outlined" style="font-size:1.6rem; color: var(--green);">library_books</span></span>
                <div>
                  <strong style="display:block; font-size:0.92rem; color:var(--text);">Peminjaman Buku (Sirkulasi)</strong>
                  <span style="font-size:0.78rem; color:var(--muted);">Dihitung per transaksi peminjaman buku koha yang sah.</span>
                </div>
              </div>
              <strong style="color:var(--green); font-size:1.1rem;">+25 XP</strong>
            </div>

            <div style="display:flex; align-items:center; justify-content:space-between; padding:12px; border-radius:10px; border:1px solid var(--border); background:rgba(255,145,77,0.05);">
              <div style="display:flex; align-items:center; gap:10px;">
                <span style="font-size:1.5rem; display:flex; align-items:center;"><span class="material-icons-outlined" style="font-size:1.6rem; color: var(--orange);">school</span></span>
                <div>
                  <strong style="display:block; font-size:0.92rem; color:var(--text);">Seminar &amp; Workshop Literasi</strong>
                  <span style="font-size:0.78rem; color:var(--muted);">Diberikan oleh admin pustakawan saat Anda mengikuti event perpustakaan.</span>
                </div>
              </div>
              <strong style="color:var(--orange); font-size:1.1rem;">+15 XP</strong>
            </div>
          </div>
        </div>

        <!-- 3. BADGES -->
        <div class="guide-panel" id="gpanel-badges" style="display:none;">
          <p style="font-size:0.9rem; color:var(--muted); margin-bottom:14px;">Lencana kehormatan yang didapatkan secara otomatis jika memenuhi kriteria tertentu:</p>
          <div style="display:flex; flex-direction:column; gap:10px;">
            <div style="display:flex; align-items:center; gap:12px; padding:12px; border-radius:10px; border:1px solid var(--border); background:rgba(255,255,255,0.02);">
              <div style="font-size:1.8rem; width:44px; height:44px; display:flex; align-items:center; justify-content:center; background:#bdc3c720; border-radius:50%; flex-shrink:0;"><span class="material-icons-outlined" style="color:#94A3B8; font-size:1.8rem;">workspace_premium</span></div>
              <div>
                <strong style="display:block; font-size:0.95rem; color:white; font-weight:700;">Weekly Warrior</strong>
                <span style="font-size:0.8rem; color:var(--muted);">Melakukan kunjungan fisik ke perpustakaan minimal 3 kali dalam seminggu.</span>
              </div>
            </div>

            <div style="display:flex; align-items:center; gap:12px; padding:12px; border-radius:10px; border:1px solid var(--border); background:rgba(255,255,255,0.02);">
              <div style="font-size:1.8rem; width:44px; height:44px; display:flex; align-items:center; justify-content:center; background:#9b59b620; border-radius:50%; flex-shrink:0;"><span class="material-icons-outlined" style="color:#8B5CF6; font-size:1.8rem;">library_books</span></div>
              <div>
                <strong style="display:block; font-size:0.95rem; color:white; font-weight:700;">Book Worm</strong>
                <span style="font-size:0.8rem; color:var(--muted);">Meminjam lebih dari 5 buku dalam periode satu semester.</span>
              </div>
            </div>

            <div style="display:flex; align-items:center; gap:12px; padding:12px; border-radius:10px; border:1px solid var(--border); background:rgba(255,255,255,0.02);">
              <div style="font-size:1.8rem; width:44px; height:44px; display:flex; align-items:center; justify-content:center; background:#f1c40f20; border-radius:50%; flex-shrink:0;"><span class="material-icons-outlined" style="color:#FFB800; font-size:1.8rem;">workspace_premium</span></div>
              <div>
                <strong style="display:block; font-size:0.95rem; color:white; font-weight:700;">Library Legend</strong>
                <span style="font-size:0.8rem; color:var(--muted);">Menembus jajaran prestisius Top 10 Leaderboard pada bulan berjalan.</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 4. LEVELS -->
        <div class="guide-panel" id="gpanel-levels" style="display:none;">
          <p style="font-size:0.9rem; color:var(--muted); margin-bottom:12px;">Akumulasi XP Anda menentukan tingkatan profil level Anda:</p>
          <div class="guide-levels-grid">
            <div style="padding:10px; border-radius:8px; border:1px solid var(--border); text-align:center; background:rgba(255,255,255,0.02);">
              <div style="font-weight:bold; font-size:0.9rem; color:#95a5a6;">Egg / Pengunjung</div>
              <div style="font-size:0.75rem; color:var(--muted); margin-top:2px;">0 - 100 XP</div>
            </div>
            <div style="padding:10px; border-radius:8px; border:1px solid var(--border); text-align:center; background:rgba(255,255,255,0.02);">
              <div style="font-weight:bold; font-size:0.9rem; color:#3498db; display:flex; align-items:center; justify-content:center; gap:4px;"><span class="material-icons-outlined" style="font-size:0.95rem; color:#3498db;">auto_stories</span> Pembaca</div>
              <div style="font-size:0.75rem; color:var(--muted); margin-top:2px;">101 - 300 XP</div>
            </div>
            <div style="padding:10px; border-radius:8px; border:1px solid var(--border); text-align:center; background:rgba(255,255,255,0.02);">
              <div style="font-weight:bold; font-size:0.9rem; color:#2ecc71; display:flex; align-items:center; justify-content:center; gap:4px;"><span class="material-icons-outlined" style="font-size:0.95rem; color:#2ecc71;">edit</span> Pelajar</div>
              <div style="font-size:0.75rem; color:var(--muted); margin-top:2px;">301 - 700 XP</div>
            </div>
            <div style="padding:10px; border-radius:8px; border:1px solid var(--border); text-align:center; background:rgba(255,255,255,0.02);">
              <div style="font-weight:bold; font-size:0.9rem; color:#9b59b6; display:flex; align-items:center; justify-content:center; gap:4px;"><span class="material-icons-outlined" style="font-size:0.95rem; color:#9b59b6;">science</span> Peneliti</div>
              <div style="font-size:0.75rem; color:var(--muted); margin-top:2px;">701 - 1500 XP</div>
            </div>
            <div style="padding:10px; border-radius:8px; border:1px solid var(--border); text-align:center; background:rgba(255,255,255,0.02);">
              <div style="font-weight:bold; font-size:0.9rem; color:#e67e22; display:flex; align-items:center; justify-content:center; gap:4px;"><span class="material-icons-outlined" style="font-size:0.95rem; color:#e67e22;">school</span> Cendekia</div>
              <div style="font-size:0.75rem; color:var(--muted); margin-top:2px;">1501 - 3000 XP</div>
            </div>
            <div style="padding:10px; border-radius:8px; border:1px solid var(--border); text-align:center; background:rgba(255,255,255,0.02);">
              <div style="font-weight:bold; font-size:0.9rem; color:#f1c40f; display:flex; align-items:center; justify-content:center; gap:4px;"><span class="material-icons-outlined" style="font-size:0.95rem; color:#f1c40f;">workspace_premium</span> Legenda Perpus</div>
              <div style="font-size:0.75rem; color:var(--muted); margin-top:2px;">3001+ XP</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;

  // Bind tab switching events inside Guide Modal
  const tabBtns = container.querySelectorAll('.guide-tab-btn');
  const panels = container.querySelectorAll('.guide-panel');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const activeTab = btn.dataset.guideTab;

      // Update button visual
      tabBtns.forEach(b => {
        b.style.color = 'var(--muted)';
        b.style.borderBottom = '3px solid transparent';
        b.classList.remove('active');
      });
      btn.style.color = 'var(--gold)';
      btn.style.borderBottom = '3px solid var(--gold)';
      btn.classList.add('active');

      // Update panel visibility
      panels.forEach(p => {
        p.style.display = 'none';
        p.classList.remove('active');
      });
      const activePanel = container.querySelector(`#gpanel-${activeTab}`);
      if (activePanel) {
        activePanel.style.display = 'block';
        activePanel.classList.add('active');
      }
    });
  });

  openModal();
}


function openRedeemModal(rewardId, rewardName, rewardCost, rewardStock) {
  const container = document.getElementById('modalBody');
  if (!container) return;

  // Render Step 1: Input NIM
  container.innerHTML = `
    <div class="redeem-modal-wrapper" style="text-align:left; padding: 10px 5px;">
      <h2 style="display:flex; align-items:center; gap:8px; margin-bottom:12px; font-size:1.3rem; color:var(--text); font-weight:800;">
        <span class="material-icons-outlined" style="color:var(--gold); font-size:1.8rem;">redeem</span>
        Tukar Poin / Redeem
      </h2>
      
      <div style="background:rgba(255,184,0,0.06); padding:14px; border-radius:12px; border:1px solid rgba(255,184,0,0.15); margin-bottom:18px;">
        <h4 style="margin:0 0 4px 0; font-size:0.95rem; color:var(--text); font-weight:700; display:flex; align-items:center; gap:4px;"><span class="material-icons-outlined" style="color:var(--gold); font-size:1.15rem;">redeem</span> ${rewardName}</h4>
        <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.82rem; color:var(--muted); margin-top:8px;">
          <span>Biaya Penukaran: <strong style="color:var(--gold); font-size:0.9rem;">${rewardCost} XP</strong></span>
          <span>Tersedia: <strong style="color:var(--text);">${rewardStock} unit</strong></span>
        </div>
      </div>

      <div id="redeemStepContainer">
        <!-- STEP 1 FORM -->
        <form id="otpRequestForm">
          <label style="display:block; font-size:0.82rem; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;">Masukkan NIM / ID Anggota Anda:</label>
          <div style="position:relative; margin-bottom:14px;">
            <span class="material-icons-outlined" style="position:absolute; left:12px; top:50%; transform:translateY(-50%); color:var(--muted); font-size:1.2rem;">badge</span>
            <input type="text" id="redeemMemberId" placeholder="Contoh: L200220001" required 
              style="width:100%; background:var(--surface2); border:1px solid var(--border); border-radius:10px; padding:12px 12px 12px 38px; color:var(--text); font-family:inherit; font-size:0.92rem; outline:none; transition:border-color 0.2s;">
          </div>
          
          <div id="redeemError" style="color:var(--red); font-size:0.8rem; font-weight:600; margin-bottom:14px; display:none;"></div>
          
          <button type="submit" id="btnRequestOtp" style="width:100%; background:var(--blue); border:none; color:white; padding:12px; border-radius:10px; font-family:'Inter',sans-serif; font-size:0.9rem; font-weight:700; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:8px; transition:background 0.2s;">
            <span class="material-icons-outlined" style="font-size:1.2rem;">send</span> Kirim Kode OTP Verifikasi
          </button>
        </form>
      </div>
    </div>
  `;

  // Submit Handler for Step 1 (Request OTP)
  const otpRequestForm = document.getElementById('otpRequestForm');
  otpRequestForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const memberId = document.getElementById('redeemMemberId').value.trim();
    const btn = document.getElementById('btnRequestOtp');
    const errDiv = document.getElementById('redeemError');
    
    // UI Loading state
    btn.disabled = true;
    btn.innerHTML = `<span class="material-icons-outlined" style="animation: spin 1s linear infinite; display: inline-block;">sync</span> Mengirim OTP...`;
    errDiv.style.display = 'none';

    try {
      const response = await fetch('/api/redeem/request-otp/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': CSRF_TOKEN
        },
        body: JSON.stringify({ member_id: memberId, reward_id: rewardId })
      });

      const result = await response.json();
      
      if (!response.ok || !result.success) {
        throw new Error(result.error || 'Terjadi kesalahan saat meminta OTP.');
      }

      // Step 2: Show OTP Verification Form
      renderOtpVerificationStep(memberId, result.email_masked);

    } catch (error) {
      errDiv.textContent = error.message;
      errDiv.style.display = 'block';
      btn.disabled = false;
      btn.innerHTML = `<span class="material-icons-outlined" style="font-size:1.2rem;">send</span> Kirim Kode OTP Verifikasi`;
    }
  });

  // Render Step 2: Input OTP Code
  function renderOtpVerificationStep(memberId, maskedEmail) {
    const stepContainer = document.getElementById('redeemStepContainer');
    stepContainer.innerHTML = `
      <form id="otpVerifyForm">
        <div style="background:rgba(77,166,255,0.06); padding:12px; border-radius:10px; border:1px solid rgba(77,166,255,0.15); margin-bottom:16px; font-size:0.82rem; line-height:1.5; color:var(--text); display:flex; align-items:flex-start; gap:8px;">
          <span class="material-icons-outlined" style="font-size: 1.2rem; color: var(--blue); margin-top:2px;">campaign</span>
          <div>
            Kode verifikasi OTP telah dikirim ke email kampus Anda:<br>
            <strong style="color:var(--blue);">${maskedEmail}</strong>
          </div>
        </div>

        <label style="display:block; font-size:0.82rem; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;">Masukkan 6-Digit OTP:</label>
        <div style="position:relative; margin-bottom:14px;">
          <span class="material-icons-outlined" style="position:absolute; left:12px; top:50%; transform:translateY(-50%); color:var(--muted); font-size:1.2rem;">lock</span>
          <input type="text" id="redeemOtp" maxlength="6" placeholder="******" required 
            style="width:100%; background:var(--surface2); border:1px solid var(--border); border-radius:10px; padding:12px 12px 12px 38px; color:var(--text); font-family:inherit; font-size:1.1rem; font-weight:700; letter-spacing:6px; text-align:center; outline:none; transition:border-color 0.2s;">
        </div>

        <div id="redeemError" style="color:var(--red); font-size:0.8rem; font-weight:600; margin-bottom:14px; display:none;"></div>

        <div style="display:flex; gap:8px;">
          <button type="button" id="btnBackToStep1" style="flex:1; background:var(--surface3); border:none; color:var(--text); padding:12px; border-radius:10px; font-family:inherit; font-size:0.9rem; font-weight:700; cursor:pointer; transition:background 0.2s;">Kembali</button>
          <button type="submit" id="btnConfirmRedeem" style="flex:2; background:var(--green); border:none; color:white; padding:12px; border-radius:10px; font-family:'Inter',sans-serif; font-size:0.9rem; font-weight:700; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:6px; transition:background 0.2s;">
            <span class="material-icons-outlined" style="font-size:1.2rem;">check_circle</span> Verifikasi &amp; Tukar
          </button>
        </div>
      </form>
    `;

    // Back Button Handler
    document.getElementById('btnBackToStep1').addEventListener('click', () => {
      openRedeemModal(rewardId, rewardName, rewardCost, rewardStock);
    });

    // Verification Form Submit Handler
    const otpVerifyForm = document.getElementById('otpVerifyForm');
    otpVerifyForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const otpCode = document.getElementById('redeemOtp').value.trim();
      const btn = document.getElementById('btnConfirmRedeem');
      const errDiv = document.getElementById('redeemError');

      btn.disabled = true;
      btn.innerHTML = `<span class="material-icons-outlined" style="animation: spin 1s linear infinite; display: inline-block;">sync</span> Memverifikasi...`;
      errDiv.style.display = 'none';

      try {
        const response = await fetch('/api/redeem/confirm/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN
          },
          body: JSON.stringify({ member_id: memberId, otp: otpCode })
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
          throw new Error(result.error || 'Terjadi kesalahan saat verifikasi OTP.');
        }

        // Step 3: Show Success Screen with Coupon Code and QR Code
        renderRedeemSuccessStep(result.code, rewardName, rewardCost, result.remaining_points);

      } catch (error) {
        errDiv.textContent = error.message;
        errDiv.style.display = 'block';
        btn.disabled = false;
        btn.innerHTML = `<span class="material-icons-outlined" style="font-size:1.2rem;">check_circle</span> Verifikasi &amp; Tukar`;
      }
    });
  }

  // Render Step 3: Success Screen
  function renderRedeemSuccessStep(claimCode, name, cost, remainingPoints) {
    const stepContainer = document.getElementById('redeemStepContainer');
    const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${claimCode}`;
    
    // Trigger toast success
    showToast('<span class="material-icons-outlined" style="color:var(--green)">celebration</span>', 'Penukaran poin berhasil!');

    stepContainer.innerHTML = `
      <div style="text-align:center; padding:10px 0;">
        <div style="font-size:3rem; color:var(--green); margin-bottom:10px;"><span class="material-icons-outlined" style="font-size: 3rem; color: var(--green); animation: bounce 1.5s ease-in-out infinite;">celebration</span></div>
        <h3 style="font-size:1.2rem; font-weight:800; color:var(--text); margin-bottom:6px;">Penukaran Berhasil!</h3>
        <p style="font-size:0.85rem; color:var(--muted); margin-bottom:18px;">
          Poin Anda telah berhasil dipotong sebanyak <strong style="color:var(--gold);">${cost} XP</strong>. Sisa poin Anda sekarang: <strong>${remainingPoints} XP</strong>.
        </p>

        <!-- QR Code -->
        <div style="background:white; display:inline-block; padding:12px; border-radius:16px; box-shadow:0 8px 24px rgba(0,0,0,0.08); margin-bottom:16px; border:1px solid var(--border);">
          <img src="${qrUrl}" alt="${claimCode}" style="width:150px; height:150px; display:block;">
        </div>

        <!-- Claim Code -->
        <div style="background:var(--surface2); border:1px dashed var(--border); padding:10px; border-radius:8px; display:inline-block; font-family:monospace; font-weight:700; font-size:1.05rem; letter-spacing:1px; color:var(--text); margin-bottom:18px; width:100%;">
          ${claimCode}
        </div>

        <p style="font-size:0.8rem; line-height:1.5; color:var(--muted); margin-bottom:20px; max-width:90%; margin-left:auto; margin-right:auto;">
          Silakan tunjukkan Kode Unik atau QR Code di atas ke pustakawan di <strong>Meja Sirkulasi</strong> untuk pengambilan barang. Bukti penukaran juga dikirim ke email.
        </p>

        <button id="btnRedeemFinish" style="width:100%; background:var(--blue); border:none; color:white; padding:12px; border-radius:10px; font-family:inherit; font-size:0.9rem; font-weight:700; cursor:pointer; transition:background 0.2s;">Selesai</button>
      </div>
    `;

    document.getElementById('btnRedeemFinish').addEventListener('click', () => {
      closeModal();
      // Reload current tab to update points / leaderboard ranking live!
      loadTab(currentTab);
    });
  }

  openModal();
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
  document.getElementById('toastIcon').innerHTML = icon;
  document.getElementById('toastMsg').textContent = msg;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), duration);
}

// ── LIVE RANK SHUFFLE DEMO ──
// Every 10s, briefly animate two rows swapping in the student list to show "live" feel.
setInterval(() => {
  const list = document.getElementById('list-student-xp');
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
