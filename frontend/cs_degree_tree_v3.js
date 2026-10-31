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
  const CS_MAP_CODES = ['CSC 101','CSC 111','CSC 211','CSC 215','CSC 231','CSC 331','CSC 350','MAT 206','MAT 301','MAT 302','PHY 215'];
  const CS_COMMUNICATION_CODES = ['ENG 101','ENG 201'];
  const CS_ELECTIVE_TRACKS = [
    { name: 'Mobile device programming', accent: 'mobile', codes: ['CIS 272','CIS 285','CIS 364','CIS 385'] },
    { name: 'Data analytics', accent: 'data', codes: ['CSC 103','CSC 203','CIS 317','CIS 395'] },
    { name: 'Cybersecurity', accent: 'cyber', codes: ['CIS 316','CIS 345','CIS 359','CIS 362'] }
  ];

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
    if (state.completed.has(node.code) || completed.has(node.id)) return 'completed';
    return prerequisiteSatisfied(node.id, completed) ? 'available' : 'locked';
  }

  function courseCard(node, elective = false) {
    const status = nodeStatus(node), unlocks = downstreamCount(node.id), coreq = corequisites(node.id)
      .map(id => state.graph.nodes.find(item => item.id === id)?.code).filter(Boolean);
    const prerequisiteCodes = prerequisiteGroups(node.id).map(group => group
      .map(id => state.graph.nodes.find(item => item.id === id)?.code).filter(Boolean).join(' or ')).filter(Boolean);
    const unlockedCodes = state.graph.edges.filter(edge => edge.source_id === node.id && edge.relation_type === 'prerequisite')
      .map(edge => state.graph.nodes.find(item => item.id === edge.target_id)?.code).filter(Boolean);
    const detailsId = `course-details-${String(node.code).replace(/[^a-z0-9]+/gi, '-').toLowerCase()}`;
    return `<article class="course-card ${status}" data-node-id="${node.id}" data-course-code="${escapeHtml(node.code)}">
      <button type="button" class="course-select" aria-pressed="${status === 'completed'}" aria-label="${status === 'completed' ? 'Remove' : 'Mark'} ${escapeHtml(node.code)} as completed">
        <span class="course-code"><span>${escapeHtml(node.code)}</span><span class="check">${status === 'completed' ? '✓' : ''}</span></span>
        <span class="course-title">${escapeHtml(node.title)}</span>
      </button>
      <button type="button" class="course-details-toggle" aria-expanded="false" aria-controls="${detailsId}">Class details</button>
      <span id="${detailsId}" class="course-details-panel">
        <span><strong>Credits:</strong> ${Number(node.credits || 0)}</span>
        <span><strong>Prerequisites:</strong> ${escapeHtml(prerequisiteCodes.join(' and ') || 'None shown')}</span>
        <span><strong>Unlocks:</strong> ${escapeHtml(unique(unlockedCodes).join(', ') || 'No later course shown')}</span>
        ${coreq.length ? `<span><strong>Co-requisite:</strong> ${escapeHtml(coreq.join(' / '))}</span>` : ''}
        ${elective ? '<span><strong>Requirement:</strong> Program elective option</span>' : ''}
      </span>
    </article>`;
  }

  function attachCourseInteractions() {
    els.tree.querySelectorAll('.course-select').forEach(button => button.addEventListener('click', () => {
      toggleCourse(button.closest('[data-course-code]').dataset.courseCode);
    }));
    els.tree.querySelectorAll('.course-details-toggle').forEach(button => button.addEventListener('click', () => {
      const card = button.closest('.course-card'), panel = document.getElementById(button.getAttribute('aria-controls'));
      const expanded = button.getAttribute('aria-expanded') === 'true';
      els.tree.querySelectorAll('.course-card.details-open').forEach(openCard => {
        if (openCard === card) return;
        openCard.classList.remove('details-open');
        openCard.querySelector('.course-details-toggle')?.setAttribute('aria-expanded', 'false');
        openCard.querySelector('.course-details-panel')?.classList.remove('open');
      });
      button.setAttribute('aria-expanded', String(!expanded));
      card.classList.toggle('details-open', !expanded);
      panel.classList.toggle('open', !expanded);
    }));
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
    if (state.graph.program.code === 'CS') {
      renderComputerScienceTree();
      return;
    }
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
    attachCourseInteractions();
    updatePlanning();
    requestAnimationFrame(drawConnectors);
  }

  function nodeByCode(code) {
    return state.graph.nodes.find(node => node.code === code);
  }

  function speechNode(code) {
    return {
      id: `speech-${code.replace(/\s/g, '-').toLowerCase()}`,
      code,
      title: code === 'SPE 100' ? 'Fundamentals of Public Speaking' : 'Public Speaking for Non-Native Speakers',
      credits: 3,
      synthetic: true
    };
  }

  function renderComputerScienceTree() {
    const mapNodes = CS_MAP_CODES.map(nodeByCode).filter(Boolean);
    const communication = CS_COMMUNICATION_CODES.map(nodeByCode).filter(Boolean);
    const speech = [speechNode('SPE 100'), speechNode('SPE 102')];
    const positions = {
      'CSC 101':'csc101','CSC 111':'csc111','CSC 211':'csc211','CSC 215':'csc215',
      'CSC 231':'csc231','CSC 331':'csc331','CSC 350':'csc350','MAT 206':'mat206',
      'MAT 301':'mat301','MAT 302':'mat302','PHY 215':'phy215'
    };
    const fixedEdges = [
      ['CSC 101','CSC 111','prerequisite'],['MAT 206','CSC 111','prerequisite'],['MAT 206','MAT 301','prerequisite'],
      ['CSC 111','CSC 211','prerequisite'],['CSC 111','CSC 215','prerequisite'],['CSC 111','CSC 231','prerequisite'],
      ['MAT 301','CSC 231','prerequisite'],['MAT 301','PHY 215','prerequisite'],['MAT 301','MAT 302','prerequisite'],
      ['CSC 211','CSC 331','prerequisite'],['CSC 211','CSC 350','prerequisite'],['CSC 231','CSC 331','prerequisite'],
      ['MAT 302','PHY 215','corequisite']
    ];
    els.tree.innerHTML = `<section class="fixed-map-section"><div class="map-section-heading"><div><span class="eyebrow">Professor-reviewed primary sequence</span><h3>CSC curriculum map</h3></div><p>Arrows show prerequisites. The dashed purple connection marks a co-requisite.</p></div>
      <div id="cs-fixed-map" class="cs-fixed-map"><svg class="tree-connectors" aria-hidden="true"></svg>${mapNodes.map(node => `<div class="fixed-node ${positions[node.code]}">${courseCard(node)}</div>`).join('')}</div></section>
      <section class="support-branches"><div class="communication-branch"><div class="track-heading"><span class="track-icon">Aa</span><div><h3>Communication sequence</h3><p>Complete composition in order and choose one speech course.</p></div></div><div id="communication-map" class="communication-map"><svg class="tree-connectors" aria-hidden="true"></svg><div>${communication[0] ? courseCard(communication[0]) : ''}</div><span class="branch-arrow">→</span><div>${communication[1] ? courseCard(communication[1]) : ''}</div><span class="branch-divider">and</span><div class="alternative-stack"><span class="alternative-label">Choose one</span>${speech.map(node => courseCard(node)).join('')}</div></div></div></section>
      <section class="elective-tracks"><div class="elective-orbit-header"><div><h3>Program elective tracks</h3><p>Twelve approved options grouped into three coherent pathways. The degree requires 6 program-elective credits.</p></div><span class="eyebrow">4 courses per track</span></div><div class="track-grid">${CS_ELECTIVE_TRACKS.map(track => `<article class="elective-track ${track.accent}"><div class="track-heading"><span class="track-icon">${track.accent === 'mobile' ? '▣' : track.accent === 'data' ? '⌁' : '◆'}</span><div><h4>${escapeHtml(track.name)}</h4><p>${track.codes.length} approved courses</p></div></div><div class="track-courses">${track.codes.map(nodeByCode).filter(Boolean).map(node => courseCard(node, true)).join('')}</div></article>`).join('')}</div></section>`;
    els.tree.hidden = false; els.status.hidden = true;
    attachCourseInteractions();
    updatePlanning();
    requestAnimationFrame(() => {
      drawFixedConnectors('cs-fixed-map', fixedEdges);
      drawFixedConnectors('communication-map', [['ENG 101','ENG 201','prerequisite']]);
    });
  }

  function drawFixedConnectors(containerId, edgeSpecs) {
    const container = document.getElementById(containerId), svg = container?.querySelector('.tree-connectors');
    if (!container || !svg) return;
    const bounds = container.getBoundingClientRect();
    svg.setAttribute('viewBox', `0 0 ${bounds.width} ${bounds.height}`);
    svg.innerHTML = '<defs><marker id="fixed-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10Z" fill="context-stroke"/></marker></defs>';
    edgeSpecs.forEach(([sourceCode, targetCode, type]) => {
      const source = container.querySelector(`[data-course-code="${sourceCode}"]`), target = container.querySelector(`[data-course-code="${targetCode}"]`);
      if (!source || !target) return;
      const a = source.getBoundingClientRect(), b = target.getBoundingClientRect();
      const dx = (b.left + b.width / 2) - (a.left + a.width / 2), dy = (b.top + b.height / 2) - (a.top + a.height / 2);
      let x1, y1, x2, y2;
      if (Math.abs(dy) >= Math.abs(dx)) {
        x1 = a.left + a.width / 2 - bounds.left; y1 = (dy >= 0 ? a.bottom : a.top) - bounds.top;
        x2 = b.left + b.width / 2 - bounds.left; y2 = (dy >= 0 ? b.top : b.bottom) - bounds.top;
      } else {
        x1 = (dx >= 0 ? a.right : a.left) - bounds.left; y1 = a.top + a.height / 2 - bounds.top;
        x2 = (dx >= 0 ? b.left : b.right) - bounds.left; y2 = b.top + b.height / 2 - bounds.top;
      }
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      const curveX = x1 + (x2 - x1) / 2, curveY = y1 + (y2 - y1) / 2;
      path.setAttribute('d', Math.abs(dy) >= Math.abs(dx) ? `M${x1} ${y1} C${x1} ${curveY},${x2} ${curveY},${x2} ${y2}` : `M${x1} ${y1} C${curveX} ${y1},${curveX} ${y2},${x2} ${y2}`);
      path.setAttribute('marker-end', 'url(#fixed-arrow)');
      path.classList.add(type === 'corequisite' ? 'corequisite-link' : 'prerequisite-link');
      svg.appendChild(path);
    });
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
    if (graph.program.code === 'CS') {
      [...CS_MAP_CODES, ...CS_COMMUNICATION_CODES].map(nodeByCode).filter(Boolean).forEach(node => requiredSet.add(node.id));
    }
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
  window.addEventListener('resize', () => requestAnimationFrame(() => {
    if (state.graph?.program.code === 'CS') {
      renderComputerScienceTree();
    } else {
      drawConnectors();
    }
  }));
  init();
})();
