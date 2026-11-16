# Demo card · 2 minutes

| # | Click | Say |
|---|---|---|
| 1 | **▶ Start demo** (or Slide: Exec summary) | "Advisors read every mixed email. Agents read and draft; code and a person decide." |
| 2 | **Slide: Architecture** | "Orchestrator agent plans, specialist agents draft, an LLM judge checks, code gates and a person approve." |
| 3 | **App → Blind test case → B1 → Frontend** | "This is the frontend: what the risk advisor sees. Hardest email: bad wording, a buried accident, 'skip review', sent twice. Each task has a next step." |
| 4 | **Backend → Trace → Timeline** | "This is the backend: agents inside a code workflow engine. Every task ends in exactly one valid state." |
| 5 | **Slide: Failure** | "A rate-limit test showed the claim backstop depended on the model. I moved it outside the agent path." |
| 6 | **App → Outage drill** | "Agent down: claim still escalated, retries, nothing sent." |
| 7 | **Slide: Evidence** | "I picked each eval for a risk: a frozen blind case for orchestration, adversarial tests for costly failures, an LLM judge for drafts, DeepEval tool correctness for lookups. It caught a prompt regression. Every completed run passed 8/8, on one synthetic scenario." |
| 8 | **Close** | "Shadow mode on real requests, then a certificates pilot, then wider autonomy." |

**Ground truth (say at the eval panel):** "Each check compares the run to an expected outcome I froze before any run. It's synthetic and written by me; production ground truth is advisor-labeled real requests."

**How I ran evals:** "Read the traces, label failures, find the cause, fix, add a test that fails without the fix, replay."

**Why each eval (say when you reach the evidence slide):**
- *Frozen blind case:* "An end-to-end orchestration test with the expected answer fixed before the model ran, not grading after seeing the output."
- *Adversarial + outage drill:* "The failures I care most about are rare but costly, so a happy-path sample wouldn't expose them."
- *LLM judge:* "Only for free-text drafts, where semantic grounding matters and deterministic scoring is weak. One gate, not the source of truth."
- *DeepEval tool correctness:* "Tool selection is structured and objectively checkable, so no reason to add another model judge." Add: "Small sample, so it's regression evidence, not proof of reliability."

**If asked about the failure:** "Found by a chaos test. Safety checks now never wait on the model."

**If asked why not promptfoo / Langfuse:** "Planned for production. They need keys or a server, and they pay off across many real cases. Here I ran the evals that test this prototype's biggest risks."
