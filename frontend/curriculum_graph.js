(function () {
  const state = { graph: null, completed: new Set(), lastFocus: null, highlightedNodeId: null, resizeObserver: null, drawTimer: null, onGroupOpen: null };

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
    modal.innerHTML = `<div class="curriculum-graph-backdrop" data-graph-close></div><section class="curriculum-graph-dialog" role="dialog" aria-modal="true" aria-labelledby="curriculumGraphTitle"><header class="curriculum-graph-toolbar"><div><h2 id="curriculumGraphTitle">Course dependency map</h2><p id="curriculumGraphSubtitle">Loading curriculum relationships…</p></div><div class="curriculum-graph-actions"><button class="curriculum-graph-print" type="button">Download / save PDF</button><button class="curriculum-graph-close" type="button" data-graph-close>Close</button></div></header><div id="curriculumGraphContent" class="curriculum-graph-scroll"></div></section>`;
    document.body.appendChild(modal);
    modal.querySelectorAll('[data-graph-close]').forEach(item => item.addEventListener('click', close));
    modal.querySelector('.curriculum-graph-print').addEventListener('click', printGraph);
    modal.addEventListener('keydown', event => { if (event.key === 'Escape') close(); });
    return modal;
  }

  function relationshipSummary(node, graph) {
    const nodeById = new Map(graph.nodes.map(item => [item.id, item]));
    const incomingGroups = new Map();
    graph.edges.filter(edge => edge.target_id === node.id).forEach(edge => {
      const key = `${edge.relation_type}-${edge.group_id}`;
      if (!incomingGroups.has(key)) incomingGroups.set(key, []);
      const code = nodeById.get(edge.source_id)?.code;
      if (code) incomingGroups.get(key).push(code);
    });
    const incoming = [...incomingGroups.values()].map(codes => codes.join(' or '));
    const outgoing = graph.edges.filter(edge => edge.source_id === node.id).map(edge => nodeById.get(edge.target_id)?.code).filter(Boolean);
    return { incoming, outgoing };
  }

  function nodeCard(node, graph, isMainNode = false) {
    const completed = state.completed.has(node.code) ? ' completed' : '';
    const relationships = relationshipSummary(node, graph);
    const prerequisites = relationships.incoming.length ? relationships.incoming.join(' and ') : 'None shown';
    const unlocks = relationships.outgoing.length ? relationships.outgoing.join(', ') : 'No later course shown';
    return `<button type="button" class="curriculum-node${completed}" data-node-id="${node.id}"${isMainNode ? ` data-main-node-id="${node.id}"` : ''} aria-expanded="false"><span class="node-topline"><span class="code">${escapeHtml(node.code)}</span><span class="node-expand" aria-hidden="true">+</span></span><span class="node-details"><span class="title">${escapeHtml(node.title)}</span><span class="credits">${node.credits} credit${node.credits === 1 ? '' : 's'}</span><span class="relationship"><strong>Needs:</strong> ${escapeHtml(prerequisites)}</span><span class="relationship"><strong>Unlocks:</strong> ${escapeHtml(unlocks)}</span></span></button>`;
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
    const startOpen = hasSequence && cluster.node_ids.length <= 5;
    return `<details class="curriculum-group-tree ${escapeHtml(cluster.type)}" data-cluster-id="${escapeHtml(cluster.id)}"${startOpen ? ' open' : ''}><summary class="curriculum-group-card"><span><strong>${escapeHtml(cluster.name)}</strong><small>${escapeHtml(clusterRequirement(cluster))}${hasSequence ? ' · sequence' : ''}</small></span><span class="cluster-chevron" aria-hidden="true">+</span></summary><div class="curriculum-mini-branch">${layers.map((layer, index) => `${index ? '<div class="mini-branch-arrow" aria-hidden="true">↓</div>' : ''}<div class="curriculum-mini-level" aria-label="${escapeHtml(cluster.name)} level ${index + 1}">${layer.map(id => nodes.has(id) ? nodeCard(nodes.get(id), graph) : '').join('')}</div>`).join('')}</div></details>`;
  }

  function downstreamPath(nodeId) {
    const edges = state.graph?.edges || [];
    const reached = new Set([Number(nodeId)]), highlightedEdges = new Set();
    const queue = [Number(nodeId)];
    while (queue.length) {
      const source = queue.shift();
      edges.forEach(edge => {
        if (edge.source_id !== source || edge.relation_type === 'corequisite') return;
        highlightedEdges.add(`${edge.source_id}-${edge.target_id}-${edge.relation_type}-${edge.group_id}`);
        if (!reached.has(edge.target_id)) {
          reached.add(edge.target_id);
          queue.push(edge.target_id);
        }
      });
    }
    return { reached, highlightedEdges };
  }

  function applyHighlight(target) {
    target.querySelectorAll('.curriculum-node.path-source, .curriculum-node.path-destination').forEach(card => card.classList.remove('path-source', 'path-destination'));
    if (state.highlightedNodeId == null) return;
    const path = downstreamPath(state.highlightedNodeId);
    target.querySelectorAll(`[data-node-id="${state.highlightedNodeId}"]`).forEach(card => card.classList.add('path-source'));
    path.reached.forEach(nodeId => {
      if (nodeId === Number(state.highlightedNodeId)) return;
      target.querySelectorAll(`[data-node-id="${nodeId}"]`).forEach(card => card.classList.add('path-destination'));
    });
  }

  function scheduleDrawEdges() {
    cancelAnimationFrame(state.drawFrame);
    clearTimeout(state.drawTimer);
    state.drawFrame = requestAnimationFrame(drawEdges);
    state.drawTimer = setTimeout(() => requestAnimationFrame(drawEdges), 180);
  }

  function attachInteractions(target) {
    if (target.dataset.graphInteractionsAttached) return;
    target.dataset.graphInteractionsAttached = 'true';
    target.addEventListener('click', event => {
      const groupCard = event.target.closest('.curriculum-group-card');
      if (groupCard && state.onGroupOpen) {
        const clusterId = groupCard.closest('.curriculum-group-tree')?.dataset.clusterId;
        const cluster = state.graph?.clusters.find(item => item.id === clusterId);
        if (cluster?.choice_group_code) {
          event.preventDefault();
          state.onGroupOpen(cluster);
          return;
        }
      }
      const card = event.target.closest('.curriculum-node');
      if (!card || !target.contains(card)) return;
      const expanded = card.getAttribute('aria-expanded') === 'true';
      card.setAttribute('aria-expanded', String(!expanded));
      card.classList.toggle('expanded', !expanded);
      card.querySelector('.node-expand').textContent = expanded ? '+' : '−';
      state.highlightedNodeId = Number(card.dataset.nodeId);
      applyHighlight(target);
      scheduleDrawEdges();
    });
    target.addEventListener('toggle', scheduleDrawEdges, true);
  }

  function render(graph, target) {
    state.graph = graph;
    const nodes = new Map(graph.nodes.map(node => [node.id, node]));
    const mainClusterTypes = new Set(['program_required']);
    const mainIds = new Set(graph.clusters.filter(cluster => mainClusterTypes.has(cluster.type)).flatMap(cluster => cluster.node_ids));
    const preferredRoots = new Set((graph.preferred_root_course_codes || []).map(code => graph.nodes.find(node => node.code === code)?.id).filter(Boolean));
    // Required-course ancestors may live in Common/Flexible Core or in the
    // support bucket. Pull only ancestors that actually unlock a required node.
    let changed = true;
    while (changed) {
      changed = false;
      graph.edges.forEach(edge => {
        if (edge.relation_type === 'prerequisite' && mainIds.has(edge.target_id) && !preferredRoots.has(edge.target_id) && !mainIds.has(edge.source_id)) {
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
    target.innerHTML = `<div class="curriculum-graph-legend"><span>Prerequisite</span><span class="coreq">Corequisite</span><span class="recommended">Recommended sequence</span><span class="highlighted">Selected pathway</span><em>Click a course to expand it and highlight everything it unlocks</em></div>${graph.cycle_node_ids.length ? '<p class="curriculum-cycle-warning">This graph contains a circular relationship. An administrator should review the highlighted curriculum data.</p>' : ''}<section class="curriculum-tree-panel"><h3>Course dependency forest</h3><p class="curriculum-cluster-meta">Course groups begin beside the first classes as independent trees. Short sequences start open; click a group card to fold or unfold it.</p><div class="curriculum-graph-canvas" id="curriculumGraphCanvas"><svg class="curriculum-edge-layer" aria-hidden="true"></svg><div class="curriculum-levels">${mainLayers.map((layer, index) => `<div class="curriculum-level${index === 0 ? ' curriculum-root-level' : ''}" aria-label="Dependency level ${index + 1}">${index === 0 ? secondary.map(cluster => clusterBranch(cluster, nodes, graph)).join('') : ''}${layer.map(id => nodes.has(id) ? nodeCard(nodes.get(id), graph, true) : '').join('')}</div>`).join('')}</div></div></section>`;
    attachInteractions(target);
    state.highlightedNodeId = null;
    if (state.resizeObserver) state.resizeObserver.disconnect();
    const canvas = target.querySelector('#curriculumGraphCanvas');
    if (canvas && window.ResizeObserver) {
      state.resizeObserver = new ResizeObserver(scheduleDrawEdges);
      state.resizeObserver.observe(canvas);
      canvas.querySelectorAll('.curriculum-node, .curriculum-group-tree').forEach(item => state.resizeObserver.observe(item));
    }
    scheduleDrawEdges();
  }

  function drawEdges() {
    const canvas = document.getElementById('curriculumGraphCanvas');
    if (!canvas || !state.graph) return;
    const svg = canvas.querySelector('svg');
    const bounds = canvas.getBoundingClientRect();
    svg.setAttribute('viewBox', `0 0 ${bounds.width} ${bounds.height}`);
    svg.innerHTML = '';
    const highlightedEdgeKeys = state.highlightedNodeId == null ? new Set() : downstreamPath(state.highlightedNodeId).highlightedEdges;
    state.graph.edges.forEach(edge => {
      const source = canvas.querySelector(`[data-main-node-id="${edge.source_id}"]`);
      const target = canvas.querySelector(`[data-main-node-id="${edge.target_id}"]`);
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
      path.dataset.edgeKey = `${edge.source_id}-${edge.target_id}-${edge.relation_type}-${edge.group_id}`;
      const highlighted = highlightedEdgeKeys.has(path.dataset.edgeKey);
      if (highlighted) {
        path.setAttribute('stroke', '#16a34a');
        path.setAttribute('stroke-width', '5');
        path.classList.add('path-highlight');
      }
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
    state.onGroupOpen = typeof options.onGroupOpen === 'function' ? options.onGroupOpen : null;
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

  function printGraph() {
    document.body.classList.add('curriculum-graph-printing');
    const cleanup = () => document.body.classList.remove('curriculum-graph-printing');
    window.addEventListener('afterprint', cleanup, { once: true });
    window.print();
    setTimeout(cleanup, 1500);
  }

  window.addEventListener('resize', drawEdges);
  window.CurriculumGraph = { open, close, load, render, isSupported: code => Boolean(code), printGraph };
})();
