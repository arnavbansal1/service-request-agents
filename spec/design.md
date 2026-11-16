# Design · Service Request Agents (Mock 4)

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
