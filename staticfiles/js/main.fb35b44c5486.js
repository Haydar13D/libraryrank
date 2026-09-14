/**
 * LibraryRank — Main Frontend JS
 * Fetches data from Django JSON APIs and renders the leaderboard UI.
 */

'use strict';

// ── SVG ICONS HELPER ──
const ICONS = {
  trophy: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"></path><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"></path><path d="M4 22h16"></path><path d="M10 14.66V17c0 .55-.45 1-1 1H7c-.55 0-1 .45-1 1v1c0 .55.45 1 1 1h10c.55 0 1-.45 1-1v-1c0-.55-.45-1-1-1h-2c-.55 0-1-.45-1-1v-2.34"></path><path d="M18 4H6v7a6 6 0 0 0 12 0V4z"></path></svg>`,
  crown: (size=22, color='#F59E0B') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m2 4 3 12h14l3-12-6 7-4-7-4 7-6-7zm3 16h14"></path></svg>`,
  medal: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="6"></circle><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"></path></svg>`,
  star: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>`,
  book: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>`,
  user: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>`,
  school: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"></path><path d="M6 12v5c3 3 9 3 12 0v-5"></path></svg>`,
  briefcase: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>`,
  fire: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 3z"></path></svg>`,
  search: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>`,
  spinner: (size=20, color='currentColor') => `<svg class="svg-icon" style="animation:spinLoading 1s linear infinite;" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line></svg>`,
  gift: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 12 20 22 4 22 4 12"></polyline><rect x="2" y="7" width="20" height="5"></rect><line x1="12" y1="22" x2="12" y2="7"></line><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"></path><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"></path></svg>`,
  diamond: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3h12l4 6-10 12L2 9z"></path><path d="M11 3 8 9l4 12 4-12-3-6"></path><path d="M2 9h20"></path></svg>`,
  chart: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>`,
  walk: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m13 4 2 2 3-1"></path><circle cx="13" cy="4" r="1.5"></circle><path d="M10 20v-5l-2-3 4-4 3 2 3 6"></path><path d="m6 17 3-3"></path></svg>`,
  building: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18"></path><path d="M5 21V7l8-4v18"></path><path d="M19 21V11l-6-4"></path><path d="M9 9v.01"></path><path d="M9 12v.01"></path><path d="M9 15v.01"></path><path d="M9 18v.01"></path></svg>`,
  check: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`,
  close: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`,
  camera: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>`,
  lock: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>`,
  send: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>`,
  celebration: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5.8 11.3 2 22l10.7-3.8"></path><path d="M4 3h.01"></path><path d="M22 8h.01"></path><path d="M15 2h.01"></path><path d="M22 20h.01"></path><path d="m22 2-2.24.75a2.9 2.9 0 0 0-1.96 3.12v0c.1.86-.57 1.63-1.45 1.63h-.38c-.86 0-1.6.6-1.76 1.44L14 12"></path></svg>`,
  target: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>`,
  trendUp: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>`,
  shield: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>`,
  badge: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z"></path></svg>`,
  idCard: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="18" rx="2"></rect><circle cx="8" cy="10" r="2"></circle><line x1="14" y1="9" x2="18" y2="9"></line><line x1="14" y1="13" x2="18" y2="13"></line><path d="M4 17a4 4 0 0 1 8 0"></path></svg>`,
  megaphone: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 11 18-5v12L3 13v-2z"></path><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"></path></svg>`,
  flask: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 2v7.527a2 2 0 0 1-.211.896L4.72 20.55a1 1 0 0 0 .9 1.45h12.76a1 1 0 0 0 .9-1.45l-5.069-10.127A2 2 0 0 1 14 9.527V2"></path><path d="M8.5 2h7"></path><path d="M7 16h10"></path></svg>`,
  feather: (size=20, color='currentColor') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.24 12.24a6 6 0 0 0-8.49-8.49L5 10.5V19h8.5z"></path><line x1="16" y1="8" x2="2" y2="22"></line><line x1="17.5" y1="15" x2="9" y2="15"></line></svg>`,
  twitter: (size=16) => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>`,
  facebook: (size=16) => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="currentColor"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg>`,
  whatsapp: (size=16) => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="currentColor"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>`,
  inbox: (size=36, color='var(--muted)') => `<svg class="svg-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"></polyline><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"></path></svg>`
};

// ── CONFIG ──
const ROLE_COLORS = {
  student: { bg: 'rgba(77,166,255,.18)', text: 'var(--blue)' },
  lecturer: { bg: 'rgba(61,224,138,.18)', text: 'var(--green)' },
  staff: { bg: 'rgba(255,145,77,.18)', text: 'var(--orange)' },
};

const BOOK_ICONS = { 
  CS: ICONS.chart(16), 
  Economics: ICONS.chart(16), 
  Medicine: ICONS.star(16), 
  Law: ICONS.briefcase(16), 
  Engineering: ICONS.building(16), 
  Psychology: ICONS.user(16), 
  Mathematics: ICONS.chart(16), 
  Chemistry: ICONS.star(16), 
  default: ICONS.book(16) 
};

const getBadgeIconHtml = (icon) => {
  const badgeMap = {
    '🥇': ICONS.medal(28, '#F59E0B'),
    '🥈': ICONS.medal(28, '#94A3B8'),
    '🥉': ICONS.medal(28, '#B45309'),
    '📚': ICONS.book(28, '#8B5CF6'),
  };
  return badgeMap[icon] || `<span style="font-size:1.8rem;">${icon}</span>`;
};

let currentDateFrom = document.getElementById('dateFrom')?.value || '';
let currentDateTo = document.getElementById('dateTo')?.value || '';
let currentSearch = document.getElementById('searchInput')?.value || '';
let currentTab = 'overview';
let searchTimer = null;

