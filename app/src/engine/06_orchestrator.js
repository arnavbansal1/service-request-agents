/* ================= 6. Orchestrator ================= */
function transition(R,task,to,why,parent){
  const from=task.state;const ok=(TRANSITIONS[from]||[]).includes(to);
  if(!ok){R.stats.invalid++;event(R.T,`invalid transition ${from} → ${to}`,"state",{"task.id":task.id,"state.from":from,"state.to":to},parent,"error");
    if(from!=="escalated_advisor"&&(TRANSITIONS[from]||[]).includes("escalated_advisor")){task.state="escalated_advisor";task.reason="Invalid transition blocked; failed closed";task.history.push({from,to:"escalated_advisor",why:task.reason})}return false}
  task.history.push({from,to,why:why||""});task.state=to;if(TERMINAL.has(to)||to==="awaiting_approval")task.reason=why||task.reason;
  event(R.T,`state ${from} → ${to}`,"state",{"task.id":task.id,"state.from":from,"state.to":to,"reason":why||""},parent);return true}
function validateIntake(out,email){
  const probs=[];const reqs=Array.isArray(out&&out.requests)?out.requests:(probs.push("requests is not a list"),[]);
  const tasks=reqs.map((r,i)=>{const type=TYPES[r&&r.type]?r.type:"other";if(!TYPES[r&&r.type])probs.push(`request ${i+1}: unknown type "${r&&r.type}" → other`);
    const quote=String(r&&r.quote||"");const qok=!!quote&&norm(email.body).includes(norm(quote));if(!qok)probs.push(`request ${i+1}: quote not found in email`);
    const d=(r&&r.details)||{};return{type,proposedRoute:ROUTES[r&&r.route]?r.route:null,summary:String(r&&r.summary||TYPES[type]),urgency:r&&r.urgency==="urgent"?"urgent":"normal",quote,quoteOk:qok,details:{holder_name:d.holder_name||null,holder_address:d.holder_address||null,wording_requested:(Array.isArray(d.wording_requested)?d.wording_requested:[]).map(String),line:d.line||null,question:d.question||null},missing:Array.isArray(r&&r.missing_info)?r.missing_info.map(String):[]}});
  return{tasks,probs}}
function makeTask(R,email,t,source){const n=R.tasks.filter(x=>x.email===email.id).length+1;const task={id:`${email.id}-T${n}`,email:email.id,...t,source,state:"received",history:[],gates:[],records:{},draft:null,qa:null,reason:"",decision:null};R.tasks.push(task);event(R.T,`task created: ${TYPES[task.type]}`,"state",{"task.id":task.id,"task.type":task.type,"task.source":source},R.emailSpan[email.id]);
  task.route=policyRoute(task.type);
  if(source==="intake agent"){const pr=task.proposedRoute;task.planOk=pr===task.route;if(!task.planOk)R.stats.overrides++;
    event(R.T,`plan check ${task.id}: agent proposed ${pr?ROUTES[pr]:"no route"} · policy says ${ROUTES[task.route]} → ${task.planOk?"accepted":"overridden by code"}`,"gate",{"gate.name":"plan_check","gate.result":task.planOk?"accepted":"overridden","task.id":task.id,"plan.proposed":pr||"none","plan.enforced":task.route},R.emailSpan[email.id],task.planOk?"ok":"error")}
  return task}
