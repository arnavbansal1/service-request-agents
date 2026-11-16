# Mock 4 framing: client service requests (built on labeled assumptions; discovery answers pending)

1. **Workflow:** email/portal request → intake (read, classify; one email can hold two requests) → context (agency system: policies, certificate holders, endorsements, contract requirements) → decision (complete? handle directly or send to advisor/carrier?) → action (issue COI, request endorsement, report claim) → communication (acknowledge, update, deliver) → completion (logged).
2. **Bottleneck:** every request needs a person to read, look up and decide before anything happens. **Costliest failure:** an urgent claim buried in a routine queue; next, a wrong COI (holder, coverage, unsupported wording).
3. **Wedges:**
   - A. Triage for all request types: classify, urgency, completeness, route with context packet. Broad, low risk, prevents missed claims; doesn't do the work.
   - B. COI lane end to end: draft from policy data, check holder requirements, human approves. High volume, measurable; narrow, wrong-COI risk.
   - C. Full service agent: too broad and too risky to start.
4. **Recommendation:** A with one deep lane (B).
5. **Architecture:** deterministic workflow + model calls (classify, extract, draft) + an independent outbound verifier (separate model call + deterministic field checks against policy data). Not full multi-agent: steps are stable; parallel agents add little.
6. **Automate:** classify, extract with quotes, flag urgency, pull context, check completeness. **Suggest:** COI drafts, client replies, missing-info requests. **Escalate:** any possible claim (immediately), endorsements/coverage changes, billing disputes, unsupported wording, unclear or unsupported requests.
7. **MVP:** inbox of ~10 sample requests, urgent pinned; each shows type(s), urgency, quoted facts, account context, completeness checklist, route + reason, draft, QA results, approve / edit / escalate, trace.
8. **North Star:** requests resolved correctly within SLA. **Guardrail:** 0 urgent claims unrouted; 0 COIs mismatching policy data.
9. **Biggest assumption:** the model reliably catches urgency and multi-request emails, and policy data is clean enough to draft COIs.
10. **Facts:** request types, channels, the six-step process, the four named failures. **Assumptions:** COIs are the volume leader; nothing goes out unreviewed; agency system readable; metric = turnaround.

**If answers differ:** endorsements lead volume → deep lane = endorsements; standard COIs already go out unreviewed → auto-issue with the verifier as a hard gate; error rate is the metric → North Star = resolved right the first time.
