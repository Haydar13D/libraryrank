/**
 * LIBRARYRANK TV / KIOSK DISPLAY CONTROLLER
 * Handles auto-carousel, live clock, fullscreen, and background polling.
 */

const KIOSK_CONFIG = {
  SLIDE_DURATION_SEC: 15,
  POLL_INTERVAL_SEC: 60,
};

let currentSlideIdx = 0;
let totalSlides = 4;
let slideTimer = null;
let progressTimer = null;
let progressVal = 0;
let isPaused = false;
let dailyChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
  initClock();
  initCarousel();
  initFullscreen();
  initThemeToggle();
  fetchKioskData();

  // Polling data every 60s
  setInterval(fetchKioskData, KIOSK_CONFIG.POLL_INTERVAL_SEC * 1000);
});

/* -------------------------------------------------------------
   CLOCK & DATE
   ------------------------------------------------------------- */
function initClock() {
  const timeEl = document.getElementById('kioskTime');
  const dateEl = document.getElementById('kioskDate');

  function updateClock() {
    const now = new Date();

    // Time format (HH:mm:ss WIB)
    const hours = String(now.getHours()).padStart(2, '0');
    const mins = String(now.getMinutes()).padStart(2, '0');
    const secs = String(now.getSeconds()).padStart(2, '0');
    timeEl.textContent = `${hours}:${mins}:${secs} WIB`;

    // Date format in Indonesian
    const options = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
    dateEl.textContent = now.toLocaleDateString('id-ID', options);
  }

  updateClock();
  setInterval(updateClock, 1000);
}

/* -------------------------------------------------------------
   CAROUSEL & PROGRESS BAR
   ------------------------------------------------------------- */
function initCarousel() {
  const slides = document.querySelectorAll('.kiosk-slide');
  totalSlides = slides.length;

  const dotsContainer = document.getElementById('kioskDots');
  dotsContainer.innerHTML = '';

  for (let i = 0; i < totalSlides; i++) {
    const dot = document.createElement('div');
    dot.className = `kiosk-dot ${i === 0 ? 'active' : ''}`;
    dot.addEventListener('click', () => {
      goToSlide(i);
    });
    dotsContainer.appendChild(dot);
  }

  startSlideCycle();

  // Keyboard navigation
  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') {
      nextSlide();
    } else if (e.key === 'ArrowLeft') {
      prevSlide();
    } else if (e.key === ' ') {
      e.preventDefault();
      togglePause();
    }
  });
}

function startSlideCycle() {
  clearInterval(progressTimer);
  progressVal = 0;
  updateProgressBar(0);

  const stepMs = 100;
  const totalSteps = (KIOSK_CONFIG.SLIDE_DURATION_SEC * 1000) / stepMs;
  const increment = 100 / totalSteps;

  progressTimer = setInterval(() => {
    if (!isPaused) {
      progressVal += increment;
      updateProgressBar(progressVal);

      if (progressVal >= 100) {
        nextSlide();
      }
    }
  }, stepMs);
}

function updateProgressBar(val) {
  const bar = document.getElementById('kioskProgressBar');
  if (bar) {
    bar.style.width = `${Math.min(100, val)}%`;
  }
}

function goToSlide(idx) {
  const slides = document.querySelectorAll('.kiosk-slide');
  const dots = document.querySelectorAll('.kiosk-dot');

  slides.forEach((s, i) => {
    s.classList.toggle('active', i === idx);
  });

  dots.forEach((d, i) => {
    d.classList.toggle('active', i === idx);
  });

  currentSlideIdx = idx;
  startSlideCycle();
}

function nextSlide() {
  const nextIdx = (currentSlideIdx + 1) % totalSlides;
  goToSlide(nextIdx);
}

function prevSlide() {
  const prevIdx = (currentSlideIdx - 1 + totalSlides) % totalSlides;
  goToSlide(prevIdx);
}

function togglePause() {
  isPaused = !isPaused;
  const badge = document.querySelector('.kiosk-live-badge');
  if (badge) {
    badge.innerHTML = isPaused
      ? '<svg class="svg-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle; margin-right:4px;"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg> PAUSED'
      : '<span class="live-dot"></span>';
  }
}

/* -------------------------------------------------------------
   FULLSCREEN & THEME TOGGLE
   ------------------------------------------------------------- */
function initFullscreen() {
  const btn = document.getElementById('btnFullscreen');
  if (!btn) return;

  btn.addEventListener('click', () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch((err) => {
        console.warn('Fullscreen error:', err);
      });
    } else {
      document.exitFullscreen().catch((err) => {
        console.warn('Exit fullscreen error:', err);
      });
    }
  });
}

