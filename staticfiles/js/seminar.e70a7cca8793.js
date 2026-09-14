// ── SEMINAR & ACADEMIC PORTAL JAVASCRIPT CONTROLLER ──
// Precision UI with live search, member identity card, and instant modal handling.

let loadedSeminarsList = [];
let currentModeFilter = 'all';
let currentSearchQuery = '';
let currentMemberInfo = null;

document.addEventListener('DOMContentLoaded', () => {
  // Restore saved NIM from localStorage
  const savedNim = localStorage.getItem('seminar_nim');
  if (savedNim) {
    const nimInput = document.getElementById('nimInput');
    const claimNim = document.getElementById('claimNim');
    if (nimInput) nimInput.value = savedNim;
    if (claimNim) claimNim.value = savedNim;
  }

  loadSeminars();
  initModalListeners();
});

// Tab switching (List vs Claim)
window.switchSeminarTab = function (tab) {
  const btnList = document.getElementById('tabBtnList');
  const btnClaim = document.getElementById('tabBtnClaim');
  const panelList = document.getElementById('panel-seminar-list');
  const panelClaim = document.getElementById('panel-seminar-claim');

  if (tab === 'list') {
    if (btnList) btnList.classList.add('active');
    if (btnClaim) btnClaim.classList.remove('active');
    if (panelList) panelList.style.display = 'block';
    if (panelClaim) panelClaim.style.display = 'none';
  } else {
    if (btnList) btnList.classList.remove('active');
    if (btnClaim) btnClaim.classList.add('active');
    if (panelList) panelList.style.display = 'none';
    if (panelClaim) panelClaim.style.display = 'block';
    populateClaimDropdown();
  }
};

// Mode Filter: all | offline | online | hybrid | my
window.filterSeminarMode = function (mode) {
  currentModeFilter = mode;

  const buttons = document.querySelectorAll('#seminarModeFilters .sem-filter-btn');
  buttons.forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-mode') === mode);
  });

  applyFiltersAndRender();
};

// Live Search handler
window.onSeminarSearchInput = function (e) {
  currentSearchQuery = (e.target.value || '').trim().toLowerCase();
  applyFiltersAndRender();
};

// Filter & Search applicator
function applyFiltersAndRender() {
  let filtered = [...loadedSeminarsList];

  // 1. Mode Filter
  if (currentModeFilter === 'my') {
    filtered = filtered.filter(s => s.reg_status && s.reg_status !== 'not_registered');
  } else if (currentModeFilter !== 'all') {
    filtered = filtered.filter(s => s.event_mode === currentModeFilter);
  }

  // 2. Search Query Filter
  if (currentSearchQuery) {
    filtered = filtered.filter(s => {
      const title = (s.title || '').toLowerCase();
      const speaker = (s.speaker || '').toLowerCase();
      const location = (s.location || '').toLowerCase();
      const category = (s.category_display || s.category || '').toLowerCase();
      return title.includes(currentSearchQuery) || 
             speaker.includes(currentSearchQuery) || 
             location.includes(currentSearchQuery) ||
             category.includes(currentSearchQuery);
    });
  }

  renderSeminarCards(filtered);
}

