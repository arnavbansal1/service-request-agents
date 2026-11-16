/* ================= 12. Wiring ================= */
function switchDs(ds){if(state.busy)return;state.ds=ds;state.R=null;state.sel=null;state.selTask=null;history.replaceState(null,"",ds==="blind"?"#blind":"#");state.mode=SAVED[ds]?"saved":(state.sample?"live":"saved");renderAll();setStatus(ds==="blind"?"Blind test case: expected outcome frozen before any run. Replay the recorded run, or go live under Advanced.":"Click ▶ Start demo, or Run inbox.")}
$("dsDemo").onclick=()=>switchDs("demo");$("dsBlind").onclick=()=>switchDs("blind");
$("mSaved").onclick=()=>{state.mode="saved";renderControls()};$("mLive").onclick=()=>{state.mode="live";renderControls()};
$("runBtn").onclick=()=>runInbox();
$("run3Btn").onclick=async()=>{const m=state.mode;state.mode="live";for(let i=0;i<3;i++){if(i){setStatus(`Pausing 20s before live run ${i+1} of 3 (rate limits)…`);await sleep(20000)}await runInbox()}state.mode=m;renderControls()};
$("faultBtn").onclick=()=>{state.persistFault=!state.persistFault;renderControls()};
$("killBtn").onclick=()=>{state.killed=!state.killed;if(state.R)event(state.R.T,state.killed?"kill switch ON":"kill switch released","guard",{},state.R.emailSpan[state.sel]||null);renderAll()};
$("vTree").onclick=()=>{state.view="tree";renderAll()};$("vTime").onclick=()=>{state.view="time";renderAll()};
document.addEventListener("click",ev=>{const d=document.querySelector("details.adv");if(d&&d.open&&(!d.contains(ev.target)||ev.target.closest(".advp button")))setTimeout(()=>{d.open=false},0)});
$("layBoth").onclick=()=>{state.layer="both";renderAll()};$("layFe").onclick=()=>{state.layer="fe";renderAll()};$("layBe").onclick=()=>{state.layer="be";renderAll()};
$("tourBtn").onclick=()=>{state.guided=false;showTour(0)};
$("demoBtn").onclick=async()=>{if(state.busy)return;state.guided=true;await loadRecorded();showTour(0)};
$("drillBtn").onclick=async()=>{if(state.busy)return;if(state.ds!=="blind")switchDs("blind");state.outage=true;try{await runInbox()}finally{state.outage=false}state.sel="B1";renderAll()};
document.addEventListener("keydown",ev=>{if(state.tour==null)return;if(ev.key==="ArrowRight")showTour(state.tour+1);if(ev.key==="ArrowLeft")showTour(state.tour-1);if(ev.key==="Escape")showTour(null)});
$("exportBtn").onclick=async()=>{if(!state.R)return;const data=JSON.stringify(otelExport(state.R),null,2);const fn=`trace-${state.R.T.trace_id}.json`;
  try{const dl=window.claude?await window.claude.use("downloads"):null;if(dl){await dl.save({filename:fn,data});setStatus("Trace exported: "+fn);return}}catch(e){setStatus("Export cancelled");return}
  try{await navigator.clipboard.writeText(data);setStatus("Trace JSON copied to clipboard")}catch(e){$("raw").textContent=data;$("raw").closest("details").open=true;setStatus("Trace JSON shown in Raw agent outputs")}};
window.__mas={showTour,tourSteps,transition,runInbox,newRun,state,EXPECTED,scoreBlind,conservation,approve,otelExport,setSaved:(ds,v)=>{SAVED[ds]=v}};
switchDs(state.ds);
(async()=>{try{state.sample=window.claude?await window.claude.use("sample"):null}catch(e){state.sample=null}renderControls()})();
