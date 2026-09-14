// ── SEMINAR PORTAL JS ──

document.addEventListener('DOMContentLoaded', () => {
  // Restore NIM if saved in localStorage
  const savedNim = localStorage.getItem('seminar_nim');
  if (savedNim) {
    document.getElementById('nimInput').value = savedNim;
    document.getElementById('claimNim').value = savedNim;
  }
  loadSeminars();
});

let loadedSeminarsList = [];

// Tab switching
window.switchSeminarTab = function (tab) {
  const btnList = document.getElementById('tabBtnList');
  const btnClaim = document.getElementById('tabBtnClaim');
  const panelList = document.getElementById('panel-seminar-list');
  const panelClaim = document.getElementById('panel-seminar-claim');

  if (tab === 'list') {
    btnList.classList.add('active');
    btnClaim.classList.remove('active');
    panelList.style.display = 'block';
    panelClaim.style.display = 'none';
  } else {
    btnList.classList.remove('active');
    btnClaim.classList.add('active');
    panelList.style.display = 'none';
    panelClaim.style.display = 'block';
    populateClaimDropdown();
  }
};

// Load seminars from API
window.loadSeminars = async function () {
  const nim = document.getElementById('nimInput').value.trim();
  if (nim) {
    localStorage.setItem('seminar_nim', nim);
    document.getElementById('claimNim').value = nim;
  }

  const container = document.getElementById('seminarContainer');
  container.innerHTML = `
    <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--muted);">
      <div class="lb-skeleton" style="margin: 0 auto 10px; width: 50px; height: 50px; border-radius: 50%;"></div>
      Memuat daftar seminar...
    </div>
  `;

  try {
    const url = nim ? `/api/seminar/list/?member_id=${encodeURIComponent(nim)}` : '/api/seminar/list/';
    const res = await fetch(url);
    const data = await res.json();
    
    if (data.success) {
      loadedSeminarsList = data.seminars;
      renderSeminarCards(data.seminars);
      populateClaimDropdown();
    } else {
      container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #ff5c5c;">Gagal memuat: ${data.error}</div>`;
    }
  } catch (e) {
    console.error(e);
    container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #ff5c5c;">Kesalahan jaringan saat memuat data.</div>`;
  }
};

