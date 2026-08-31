(function () {
  const state = { graph: null, completed: new Set(), lastFocus: null };

  function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
  }

  function ensureModal() {
    let modal = document.getElementById('curriculumGraphModal');
    if (modal) return modal;
    modal = document.createElement('div');
    modal.id = 'curriculumGraphModal';
    modal.className = 'curriculum-graph-modal';
    modal.hidden = true;
    modal.innerHTML = `<div class="curriculum-graph-backdrop" data-graph-close></div><section class="curriculum-graph-dialog" role="dialog" aria-modal="true" aria-labelledby="curriculumGraphTitle"><header class="curriculum-graph-toolbar"><div><h2 id="curriculumGraphTitle">Course dependency map</h2><p id="curriculumGraphSubtitle">Loading curriculum relationships…</p></div><button class="curriculum-graph-close" type="button" data-graph-close>Close</button></header><div id="curriculumGraphContent" class="curriculum-graph-scroll"></div></section>`;
    document.body.appendChild(modal);
    modal.querySelectorAll('[data-graph-close]').forEach(item => item.addEventListener('click', close));
    modal.addEventListener('keydown', event => { if (event.key === 'Escape') close(); });
    return modal;
  }

  function nodeCard(node) {
    const completed = state.completed.has(node.code) ? ' completed' : '';
    return `<article class="curriculum-node${completed}" data-node-id="${node.id}"><div class="code">${escapeHtml(node.code)}</div><div class="title">${escapeHtml(node.title)}</div><div class="credits">${node.credits} credit${node.credits === 1 ? '' : 's'}</div></article>`;
  }

  function render(graph, target) {
    state.graph = graph;
    const nodes = new Map(graph.nodes.map(node => [node.id, node]));
    const mainClusterTypes = new Set(['program_required']);
    const mainIds = new Set(graph.clusters.filter(cluster => mainClusterTypes.has(cluster.type)).flatMap(cluster => cluster.node_ids));
    // Required-course ancestors may live in Common/Flexible Core or in the
    // support bucket. Pull only ancestors that actually unlock a required node.
    let changed = true;
    while (changed) {
      changed = false;
      graph.edges.forEach(edge => {
        if (edge.relation_type === 'prerequisite' && mainIds.has(edge.target_id) && !mainIds.has(edge.source_id)) {
          mainIds.add(edge.source_id);
          changed = true;
        }
      });
    }
    if (!mainIds.size) graph.nodes.forEach(node => mainIds.add(node.id));
    const mainLayers = graph.layers.map(layer => layer.filter(id => mainIds.has(id))).filter(layer => layer.length);
    const seenClusters = new Set();
    const secondary = graph.clusters.filter(cluster => {
      if (mainClusterTypes.has(cluster.type) || !cluster.node_ids.length) return false;
      const signature = `${cluster.name}|${cluster.node_ids.join(',')}`;
      if (seenClusters.has(signature)) return false;
      seenClusters.add(signature);
      return true;
    });
    target.innerHTML = `<div class="curriculum-graph-legend"><span>Prerequisite</span><span class="coreq">Corequisite</span><span class="recommended">Recommended sequence</span></div>${graph.cycle_node_ids.length ? '<p class="curriculum-cycle-warning">This graph contains a circular relationship. An administrator should review the highlighted curriculum data.</p>' : ''}<section class="curriculum-tree-panel"><h3>Required-course dependency tree</h3><p class="curriculum-cluster-meta">Read from top to bottom. A branching line means the later course depends on an earlier course.</p><div class="curriculum-graph-canvas" id="curriculumGraphCanvas"><svg class="curriculum-edge-layer" aria-hidden="true"></svg><div class="curriculum-levels">${mainLayers.map((layer, index) => `<div class="curriculum-level" aria-label="Dependency level ${index + 1}">${layer.map(id => nodes.has(id) ? nodeCard(nodes.get(id)) : '').join('')}</div>`).join('')}</div></div></section>${secondary.map(cluster => `<section class="curriculum-cluster ${escapeHtml(cluster.type)}"><h3>${escapeHtml(cluster.name)}</h3><p class="curriculum-cluster-meta">${cluster.required_credits ? `${cluster.required_credits} credits required` : cluster.required_course_count ? `${cluster.required_course_count} course(s) required` : 'Separate curriculum group'}</p><div class="curriculum-cluster-nodes">${cluster.node_ids.map(id => nodes.has(id) ? nodeCard(nodes.get(id)) : '').join('')}</div></section>`).join('')}`;
    requestAnimationFrame(drawEdges);
  }

  function drawEdges() {
    const canvas = document.getElementById('curriculumGraphCanvas');
    if (!canvas || !state.graph) return;
    const svg = canvas.querySelector('svg');
    const bounds = canvas.getBoundingClientRect();
    svg.setAttribute('viewBox', `0 0 ${bounds.width} ${bounds.height}`);
    svg.innerHTML = '';
    state.graph.edges.forEach(edge => {
      const source = canvas.querySelector(`[data-node-id="${edge.source_id}"]`);
      const target = canvas.querySelector(`[data-node-id="${edge.target_id}"]`);
      if (!source || !target) return;
      const a = source.getBoundingClientRect(), b = target.getBoundingClientRect();
      const x1 = a.left + a.width / 2 - bounds.left, y1 = a.bottom - bounds.top;
      const x2 = b.left + b.width / 2 - bounds.left, y2 = b.top - bounds.top;
      const mid = y1 + (y2 - y1) / 2;
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', `M ${x1} ${y1} C ${x1} ${mid}, ${x2} ${mid}, ${x2} ${y2}`);
      path.setAttribute('fill', 'none');
      path.setAttribute('stroke', edge.relation_type === 'corequisite' ? '#8b5cf6' : edge.relation_type === 'recommended' ? '#f59e0b' : '#2563eb');
      path.setAttribute('stroke-width', edge.origin === 'admin' ? '3.5' : '2.5');
      if (edge.relation_type !== 'prerequisite') path.setAttribute('stroke-dasharray', edge.relation_type === 'corequisite' ? '7 5' : '3 5');
      svg.appendChild(path);
    });
  }

  async function load(programCode, target) {
    target.innerHTML = '<div class="curriculum-graph-empty">Loading dependency map…</div>';
    const response = await fetch(`/api/db/programs/${encodeURIComponent(programCode)}/graph`);
    if (!response.ok) throw new Error((await response.json().catch(() => ({}))).detail || 'Could not load dependency map');
    const graph = await response.json();
    render(graph, target);
    return graph;
  }

  async function open(programCode, options = {}) {
    const modal = ensureModal();
    state.lastFocus = document.activeElement;
    state.completed = new Set(options.completedCourseCodes || []);
    modal.hidden = false;
    document.body.style.overflow = 'hidden';
    const content = modal.querySelector('#curriculumGraphContent');
    try {
      const graph = await load(programCode, content);
      modal.querySelector('#curriculumGraphTitle').textContent = `${graph.program.name} dependency map`;
      modal.querySelector('#curriculumGraphSubtitle').textContent = `${graph.program.institution} · ${graph.program.catalog_year || 'current catalog'} · administrator-editable relationships`;
    } catch (error) {
      content.innerHTML = `<div class="curriculum-graph-error">${escapeHtml(error.message)}</div>`;
    }
    modal.querySelector('.curriculum-graph-close').focus();
  }

  function close() {
    const modal = document.getElementById('curriculumGraphModal');
    if (!modal) return;
    modal.hidden = true;
    document.body.style.overflow = '';
    state.lastFocus?.focus?.();
  }

  window.addEventListener('resize', drawEdges);
  window.CurriculumGraph = { open, close, load, render, isSupported: code => ['CS','CCNY_CS_BS','BC_CS_BS','JJAY_CSIS_BS'].includes(code) };
})();
