// ── Toast Notifications ─────────────────────────────────────────
function showToast(msg, type = 'success') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${type === 'success' ? '✓' : '✕'}</span> ${msg}`;
  container.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transform = 'translateX(100%)'; toast.style.transition = '.3s ease'; }, 2800);
  setTimeout(() => toast.remove(), 3100);
}

// ── Task Status Update (AJAX) ────────────────────────────────────
async function updateTaskStatus(taskId, newStatus, selectEl) {
  const original = selectEl.dataset.original || selectEl.value;
  try {
    const res = await fetch(`/tasks/${taskId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus }),
    });
    if (!res.ok) throw new Error('Failed');
    const data = await res.json();
    selectEl.dataset.original = data.status;
    // Update badge styling
    const row = selectEl.closest('tr') || selectEl.closest('.task-item');
    if (row) {
      row.querySelectorAll('.status-indicator').forEach(el => {
        el.className = `badge badge-${data.status === 'in_progress' ? 'progress' : data.status}`;
        el.textContent = data.status === 'in_progress' ? 'In Progress' : data.status.charAt(0).toUpperCase() + data.status.slice(1);
      });
    }
    showToast('Status updated!', 'success');
  } catch (e) {
    selectEl.value = original;
    showToast('Update failed. Please try again.', 'error');
  }
}

// ── Delete confirmation ──────────────────────────────────────────
function confirmDelete(msg) {
  return confirm(msg || 'Are you sure you want to delete this?');
}

// ── Animated counters ────────────────────────────────────────────
function animateCounters() {
  document.querySelectorAll('.stat-value[data-target]').forEach(el => {
    const target = parseInt(el.dataset.target, 10);
    if (isNaN(target)) return;
    let cur = 0; const step = Math.max(1, Math.floor(target / 30));
    const timer = setInterval(() => {
      cur = Math.min(cur + step, target);
      el.textContent = cur;
      if (cur >= target) clearInterval(timer);
    }, 30);
  });
}

// ── Progress bar animation ───────────────────────────────────────
function animateProgressBars() {
  document.querySelectorAll('.progress-bar[data-width]').forEach(bar => {
    setTimeout(() => { bar.style.width = bar.dataset.width + '%'; }, 100);
  });
}

// ── Init ─────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  animateCounters();
  animateProgressBars();

  // Feather icons replace
  if (typeof feather !== 'undefined') feather.replace();

  // Auto-dismiss flash messages
  document.querySelectorAll('.alert-auto').forEach(el => {
    setTimeout(() => { el.style.opacity = '0'; el.style.transition = '.4s'; setTimeout(() => el.remove(), 400); }, 4000);
  });
});