// Fetch seminars and member status from API
window.loadSeminars = async function () {
  const nimInput = document.getElementById('nimInput');
  const nim = nimInput ? nimInput.value.trim() : '';

  if (nim) {
    localStorage.setItem('seminar_nim', nim);
    const claimNim = document.getElementById('claimNim');
    if (claimNim) claimNim.value = nim;
  }

  const container = document.getElementById('seminarContainer');
  if (container) {
    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 48px 20px; color: var(--muted);">
        <div class="lb-skeleton" style="margin: 0 auto 12px; width: 44px; height: 44px; border-radius: 50%;"></div>
        <div style="font-weight: 600; font-size: 0.9rem; color: var(--text);">Memuat agenda kegiatan &amp; seminar...</div>
        <div style="font-size: 0.78rem; margin-top: 4px;">Menghubungkan ke sistem perpustakaan</div>
      </div>
    `;
  }

  try {
    const url = nim ? `/api/seminar/list/?member_id=${encodeURIComponent(nim)}` : '/api/seminar/list/';
    const res = await fetch(url);
    const data = await res.json();

    if (data.success) {
      loadedSeminarsList = data.seminars || [];
      currentMemberInfo = data.member || null;

      updateMemberBanner(currentMemberInfo, loadedSeminarsList);
      applyFiltersAndRender();
      populateClaimDropdown();
    } else {
      if (container) {
        container.innerHTML = `
          <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--red); background: var(--surface); border-radius: var(--radius-lg); border: 1px solid var(--border);">
            <h4 style="margin-bottom: 4px;">Gagal memuat agenda kegiatan</h4>
            <p style="font-size: 0.82rem; color: var(--muted);">${escapeHtml(data.error || 'Terjadi kesalahan')}</p>
          </div>
        `;
      }
    }
  } catch (err) {
    console.error('Error loading seminars:', err);
    if (container) {
      container.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--red); background: var(--surface); border-radius: var(--radius-lg); border: 1px solid var(--border);">
          <h4 style="margin-bottom: 4px;">Kesalahan Jaringan</h4>
          <p style="font-size: 0.82rem; color: var(--muted);">Tidak dapat terhubung ke server. Silakan coba sesaat lagi.</p>
        </div>
      `;
    }
  }
};

// Reset NIM filter
window.clearMemberNim = function () {
  localStorage.removeItem('seminar_nim');
  const nimInput = document.getElementById('nimInput');
  const claimNim = document.getElementById('claimNim');
  if (nimInput) nimInput.value = '';
  if (claimNim) claimNim.value = '';
  loadSeminars();
};

// Render Member Identity Banner
function updateMemberBanner(member, seminars) {
  const banner = document.getElementById('semMemberBanner');
  const myFilterBtn = document.getElementById('btnFilterMySeminars');

  if (!banner) return;

  if (!member || !member.member_id) {
    banner.style.display = 'none';
    if (myFilterBtn) myFilterBtn.style.display = 'none';
    if (currentModeFilter === 'my') {
      filterSeminarMode('all');
    }
    return;
  }

  // Count user registrations
  const registeredCount = seminars.filter(s => s.reg_status === 'registered').length;
  const attendedCount = seminars.filter(s => s.reg_status === 'attended').length;

  const nameEl = document.getElementById('semMemberName');
  const subEl = document.getElementById('semMemberSub');
  const avatarEl = document.getElementById('semMemberAvatar');
  const regCountEl = document.getElementById('semStatRegCount');
  const attendCountEl = document.getElementById('semStatAttendCount');

  if (nameEl) nameEl.textContent = member.name || member.member_id;
  if (subEl) subEl.textContent = `${member.faculty || 'Civitas UMS'} • NIM: ${member.member_id}`;
  if (avatarEl) avatarEl.textContent = getInitials(member.name || member.member_id);
  if (regCountEl) regCountEl.textContent = registeredCount;
  if (attendCountEl) attendCountEl.textContent = attendedCount;

  banner.style.display = 'flex';
  if (myFilterBtn) {
    myFilterBtn.style.display = 'inline-flex';
    myFilterBtn.innerHTML = `
      <svg class="svg-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
        <circle cx="12" cy="7" r="4"></circle>
      </svg>
      Acara Saya (${registeredCount + attendedCount})
    `;
  }
}

