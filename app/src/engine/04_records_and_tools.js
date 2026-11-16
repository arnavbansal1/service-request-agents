/* ================= 4. Mock system of record + tools (read-only) ================= */
function accountByEmail(addr){return AMS.accounts.find(a=>a.contacts.includes(String(addr||"").toLowerCase()))||null}
const TOOLS={
  get_account:a=>{const x=accountByEmail(a.client_email);return x?{record_id:"account:"+x.account_id,data:{account_id:x.account_id,name:x.name,account_manager:x.account_manager,policies:x.policies.map(p=>p.policy_id)}}:{record_id:null,data:null}},
  get_policy:a=>{const x=accountByEmail(a.client_email);const p=x&&x.policies.find(p=>p.line===a.line);return p?{record_id:"policy:"+p.policy_id,data:{...p,insured:x.name,account_id:x.account_id}}:{record_id:null,data:null}},
  get_holder_requirements:a=>{const h=AMS.holders.find(h=>norm(h.holder_name)===norm(a.holder_name));return h?{record_id:"holder:"+h.holder_name,data:h}:{record_id:null,data:null}},
  get_prior_requests:a=>{const x=accountByEmail(a.client_email);return{record_id:x?"prior:"+x.account_id:null,data:x?AMS.prior_requests.filter(r=>r.account_id===x.account_id):[]}}
};
async function execTool(R,agent,tool,args,parent){
  const allowed=(POLICY[agent]||{}).tools||[];
  if(!allowed.includes(tool)){event(R.T,`execute_tool ${tool}`,"tool",{"gen_ai.operation.name":"execute_tool","gen_ai.tool.name":tool,"gen_ai.agent.name":agent,"error.type":"permission_denied","policy.allowed":allowed.join(",")},parent,"error");R.stats.denied++;return{denied:true}}
  for(let attempt=1;attempt<=RETRY.maxAttempts;attempt++){
    const s=startSpan(R.T,`execute_tool ${tool}`,"tool",{"gen_ai.operation.name":"execute_tool","gen_ai.tool.name":tool,"gen_ai.tool.call.id":uid("call"),"gen_ai.agent.name":agent,"retry.attempt":attempt,"tool.args":JSON.stringify(args)},parent);
    await sleep(40);
    const f=R.faults[tool];if(f&&f.length){const kind=f.shift();if(kind==="timeout"){endSpan(R.T,s,"error",{"error.type":"timeout"});R.stats.timeouts++;if(attempt<RETRY.maxAttempts){event(R.T,`retry ${tool} in ${RETRY.backoffMs[attempt-1]}ms`,"state",{"retry.attempt":attempt+1},parent);await sleep(RETRY.backoffMs[attempt-1]);R.stats.retries++;continue}return{timeout:true}}}
    let out;try{out=TOOLS[tool](args||{})}catch(e){endSpan(R.T,s,"error",{"error.type":"tool_error"});return{error:true}}
    s.io={input:args,output:out.data};endSpan(R.T,s,"ok",{"result.record_id":out.record_id||"none"});return{ok:true,...out,attempt}}
}

