import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
ROOT = HERE.parent
"""Spec-driven build: requirements.md, design.md, tasks.md + in-app traceability (requirement -> tests -> result)."""
import json, pathlib
from html import escape as e
REQS = [
 ("R1","WHEN an email contains several requests, THE SYSTEM SHALL create one typed task per request with an exact supporting quote.",["blind oracle: B1 split","adversarial: fabricated quote","adversarial: unknown type"]),
 ("R2","WHEN the orchestrator agent proposes a route, THE WORKFLOW ENGINE SHALL check it against policy and override it if it differs, logging the override.",["adversarial: orchestrator agent proposes a bad plan"]),
 ("R3","WHEN an email mentions an accident, injury, damage or loss, THE SYSTEM SHALL create a claim task and escalate it before any drafting, even if the agent missed it.",["blind oracle: Claim escalated","adversarial: intake drops the claim","adversarial: malformed intake","claim backstop still escalates"]),
 ("R4","THE SYSTEM SHALL give every task exactly one end state and SHALL block and fail closed on any invalid transition.",["Every task ends","forced invalid transition","demo: conservation"]),
 ("R5","EACH agent SHALL call only the tools its policy allows, within its call budget, for the sender's own account.",["adversarial: context requests a disallowed tool","adversarial: context looks up another client"]),
 ("R6","THE LLM judge SHALL review each draft against its own fresh fetch of every record the draft cites.",["blind oracle: Certificate blocked","adversarial: QA wrongly passes"]),
 ("R7","WHEN requested or required wording is not supported by a policy endorsement, THE SYSTEM SHALL block the certificate and escalate to an advisor.",["blind oracle: Certificate blocked","adversarial: intake misses wording","adversarial: fulfillment adds unsupported wording"]),
 ("R8","THE SYSTEM SHALL send nothing without a person's approval, and SHALL send at most once per approved draft.",["approve sends once","approving an escalated task","Nothing sent without a person"]),
 ("R9","WHEN the same email arrives again, THE SYSTEM SHALL create no tasks, call no agents and take no actions.",["Resend deduplicated","adversarial: triple resend"]),
 ("R10","WHEN a lookup times out, THE SYSTEM SHALL retry up to 3 times and then escalate instead of acting on partial context.",["First lookup timed out","persistent timeout: Certificate escalated","persistent timeout: Timeouts retried"]),
 ("R11","Instructions inside client text SHALL NOT change permissions, routing or the approval step.",["\"Skip review\" flagged","adversarial: injection fields in agent output"]),
 ("R12","WHEN the kill switch is on or an agent fails, THE SYSTEM SHALL hand open tasks to a person.",["adversarial: kill switch","adversarial: intake agent fails","adversarial: fulfillment fails"]),
 ("R13","THE SYSTEM SHALL record every agent call, tool call, state change, gate and retry as a trace span with input and output.",["trace spans render","span detail shows input and output","scores on trace"]),
]
STORIES = [
 ("US1","Risk advisor","each client email split into separate, typed tasks with the agent's plan checked by code","nothing in a multi-request email gets missed or misrouted",["R1","R2"]),
 ("US2","Claims advisor","any mention of an accident, injury or damage escalated to me before anything else","possible claims are reported fast, even when buried in a certificate request",["R3"]),
 ("US3","Risk advisor","certificates drafted only with wording the policy supports, and checked by a grounded LLM judge","we never misrepresent coverage (E&O risk)",["R6","R7"]),
 ("US4","Risk advisor","to approve every outgoing certificate or reply, and have it sent exactly once","I stay accountable for what clients and holders receive",["R8"]),
 ("US5","Service lead","resent emails recognized and ignored","clients and holders never get duplicates",["R9"]),
 ("US6","Service lead","system outages retried and then escalated","nobody acts on partial information",["R10"]),
 ("US7","Firm leadership","agents limited to their own tools, and client text unable to change permissions or skip review","a prompt injection can't cause an unreviewed send",["R5","R11"]),
 ("US8","Operations owner","a kill switch, and every task ending in exactly one valid state","nothing silently disappears and I can stop the system at any time",["R4","R12"]),
 ("US9","Auditor or engineer","a trace of every agent call, tool call, state change and gate, with inputs and outputs","I can debug, audit and explain any decision",["R13"]),
]
def results():
    r={}
    for f in [ROOT/'tests'/'engine_results.json',ROOT/'tests'/'ui_results.json']:
        p=pathlib.Path(f)
        if p.exists(): r.update({x['test']:x['pass'] for x in json.loads(p.read_text())})
    return r
