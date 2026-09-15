(() => {
  const selected=(()=>{try{return JSON.parse(sessionStorage.getItem('selectedProgramContext')||'null')}catch(_){return null}})();
  const unloaded=(()=>{try{return JSON.parse(sessionStorage.getItem('unloadedProgramContext')||'null')}catch(_){return null}})();
  const intake=(()=>{try{return JSON.parse(sessionStorage.getItem('narrativeAdvisingDraftV1')||'null')}catch(_){return null}})();
  const messages=document.getElementById('messages'),form=document.getElementById('advisor-form'),question=document.getElementById('advisor-question'),askButton=document.getElementById('ask-button');
  let program=null,activeAction=null;
  const esc=value=>String(value??'').replace(/[&<>'"]/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
  const ACTIONS={
    planner:{id:'planner',label:'Degree progress',mode:'Degree progress',url:'/db-progress?embedded=workspace',description:'Completed and remaining requirements'},
    semester:{id:'semester',label:'Next semester',mode:'Next-semester AI advisement',url:'/db-progress?embedded=workspace&mode=ai-plan',description:'AI-supported semester planning'},
    transfer:{id:'transfer',label:'Transfer',mode:'Transfer analysis',url:'/transfer-analysis?embedded=workspace',description:'Program and transfer comparison'},
    major:{id:'major',label:'Major change',mode:'Major-change comparison',url:'/program-selector?embedded=workspace',description:'Explore another curriculum'},
    tree:{id:'tree',label:'Degree tree',mode:'Prerequisite degree-tree',url:'#degree-tree',description:'Prerequisites and dependencies'}
  };
  function addMessage(role,text){const div=document.createElement('div');div.className=`message ${role}`;div.textContent=text;messages.appendChild(div);div.scrollIntoView({behavior:'smooth',block:'end'})}
  function selectProgramContext(){sessionStorage.setItem('selectedProgramContext',JSON.stringify({institutionCode:program.institution_code,programCode:program.code,studentStatus:'current',onboardingSource:'narrative'}))}
  function actionFor(raw){return ACTIONS[raw?.id]||ACTIONS.planner}
  function renderTabs(actions){document.getElementById('all-tools').innerHTML=actions.map(action=>`<button type="button" class="tool-tab" data-action="${esc(action.id)}" aria-selected="false" title="${esc(action.description)}">${esc(action.label)}</button>`).join('')}
  function setMode(action){activeAction=action;document.getElementById('tool-mode').textContent=`${action.mode} is active`;document.querySelectorAll('.tool-tab').forEach(tab=>tab.setAttribute('aria-selected',String(tab.dataset.action===action.id)))}
  function completedCourseCodes(){try{return JSON.parse(sessionStorage.getItem('cunyBeyondImportedCoursesV1')||'[]').map(item=>item.code).filter(Boolean)}catch(_){return[]}}
  function openTool(actionId){
    const action=actionFor({id:actionId});setMode(action);const stage=document.getElementById('tool-stage');
    if(action.id==='tree'){stage.innerHTML='<div class="tree-launch"><strong>Interactive degree tree</strong><p>Open the prerequisite and course-dependency visualization while keeping this advising conversation available.</p><button type="button" id="launch-tree">Open degree tree</button></div>';document.getElementById('launch-tree').onclick=()=>window.CurriculumGraph?.open(program.code,{completedCourseCodes:completedCourseCodes()});return}
    stage.innerHTML='<iframe id="tool-frame" title="Embedded advising tool"></iframe>';const frame=document.getElementById('tool-frame');frame.title=action.label;frame.src=action.url;
  }
  function openExpanded(){
    if(!activeAction)return;if(activeAction.id==='tree'){window.CurriculumGraph?.open(program.code,{completedCourseCodes:completedCourseCodes()});return}
    const modal=document.getElementById('tool-modal');document.getElementById('tool-modal-title').textContent=activeAction.label;document.getElementById('tool-modal-frame').src=activeAction.url;modal.hidden=false;document.body.style.overflow='hidden';document.getElementById('close-tool').focus()
  }
  function closeExpanded(){const modal=document.getElementById('tool-modal');modal.hidden=true;document.getElementById('tool-modal-frame').src='about:blank';document.body.style.overflow='';document.getElementById('expand-tool').focus()}
  function recommendActions(actions){const target=document.getElementById('recommended-tools');target.innerHTML=actions.length?`Suggested: ${actions.map(item=>`<button type="button" data-recommended="${esc(item.id)}">${esc(actionFor(item).label)}</button>`).join('')}`:''}
  async function init(){
    if(!selected?.programCode&&!unloaded?.current_major){location.replace('/');return}
    if(selected?.programCode){const response=await fetch('/api/db/programs?selector_only=true'),programs=await response.json();program=programs.find(item=>item.institution_code===selected.institutionCode&&item.code===selected.programCode)}
    if(!program)program={code:'NOT_LOADED',name:unloaded?.current_major||intake?.current_major||'Program not loaded',degree_type:'',catalog_year:'',department:'Curriculum not loaded',institution:unloaded?.institution||intake?.institution||'Other institution',institution_code:''};else selectProgramContext();
    document.getElementById('program-heading').textContent=`${program.name} · ${program.catalog_year||'Current catalog'}`;document.getElementById('program-name').textContent=`${program.name} (${program.degree_type||'Degree'})`;document.getElementById('program-meta').textContent=`${program.department} · ${program.catalog_year||'Current catalog'}`;
    const available=program.code==='NOT_LOADED'?[ACTIONS.transfer,ACTIONS.major]:Object.values(ACTIONS);renderTabs(available);openTool(available[0].id);
    if(program.code!=='NOT_LOADED')try{const response=await fetch(`/api/db/programs/${encodeURIComponent(program.code)}/degree-map-source`);if(response.ok){const map=await response.json(),url=map.source_pdf||map.source_pdfs?.[0]?.url;if(url)document.getElementById('degree-map-link').innerHTML=`<a class="degree-map" href="${esc(url)}" target="_blank" rel="noopener">Official PDF ↗</a>`}}catch(_){}
  }
  document.getElementById('all-tools').addEventListener('click',event=>{const button=event.target.closest('[data-action]');if(button)openTool(button.dataset.action)});
  document.getElementById('recommended-tools').addEventListener('click',event=>{const button=event.target.closest('[data-recommended]');if(button)openTool(button.dataset.recommended)});
  document.getElementById('expand-tool').addEventListener('click',openExpanded);document.getElementById('close-tool').addEventListener('click',closeExpanded);document.querySelector('[data-close-tool]').addEventListener('click',closeExpanded);document.addEventListener('keydown',event=>{if(event.key==='Escape'&&!document.getElementById('tool-modal').hidden)closeExpanded()});
  document.getElementById('question-suggestions').addEventListener('click',event=>{const button=event.target.closest('button');if(!button)return;question.value=button.textContent;question.focus()});
  form.addEventListener('submit',async event=>{
    event.preventDefault();const text=question.value.trim();if(!text||!program)return;addMessage('user',text);question.value='';askButton.disabled=true;askButton.textContent='Thinking…';
    try{const response=await fetch('/api/current-student-advisor/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_question:text,program,active_tool:{...activeAction,completed_courses:completedCourseCodes()},conversation_summary:intake?JSON.stringify({institution:intake.institution,current_major:intake.current_major,goal_type:intake.goal_type,completed_courses:intake.transcript_courses}):''})}),data=await response.json();if(!response.ok)throw new Error(data.detail||'The AI advisor is unavailable.');addMessage('assistant',data.answer||'No answer was returned.');const actions=(data.recommended_actions||[]).filter(action=>program.code!=='NOT_LOADED'||['transfer','major'].includes(action.id));recommendActions(actions)}catch(error){addMessage('error',error.message)}finally{askButton.disabled=false;askButton.textContent='Ask';question.focus()}
  });
  init().catch(()=>location.replace('/'));
})();