// Render Seminar Cards Grid
function renderSeminarCards(seminars) {
  const container = document.getElementById('seminarContainer');
  if (!container) return;

  if (seminars.length === 0) {
    const filterLabels = {
      'offline': 'kategori Tatap Muka (Offline)',
      'online': 'kategori Daring (Online / Zoom)',
      'hybrid': 'kategori Hybrid',
      'my': 'daftar yang telah Anda daftarkan'
    };
    const filterDesc = filterLabels[currentModeFilter] || 'pencarian atau filter saat ini';

    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 56px 20px; background: var(--surface); border-radius: var(--radius-lg); border: 1px dashed var(--border);">
        <div style="width: 48px; height: 48px; margin: 0 auto 12px; border-radius: 50%; background: var(--surface2); display: flex; align-items: center; justify-content: center; color: var(--muted);">
          <svg class="svg-icon" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
        </div>
        <h4 style="color: var(--text); font-size: 1rem; font-weight: 700; margin-bottom: 4px;">Tidak Ada Kegiatan Ditemukan</h4>
        <p style="color: var(--muted); font-size: 0.82rem; max-width: 360px; margin: 0 auto;">Belum ada jadwal acara untuk ${filterDesc}.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = seminars.map(sem => {
    // 1. Category config
    const categoryConfigs = {
      'seminar': { bg: 'rgba(59,130,246,0.1)', color: '#2563eb', label: 'SEMINAR', icon: '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path>' },
      'workshop': { bg: 'rgba(139,92,246,0.1)', color: '#7c3aed', label: 'WORKSHOP', icon: '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>' },
      'training': { bg: 'rgba(245,158,11,0.1)', color: '#d97706', label: 'PELATIHAN', icon: '<circle cx="12" cy="8" r="7"></circle><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline>' },
      'webinar': { bg: 'rgba(6,182,212,0.1)', color: '#0891b2', label: 'WEBINAR', icon: '<polygon points="23 7 16 12 23 17 23 7"></polygon><rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>' },
      'book_review': { bg: 'rgba(236,72,153,0.1)', color: '#db2777', label: 'BEDAH BUKU', icon: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>' },
      'other': { bg: 'rgba(107,114,128,0.1)', color: '#4b5563', label: 'ACARA', icon: '<circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line>' }
    };
    const cat = categoryConfigs[sem.category] || categoryConfigs['seminar'];
    const catBadge = `<span class="sem-pill" style="background:${cat.bg}; color:${cat.color};"><svg class="svg-icon" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">${cat.icon}</svg>${escapeHtml(sem.category_display || cat.label)}</span>`;

    // 2. Mode badge
    let modeBadge = '';
    if (sem.event_mode === 'online') {
      modeBadge = `<span class="sem-pill" style="background:rgba(6,182,212,0.1); color:#0891b2;"><svg class="svg-icon" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"></polygon><rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect></svg>DARING</span>`;
    } else if (sem.event_mode === 'hybrid') {
      modeBadge = `<span class="sem-pill" style="background:rgba(139,92,246,0.1); color:#7c3aed;"><svg class="svg-icon" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>HYBRID</span>`;
    } else {
      modeBadge = `<span class="sem-pill" style="background:rgba(16,185,129,0.1); color:var(--green);"><svg class="svg-icon" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>TATAP MUKA</span>`;
    }

    // 3. User status badge & button actions
    let statusBadge = '';
    let actionBtnHtml = '';
    let cardClass = 'sem-card';

    if (sem.reg_status === 'attended') {
      cardClass += ' is-attended';
      statusBadge = `<span class="sem-pill" style="background:rgba(16,185,129,0.12); color:var(--green);"><span class="live-dot" style="background:var(--green); animation:none; position:static; display:inline-block; margin:0;"></span>HADIR</span>`;
      
      if (sem.has_certificate && sem.certificate_url) {
        actionBtnHtml = `
          <a href="${sem.certificate_url}" target="_blank" download class="sem-btn-cert" style="text-decoration: none;">
            <svg class="svg-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            Unduh E-Sertifikat (PDF)
          </a>
        `;
      } else {
        actionBtnHtml = `<div class="sem-btn-disabled" style="color: var(--green); border-color: rgba(16,185,129,0.3);">✓ Kehadiran Berhasil Dikonfirmasi (+${sem.points_attend} XP)</div>`;
      }
    } else if (sem.reg_status === 'registered') {
      cardClass += ' is-registered';
      statusBadge = `<span class="sem-pill" style="background:rgba(47,49,133,0.1); color:var(--primary);"><svg class="svg-icon" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>TERDAFTAR</span>`;
      
      if (sem.claim_code_active) {
        actionBtnHtml = `
          <button type="button" onclick="openQuickClaimModal('${sem.id}', '${escapeHtml(sem.title)}', '${sem.points_attend}')" class="sem-btn-primary" style="background: #10b981;">
            <svg class="svg-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            Klaim Kehadiran (+${sem.points_attend} XP)
          </button>
        `;
      } else {
        actionBtnHtml = `<div class="sem-btn-disabled">Terdaftar • Klaim Dibuka Saat Acara</div>`;
      }
    } else {
      // Not registered
      if (sem.is_upcoming) {
        statusBadge = `<span class="sem-pill" style="background:var(--surface2); color:var(--muted);">SEGERA HADIR</span>`;
        actionBtnHtml = `<div class="sem-btn-disabled">Pendaftaran Belum Dibuka</div>`;
      } else if (sem.is_closed) {
        statusBadge = `<span class="sem-pill" style="background:rgba(239,68,68,0.08); color:var(--red);">DITUTUP</span>`;
        actionBtnHtml = `<div class="sem-btn-disabled">Pendaftaran Ditutup</div>`;
      } else {
        // Open for registration
        statusBadge = `<span class="sem-pill" style="background:rgba(16,185,129,0.08); color:var(--green);"><span class="live-dot" style="background:var(--green); position:static; display:inline-block; margin:0;"></span>BUKA</span>`;
        actionBtnHtml = `
          <button type="button" onclick="openRegModal('${sem.id}', '${escapeHtml(sem.title)}')" class="sem-btn-primary">
            Daftar Acara (+${sem.points_register} XP)
          </button>
        `;
      }
    }

    // 4. Poster cover or placeholder
    const posterHtml = sem.image_url ? `
      <div class="sem-poster-wrap">
        <img src="${sem.image_url}" alt="${escapeHtml(sem.title)}" class="sem-poster-img" loading="lazy">
      </div>
    ` : `
      <div class="sem-poster-wrap">
        <div class="sem-poster-placeholder">
          <svg class="svg-icon" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
          </svg>
          <span>${escapeHtml(sem.category_display || 'SEMINAR PERPUSTAKAAN')}</span>
        </div>
      </div>
    `;

    // 5. Zoom Button or Locked Notice if online / hybrid
    let zoomAreaHtml = '';
    if (sem.event_mode === 'online' || sem.event_mode === 'hybrid') {
      if (sem.reg_status === 'registered' || sem.reg_status === 'attended') {
        if (sem.meeting_url) {
          zoomAreaHtml = `
            <a href="${sem.meeting_url}" target="_blank" rel="noopener noreferrer" class="sem-btn-zoom">
              <svg class="svg-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="23 7 16 12 23 17 23 7"></polygon>
                <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
              </svg>
              Masuk Zoom Meeting (Terbuka)
            </a>
          `;
        }
      } else {
        zoomAreaHtml = `
          <div style="display: flex; align-items: center; gap: 6px; font-size: 0.72rem; color: var(--muted); background: var(--surface2); padding: 6px 10px; border-radius: var(--radius-sm); border: 1px dashed var(--border); margin-bottom: 8px;">
            <svg class="svg-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
            <span>Link Zoom &amp; Passcode terbuka setelah Anda mendaftar.</span>
          </div>
        `;
      }
    }

    // 6. Location meta
    let locationMeta = '';
    if (sem.event_mode === 'online') {
      locationMeta = `
        <div class="sem-meta-item is-online">
          <svg class="svg-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"></polygon><rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect></svg>
          <span>Daring via Zoom / Virtual Room</span>
        </div>
      `;
    } else if (sem.event_mode === 'hybrid') {
      locationMeta = `
        <div class="sem-meta-item">
          <svg class="svg-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
          <span><strong>Lokasi:</strong> ${escapeHtml(sem.location || 'Ruang Seminar')} <span style="color:#7c3aed; font-weight:700;">(+ Zoom)</span></span>
        </div>
      `;
    } else {
      locationMeta = `
        <div class="sem-meta-item">
          <svg class="svg-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
          <span><strong>Lokasi:</strong> ${escapeHtml(sem.location || 'Ruang Seminar Perpustakaan UMS')}</span>
        </div>
      `;
    }

    return `
      <div class="${cardClass}">
        ${posterHtml}
        
        <div class="sem-card-body">
          <div class="sem-badge-row">
            <div class="sem-badges-left">
              ${catBadge}
              ${modeBadge}
              ${statusBadge}
            </div>
            <span class="sem-pill-xp">
              <svg class="svg-icon" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
              +${sem.points_attend} XP
            </span>
          </div>

          <h3 class="sem-card-title">${escapeHtml(sem.title)}</h3>

          <div class="sem-meta-list">
            <div class="sem-meta-item">
              <svg class="svg-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
              <span><strong>Narasumber:</strong> ${escapeHtml(sem.speaker || '-')}</span>
            </div>
            <div class="sem-meta-item">
              <svg class="svg-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
              <span><strong>Waktu:</strong> ${escapeHtml(sem.date_formatted || '')}</span>
            </div>
            ${locationMeta}
          </div>

          <p class="sem-card-desc">
            ${escapeHtml(sem.description || 'Tidak ada deskripsi tambahan untuk kegiatan ini.')}
          </p>
        </div>

        <div class="sem-card-footer">
          ${zoomAreaHtml}
          ${actionBtnHtml}
        </div>
      </div>
    `;
  }).join('');
}

// Quick Claim Modal Handlers (Direct from Card)
window.openQuickClaimModal = function (seminarId, seminarTitle, points) {
  const overlay = document.getElementById('seminarClaimOverlay');
  const titleEl = document.getElementById('claimModalSeminarTitle');
  const idEl = document.getElementById('quickClaimSeminarId');
  const nimEl = document.getElementById('quickClaimNim');
  const codeEl = document.getElementById('quickClaimCode');
  const btnTextEl = document.getElementById('quickClaimBtnText');

  if (idEl) idEl.value = seminarId;
  if (titleEl) titleEl.textContent = seminarTitle;
  if (btnTextEl) btnTextEl.textContent = `Klaim Kehadiran (+${points || 15} XP)`;

  // Auto-fill active NIM
  const activeNim = (document.getElementById('nimInput')?.value || localStorage.getItem('seminar_nim') || '').trim();
  if (nimEl) nimEl.value = activeNim;
  if (codeEl) {
    codeEl.value = '';
    setTimeout(() => codeEl.focus(), 150);
  }

  if (overlay) overlay.classList.add('open');
};

window.closeClaimModal = function () {
  const overlay = document.getElementById('seminarClaimOverlay');
  if (overlay) overlay.classList.remove('open');
};

// Submit Quick Claim from Card Modal
window.submitQuickClaim = async function (e) {
  e.preventDefault();

  const btn = document.getElementById('btnSubmitQuickClaim');
  const origText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = 'Memproses klaim...';

  const memberId = document.getElementById('quickClaimNim').value.trim();
  const seminarId = document.getElementById('quickClaimSeminarId').value;
  const claimCode = document.getElementById('quickClaimCode').value.trim();

  if (!memberId || !seminarId || !claimCode) {
    showToast('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--gold)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>', 'Semua kolom wajib diisi.', 3000);
    btn.disabled = false;
    btn.innerHTML = origText;
    return;
  }

  try {
    const res = await fetch('/api/seminar/claim/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': typeof CSRF_TOKEN !== 'undefined' ? CSRF_TOKEN : ''
      },
      body: JSON.stringify({ member_id: memberId, seminar_id: seminarId, claim_code: claimCode })
    });
    const data = await res.json();

    if (data.success) {
      const msg = data.certificate_url
        ? `${data.message} E-Sertifikat PDF siap diunduh!`
        : data.message;
      showToast('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--green)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 12 20 22 4 22 4 12"></polyline><rect x="2" y="7" width="20" height="5"></rect><line x1="12" y1="22" x2="12" y2="7"></line><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"></path><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"></path></svg>', msg, 6000);

      closeClaimModal();
      
      const nimInput = document.getElementById('nimInput');
      if (nimInput) nimInput.value = memberId;
      localStorage.setItem('seminar_nim', memberId);

      // Reload seminars and refresh card status
      await loadSeminars();
    } else {
      showToast('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--red)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>', data.error || 'Gagal mengklaim kehadiran.', 4000);
    }
  } catch (err) {
    console.error(err);
    showToast('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--red)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>', 'Terjadi kesalahan jaringan.', 3000);
  } finally {
    btn.disabled = false;
    btn.innerHTML = origText;
  }
};

