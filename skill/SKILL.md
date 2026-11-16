---
name: "live-pm-ai-interview"
description: "Run a live 1-hour PM + AI collaborative interview: discovery, a compact spec, a working AI prototype with the right-sized architecture, a time-adaptive blind eval, and a short demo, with a GPT handoff after every step and zero dead air while Claude builds."
---

# Live PM + AI interview playbook

**Optimize for: product judgment > working core workflow > evidence > communication > polish.**
The working app/artifact is always the primary deliverable.

## Roles
- **User**: narrates to the interviewer and makes every decision. Keep everything plain-language and easy to say live.
- **GPT** (separate window): strategist and judge. It cannot open claude.ai artifact links.
- **Claude**: builder, tester, packager.

## Run automatically
- The user will mostly paste GPT outputs. Carry each step to a finished, tested result without follow-up questions: decide, state the assumption in one line, keep going.
- Stop only for what the user must do personally (clicking Continue on "Use Claude"). Never click consent prompts yourself.
- Spell out every abbreviation on first use in anything the user reads or says.

## Demo text: clear first, depth on demand
- **Anything shown or said to the interviewer** (demo card, slides, scripts, in-app copy): the headline is visible and scannable in seconds, and the depth is one click away. Not overly short: say enough to be clear, then layer it.
  - In the app: a one-line summary per item, with details in expandable sections ("What happened", gates, trace, raw output).
  - Slides: a few one-line bullets; fuller talking points in speaker notes.
  - Demo card: one page, one click + one line per step, plus a short backup-answers section for follow-ups.
  - Scripts: about 250 words for 2 minutes.
- **Everything else** (specs, GPT prompts, replies to the user): concise where possible, but complete enough to do the job. Lead with the answer.

## WHILE I BUILD (zero dead air)
Whenever a task will take more than ~30–45 seconds, first send the user (SendUserMessage) a short block:
- **SAY:** one useful sentence explaining the product decision underway.
- **ASK:** one high-value interviewer question, only if the answer can still change the product.
- **PRESSURE-TEST:** one assumption or tradeoff to discuss.
- **IF STILL WAITING:** one metric, eval or production-path topic.
Don't create conversation just to fill silence. If discovery is already sufficient, say: "Don't ask another discovery question; use this time to discuss [tradeoff/eval/rollout]."

## After every major decision boundary, or whenever GPT could materially change the next action
End with a paste-ready GPT prompt in a code block: what changed, results, caveats, one focused question, and an invitation to push back on overclaiming.
- Short output: inline. Long output or screenshots: ONE PDF (`kit/handoff.py`) via SendUserFile.
- Send only what's new; never restate the case. Never rely on artifact links for GPT.

## Operating principles
1. The real bottleneck, not the most interesting problem.
2. Name the decision each output enables.
3. The smallest useful artifact.
4. Label assumptions; thresholds and domain rules are "prototype defaults".
5. A concrete verification step before moving on.
- Decide and state the tradeoff; no broad frameworks.
- No new features before the core workflow works end to end.
- Unfamiliar operations: briefly map inputs → transformations → handoffs → failure points → decision. Research only the 2–3 facts that could change the product.

## Pre-flight (before the interview)
- Regular Chrome profile; Claude in Chrome connected. Publish a tiny `sample` test page; the user clicks Continue once. Headless Chrome + Playwright work.
- Company research: 5–8 sourced lines; label company-reported numbers as claims. Frame work in the company's terms (their roles, clients, reviewer bar) without branding the app as the company.