function initThemeToggle() {
  const btn = document.getElementById('btnThemeToggle');
  if (!btn) return;

  btn.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('kiosk_theme', next);

    if (dailyChartInstance) {
      const isLight = next === 'light';
      const gridColor = isLight ? 'rgba(0, 0, 0, 0.06)' : 'rgba(255, 255, 255, 0.05)';
      const tickColor = isLight ? '#64748b' : '#94a3b8';
      dailyChartInstance.options.scales.x.grid.color = gridColor;
      dailyChartInstance.options.scales.x.ticks.color = tickColor;
      dailyChartInstance.options.scales.y.grid.color = gridColor;
      dailyChartInstance.options.scales.y.ticks.color = tickColor;
      dailyChartInstance.update();
    }
  });
}

/* -------------------------------------------------------------
   DATA FETCHING & DOM POPULATION
   ------------------------------------------------------------- */
async function fetchKioskData() {
  try {
    const [overviewRes, facultiesRes] = await Promise.all([
      fetch('/api/overview/'),
      fetch('/api/faculties/')
    ]);
    
    if (!overviewRes.ok) throw new Error('Failed to fetch overview');
    const data = await overviewRes.json();
    
    let faculties = [];
    if (facultiesRes.ok) {
      try {
        const facData = await facultiesRes.json();
        faculties = facData.faculties || [];
      } catch (e) {}
    }

    renderLeaderboardSlide(data.leaderboard || []);
    renderFacultiesSlide(faculties.length > 0 ? faculties : (data.faculties || []));
    renderStatsSlide(data, faculties);
  } catch (err) {
    console.error('Error fetching kiosk data:', err);
  }
}

function getAvatarColor(rank) {
  if (rank === 1) return '#f59e0b';
  if (rank === 2) return '#94a3b8';
  if (rank === 3) return '#d97706';
  const colors = ['#1cbdb3', '#3b82f6', '#8b5cf6', '#ec4899', '#10b981', '#6366f1'];
  return colors[rank % colors.length];
}

function getInitials(name) {
  if (!name) return 'U';
  const parts = name.trim().split(' ');
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
  return (parts[0][0] + parts[1][0]).toUpperCase();
}

function renderLeaderboardSlide(members) {
  if (!members || members.length === 0) return;

  // Podium Spots (1, 2, 3)
  const rank1 = members[0];
  const rank2 = members[1];
  const rank3 = members[2];

  if (rank1) {
    document.getElementById('podiumName1').textContent = rank1.name || rank1.id;
    document.getElementById('podiumSub1').textContent = rank1.faculty ? `${rank1.faculty} • ${rank1.id}` : (rank1.id || '');
    document.getElementById('podiumXp1').textContent = `${(rank1.visits || 0).toLocaleString('id-ID')} XP`;
    document.getElementById('podiumAvatar1').textContent = getInitials(rank1.name);
  }

  if (rank2) {
    document.getElementById('podiumName2').textContent = rank2.name || rank2.id;
    document.getElementById('podiumSub2').textContent = rank2.faculty ? `${rank2.faculty} • ${rank2.id}` : (rank2.id || '');
    document.getElementById('podiumXp2').textContent = `${(rank2.visits || 0).toLocaleString('id-ID')} XP`;
    document.getElementById('podiumAvatar2').textContent = getInitials(rank2.name);
  }

  if (rank3) {
    document.getElementById('podiumName3').textContent = rank3.name || rank3.id;
    document.getElementById('podiumSub3').textContent = rank3.faculty ? `${rank3.faculty} • ${rank3.id}` : (rank3.id || '');
    document.getElementById('podiumXp3').textContent = `${(rank3.visits || 0).toLocaleString('id-ID')} XP`;
    document.getElementById('podiumAvatar3').textContent = getInitials(rank3.name);
  }

  // Runners up (Rank 4 to 10)
  const runnersList = document.getElementById('runnersList');
  if (runnersList) {
    runnersList.innerHTML = '';
    const runners = members.slice(3, 10);
    runners.forEach((m, idx) => {
      const rankNum = idx + 4;
      const card = document.createElement('div');
      card.className = 'runner-card';
      const subInfo = m.faculty ? `${m.faculty} • ${m.id}` : (m.id || '');
      card.innerHTML = `
        <div class="runner-left">
          <div class="runner-rank">#${rankNum}</div>
          <div class="runner-name-group">
            <div class="runner-name" title="${m.name}">${m.name}</div>
            <div class="runner-faculty">${subInfo}</div>
          </div>
        </div>
        <div class="runner-right">
          <div class="runner-xp">${(m.visits || 0).toLocaleString('id-ID')} XP</div>
          <div class="runner-level">${m.level ? m.level.name : 'Reader'}</div>
        </div>
      `;
      runnersList.appendChild(card);
    });
  }
}

