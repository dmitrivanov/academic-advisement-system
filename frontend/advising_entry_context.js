(() => {
  'use strict';

  const allowedPaths = new Set(['/bmcc_student', '/high_school_student', '/advising-app_v1']);
  const storedPath = sessionStorage.getItem('cunyBeyondEntryPathV1');
  const entryPath = allowedPaths.has(storedPath) ? storedPath : '/advising-app_v1';

  document.querySelectorAll('a[href^="/advising-app_v1?returned="]').forEach(link => {
    const url = new URL(link.href, window.location.origin);
    link.href = `${entryPath}${url.search}`;
  });
})();
