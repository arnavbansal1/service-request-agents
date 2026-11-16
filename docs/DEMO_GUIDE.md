# Demo guide · Service Request Agents (Mock 4)

**Length:** about 5 minutes for the overview; 15–20 minutes with discussion. Pause on any step.
**Fast path:** the one-page demo card (`M4_Demo_Card.pdf`). This guide is the fuller reference behind it.
**If anything stalls:** click **Replay recorded run**. The demo never depends on a live model call.

**Claim discipline (say only this):** "every completed model run passed the 8 frozen checks" · "development evidence on one synthetic scenario" · the LLM judge is "same vendor" · tools not run are "planned".

## A. The run of show

4 slides (`M4_Demo_4Slides.pdf`), with the app's **▶ Start demo** guided steps in the middle.

| # | Where | Click | Say | Time |
|---|---|---|---|---|
| 1 | Slide 1: Exec summary | none | "Clients send mixed emails: a certificate request, an accident mentioned in passing, a billing question. Advisors read and look up every one. Agents do the reading and drafting; code and a person decide." | 30s |
| 2 | Slide 2: Architecture | none | "An orchestrator agent plans, specialist agents look up and draft, an LLM judge checks the draft, and code gates plus a person approve. Backend on the left, the advisor's frontend on the right." | 30s |
| 3 | App, step 1: The case | **▶ Start demo** | "One email, sent twice: a certificate for a new customer, a fender-bender in passing, and 'skip the usual review'." | 20s |
| 4 | App, step 2: Frontend | **Next** | "This is what the risk advisor gets. The possible claim is escalated first. The certificate is blocked by code because the policy lacks two wordings. Every task has a next step, and nothing is sent without the advisor." | 40s |
| 5 | App, step 3: Backend | **Next** | "This is what the system did. Agents run inside a code workflow engine, and every task ends in exactly one valid state. The red bars are the timeout and the blocked gates." | 30s |
| 6 | Slide 3 or app step 4: The failure | **Next** | "The most useful failure came from a rate-limit test. When the agent failed, the urgent-claim backstop didn't run, because it was tied to the model succeeding. I moved it outside the agent path." | 30s |
| 7 | App, step 5: The fix, live | **Next** (runs the outage drill) | "Now the orchestrator agent is rate-limited on every call. Code still escalates the claim, retries back off, and nothing is sent." | 30s |
| 8 | App, step 6: Ground truth and evidence | **Next** | "Each check compares the run to an expected outcome I froze before any run. Every completed model run passed the 8 frozen checks, on one synthetic scenario." | 30s |
| 9 | Slide 4: Evals and path | none | "I picked each eval for a risk" (section C), then the close (section D). | 60s |

**Three places to pause and ask the interviewer**
- After step 4: "Would your advisors want the claim escalated before anything else, even if it delays the certificate?"
- After step 7: "Which failure worries you more here: a missed claim or a wrong certificate?"
- After step 8: "What evidence would you need before a pilot?"

## B. Frontend, backend and ground truth (one line each)

- **Frontend:** "What the risk advisor sees and approves: tasks, drafts, next steps."
- **Backend:** "Agents, the workflow engine, gates and records. In this prototype both run in one page; in production the backend is a service."
- **Ground truth:** "A frozen expected outcome plus the system-of-record data. It's synthetic and written by me; production ground truth is advisor-labeled real requests."

Use the **Both / Frontend / Backend** toggle if asked to show one side only.

## C. Evals we ran, and why

| Eval | Risk it tests | Why this one | Result |
|---|---|---|---|
| Frozen blind case (8 checks) | Orchestration end to end | The expected answer was fixed before the model ran, so I'm not grading after seeing the output | Every completed model run passed 8/8 |
| Adversarial tests + outage drill | Rare, costly failures | A happy-path sample wouldn't expose them | 44 engine and adversarial tests pass |
| LLM judge (same vendor) | Unsupported claims in free-text drafts | Deterministic scoring is weak on free text. It is one gate, not the source of truth | Blocks drafts that cite what the records don't show |
| DeepEval tool correctness | Wrong or missing lookups | Tool choice is structured and checkable, so no second model judge is needed | On 10 recorded live runs it caught a prompt regression: context prompt v1 4/4, v2 1/3, v3 3/3 |
| UI tests | The demo itself breaking | Cheap, and it protects the live walkthrough | 25 pass |

**Planned, not run:** promptfoo red-teaming, DeepEval's model-judged metrics, Langfuse tracing. "They need keys or a server, and they pay off across many real cases."

**How I ran evals:** "Read the traces, label failures, find the cause, fix, add a test that fails without the fix, replay."

## D. Close (30 seconds)

"Next is real requests in shadow mode: agents draft, advisors still do the work, and we measure drafts approved without edits and zero wrong sends. Then a pilot on certificates only. Autonomy widens one request type at a time, each with eval evidence and a rollback plan. The bar stays the same: would a risk advisor send this without edits?"

## E. Results (say only what's here)

- Every completed model run passed the 8 frozen checks. Two runs were cut short by the rate limit; both failed closed and nothing was sent.
- Four fixes: (1) the judge re-fetches every record the draft cites · (2) the claim backstop runs without the model, plus backoff · (3) context prompt v3 · (4) the policy-match gate checks each policy.
- Live-verified: fixes 1, 3 and 4. Fix 2 is verified by the outage drill and tests; the original failure happened live.
- Offline: 44 engine and adversarial tests, 25 UI tests.

## F. Likely questions

**"How did you find the failure?"**
**A chaos-style test, not luck.** Back-to-back live runs hit the rate limit. Everything failed closed, but one trace had no claim task. That is the costliest miss, so it became the top fix.

**"Why was the backstop tied to the model?"**
**It sat inside the success path.** The scan for incident words ran only after the agent returned. Now it runs on the raw email every time, and a test locks that in.

**"Why several agents and not one, or a plain workflow?"**
**Different permissions and an independent check.** Lookups are read-only, drafting has no tools, and the judge re-fetches the records. Everything consequential is still plain code: routing policy, gates, state, sends.

**"What's real and what's mocked?"**
**The model calls, gates, tests and scoring are real; the data is synthetic.** The policy system, email and send are mocks behind an interface. The app has a "What's real, mocked, not built" table.

**"Why not automate the send?"**
**A wrong certificate or a missed claim costs far more than a review.** A person approves every external send until real-case evidence earns more autonomy, one request type at a time.

**"What does production take?"**
**The normal delivery path, with evals as a gate.** Architecture review, full testing in test environments, user acceptance testing with advisors on real requests, then a controlled rollout: shadow mode, a certificates pilot, change approval for each expansion, with monitoring and rollback.

## G. Stretching to 15–20 minutes

Open these only when asked; each is one click in the app:
- **Details** on a task: the plan, each gate, the judge's output, the draft.
- **Trace:** timeline and tree views of every agent step, lookup and retry.
- **Prompts and agent skills:** the versioned prompts (this is where the v2 regression shows).
- **Spec:** user stories and requirements with traceability.
- **Architecture:** business, process and technical diagrams.
- **Ground truth data:** the frozen expected outcome and the records.
