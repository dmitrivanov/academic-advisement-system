(function () {
  'use strict';

  const STORAGE_KEY = 'cunyBeyondAnonymousDraftV1';
  const MAX_SKILLS = 5;
  const SKILLS = [
    'Analyzing data', 'Communicating ideas', 'Solving technical problems',
    'Helping people', 'Organizing projects', 'Working with numbers',
    'Writing and storytelling', 'Designing experiences', 'Leading teams',
    'Researching questions', 'Building or repairing things', 'Learning languages'
  ];
  const PROFILE_LABELS = {
    high_school: 'High-school student', working_adult: 'Working adult',
    some_college: 'Adult with some college', transfer: 'Transfer student',
    returning: 'Returning student', degree_holder: 'Adult with a degree'
  };
  const state = { step: 0, profile: '', careerGoal: '', employment: '', skills: [], cplSelections: [], expiresAt: 0 };
  const form = document.getElementById('intake-form');
  const steps = Array.from(document.querySelectorAll('.step'));
  const nextButton = document.getElementById('next-button');
  const backButton = document.getElementById('back-button');
  const errorBox = document.getElementById('form-error');
  let ttlHours = 24;
  let latestRecommendations = [];
  let supportedCareers = [];

  function selectedValue(name) {
    const selected = form.querySelector(`input[name="${name}"]:checked`);
    return selected ? selected.value : '';
  }

  function loadDraft() {
    try {
      const draft = JSON.parse(localStorage.getItem(STORAGE_KEY));
      if (!draft || !draft.expiresAt || Date.now() >= draft.expiresAt) {
        localStorage.removeItem(STORAGE_KEY);
        return;
      }
      Object.assign(state, draft);
      state.step = Math.min(Math.max(Number(state.step) || 0, 0), steps.length - 1);
      state.skills = Array.isArray(state.skills) ? state.skills.slice(0, MAX_SKILLS) : [];
      state.cplSelections = Array.isArray(state.cplSelections) ? state.cplSelections.slice(0, 9) : [];
      document.getElementById('save-status').textContent = 'Your saved draft was restored on this device.';
    } catch (_) { localStorage.removeItem(STORAGE_KEY); }
  }

  function saveDraft() {
    state.expiresAt = Date.now() + ttlHours * 60 * 60 * 1000;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    document.getElementById('save-status').textContent = `Draft saved in this browser for ${ttlHours} hour${ttlHours === 1 ? '' : 's'}.`;
  }

  function renderSkills() {
    const fieldset = document.getElementById('skill-choices');
    fieldset.innerHTML = SKILLS.map(skill => `<label><input type="checkbox" name="skills" value="${skill}"><span>${skill}</span></label>`).join('');
  }

  function restoreInputs() {
    ['profile', 'employment'].forEach(name => {
      const value = state[name];
      if (value) {
        const input = form.querySelector(`input[name="${name}"][value="${value}"]`);
        if (input) input.checked = true;
      }
    });
    document.getElementById('career-goal').value = state.careerGoal || '';
    state.skills.forEach(skill => {
      const input = Array.from(form.querySelectorAll('input[name="skills"]')).find(item => item.value === skill);
      if (input) input.checked = true;
    });
    state.cplSelections.forEach(code => {
      const input = form.querySelector(`input[name="cpl"][value="${code}"]`);
      if (input) input.checked = true;
    });
    updateCounts();
  }

  function updateCounts() {
    document.getElementById('goal-count').textContent = document.getElementById('career-goal').value.length;
    const count = form.querySelectorAll('input[name="skills"]:checked').length;
    document.getElementById('skill-count').textContent = `${count} of ${MAX_SKILLS} selected`;
    form.querySelectorAll('input[name="skills"]:not(:checked)').forEach(input => { input.disabled = count >= MAX_SKILLS; });
  }

  function validateStep() {
    if (state.step === 0 && !selectedValue('profile')) return 'Choose the path that best describes you.';
    if (state.step === 1 && document.getElementById('career-goal').value.trim().length < 2) return 'Enter a short career or life goal.';
    if (state.step === 2 && !selectedValue('employment')) return 'Choose an employment answer.';
    if (state.step === 3 && form.querySelectorAll('input[name="skills"]:checked').length === 0) return 'Choose at least one skill.';
    if (state.step === 4 && form.querySelectorAll('input[name="cpl"]:checked').length === 0) return 'Choose at least one answer, Not sure, or None of these.';
    return '';
  }

  function captureState() {
    state.profile = selectedValue('profile') || state.profile;
    state.careerGoal = document.getElementById('career-goal').value.trim();
    state.employment = selectedValue('employment') || state.employment;
    state.skills = Array.from(form.querySelectorAll('input[name="skills"]:checked')).map(input => input.value).slice(0, MAX_SKILLS);
    state.cplSelections = Array.from(form.querySelectorAll('input[name="cpl"]:checked')).map(input => input.value).slice(0, 9);
  }

  function renderSummary() {
    const employment = state.employment === 'yes' ? 'Currently working' : state.employment === 'no' ? 'Not currently working' : 'Prefer not to say';
    document.getElementById('summary').innerHTML = `
      <div class="summary-row"><strong>Your path</strong>${PROFILE_LABELS[state.profile] || 'Not provided'}</div>
      <div class="summary-row"><strong>Your goal</strong>${escapeHtml(state.careerGoal)}</div>
      <div class="summary-row"><strong>Employment</strong>${employment}</div>
      <div class="summary-row"><strong>Skills</strong>${state.skills.map(escapeHtml).join(', ')}</div>
      <div class="summary-row"><strong>Prior-learning screen</strong>${state.cplSelections.includes('none') ? 'None selected' : `${state.cplSelections.length} possible path${state.cplSelections.length === 1 ? '' : 's'} to review`}</div>`;
  }

  function escapeHtml(value) {
    const node = document.createElement('span');
    node.textContent = value || '';
    return node.innerHTML;
  }

  function safeUrl(value) {
    try {
      const parsed = new URL(value, window.location.origin);
      return ['http:', 'https:'].includes(parsed.protocol) ? parsed.href : '#';
    } catch (_) { return '#'; }
  }

  function openDegreePlanner(index) {
    const result = latestRecommendations[index];
    if (!result) return;
    sessionStorage.setItem('selectedProgramContext', JSON.stringify({
      institutionCode: result.institution_code,
      institutionName: result.institution_name,
      programCode: result.program_code,
      programName: result.program_name,
      catalogYear: result.catalog_year || '',
      selectedAt: new Date().toISOString(),
      source: 'cuny-beyond'
    }));
    window.location.href = '/db-progress';
  }

  function renderRecommendations(data) {
    const container = document.getElementById('recommendation-results');
    latestRecommendations = data.recommendations || [];
    if (!latestRecommendations.length) {
      const choices = (data.supported_careers || supportedCareers.slice(0, 8).map(item => item.name));
      container.innerHTML = `<div class="next-stage"><strong>No reviewed match yet</strong><p>${escapeHtml(data.message || 'Choose a supported career title or speak with an advisor.')}</p><div class="career-suggestions">${choices.map(name => `<button class="career-chip" type="button" data-retry-career="${escapeHtml(name)}">${escapeHtml(name)}</button>`).join('')}</div></div>`;
      return;
    }
    const careerName = data.matched_career ? data.matched_career.name : state.careerGoal;
    container.innerHTML = `<h3>Top starting points for ${escapeHtml(careerName)}</h3>` + latestRecommendations.map((item, index) => {
      const tags = [item.advising_label, item.evidence_level + ' evidence', ...item.matched_skills].map(tag => `<span class="match-tag">${escapeHtml(tag)}</span>`).join('');
      return `<article class="recommendation-card">
        <div class="recommendation-heading"><div><h3>${escapeHtml(item.program_name)} (${escapeHtml(item.degree_type || 'Degree')})</h3><p>${escapeHtml(item.department_name)} · ${escapeHtml(item.catalog_year || 'Current catalog')}</p></div><span class="match-score">${item.score} fit points</span></div>
        <p class="match-explanation">${escapeHtml(item.explanation)}</p>
        <div class="match-details">${tags}</div>
        <p class="source-note">Career evidence: ${item.score_components.career} points; selected-skill evidence: ${item.score_components.skills} points. Reviewed ${escapeHtml(item.reviewed_at)} from <a href="${safeUrl(item.source_url)}" target="_blank" rel="noopener">${escapeHtml(item.source_title)}</a>.</p>
        <div class="recommendation-actions"><button type="button" data-open-program="${index}">Open interactive degree planner</button><a href="${safeUrl(item.official_program_url)}" target="_blank" rel="noopener">Official BMCC program page</a></div>
      </article>`;
    }).join('');
  }

  function renderCplResults(data) {
    const section = document.getElementById('cpl-results-section');
    const container = document.getElementById('cpl-results');
    const checklist = document.getElementById('cpl-checklist');
    section.hidden = false;
    document.getElementById('cpl-disclaimer').textContent = data.disclaimer || 'Possible opportunities require official evaluation.';
    const opportunities = data.opportunities || [];
    if (!opportunities.length) {
      container.innerHTML = `<div class="summary-row">${escapeHtml(data.message || 'No CPL preparation path selected.')}</div>`;
      checklist.innerHTML = '';
      return;
    }
    container.innerHTML = opportunities.map(item => {
      const programNotes = (item.program_guidance || []).map(note => `<div class="program-cpl-note"><strong>${escapeHtml(note.program_name)}:</strong> ${escapeHtml(note.guidance)}<br><small>Prepare: ${escapeHtml(note.evidence_requested)}</small></div>`).join('');
      return `<article class="cpl-card"><span class="cpl-status">${escapeHtml(item.status_label)}</span><h4>${escapeHtml(item.name)}</h4><p>${escapeHtml(item.description)}</p><p><strong>What to gather:</strong> ${escapeHtml(item.evidence_requested)}</p><p><strong>Official next step:</strong> ${escapeHtml(item.next_step)}</p>${programNotes}<p class="source-note">Reviewed ${escapeHtml(item.reviewed_at)}. <a href="${safeUrl(item.official_url)}" target="_blank" rel="noopener">${escapeHtml(item.source_title)}</a></p></article>`;
    }).join('');
    const documents = data.document_checklist || [];
    checklist.innerHTML = documents.length ? `<h4>Document checklist for an advisor or CPL conversation</h4><ul>${documents.map(item => `<li>${escapeHtml(item)}</li>`).join('')}</ul>` : '';
  }

  async function requestCplScreening(programCodes) {
    const response = await fetch('/api/db/cuny-beyond/cpl-screening', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ selections: state.cplSelections, program_codes: programCodes })
    });
    if (!response.ok) throw new Error('CPL screening unavailable');
    renderCplResults(await response.json());
  }

  async function requestRecommendations() {
    captureState();
    const button = document.getElementById('match-button');
    const status = document.getElementById('match-status');
    button.disabled = true;
    status.textContent = 'Checking reviewed BMCC mappings…';
    let programCodes = [];
    try {
      const response = await fetch('/api/db/cuny-beyond/recommendations', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ career_goal: state.careerGoal, skills: state.skills })
      });
      if (!response.ok) throw new Error('Recommendation service unavailable');
      const data = await response.json();
      renderRecommendations(data);
      programCodes = (data.recommendations || []).map(item => item.program_code);
      status.textContent = data.matched_career ? `Matched to the reviewed ${data.matched_career.name} career profile.` : 'No career profile matched yet.';
    } catch (_) {
      status.textContent = 'We could not load program matches. Your browser draft is still saved; please try again.';
    }
    try {
      await requestCplScreening(programCodes);
    } catch (_) {
      document.getElementById('cpl-results-section').hidden = false;
      document.getElementById('cpl-disclaimer').textContent = 'Prior-learning guidance could not be loaded. No degree totals were changed; please use the official BMCC CPL page.';
    } finally { button.disabled = false; }
  }

  function showStep(focusHeading) {
    steps.forEach((step, index) => { step.hidden = index !== state.step; });
    document.getElementById('step-count').textContent = `Step ${state.step + 1} of ${steps.length}`;
    document.getElementById('progress-fill').style.width = `${((state.step + 1) / steps.length) * 100}%`;
    backButton.hidden = state.step === 0;
    nextButton.hidden = state.step === steps.length - 1;
    errorBox.textContent = '';
    if (state.step === steps.length - 1) renderSummary();
    if (focusHeading) steps[state.step].querySelector('h2').focus();
  }

  nextButton.addEventListener('click', () => {
    const error = validateStep();
    if (error) { errorBox.textContent = error; return; }
    captureState();
    state.step += 1;
    saveDraft();
    showStep(true);
  });
  backButton.addEventListener('click', () => { captureState(); state.step -= 1; saveDraft(); showStep(true); });
  document.getElementById('restart-button').addEventListener('click', () => {
    if (!window.confirm('Clear this browser draft and start again?')) return;
    localStorage.removeItem(STORAGE_KEY);
    form.reset();
    Object.assign(state, { step: 0, profile: '', careerGoal: '', employment: '', skills: [], cplSelections: [], expiresAt: 0 });
    document.getElementById('save-status').textContent = 'Draft cleared.';
    updateCounts(); showStep(true);
  });
  document.getElementById('career-goal').addEventListener('input', updateCounts);
  document.getElementById('skill-choices').addEventListener('change', updateCounts);
  document.getElementById('cpl-choices').addEventListener('change', event => {
    const changed = event.target;
    if (!changed.matches('input[name="cpl"]') || !changed.checked) return;
    const all = Array.from(form.querySelectorAll('input[name="cpl"]'));
    if (changed.value === 'none') all.forEach(input => { if (input !== changed) input.checked = false; });
    else {
      const none = form.querySelector('input[name="cpl"][value="none"]');
      if (none) none.checked = false;
    }
  });
  document.getElementById('match-button').addEventListener('click', requestRecommendations);
  document.getElementById('recommendation-results').addEventListener('click', event => {
    const button = event.target.closest('[data-open-program]');
    if (button) openDegreePlanner(Number(button.dataset.openProgram));
    const retry = event.target.closest('[data-retry-career]');
    if (retry) {
      document.getElementById('career-goal').value = retry.dataset.retryCareer;
      state.careerGoal = retry.dataset.retryCareer;
      saveDraft(); updateCounts(); requestRecommendations();
    }
  });

  function renderSupportedCareers() {
    const featuredNames = ['Data Analyst', 'Software Developer', 'Computer Systems Analyst', 'Information Security Analyst', 'Business Intelligence Analyst'];
    const featured = featuredNames.map(name => supportedCareers.find(item => item.name === name)).filter(Boolean);
    document.getElementById('career-options').innerHTML = supportedCareers.map(item => `<option value="${escapeHtml(item.name)}"></option>`).join('');
    document.getElementById('career-suggestions').innerHTML = featured.map(item => `<button class="career-chip" type="button" data-career-name="${escapeHtml(item.name)}">${escapeHtml(item.name)}</button>`).join('');
  }

  document.getElementById('career-suggestions').addEventListener('click', event => {
    const button = event.target.closest('[data-career-name]');
    if (!button) return;
    document.getElementById('career-goal').value = button.dataset.careerName;
    updateCounts();
    document.getElementById('career-goal').focus();
  });

  async function initialize() {
    renderSkills();
    try {
      const response = await fetch('/api/cuny-beyond/config');
      if (response.ok) ttlHours = (await response.json()).session_ttl_hours || ttlHours;
    } catch (_) { /* Static defaults keep the public intake usable. */ }
    try {
      const response = await fetch('/api/db/cuny-beyond/careers');
      if (response.ok) { supportedCareers = await response.json(); renderSupportedCareers(); }
    } catch (_) { /* Typed aliases continue to work if discovery is temporarily unavailable. */ }
    loadDraft(); restoreInputs(); showStep(false);
  }
  initialize();
})();
