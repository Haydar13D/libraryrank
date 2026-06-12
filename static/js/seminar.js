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
        <span class="material-icons-outlined" style="font-size: 2.5rem; color: var(--muted); margin-bottom: 10px;">event_note</span>
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
      badgeHtml = `<span style="background: rgba(47,49,133,0.08); color: var(--primary); padding: 4px 10px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;"><span class="material-icons-outlined" style="font-size:0.85rem;">assignment</span> TERDAFTAR</span>`;
      
      if (sem.claim_code_active) {
        buttonHtml = `<button onclick="goToClaimTab('${sem.id}')" style="width: 100%; padding: 9px; border-radius: 8px; border: none; background: var(--primary); color: #fff; font-family: 'Inter', sans-serif; font-weight: 600; cursor: pointer; font-size: 0.82rem;">Klaim Kehadiran Sekarang</button>`;
      } else {
        buttonHtml = `<button disabled style="width: 100%; padding: 9px; border-radius: 8px; border: 1px solid var(--border); background: var(--surface2); color: var(--muted); font-family: 'Inter', sans-serif; font-weight: 600; font-size: 0.82rem;">Terdaftar (Klaim Hari-H)</button>`;
      }
    } else {
      // not_registered
      if (sem.is_upcoming) {
        badgeHtml = `<span style="background: var(--surface2); color: var(--muted); padding: 4px 10px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;"><span class="material-icons-outlined" style="font-size:0.85rem;">schedule</span> BELUM DIBUKA</span>`;
        buttonHtml = `<button disabled style="width: 100%; padding: 9px; border-radius: 8px; border: 1px solid var(--border); background: var(--surface2); color: var(--muted); font-family: 'Inter', sans-serif; font-weight: 600; font-size: 0.82rem;">Pendaftaran Belum Dibuka</button>`;
      } else if (sem.is_closed) {
        badgeHtml = `<span style="background: rgba(239,68,68,0.08); color: var(--red); padding: 4px 10px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;"><span class="material-icons-outlined" style="font-size:0.85rem;">cancel</span> DITUTUP</span>`;
        buttonHtml = `<button disabled style="width: 100%; padding: 9px; border-radius: 8px; border: 1px solid var(--border); background: var(--surface2); color: var(--muted); font-family: 'Inter', sans-serif; font-weight: 600; font-size: 0.82rem;">Tutup</button>`;
      } else if (sem.is_open) {
        badgeHtml = `<span style="background: rgba(16,185,129,0.08); color: var(--green); padding: 4px 10px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;"><span class="live-dot" style="background:var(--green); position:static; display:inline-block; margin:0;"></span>PENDAFTARAN DIBUKA</span>`;
        buttonHtml = `<button onclick="openRegModal('${sem.id}', '${escapeHtml(sem.title)}')" style="width: 100%; padding: 9px; border-radius: 8px; border: none; background: var(--primary); color: #fff; font-family: 'Inter', sans-serif; font-weight: 600; cursor: pointer; font-size: 0.82rem;">Daftar Seminar (+${sem.points_register} XP)</button>`;
      }
    }

    return `
      <div class="card-block" style="border-radius: var(--radius); padding: 18px; border: 1px solid ${sem.reg_status !== 'not_registered' ? 'var(--primary)' : 'var(--border)'}; display: flex; flex-direction: column; justify-content: space-between; transition: border-color 0.15s;">
        <div>
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; flex-wrap: wrap; gap: 6px;">
            ${badgeHtml}
            <span style="font-size: 0.72rem; color: var(--muted); font-weight: 600; border: 1px solid var(--border); padding: 3px 8px; border-radius: 4px; display: inline-flex; align-items: center; gap: 3px;"><span class="material-icons-outlined" style="font-size:0.82rem;">stars</span> +${sem.points_attend} XP</span>
          </div>
          <h4 style="font-size: 0.95rem; font-weight: 700; color: var(--text); margin-bottom: 6px; line-height: 1.4;">${sem.title}</h4>
          <div style="font-size: 0.78rem; color: var(--muted); margin-bottom: 3px; display: flex; align-items: center; gap: 5px;">
            <span class="material-icons-outlined" style="font-size: 0.9rem; color: var(--muted);">person</span> <strong>Speaker:</strong> ${sem.speaker}
          </div>
          <div style="font-size: 0.78rem; color: var(--muted); margin-bottom: 10px; display: flex; align-items: center; gap: 5px;">
            <span class="material-icons-outlined" style="font-size: 0.9rem; color: var(--muted);">schedule</span> <strong>Waktu:</strong> ${sem.date_formatted}
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

  // Filter only seminars where status is 'registered' or 'attended' (so they can select it for claim)
  const registeredSeminars = loadedSeminarsList.filter(s => s.reg_status === 'registered' || s.reg_status === 'attended');

  if (registeredSeminars.length === 0) {
    select.innerHTML = '<option value="" disabled selected>-- Masukkan NIM yang sudah terdaftar --</option>';
    return;
  }

  select.innerHTML = `
    <option value="" disabled ${!currentSelectVal ? 'selected' : ''}>-- Pilih Seminar --</option>
    ${registeredSeminars.map(sem => `
      <option value="${sem.id}" ${currentSelectVal == sem.id ? 'selected' : ''} ${sem.reg_status === 'attended' ? 'disabled style="color:var(--muted);"' : ''}>
        ${sem.title} (${sem.reg_status === 'attended' ? 'Sudah Hadir' : 'Klaim XP Kehadiran'})
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
  document.getElementById('regModalSeminarTitle').innerHTML = `<span class="material-icons-outlined" style="vertical-align: middle; color: var(--gold); font-size: 1.1rem; margin-right: 4px;">push_pin</span> ${seminarTitle}`;
  
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
      showToast('<span class="material-icons-outlined" style="color:var(--green)">celebration</span>', data.message, 4000);
      closeRegModal();
      
      // Update check NIM and reload to show status
      document.getElementById('nimInput').value = memberId;
      localStorage.setItem('seminar_nim', memberId);
      loadSeminars();
    } else {
      showToast('<span class="material-icons-outlined" style="color:var(--red)">cancel</span>', data.error || 'Gagal mendaftar.', 4000);
    }
  } catch (err) {
    console.error(err);
    showToast('<span class="material-icons-outlined" style="color:var(--red)">cancel</span>', 'Terjadi kesalahan jaringan.', 3000);
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
    showToast('<span class="material-icons-outlined" style="color:var(--gold)">warning</span>', 'Pilih seminar terlebih dahulu.', 3000);
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
      showToast('<span class="material-icons-outlined" style="color:var(--gold)">redeem</span>', data.message, 5000);
      document.getElementById('claimCode').value = '';
      
      // Update check NIM and reload to show updated status
      document.getElementById('nimInput').value = memberId;
      localStorage.setItem('seminar_nim', memberId);
      loadSeminars();
    } else {
      showToast('<span class="material-icons-outlined" style="color:var(--red)">cancel</span>', data.error || 'Gagal mengklaim kehadiran.', 4000);
    }
  } catch (err) {
    console.error(err);
    showToast('<span class="material-icons-outlined" style="color:var(--red)">cancel</span>', 'Terjadi kesalahan jaringan.', 3000);
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