## Delivery lifecycle (default enterprise flow)
Business / user requirements → User stories → Analysis → **reqs.md + tasks.md** → Design + architecture → **design.md** → Code → Unit testing → Test environments / QA → UAT → Productionalize → Production.
**CI/CD + DevOps spans Code through Production:** build → test → eval → package → deploy to environments → approvals → production.
- **Requirements:** user/job, current workflow, pain point, business outcome, constraints, success criteria.
- **User stories:** "As a [user], I want [capability], so that [outcome]."
- **reqs.md:** functional + non-functional requirements, acceptance criteria, edge cases, source-of-truth rules, autonomy boundaries, safety requirements, metrics/guardrails, assumptions + open questions. (Doubles as the compact PM spec; PASS IF lives here.)
- **tasks.md:** implementation tasks, dependencies, sequencing, test requirements, explicit cuts/non-goals.
- **design.md (only what's relevant):** UX/workflow, system architecture, workflow vs agent vs multi-agent choice, model/prompt/context, data model, tools/APIs/MCP, infrastructure, security/permissions, observability, retries/idempotency, safety gates/kill switch, deployment.
- **Code:** smallest complete workflow first.
- **Unit testing:** functions, schemas, deterministic rules, state transitions, safety gates, tool wrappers.
- **Test environments / QA:** integration, end-to-end, regression, adversarial, model variability, retries/timeouts, duplicate actions, prompt injection, agent orchestration failures.
- **UAT (user acceptance testing):** business/domain users validate correctness, usability, business rules, exceptions, and whether it solves the real problem.
- **Productionalize:** scaling, secrets/config, monitoring, alerts, rollback, runbooks, permissions, audit, deployment readiness, reliability/performance.
- **Production:** controlled rollout (shadow → pilot → phased autonomy), observability, business + safety metrics, online evals, feedback loop.
- **AI evals span stages:** prompt/model evals in Code; blind, adversarial and regression evals in QA; expert validation in UAT; online evals in Production.
- **Live 60-minute compression:** actually create lightweight user stories, reqs.md, tasks.md and design.md (about one page total, written in one pass, `kit/mas/spec.py` pattern); build, unit-test and QA-test the prototype; *explain* UAT and productionalization, never pretend they happened. Speed over document polish.

## Timeline (60 min)
1. **0–5 Discovery:** only the 3 questions that change what we build, how autonomous it is, or what success means.
2. **5–12 Framing (<400 words):** workflow, bottleneck, 2–3 approaches with tradeoffs, recommendation, smallest MVP, biggest assumption, Automate / Suggest / Human split, named reviewer bar.
3. **12–15 Scope lock. The only mandatory artifacts (lightweight, one pass):**
   - User stories + reqs.md (the compact PM spec, including PASS IF: Outcome / Safety / Process / Efficiency) + tasks.md.
   - design.md, with the architecture choice also stated aloud (see Architecture choice).
   - Frozen expected outcome, if we're about to eval.
   No pre-build deck. No mandatory diagrams.
4. **15–35 Build:** one self-contained HTML page, published as an artifact. Core workflow first.
5. **35–45 Real AI + eval:** live call (`sample`, `cache:false`), same schema, in-app scorecard.
6. **45–52 Stress test** at the depth time allows (see Eval).
7. **52–60 Present:** from the app. 4-slide results deck only if the product and eval already work and time permits. One-page AI PRD only if time remains after that.

## Architecture choice (decide fresh every case)
Choose among: **deterministic software/workflow · workflow + bounded model calls · single agent with bounded tools · multi-agent system · mixed.**
Decide on: workflow variability, tool use, permission boundaries, need for independent verification, and the consequence of error. Say the choice and the one-line reason aloud.
- Do not add agents to demonstrate sophistication.
- **One architecture diagram, only if it materially helps explain a product or technical decision.**

## Eval (time-adaptive)
**Minimum (always):**
- Expected result frozen before any run (chmod 444 + sha256), never shown to the model.
- One representative blind/adversarial test.
- Score the outcome AND the path taken.
- Fix consequential failures and replay.
**If time:** more edge/adversarial cases; repeated uncached live runs; a broader regression suite. Don't force 3 live runs when rate limits, latency or remaining time make them low value.
- **Presentation must show "Evals we ran, and why":** each eval tied to the risk it tests and its result, plus "planned, not run, and why." The user articulates these decisions live (feed them through WHILE I BUILD → SAY) and lands them in the demo.
- Run what's possible offline: e.g., DeepEval's ToolCorrectnessMetric is deterministic (pass a stub model so it never needs an API key) and works on recorded live traces. Tools that need keys or servers (promptfoo red team, LLM-judged metrics, Langfuse) stay "planned" unless actually run.
- Synthetic evals are development evidence, not production validation; say so.

## Build defaults
- Layers: source → AI (JSON) → deterministic rules → review UI. Only the AI step changes when going live.
- Exact quotes verified against the source; unverified → Needs review. Safety never depends on model confidence.
- Validate AI output; one bad item never breaks the run; never silently coerce; a check that can't run fails safe.
- **Safety checks never depend on model success:** run backstops on raw input or after every outcome, including agent failure.
- Kill switch / rollback for any external or consequential action. A person approves external sends.
- Raw-output panel; saved sample as offline fallback; persist live runs to the artifact `db` and read them with `db_query` to score.
- Back off on `rate_limited`; never loop.
- Polish last: readable type, one-line thesis under the header, a plain-English "what happened" per item.

## Testing before every publish
Headless Playwright: renders, controls work, no console errors. Engine/adversarial tests green. Frozen files unchanged. Report failures and untested items, not just passes.

## GLOBAL STOP RULE
Once the core workflow works, the riskiest assumption has been tested, a consequential failure has been fixed and replayed, and the demo is stable: **STOP BUILDING.** Freeze the published version.

## UI that explains itself (learned in Mock 4)
The interviewer should understand the product without you explaining it; less to explain means less to fumble live.
- **"▶ Start demo" overlay** on top of the normal app: 5–6 steps in the story order, each with a title plus one-line caption and Next/Back. The app underneath stays fully usable.
- **Recorded live run built in** as the default for the hard case (labeled "recorded live run, time"), so the demo is instant and never depends on the model responding live. Live mode stays one click away.
- **A drill button** that reproduces the key failure safely, for the "show the fix" step.
- **"Your next step" on every item**: the concrete action for the end user (e.g., a risk advisor). This is what makes it a useful product, not just a pipeline.
- **Headline visible, depth one click away:** short status line, ≤5 status chips, one-line story items, ✓/✗ pills; plan, gate detail, judge output, drafts, prompts, skills, spec and production path behind "Details" toggles.
- **Primary actions only in the toolbar** (Start demo, case switch, run, drill); everything else under an "Advanced" menu that closes on outside click.
- Frame all copy in the company's roles and clients (e.g., "risk advisor") without branding the app as the company.

## Show the layers and the ground truth
- **Frontend vs backend, visibly:** tag every panel (Frontend = what the end user sees and approves; Backend = agents, workflow engine, gates, records) and add a Both / Frontend / Backend view toggle. The guided demo shows the frontend step, then the backend step. Say honestly where both run (a prototype page) and what the backend becomes in production.
- **Ground truth, visibly:** a "Ground truth data" panel with (1) the frozen expected outcome (hash, "never shown to a model") and (2) the system-of-record data drafts and gates must match. The eval table shows **Expected (frozen) vs Actual vs Result** per check. State its limits: synthetic and self-written until domain experts label real cases.
- **"What's real, mocked, not built"** table, one click away.

## Presenting (5-minute overview; 15–20 minutes with discussion)
Plan for a ~5-minute overview that can stretch to 15–20 minutes with interviewer discussion; pause on any step. Order: problem + product choice → architecture in one sentence → hardest case → the most useful failure + fix (shown live if possible) → evidence → path (labeled real requests → shadow mode → pilot → expand by request type).
- Give the user a **one-page demo card**: ~8 rows, one click and one line each.
- On the demo card, add one sentence per eval on **why that eval over the alternatives** (e.g., deterministic scoring when the output is objectively checkable; an LLM judge only for free text, as one gate), plus the sample-size caveat.
- Before the real demo, make a **walkthrough PDF for GPT** (`kit/handoff.py`): every slide, a screenshot of each guided demo step with its caption, and the demo card. Ask GPT to coach delivery: per-step script with pauses, where you'd ramble or overclaim, the toughest questions with short answers, and how to stretch to 15–20 minutes.
- Optional, if time: a 4-slide deck (`kit/demo_deck/`): exec summary · simple architecture · hardest case + failure/fix · evidence + path.
- **Claim discipline:** "every completed model run passed the N frozen checks"; "development evidence on one synthetic scenario"; say which fixes were live-verified versus offline only; qualify an LLM judge as "same vendor" unless it isn't; never "production-ready", "fully validated" or "proven reliable".
- If asked about production: walk the delivery lifecycle from where the prototype stops (unit testing + part of QA) through full QA in test environments, UAT with domain users on real cases, productionalize, and a controlled production rollout, with CI/CD + DevOps and evals spanning all of it.

## REFERENCE PATTERN — use only when the case warrants it (validated in Mock 4)
Multi-agent, code-enforced. Templates in `kit/mas/`.
- **Orchestrator agent** splits the input into typed tasks with quotes and proposes a route per task. **Workflow engine (code)** checks the plan against policy and overrides it; it owns state, retries, dedupe, idempotency, audit and the kill switch.
- **Specialist agents** with tool permissions in code: context (read-only lookups), drafting (no tools), **LLM judge** (re-fetches every record the draft cites; same vendor in the prototype).
- **Code gates** for consequential conditions; the judge's verdict is one gate, not the only one.
- Code guards on raw input: injection flag (no effect on permissions), incident backstop, fingerprint dedupe. Tool timeouts: retry with backoff, then escalate. Every task ends in exactly one valid state.
- Mock 4 blind case: a multi-request email with a buried claim, unsupported wording, "skip review", a resend and a tool timeout.
- Mock 4 lessons: backstops must run even when the agent fails (found via rate limits); the judge must fetch everything the draft cites; prompt changes can regress, so version prompts and replay.

## Borrowed practices (Product Compass / product-engineering)
- **PM eval routine:** review traces → label → error analysis → change prompt or code → replay. Evals need domain judgment; the PM owns them.
- **Context before requirements:** capture users, problems, jobs and out-of-scope first; mark your own solution idea as non-binding and ask the agent for alternatives.
- **The product is the spec:** review the prototype and artifacts (permissions table, intended-vs-implemented), not the code.
- **The writer never reviews its own work:** separate builder and reviewer (GPT, or a fresh session); same idea as the LLM judge.
- **Every fix lands with a test that failed before the fix.**
- **Rules keep their receipts:** each lesson in `LESSONS.md` records the date and the observed failure.
- **Stop-and-check:** verify prerequisites, plan in one page, build, run, then stop for review.
- **Swappable data sources:** tools behind an interface so mocks can be replaced by real systems.
- **Check data access rules before sharing** anything with real data.

## Starter kit (`/home/claude/kit`; unzip the skill pack there if missing)
- `app_template.html` (document review), `app_template_mapping.html` (column mapping), `app_template_reconciliation.html`.
- `mas/` (reference multi-agent pattern: app, tests, diagram generators, spec generator, agent skills). Paths point at /home/claude/mock4; adjust.
- `demo_deck/` (4-slide template), `render_deck.py`, `handoff.py`, `freeze.sh`, `test_app.py`, `PM_SPEC_TEMPLATE.md`, `ONE_PAGE_AI_PRD_TEMPLATE.md`, `PROMPT_TEMPLATES.md`, `LESSONS.md`.

## End of every mock
Once Claude and GPT finish iterating and the demo is ready: give the user an updated SKILL.md plus the skill-pack zip (they pass it to other Claude sessions). **GitHub is the last step, only after the demo is produced** (app, slides, demo card, walkthrough PDF): then a private repo with a README that shows the overview, diagrams, a demo sample, methods, evals and the most useful failure; never spend interview time on it before the demo is ready. Append worked / failed / stop-doing to `kit/LESSONS.md`.

## Avoid
- Overbuilding: extra agents, diagrams, decks or panels before the core workflow and eval work.
- Clicking consent prompts or granting permissions for the user.
- Changing frozen answer keys, prompts or untouched rules when told not to.
- Overclaiming domain rules or results.