// Populate Claim Dropdown select — ONLY shows seminars the member is registered for
function populateClaimDropdown() {
  const select = document.getElementById('claimSeminarSelect');
  if (!select) return;

  const currentSelectVal = select.value;
  const nim = (document.getElementById('claimNim')?.value || document.getElementById('nimInput')?.value || '').trim();

  if (!nim) {
    select.innerHTML = '<option value="" disabled selected>-- Masukkan NIM di atas untuk memuat seminar Anda --</option>';
    return;
  }

  // ONLY filter seminars where the user has actually registered (registered or attended)
  const registeredSeminars = loadedSeminarsList.filter(s => s.reg_status === 'registered' || s.reg_status === 'attended');

  if (registeredSeminars.length === 0) {
    select.innerHTML = '<option value="" disabled selected>-- Belum ada seminar yang Anda daftarkan --</option>';
    return;
  }

  select.innerHTML = `
    <option value="" disabled ${!currentSelectVal ? 'selected' : ''}>-- Pilih Seminar yang Telah Didaftar --</option>
    ${registeredSeminars.map(sem => `
      <option value="${sem.id}" ${currentSelectVal == sem.id ? 'selected' : ''} ${sem.reg_status === 'attended' ? 'disabled' : ''}>
        ${escapeHtml(sem.title)} ${sem.reg_status === 'attended' ? '(Sudah Diklaim / Hadir)' : '(Terdaftar - Siap Klaim)'}
      </option>
    `).join('')}
  `;
}

