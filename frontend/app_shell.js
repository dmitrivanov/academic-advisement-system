(function () {
  const currentPath = window.location.pathname;
  const items = [
    { href: '/program-selector', label: 'Programs', paths: ['/program-selector'] },
    { href: '/db-progress', label: 'My Progress', paths: ['/db-progress'] },
    { href: '/careers', label: 'Careers', paths: ['/careers'] },
    { href: '/transfer-analysis', label: 'Compare', paths: ['/transfer-analysis'] },
    { href: '/admin', label: 'Admin', paths: ['/admin'] }
  ];

  function linkMarkup(item) {
    const active = item.paths.some(path => currentPath === path || (path === '/admin' && currentPath.startsWith('/admin')));
    return `<a class="aas-link" href="${item.href}"${active ? ' aria-current="page"' : ''}>${item.label}</a>`;
  }

  function render() {
    if (!document.body || document.querySelector('.aas-header')) return;
    document.body.classList.add('has-app-shell');

    const header = document.createElement('header');
    header.className = 'aas-header';
    header.innerHTML = `
      <div class="aas-inner">
        <a class="aas-brand" href="/program-selector" aria-label="Academic Advisement home">
          <span class="aas-mark">AA</span>
          <span class="aas-brand-copy"><strong>Academic Advisement</strong><small>Plan with a complete curriculum view</small></span>
        </a>
        <button class="aas-menu-button" type="button" aria-expanded="false" aria-controls="aas-primary-nav" aria-label="Open navigation">☰</button>
        <nav class="aas-nav" id="aas-primary-nav" aria-label="Main navigation">
          ${items.map(linkMarkup).join('')}
          <a class="aas-link aas-logout" href="/logout">Log out</a>
        </nav>
      </div>`;
    document.body.prepend(header);

    const menuButton = header.querySelector('.aas-menu-button');
    const nav = header.querySelector('.aas-nav');
    menuButton.addEventListener('click', () => {
      const open = nav.classList.toggle('is-open');
      menuButton.setAttribute('aria-expanded', String(open));
      menuButton.textContent = open ? '×' : '☰';
    });

    const bottomNav = document.createElement('nav');
    bottomNav.className = 'aas-bottom-nav';
    bottomNav.setAttribute('aria-label', 'Mobile navigation');
    bottomNav.innerHTML = items.map(linkMarkup).join('');
    document.body.append(bottomNav);

    const footer = document.createElement('footer');
    footer.className = 'aas-footer';
    footer.textContent = 'Academic planning estimates should be confirmed with an academic advisor.';
    document.body.append(footer);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', render);
  else render();
})();
