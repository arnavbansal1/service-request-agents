/* ================= 8. Run control ================= */
const state={ds:location.hash==="#blind"?"blind":"demo",mode:"saved",R:null,sel:null,selTask:null,killed:false,persistFault:false,sample:null,db:undefined,runs:{demo:[],blind:[]},outage:false,busy:false,view:"tree",tour:null,selSpan:null,layer:"both"};
function newRun(){const ds=INBOX[state.ds];const faults=JSON.parse(JSON.stringify(state.persistFault&&state.ds==="blind"?EXPECTED.variant_persistent_timeout.faults:ds.faults||{}));
  return{ds:state.ds,mode:state.mode,T:newTrace(),tasks:[],emails:JSON.parse(JSON.stringify(ds.emails)),seen:{},faults,emailSpan:{},raw:[],saved:state.mode==="saved"?SAVED[state.ds]:null,sample:state.sample,killed:()=>state.killed,outage:state.outage&&state.ds==="blind"?new Set(["intake"]):null,stats:{overrides:0,denied:0,timeouts:0,retries:0,duplicates:0,invalid:0,validation:0,sends:0},sent:{},startedAt:new Date()}}
async function runInbox(opts){opts=opts||{};if(state.busy)return;state.busy=true;renderControls();
  const R=opts.R||newRun();state.R=R;setStatus(`${R.mode==="live"?"Live Claude":"Saved run"}: processing ${R.emails.length} emails…`);
  const t0=performance.now();
  try{for(const e of R.emails){await processEmail(R,e);renderAll()}}
  finally{R.ms=Math.round(performance.now()-t0);state.busy=false}
  R.check=conservation(R);R.score=state.ds==="blind"&&!R.outage?scoreBlind(R):null;
  if(R.outage){const c=R.tasks.find(t=>t.type==="claim");R.drill={claim:!!c&&c.state==="escalated_urgent"&&/backstop/.test(c.source),sends:R.stats.sends,ended:R.check.ok,retries:R.T.spans.filter(x=>/rate limited/.test(x.name)).length}}
  state.runs[state.ds].push({n:state.runs[state.ds].length+1,mode:R.mode,ms:R.ms,score:R.score,cons:R.check,dispositions:Object.fromEntries(R.tasks.map(t=>[t.type+"@"+t.email,t.state])),fault:state.persistFault,drill:!!R.outage,recorded:R.mode==="saved"&&R.ds==="blind"});
  if(!state.sel&&R.emails[0])state.sel=R.emails[0].id;
  if(R.mode==="saved"&&R.ds==="blind"&&!R.outage)setStatus("Done · replayed the recorded live Claude run (Nov 15, 20:09). Live mode is under Advanced.");else setStatus(`Done in ${(R.ms/1000).toFixed(1)}s · ${R.tasks.length} tasks · ${R.check.ok?"every task in exactly one valid end state":"TASK CONSERVATION FAILED"}`,!R.check.ok);
  if(R.mode==="live"&&!R.outage)await persistRun(R);renderAll();return R}
function conservation(R){const problems=[];R.tasks.forEach(t=>{if(!END_STATES.has(t.state))problems.push(`${t.id} stuck in ${t.state}`);let cur="received";t.history.forEach(h=>{if(h.from!==cur)problems.push(`${t.id} history break at ${h.from}`);cur=h.to});if(cur!==t.state)problems.push(`${t.id} history doesn't end at its state`)});
  const ids=new Set(R.tasks.map(t=>t.id));return{ok:problems.length===0&&R.stats.invalid===0&&ids.size===R.tasks.length,problems,total:R.tasks.length,ended:R.tasks.filter(t=>END_STATES.has(t.state)).length,invalid:R.stats.invalid}}
function approve(task,yes){const R=state.R;const root=R.emailSpan[task.email];
  if(task.state!=="awaiting_approval"){event(R.T,`approve ignored: ${task.id} is ${task.state}`,"human",{"task.id":task.id},root,"error");renderAll();return}
  if(!yes){task.decision={by:"risk advisor",action:"rejected",at:new Date()};event(R.T,`human: rejected ${task.id}`,"human",{"task.id":task.id},root);transition(R,task,"escalated_advisor","Rejected by a person",root);renderAll();return}
  const key=`${task.id}:${hash(JSON.stringify(task.draft))}`;task.decision={by:"risk advisor",action:"approved",at:new Date()};
  event(R.T,`human: approved ${task.id}`,"human",{"task.id":task.id},root);
  if(R.sent[key]){event(R.T,`record_send skipped: idempotency key already used`,"guard",{"idempotency.key":key},root);renderAll();return}
  R.sent[key]=true;R.stats.sends++;event(R.T,`record_send ${task.type==="coi"?"certificate":"reply"} → ${task.type==="coi"?task.draft.coi.holder_name+" and client":"client"} (simulated)`,"tool",{"gen_ai.operation.name":"execute_tool","gen_ai.tool.name":"record_send","gen_ai.agent.name":"workflow_engine","idempotency.key":key},root);
  transition(R,task,"sent","Approved by a person; sent once",root);renderAll()}
async function getDb(){if(state.db!==undefined)return state.db;try{state.db=window.claude?await window.claude.use("db"):null}catch(e){state.db=null}return state.db}
async function persistRun(R){const db=await getDb();if(!db)return;try{await db.collection("runs").doc(`${R.ds}-${Date.now()}`).set({dataset:R.ds,at:new Date().toISOString(),ms:R.ms,fault:state.persistFault,score:R.score||null,conservation:R.check,stats:R.stats,tasks:R.tasks.map(t=>({id:t.id,type:t.type,state:t.state,reason:t.reason,gates:t.gates.map(g=>g.name+":"+(g.pass?"pass":"fail"))})),raw:JSON.stringify(R.raw).slice(0,120000),trace:JSON.stringify(otelExport(R)).slice(0,200000)})}catch(e){}}