// Go to claim tab and preselect seminar
window.goToClaimTab = function (seminarId) {
  switchSeminarTab('claim');
  const select = document.getElementById('claimSeminarSelect');
  if (select) {
    select.value = seminarId;
  }
};

// Modal Registration Open
window.openRegModal = async function (seminarId, seminarTitle) {
  const overlay = document.getElementById('seminarRegOverlay');
  const titleEl = document.getElementById('regModalSeminarTitle');
  const idEl = document.getElementById('regSeminarId');

  if (idEl) idEl.value = seminarId;
  if (titleEl) titleEl.textContent = seminarTitle;

  // Prefill NIM if active from localStorage or search input
  const checkNim = (document.getElementById('nimInput')?.value || localStorage.getItem('seminar_nim') || '').trim();
  const regNim = document.getElementById('regNim');
  const regEmail = document.getElementById('regEmail');

  if (checkNim && regNim) {
    regNim.value = checkNim;
    
    // Auto lookup Koha official email
    if (currentMemberInfo && currentMemberInfo.member_id?.toUpperCase() === checkNim.toUpperCase() && currentMemberInfo.email) {
      if (regEmail) regEmail.value = currentMemberInfo.email;
    } else {
      lookupKohaEmail(checkNim);
    }
  } else if (regEmail) {
    regEmail.value = '';
  }

  if (overlay) overlay.classList.add('open');
};

