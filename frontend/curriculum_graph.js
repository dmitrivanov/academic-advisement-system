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

  function relationshipSummary(node, graph) {
    const nodeById = new Map(graph.nodes.map(item => [item.id, item]));
    const incoming = graph.edges.filter(edge => edge.target_id === node.id).map(edge => nodeById.get(edge.source_id)?.code).filter(Boolean);
    const outgoing = graph.edges.filter(edge => edge.source_id === node.id).map(edge => nodeById.get(edge.target_id)?.code).filter(Boolean);
    return { incoming, outgoing };
  }

  function nodeCard(node, graph) {
    const completed = state.completed.has(node.code) ? ' completed' : '';
    const relationships = relationshipSummary(node, graph);
    const prerequisites = relationships.incoming.length ? relationships.incoming.join(' or ') : 'None shown';
    const unlocks = relationships.outgoing.length ? relationships.outgoing.join(', ') : 'No later course shown';
    return `<button type="button" class="curriculum-node${completed}" data-node-id="${node.id}" aria-expanded="false"><span class="node-topline"><span class="code">${escapeHtml(node.code)}</span><span class="node-expand" aria-hidden="true">+</span></span><span class="node-details"><span class="title">${escapeHtml(node.title)}</span><span class="credits">${node.credits} credit${node.credits === 1 ? '' : 's'}</span><span class="relationship"><strong>Needs:</strong> ${escapeHtml(prerequisites)}</span><span class="relationship"><strong>Unlocks:</strong> ${escapeHtml(unlocks)}</span></span></button>`;
  }

  function layeredSubset(nodeIds, graph) {
    const ids = new Set(nodeIds);
    const inbound = new Map([...ids].map(id => [id, 0]));
    const outbound = new Map([...ids].map(id => [id, []]));
    graph.edges.forEach(edge => {
      if (edge.relation_type !== 'prerequisite' || !ids.has(edge.source_id) || !ids.has(edge.target_id)) return;
      outbound.get(edge.source_id).push(edge.target_id);
      inbound.set(edge.target_id, inbound.get(edge.target_id) + 1);
    });
    let ready = [...ids].filter(id => inbound.get(id) === 0).sort((a, b) => a - b);
    const layers = [], emitted = new Set();
    while (ready.length) {
      const level = ready;
      layers.push(level);
      ready = [];
      level.forEach(source => {
        emitted.add(source);
        outbound.get(source).forEach(target => {
          inbound.set(target, inbound.get(target) - 1);
          if (inbound.get(target) === 0) ready.push(target);
        });
      });
      ready.sort((a, b) => a - b);
    }
    const remaining = [...ids].filter(id => !emitted.has(id));
    if (remaining.length) layers.push(remaining);
    return layers;
  }

  function clusterRequirement(cluster) {
    if (cluster.required_credits) return `${cluster.required_credits} credits`;
    if (cluster.required_course_count) return `${cluster.required_course_count} course${cluster.required_course_count === 1 ? '' : 's'}`;
    return `${cluster.node_ids.length} option${cluster.node_ids.length === 1 ? '' : 's'}`;
  }

  function clusterBranch(cluster, nodes, graph) {
    const layers = layeredSubset(cluster.node_ids, graph);
    const hasSequence = layers.length > 1;
    return `<details class="curriculum-cluster ${escapeHtml(cluster.type)}"><summary><span><strong>${escapeHtml(cluster.name)}</strong><small>${escapeHtml(clusterRequirement(cluster))}${hasSequence ? ' · sequence available' : ''}</small></span><span class="cluster-chevron" aria-hidden="true">⌄</span></summary><div class="curriculum-mini-branch">${layers.map((layer, index) => `${index ? '<div class="mini-branch-arrow" aria-hidden="true">↓</div>' : ''}<div class="curriculum-mini-level" aria-label="${escapeHtml(cluster.name)} level ${index + 1}">${layer.map(id => nodes.has(id) ? nodeCard(nodes.get(id), graph) : '').join('')}</div>`).join('')}</div></details>`;
  }

  function attachInteractions(target) {
    if (target.dataset.graphInteractionsAttached) return;
    target.dataset.graphInteractionsAttached = 'true';
    target.addEventListener('click', event => {
      const card = event.target.closest('.curriculum-node');
      if (!card || !target.contains(card)) return;
      const expanded = card.getAttribute('aria-expanded') === 'true';
      card.setAttribute('aria-expanded', String(!expanded));
      card.classList.toggle('expanded', !expanded);
      card.querySelector('.node-expand').textContent = expanded ? '+' : '−';
      requestAnimationFrame(drawEdges);
    });
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
      if (mainClusterTypes.has(cluster.type) || cluster.type === 'prerequisite_support' || !cluster.node_ids.length) return false;
      const signature = `${cluster.name}|${cluster.node_ids.join(',')}`;
      if (seenClusters.has(signature)) return false;
      seenClusters.add(signature);
      return true;
    });
    target.innerHTML = `<div class="curriculum-graph-legend"><span>Prerequisite</span><span class="coreq">Corequisite</span><span class="recommended">Recommended sequence</span><em>Click any course card for details</em></div>${graph.cycle_node_ids.length ? '<p class="curriculum-cycle-warning">This graph contains a circular relationship. An administrator should review the highlighted curriculum data.</p>' : ''}<section class="curriculum-branch-section"><div class="curriculum-branch-heading"><div><h3>Curriculum group branches</h3><p>Compact by default. Open a group to see its courses and any internal sequence.</p></div><span>${secondary.length} groups</span></div><div class="curriculum-branch-grid">${secondary.map(cluster => clusterBranch(cluster, nodes, graph)).join('')}</div></section><section class="curriculum-tree-panel"><h3>Required-course dependency tree</h3><p class="curriculum-cluster-meta">Read from top to bottom. A branching line means the later course depends on an earlier course.</p><div class="curriculum-graph-canvas" id="curriculumGraphCanvas"><svg class="curriculum-edge-layer" aria-hidden="true"></svg><div class="curriculum-levels">${mainLayers.map((layer, index) => `<div class="curriculum-level" aria-label="Dependency level ${index + 1}">${layer.map(id => nodes.has(id) ? nodeCard(nodes.get(id), graph) : '').join('')}</div>`).join('')}</div></div></section>`;
    attachInteractions(target);
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
