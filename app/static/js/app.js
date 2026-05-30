let toastTimer = null;

function showToast(message, type = 'info') {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.className = `toast ${type}`;
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.classList.add('hidden');
  }, 3000);
}

function addActivityItem(type, id, points, name) {
  const list = document.querySelector('.activity-list');
  if (!list) return;
  const empty = document.querySelector('.empty-state');
  if (empty) empty.remove();

  const icon = type === 'chore' ? '🧹' : '⭐';
  const li = document.createElement('li');
  li.className = 'activity-item earned';
  li.innerHTML = `
    <span class="act-icon">${icon}</span>
    <span class="act-name">${name}</span>
    <span class="act-pts green">+${points} pts</span>
  `;
  list.prepend(li);
}