window.closeRegModal = function () {
  const overlay = document.getElementById('seminarRegOverlay');
  if (overlay) overlay.classList.remove('open');
};

// Auto lookup Koha email
async function lookupKohaEmail(nim) {
  const regEmail = document.getElementById('regEmail');
  if (!regEmail || !nim) return;

  try {
    const res = await fetch(`/api/member/${encodeURIComponent(nim)}/`);
    const data = await res.json();
    if (data && data.email) {
      regEmail.value = data.email;
    } else {
      regEmail.value = `${nim.toLowerCase()}@student.ums.ac.id`;
    }
  } catch (err) {
    regEmail.value = `${nim.toLowerCase()}@student.ums.ac.id`;
  }
}

// Modal Debounced Lookup & Claim NIM sync
function initModalListeners() {
  const regNim = document.getElementById('regNim');
  if (regNim) {
    let debounceTimer = null;
    regNim.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      const val = regNim.value.trim();
      if (!val) return;

      debounceTimer = setTimeout(() => {
        lookupKohaEmail(val);
      }, 400);
    });
  }

  const claimNim = document.getElementById('claimNim');
  if (claimNim) {
    let claimDebounce = null;
    claimNim.addEventListener('input', () => {
      clearTimeout(claimDebounce);
      const val = claimNim.value.trim();
      claimDebounce = setTimeout(async () => {
        if (val) {
          localStorage.setItem('seminar_nim', val);
          const nimInput = document.getElementById('nimInput');
          if (nimInput) nimInput.value = val;
          await loadSeminars();
        } else {
          populateClaimDropdown();
        }
      }, 500);
    });
  }
}

