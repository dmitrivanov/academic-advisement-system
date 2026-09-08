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
    some_college: 'Adult with some college', transfer: 'Transfer to BMCC',
    returning: 'Returning BMCC student', degree_holder: 'Adult with a degree',
    current_bmcc: 'Current BMCC student', current_cuny: 'Current CUNY student'
  };
  const EMPLOYMENT_LABELS = { yes: 'Yes, I currently work', no: 'No, I am not currently working', prefer_not: 'Prefer not to say' };
  const CPL_LABELS = {
    'previous-college-credit': 'Previous college courses', 'standardized-exams': 'AP or recognized exams',
    'ace-reviewed-learning': 'ACE or NCCRS learning', 'employer-training': 'Employer or industry training',
    'military-learning': 'Military learning', 'licenses-certifications': 'Licenses or certifications',
    'biliteracy-language': 'Biliteracy or language proficiency', 'portfolio-experiential': 'Portfolio or substantial experience',
    'not-sure': 'Not sure', none: 'None of these'
  };
  const CHAT_QUESTIONS = [
    'What best describes you?', 'What do you want to do in your life or career?',
    'Are you currently working?', 'Which skills do you use or want to build?',
    'Could any previous learning be relevant?'
  ];
  const state = { step: 0, profile: '', careerGoal: '', employment: '', skills: [], cplSelections: [], freeAnswers: {}, apExams: [], transcriptCourses: [], expiresAt: 0 };
  const form = document.getElementById('intake-form');
  const steps = Array.from(document.querySelectorAll('.step'));
  const nextButton = document.getElementById('next-button');
  const backButton = document.getElementById('back-button');
  const errorBox = document.getElementById('form-error');
  let ttlHours = 24;
  let latestRecommendations = [];
  let supportedCareers = [];
  let latestCplScreening = null;
  let latestMatchedCareer = null;

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
      state.freeAnswers = state.freeAnswers && typeof state.freeAnswers === 'object' ? state.freeAnswers : {};
      state.apExams = Array.isArray(state.apExams) ? state.apExams.slice(0, 20) : [];
      state.transcriptCourses = Array.isArray(state.transcriptCourses) ? state.transcriptCourses.slice(0, 80) : [];
      document.getElementById('save-status').textContent = 'Your saved draft was restored on this device.';
    } catch (_) { localStorage.removeItem(STORAGE_KEY); }
  }

  function saveDraft() {
    state.expiresAt = Date.now() + ttlHours * 60 * 60 * 1000;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    document.getElementById('save-status').textContent = `Draft saved in this browser for ${ttlHours} hour${ttlHours === 1 ? '' : 's'}.`;
  }

  function renderSkills(skills = SKILLS) {
    const fieldset = document.getElementById('skill-choices');
    const choices = [...new Set([...state.skills, ...skills])].slice(0, 20);
    fieldset.innerHTML = choices.map(skill => `<label><input type="checkbox" name="skills" value="${escapeHtml(skill)}"${state.skills.includes(skill) ? ' checked' : ''}><span>${escapeHtml(skill)}</span></label>`).join('');
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
    document.getElementById('profile-free').value = state.freeAnswers.profile || '';
    document.getElementById('employment-free').value = state.freeAnswers.employment || '';
    document.getElementById('skills-free').value = state.freeAnswers.skills || '';
    document.getElementById('cpl-free').value = state.freeAnswers.cpl || '';
    state.skills.forEach(skill => {
      const input = Array.from(form.querySelectorAll('input[name="skills"]')).find(item => item.value === skill);
      if (input) input.checked = true;
    });
    state.cplSelections.forEach(code => {
      const input = form.querySelector(`input[name="cpl"][value="${code}"]`);
      if (input) input.checked = true;
    });
    updateCounts();
    renderApResults();
  }

  function updateCounts() {
    document.getElementById('goal-count').textContent = document.getElementById('career-goal').value.length;
    const count = form.querySelectorAll('input[name="skills"]:checked').length;
    document.getElementById('skill-count').textContent = `${count} of ${MAX_SKILLS} selected`;
    form.querySelectorAll('input[name="skills"]:not(:checked)').forEach(input => { input.disabled = count >= MAX_SKILLS; });
  }

  function validateStep() {
    if (state.step === 0 && !selectedValue('profile') && document.getElementById('profile-free').value.trim().length < 2) return 'Choose a tag or describe what best describes you.';
    if (state.step === 1 && document.getElementById('career-goal').value.trim().length < 2) return 'Enter a short career or life goal.';
    if (state.step === 2 && !selectedValue('employment') && document.getElementById('employment-free').value.trim().length < 2) return 'Choose a tag or describe your work situation.';
    if (state.step === 3 && form.querySelectorAll('input[name="skills"]:checked').length === 0 && document.getElementById('skills-free').value.trim().length < 2) return 'Choose or enter at least one skill.';
    if (state.step === 4 && form.querySelectorAll('input[name="cpl"]:checked').length === 0 && document.getElementById('cpl-free').value.trim().length < 2) return 'Choose a tag or describe previous learning.';
    return '';
  }

  function captureState() {
    state.profile = selectedValue('profile') || state.profile;
    state.careerGoal = document.getElementById('career-goal').value.trim();
    state.employment = selectedValue('employment') || state.employment;
    state.skills = Array.from(form.querySelectorAll('input[name="skills"]:checked')).map(input => input.value).slice(0, MAX_SKILLS);
    state.cplSelections = Array.from(form.querySelectorAll('input[name="cpl"]:checked')).map(input => input.value).slice(0, 9);
    state.freeAnswers = {
      profile: document.getElementById('profile-free').value.trim(), employment: document.getElementById('employment-free').value.trim(),
      skills: document.getElementById('skills-free').value.trim(), cpl: document.getElementById('cpl-free').value.trim()
    };
  }

  function renderSummary() {
    const employment = state.employment === 'yes' ? 'Currently working' : state.employment === 'no' ? 'Not currently working' : 'Prefer not to say';
    document.getElementById('summary').innerHTML = `
      <div class="summary-row"><strong>Student status</strong>${escapeHtml(PROFILE_LABELS[state.profile] || state.freeAnswers.profile || 'Not provided')}</div>
      <div class="summary-row"><strong>Your goal</strong>${escapeHtml(state.careerGoal)}</div>
      <div class="summary-row"><strong>Employment</strong>${escapeHtml(state.employment ? employment : state.freeAnswers.employment || 'Not provided')}</div>
      <div class="summary-row"><strong>Skills</strong>${state.skills.map(escapeHtml).join(', ')}</div>
      <div class="summary-row"><strong>Prior-learning screen</strong>${state.cplSelections.includes('none') ? 'None selected' : `${state.cplSelections.length} possible path${state.cplSelections.length === 1 ? '' : 's'} to review`}</div>`;
  }

  function chatAnswers() {
    return [
      PROFILE_LABELS[state.profile] || state.freeAnswers.profile || '', state.careerGoal || '', EMPLOYMENT_LABELS[state.employment] || state.freeAnswers.employment || '',
      state.skills.join(', ') || state.freeAnswers.skills, state.cplSelections.map(code => CPL_LABELS[code] || code).join(', ') || state.freeAnswers.cpl
    ];
  }

  function renderChatHistory() {
    const answers = chatAnswers();
    const completed = Math.min(state.step, CHAT_QUESTIONS.length);
    document.getElementById('chat-history').innerHTML = CHAT_QUESTIONS.slice(0, completed).map((question, index) => `
      <div class="chat-turn">
        <div class="chat-bubble assistant"><small>AI Academic Advisement Chatbot</small>${escapeHtml(question)}</div>
        <div class="chat-bubble user"><small>You</small>${escapeHtml(answers[index] || 'Skipped')}</div>
      </div>`).join('');
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
    saveProgramContext(result);
    window.location.href = '/db-progress';
  }

  function saveProgramContext(result) {
    sessionStorage.setItem('selectedProgramContext', JSON.stringify({
      institutionCode: result.institution_code,
      institutionName: result.institution_name,
      programCode: result.program_code,
      programName: result.program_name,
      catalogYear: result.catalog_year || '',
      selectedAt: new Date().toISOString(),
      source: 'cuny-beyond'
    }));
  }

  function openPlannerModal() {
    const result = latestRecommendations[0];
    const status = document.getElementById('transcript-status');
    if (!result) {
      status.textContent = 'Find your BMCC program matches first so the completed-course page knows which curriculum to display.';
      document.getElementById('match-button').focus();
      return;
    }
    saveProgramContext(result);
    const modal = document.getElementById('planner-modal');
    document.getElementById('planner-modal-title').textContent = `Review recognized courses for ${result.program_name}`;
    document.getElementById('planner-modal-frame').src = `/db-progress?embedded=transcript&v=${Date.now()}`;
    modal.hidden = false;
    document.body.style.overflow = 'hidden';
    document.getElementById('close-planner-modal').focus();
  }

  function closePlannerModal() {
    const modal = document.getElementById('planner-modal');
    modal.hidden = true;
    document.getElementById('planner-modal-frame').src = 'about:blank';
    document.body.style.overflow = '';
    document.getElementById('apply-transcript')?.focus();
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
      const mapUrl = item.degree_map?.source_pdf || item.degree_map?.source_pdfs?.[0]?.url;
      const degreeMap = mapUrl ? `<details class="degree-map-preview"><summary>View degree map now</summary><iframe src="${safeUrl(mapUrl)}#view=FitH" title="${escapeHtml(item.program_name)} degree map" loading="lazy"></iframe><p class="source-note"><a href="${safeUrl(mapUrl)}" target="_blank" rel="noopener">Open or download the degree-map PDF</a></p></details>` : '';
      return `<article class="recommendation-card">
        <div class="recommendation-heading"><div><h3>${escapeHtml(item.program_name)} (${escapeHtml(item.degree_type || 'Degree')})</h3><p>${escapeHtml(item.department_name)} · ${escapeHtml(item.catalog_year || 'Current catalog')}</p></div><span class="match-score">${item.score} fit points</span></div>
        <p class="match-explanation">${escapeHtml(item.explanation)}</p>
        <div class="match-details">${tags}</div>
        <p class="source-note">Career evidence: ${item.score_components.career} points; selected-skill evidence: ${item.score_components.skills} points. Reviewed ${escapeHtml(item.reviewed_at)} from <a href="${safeUrl(item.source_url)}" target="_blank" rel="noopener">${escapeHtml(item.source_title)}</a>.</p>
        <div class="recommendation-actions"><button type="button" data-open-program="${index}">Open interactive degree planner</button><button type="button" data-open-graph="${escapeHtml(item.program_code)}">View degree map tree</button><a href="${safeUrl(item.official_program_url)}" target="_blank" rel="noopener">Official BMCC program page</a></div>${degreeMap}
      </article>`;
    }).join('');
  }

  function renderCplResults(data) {
    latestCplScreening = data;
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

  function saveReferralSummary(matchedCareer) {
    if (matchedCareer) latestMatchedCareer = matchedCareer;
    const transferSnapshot = (() => { try { return JSON.parse(sessionStorage.getItem('transferSnapshot') || 'null'); } catch (_) { return null; } })();
    const scheduleChecklist = (() => { try { return JSON.parse(sessionStorage.getItem('cunyBeyondScheduleChecklistV1') || 'null'); } catch (_) { return null; } })();
    const summary = {
      pathway: PROFILE_LABELS[state.profile] || state.profile,
      career_goal: state.careerGoal,
      matched_career: latestMatchedCareer?.name || null,
      skills: state.skills.slice(0, MAX_SKILLS),
      recommended_programs: latestRecommendations.slice(0, 3).map(item => ({
        code: item.program_code, name: item.program_name, degree_type: item.degree_type,
        score: item.score, explanation: item.explanation, official_url: item.official_program_url,
        source_title: item.source_title, source_url: item.source_url,
      })),
      cpl_possibilities: (latestCplScreening?.opportunities || []).map(item => ({ name: item.name, status: item.status_label, next_step: item.next_step, official_url: item.official_url })),
      completed_courses: transferSnapshot?.completed_course_details || [],
      transfer_options: latestRecommendations.slice(0, 3).flatMap(item => item.transfer_options?.length
        ? item.transfer_options.map(option => ({ program: item.program_name, next_step: `${option.target_institution} - ${option.target_program}: ${option.explanation}` }))
        : [{ program: item.program_name, next_step: 'No reviewed destination is published yet; use CUNY Transfer Explorer with an advisor.' }]),
      schedule_checklist: scheduleChecklist,
      sources: [
        ...latestRecommendations.map(item => ({ title: item.source_title, url: item.source_url })),
        { title: 'BMCC Academic Advisement', url: 'https://www.bmcc.cuny.edu/academics/advisement/advisement/' },
      ],
      expires_at: Date.now() + ttlHours * 60 * 60 * 1000,
    };
    sessionStorage.setItem('cunyBeyondReferralSummaryV1', JSON.stringify(summary));
    document.getElementById('referral-action').hidden = false;
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
      saveReferralSummary(data.matched_career);
    } catch (_) {
      status.textContent = 'We could not load program matches. Your browser draft is still saved; please try again.';
    }
    try {
      await requestCplScreening(programCodes);
      saveReferralSummary(null);
    } catch (_) {
      document.getElementById('cpl-results-section').hidden = false;
      document.getElementById('cpl-disclaimer').textContent = 'Prior-learning guidance could not be loaded. No degree totals were changed; please use the official BMCC CPL page.';
    } finally { button.disabled = false; }
  }

  async function interpretFreeAnswer(step, answer, allowedValues) {
    if (!answer || !document.getElementById('ai-assisted').checked) return [];
    const response = await fetch('/api/cuny-beyond/interpret', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ step, answer, career_goal: document.getElementById('career-goal').value.trim(), allowed_values: allowedValues })
    });
    if (!response.ok) throw new Error('AI interpretation is temporarily unavailable');
    return response.json();
  }

  async function applyFreeAnswerForStep() {
    captureState();
    if (state.step === 0 && !selectedValue('profile') && state.freeAnswers.profile) {
      const result = await interpretFreeAnswer('profile', state.freeAnswers.profile, Object.keys(PROFILE_LABELS));
      const input = form.querySelector(`input[name="profile"][value="${result.selected_values?.[0] || ''}"]`);
      if (input) input.checked = true;
    } else if (state.step === 2 && !selectedValue('employment') && state.freeAnswers.employment) {
      const result = await interpretFreeAnswer('employment', state.freeAnswers.employment, Object.keys(EMPLOYMENT_LABELS));
      const input = form.querySelector(`input[name="employment"][value="${result.selected_values?.[0] || ''}"]`);
      if (input) input.checked = true;
    } else if (state.step === 3 && state.freeAnswers.skills) {
      addCustomSkill(state.freeAnswers.skills);
    } else if (state.step === 4 && !state.cplSelections.length && state.freeAnswers.cpl) {
      const result = await interpretFreeAnswer('cpl', state.freeAnswers.cpl, Object.keys(CPL_LABELS));
      (result.selected_values || []).forEach(value => { const input = form.querySelector(`input[name="cpl"][value="${value}"]`); if (input) input.checked = true; });
    }
    captureState();
  }

  async function refreshContextualSkills() {
    const goal = state.careerGoal || document.getElementById('career-goal').value.trim();
    if (!goal || !document.getElementById('ai-assisted').checked) { renderSkills(); updateCounts(); return; }
    try {
      const result = await interpretFreeAnswer('skills', `Suggest skills for ${goal}`, []);
      if (result.skills?.length) renderSkills(result.skills);
    } catch (_) { renderSkills(); }
    updateCounts();
  }

  function showStep(focusHeading) {
    steps.forEach((step, index) => { step.hidden = index !== state.step; });
    form.classList.toggle('results-view', state.step === steps.length - 1);
    renderChatHistory();
    document.getElementById('step-count').textContent = state.step === steps.length - 1 ? 'Your results' : `Question ${state.step + 1} of ${steps.length - 1}`;
    document.getElementById('progress-fill').style.width = `${((state.step + 1) / steps.length) * 100}%`;
    backButton.hidden = state.step === 0;
    nextButton.hidden = state.step === steps.length - 1;
    errorBox.textContent = '';
    if (state.step === steps.length - 1) renderSummary();
    if (focusHeading) {
      steps[state.step].querySelector('h2').focus();
      const conversation = document.getElementById('intake-form');
      const current = steps[state.step];
      const centeredTop = Math.max(0, current.offsetTop - (conversation.clientHeight - Math.min(current.offsetHeight, conversation.clientHeight)) / 2);
      conversation.scrollTo({ top: centeredTop, behavior: 'smooth' });
    }
  }

  nextButton.addEventListener('click', async () => {
    const error = validateStep();
    if (error) { errorBox.textContent = error; return; }
    nextButton.disabled = true;
    errorBox.textContent = '';
    try { await applyFreeAnswerForStep(); }
    catch (err) { errorBox.textContent = `${err.message}. Choose a quick tag or turn off AI assist to continue.`; nextButton.disabled = false; return; }
    if (state.step === 1) { captureState(); await refreshContextualSkills(); }
    state.step += 1;
    saveDraft();
    showStep(true);
    nextButton.disabled = false;
  });
  backButton.addEventListener('click', () => { captureState(); state.step -= 1; saveDraft(); showStep(true); });
  document.getElementById('restart-button').addEventListener('click', () => {
    if (!window.confirm('Clear this browser draft and start again?')) return;
    localStorage.removeItem(STORAGE_KEY);
    form.reset();
    Object.assign(state, { step: 0, profile: '', careerGoal: '', employment: '', skills: [], cplSelections: [], freeAnswers: {}, apExams: [], transcriptCourses: [], expiresAt: 0 });
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
    document.getElementById('ap-details').hidden = !form.querySelector('input[name="cpl"][value="standardized-exams"]')?.checked;
  });
  document.getElementById('match-button').addEventListener('click', requestRecommendations);
  document.getElementById('recommendation-results').addEventListener('click', event => {
    const button = event.target.closest('[data-open-program]');
    if (button) openDegreePlanner(Number(button.dataset.openProgram));
    const graphButton = event.target.closest('[data-open-graph]');
    if (graphButton) CurriculumGraph.open(graphButton.dataset.openGraph);
    const retry = event.target.closest('[data-retry-career]');
    if (retry) {
      document.getElementById('career-goal').value = retry.dataset.retryCareer;
      state.careerGoal = retry.dataset.retryCareer;
      saveDraft(); updateCounts(); requestRecommendations();
    }
  });

  function renderSupportedCareers() {
    const featuredNames = ['Registered Nurse', 'Data Analyst', 'Accounting Clerk', 'Case Manager', 'Police Officer', 'Urban Planner'];
    const featured = featuredNames.map(name => supportedCareers.find(item => item.name === name)).filter(Boolean);
    document.getElementById('career-options').innerHTML = supportedCareers.map(item => `<option value="${escapeHtml(item.name)}"></option>`).join('');
    document.getElementById('career-suggestions').innerHTML = featured.map(item => `<button class="career-chip" type="button" data-career-name="${escapeHtml(item.name)}">${escapeHtml(item.name)}</button>`).join('');
    renderCareerBrowser('');
  }

  function renderCareerBrowser(query) {
    const normalized = (query || '').trim().toLowerCase();
    const matches = supportedCareers.filter(item => [item.name, ...(item.aliases || [])].some(value => value.toLowerCase().includes(normalized)));
    document.getElementById('career-browser-count').textContent = `${matches.length} reviewed career${matches.length === 1 ? '' : 's'} shown`;
    document.getElementById('career-browser-results').innerHTML = matches.map(item => `<button type="button" data-career-name="${escapeHtml(item.name)}"><strong>${escapeHtml(item.name)}</strong><small>${item.program_count} reviewed BMCC program match${item.program_count === 1 ? '' : 'es'}</small></button>`).join('') || '<p class="field-help">No reviewed title matches that filter.</p>';
  }

  function chooseCareer(event) {
    const button = event.target.closest('[data-career-name]');
    if (!button) return;
    document.getElementById('career-goal').value = button.dataset.careerName;
    updateCounts();
    document.getElementById('career-goal').focus();
  }
  document.getElementById('career-suggestions').addEventListener('click', chooseCareer);
  document.getElementById('career-browser-results').addEventListener('click', chooseCareer);
  document.getElementById('career-filter').addEventListener('input', event => renderCareerBrowser(event.target.value));

  function addCustomSkill(value) {
    const skill = (value || '').trim().slice(0, 100);
    if (!skill || state.skills.includes(skill) || state.skills.length >= MAX_SKILLS) return;
    state.skills.push(skill);
    renderSkills();
    document.getElementById('skills-free').value = '';
    updateCounts();
  }
  document.getElementById('add-skill').addEventListener('click', () => addCustomSkill(document.getElementById('skills-free').value));

  async function calculateApCredits() {
    if (!state.apExams.length) { document.getElementById('ap-results').innerHTML = ''; return; }
    const response = await fetch('/api/db/cuny-beyond/ap-equivalencies', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ exams: state.apExams })
    });
    if (!response.ok) throw new Error('AP equivalencies could not be loaded');
    const data = await response.json();
    state.apCredits = data.results;
    const apImports = data.results.filter(item => !item.bmcc_equivalency.includes(' or ')).map(item => ({ code: item.bmcc_equivalency, bmcc_equivalency: item.bmcc_equivalency, title: `${item.exam} score ${item.score}`, credits: item.estimated_credits, source: 'AP planning estimate' }));
    const existing = state.transcriptCourses.filter(item => item.include !== false && item.code);
    sessionStorage.setItem('cunyBeyondImportedCoursesV1', JSON.stringify([...existing, ...apImports]));
    document.getElementById('ap-results').innerHTML = data.results.map((item, index) => `<div class="ap-result"><span><strong>${escapeHtml(item.exam)} · score ${item.score}</strong><br>BMCC: ${escapeHtml(item.bmcc_equivalency)} · ${item.estimated_credits ?? 'credit amount requires review'}${item.estimated_credits != null ? ' estimated credits' : ''}</span><button type="button" data-remove-ap="${index}">Remove</button></div>`).join('') + `<p class="transcript-notice"><strong>Estimated total with known catalog credits: ${data.estimated_total_credits}</strong><br>${escapeHtml(data.disclaimer)} <a href="https://www.bmcc.cuny.edu/admissions/apply-now/credit-for-prior-learning-cpl/" target="_blank" rel="noopener">BMCC CPL source</a></p>`;
  }
  function renderApResults() {
    document.getElementById('ap-details').hidden = !state.cplSelections.includes('standardized-exams');
    calculateApCredits().catch(err => { document.getElementById('ap-results').textContent = err.message; });
  }
  document.getElementById('add-ap').addEventListener('click', () => {
    const exam = document.getElementById('ap-exam').value;
    const score = Number(document.getElementById('ap-score').value);
    if (exam && !state.apExams.some(item => item.exam === exam)) state.apExams.push({ exam, score });
    saveDraft(); renderApResults();
  });
  document.getElementById('ap-results').addEventListener('click', event => {
    const button = event.target.closest('[data-remove-ap]');
    if (!button) return;
    state.apExams.splice(Number(button.dataset.removeAp), 1); saveDraft(); renderApResults();
  });

  function renderTranscriptReview(courses, warnings = []) {
    state.transcriptCourses = courses;
    const container = document.getElementById('transcript-review');
    if (!courses.length) { container.innerHTML = '<p class="transcript-notice">No clearly completed college courses were found. Review the source document manually.</p>'; return; }
    container.innerHTML = `<table class="transcript-table"><thead><tr><th>Use</th><th>Institution</th><th>Course</th><th>Title</th><th>Credits</th><th>Grade</th></tr></thead><tbody>${courses.map((item, index) => `<tr><td><input type="checkbox" data-transcript-include="${index}"${item.include !== false ? ' checked' : ''}></td><td>${escapeHtml(item.institution || 'Not identified')}</td><td><input data-transcript-field="code" data-index="${index}" value="${escapeHtml(item.code)}"></td><td>${escapeHtml(item.title)}</td><td>${item.credits ?? '—'}</td><td>${escapeHtml(item.grade)}</td></tr>`).join('')}</tbody></table>${warnings.map(item => `<p class="transcript-notice">${escapeHtml(item)}</p>`).join('')}<button type="button" id="apply-transcript">Use reviewed courses in degree planner</button><p class="field-help">BMCC courses and published BMCC AP equivalencies can be checked automatically when they appear in the selected program. Courses from another college remain in the transfer-review snapshot until an official equivalency is confirmed.</p>`;
    document.getElementById('apply-transcript').addEventListener('click', applyTranscriptCourses);
  }
  function applyTranscriptCourses() {
    document.querySelectorAll('[data-transcript-include]').forEach(input => { state.transcriptCourses[Number(input.dataset.transcriptInclude)].include = input.checked; });
    document.querySelectorAll('[data-transcript-field="code"]').forEach(input => { state.transcriptCourses[Number(input.dataset.index)].code = input.value.trim().toUpperCase(); });
    const selected = state.transcriptCourses.filter(item => item.include && item.code);
    const apCourses = (state.apCredits || []).filter(item => !item.bmcc_equivalency.includes(' or ')).map(item => ({ code: item.bmcc_equivalency, bmcc_equivalency: item.bmcc_equivalency, title: `${item.exam} score ${item.score}`, credits: item.estimated_credits, source: 'AP planning estimate' }));
    const imported = [...selected, ...apCourses];
    sessionStorage.setItem('cunyBeyondImportedCoursesV1', JSON.stringify(imported));
    sessionStorage.setItem('transferSnapshot', JSON.stringify({ completed_courses: imported.map(item => item.code), completed_course_details: imported, source: 'cuny-beyond-import', timestamp: new Date().toISOString() }));
    saveDraft();
    document.getElementById('transcript-status').textContent = `${imported.length} reviewed course or AP equivalenc${imported.length === 1 ? 'y' : 'ies'} will be carried into the interactive degree planner.`;
    openPlannerModal();
  }
  document.getElementById('analyze-transcript').addEventListener('click', async () => {
    const file = document.getElementById('transcript-file').files[0];
    const status = document.getElementById('transcript-status');
    if (!file) { status.textContent = 'Choose a PDF, JPG, or PNG first.'; return; }
    status.textContent = 'Reading the document securely…';
    const body = new FormData(); body.append('document', file);
    try {
      const response = await fetch('/api/cuny-beyond/transcript-extract', { method: 'POST', body });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Document analysis failed');
      status.textContent = data.disclaimer;
      renderTranscriptReview(data.courses || [], data.warnings || []);
    } catch (err) { status.textContent = err.message; }
  });
  document.getElementById('close-planner-modal').addEventListener('click', closePlannerModal);
  document.querySelector('[data-close-planner]').addEventListener('click', closePlannerModal);
  document.addEventListener('keydown', event => { if (event.key === 'Escape' && !document.getElementById('planner-modal').hidden) closePlannerModal(); });


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
    try {
      const response = await fetch('/api/db/cuny-beyond/ap-equivalencies');
      if (response.ok) document.getElementById('ap-exam').innerHTML = (await response.json()).map(item => `<option value="${escapeHtml(item.exam)}">${escapeHtml(item.exam)}</option>`).join('');
    } catch (_) { document.getElementById('ap-details').hidden = true; }
    loadDraft(); restoreInputs(); showStep(false);
  }
  initialize();
})();
