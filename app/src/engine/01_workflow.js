/* ================= 1. Workflow definition (deterministic) ================= */
const STATE_LABEL={received:"Received",triaged:"Triaged",context:"Gathering context",drafted:"Drafted",qa:"LLM judge",gated:"Safety gates",awaiting_approval:"Awaiting approval",sent:"Sent",escalated_urgent:"Escalated: urgent claim",escalated_advisor:"Escalated to advisor",routed_human:"Routed to a person",needs_info:"Needs client info"};
const TRANSITIONS={received:["triaged","escalated_advisor"],triaged:["escalated_urgent","routed_human","context","escalated_advisor"],context:["drafted","escalated_advisor"],drafted:["qa","escalated_advisor"],qa:["gated","escalated_advisor"],gated:["awaiting_approval","escalated_advisor","needs_info"],awaiting_approval:["sent","escalated_advisor"]};
const TERMINAL=new Set(["sent","escalated_urgent","escalated_advisor","routed_human","needs_info"]);
const END_STATES=new Set([...TERMINAL,"awaiting_approval"]); /* awaiting_approval = handed to a person */
const HAPPY=["received","triaged","context","drafted","qa","gated","awaiting_approval","sent"];
const TYPES={coi:"Certificate of insurance",claim:"Possible claim",policy_question:"Policy question",endorsement:"Endorsement change",billing:"Billing",new_exposure:"New location or vehicle",risk_request:"Risk request",other:"Other"};
const AGENT_LABEL={intake:"Orchestrator agent",context:"Context agent",fulfillment:"Fulfillment agent",qa:"LLM judge",workflow_engine:"Workflow engine (code)"};
const ROUTES={specialist_agents:"specialist agents",human:"a person",urgent_escalation:"urgent escalation"};
function policyRoute(type){return type==="claim"?"urgent_escalation":AGENT_LANES.has(type)?"specialist_agents":"human"}
const AGENT_LANES=new Set(["coi","policy_question"]);
const ROUTE_TO={endorsement:"advisor",new_exposure:"advisor",billing:"billing team",risk_request:"advisor",other:"service team"};
/* Policy as code: what each agent may touch. Agents can't change this. */
const POLICY={
  intake:{tools:[],can:"Orchestrator agent: splits the email into typed tasks and proposes a plan (route per task). No tools; its plan is checked by code",version:"intake@v3"},
  context:{tools:["get_account","get_policy","get_holder_requirements","get_prior_requests"],maxCalls:4,can:"Read-only lookups it chooses",version:"context@v3"},
  fulfillment:{tools:[],can:"Draft a certificate, reply or plan; no tools, no sending",version:"fulfillment@v2"},
  qa:{tools:["get_account","get_policy","get_holder_requirements"],can:"LLM-as-judge: gets its own fresh fetch of every record the draft relies on, then gives a pass/fail verdict with issues",version:"qa@v3"},
  workflow_engine:{tools:["dedupe","escalate","record_send"],can:"Code, not an agent: validates the plan against policy, owns state, retries, gates; sends only after a person approves"}
};
const RETRY={maxAttempts:3,backoffMs:[150,300]};
const INJECTION_RE=/\b(skip|bypass|ignore|disregard)\b[^.]{0,40}\b(review|approval|check|checks|instructions|rules|process)\b|\bjust send\b|\bsend (it |the certificate )?(straight|directly)\b|\bno need to (review|check)\b/i;
const INCIDENT_RE=/\b(accident|rear-ended|rear ended|collision|crash(ed)?|injur\w*|hurt|damaged?|fell|fire|theft|stolen|lawsuit|sued|totaled)\b/i;
const WORDING={"additional insured":/additional insured/i,"primary and non-contributory":/primary\s*(and|&)\s*non-?\s*contributory/i,"waiver of subrogation":/waiver of subrogation/i};

