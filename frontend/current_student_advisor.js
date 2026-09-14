(() => {
  const selected = (() => { try { return JSON.parse(sessionStorage.getItem('selectedProgramContext') || 'null'); } catch (_) { return null; } })();
  const unloaded = (() => { try { return JSON.parse(sessionStorage.getItem('unloadedProgramContext') || 'null'); } catch (_) { return null; } })();
  const intake = (() => { try { return JSON.parse(sessionStorage.getItem('narrativeAdvisingDraftV1') || 'null'); } catch (_) { return null; } })();
  const messages = document.getElementById('messages');
  const form = document.getElementById('advisor-form');
  const question = document.getElementById('advisor-question');
  const askButton = document.getElementById('ask-button');
  let program = null;
  const esc = value => String(value ?? '').replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
  const ACTIONS = {
    planner:{id:'planner',label:'Interactive degree planner',url:'/db-progress',description:'Review completed and remaining requirements.'},
    semester:{id:'semester',label:'AI degree / next-semester plan',url:'/db-progress?mode=ai-plan',description:'Build a suggested semester sequence.'},
    transfer:{id:'transfer',label:'Transfer analysis',url:'/transfer-analysis',description:'Compare programs and transfer pathways.'},
    major:{id:'major',label:'Major change',url:'/program-selector',description:'Compare another program with this major.'},
    tree:{id:'tree',label:'Interactive degree tree',url:'#degree-tree',description:'See prerequisites and course dependencies.'}
  };
  function addMessage(role,text){const div=document.createElement('div');div.className=`message ${role}`;div.textContent=text;messages.appendChild(div);div.scrollIntoView({behavior:'smooth',block:'end'});}
  function toolCard(action){return `<a class="tool-card" href="${esc(action.url)}" data-action="${esc(action.id)}"><strong>${esc(action.label)}</strong><small>${esc(action.description)}</small></a>`;}
  function renderTools(target, actions){target.innerHTML=actions.map(toolCard).join('');}
  function selectProgramContext(){sessionStorage.setItem('selectedProgramContext',JSON.stringify({institutionCode:program.institution_code,programCode:program.code,studentStatus:'current',onboardingSource:'narrative'}));}
  async function init(){
    if(!selected?.programCode && !unloaded?.current_major){location.replace('/');return;}
    if(selected?.programCode){
      const response=await fetch('/api/db/programs?selector_only=true');const programs=await response.json();
      program=programs.find(item=>item.institution_code===selected.institutionCode&&item.code===selected.programCode);
    }
    if(!program) program={code:'NOT_LOADED',name:unloaded?.current_major||intake?.current_major||'Program not loaded',degree_type:'',catalog_year:'',department:'Curriculum not loaded',institution:unloaded?.institution||intake?.institution||'Other institution',institution_code:''};
    else selectProgramContext();
    document.getElementById('program-heading').textContent=`${program.name} · ${program.catalog_year||'Current catalog'}`;
    document.getElementById('program-name').textContent=`${program.name} (${program.degree_type||'Degree'})`;
    document.getElementById('program-meta').textContent=`${program.department} · ${program.catalog_year||'Current catalog'}`;
    const availableActions=program.code==='NOT_LOADED'?[ACTIONS.transfer,ACTIONS.major]:Object.values(ACTIONS);
    renderTools(document.getElementById('all-tools'),availableActions);
    if(program.code!=='NOT_LOADED')try{const mapResponse=await fetch(`/api/db/programs/${encodeURIComponent(program.code)}/degree-map-source`);if(mapResponse.ok){const map=await mapResponse.json();const url=map.source_pdf||map.source_pdfs?.[0]?.url;if(url)document.getElementById('degree-map-link').innerHTML=`<a class="degree-map" href="${esc(url)}" target="_blank" rel="noopener">Open official degree-map PDF ↗</a>`;}}catch(_){}
  }
  document.body.addEventListener('click',event=>{const link=event.target.closest('[data-action="tree"]');if(!link)return;event.preventDefault();if(program&&program.code!=='NOT_LOADED'&&window.CurriculumGraph)window.CurriculumGraph.open(program.code,{completedCourseCodes:[]});});
  document.getElementById('question-suggestions').addEventListener('click',event=>{const button=event.target.closest('button');if(!button)return;question.value=button.textContent;question.focus();});
  form.addEventListener('submit',async event=>{
    event.preventDefault();const text=question.value.trim();if(!text||!program)return;addMessage('user',text);question.value='';askButton.disabled=true;askButton.textContent='Thinking…';
    try{const response=await fetch('/api/current-student-advisor/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_question:text,program,conversation_summary:intake?JSON.stringify({institution:intake.institution,current_major:intake.current_major,goal_type:intake.goal_type,completed_courses:intake.transcript_courses}):''})});const data=await response.json();if(!response.ok)throw new Error(data.detail||'The AI advisor is unavailable.');addMessage('assistant',data.answer||'No answer was returned.');const actions=(data.recommended_actions||[]).filter(action=>program.code!=='NOT_LOADED'||['transfer','major'].includes(action.id));renderTools(document.getElementById('recommended-tools'),actions);}catch(error){addMessage('error',error.message);}finally{askButton.disabled=false;askButton.textContent='Ask';question.focus();}
  });
  init().catch(()=>location.replace('/'));
})();
