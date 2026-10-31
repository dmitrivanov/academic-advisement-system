(function () {
  const state = { programs: [], graph: null, completed: new Set() };
  const els = {
    program: document.getElementById('program-select'), tree: document.getElementById('degree-tree'),
    status: document.getElementById('tree-status'), title: document.getElementById('tree-title'),
    count: document.getElementById('completed-count'), progress: document.getElementById('progress-bar'),
    next: document.getElementById('next-courses'), plan: document.getElementById('semester-plan'),
    planTotal: document.getElementById('plan-total'), reset: document.getElementById('reset-progress')
  };

  const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const storageKey = code => `aas.cs-tree-v3.completed.${code}`;
  const unique = values => [...new Set(values)];

  function programIsInScope(program) {
    return program.institution_code === 'BMCC' && (
      program.department_code === 'CIS' || /computer (information|science)/i.test(program.department || '')
    ) && program.has_curriculum;
  }

  function requiredNodeIds(graph) {
    const ids = graph.clusters.filter(cluster => cluster.type === 'program_required').flatMap(cluster => cluster.node_ids || []);
    return unique(ids).filter(id => graph.nodes.some(node => node.id === id));
  }

  function electiveNodeIds(graph) {
    return unique(graph.clusters.filter(cluster => cluster.type === 'program_elective' || cluster.type === 'elective_choice')
      .flatMap(cluster => cluster.display_node_ids || cluster.node_ids || []));
  }

  function prerequisiteGroups(nodeId, graph = state.graph) {
    const groups = new Map();
    graph.edges.filter(edge => edge.target_id === nodeId && edge.relation_type === 'prerequisite').forEach(edge => {
      if (!groups.has(edge.group_id)) groups.set(edge.group_id, []);
      groups.get(edge.group_id).push(edge.source_id);
    });
    return [...groups.values()];
  }

  function prerequisiteSatisfied(nodeId, completedIds, graph = state.graph) {
    return prerequisiteGroups(nodeId, graph).every(group => group.some(id => completedIds.has(id)));
  }

  function corequisites(nodeId, graph = state.graph) {
    const ids = [];
    graph.edges.filter(edge => edge.relation_type === 'corequisite').forEach(edge => {
      if (edge.target_id === nodeId) ids.push(edge.source_id);
      if (edge.source_id === nodeId) ids.push(edge.target_id);
    });
    return unique(ids);
  }

  function downstreamCount(nodeId, graph = state.graph) {
    const reached = new Set(), queue = [nodeId];
    while (queue.length) {
      const current = queue.shift();
      graph.edges.filter(edge => edge.source_id === current && edge.relation_type === 'prerequisite').forEach(edge => {
        if (!reached.has(edge.target_id)) { reached.add(edge.target_id); queue.push(edge.target_id); }
      });
    }
    return reached.size;
  }

  function completedIds() {
    return new Set(state.graph.nodes.filter(node => state.completed.has(node.code)).map(node => node.id));
  }

  function nodeStatus(node, completed = completedIds()) {
    if (completed.has(node.id)) return 'completed';
    return prerequisiteSatisfied(node.id, completed) ? 'available' : 'locked';
  }

  function courseCard(node, elective = false) {
    const status = nodeStatus(node), unlocks = downstreamCount(node.id), coreq = corequisites(node.id)
      .map(id => state.graph.nodes.find(item => item.id === id)?.code).filter(Boolean);
    return `<button type="button" class="course-card ${status}" data-node-id="${node.id}" data-course-code="${escapeHtml(node.code)}" aria-pressed="${status === 'completed'}">
      <span class="course-code"><span>${escapeHtml(node.code)}</span><span class="check">${status === 'completed' ? '✓' : ''}</span></span>
      <span class="course-title">${escapeHtml(node.title)}</span>
      <span class="course-meta">${node.credits} credits${unlocks ? ` · <span class="unlocks">unlocks ${unlocks}</span>` : ''}${elective ? ' · elective option' : ''}</span>
      ${coreq.length ? `<span class="coreq-badge">Take with ${escapeHtml(coreq.join(' / '))}</span>` : ''}
    </button>`;
  }

  function stableStages(nodes) {
    const nodeIds = new Set(nodes.map(node => node.id));
    const memo = new Map();
    function depth(nodeId, trail = new Set()) {
      if (memo.has(nodeId)) return memo.get(nodeId);
      if (trail.has(nodeId)) return 0;
      const nextTrail = new Set(trail).add(nodeId);
      const parents = prerequisiteGroups(nodeId).flat().filter(id => nodeIds.has(id));
      const value = parents.length ? Math.max(...parents.map(id => depth(id, nextTrail))) + 1 : 0;
      memo.set(nodeId, value); return value;
    }
    const result = [[], [], [], []];
    nodes.forEach(node => result[Math.min(depth(node.id), 3)].push(node));
    result.forEach(stage => stage.sort((a, b) => a.code.localeCompare(b.code)));
    return result;
  }

  function renderTree() {
    const graph = state.graph, requiredIds = new Set(requiredNodeIds(graph)), electiveIds = new Set(electiveNodeIds(graph));
    const required = graph.nodes.filter(node => requiredIds.has(node.id) && !electiveIds.has(node.id));
    const electives = graph.nodes.filter(node => electiveIds.has(node.id) && !requiredIds.has(node.id));
    const stages = stableStages(required);
    const secondaryClusters = graph.clusters.filter(cluster => ['common_core','flexible_core'].includes(cluster.type));
    els.tree.innerHTML = `<div class="tree-stage-labels">${['Foundation','Gateway courses','Advanced sequence','Degree completion'].map(label => `<div class="tree-stage-label">${label}</div>`).join('')}</div>
      <div id="tree-grid" class="tree-grid"><svg class="tree-connectors" aria-hidden="true"></svg>${stages.map(stage => `<div class="tree-stage">${stage.map(node => courseCard(node)).join('') || '<div class="empty-copy">No courses in this stage.</div>'}</div>`).join('')}</div>
      ${electives.length ? `<section class="elective-orbit"><div class="elective-orbit-header"><div><h3>Program elective pathways</h3><p>Visible as part of the main tree—select completed electives here.</p></div><span class="eyebrow">Choose approved options</span></div><div class="elective-courses">${electives.map(node => courseCard(node, true)).join('')}</div></section>` : ''}
      ${secondaryClusters.length ? `<section class="requirement-ribbon"><strong>General education branches</strong><div class="requirement-pills">${secondaryClusters.map(cluster => `<span>${escapeHtml(cluster.name)} · ${cluster.required_credits || cluster.required_course_count || ''}${cluster.required_credits ? ' credits' : cluster.required_course_count ? ' courses' : ''}</span>`).join('')}</div></section>` : ''}`;
    els.tree.hidden = false; els.status.hidden = true;
    els.tree.querySelectorAll('[data-course-code]').forEach(card => card.addEventListener('click', () => toggleCourse(card.dataset.courseCode)));
    updatePlanning();
    requestAnimationFrame(drawConnectors);
  }

  function drawConnectors() {
    const grid = document.getElementById('tree-grid'), svg = grid?.querySelector('.tree-connectors');
    if (!grid || !svg || !state.graph) return;
    const bounds = grid.getBoundingClientRect();
    svg.setAttribute('viewBox', `0 0 ${bounds.width} ${bounds.height}`);
    svg.innerHTML = '<defs><marker id="v3-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10Z" fill="context-stroke"/></marker></defs>';
    state.graph.edges.filter(edge => edge.relation_type === 'prerequisite' || edge.relation_type === 'corequisite').forEach(edge => {
      const source = grid.querySelector(`[data-node-id="${edge.source_id}"]`), target = grid.querySelector(`[data-node-id="${edge.target_id}"]`);
      if (!source || !target) return;
      const a = source.getBoundingClientRect(), b = target.getBoundingClientRect();
      const x1 = a.right - bounds.left, y1 = a.top + a.height / 2 - bounds.top;
      const x2 = b.left - bounds.left, y2 = b.top + b.height / 2 - bounds.top;
      if (x2 <= x1) return;
      const middle = x1 + (x2 - x1) / 2;
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', `M${x1} ${y1} C${middle} ${y1},${middle} ${y2},${x2} ${y2}`);
      path.setAttribute('marker-end', 'url(#v3-arrow)');
      path.classList.add(edge.relation_type === 'corequisite' ? 'corequisite-link' : 'prerequisite-link');
      svg.appendChild(path);
    });
  }

  function toggleCourse(code) {
    state.completed.has(code) ? state.completed.delete(code) : state.completed.add(code);
    localStorage.setItem(storageKey(state.graph.program.code), JSON.stringify([...state.completed]));
    renderTree();
  }

  function priorityAvailable(nodes, completed) {
    return nodes.filter(node => !completed.has(node.id) && prerequisiteSatisfied(node.id, completed))
      .sort((a, b) => downstreamCount(b.id) - downstreamCount(a.id) || a.code.localeCompare(b.code));
  }

  function deterministicPlan(nodes, initiallyCompleted) {
    const remaining = new Map(nodes.filter(node => !initiallyCompleted.has(node.id)).map(node => [node.id, node]));
    const completed = new Set(initiallyCompleted), semesters = [];
    for (let term = 0; term < 8 && remaining.size; term += 1) {
      const eligible = priorityAvailable([...remaining.values()], completed);
      const selected = [], selectedIds = new Set(); let credits = 0;
      for (const node of eligible) {
        if (selectedIds.has(node.id)) continue;
        const bundle = [node, ...corequisites(node.id).map(id => remaining.get(id)).filter(Boolean)];
        const bundleCredits = bundle.reduce((sum, item) => sum + Number(item.credits || 0), 0);
        if (selected.length && credits + bundleCredits > 17) continue;
        if (!bundle.every(item => prerequisiteSatisfied(item.id, completed))) continue;
        bundle.forEach(item => { if (!selectedIds.has(item.id)) { selected.push(item); selectedIds.add(item.id); credits += Number(item.credits || 0); } });
        if (credits >= 14) break;
      }
      if (!selected.length) break;
      semesters.push({ courses: selected, credits });
      selected.forEach(node => { completed.add(node.id); remaining.delete(node.id); });
    }
    return { semesters, unresolved: [...remaining.values()] };
  }

  function updatePlanning() {
    const graph = state.graph, completed = completedIds();
    const requiredSet = new Set(requiredNodeIds(graph));
    const required = graph.nodes.filter(node => requiredSet.has(node.id));
    const available = priorityAvailable(required, completed).slice(0, 5);
    els.next.innerHTML = available.length ? available.map((node, index) => `<div class="recommendation"><span class="rank">${index + 1}</span><span><strong>${escapeHtml(node.code)}</strong><small>${escapeHtml(node.title)}</small></span><em>${downstreamCount(node.id)} unlocks</em></div>`).join('') : '<div class="empty-copy">No additional required course is currently available. Check prerequisite or elective choices.</div>';
    const plan = deterministicPlan(required, completed);
    els.plan.innerHTML = plan.semesters.length ? plan.semesters.map((semester, index) => `<section class="semester"><header><span>Semester ${index + 1}</span><span>${semester.credits} credits</span></header><ul>${semester.courses.map(node => `<li><strong>${escapeHtml(node.code)}</strong><span>${escapeHtml(node.title)}</span></li>`).join('')}</ul></section>`).join('') : '<div class="empty-copy">Select a program to create the remaining pathway.</div>';
    const totalCredits = plan.semesters.reduce((sum, semester) => sum + semester.credits, 0);
    els.planTotal.textContent = `${plan.semesters.length} terms · ${totalCredits} credits`;
    if (plan.unresolved.length) els.plan.insertAdjacentHTML('beforeend', `<div class="empty-copy">${plan.unresolved.length} course${plan.unresolved.length === 1 ? '' : 's'} need an elective or prerequisite decision before placement.</div>`);
    const relevantCount = required.length;
    const completedRelevant = required.filter(node => completed.has(node.id)).length;
    els.count.textContent = state.completed.size;
    els.progress.style.width = `${relevantCount ? Math.min(100, completedRelevant / relevantCount * 100) : 0}%`;
  }

  async function loadProgram(code) {
    els.tree.hidden = true; els.status.hidden = false; els.status.className = 'status-message'; els.status.textContent = 'Loading the canonical curriculum…';
    try {
      const response = await fetch(`/api/db/programs/${encodeURIComponent(code)}/graph`);
      if (!response.ok) throw new Error((await response.json().catch(() => ({}))).detail || 'The degree tree could not be loaded.');
      state.graph = await response.json();
      try { state.completed = new Set(JSON.parse(localStorage.getItem(storageKey(code)) || '[]')); } catch (_) { state.completed = new Set(); }
      els.title.textContent = `${state.graph.program.name} (${state.graph.program.degree_type}) · ${state.graph.program.catalog_year}`;
      renderTree();
    } catch (error) { els.status.className = 'status-message error'; els.status.textContent = error.message; }
  }

  async function init() {
    try {
      const response = await fetch('/api/db/programs?selector_only=true');
      if (!response.ok) throw new Error('Programs could not be loaded.');
      state.programs = (await response.json()).filter(programIsInScope);
      if (!state.programs.length) throw new Error('No BMCC CS-department curricula are available.');
      els.program.innerHTML = state.programs.map(program => `<option value="${escapeHtml(program.code)}">${escapeHtml(program.name)} (${escapeHtml(program.degree_type)})</option>`).join('');
      const preferred = state.programs.find(program => program.code === 'CS') || state.programs[0];
      els.program.value = preferred.code; await loadProgram(preferred.code);
    } catch (error) { els.status.className = 'status-message error'; els.status.textContent = error.message; }
  }

  els.program.addEventListener('change', () => loadProgram(els.program.value));
  els.reset.addEventListener('click', () => { if (!state.graph) return; state.completed.clear(); localStorage.removeItem(storageKey(state.graph.program.code)); renderTree(); });
  window.addEventListener('resize', () => requestAnimationFrame(drawConnectors));
  init();
})();