function renderFacultiesSlide(faculties) {
  const container = document.getElementById('facultyGrid');
  if (!container || !faculties || faculties.length === 0) return;

  // Sort by points or visits descending
  const sorted = [...faculties].sort((a, b) => (b.points || b.visits || 0) - (a.points || a.visits || 0)).slice(0, 6);

  container.innerHTML = '';
  sorted.forEach((fac, idx) => {
    const isTop = idx === 0;
    const card = document.createElement('div');
    card.className = `faculty-kiosk-card ${isTop ? 'top-rank' : ''}`;

    const color = fac.color || '#1cbdb3';
    const totalXP = (fac.points || fac.visits || 0).toLocaleString('id-ID');
    const students = fac.student_count || fac.members_count || '-';

    card.innerHTML = `
      <div>
        <div class="faculty-kiosk-header">
          <div class="faculty-kiosk-badge" style="background-color: ${color};">
            ${fac.code ? fac.code.substring(0, 3) : 'FK'}
          </div>
          <div class="faculty-kiosk-rank">#${idx + 1}</div>
        </div>
        <div class="faculty-kiosk-name">${fac.name}</div>
      </div>
      <div class="faculty-kiosk-stats">
        <div class="faculty-stat-item">
          <p>Total Kontribusi</p>
          <h4 class="xp-val">${totalXP} XP</h4>
        </div>
        <div class="faculty-stat-item">
          <p>Anggota Aktif</p>
          <h4>${students} Mahasiswa</h4>
        </div>
      </div>
    `;
    container.appendChild(card);
  });
}

function renderStatsSlide(data, faculties = []) {
  // Counters from nested data.stats or root
  const stats = data.stats || {};
  const totalVisits = stats.total_visitors !== undefined ? stats.total_visitors : (data.total_visits || 0);
  const totalBorrows = stats.total_books !== undefined ? stats.total_books : (data.total_borrows || 0);
  const activeMembers = stats.active_members !== undefined ? stats.active_members : (data.active_members || (data.leaderboard ? data.leaderboard.length : 0));
  
  let topFacultyName = '-';
  if (data.top_faculty && data.top_faculty.name) {
    topFacultyName = data.top_faculty.name;
  } else if (faculties && faculties.length > 0) {
    const sortedFac = [...faculties].sort((a, b) => (b.points || b.visits || b.visitors || 0) - (a.points || a.visits || a.visitors || 0));
    topFacultyName = sortedFac[0].name;
  }

  const elV = document.getElementById('statVisits');
  const elB = document.getElementById('statBorrows');
  const elM = document.getElementById('statMembers');
  const elF = document.getElementById('statTopFaculty');

  if (elV) elV.textContent = Number(totalVisits).toLocaleString('id-ID');
  if (elB) elB.textContent = Number(totalBorrows).toLocaleString('id-ID');
  if (elM) elM.textContent = Number(activeMembers).toLocaleString('id-ID');
  if (elF) elF.textContent = topFacultyName;

  // Render Daily Visits Chart
  const canvas = document.getElementById('kioskDailyChart');
  if (canvas && window.Chart) {
    const dailyData = data.daily_visits || [340, 420, 510, 480, 590, 210, 80];
    const days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'];

    if (dailyChartInstance) {
      dailyChartInstance.data.datasets[0].data = dailyData;
      dailyChartInstance.update();
    } else {
      const ctx = canvas.getContext('2d');
      dailyChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: days,
          datasets: [{
            label: 'Kunjungan Harian',
            data: dailyData,
            borderColor: '#1cbdb3',
            backgroundColor: 'rgba(28, 189, 179, 0.15)',
            borderWidth: 3,
            tension: 0.4,
            fill: true,
            pointBackgroundColor: '#1cbdb3',
            pointBorderColor: '#ffffff',
            pointRadius: 5,
            pointHoverRadius: 7
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: '#111827',
              titleColor: '#ffffff',
              bodyColor: '#1cbdb3',
              displayColors: false,
              padding: 10
            }
          },
          scales: {
            x: {
              grid: { color: 'rgba(255, 255, 255, 0.05)' },
              ticks: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', weight: '600' } }
            },
            y: {
              grid: { color: 'rgba(255, 255, 255, 0.05)' },
              ticks: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans' } },
              beginAtZero: true
            }
          }
        }
      });
    }
  }
}