// Render cards
function renderSeminarCards(seminars) {
  const container = document.getElementById('seminarContainer');
  if (seminars.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 48px; background: var(--surface); border-radius: var(--radius); border: 1px dashed var(--border);">
        <div style="margin-bottom: 12px; color: var(--muted); display: flex; justify-content: center;">
          <svg class="svg-icon" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
        </div>
        <h4 style="color: var(--text); margin-bottom: 4px; font-size: 0.95rem;">Belum Ada Seminar Aktif</h4>
        <p style="color: var(--muted); font-size: 0.82rem;">Tidak ada jadwal seminar yang terdaftar untuk 30 hari terakhir atau mendatang.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = seminars.map(sem => {
    let buttonHtml = '';
    let badgeHtml = '';

    if (sem.reg_status === 'attended') {
      badgeHtml = `<span style="background: rgba(16,185,129,0.1); color: var(--green); padding: 4px 10px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;"><span class="live-dot" style="background:var(--green); animation:none; position:static; display:inline-block; margin:0;"></span>HADIR</span>`;
      buttonHtml = `<button disabled style="width: 100%; padding: 9px; border-radius: 8px; border: 1px solid var(--border); background: var(--surface2); color: var(--muted); font-family: 'Inter', sans-serif; font-weight: 600; font-size: 0.82rem;">Selesai (Sudah Diklaim)</button>`;
    } else if (sem.reg_status === 'registered') {
      badgeHtml = `<span style="background: rgba(47,49,133,0.08); color: var(--primary); padding: 4px 10px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;"><svg class="svg-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg> TERDAFTAR</span>`;
      
      if (sem.claim_code_active) {
        buttonHtml = `<button onclick="goToClaimTab('${sem.id}')" style="width: 100%; padding: 9px; border-radius: 8px; border: none; background: var(--primary); color: #fff; font-family: 'Inter', sans-serif; font-weight: 600; cursor: pointer; font-size: 0.82rem;">Klaim Kehadiran Sekarang</button>`;
      } else {
        buttonHtml = `<button disabled style="width: 100%; padding: 9px; border-radius: 8px; border: 1px solid var(--border); background: var(--surface2); color: var(--muted); font-family: 'Inter', sans-serif; font-weight: 600; font-size: 0.82rem;">Terdaftar (Klaim Hari-H)</button>`;
      }
    } else {
      // not_registered
      if (sem.is_upcoming) {
        badgeHtml = `<span style="background: var(--surface2); color: var(--muted); padding: 4px 10px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;"><svg class="svg-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> BELUM DIBUKA</span>`;
        buttonHtml = `<button disabled style="width: 100%; padding: 9px; border-radius: 8px; border: 1px solid var(--border); background: var(--surface2); color: var(--muted); font-family: 'Inter', sans-serif; font-weight: 600; font-size: 0.82rem;">Pendaftaran Belum Dibuka</button>`;
      } else if (sem.is_closed) {
        badgeHtml = `<span style="background: rgba(239,68,68,0.08); color: var(--red); padding: 4px 10px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;"><svg class="svg-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg> DITUTUP</span>`;
        buttonHtml = `<button disabled style="width: 100%; padding: 9px; border-radius: 8px; border: 1px solid var(--border); background: var(--surface2); color: var(--muted); font-family: 'Inter', sans-serif; font-weight: 600; font-size: 0.82rem;">Tutup</button>`;
      } else if (sem.is_open) {
        badgeHtml = `<span style="background: rgba(16,185,129,0.08); color: var(--green); padding: 4px 10px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;"><span class="live-dot" style="background:var(--green); position:static; display:inline-block; margin:0;"></span>PENDAFTARAN DIBUKA</span>`;
        buttonHtml = `<button onclick="openRegModal('${sem.id}', '${escapeHtml(sem.title)}')" style="width: 100%; padding: 9px; border-radius: 8px; border: none; background: var(--primary); color: #fff; font-family: 'Inter', sans-serif; font-weight: 600; cursor: pointer; font-size: 0.82rem;">Daftar Seminar (+${sem.points_register} XP)</button>`;
      }
    }

    const posterHtml = sem.image_url ? `
      <div style="width: 100%; height: 140px; border-radius: 8px; overflow: hidden; margin-bottom: 12px; border: 1px solid var(--border); background: var(--surface2);">
        <img src="${sem.image_url}" alt="${escapeHtml(sem.title)}" style="width: 100%; height: 100%; object-fit: cover; display: block;" loading="lazy">
      </div>
    ` : '';

    return `
      <div class="card-block" style="border-radius: var(--radius); padding: 18px; border: 1px solid ${sem.reg_status !== 'not_registered' ? 'var(--primary)' : 'var(--border)'}; display: flex; flex-direction: column; justify-content: space-between; transition: border-color 0.15s;">
        <div>
          ${posterHtml}
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; flex-wrap: wrap; gap: 6px;">
            ${badgeHtml}
            <span style="font-size: 0.72rem; color: var(--muted); font-weight: 600; border: 1px solid var(--border); padding: 3px 8px; border-radius: 4px; display: inline-flex; align-items: center; gap: 3px;">
              <svg class="svg-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--gold)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg> +${sem.points_attend} XP
            </span>
          </div>
          <h4 style="font-size: 0.95rem; font-weight: 700; color: var(--text); margin-bottom: 6px; line-height: 1.4;">${sem.title}</h4>
          <div style="font-size: 0.78rem; color: var(--muted); margin-bottom: 3px; display: flex; align-items: center; gap: 5px;">
            <svg class="svg-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg> <strong>Speaker:</strong> ${sem.speaker}
          </div>
          <div style="font-size: 0.78rem; color: var(--muted); margin-bottom: 10px; display: flex; align-items: center; gap: 5px;">
            <svg class="svg-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> <strong>Waktu:</strong> ${sem.date_formatted}
          </div>
          <p style="font-size: 0.78rem; color: var(--muted); line-height: 1.5; margin-bottom: 16px;">
            ${sem.description || 'Tidak ada deskripsi.'}
          </p>
        </div>
        <div>
          ${buttonHtml}
        </div>
      </div>
    `;
  }).join('');
}

// Populate Claim Dropdown select
function populateClaimDropdown() {
  const select = document.getElementById('claimSeminarSelect');
  if (!select) return;

  const currentSelectVal = select.value;

  if (loadedSeminarsList.length === 0) {
    select.innerHTML = '<option value="" disabled selected>Belum ada seminar terdaftar</option>';
    return;
  }

  // If user has specific registrations, show those; otherwise show all seminars
  const registeredSeminars = loadedSeminarsList.filter(s => s.reg_status === 'registered' || s.reg_status === 'attended');
  const seminarsToShow = registeredSeminars.length > 0 ? registeredSeminars : loadedSeminarsList;

  select.innerHTML = `
    <option value="" disabled ${!currentSelectVal ? 'selected' : ''}>-- Pilih Seminar --</option>
    ${seminarsToShow.map(sem => `
      <option value="${sem.id}" ${currentSelectVal == sem.id ? 'selected' : ''} ${sem.reg_status === 'attended' ? 'disabled style="color:var(--muted);"' : ''}>
        ${sem.title} ${sem.reg_status === 'attended' ? '(Sudah Hadir)' : (sem.reg_status === 'registered' ? '(Terdaftar - Siap Klaim)' : '')}
      </option>
    `).join('')}
  `;
}

// Route to claim tab and pre-select seminar
window.goToClaimTab = function (seminarId) {
  switchSeminarTab('claim');
  const select = document.getElementById('claimSeminarSelect');
  if (select) {
    select.value = seminarId;
  }
};

// Modal Registration handling
window.openRegModal = function (seminarId, seminarTitle) {
  const overlay = document.getElementById('seminarRegOverlay');
  document.getElementById('regSeminarId').value = seminarId;
  document.getElementById('regModalSeminarTitle').innerHTML = `<svg class="svg-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--gold)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle; margin-right:4px;"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> ${seminarTitle}`;
  
  // Prefill NIM if checked
  const checkNim = document.getElementById('nimInput').value.trim();
  if (checkNim) {
    document.getElementById('regNim').value = checkNim;
    document.getElementById('regEmail').value = `${checkNim.toLowerCase()}@student.ums.ac.id`;
  }
  
  overlay.classList.add('open');
};

window.closeRegModal = function () {
  document.getElementById('seminarRegOverlay').classList.remove('open');
};

// Direct Registration (No OTP)
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
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF_TOKEN },
      body: JSON.stringify({ member_id: memberId, email: email, seminar_id: seminarId })
    });
    const data = await res.json();

    if (data.success) {
      showToast('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--green)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>', data.message, 4000);
      closeRegModal();
      
      // Update check NIM and reload to show status
      document.getElementById('nimInput').value = memberId;
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

// Claim attendance
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
    showToast('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--gold)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>', 'Pilih seminar terlebih dahulu.', 3000);
    btn.disabled = false;
    btn.innerHTML = origText;
    return;
  }

  try {
    const res = await fetch('/api/seminar/claim/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF_TOKEN },
      body: JSON.stringify({ member_id: memberId, seminar_id: seminarId, claim_code: claimCode })
    });
    const data = await res.json();

    if (data.success) {
      showToast('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--gold)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 12 20 22 4 22 4 12"></polyline><rect x="2" y="7" width="20" height="5"></rect><line x1="12" y1="22" x2="12" y2="7"></line><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"></path><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"></path></svg>', data.message, 5000);
      document.getElementById('claimCode').value = '';
      
      // Update check NIM and reload to show updated status
      document.getElementById('nimInput').value = memberId;
      localStorage.setItem('seminar_nim', memberId);
      loadSeminars();
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

// Simple HTML escaping helper
function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
