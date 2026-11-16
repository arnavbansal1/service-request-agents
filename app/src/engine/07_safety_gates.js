/* ================= 7. Deterministic safety gates ================= */
function primaryLine(task){const l=String(task.details&&task.details.line||"").toLowerCase();return task.type==="coi"?"general_liability":(/auto/.test(l)?"commercial_auto":"general_liability")}
function supportedWording(policy){const ends=(policy&&policy.endorsements||[]).join(" | ");return Object.keys(WORDING).filter(k=>WORDING[k].test(ends))}
function runGates(R,email,task){
  const G=[];const acct=accountByEmail(email.from);const recs=task.qaRecords||{};const pl=primaryLine(task);const pol=Object.values(recs).find(r=>r&&r.policy_id&&r.line===pl)||Object.values(recs).find(r=>r&&r.policy_id);
  G.push({name:"approval_required",label:"Human approval required",pass:true,detail:email.injection?`Client text asked to "${email.injection}"; approval is set in code and can't be skipped`:"Always on for external actions"});
  if(task.type==="coi"){
    const d=task.draft&&task.draft.coi||{};
    const requested=[...new Set([...task.details.wording_requested.flatMap(w=>wordingIn(w)),...wordingIn(task.quote),...wordingIn(email.body),...(d.wording||[]).flatMap(w=>wordingIn(w))])];
    const sup=supportedWording(pol);const unsupported=requested.filter(w=>!sup.includes(w));task.unsupported=unsupported;
    G.push({name:"unsupported_wording",label:"Wording supported",pass:!!pol&&unsupported.length===0,detail:!pol?"No policy record to check against":unsupported.length?`Requested but not on the policy: ${unsupported.join(", ")}`:`All requested wording supported (${requested.join(", ")||"none"})`});
    const pm=[];if(!pol)pm.push("no policy record");else{
      /* each drafted policy is checked against ITS OWN record (found by the 4th live batch: auto policies were compared to the GL record) */
      (d.policies||[]).forEach(p=>{const rec=Object.values(recs).find(r=>r&&r.policy_id===p.policy_id);if(!rec){pm.push(`policy ${p.policy_id} not in the judge's fetched records`);return}
        Object.entries(rec.limits||{}).forEach(([k,v])=>{if(p[k]==null)pm.push(`${p.policy_id}: ${k.replace(/_/g," ")} missing`);else if(Number(p[k])!==v)pm.push(`${p.policy_id}: ${k.replace(/_/g," ")} differs`)})});
      if(!(d.policies||[]).some(p=>p.policy_id===pol.policy_id))pm.push(`primary policy ${pol.policy_id} not on the draft`);
      if(acct&&d.insured!==acct.name)pm.push(`insured name "${d.insured}" ≠ "${acct.name}"`)}
    G.push({name:"policy_match",label:"Policy match",pass:pm.length===0,detail:pm.length?pm.join("; "):"Policy number, limits and insured match the system of record"});
    const hold=Object.values(recs).find(r=>r&&r.requirements);const lim=[];if(hold&&pol){Object.entries(hold.min_limits||{}).forEach(([k,v])=>{if((pol.limits[k]||0)<v)lim.push(`${k} below holder minimum`)});(hold.requirements||[]).forEach(q=>{if(!sup.includes(q))lim.push(`holder requires "${q}"`)})}
    G.push({name:"holder_requirements",label:"Holder requirements",pass:lim.length===0,detail:!hold?"Holder not on file: requirements unknown (checked on wording only)":lim.length?lim.join("; "):"Policy meets the holder's requirements"});
    const miss=[];if(!d.holder_name)miss.push("holder name");if(!d.holder_address)miss.push("holder address");
    G.push({name:"evidence_complete",label:"Evidence complete",pass:miss.length===0,detail:miss.length?`Missing: ${miss.join(", ")}`:"Holder name and address present"});
  }
  if(task.type==="policy_question"){const reply=String(task.draft&&task.draft.reply||"");const nums=(reply.match(/\$\s?[\d,]+/g)||[]).map(x=>Number(x.replace(/[$,\s]/g,"")));const vals=pol?Object.values(pol.limits):[];const bad=nums.filter(n=>!vals.includes(n));
    G.push({name:"numbers_grounded",label:"Numbers grounded",pass:!!pol&&bad.length===0,detail:!pol?"No policy record":bad.length?`Not in the policy record: ${bad.map(money).join(", ")}`:`Every amount matches the policy (${nums.map(money).join(", ")||"none"})`})}
  const cites=(task.draft&&task.draft.citations)||[];const known=new Set(Object.keys(task.records||{}));const badC=cites.filter(c=>!known.has(c));
  G.push({name:"citations_valid",label:"Citations verified",pass:badC.length===0,detail:badC.length?`Cites records not fetched: ${badC.join(", ")}`:`${cites.length} citation(s) all fetched`});
  const q=task.qa||{};G.push({name:"llm_judge",label:"LLM judge verdict",pass:q.verdict==="pass",detail:q.verdict==="pass"?"Judge passed the draft":(q.issues||[]).map(i=>`${i.type}: ${i.detail}`).join(" · ")||"Judge did not pass the draft"});
  return G}

