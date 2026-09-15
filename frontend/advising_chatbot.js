(() => {
  const conversation = document.getElementById('conversation');
  const suggestions = document.getElementById('suggestions');
  const form = document.getElementById('composer');
  const input = document.getElementById('message-input');
  const send = document.getElementById('send');
  const STORAGE_KEY = 'narrativeAdvisingDraftV1';
  const state = { stage: 'identity', student_type: null, institution: null, current_major: null, selected_program: null, goal_type: null, career_goal: null, has_college_courses: null, employment: null, skills: [], transcript_courses: [], ap_exams: [], course_description: '', pending_action: null };

  const esc = value => String(value ?? '').replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
  const safeUrl = value => { try { const url = new URL(value, location.origin); return ['http:','https:'].includes(url.protocol) ? esc(url.href) : '#'; } catch (_) { return '#'; } };
  const labels = {
    current_bmcc: 'a current BMCC student', current_cuny: 'a student at another CUNY college', other_college: 'a student at another institution',
    degree_holder: 'a student who already completed a degree', working_adult: 'a working adult', high_school: 'a high-school student',
    transfer: 'transfer to another CUNY college', change_major: 'change majors', next_semester: 'plan next semester', general: 'ask a general advising question'
  };

  function addTurn(role, html) {
    const turn = document.createElement('div'); turn.className = `turn ${role}`;
    turn.innerHTML = `<div class="bubble">${html}</div>`; conversation.appendChild(turn);
    requestAnimationFrame(() => turn.scrollIntoView({behavior:'smooth', block:'center'}));
  }
  function setSuggestions(items = []) {
    suggestions.classList.remove('identity-selector');
    suggestions.innerHTML = items.map(item => `<button type="button" data-answer="${esc(item.value || item.label)}">${esc(item.label)}</button>`).join('');
  }
  function setIdentitySuggestions() {
    suggestions.classList.add('identity-selector');
    suggestions.innerHTML = `<section><strong>New students</strong><div><button type="button" data-answer="I am a high-school student">High-school student</button><button type="button" data-answer="I am a working adult and not currently a CUNY student">Working adult</button><button type="button" data-answer="I have some college coursework and want to attend BMCC">Adult with some college</button><button type="button" data-answer="I want to transfer to BMCC">Transfer to BMCC</button><button type="button" data-answer="I already have a college degree">Adult with a degree</button></div></section><section><strong>Current students</strong><div><button type="button" data-answer="I am a current BMCC student">Current BMCC student</button><button type="button" data-answer="I am a student at another CUNY college">Current CUNY student</button></div></section>`;
  }
  function ask(text, items = [], placeholder = 'Write your answer in your own words…') {
    addTurn('assistant', `<strong>AI Advisor</strong>${esc(text)}`); setSuggestions(items); input.placeholder = placeholder; input.focus();
    document.getElementById('progress-label').textContent = text.length > 48 ? `${text.slice(0, 45)}…` : text;
  }
  function save() { sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }
  function mergeFacts(facts) {
    ['student_type','institution','current_major','goal_type','career_goal','has_college_courses','employment'].forEach(key => {
      if (facts[key] !== null && facts[key] !== undefined && facts[key] !== '') state[key] = facts[key];
    });
    if (Array.isArray(facts.skills) && facts.skills.length) state.skills = facts.skills.slice(0, 5);
    save();
  }
  async function interpret(message) {
    try {
      const response = await fetch('/api/advising-chatbot/interpret', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message, stage:state.stage, context:state})});
      if (!response.ok) throw new Error(); return await response.json();
    } catch (_) { return {}; }
  }

  function nextAfterIdentity() {
    if (state.student_type === 'current_bmcc') {
      state.institution = 'BMCC';
      state.stage = 'major';
      ask('What is your current major? You can type the name or describe the program.', [], 'For example: Computer Science');
    } else if (['current_cuny','other_college','degree_holder'].includes(state.student_type) || state.has_college_courses === true) {
      state.stage = 'institution';
      ask('Which college are you attending, or where did you earn your degree or college credits?', [], 'For example: Queens College or LaGuardia Community College');
    } else {
      state.stage = 'career';
      ask('What would you like to do in your life or career? A job title, field, or problem you want to solve is enough.', [
        {label:'Data Analyst'}, {label:'Registered Nurse'}, {label:'Software Developer'}
      ], 'For example: I want to work with data and help organizations make decisions');
    }
  }
  function askGoal() {
    state.stage = 'goal';
    ask('What would you like help with today? Tell me naturally and include any details that matter.', [
      {label:'Transfer planning',value:'I want to transfer to another CUNY college'}, {label:'Change my major',value:'I want to change my major'},
      {label:'Plan next semester',value:'Help me decide what to take next semester'}, {label:'General question',value:'I have a general question for an advisor'}
    ], 'For example: I want to change from engineering to computer science');
  }

  function askCompletedCourses() {
    state.stage = 'course_check';
    ask('Have you completed any college-level or AP courses? If yes, I will help you record them before opening the next tool.', [
      {label:'Yes, I have completed courses',value:'Yes, I have completed college-level courses'},
      {label:'No completed courses',value:'No, I have not completed any college-level courses'}
    ]);
  }

  function programScore(program, query) {
    const needle = query.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
    const code = String(program.code || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
    const name = String(program.name || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
    if (!needle) return 0;
    if (needle === code || needle === name) return 100;
    if (name.includes(needle) || needle.includes(name)) return 80;
    return needle.split(' ').filter(token => token.length > 1).reduce(
      (score, token) => score + (name.includes(token) || code === token ? 12 : 0), 0
    );
  }

  async function resolveCurrentProgram(query) {
    const response = await fetch('/api/db/programs?selector_only=true');
    if (!response.ok) throw new Error('The program list is temporarily unavailable.');
    const institutionNeedle = String(state.institution || '').toLowerCase();
    const programs = (await response.json()).filter(program => {
      if (!program.has_curriculum) return false;
      if (state.student_type === 'current_bmcc') return program.institution_code === 'BMCC';
      if (!institutionNeedle) return true;
      return String(program.institution || '').toLowerCase().includes(institutionNeedle)
        || institutionNeedle.includes(String(program.institution || '').toLowerCase())
        || String(program.institution_code || '').toLowerCase() === institutionNeedle;
    });
    return programs.map(program => ({program, score:programScore(program, query)})).sort((a,b)=>b.score-a.score)[0];
  }

  function saveSelectedProgram(program) {
    state.selected_program = program; state.current_major = program.name;
    sessionStorage.setItem('selectedProgramContext', JSON.stringify({
      institutionCode:program.institution_code, programCode:program.code, studentStatus:'current', onboardingSource:'narrative'
    }));
    save();
  }

  async function showCurrentProgramCard(query) {
    try {
      const match = await resolveCurrentProgram(query);
      if (!match || match.score < 12) {
        if (state.student_type === 'current_bmcc') {
          addTurn('assistant','<span class="program-error">I could not match that to a BMCC major currently loaded in the advising database. Please type the official major name or program code.</span>');
          state.stage = 'major'; return false;
        }
        state.selected_program = null;
        sessionStorage.removeItem('selectedProgramContext');
        sessionStorage.setItem('unloadedProgramContext', JSON.stringify({institution:state.institution,current_major:state.current_major}));
        addTurn('assistant', `<section class="inline-module"><span class="program-error">${esc(state.current_major)} at ${esc(state.institution || 'that institution')} is not currently loaded in our curriculum database.</span><p>You can still upload or list completed courses and continue with general, career, or transfer guidance. The manual degree-progress selector is available only for programs loaded in the system.</p></section>`);
        return true;
      }
      const program = match.program; saveSelectedProgram(program);
      let degreeMap = null;
      try {
        const response = await fetch(`/api/db/programs/${encodeURIComponent(program.code)}/degree-map-source`);
        if (response.ok) degreeMap = await response.json();
      } catch (_) {}
      const mapUrl = degreeMap?.source_pdf || degreeMap?.source_pdfs?.[0]?.url;
      addTurn('assistant', `<section class="inline-module current-program-card"><span class="program-badge">Matched program</span><h2>${esc(program.name)} (${esc(program.degree_type || 'Degree')})</h2><p class="program-meta">${esc(program.institution)} · ${esc(program.department)} · ${esc(program.catalog_year || 'Current catalog')}</p><div class="recommendation-actions"><a href="/db-progress">Open interactive degree planner</a><button type="button" data-current-tree="${esc(program.code)}">View interactive degree tree</button>${mapUrl?`<a class="secondary" href="${safeUrl(mapUrl)}" target="_blank" rel="noopener">View degree-map PDF</a>`:''}</div></section>`);
      return true;
    } catch (error) {
      addTurn('assistant', `<span class="program-error">${esc(error.message)}</span>`); return false;
    }
  }
  function summaryText() {
    const parts = [];
    if (state.student_type) parts.push(labels[state.student_type]);
    if (state.institution) parts.push(`college: ${state.institution}`);
    if (state.current_major) parts.push(`current major: ${state.current_major}`);
    if (state.goal_type) parts.push(`goal: ${labels[state.goal_type] || state.goal_type}`);
    if (state.career_goal) parts.push(`career interest: ${state.career_goal}`);
    if (state.transcript_courses.length) parts.push(`${state.transcript_courses.length} reviewed course${state.transcript_courses.length === 1 ? '' : 's'}`);
    return parts.join('; ');
  }
  function askConfirmation(action) {
    state.pending_action = action; state.stage = 'confirm'; save();
    ask(`Before I open the next tool, I understood that you are ${summaryText() || 'exploring your options'}. Is that correct?`, [
      {label:'Yes, continue',value:'yes'}, {label:'No, start over',value:'no'}
    ], 'Type yes, or explain what I should correct');
  }
  function showRoute() {
    setSuggestions([]); form.hidden = true;
    const routes = {
      transfer: ['/transfer-analysis','Continue to transfer analysis'],
      change_major: ['/program-selector','Compare or change a major'],
      next_semester: ['/db-progress','Open completed courses and degree planning'],
      general: ['/current-student-advisor','Continue to the AI advising workspace']
    };
    const [url, label] = routes[state.goal_type] || routes.general;
    addTurn('assistant', `<section class="inline-module route-card"><h2>Your next step is ready</h2><p>I’ll carry the selected program and reviewed course snapshot into the next tool. Login is currently archived.</p><a href="${url}">${label}</a></section>`);
  }

  function showTranscript() {
    state.stage = 'course_list'; save();
    ask('Type completed courses directly below, or optionally use the transcript, AP, or manual-selection controls. The buttons are shortcuts, not required.');
    setSuggestions([]); form.hidden = false;
    const node = document.getElementById('transcript-template').content.cloneNode(true);
    conversation.appendChild(node); const module = conversation.lastElementChild; module.scrollIntoView({behavior:'smooth', block:'center'});
    setupPriorLearning(module);
    module.querySelector('.list-courses').addEventListener('click', () => chooseCourseEntry(module, 'list'));
    module.querySelector('.manual-courses').addEventListener('click', () => chooseCourseEntry(module, 'manual'));
    module.querySelector('.no-courses').addEventListener('click', () => chooseCourseEntry(module, 'none'));
    module.querySelector('.analyze-transcript').addEventListener('click', () => analyzeTranscript(module));
  }
  async function setupPriorLearning(module) {
    const apPanel=module.querySelector('.ap-selector'),exam=module.querySelector('.ap-exam');
    module.querySelectorAll('[data-prior]').forEach(button=>button.addEventListener('click',()=>{module.querySelectorAll('[data-prior]').forEach(item=>item.classList.toggle('is-selected',item===button));apPanel.hidden=button.dataset.prior!=='ap'}));
    try{const response=await fetch('/api/db/cuny-beyond/ap-equivalencies');if(response.ok){const data=await response.json();const names=[...new Set((data.exams||data||[]).map(item=>item.exam||item.name).filter(Boolean))];exam.innerHTML=names.map(name=>`<option value="${esc(name)}">${esc(name)}</option>`).join('')}}catch(_){}
    module.querySelector('.add-ap').addEventListener('click',async()=>{
      const item={exam:exam.value,score:Number(module.querySelector('.ap-score').value)};if(!item.exam)return;
      if(!state.ap_exams.some(existing=>existing.exam===item.exam))state.ap_exams.push(item);save();
      module.querySelector('.ap-list').innerHTML=state.ap_exams.map(entry=>`<span>${esc(entry.exam)} · score ${entry.score}</span>`).join('');
      try{const response=await fetch('/api/db/cuny-beyond/ap-equivalencies',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({exams:state.ap_exams})});if(response.ok){const data=await response.json();const apCourses=(data.results||[]).filter(result=>result.bmcc_equivalency&&!result.bmcc_equivalency.includes(' or ')).map(result=>({code:result.bmcc_equivalency,title:`${result.exam} score ${result.score}`,credits:result.estimated_credits,source:'AP planning estimate',include:true}));state.transcript_courses=[...state.transcript_courses.filter(course=>course.source!=='AP planning estimate'),...apCourses];persistImportedCourses(state.transcript_courses,'ap-and-coursework');save()}}catch(_){}
      let continueButton=module.querySelector('.use-ap');if(!continueButton){continueButton=document.createElement('button');continueButton.type='button';continueButton.className='use-ap';continueButton.textContent='Use AP estimates and continue';module.querySelector('.ap-selector').appendChild(continueButton);continueButton.addEventListener('click',()=>{persistImportedCourses(state.transcript_courses,'ap-and-coursework');module.querySelectorAll('button,input,select').forEach(element=>element.disabled=true);askConfirmation(state.goal_type==='general'?'workspace':'route')})}
    });
  }
  async function analyzeTranscript(module) {
    const file = module.querySelector('.transcript-file').files[0]; const status = module.querySelector('.transcript-status');
    if (!file) { status.textContent = 'Choose a PDF, JPG, or PNG first.'; return; }
    status.textContent = 'Reading the document…';
    try {
      const body = new FormData(); body.append('document', file);
      const response = await fetch('/api/cuny-beyond/transcript-extract', {method:'POST', body});
      const data = await response.json(); if (!response.ok) throw new Error(data.detail || 'Transcript analysis failed');
      state.transcript_courses = (data.courses || []).map(course => ({...course, include:true})); save();
      module.querySelector('.transcript-results').innerHTML = state.transcript_courses.length ? `<table class="transcript-table"><thead><tr><th>Use</th><th>Course</th><th>Title</th><th>Credits</th></tr></thead><tbody>${state.transcript_courses.map((c,i) => `<tr><td><input type="checkbox" data-course="${i}" checked aria-label="Use ${esc(c.code)}"></td><td>${esc(c.code)}</td><td>${esc(c.title)}</td><td>${esc(c.credits ?? '—')}</td></tr>`).join('')}</tbody></table>` : '<p>No clearly completed courses were found. You can continue without them.</p>';
      status.textContent = data.disclaimer || 'Review every row before continuing.';
      let useButton = module.querySelector('.use-transcript');
      if (!useButton) {
        useButton = document.createElement('button'); useButton.type='button'; useButton.className='use-transcript';
        module.querySelector('.module-actions').prepend(useButton);
        useButton.addEventListener('click', () => finishTranscript(module));
      }
      useButton.textContent = 'Use reviewed list and continue';
    } catch (error) { status.textContent = error.message; }
  }
  function finishTranscript(module) {
    module.querySelectorAll('[data-course]').forEach(box => state.transcript_courses[Number(box.dataset.course)].include = box.checked);
    const selected = state.transcript_courses.filter(course => course.include && course.code);
    persistImportedCourses(selected, 'transcript');
    form.hidden = false; module.querySelectorAll('button,input').forEach(element => element.disabled = true);
    askConfirmation(state.goal_type === 'general' ? 'workspace' : 'route');
  }
  function persistImportedCourses(courses, recognitionSource) {
    const institution = state.selected_program?.institution || state.institution || '';
    const imported = courses.map(course => ({...course, institution:course.institution || institution, recognition_source:recognitionSource, include:true}));
    sessionStorage.setItem('cunyBeyondImportedCoursesV1', JSON.stringify(imported));
    sessionStorage.setItem('transferSnapshot', JSON.stringify({completed_courses:imported.map(item=>item.code),completed_course_details:imported,source:`narrative-${recognitionSource}-import`,timestamp:new Date().toISOString()}));
  }
  async function resolveTypedCourses(message) {
    const codes = message.toUpperCase().match(/\b[A-Z]{2,4}\s*\d{2,4}(?:\.\d)?\b/g) || [];
    const resolved = new Map(codes.map(code => {
      const normalized=code.replace(/\s+/g,' ');return [normalized,{code:normalized,title:'Student-entered course',include:true}];
    }));
    if (state.selected_program) {
      try {
        const response=await fetch(`/api/db/programs/${encodeURIComponent(state.selected_program.code)}/requirements`);
        if(response.ok){const data=await response.json();const normalizedMessage=message.toLowerCase().replace(/[^a-z0-9]+/g,' ');(data.groups||[]).flatMap(group=>group.courses||[]).forEach(course=>{const title=String(course.title||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();if(title.length>5&&normalizedMessage.includes(title))resolved.set(course.code,{code:course.code,title:course.title,include:true});});}
      } catch (_) {}
    }
    return [...resolved.values()];
  }
  function chooseCourseEntry(module, mode) {
    if (mode === 'manual') {
      if (state.selected_program) {
        form.hidden=true; module.querySelectorAll('button,input').forEach(element=>element.disabled=true);
        const wrapper=document.createElement('section');wrapper.className='inline-module manual-selector';
        wrapper.innerHTML='<h2>Manual completed-course selector</h2><p>Select completed courses below. When finished, return here and continue.</p><iframe src="/db-progress?embedded=course-intake" title="Manual completed-course selector"></iframe><button type="button">I finished selecting courses</button>';
        conversation.appendChild(wrapper);wrapper.scrollIntoView({behavior:'smooth',block:'center'});
        wrapper.querySelector('button').addEventListener('click',()=>{wrapper.querySelector('iframe').remove();wrapper.querySelector('button').disabled=true;form.hidden=false;askConfirmation(state.goal_type==='general'?'workspace':'route');});
        return;
      }
      module.querySelector('.transcript-status').textContent = 'That program is not loaded, so the program-specific manual selector is unavailable. Please list courses here or upload a transcript.';
      return;
    }
    form.hidden = false;
    module.querySelectorAll('button,input').forEach(element => element.disabled = true);
    if (mode === 'none') {
      state.has_college_courses = false; state.transcript_courses = []; save();
      askConfirmation(state.goal_type === 'general' ? 'workspace' : 'route'); return;
    }
    state.stage='course_list';
    ask('List the completed course codes or names in one message. Separate them with commas—for example: ENG 101, MAT 206, CSC 101.', [], 'ENG 101, MAT 206, CSC 101');
  }

  async function showRecommendations() {
    setSuggestions([]); form.hidden = true;
    const fragment = document.getElementById('recommendations-template').content.cloneNode(true); conversation.appendChild(fragment);
    const module = conversation.lastElementChild; const status = module.querySelector('.recommendation-status'); const results = module.querySelector('.recommendation-results');
    try {
      const response = await fetch('/api/db/cuny-beyond/recommendations', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({career_goal:state.career_goal,skills:state.skills})});
      const data = await response.json(); if (!response.ok) throw new Error('Recommendation service is unavailable.');
      status.textContent = data.matched_career ? `Matched to the reviewed ${data.matched_career.name} profile.` : (data.message || 'No reviewed match yet.');
      results.innerHTML = (data.recommendations || []).map(item => {
        const mapUrl = item.degree_map?.source_pdf || item.degree_map?.source_pdfs?.[0]?.url;
        return `<article class="recommendation-card"><h3>${esc(item.program_name)} (${esc(item.degree_type || 'Degree')})</h3><p>${esc(item.explanation)}</p><div class="recommendation-actions"><a href="/db-progress">Open interactive degree planner</a>${mapUrl ? `<a class="secondary" href="${safeUrl(mapUrl)}" target="_blank" rel="noopener">View degree-map PDF</a>`:''}<a class="secondary" href="${safeUrl(item.official_program_url)}" target="_blank" rel="noopener">Official program page</a></div></article>`;
      }).join('') || `<p>Try a reviewed title such as Data Analyst, Registered Nurse, or Software Developer, or continue in the <a href="/cuny-beyond">full advising intake</a>.</p>`;
    } catch (error) { status.textContent = error.message; }
    module.scrollIntoView({behavior:'smooth', block:'center'});
  }

  async function handleMessage(message) {
    addTurn('user', esc(message)); setSuggestions([]); send.disabled = true;
    const facts = await interpret(message); mergeFacts(facts); send.disabled = false;
    if (state.stage === 'identity') {
      if (!state.student_type) { ask('I did not want to guess. Are you currently at BMCC, at another CUNY/college, in high school, or returning as a working adult?', [{label:'Current BMCC student'},{label:'Another CUNY student'},{label:'High-school student'},{label:'Working adult'}]); return; }
      nextAfterIdentity();
    } else if (state.stage === 'institution') {
      if (!state.institution) state.institution = message;
      state.stage='major';
      ask('What major or degree are you pursuing, or what degree did you complete?', [], 'For example: Computer Science B.S.');
    } else if (state.stage === 'major') {
      if (!state.current_major) state.current_major = message;
      if (!(await showCurrentProgramCard(state.current_major))) return;
      askGoal();
    }
    else if (state.stage === 'goal') {
      if (!state.goal_type) { ask('Would you like help with transferring, changing your major, planning next semester, or a general advising question?', [{label:'Transfer planning'},{label:'Change my major'},{label:'Plan next semester'},{label:'General question'}]); return; }
      askCompletedCourses();
    } else if (state.stage === 'course_check') {
      if (state.has_college_courses === true || /^(yes|i have|completed)/i.test(message.trim())) {
        state.has_college_courses = true; showTranscript();
      } else if (state.has_college_courses === false || /^(no|none|not yet)/i.test(message.trim())) {
        state.has_college_courses = false; askConfirmation(state.goal_type === 'general' ? 'workspace' : 'route');
      } else {
        ask('Please tell me whether you have completed any college-level or AP courses.', [{label:'Yes'},{label:'No'}]);
      }
    } else if (state.stage === 'course_list') {
      state.course_description = message;
      state.transcript_courses = await resolveTypedCourses(message);
      persistImportedCourses(state.transcript_courses, 'chat-entered');
      save();
      addTurn('assistant', state.transcript_courses.length ? `I recorded ${state.transcript_courses.map(course=>esc(course.code)).join(', ')} for review.` : 'I saved your course description for the advisor, but I could not identify standardized course codes. The next tool will require manual review.');
      askConfirmation(state.goal_type === 'general' ? 'workspace' : 'route');
    } else if (state.stage === 'career') {
      if (!state.career_goal) state.career_goal = message; state.stage = 'skills';
      ask('What skills do you already use or want to build? A sentence is fine; I will extract up to five.', [{label:'Analyze data and solve problems'},{label:'Help people and communicate clearly'},{label:'Build software and learn technology'}]);
    } else if (state.stage === 'skills') { if (!state.skills.length) state.skills = message.split(/,|\band\b/i).map(x=>x.trim()).filter(Boolean).slice(0,5); askConfirmation('recommend'); }
    else if (state.stage === 'confirm') {
      if (/^(no|not|incorrect|start over)/i.test(message.trim())) { restart(); return; }
      if (!/^(yes|correct|right|continue|ok|okay)/i.test(message.trim())) { askConfirmation(state.pending_action); return; }
      if (state.pending_action === 'recommend') showRecommendations();
      else if (state.pending_action === 'workspace') location.href = '/current-student-advisor';
      else showRoute();
    }
  }

  function restart() {
    sessionStorage.removeItem(STORAGE_KEY); sessionStorage.removeItem('unloadedProgramContext'); sessionStorage.removeItem('cunyBeyondImportedCoursesV1'); Object.assign(state,{stage:'identity',student_type:null,institution:null,current_major:null,selected_program:null,goal_type:null,career_goal:null,has_college_courses:null,employment:null,skills:[],transcript_courses:[],ap_exams:[],course_description:'',pending_action:null});
    conversation.innerHTML=''; form.hidden=false; ask('Tell me where you are in your education right now. You can answer naturally.', [], 'For example: I am at BMCC studying computer science');setIdentitySuggestions();
  }
  form.addEventListener('submit', event => { event.preventDefault(); const message=input.value.trim(); if(!message)return; input.value=''; handleMessage(message); });
  input.addEventListener('keydown', event => { if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();form.requestSubmit();} });
  suggestions.addEventListener('click', event => { const button=event.target.closest('[data-answer]'); if(!button)return; input.value=button.dataset.answer; form.requestSubmit(); });
  conversation.addEventListener('click', event => {
    const tree = event.target.closest('[data-current-tree]');
    if (tree && window.CurriculumGraph) window.CurriculumGraph.open(tree.dataset.currentTree, {completedCourseCodes:[]});
  });
  document.getElementById('restart').addEventListener('click', restart);
  restart();
})();
