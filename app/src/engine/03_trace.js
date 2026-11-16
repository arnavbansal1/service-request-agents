/* ================= 3. Trace (OpenTelemetry GenAI-style spans) ================= */
function newTrace(){return{trace_id:hash(String(Math.random())+Date.now())+hash(String(performance.now())),spans:[],t0:performance.now()}}
function startSpan(T,name,kind,attrs,parent){const s={span_id:uid("s"),parent_id:parent?parent.span_id:null,name,kind,attributes:{...attrs},start:performance.now()-T.t0,end:null,status:"ok"};T.spans.push(s);return s}
function endSpan(T,s,status,extra){s.end=performance.now()-T.t0;if(status)s.status=status;if(extra)Object.assign(s.attributes,extra);return s}
function event(T,name,kind,attrs,parent,status){const s=startSpan(T,name,kind,attrs,parent);return endSpan(T,s,status||"ok")}