// Submit Seminar Registration
window.submitSeminarRegistration = async function (e) {
  e.preventDefault();

  const btn = e.target.querySelector('button[type="submit"]');
  const origText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = 'Mendaftarkan...';

  const memberId = document.getElementById('regNim').value.trim();
  const email = document.getElementById('regEmail').value.trim();
  const seminarId = document.getElementById('regSeminarId').value;

  try {
    const res = await fetch('/api/seminar/register/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': typeof CSRF_TOKEN !== 'undefined' ? CSRF_TOKEN : ''
      },
      body: JSON.stringify({ member_id: memberId, email: email, seminar_id: seminarId })
    });
    const data = await res.json();

    if (data.success) {
      showToast('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--green)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>', data.message, 4500);
      closeRegModal();

      const nimInput = document.getElementById('nimInput');
      if (nimInput) nimInput.value = memberId;
      localStorage.setItem('seminar_nim', memberId);
      loadSeminars();
    } else {
      showToast('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--red)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>', data.error || 'Gagal mendaftar.', 4000);
    }
  } catch (err) {
    console.error(err);
    showToast('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--red)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>', 'Terjadi kesalahan jaringan.', 3000);
  } finally {
    btn.disabled = false;
    btn.innerHTML = origText;
  }
};

// Submit Attendance Claim
window.handleClaimAttendance = async function (e) {
  e.preventDefault();

  const btn = e.target.querySelector('button[type="submit"]');
  const origText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = 'Memproses klaim...';

  const memberId = document.getElementById('claimNim').value.trim();
  const seminarId = document.getElementById('claimSeminarSelect').value;
  const claimCode = document.getElementById('claimCode').value.trim();

  if (!seminarId) {
    showToast('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--gold)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>', 'Silakan pilih seminar terlebih dahulu.', 3000);
    btn.disabled = false;
    btn.innerHTML = origText;
    return;
  }

  try {
    const res = await fetch('/api/seminar/claim/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': typeof CSRF_TOKEN !== 'undefined' ? CSRF_TOKEN : ''
      },
      body: JSON.stringify({ member_id: memberId, seminar_id: seminarId, claim_code: claimCode })
    });
    const data = await res.json();

    if (data.success) {
      const msg = data.certificate_url
        ? `${data.message} E-Sertifikat PDF siap diunduh!`
        : data.message;
      showToast('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--green)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 12 20 22 4 22 4 12"></polyline><rect x="2" y="7" width="20" height="5"></rect><line x1="12" y1="22" x2="12" y2="7"></line><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"></path><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"></path></svg>', msg, 6000);

      document.getElementById('claimCode').value = '';
      const nimInput = document.getElementById('nimInput');
      if (nimInput) nimInput.value = memberId;
      localStorage.setItem('seminar_nim', memberId);

      // Reload seminars
      await loadSeminars();
      switchSeminarTab('list');
    } else {
      showToast('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--red)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>', data.error || 'Gagal mengklaim kehadiran.', 4000);
    }
  } catch (err) {
    console.error(err);
    showToast('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--red)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>', 'Terjadi kesalahan jaringan.', 3000);
  } finally {
    btn.disabled = false;
    btn.innerHTML = origText;
  }
};

// Helper: Initials
function getInitials(name) {
  if (!name) return 'U';
  const parts = name.trim().split(' ').filter(Boolean);
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
  return (parts[0][0] + parts[1][0]).toUpperCase();
}

// Helper: Escape HTML
function escapeHtml(unsafe) {
  if (typeof unsafe !== 'string') return '';
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