// ── INIT ──
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('panel-overview') || document.querySelector('.tab-btn[data-tab]')) {
    bindControls();
    loadTab('overview');
  }
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
  document.getElementById('btnFilter')?.addEventListener('click', () => {
    currentDateFrom = document.getElementById('dateFrom')?.value || '';
    currentDateTo = document.getElementById('dateTo')?.value || '';
    loadTab(currentTab);
  });

  // Quick Preset Buttons
  document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const days = parseInt(btn.dataset.days);
      const to = new Date();
      const from = new Date();
      from.setDate(to.getDate() - days);

      document.getElementById('dateFrom').value = from.toISOString().split('T')[0];
      document.getElementById('dateTo').value = to.toISOString().split('T')[0];
      currentDateFrom = document.getElementById('dateFrom').value;
      currentDateTo = document.getElementById('dateTo').value;

      document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      loadTab(currentTab);
    });
  });

  // Exports
  document.getElementById('btnExcelExport')?.addEventListener('click', () => {
    const url = `/export/excel/?date_from=${currentDateFrom}&date_to=${currentDateTo}`;
    window.location.href = url;
    showToast(ICONS.chart(20, 'var(--green)'), 'Downloading Excel...');
  });

  document.getElementById('btnPdfExport')?.addEventListener('click', () => {
    const url = `/export/pdf/?date_from=${currentDateFrom}&date_to=${currentDateTo}`;
    window.location.href = url;
    showToast(ICONS.book(20, 'var(--red)'), 'Downloading PDF...');
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
  const paramsObj = {};
  if (currentDateFrom) paramsObj.date_from = currentDateFrom;
  if (currentDateTo) paramsObj.date_to = currentDateTo;
  if (currentSearch) paramsObj.q = currentSearch;
  const params = new URLSearchParams(paramsObj);

  switch (tab) {
    case 'overview': fetchOverview(params); break;
    case 'students': fetchRole('student', params); break;
    case 'lecturers': fetchRole('lecturer', params); break;
    case 'staff': fetchRole('staff', params); break;
    case 'books': fetchBooks(params); break;
    case 'faculties': fetchFaculties(params); break;
  }
}

// ── API CALLS ──
async function fetchOverview(params) {
  try {
    const res = await fetch(`/api/overview/?${params}`);
    const data = await res.json();
    renderStats(data.stats);
    renderNominations(data.nominations);

    // Split leaderboard into top 3 (podium) and the rest (list)
    renderPodium('podium-overview', data.leaderboard.slice(0, 3), 'student');
    renderList('overviewList', data.leaderboard.slice(3), null, true, 'visits', 'XP', 3);

    if (typeof Chart !== 'undefined') renderChart(data);
  } catch (e) { console.error(e); }
}

async function updateQuickSearch(q) {
  const quickCard = document.getElementById('searchResultQuick');
  const searchIcon = document.getElementById('heroSearchIcon') || document.querySelector('.search-icon');

  if (!quickCard) return;
  if (!q || q.length < 3) {
    quickCard.style.display = 'none';
    if (searchIcon) searchIcon.innerHTML = ICONS.search(22, 'var(--muted)');
    return;
  }

  if (searchIcon) {
    searchIcon.innerHTML = ICONS.spinner(22, 'var(--primary)');
  }

  try {
    const params = new URLSearchParams({ q: q });
    const res = await fetch(`/api/overview/?${params}`);
    const data = await res.json();
    if (data.leaderboard && data.leaderboard.length > 0) {
      const p = data.leaderboard[0];

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
  } catch (e) { } finally {
    if (searchIcon) searchIcon.innerHTML = ICONS.search(22, 'var(--muted)');
  }
}

async function fetchRole(role, params) {
  try {
    const res = await fetch(`/api/pemustaka-teraktif/?role=${role}&${params}`);
    const data = await res.json();

    const topXp = data.top_xp || [];
    if (topXp.length >= 3) {
      renderPodium(`podium-${role}-xp`, topXp.slice(0, 3), role);
      renderList(`list-${role}-xp`, topXp.slice(3), role, false, 'total_p', 'XP', 3);
    } else {
      const podiumEl = document.getElementById(`podium-${role}-xp`);
      if (podiumEl) podiumEl.innerHTML = '';
      renderList(`list-${role}-xp`, topXp, role, false, 'total_p', 'XP', 0);
    }

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
    const stats = data.stats || {};
    const total = stats.total_visitors || 500;
    dataPoints = Array.from({ length: 6 }, () => Math.floor((Math.random() * 0.3 + 0.1) * (total / 6)));
    dataPoints.push(0); // Sunday is always 0
  }

  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const textColor = isDark ? '#94A3B8' : '#64748B';
  const gridColor = isDark ? '#334155' : '#E2E8F0';

  const ctxObj = ctx.getContext('2d');
  const gradientFill = ctxObj.createLinearGradient(0, 0, 0, 300);
  gradientFill.addColorStop(0, 'rgba(96, 165, 250, 0.4)');
  gradientFill.addColorStop(1, 'rgba(96, 165, 250, 0.0)');

  const gradientStroke = ctxObj.createLinearGradient(0, 0, 600, 0);
  gradientStroke.addColorStop(0, '#60a5fa');
  gradientStroke.addColorStop(1, '#a78bfa');

  if (overviewChartInstance) overviewChartInstance.destroy();

  overviewChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min'],
      datasets: [{
        label: 'Kunjungan',
        data: dataPoints,
        borderColor: gradientStroke,
        backgroundColor: gradientFill,
        fill: true,
        tension: 0.45,
        borderWidth: 4,
        pointBackgroundColor: '#1e293b',
        pointBorderColor: '#a78bfa',
        pointBorderWidth: 3,
        pointRadius: 5,
        pointHoverRadius: 8,
        pointHoverBackgroundColor: '#a78bfa',
        pointHoverBorderColor: '#fff',
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.9)',
          titleColor: '#fff',
          bodyColor: '#cbd5e1',
          titleFont: { family: "'Plus Jakarta Sans', sans-serif", size: 14, weight: 'bold' },
          bodyFont: { family: "'Plus Jakarta Sans', sans-serif", size: 13 },
          borderColor: 'rgba(255,255,255,0.1)',
          borderWidth: 1,
          padding: 12,
          displayColors: false,
          callbacks: {
            label: function (context) {
              return context.parsed.y.toLocaleString() + ' kunjungan';
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: gridColor, borderDash: [6, 6], drawBorder: false },
          ticks: { color: textColor, padding: 12, font: { family: "'Plus Jakarta Sans', sans-serif", size: 12 } }
        },
        x: {
          grid: { display: false, drawBorder: false },
          ticks: { color: textColor, padding: 12, font: { family: "'Plus Jakarta Sans', sans-serif", size: 12 } }
        }
      },
      interaction: {
        mode: 'index',
        intersect: false,
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
    student: { label: `${ICONS.school(16, 'var(--gold)')} Top Mahasiswa`, cls: 'students' },
    lecturer: { label: `${ICONS.user(16, 'var(--gold)')} Top Dosen`, cls: 'lecturers' },
    staff: { label: `${ICONS.briefcase(16, 'var(--gold)')} Top Staff`, cls: 'staff' },
  };

  container.innerHTML = Object.entries(roleConfig).map(([role, cfg]) => {
    const n = noms[role];
    if (!n) return `<div class="nom-card"><div class="nom-label">${cfg.label}</div><div class="empty-state"><div class="icon">${ICONS.inbox(24)}</div><p>Belum ada data</p></div></div>`;
    const { bg, text } = ROLE_COLORS[role];
    return `
      <div class="nom-card">
        <div class="nom-card-header">
          <div class="nom-label">${cfg.label}</div>
          <div style="color:var(--gold); display:flex; align-items:center;">${ICONS.crown(18, 'var(--gold)')}</div>
        </div>
        <div class="nom-card-body">
          <div class="nom-avatar-big" style="background:${bg};color:${text}">${n.initials}</div>
          <div class="nom-info">
            <div class="nom-winner">${n.name}</div>
            <div class="nom-detail">${n.faculty}${n.title ? ' · ' + n.title : ''}</div>
            <div class="nom-xp-tag">${Number(n.visits).toLocaleString()} XP</div>
          </div>
        </div>
      </div>`;
  }).join('');
}

function renderList(containerId, items, forceRole, showRoleTag = false, scoreKey = 'visits', scoreLabel = 'visits', rankOffset = 0) {
  const el = document.getElementById(containerId);
  if (!el) return;

  if (!items.length) {
    el.innerHTML = `<div class="empty-state" style="padding:20px; text-align:center;"><div class="icon">${ICONS.inbox(28)}</div><p style="color:var(--muted); font-size:0.8rem; margin-top:4px;">Tidak ada data ditemukan.</p></div>`;
    return;
  }

  el.innerHTML = items.map((p, i) => {
    const role = forceRole || p.role;
    const { bg, text } = ROLE_COLORS[role] || ROLE_COLORS.student;
    const actualRank = i + rankOffset;
    const rankEl = actualRank === 0 ? ICONS.medal(18, '#F59E0B') : actualRank === 1 ? ICONS.medal(18, '#94A3B8') : actualRank === 2 ? ICONS.medal(18, '#B45309') : `#${actualRank + 1}`;
    const rankCls = actualRank === 0 ? 'top1' : actualRank === 1 ? 'top2' : actualRank === 2 ? 'top3' : '';

    return `
      <div class="lb-item ${rankCls}" data-id="${p.id}" data-role="${role}">
        <div class="lb-col lb-col-rank ${rankCls}">${rankEl}</div>
        <div class="lb-col lb-col-user">
          <div class="lb-avatar" style="background:${bg};color:${text}">${p.initials}</div>
          <div class="lb-info">
            <div class="lb-name">${p.name}</div>
            <div class="lb-sub">@${(p.id || p.sub || '').toString().toLowerCase()}</div>
          </div>
        </div>
        <div class="lb-col lb-col-dept">${p.sub || p.faculty || '-'}</div>
        <div class="lb-col lb-col-score">${Number(p[scoreKey] ?? p.visits ?? 0).toLocaleString()}${scoreLabel === 'XP' ? ' <span style="font-size:0.75em; font-weight:700; color:var(--muted);">XP</span>' : ''}</div>
      </div>`;
  }).join('');

  // Bind click for modal
  el.querySelectorAll('.lb-item').forEach(item => {
    item.addEventListener('click', () => fetchMemberDetail(item.dataset.id, item.dataset.role));
  });

  // Stagger entrance animation (Fast & Snappy: 15ms)
  el.querySelectorAll('.lb-item').forEach((item, i) => {
    item.style.opacity = '0';
    item.style.transform = 'translateY(4px)';
    setTimeout(() => {
      item.style.transition = 'opacity .12s ease, transform .12s ease';
      item.style.opacity = '1';
      item.style.transform = 'translateY(0)';
    }, i * 15);
  });
}

function renderPodium(containerId, items, role) {
  const el = document.getElementById(containerId);
  if (!el || items.length < 2) { if (el) el.innerHTML = ''; return; }

  // Order: 2nd place (left), 1st place (center), 3rd place (right)
  const podiumConfig = [
    { idx: 1, cls: 'second', rank: 2, medalColor: '#94A3B8' },
    { idx: 0, cls: 'first', rank: 1, medalColor: '#F59E0B' },
    { idx: 2, cls: 'third', rank: 3, medalColor: '#B45309' }
  ];

  el.innerHTML = podiumConfig.map(cfg => {
    const p = items[cfg.idx];
    if (!p) return '';
    const itemRole = p.role || role;
    const { bg, text } = ROLE_COLORS[itemRole] || ROLE_COLORS.student;
    const scoreVal = Number(p.total_p ?? p.visits ?? 0).toLocaleString();

    return `
      <div class="podium-item ${cfg.cls}" data-id="${p.id}" data-role="${itemRole}">
        <div class="podium-avatar-wrap">
          ${cfg.cls === 'first' ? `<div class="podium-crown">${ICONS.crown(28, '#F59E0B')}</div>` : ''}
          <div class="podium-avatar" style="background:${bg};color:${text}">
            ${p.initials}
          </div>
        </div>
        <div class="podium-name">${p.name}</div>
        <div class="podium-dept">${p.sub || p.faculty || ''}</div>
        <div class="podium-base">
          <div class="podium-rank-badge" style="color:${cfg.medalColor}">
            ${ICONS.medal(18, cfg.medalColor)}
            <span>#${cfg.rank}</span>
          </div>
          <div class="podium-xp-pill">
            ${ICONS.diamond(14, 'var(--blue)')}
            <strong>${scoreVal}</strong>
            <span style="font-size:0.75rem; color:var(--muted); font-weight:600;">XP</span>
          </div>
        </div>
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
      <div class="fac-bar-track"><div class="fac-bar-fill" style="background:${f.color}" data-pct="${Math.round(f.visitors / max * 100)}%"></div></div>
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
      <div class="book-icon" style="display:flex; align-items:center;">${ICONS.building(18, 'var(--gold)')}</div>
      <div class="book-info">
        <div class="book-title">${f.name}</div>
        <div class="book-author">${f.visitors} visitors</div>
      </div>
      <div class="book-bar-wrap">
        <div class="book-bar-track"><div class="book-bar-fill" style="background:${f.color};width:0%" data-pct="${Math.round(f.books / max * 100)}%"></div></div>
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
        <div style="font-family:var(--font-heading);font-weight:800;font-size:.95rem;color:${text};flex-shrink:0">${t.visits}</div>
      </div>`;
  }).join('') || `<div class="empty-state"><div class="icon">${ICONS.inbox(32)}</div><p>No data yet</p></div>`;
}

// ── MODAL ──
function escapeHtml(unsafe) {
  if (!unsafe) return '';
  return String(unsafe)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function renderModal(data, role) {
  const { bg, text } = ROLE_COLORS[role] || ROLE_COLORS.student;
  const borrows = data.recent_borrows || [];
  const badges = data.badges || [];
  const rewards = data.rewards || [];
  const userXP = data.visits_total || 0;

  const shareText = encodeURIComponent(`Saya baru saja meraih prestasi di LibraryRank Universitas! Cek profil ${data.name} dengan total XP ${data.visits_total}.`);
  const shareUrl = encodeURIComponent(window.location.origin);
  const lvl = data.level || { name: 'Visitor', progress_perc: 0, current_xp: 0, max_xp: 100, color: '#95a5a6' };

  // Rewards catalog HTML inside member detail
  const rewardsHtml = rewards.length ? `
    <div class="modal-rewards" style="margin-top:28px; text-align:left; border-top:1px solid var(--border); padding-top:22px;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; flex-wrap:wrap; gap:8px;">
        <h4 style="margin:0; font-size:0.85rem; color:var(--text); font-weight:700; text-transform:uppercase; letter-spacing:0.04em; display:flex; align-items:center; gap:6px;">
          ${ICONS.gift(18, 'var(--gold)')} Tukar Poin Merchandise
        </h4>
        <span style="font-size:0.75rem; color:var(--gold); font-weight:700; background:var(--gold-bg); padding:3px 8px; border-radius:4px; border:1px solid rgba(245,158,11,0.3);">
          ${userXP.toLocaleString()} XP Tersedia
        </span>
      </div>
      
      <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(200px, 1fr)); gap:12px;">
        ${rewards.map(r => {
          const canAfford = userXP >= r.points_cost && r.stock > 0;
          let btnText = 'Tukar Sekarang';
          let btnStyle = 'background:var(--primary); color:#fff; cursor:pointer;';
          let disabled = '';
          
          if (r.stock <= 0) {
            btnText = 'Stok Habis';
            btnStyle = 'background:var(--surface2); color:var(--muted); cursor:not-allowed; border:1px solid var(--border);';
            disabled = 'disabled';
          } else if (userXP < r.points_cost) {
            btnText = `Kurang ${r.points_cost - userXP} XP`;
            btnStyle = 'background:var(--surface2); color:var(--muted); cursor:not-allowed; border:1px solid var(--border);';
            disabled = 'disabled';
          }

          return `
            <div style="background:var(--surface2); border:1px solid var(--border); border-radius:10px; padding:12px; display:flex; flex-direction:column; justify-content:space-between;">
              <div>
                <div style="width:100%; height:90px; background:var(--surface); border-radius:6px; display:flex; align-items:center; justify-content:center; margin-bottom:10px; overflow:hidden;">
                  <img src="${r.image_url}" alt="${r.name}" style="max-width:85%; max-height:85%; object-fit:contain;" onerror="this.src='https://placehold.co/120x80/1e2230/949cae?text=${encodeURIComponent(r.name)}';">
                </div>
                <div style="font-weight:700; font-size:0.85rem; color:var(--text); margin-bottom:4px; line-height:1.3;">${r.name}</div>
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.75rem; margin-bottom:10px;">
                  <span style="color:var(--gold); font-weight:800; font-variant-numeric:tabular-nums;">${r.points_cost} XP</span>
                  <span style="color:var(--muted);">Stok: ${r.stock}</span>
                </div>
              </div>
              <button ${disabled} onclick="openRedeemModal(${r.id}, '${escapeHtml(r.name)}', ${r.points_cost}, ${r.stock}, '${data.id}')"
                style="width:100%; padding:8px 10px; border-radius:6px; border:none; font-family:inherit; font-size:0.78rem; font-weight:700; transition:opacity 0.15s; ${btnStyle}">
                ${btnText}
              </button>
            </div>
          `;
        }).join('')}
      </div>
    </div>
  ` : '';

  document.getElementById('modalBody').innerHTML = `
    <div id="captureCard" style="padding:4px 0 10px; text-align:center;">
      <div class="modal-avatar" style="border: 3px solid ${lvl.color}; background:${bg};color:${text};margin:0 auto 14px;width:76px;height:76px;font-size:1.8rem;line-height:70px;">${data.initials}</div>
      <div class="modal-name" style="font-size:1.25rem; font-weight:800; color:var(--text); margin-bottom:4px;">${data.name}</div>
      <div class="modal-sub" style="font-size:0.82rem; color:var(--muted); margin-bottom:18px;">${data.id} · ${data.faculty || data.department || ''} ${data.year ? '· ' + data.year : ''}</div>
      
      <div style="margin: 18px auto 0; max-width: 90%;">
        <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:8px; font-size:0.8rem; font-weight:700;">
          <span style="color:${lvl.color}; text-transform:uppercase; font-size:11px; letter-spacing:1px">${lvl.name}</span>
          <span style="color:var(--text); font-size:11px">${lvl.current_xp} / ${lvl.max_xp == lvl.current_xp ? 'MAX' : lvl.max_xp} XP</span>
        </div>
        <div style="height:8px; border-radius:4px; background:var(--surface2); border:1px solid var(--border); overflow:hidden;">
          <div style="height:100%; width:${lvl.progress_perc}%; background:${lvl.color}; transition: width 1s ease;"></div>
        </div>
      </div>
      
      <div class="modal-stats" style="margin-top:24px; display:flex; justify-content:center; gap:20px;">
        <div class="modal-stat"><strong style="color:${text}">${data.visits_total}</strong><span>Total Visits</span></div>
        <div class="modal-stat"><strong style="color:var(--purple)">${data.books_total}</strong><span>Total Books</span></div>
        <div class="modal-stat"><strong style="color:var(--orange)">${data.streak}</strong><span>Day Streak <span style="vertical-align:middle; display:inline-flex; align-items:center; color:var(--orange);">${ICONS.fire(18, 'var(--orange)')}</span></span></div>
      </div>

      ${badges.length ? `
      <div class="modal-badges" style="margin-top:28px; text-align:left;">
        <h4 style="margin-bottom:14px;font-size:.82rem;color:var(--muted);text-transform:uppercase;letter-spacing:1px;text-align:center;display:flex;align-items:center;justify-content:center;gap:6px;font-weight:700;">
          ${ICONS.trophy(18, 'var(--gold)')} Prestasi / Badges
        </h4>
        <div style="display:flex; flex-direction:column; gap:12px;">
          ${badges.map(b => `
            <div style="display:flex; align-items:center; gap:14px; padding:14px; border-radius:10px; border:1px solid var(--border); background:var(--surface2)">
              <div style="font-size:1.8rem; width:48px; height:48px; display:flex; align-items:center; justify-content:center; background:${b.image_url ? 'none' : b.color + '20'}; border-radius:50%;flex-shrink:0;">
                ${b.image_url ? `<img src="${b.image_url}" alt="${b.name}" style="width:100%; height:100%; object-fit:contain;">` : getBadgeIconHtml(b.icon)}
              </div>
              <div style="flex:1;">
                <div style="font-weight:700; color:var(--text); font-size:0.95rem; margin-bottom:2px;">${b.name}</div>
                <div style="font-size:.8rem; color:var(--muted);">${b.desc}</div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>` : ''}

      ${rewardsHtml}
    </div>

    <!-- Share Buttons -->
    <div class="modal-share" style="margin-top:24px; padding-top:22px; border-top:1px solid var(--border);">
      <h4 style="margin-bottom:14px;font-size:.82rem;color:var(--muted);text-align:center;display:flex;align-items:center;justify-content:center;gap:6px;font-weight:700;text-transform:uppercase;letter-spacing:0.04em;">
        ${ICONS.megaphone(16, 'var(--gold)')} Share Pencapaianmu
      </h4>
      <div style="display:flex; justify-content:center; gap:10px; flex-wrap:wrap;">
        <a href="https://twitter.com/intent/tweet?text=${shareText}&url=${shareUrl}" target="_blank" style="display:inline-flex; align-items:center; gap:6px; padding:9px 16px; border-radius:8px; background:#1DA1F2; color:#fff; text-decoration:none; font-size:.82rem; font-weight:700;">${ICONS.twitter(15)} Twitter</a>
        <a href="https://www.facebook.com/sharer/sharer.php?u=${shareUrl}&quote=${shareText}" target="_blank" style="display:inline-flex; align-items:center; gap:6px; padding:9px 16px; border-radius:8px; background:#1877F2; color:#fff; text-decoration:none; font-size:.82rem; font-weight:700;">${ICONS.facebook(15)} Facebook</a>
        <a href="https://api.whatsapp.com/send?text=${shareText}%20${shareUrl}" target="_blank" style="display:inline-flex; align-items:center; gap:6px; padding:9px 16px; border-radius:8px; background:#25D366; color:#fff; text-decoration:none; font-size:.82rem; font-weight:700;">${ICONS.whatsapp(15)} WhatsApp</a>
        <button onclick="downloadIGStory()" style="display:inline-flex; align-items:center; gap:6px; padding:9px 16px; border-radius:8px; background:linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888); color:#fff; border:none; cursor:pointer; font-size:.82rem; font-weight:700;">${ICONS.camera(16, '#fff')} IG Story</button>
      </div>
    </div>
  `;
  openModal();
}

async function downloadIGStory() {
  showToast(ICONS.camera(20, 'var(--primary)'), 'Generating Story Image...', 2000);
  const card = document.getElementById('captureCard');
  if (!card) return;
  try {
    const canvas = await html2canvas(card, {
      backgroundColor: '#282A6A',
      scale: 2,
      logging: false
    });
    const link = document.createElement('a');
    link.download = 'LibraryRank_Achievement.jpg';
    link.href = canvas.toDataURL('image/jpeg', 0.9);
    link.click();
    showToast(ICONS.check(20, 'var(--green)'), 'Image Downloaded! Share to Story.', 4000);
  } catch (e) {
    console.error(e);
    showToast(ICONS.close(20, 'var(--red)'), 'Gagal memuat gambar', 3000);
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
    <div class="guide-modal-wrapper" style="text-align:left;">
      <h2 style="display:flex; align-items:center; gap:10px; margin-bottom:20px; font-size:1.35rem; color:var(--text); font-weight:800; padding-right:32px;">
        ${ICONS.book(24, 'var(--gold)')}
        Panduan Leaderboard LibraryRank
      </h2>
      
      <!-- Tab Menu Modal -->
      <div class="guide-tabs" style="display:flex; border-bottom:1px solid var(--border); margin-bottom:22px; gap:6px; overflow-x:auto; padding-bottom:4px;">
        <button class="guide-tab-btn active" data-guide-tab="about" style="flex:1; padding:10px 8px; border:none; background:none; font-family:inherit; font-size:0.85rem; font-weight:700; color:var(--gold); border-bottom:2px solid var(--gold); cursor:pointer; text-align:center; transition:all 0.15s; white-space:nowrap; display:flex; align-items:center; justify-content:center; gap:6px;">${ICONS.book(16, 'var(--gold)')} Tentang</button>
        <button class="guide-tab-btn" data-guide-tab="points" style="flex:1; padding:10px 8px; border:none; background:none; font-family:inherit; font-size:0.85rem; font-weight:700; color:var(--muted); border-bottom:2px solid transparent; cursor:pointer; text-align:center; transition:all 0.15s; white-space:nowrap; display:flex; align-items:center; justify-content:center; gap:6px;">${ICONS.trendUp(16)} Poin (XP)</button>
        <button class="guide-tab-btn" data-guide-tab="badges" style="flex:1; padding:10px 8px; border:none; background:none; font-family:inherit; font-size:0.85rem; font-weight:700; color:var(--muted); border-bottom:2px solid transparent; cursor:pointer; text-align:center; transition:all 0.15s; white-space:nowrap; display:flex; align-items:center; justify-content:center; gap:6px;">${ICONS.trophy(16)} Badges</button>
        <button class="guide-tab-btn" data-guide-tab="levels" style="flex:1; padding:10px 8px; border:none; background:none; font-family:inherit; font-size:0.85rem; font-weight:700; color:var(--muted); border-bottom:2px solid transparent; cursor:pointer; text-align:center; transition:all 0.15s; white-space:nowrap; display:flex; align-items:center; justify-content:center; gap:6px;">${ICONS.shield(16)} Levels</button>
      </div>

      <!-- Tab Content Modal -->
      <div class="guide-panels">
        <!-- 1. TENTANG -->
        <div class="guide-panel active" id="gpanel-about" style="display:block;">
          <p style="font-size:0.92rem; line-height:1.65; color:var(--text); margin-bottom:16px;">
            Selamat datang di <strong>LibraryRank</strong>, platform gamifikasi resmi Perpustakaan UMS! Platform ini dirancang khusus untuk mengapresiasi keaktifan kunjungan fisik, literasi, peminjaman buku, serta keikutsertaan event ilmiah dari para civitas akademika (Mahasiswa, Dosen, &amp; Tendik/Staff).
          </p>
          <div style="background:var(--surface2); border-left:4px solid var(--gold); padding:14px 16px; border-radius:6px; margin-top:16px; font-size:0.86rem; line-height:1.6; color:var(--text);">
            <strong style="color:var(--gold); display:flex; align-items:center; gap:6px; margin-bottom:6px; font-size:0.92rem;">
              ${ICONS.target(18, 'var(--gold)')} Misi Utama Kami:
            </strong>
            Membangun atmosfer akademik yang kompetitif dan menyenangkan, serta memotivasi minat baca melalui perolehan poin prestasi, lencana kehormatan (badges), dan reward eksklusif perpustakaan.
          </div>
        </div>

        <!-- 2. POIN (XP) -->
        <div class="guide-panel" id="gpanel-points" style="display:none;">
          <p style="font-size:0.9rem; color:var(--muted); margin-bottom:14px;">Dapatkan poin XP (Experience Points) dari setiap aktivitas keaktifan Anda di perpustakaan:</p>
          <div style="display:flex; flex-direction:column; gap:10px;">
            <div style="display:flex; align-items:center; justify-content:space-between; padding:12px; border-radius:10px; border:1px solid var(--border); background:rgba(77,166,255,0.05);">
              <div style="display:flex; align-items:center; gap:10px;">
                <span style="font-size:1.5rem; display:flex; align-items:center;">${ICONS.walk(26, 'var(--blue)')}</span>
                <div>
                  <strong style="display:block; font-size:0.92rem; color:var(--text);">Kunjungan Fisik (Gate Scan)</strong>
                  <span style="font-size:0.78rem; color:var(--muted);">Terdeteksi otomatis saat memindai kartu di pintu masuk.</span>
                </div>
              </div>
              <strong style="color:var(--blue); font-size:1.1rem;">+10 XP</strong>
            </div>

            <div style="display:flex; align-items:center; justify-content:space-between; padding:12px; border-radius:10px; border:1px solid var(--border); background:rgba(61,224,138,0.05);">
              <div style="display:flex; align-items:center; gap:10px;">
                <span style="font-size:1.5rem; display:flex; align-items:center;">${ICONS.book(26, 'var(--green)')}</span>
                <div>
                  <strong style="display:block; font-size:0.92rem; color:var(--text);">Peminjaman Buku (Sirkulasi)</strong>
                  <span style="font-size:0.78rem; color:var(--muted);">Dihitung per transaksi peminjaman buku koha yang sah.</span>
                </div>
              </div>
              <strong style="color:var(--green); font-size:1.1rem;">+25 XP</strong>
            </div>

            <div style="display:flex; align-items:center; justify-content:space-between; padding:12px; border-radius:10px; border:1px solid var(--border); background:rgba(255,145,77,0.05);">
              <div style="display:flex; align-items:center; gap:10px;">
                <span style="font-size:1.5rem; display:flex; align-items:center;">${ICONS.school(26, 'var(--orange)')}</span>
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
              <div style="width:44px; height:44px; display:flex; align-items:center; justify-content:center; background:#bdc3c720; border-radius:50%; flex-shrink:0;">
                ${ICONS.trophy(24, '#94A3B8')}
              </div>
              <div>
                <strong style="display:block; font-size:0.95rem; color:var(--text); font-weight:700;">Weekly Warrior</strong>
                <span style="font-size:0.8rem; color:var(--muted);">Melakukan kunjungan fisik ke perpustakaan minimal 3 kali dalam seminggu.</span>
              </div>
            </div>

            <div style="display:flex; align-items:center; gap:12px; padding:12px; border-radius:10px; border:1px solid var(--border); background:rgba(255,255,255,0.02);">
              <div style="width:44px; height:44px; display:flex; align-items:center; justify-content:center; background:#9b59b620; border-radius:50%; flex-shrink:0;">
                ${ICONS.book(24, '#8B5CF6')}
              </div>
              <div>
                <strong style="display:block; font-size:0.95rem; color:var(--text); font-weight:700;">Book Worm</strong>
                <span style="font-size:0.8rem; color:var(--muted);">Meminjam lebih dari 5 buku dalam periode satu semester.</span>
              </div>
            </div>

            <div style="display:flex; align-items:center; gap:12px; padding:12px; border-radius:10px; border:1px solid var(--border); background:rgba(255,255,255,0.02);">
              <div style="width:44px; height:44px; display:flex; align-items:center; justify-content:center; background:#f1c40f20; border-radius:50%; flex-shrink:0;">
                ${ICONS.crown(24, '#FFB800')}
              </div>
              <div>
                <strong style="display:block; font-size:0.95rem; color:var(--text); font-weight:700;">Library Legend</strong>
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
              <div style="font-weight:bold; font-size:0.9rem; color:#95a5a6;">Pengunjung</div>
              <div style="font-size:0.75rem; color:var(--muted); margin-top:2px;">0 - 100 XP</div>
            </div>
            <div style="padding:10px; border-radius:8px; border:1px solid var(--border); text-align:center; background:rgba(255,255,255,0.02);">
              <div style="font-weight:bold; font-size:0.9rem; color:#3498db; display:flex; align-items:center; justify-content:center; gap:4px;">${ICONS.book(15, '#3498db')} Pembaca</div>
              <div style="font-size:0.75rem; color:var(--muted); margin-top:2px;">101 - 300 XP</div>
            </div>
            <div style="padding:10px; border-radius:8px; border:1px solid var(--border); text-align:center; background:rgba(255,255,255,0.02);">
              <div style="font-weight:bold; font-size:0.9rem; color:#2ecc71; display:flex; align-items:center; justify-content:center; gap:4px;">${ICONS.feather(15, '#2ecc71')} Pelajar</div>
              <div style="font-size:0.75rem; color:var(--muted); margin-top:2px;">301 - 700 XP</div>
            </div>
            <div style="padding:10px; border-radius:8px; border:1px solid var(--border); text-align:center; background:rgba(255,255,255,0.02);">
              <div style="font-weight:bold; font-size:0.9rem; color:#9b59b6; display:flex; align-items:center; justify-content:center; gap:4px;">${ICONS.flask(15, '#9b59b6')} Peneliti</div>
              <div style="font-size:0.75rem; color:var(--muted); margin-top:2px;">701 - 1500 XP</div>
            </div>
            <div style="padding:10px; border-radius:8px; border:1px solid var(--border); text-align:center; background:rgba(255,255,255,0.02);">
              <div style="font-weight:bold; font-size:0.9rem; color:#e67e22; display:flex; align-items:center; justify-content:center; gap:4px;">${ICONS.school(15, '#e67e22')} Cendekia</div>
              <div style="font-size:0.75rem; color:var(--muted); margin-top:2px;">1501 - 3000 XP</div>
            </div>
            <div style="padding:10px; border-radius:8px; border:1px solid var(--border); text-align:center; background:rgba(255,255,255,0.02);">
              <div style="font-weight:bold; font-size:0.9rem; color:#f1c40f; display:flex; align-items:center; justify-content:center; gap:4px;">${ICONS.crown(15, '#f1c40f')} Legenda Perpus</div>
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

function openRedeemModal(rewardId, rewardName, rewardCost, rewardStock, prefilledNim = '') {
  const container = document.getElementById('modalBody');
  if (!container) return;

  // Render Step 1: Input NIM
  container.innerHTML = `
    <div class="redeem-modal-wrapper" style="text-align:left;">
      <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:20px; padding-right:32px;">
        <h2 style="display:flex; align-items:center; gap:10px; margin:0; font-size:1.3rem; color:var(--text); font-weight:800;">
          ${ICONS.gift(24, 'var(--gold)')}
          Tukar Poin / Redeem
        </h2>
      </div>
      
      <div style="background:var(--surface2); padding:16px 18px; border-radius:10px; border:1px solid var(--border); margin-bottom:22px;">
        <h4 style="margin:0 0 10px 0; font-size:1rem; color:var(--text); font-weight:700; display:flex; align-items:center; gap:8px;">
          ${ICONS.gift(18, 'var(--gold)')} ${rewardName}
        </h4>
        <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.85rem; color:var(--muted); padding-top:10px; border-top:1px solid var(--border-subtle);">
          <span>Biaya Penukaran: <strong style="color:var(--gold); font-size:0.92rem; font-weight:800;">${rewardCost} XP</strong></span>
          <span>Tersedia: <strong style="color:var(--text); font-weight:700;">${rewardStock} unit</strong></span>
        </div>
      </div>

      <div id="redeemStepContainer">
        <!-- STEP 1 FORM -->
        <form id="otpRequestForm">
          <label style="display:block; font-size:0.75rem; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.05em; margin-bottom:10px;">Masukkan NIM / ID Anggota Anda:</label>
          <div style="position:relative; margin-bottom:18px;">
            <span style="position:absolute; left:14px; top:50%; transform:translateY(-50%); display:flex; align-items:center; color:var(--muted); pointer-events:none;">
              ${ICONS.idCard(18, 'currentColor')}
            </span>
            <input type="text" id="redeemMemberId" placeholder="Contoh: L200220001" value="${escapeHtml(prefilledNim)}" required 
              style="width:100%; height:48px; background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:0 14px 0 44px; color:var(--text); font-family:inherit; font-size:0.95rem; font-weight:600; outline:none; transition:border-color 0.15s;">
          </div>
          
          <div id="redeemError" style="color:var(--red); font-size:0.82rem; font-weight:600; margin-bottom:16px; display:none; padding:10px 14px; background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.2); border-radius:8px;"></div>
          
          <button type="submit" id="btnRequestOtp" style="width:100%; height:48px; background:var(--primary); border:none; color:white; border-radius:8px; font-family:inherit; font-size:0.92rem; font-weight:700; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:8px; transition:opacity 0.15s;">
            ${ICONS.send(18, '#fff')} Kirim Kode OTP Verifikasi
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
    btn.innerHTML = `${ICONS.spinner(18, '#fff')} Mengirim OTP...`;
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
      btn.innerHTML = `${ICONS.send(18, '#fff')} Kirim Kode OTP Verifikasi`;
    }
  });

  // Render Step 2: Input OTP Code
  function renderOtpVerificationStep(memberId, maskedEmail) {
    const stepContainer = document.getElementById('redeemStepContainer');
    stepContainer.innerHTML = `
      <form id="otpVerifyForm">
        <div style="background:var(--surface2); padding:14px 16px; border-radius:10px; border:1px solid var(--border); margin-bottom:20px; font-size:0.85rem; line-height:1.5; color:var(--text); display:flex; align-items:flex-start; gap:10px;">
          <span style="display:flex; align-items:center; margin-top:2px; color:var(--primary);">${ICONS.megaphone(18, 'currentColor')}</span>
          <div>
            Kode verifikasi OTP telah dikirim ke email kampus Anda:<br>
            <strong style="color:var(--primary); font-size:0.9rem;">${maskedEmail}</strong>
          </div>
        </div>

        <label style="display:block; font-size:0.75rem; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.05em; margin-bottom:10px;">Masukkan 6-Digit OTP:</label>
        <div style="position:relative; margin-bottom:18px;">
          <span style="position:absolute; left:14px; top:50%; transform:translateY(-50%); display:flex; align-items:center; color:var(--muted); pointer-events:none;">${ICONS.lock(18, 'currentColor')}</span>
          <input type="text" id="redeemOtp" maxlength="6" placeholder="******" required 
            style="width:100%; height:52px; background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:0 14px 0 44px; color:var(--text); font-family:inherit; font-size:1.2rem; font-weight:800; letter-spacing:8px; text-align:center; outline:none; transition:border-color 0.15s;">
        </div>

        <div id="redeemError" style="color:var(--red); font-size:0.82rem; font-weight:600; margin-bottom:16px; display:none; padding:10px 14px; background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.2); border-radius:8px;"></div>

        <div style="display:flex; gap:10px; margin-top:8px;">
          <button type="button" id="btnBackToStep1" style="flex:1; height:48px; background:var(--surface2); border:1px solid var(--border); color:var(--text); border-radius:8px; font-family:inherit; font-size:0.9rem; font-weight:600; cursor:pointer; transition:background 0.15s;">Kembali</button>
          <button type="submit" id="btnConfirmRedeem" style="flex:2; height:48px; background:var(--green); border:none; color:white; border-radius:8px; font-family:inherit; font-size:0.92rem; font-weight:700; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:8px; transition:opacity 0.15s;">
            ${ICONS.check(18, '#fff')} Verifikasi &amp; Tukar
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
      btn.innerHTML = `${ICONS.spinner(18, '#fff')} Memverifikasi...`;
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
        btn.innerHTML = `${ICONS.check(18, '#fff')} Verifikasi &amp; Tukar`;
      }
    });
  }

  // Render Step 3: Success Screen
  function renderRedeemSuccessStep(claimCode, name, cost, remainingPoints) {
    const stepContainer = document.getElementById('redeemStepContainer');
    const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=${claimCode}`;

    // Trigger toast success
    showToast(ICONS.celebration(22, 'var(--green)'), 'Penukaran poin berhasil!');

    stepContainer.innerHTML = `
      <div style="text-align:center; padding:8px 0;">
        <div style="font-size:3rem; color:var(--green); margin-bottom:14px; display:flex; justify-content:center;">${ICONS.celebration(48, 'var(--green)')}</div>
        <h3 style="font-size:1.25rem; font-weight:800; color:var(--text); margin-bottom:8px;">Penukaran Berhasil!</h3>
        <p style="font-size:0.88rem; color:var(--muted); margin-bottom:22px; line-height:1.5;">
          Poin Anda telah berhasil dipotong sebanyak <strong style="color:var(--gold);">${cost} XP</strong>.<br>Sisa poin Anda sekarang: <strong>${remainingPoints} XP</strong>.
        </p>

        <!-- QR Code -->
        <div style="background:white; display:inline-block; padding:14px; border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.1); margin-bottom:20px; border:1px solid var(--border);">
          <img src="${qrUrl}" alt="${claimCode}" style="width:160px; height:160px; display:block;">
        </div>

        <!-- Claim Code -->
        <div style="background:var(--surface2); border:1px dashed var(--border); padding:12px; border-radius:8px; display:block; font-family:monospace; font-weight:800; font-size:1.15rem; letter-spacing:2px; color:var(--text); margin-bottom:20px; width:100%;">
          ${claimCode}
        </div>

        <p style="font-size:0.82rem; line-height:1.6; color:var(--muted); margin-bottom:24px; max-width:92%; margin-left:auto; margin-right:auto;">
          Silakan tunjukkan Kode Unik atau QR Code di atas ke pustakawan di <strong>Meja Sirkulasi</strong> untuk pengambilan barang. Bukti penukaran juga telah dikirim ke email Anda.
        </p>

        <button id="btnRedeemFinish" style="width:100%; height:48px; background:var(--primary); border:none; color:white; border-radius:8px; font-family:inherit; font-size:0.92rem; font-weight:700; cursor:pointer; transition:opacity 0.15s;">Selesai</button>
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
