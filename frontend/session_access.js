(async function applySessionAccess() {
  try {
    const response = await fetch("/api/session", { credentials: "same-origin" });
    if (!response.ok) return;
    const session = await response.json();
    document.documentElement.dataset.userRole = session.role;
    if (!session.is_admin) {
      document.querySelectorAll('a[href^="/admin"]').forEach((link) => link.remove());
    }
  } catch (_) {
    // Server-side authorization remains authoritative if session lookup fails.
  }
})();
