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
    degree_holder: 'Adult with a degree',
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
  const CHAT_QUESTIONS = Object.freeze({
    identity: 'What best describes you?', major: 'What is your major?', career: 'What do you want to do in your life or career?',
    employment: 'Are you currently working?', semester: 'Which semester are you in?', skills: 'Which skills do you use or want to build?',
    coursework: 'Which courses have you completed?', priorLearning: 'Could any previous learning be relevant?'
  });
  const state = { step: 0, profile: '', careerGoal: '', employment: '', skills: [], cplSelections: [], freeAnswers: {}, apExams: [], transcriptCourses: [], currentMajor: '', currentProgram: null, semesterStanding: '', expiresAt: 0 };
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
  let availablePrograms = [];
  let availableProgramCourses = [];
  let plannerMode = '';
  let modalSelectedCodes = [];

  function isCurrentStudent() { return ['current_bmcc', 'current_cuny'].includes(state.profile || selectedValue('profile')); }
  function isFirstSemester() { return state.semesterStanding === '1'; }

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
      state.currentProgram = state.currentProgram && typeof state.currentProgram === 'object' ? state.currentProgram : null;
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
    document.getElementById('current-major-search').value = state.currentMajor || '';
    if (state.semesterStanding) {
      const semester = form.querySelector(`input[name="semester_standing"][value="${state.semesterStanding}"]`);
      if (semester) semester.checked = true;
    }
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
    if (state.step === 1 && isCurrentStudent() && !state.currentProgram) return 'Choose your major from the search results.';
    if (state.step === 1 && !isCurrentStudent() && document.getElementById('career-goal').value.trim().length < 2) return 'Enter a short career or life goal.';
    if (state.step === 2 && !selectedValue('employment') && document.getElementById('employment-free').value.trim().length < 2) return 'Choose a tag or describe your work situation.';
    if (state.step === 3 && isCurrentStudent() && !selectedValue('semester_standing')) return 'Choose your current semester.';
    if (state.step === 3 && !isCurrentStudent() && form.querySelectorAll('input[name="skills"]:checked').length === 0 && document.getElementById('skills-free').value.trim().length < 2) return 'Choose or enter at least one skill.';
    if (state.step === 4 && isCurrentStudent() && !isFirstSemester() && !state.transcriptCourses.some(item => item.include !== false && item.code)) return 'Add at least one completed course using upload, manual entry, or the visual selector.';
    if (state.step === 4 && (!isCurrentStudent() || isFirstSemester()) && form.querySelectorAll('input[name="cpl"]:checked').length === 0 && document.getElementById('cpl-free').value.trim().length < 2) return 'Choose a tag or describe previous learning.';
    return '';
  }

  function captureState() {
    state.profile = selectedValue('profile') || state.profile;
    state.careerGoal = document.getElementById('career-goal').value.trim();
    state.employment = selectedValue('employment') || state.employment;
    state.skills = Array.from(form.querySelectorAll('input[name="skills"]:checked')).map(input => input.value).slice(0, MAX_SKILLS);
    state.cplSelections = Array.from(form.querySelectorAll('input[name="cpl"]:checked')).map(input => input.value).slice(0, 9);
    state.semesterStanding = selectedValue('semester_standing') || state.semesterStanding;
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
      ${state.profile === 'working_adult' ? `<div class="summary-row"><strong>Employment</strong>${escapeHtml(state.employment ? employment : state.freeAnswers.employment || 'Not provided')}</div>` : ''}
      <div class="summary-row"><strong>Skills</strong>${state.skills.map(escapeHtml).join(', ')}</div>
      <div class="summary-row"><strong>Prior-learning screen</strong>${state.cplSelections.includes('none') ? 'None selected' : `${state.cplSelections.length} possible path${state.cplSelections.length === 1 ? '' : 's'} to review`}</div>`;
  }

  function chatAnswers() {
    return {
      identity: PROFILE_LABELS[state.profile] || state.freeAnswers.profile || '',
      majorOrCareer: isCurrentStudent() ? state.currentMajor : state.careerGoal,
      employment: EMPLOYMENT_LABELS[state.employment] || state.freeAnswers.employment || '',
      semesterOrSkills: isCurrentStudent() ? state.semesterStanding : (state.skills.join(', ') || state.freeAnswers.skills),
      coursesOrPriorLearning: isCurrentStudent() && !isFirstSemester()
        ? state.transcriptCourses.filter(item => item.include !== false).map(item => item.code).join(', ')
        : (state.cplSelections.map(code => CPL_LABELS[code] || code).join(', ') || state.freeAnswers.cpl),
    };
  }

  function renderChatHistory() {
    const answers = chatAnswers();
    const turns = [
      { step: 0, question: CHAT_QUESTIONS.identity, answer: answers.identity },
      { step: 1, question: isCurrentStudent() ? CHAT_QUESTIONS.major : CHAT_QUESTIONS.career, answer: answers.majorOrCareer },
      ...(state.profile === 'working_adult' ? [{ step: 2, question: CHAT_QUESTIONS.employment, answer: answers.employment }] : []),
      { step: 3, question: isCurrentStudent() ? CHAT_QUESTIONS.semester : CHAT_QUESTIONS.skills, answer: isCurrentStudent() ? `${state.semesterStanding}${state.semesterStanding === '1' ? 'st' : state.semesterStanding === '2' ? 'nd' : state.semesterStanding === '3' ? 'rd' : 'th'} semester` : answers.semesterOrSkills },
      { step: 4, question: isCurrentStudent() && !isFirstSemester() ? CHAT_QUESTIONS.coursework : CHAT_QUESTIONS.priorLearning, answer: answers.coursesOrPriorLearning }
    ].filter(turn => turn.step < state.step);
    document.getElementById('chat-history').innerHTML = turns.map(({ question, answer }) => `
      <div class="chat-turn">
        <div class="chat-bubble assistant"><small>AI Academic Advisement Chatbot</small>${escapeHtml(question)}</div>
        <div class="chat-bubble user"><small>You</small>${escapeHtml(answer || 'Skipped')}</div>
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

  function saveCurrentProgramContext() {
    if (!state.currentProgram) return;
    sessionStorage.setItem('selectedProgramContext', JSON.stringify({
      institutionCode: state.currentProgram.institution_code, institutionName: state.currentProgram.institution,
      programCode: state.currentProgram.code, programName: state.currentProgram.name,
      catalogYear: state.currentProgram.catalog_year || '', selectedAt: new Date().toISOString(), source: 'cuny-beyond-current-student'
    }));
  }

  function openPlannerModal(mode = 'coursework') {
    plannerMode = mode;
    modalSelectedCodes = state.transcriptCourses.filter(item => item.include !== false).map(item => item.code);
    if (isCurrentStudent()) saveCurrentProgramContext();
    else if (latestRecommendations[0]) saveProgramContext(latestRecommendations[0]);
    const modal = document.getElementById('planner-modal');
    const programName = state.currentProgram?.name || latestRecommendations[0]?.program_name || 'your program';
    document.getElementById('planner-modal-title').textContent = mode === 'next-semester' ? `AI next-semester plan for ${programName}` : `Select completed courses for ${programName}`;
    document.getElementById('planner-modal-copy').textContent = mode === 'next-semester' ? 'Build and review the plan here, then return to the chatbot.' : 'Your selections return to the chatbot and remain available for this session.';
    document.getElementById('planner-modal-frame').src = `/db-progress?embedded=${mode === 'next-semester' ? 'workspace' : 'course-intake'}&v=${Date.now()}`;
    modal.hidden = false;
    document.body.style.overflow = 'hidden';
    document.getElementById('close-planner-modal').focus();
  }

  function closePlannerModal() {
    const modal = document.getElementById('planner-modal');
    modal.hidden = true;
    document.getElementById('planner-modal-frame').src = 'about:blank';
    document.body.style.overflow = '';
    if (plannerMode === 'coursework' && modalSelectedCodes.length) confirmCurrentCourses(modalSelectedCodes.map(code => courseFromCatalog(code)), 'visual selector');
    document.getElementById(plannerMode === 'next-semester' ? 'open-next-semester-plan' : 'open-completed-selector')?.focus();
    plannerMode = '';
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
    } else if (state.step === 3 && !isCurrentStudent() && state.freeAnswers.skills) {
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

  function nextStepFrom(step) {
    if (step === 0) return 1;
    if (step === 1) return state.profile === 'working_adult' ? 2 : 3;
    return Math.min(step + 1, 5);
  }

  function previousStepFrom(step) {
    if (step === 3) return state.profile === 'working_adult' ? 2 : 1;
    return Math.max(step - 1, 0);
  }

  function renderCurrentStudentSummary() {
    const courses = state.transcriptCourses.filter(item => item.include !== false && item.code);
    document.getElementById('current-student-summary').innerHTML = `
      <div class="summary-row"><strong>Student status</strong>${escapeHtml(PROFILE_LABELS[state.profile] || 'Current student')}</div>
      <div class="summary-row"><strong>Major</strong>${escapeHtml(state.currentMajor)}</div>
      <div class="summary-row"><strong>Semester</strong>${escapeHtml(state.semesterStanding === '5+' ? 'Fifth or later' : `Semester ${state.semesterStanding}`)}</div>
      <div class="summary-row"><strong>Completed-course context</strong>${courses.length ? `${courses.length} recognized course${courses.length === 1 ? '' : 's'}` : (isFirstSemester() ? 'First-semester / prior-learning review' : 'No courses confirmed')}</div>`;
    renderConfirmedCourses('current-final-courses');
    populateTransferSchools();
  }

  function showStep(focusHeading) {
    steps.forEach((step, index) => { step.hidden = index !== state.step; });
    form.classList.toggle('results-view', state.step === steps.length - 1);
    renderChatHistory();
    const current = isCurrentStudent();
    document.getElementById('career-goal-panel').hidden = current;
    document.getElementById('current-major-panel').hidden = !current;
    document.getElementById('skills-panel').hidden = current;
    document.getElementById('semester-standing-panel').hidden = !current;
    document.getElementById('prior-learning-panel').hidden = current && !isFirstSemester();
    document.getElementById('current-coursework-panel').hidden = !current || isFirstSemester();
    document.getElementById('prospective-results').hidden = current;
    document.getElementById('current-student-results').hidden = !current;
    const displayIndex = state.step === 2 ? 3 : state.step >= 3 && state.profile !== 'working_adult' ? state.step : state.step + 1;
    document.getElementById('step-count').textContent = state.step === steps.length - 1 ? 'Your advising workspace' : `Question ${Math.min(displayIndex, 5)} of 5`;
    document.getElementById('progress-fill').style.width = `${(Math.min(displayIndex, 5) / 5) * 100}%`;
    backButton.hidden = state.step === 0;
    nextButton.hidden = state.step === steps.length - 1;
    errorBox.textContent = '';
    if (state.step === steps.length - 1) current ? renderCurrentStudentSummary() : renderSummary();
    if (focusHeading) {
      steps[state.step].querySelector('div:not([hidden]) h2, h2').focus();
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
    if (state.step === 1 && !isCurrentStudent()) { captureState(); await refreshContextualSkills(); }
    state.step = nextStepFrom(state.step);
    saveDraft();
    showStep(true);
    nextButton.disabled = false;
  });
  backButton.addEventListener('click', () => { captureState(); state.step = previousStepFrom(state.step); saveDraft(); showStep(true); });
  document.getElementById('restart-button').addEventListener('click', () => {
    if (!window.confirm('Clear this browser draft and start again?')) return;
    localStorage.removeItem(STORAGE_KEY);
    form.reset();
    Object.assign(state, { step: 0, profile: '', careerGoal: '', employment: '', skills: [], cplSelections: [], freeAnswers: {}, apExams: [], transcriptCourses: [], currentMajor: '', currentProgram: null, semesterStanding: '', expiresAt: 0 });
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

  function programLabel(program) { return `${program.name}${program.degree_type ? ` (${program.degree_type})` : ''} · ${program.institution_code}`; }

  function renderMajorResults(query = '') {
    const normalized = query.trim().toLowerCase();
    const campusPrograms = availablePrograms.filter(program => state.profile !== 'current_bmcc' || program.institution_code === 'BMCC');
    const matches = campusPrograms.filter(program => !normalized || `${program.name} ${program.code} ${program.department}`.toLowerCase().includes(normalized)).slice(0, 10);
    document.getElementById('current-major-results').innerHTML = matches.map(program => `<button type="button" role="option" data-program-code="${escapeHtml(program.code)}"><strong>${escapeHtml(program.name)}</strong><small>${escapeHtml(program.degree_type || '')} · ${escapeHtml(program.institution)}</small></button>`).join('') || '<p class="field-help">No reviewed program matches that search. Try a shorter program name.</p>';
  }

  function renderPopularMajors() {
    const preferred = ['CS', 'NURS_AAS', 'ACCT_AAS', 'BBA_AS', 'PSY_AA'];
    const programs = preferred.map(code => availablePrograms.find(item => item.code === code)).filter(Boolean);
    document.getElementById('popular-major-choices').innerHTML = programs.map(program => `<button type="button" data-program-code="${escapeHtml(program.code)}">${escapeHtml(program.name)}</button>`).join('');
  }

  async function selectCurrentProgram(code) {
    const program = availablePrograms.find(item => item.code === code);
    if (!program) return;
    state.currentProgram = program;
    state.currentMajor = program.name;
    document.getElementById('current-major-search').value = program.name;
    document.getElementById('current-major-status').textContent = `Selected ${programLabel(program)}.`;
    document.getElementById('current-major-results').innerHTML = '';
    saveCurrentProgramContext();
    try {
      const response = await fetch(`/api/db/programs/${encodeURIComponent(program.code)}/requirements`);
      const data = await response.json();
      const unique = new Map();
      (data.groups || []).flatMap(group => group.courses || []).forEach(course => {
        const candidates = [course, ...(course.choice_options || [])];
        candidates.forEach(item => {
          if (item.code && !item.code.includes('-')) unique.set(item.code, { code: item.code, title: item.title || '', credits: item.credits });
        });
      });
      availableProgramCourses = [...unique.values()];
    } catch (_) { availableProgramCourses = []; }
    saveDraft();
  }

  document.getElementById('current-major-search').addEventListener('input', event => {
    if (state.currentProgram && event.target.value !== state.currentMajor) state.currentProgram = null;
    renderMajorResults(event.target.value);
  });
  function handleProgramChoice(event) {
    const button = event.target.closest('[data-program-code]');
    if (button) selectCurrentProgram(button.dataset.programCode);
  }
  document.getElementById('popular-major-choices').addEventListener('click', handleProgramChoice);
  document.getElementById('current-major-results').addEventListener('click', handleProgramChoice);

  function courseFromCatalog(code) {
    const found = availableProgramCourses.find(item => item.code === code);
    return { code, title: found?.title || '', credits: found?.credits ?? null, institution: '', grade: '', include: true, source: 'visual selector' };
  }

  function persistCompletedCourses() {
    const selected = state.transcriptCourses.filter(item => item.include !== false && item.code);
    sessionStorage.setItem('cunyBeyondImportedCoursesV1', JSON.stringify(selected));
    sessionStorage.setItem('transferSnapshot', JSON.stringify({
      source_program: {
        code: state.currentProgram?.code || '', name: state.currentProgram?.name || state.currentMajor,
        institution: state.currentProgram?.institution || '', institution_code: state.currentProgram?.institution_code || '',
        catalog_year: state.currentProgram?.catalog_year || ''
      },
      completed_courses: selected.map(item => item.code), completed_course_details: selected,
      source: 'cuny-beyond-current-student', timestamp: new Date().toISOString()
    }));
    saveDraft();
  }

  function saveCurrentReferralSummary(goal, extra = {}) {
    persistCompletedCourses();
    const completed = state.transcriptCourses.filter(item => item.include !== false && item.code);
    sessionStorage.setItem('cunyBeyondReferralSummaryV1', JSON.stringify({
      pathway: PROFILE_LABELS[state.profile] || 'Current student',
      current_program: state.currentProgram ? { code: state.currentProgram.code, name: state.currentProgram.name, institution: state.currentProgram.institution, catalog_year: state.currentProgram.catalog_year } : { name: state.currentMajor },
      semester: state.semesterStanding,
      advising_goal: goal,
      completed_courses: completed,
      transfer_destination: extra.transfer_destination || null,
      recommended_programs: [], cpl_possibilities: [], transfer_options: extra.transfer_destination ? [{ program: state.currentMajor, next_step: `Analyze transfer to ${extra.transfer_destination.school_name} — ${extra.transfer_destination.program_name}` }] : [],
      sources: [{ title: 'BMCC Academic Advisement', url: 'https://www.bmcc.cuny.edu/academics/advisement/advisement/' }],
      expires_at: Date.now() + ttlHours * 60 * 60 * 1000,
    }));
  }

  function populateTransferSchools() {
    const school = document.getElementById('transfer-school');
    if (!school || school.options.length > 1) return;
    const institutions = [...new Map(availablePrograms.filter(item => item.institution_code !== state.currentProgram?.institution_code).map(item => [item.institution_code, item.institution])).entries()];
    school.insertAdjacentHTML('beforeend', institutions.map(([code, name]) => `<option value="${escapeHtml(code)}">${escapeHtml(name)}</option>`).join(''));
  }

  function populateTransferMajors() {
    const institutionCode = document.getElementById('transfer-school').value;
    const major = document.getElementById('transfer-major');
    const programs = availablePrograms.filter(item => item.institution_code === institutionCode);
    major.innerHTML = '<option value="">Choose a major</option>' + programs.map(item => `<option value="${escapeHtml(item.code)}">${escapeHtml(item.name)}${item.degree_type ? ` (${escapeHtml(item.degree_type)})` : ''}</option>`).join('');
    major.disabled = !programs.length;
  }

  function navigateToAdvisor(tool) {
    saveCurrentReferralSummary(tool === 'semester' ? 'Next-semester / degree planning' : 'General advisement question');
    window.location.href = `/current-student-advisor?tool=${encodeURIComponent(tool)}&from=structured-chatbot`;
  }

  function openTransferAnalysis() {
    const schoolCode = document.getElementById('transfer-school').value;
    const programCode = document.getElementById('transfer-major').value;
    const status = document.getElementById('transfer-intent-status');
    const program = availablePrograms.find(item => item.code === programCode && item.institution_code === schoolCode);
    if (!program) { status.textContent = 'Choose both a destination school and destination major.'; return; }
    const intent = { institution_code: schoolCode, school_name: program.institution, program_code: program.code, program_name: program.name };
    sessionStorage.setItem('transferDestinationIntentV1', JSON.stringify(intent));
    saveCurrentReferralSummary('Transfer analysis', { transfer_destination: intent });
    window.location.href = '/transfer-analysis?from=structured-chatbot';
  }

  function openMajorChange() {
    saveCurrentReferralSummary('Major change exploration');
    window.location.href = '/transfer-analysis?mode=major-change&from=structured-chatbot';
  }

  function prepareCurrentSummary() {
    saveCurrentReferralSummary('Advising session summary');
    window.location.href = '/cuny-beyond/referral?from=current-student';
  }

  function renderConfirmedCourses(targetId = 'confirmed-courses') {
    const target = document.getElementById(targetId);
    if (!target) return;
    const selected = state.transcriptCourses.filter(item => item.include !== false && item.code);
    target.innerHTML = selected.length ? `<h3>Recognized completed courses</h3><div class="recognized-course-list">${selected.map(item => `<span><strong>${escapeHtml(item.code)}</strong>${item.title ? ` · ${escapeHtml(item.title)}` : ''}</span>`).join('')}</div><p class="field-help">Please confirm these selections with an official advisor or transcript evaluation.</p>` : '';
  }

  function confirmCurrentCourses(courses, source) {
    const merged = new Map(state.transcriptCourses.filter(item => item.include !== false && item.code).map(item => [item.code, item]));
    courses.forEach(item => { if (item.code) merged.set(item.code.toUpperCase(), { ...item, code: item.code.toUpperCase(), include: true, source: item.source || source }); });
    state.transcriptCourses = [...merged.values()];
    persistCompletedCourses();
    renderConfirmedCourses();
    document.getElementById('current-course-status').textContent = `${state.transcriptCourses.length} course${state.transcriptCourses.length === 1 ? '' : 's'} recognized and saved for this advising session.`;
  }

  function renderCurrentCourseReview(courses, warnings = []) {
    const target = document.getElementById('current-course-review');
    target.innerHTML = courses.length ? `<div class="recognized-draft"><h3>Review recognized courses</h3>${courses.map((item, index) => `<label><input type="checkbox" data-current-course="${index}" checked><span><strong>${escapeHtml(item.code)}</strong> ${escapeHtml(item.title || '')}</span></label>`).join('')}<button id="confirm-current-courses" type="button">Confirm this list</button></div>` : '<p class="transcript-notice">No program courses were confidently recognized. Try course codes or use the visual selector.</p>';
    if (warnings.length) target.insertAdjacentHTML('beforeend', warnings.map(item => `<p class="transcript-notice">${escapeHtml(item)}</p>`).join(''));
    document.getElementById('confirm-current-courses')?.addEventListener('click', () => {
      const selected = courses.filter((_, index) => target.querySelector(`[data-current-course="${index}"]`)?.checked);
      confirmCurrentCourses(selected, 'reviewed intake');
      target.innerHTML = '';
    });
  }

  async function analyzeCurrentTranscript() {
    const file = document.getElementById('current-transcript-file').files[0];
    const status = document.getElementById('current-course-status');
    if (!file) { status.textContent = 'Choose a PDF, JPG, or PNG first.'; return; }
    status.textContent = 'Reading the document securely…';
    const body = new FormData(); body.append('document', file);
    try {
      const response = await fetch('/api/cuny-beyond/transcript-extract', { method: 'POST', body });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Document analysis failed');
      renderCurrentCourseReview(data.courses || [], data.warnings || []);
      status.textContent = data.disclaimer;
    } catch (err) { status.textContent = err.message; }
  }

  async function recognizeManualCourses() {
    const text = document.getElementById('manual-course-entry').value.trim();
    const status = document.getElementById('current-course-status');
    if (!text) { status.textContent = 'Enter one or more completed courses first.'; return; }
    status.textContent = 'Recognizing courses in the selected major…';
    try {
      const response = await fetch('/api/cuny-beyond/recognize-courses', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text, courses: availableProgramCourses }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Course recognition failed');
      renderCurrentCourseReview(data.courses || [], data.warnings || []);
      status.textContent = (data.courses || []).length ? 'Review the recognized list below.' : 'No program courses were confidently recognized.';
    } catch (err) { status.textContent = err.message; }
  }

  document.getElementById('current-analyze-transcript').addEventListener('click', analyzeCurrentTranscript);
  document.getElementById('recognize-manual-courses').addEventListener('click', recognizeManualCourses);
  document.getElementById('open-completed-selector').addEventListener('click', () => openPlannerModal('coursework'));
  document.getElementById('transfer-school').addEventListener('change', populateTransferMajors);
  document.getElementById('open-next-semester-plan').addEventListener('click', () => navigateToAdvisor('semester'));
  document.getElementById('open-general-advising').addEventListener('click', () => navigateToAdvisor('planner'));
  document.getElementById('open-major-change').addEventListener('click', openMajorChange);
  document.getElementById('open-transfer-analysis').addEventListener('click', openTransferAnalysis);
  document.getElementById('prepare-current-summary').addEventListener('click', prepareCurrentSummary);
  window.addEventListener('message', event => {
    if (event.origin !== window.location.origin || event.data?.type !== 'advising-completed-courses') return;
    modalSelectedCodes = Array.isArray(event.data.courses) ? event.data.courses : [];
  });

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
      const response = await fetch('/api/db/programs?selector_only=true');
      if (response.ok) {
        availablePrograms = (await response.json()).filter(item => item.has_curriculum);
        renderPopularMajors(); renderMajorResults('');
      }
    } catch (_) { document.getElementById('current-major-status').textContent = 'Program search is temporarily unavailable.'; }
    try {
      const response = await fetch('/api/db/cuny-beyond/careers');
      if (response.ok) { supportedCareers = await response.json(); renderSupportedCareers(); }
    } catch (_) { /* Typed aliases continue to work if discovery is temporarily unavailable. */ }
    try {
      const response = await fetch('/api/db/cuny-beyond/ap-equivalencies');
      if (response.ok) document.getElementById('ap-exam').innerHTML = (await response.json()).map(item => `<option value="${escapeHtml(item.exam)}">${escapeHtml(item.exam)}</option>`).join('');
    } catch (_) { document.getElementById('ap-details').hidden = true; }
    loadDraft(); restoreInputs();
    if (state.currentProgram) await selectCurrentProgram(state.currentProgram.code);
    renderConfirmedCourses(); showStep(false);
  }
  initialize();
})();
