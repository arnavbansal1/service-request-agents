/* ================= 10. OpenTelemetry-style export ================= */
function otelExport(R){return{resource:{"service.name":"service-request-agents","deployment.environment":"prototype"},trace_id:R.T.trace_id,spans:R.T.spans.map(s=>({trace_id:R.T.trace_id,span_id:s.span_id,parent_span_id:s.parent_id,name:s.name,start_ms:Math.round(s.start),end_ms:Math.round(s.end??s.start),status:s.status==="ok"?"OK":"ERROR",attributes:s.attributes}))}}