async function processEmail(R,email){
  const root=startSpan(R.T,`invoke_workflow service_request ${email.id}`,"workflow",{"gen_ai.operation.name":"invoke_workflow","email.id":email.id,"email.from":email.from},null);R.emailSpan[email.id]=root;
  const fp=hash(norm(email.from)+"|"+norm(email.subject)+"|"+norm(email.body));
  if(R.seen[fp]){email.duplicate_of=R.seen[fp];event(R.T,`dedupe: duplicate of ${R.seen[fp]} · no new tasks, no actions`,"guard",{"idempotency.key":fp,"duplicate_of":R.seen[fp]},root);R.stats.duplicates++;endSpan(R.T,root,"ok");return}
  R.seen[fp]=email.id;email.fingerprint=fp;
  if(INJECTION_RE.test(email.body)){email.injection=(email.body.match(INJECTION_RE)||[""])[0];event(R.T,`guard: instruction in client text ("${email.injection}") · logged, no effect on permissions or workflow`,"guard",{"guard":"prompt_injection","permissions.changed":0},root)}
  let intake=null;
  try{intake=await callAgent(R,"intake",`intake:${email.id}`,email,root)}catch(e){makeTask(R,email,{type:"other",summary:"Intake failed: whole email to a person",urgency:"normal",quote:"",quoteOk:false,details:{},missing:[]},"rule: intake failure");}
  if(intake){const v=validateIntake(intake,email);v.probs.forEach(p=>event(R.T,`validation: ${p}`,"gate",{"task.email":email.id},root,"error"));R.stats.validation+=v.probs.length;
    v.tasks.forEach(t=>makeTask(R,email,t,"intake agent"))}
  /* Backstop runs whether or not the orchestrator agent succeeded (found by the rate-limit chaos run) */
  if(INCIDENT_RE.test(email.body)&&!R.tasks.some(x=>x.email===email.id&&x.type==="claim")){const m=email.body.match(INCIDENT_RE)[0];makeTask(R,email,{type:"claim",summary:`Possible incident in email ("${m}"), missed by the orchestrator agent`,urgency:"urgent",quote:m,quoteOk:true,details:{},missing:[]},"rule: incident backstop")}
  const mine=R.tasks.filter(x=>x.email===email.id);
  /* claims first, then everything else */
  mine.sort((a,b)=>(a.type==="claim"?0:1)-(b.type==="claim"?0:1));
  for(const task of mine)await runTask(R,email,task,root);
  endSpan(R.T,root,"ok");
}
async function runTask(R,email,task,root){
  const ts=startSpan(R.T,`task ${task.id} · ${TYPES[task.type]}`,"workflow",{"task.id":task.id,"task.type":task.type},root);
  try{
    transition(R,task,"triaged","Typed and prioritized",ts);
    if(task.type==="claim"){event(R.T,"gate claim_escalation: possible claim → escalate immediately","gate",{"gate.name":"claim_escalation","gate.result":"escalate"},ts);transition(R,task,"escalated_urgent","Possible claim: escalated immediately to the claims advisor, ahead of other tasks",ts);return}
    if(!AGENT_LANES.has(task.type)){transition(R,task,"routed_human",`Outside the agent lanes: routed to ${ROUTE_TO[task.type]||"a person"}`,ts);return}
    if(R.killed())throw Object.assign(new Error("Kill switch"),{code:"kill_switch"});
    transition(R,task,"context","Context agent choosing lookups",ts);
    const plan=await callAgent(R,"context",`context:${task.id}`,{task:{type:task.type,summary:task.summary,details:task.details},from:email.from},ts);
    const calls=(Array.isArray(plan&&plan.tool_calls)?plan.tool_calls:[]).slice(0,POLICY.context.maxCalls+2);
    let n=0;for(const c of calls){if(n>=POLICY.context.maxCalls){event(R.T,"tool budget exceeded: extra calls refused","guard",{"task.id":task.id},ts,"error");break}n++;
      const args={...(c&&c.args||{})};if(args.client_email&&norm(args.client_email)!==norm(email.from)){event(R.T,`guard: lookup for another client (${args.client_email}) refused`,"guard",{"task.id":task.id},ts,"error");continue}
      const r=await execTool(R,"context",String(c&&c.tool),args,ts);
      if(r.timeout){transition(R,task,"escalated_advisor",`Lookup ${c.tool} timed out ${RETRY.maxAttempts} times: escalated instead of acting on partial context`,ts);task.reasonCode="tool_timeout";return}
      if(r.ok&&r.record_id)task.records[r.record_id]=r.data}
    transition(R,task,"drafted","Fulfillment agent drafted next step",ts);
    task.draft=await callAgent(R,"fulfillment",`fulfillment:${task.id}`,{task:{type:task.type,summary:task.summary,details:task.details},records:task.records},ts);
    /* LLM judge: workflow engine re-fetches source records under QA's own permissions */
    transition(R,task,"qa","LLM judge reviews with its own evidence",ts);
    /* v2: re-fetch from source every record the draft cites (plus the primary policy and holder), never reuse the drafter's copies */
    const qaRecords={};const cites=new Set((task.draft&&task.draft.citations)||[]);const lines=new Set([primaryLine(task)]);
    Object.entries(task.records).forEach(([id,r])=>{if(cites.has(id)&&r&&r.line)lines.add(r.line)});
    const fetches=[];if([...cites].some(c=>c.startsWith("account:")))fetches.push(["get_account",{client_email:email.from}]);
    lines.forEach(l=>fetches.push(["get_policy",{client_email:email.from,line:l}]));
    if(task.type==="coi"&&task.details.holder_name)fetches.push(["get_holder_requirements",{holder_name:task.details.holder_name}]);
    for(const [tool,args] of fetches){const r=await execTool(R,"qa",tool,args,ts);
      if(r.timeout){transition(R,task,"escalated_advisor","Judge lookup timed out: escalated",ts);task.reasonCode="tool_timeout";return}
      if(r.ok&&r.record_id)qaRecords[r.record_id]=r.data}
    task.qaRecords=qaRecords;
    task.qa=await callAgent(R,"qa",`qa:${task.id}`,{request:{type:task.type,quote:task.quote,details:task.details},draft:task.draft,records:qaRecords},ts);
    transition(R,task,"gated","Deterministic safety gates",ts);
    const gates=runGates(R,email,task);task.gates=gates;
    gates.forEach(g=>event(R.T,`gate ${g.name}: ${g.pass?"pass":"FAIL"}`,"gate",{"gate.name":g.name,"gate.result":g.pass?"pass":"fail","gate.detail":g.detail},ts,g.pass?"ok":"error"));
    const failed=gates.filter(g=>!g.pass);
    if(!failed.length){transition(R,task,"awaiting_approval","All gates passed: a person must approve before anything is sent",ts);return}
    if(failed.every(g=>g.name==="evidence_complete")&&task.type==="coi"){transition(R,task,"needs_info","Missing required details: client request drafted for approval",ts);return}
    transition(R,task,"escalated_advisor",`Failed gates: ${failed.map(g=>g.label).join(", ")}`,ts);task.reasonCode=failed[0].name;
  }catch(e){const code=e&&e.code||"error";event(R.T,`error: ${e&&e.message||e}`,"state",{"error.type":code,"task.id":task.id},ts,"error");
    if(!END_STATES.has(task.state)){const to="escalated_advisor";if((TRANSITIONS[task.state]||[]).includes(to))transition(R,task,to,code==="kill_switch"?"Kill switch on: handed to a person":"Agent failure: failed closed to a person",ts);else{task.history.push({from:task.state,to,why:"forced close"});task.state=to;task.reason="Failed closed"}}}
  finally{endSpan(R.T,ts,"ok")}
}
