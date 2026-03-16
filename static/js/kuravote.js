// KuraVote theme colors
const THEME = {
  primary:      '#166534',
  primaryLight: '#16a34a',
  accent:       '#eab308',
  bg:           '#f0fdf4',
};


document.addEventListener('DOMContentLoaded', function () {

  // ── Hide page loader ──────────────────────────────────
  const loader = document.getElementById('page-loader');
  if (loader) {
    setTimeout(() => { loader.style.display = 'none'; }, 300);
  }

  // ── Auto-dismiss toasts after 4 seconds ───────────────
  document.querySelectorAll('.toast').forEach(function (el) {
    const toast = new bootstrap.Toast(el, { delay: 4000 });
    toast.show();
  });

  // ── Confirm delete actions ────────────────────────────
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      const message = el.dataset.confirm ||
                      'Are you sure you want to do this?';
      if (!confirm(message)) {
        e.preventDefault();
      }
    });
  });

  // ── Active sidebar link highlight ─────────────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.sidebar-item').forEach(function (link) {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });

  // ── Active bottom nav highlight ───────────────────────
  document.querySelectorAll('.bottom-nav-item').forEach(function (link) {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });

});