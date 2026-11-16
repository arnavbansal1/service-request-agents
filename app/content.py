import re, pathlib, sys
sys.path.insert(0,'/home/claude/mock4/app')
from techstack import svg as ts_svg, table as ts_table
from bizarch import svg as biz_svg
src = pathlib.Path('/home/claude/deck5/project/slides/architecture.html').read_text()
ARCH_SVG = '<p style="margin:0 0 10px"><b>Frontend</b> = the advisor console (inbox, task cards, approve). <b>Backend</b> = agents, workflow engine, safety gates, tools and records. In this prototype both run inside one page; in production the backend runs as the services in diagram 3.</p><h4 style="margin:4px 0">1 · Business architecture: stakeholders, value stream, who owns what</h4>' + biz_svg() + '<h4 style="margin:18px 0 4px">2 · Process flow: agents, code and people</h4>' + re.search(r'<svg class="arch".*?</svg>', src, re.S).group(0)
ARCH_SVG += '<h4 style="margin:18px 0 4px">3 · Technical architecture: services and tech stack</h4>' + ts_svg() + ts_table() + '''<h4 style="margin:18px 0 4px">4 · Layer ownership</h4><table class="sc" style="margin-top:8px"><tr><th>Layer</th><th>Owns</th><th>Production equivalent</th></tr>
<tr><td><b>Orchestrator agent</b></td><td>Splits the email, types tasks, proposes a route per task</td><td>Claude, versioned prompt</td></tr>
<tr><td><b>Workflow engine (code)</b></td><td>Checks the plan against policy; state machine, retries, deduplication, kill switch, audit</td><td>Durable workflow engine such as Temporal</td></tr>
<tr><td><b>Agents (Claude)</b></td><td>Reading, choosing lookups, drafting, LLM-as-judge review</td><td>Model gateway with versioned prompts</td></tr>
<tr><td><b>Policy as code</b></td><td>Which agent may call which tool, call budgets</td><td>Policy engine such as OPA (Open Policy Agent) or Cedar</td></tr>
<tr><td><b>Safety gates (code)</b></td><td>Wording, policy match, holder requirements, evidence, numbers, QA verdict</td><td>Same rules, owned by the service lead, unit-tested in CI</td></tr>
<tr><td><b>Trace</b></td><td>Every agent call, tool call, state change, gate and retry</td><td>OpenTelemetry into Langfuse, LangSmith, Arize Phoenix or Datadog</td></tr>
<tr><td><b>Evals</b></td><td>Blind cases scored against an outcome frozen before any run</td><td>Eval suite as a CI/CD gate; second-vendor judge</td></tr></table>'''
HOW_HTML = '''
<p><b>For risk advisors:</b> agents take the reading, lookups and drafting; you keep judgment, client relationships and every send. Reviewer bar: <i>would a risk advisor send this without edits?</i></p>
<ul><li>Code dedupes resends and flags instructions in client text.</li><li>Agents split the email, look up records, draft, and an LLM judge (same vendor) reviews.</li><li>Code gates block anything unsupported; claims escalate first, even if the agent fails.</li><li>You approve every send; it sends once.</li></ul>
<details><summary><b>What's real, mocked and not built</b></summary>
<table class="sc"><tr><th>Real in this prototype</th><th>Mocked</th><th>Not built yet</th></tr>
<tr><td>Agents (live Claude, or a recorded live run) · workflow engine and state machine · tool permissions · safety gates · dedupe, retries, kill switch · trace · scorer · approve and send-once logic</td>
<td>Client emails · agency system records · the send itself (recorded only; nothing leaves) · the lookup timeout (injected)</td>
<td>Real email and portal intake · sign-in and roles · a second-vendor judge · monitoring and alerts · UAT with advisors</td></tr></table>
<p class="note">Lookups go through a tool interface, so the mock records can be swapped for the real agency system without changing the agents.</p></details>
<details><summary><b>Path to production</b></summary>
<p>Built so far: code, unit testing and part of QA. Next: full QA in test environments → UAT (user acceptance testing) with advisors on real requests → productionalize (monitoring, alerts, rollback, permissions) → controlled rollout: shadow mode, then a certificates pilot, then more request types. CI/CD (continuous integration / delivery) runs through all of it.</p></details>
<p class="note">Thresholds and wording rules are prototype defaults, not the agency's rules.</p>'''