def match(res, frag): return [(k,v) for k,v in res.items() if frag.lower() in k.lower()]
def spec_html():
    res=results(); rows=""; R={r[0]:r for r in REQS}
    for sid,who,want,why,rids in STORIES:
        rows+=f'<tr style="background:#F7F7F3"><td colspan="4"><b>{sid}</b> · As {"an" if who[0].lower() in "aeiou" else "a"} <b>{e(who.lower())}</b>, I want {e(want)}, so that {e(why)}.</td></tr>'
        for rid in rids:
            _,txt,frags=R[rid]; ms=[m for f in frags for m in match(res,f)]; ok=bool(ms) and all(v for _,v in ms)
            rows+=f'<tr><td style="padding-left:18px"><b>{rid}</b></td><td>{e(txt)}</td><td>{len(ms)} test(s)</td><td class="{"pass" if ok else "fail"}">{"Pass" if ok else ("No test" if not ms else "FAIL")}</td></tr>'
    return f'<table class="sc"><tr><th>ID</th><th>User story → acceptance criteria (EARS style)</th><th>Proved by</th><th>Offline result</th></tr>{rows}</table><p class="note">Results from the offline engine and UI suites at build time. Full spec: requirements.md, design.md, tasks.md.</p>'
def write_md():
    d=(ROOT/'spec'); d.mkdir(exist_ok=True); res=results()
    req="# Requirements · Service Request Agents (Mock 4)\n\nUser: agency service team. Problem: mixed client emails (certificates, claims, questions, changes) take manual reading, lookups and drafting; mistakes are E&O (errors and omissions) risk.\n\n"
    R={r[0]:r for r in REQS}
    for sid,who,want,why,rids in STORIES:
        req+=f"## {sid}\n**As {"an" if who[0].lower() in "aeiou" else "a"} {who.lower()}, I want {want}, so that {why}.**\n\n"
        for rid in rids:
            _,txt,frags=R[rid]; ms=[m for f in frags for m in match(res,f)]
            req+=f"### {rid}\n{txt}\n\nAcceptance tests:\n"+"".join(f"- [{'x' if v else ' '}] {k}\n" for k,v in ms)+"\n"
    (d/'requirements.md').write_text(req)
    (d/'design.md').write_text("""# Design · Service Request Agents (Mock 4)

## Architecture
- Orchestrator agent (Claude): splits the email into typed tasks with quotes; proposes a route per task. No tools. Skill: service-intake.
- Workflow engine (code): fingerprint dedupe; injection and incident scans on raw text; validates the plan against policy (R2); state machine with an explicit transition table (R4); retries with backoff (R10); kill switch (R12); audit trace (R13).
- Context agent: picks read-only lookups (get_account, get_policy, get_holder_requirements, get_prior_requests), max 4, own account only (R5).
- Fulfillment agent: drafts a certificate or reply from cited records; no tools; cannot send. Skills: coi-drafting, policy-question.
- LLM judge: verdict + issues against its own fresh fetch of every cited record (R6). Skill: eo-review.
- Safety gates (code): approval required, wording supported (R7), policy match, holder requirements, evidence complete, numbers grounded, citations verified, LLM judge verdict.
- Person: approves or rejects; send is idempotent per task + draft hash (R8).

## States
received → triaged → {escalated_urgent | routed_human | context} → drafted → qa → gated → {awaiting_approval | escalated_advisor | needs_info}; awaiting_approval → {sent | escalated_advisor}. Any step may fail closed to escalated_advisor.

## Interfaces (agent output schemas)
- Orchestrator: {requests:[{type, route, summary, urgency, quote, details:{holder_name, holder_address, wording_requested[], line, question}, missing_info[]}], notes[]}
- Context: {tool_calls:[{tool, args}], reason}
- Fulfillment: {action, coi:{insured, holder_name, holder_address, policies[], wording[]}, unsupported_requested[], reply, citations[]}
- LLM judge: {verdict, issues:[{type, detail, evidence}]}

## Error handling
Invalid agent output → validated, flagged, safe defaults. Agent failure → retry once → escalate. Tool timeout → 3 attempts → escalate. Invalid transition → blocked, counted, escalate. Kill switch → no agent step runs.

## Testing
Engine + adversarial suite (Playwright, offline saved outputs), UI suite, blind case with frozen expected outcome (sha256), 3 live runs persisted to the artifact database.
""")
    tasks="# Tasks · Service Request Agents (Mock 4)\n\n"+"".join(f"- [x] {t}\n" for t in [
      "Freeze blind case and expected outcome (sha256) before any code (R1–R12)","Case data: mock agency records, demo + blind inbox",
      "Workflow engine: transition table, conservation check (R4)","Dedupe fingerprint (R9); injection + incident scans (R3, R11)",
      "Orchestrator agent prompt + plan check (R1, R2)","Policy as code + tool executor with retries and fault injection (R5, R10)",
      "Context, fulfillment, LLM judge agents + skills (R6)","Safety gates (R7) and idempotent approval/send (R8)",
      "Kill switch and fail-closed handling (R12)","OpenTelemetry-style trace, Langfuse-style detail pane, timeline (R13)",
      "Eval panel scored against the frozen outcome; run history; consistency","Business, process and technical architecture diagrams",
      "Engine + adversarial tests (41), UI tests","Publish; 3 live blind runs; fix found issue (judge evidence scope) and rerun",
      "Results deck, DEMO_GUIDE, GitHub repo"])
    (d/'tasks.md').write_text(tasks)
if __name__=="__main__": write_md(); print("spec written")
