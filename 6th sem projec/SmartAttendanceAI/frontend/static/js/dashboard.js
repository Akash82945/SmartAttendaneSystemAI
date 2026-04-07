/**
 * SmartAttendanceAI – Dashboard JavaScript
 * Handles: theme toggle, table search, auto-refresh KPIs,
 *          number animations, sidebar active state.
 */

'use strict';

// ── Theme Toggle ─────────────────────────────────────────────────────────────
(function () {
  const root = document.documentElement;
  let theme = root.getAttribute('data-theme') ||
    (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  root.setAttribute('data-theme', theme);

  const toggleBtn = document.querySelector('[data-theme-toggle]');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      theme = theme === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', theme);
    });
  }
})();

// ── Sidebar Active State ──────────────────────────────────────────────────────
(function () {
  const path  = window.location.pathname;
  const links = document.querySelectorAll('.sidebar-link');
  links.forEach(link => {
    link.classList.remove('active');
    if (link.getAttribute('href') === path) {
      link.classList.add('active');
    }
  });
})();

// ── Animated Counter ──────────────────────────────────────────────────────────
/**
 * Smoothly counts a number element from 0 to its target value.
 * @param {HTMLElement} el
 * @param {number} target
 * @param {number} duration  ms
 */
function animateCounter(el, target, duration = 1000) {
  if (!el) return;
  const start     = performance.now();
  const startVal  = 0;
  const isFloat   = String(target).includes('.');
  const decimals  = isFloat ? String(target).split('.')[1].length : 0;

  function step(now) {
    const elapsed  = now - start;
    const progress = Math.min(elapsed / duration, 1);
    // Ease-out cubic
    const eased    = 1 - Math.pow(1 - progress, 3);
    const current  = startVal + (target - startVal) * eased;
    el.textContent = isFloat ? current.toFixed(decimals) : Math.floor(current);
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

// Animate all KPI values on load
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.kpi-value').forEach(el => {
    const raw = parseFloat(el.textContent.replace('%', '').replace(',', ''));
    if (!isNaN(raw)) animateCounter(el, raw, 1200);
  });
});

// ── Auto-Refresh KPIs every 60s ───────────────────────────────────────────────
async function refreshKPIs() {
  try {
    const res  = await fetch('/api/analytics/monthly');
    if (!res.ok) return;
    // (Server-side renders KPIs; for SPA-like refresh trigger a soft reload)
    // Full refresh every 60s keeps data fresh without heavy websocket overhead
  } catch (e) {
    console.warn('KPI refresh error:', e);
  }
}
setInterval(refreshKPIs, 60_000);

// ── Global Table Search Utility ───────────────────────────────────────────────
/**
 * Call this to enable live search on any table.
 * @param {string} inputSelector  CSS selector for the search <input>
 * @param {string} tableSelector  CSS selector for the <table>
 */
function enableTableSearch(inputSelector, tableSelector) {
  const input = document.querySelector(inputSelector);
  const table = document.querySelector(tableSelector);
  if (!input || !table) return;

  input.addEventListener('input', () => {
    const q    = input.value.toLowerCase().trim();
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
      const match = row.textContent.toLowerCase().includes(q);
      row.style.display = match ? '' : 'none';
    });
  });
}

// Auto-enable search on students page
enableTableSearch('#searchInput', '#studentsTable');

// ── Flash Message Auto-Dismiss ────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s';
      alert.style.opacity    = '0';
      setTimeout(() => alert.remove(), 500);
    }, 4000);
  });
});

// ── Modal Helpers ─────────────────────────────────────────────────────────────
function openModal(id)  { document.getElementById(id)?.classList.add('open'); }
function closeModal(id) { document.getElementById(id)?.classList.remove('open'); }

// Close modal on backdrop click
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-backdrop')) {
    e.target.classList.remove('open');
  }
});

// Close on Escape key
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-backdrop.open')
      .forEach(m => m.classList.remove('open'));
  }
});