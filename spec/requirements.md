# Requirements · Service Request Agents (Mock 4)

User: agency service team. Problem: mixed client emails (certificates, claims, questions, changes) take manual reading, lookups and drafting; mistakes are E&O (errors and omissions) risk.

## US1
**As a risk advisor, I want each client email split into separate, typed tasks with the agent's plan checked by code, so that nothing in a multi-request email gets missed or misrouted.**

### R1
WHEN an email contains several requests, THE SYSTEM SHALL create one typed task per request with an exact supporting quote.

Acceptance tests:
- [x] blind oracle: B1 split into a claim task and a certificate task
- [x] adversarial: fabricated quote -> flagged, still safe
- [x] adversarial: unknown type -> other -> routed to a person

### R2
WHEN the orchestrator agent proposes a route, THE WORKFLOW ENGINE SHALL check it against policy and override it if it differs, logging the override.

Acceptance tests:
- [x] adversarial: orchestrator agent proposes a bad plan -> code overrides it

## US2
**As a claims advisor, I want any mention of an accident, injury or damage escalated to me before anything else, so that possible claims are reported fast, even when buried in a certificate request.**

### R3
WHEN an email mentions an accident, injury, damage or loss, THE SYSTEM SHALL create a claim task and escalate it before any drafting, even if the agent missed it.

Acceptance tests:
- [x] blind oracle: Claim escalated immediately, before any drafting
- [x] adversarial: intake drops the claim -> backstop claim escalates
- [x] adversarial: malformed intake -> backstop claim + no silent drop
- [x] adversarial: intake agent fails -> claim backstop still escalates

## US3
**As a risk advisor, I want certificates drafted only with wording the policy supports, and checked by a grounded LLM judge, so that we never misrepresent coverage (E&O risk).**

### R6
THE LLM judge SHALL review each draft against its own fresh fetch of every record the draft cites.

Acceptance tests:
- [x] blind oracle: Certificate blocked by the unsupported-wording gate
- [x] adversarial: QA wrongly passes -> deterministic gates still block

### R7
WHEN requested or required wording is not supported by a policy endorsement, THE SYSTEM SHALL block the certificate and escalate to an advisor.

Acceptance tests:
- [x] blind oracle: Certificate blocked by the unsupported-wording gate
- [x] adversarial: intake misses wording -> raw-email scan still blocks
- [x] adversarial: fulfillment adds unsupported wording -> gate blocks

## US4
**As a risk advisor, I want to approve every outgoing certificate or reply, and have it sent exactly once, so that I stay accountable for what clients and holders receive.**

### R8
THE SYSTEM SHALL send nothing without a person's approval, and SHALL send at most once per approved draft.

Acceptance tests:
- [x] approve sends once; second approve no-op
- [x] approving an escalated task does nothing
- [x] blind oracle: Nothing sent without a person
- [x] persistent timeout: Nothing sent without a person

## US5
**As a service lead, I want resent emails recognized and ignored, so that clients and holders never get duplicates.**

### R9
WHEN the same email arrives again, THE SYSTEM SHALL create no tasks, call no agents and take no actions.

Acceptance tests:
- [x] blind oracle: Resend deduplicated: no new tasks, agent calls or actions
- [x] persistent timeout: Resend deduplicated: no new tasks, agent calls or actions
- [x] adversarial: triple resend -> one set of tasks

## US6
**As a service lead, I want system outages retried and then escalated, so that nobody acts on partial information.**

### R10
WHEN a lookup times out, THE SYSTEM SHALL retry up to 3 times and then escalate instead of acting on partial context.

Acceptance tests:
- [x] blind oracle: First lookup timed out, was retried and recovered
- [x] persistent timeout: Certificate escalated (lookup never recovered)
- [x] persistent timeout: Timeouts retried, then escalated (no partial-context draft)

## US7
**As a firm leadership, I want agents limited to their own tools, and client text unable to change permissions or skip review, so that a prompt injection can't cause an unreviewed send.**

### R5
EACH agent SHALL call only the tools its policy allows, within its call budget, for the sender's own account.

Acceptance tests:
- [x] adversarial: context requests a disallowed tool -> denied and logged
- [x] adversarial: context looks up another client -> refused

### R11
Instructions inside client text SHALL NOT change permissions, routing or the approval step.

Acceptance tests:
- [x] blind oracle: "Skip review" flagged; changed no permission or rule
- [x] persistent timeout: "Skip review" flagged; changed no permission or rule
- [x] adversarial: injection fields in agent output -> ignored

## US8
**As an operations owner, I want a kill switch, and every task ending in exactly one valid state, so that nothing silently disappears and I can stop the system at any time.**

### R4
THE SYSTEM SHALL give every task exactly one end state and SHALL block and fail closed on any invalid transition.

Acceptance tests:
- [x] blind oracle: Every task ends in exactly one valid state; no invalid transitions
- [x] persistent timeout: Every task ends in exactly one valid state; no invalid transitions
- [x] forced invalid transition gated->sent blocked, fails closed to advisor
- [x] demo: conservation ok

### R12
WHEN the kill switch is on or an agent fails, THE SYSTEM SHALL hand open tasks to a person.

Acceptance tests:
- [x] adversarial: kill switch mid-run -> open tasks handed to a person
- [x] adversarial: intake agent fails -> whole email to a person
- [x] adversarial: intake agent fails -> claim backstop still escalates
- [x] adversarial: fulfillment fails -> fails closed to advisor

## US9
**As an auditor or engineer, I want a trace of every agent call, tool call, state change and gate, with inputs and outputs, so that I can debug, audit and explain any decision.**

### R13
THE SYSTEM SHALL record every agent call, tool call, state change, gate and retry as a trace span with input and output.

Acceptance tests:
- [x] trace spans render
- [x] span detail shows input and output
- [x] scores on trace

