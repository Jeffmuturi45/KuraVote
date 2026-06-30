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


// ═══════════════════════════════════════════════
// KURAVOTE GUIDED TOUR ENGINE
// ═══════════════════════════════════════════════

function startKuraTour(steps, options = {}) {
  let currentStep = 0;
  const tourId     = options.tourId || 'default';
  const csrfToken  = document.querySelector('[name=csrfmiddlewaretoken]')
                      ?.value || getCookie('csrftoken');

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
  }

  // ── Overlay ──────────────────────────────────────────
  const overlay = document.createElement('div');
  overlay.id = 'kura-tour-overlay';
  overlay.style.cssText = `
    position:fixed; inset:0; background:rgba(15,61,32,0.55);
    z-index:9000; pointer-events:none;
  `;
  document.body.appendChild(overlay);

  // ── Tooltip card ─────────────────────────────────────
  const tooltip = document.createElement('div');
  tooltip.id = 'kura-tour-tooltip';
  tooltip.style.cssText = `
    position:fixed; background:#fff; border-radius:14px;
    padding:18px 20px; max-width:300px; z-index:9001;
    box-shadow:0 12px 36px rgba(0,0,0,0.25);
    font-family:'DM Sans',sans-serif; transition:all 0.25s ease;
  `;
  document.body.appendChild(tooltip);

  // ── Spotlight cutout ─────────────────────────────────
  const spotlight = document.createElement('div');
  spotlight.id = 'kura-tour-spotlight';
  spotlight.style.cssText = `
    position:fixed; border-radius:12px; z-index:9000;
    box-shadow:0 0 0 9999px rgba(15,61,32,0.55);
    transition:all 0.3s ease; pointer-events:none;
    border:2px solid #eab308;
  `;
  document.body.appendChild(spotlight);
  overlay.remove(); // spotlight box-shadow handles the dim effect

  function renderStep() {
    const step = steps[currentStep];
    const el   = document.querySelector(step.target);

    if (!el) {
      // Target not found — skip to next step
      if (currentStep < steps.length - 1) {
        currentStep++;
        renderStep();
      } else {
        endTour();
      }
      return;
    }

    const rect = el.getBoundingClientRect();

    // Position spotlight on target
    spotlight.style.top    = (rect.top - 6) + 'px';
    spotlight.style.left   = (rect.left - 6) + 'px';
    spotlight.style.width  = (rect.width + 12) + 'px';
    spotlight.style.height = (rect.height + 12) + 'px';

    el.scrollIntoView({ behavior: 'smooth', block: 'center' });

    // Build tooltip content
    const isLast  = currentStep === steps.length - 1;
    const isFirst = currentStep === 0;

    tooltip.innerHTML = `
      <div style="display:flex; align-items:center; gap:8px;
                  margin-bottom:10px;">
        <div style="width:26px; height:26px; border-radius:50%;
                    background:#16a34a; color:#fff; display:flex;
                    align-items:center; justify-content:center;
                    font-size:11px; font-weight:700;
                    font-family:'Sora',sans-serif; flex-shrink:0;">
          ${currentStep + 1}
        </div>
        <div style="font-family:'Sora',sans-serif; font-weight:700;
                    font-size:14px; color:#166534;">
          ${step.title}
        </div>
      </div>
      <div style="font-size:13px; color:#475569; line-height:1.5;
                  margin-bottom:14px;">
        ${step.text}
      </div>
      <div style="display:flex; align-items:center;
                  justify-content:space-between;">
        <div style="font-size:11px; color:#94a3b8;">
          ${currentStep + 1} of ${steps.length}
        </div>
        <div style="display:flex; gap:6px;">
          <button onclick="kuraTourSkip()"
                  style="background:none; border:none;
                         color:#94a3b8; font-size:12px;
                         cursor:pointer; padding:6px 10px;">
            Skip
          </button>
          ${!isFirst ? `
            <button onclick="kuraTourPrev()"
                    style="background:#f0fdf4; border:1px solid #bbf7d0;
                           color:#166534; border-radius:8px;
                           padding:6px 12px; font-size:12px;
                           cursor:pointer;">
              Back
            </button>` : ''}
          <button onclick="kuraTourNext()"
                  style="background:#16a34a; border:none; color:#fff;
                         border-radius:8px; padding:6px 14px;
                         font-size:12px; font-weight:600;
                         cursor:pointer;">
            ${isLast ? 'Finish' : 'Next'}
          </button>
        </div>
      </div>
    `;

    // Position tooltip near the element
    let top  = rect.bottom + 14;
    let left = rect.left;

    if (top + 160 > window.innerHeight) {
      top = rect.top - 170;
    }
    if (left + 300 > window.innerWidth) {
      left = window.innerWidth - 320;
    }
    if (left < 10) left = 10;

    tooltip.style.top  = top + 'px';
    tooltip.style.left = left + 'px';
  }

  window.kuraTourNext = function() {
    if (currentStep < steps.length - 1) {
      currentStep++;
      renderStep();
    } else {
      endTour();
    }
  };

  window.kuraTourPrev = function() {
    if (currentStep > 0) {
      currentStep--;
      renderStep();
    }
  };

  window.kuraTourSkip = function() {
    endTour();
  };

  function endTour() {
    tooltip.remove();
    spotlight.remove();
    const ov = document.getElementById('kura-tour-overlay');
    if (ov) ov.remove();

    // Mark as seen on server
    fetch('/tour/seen/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    }).catch(() => {});
  }

  renderStep();
}