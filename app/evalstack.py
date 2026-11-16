from html import escape as e
RAN = [
 ("Frozen blind case (outcome + path)","Tests the riskiest thing, orchestration, end to end, with the answer fixed before any run","Every completed model run passed the 8 checks"),
 ("Adversarial suite + outage drill","The costly failures: a missed claim, injected instructions, duplicate sends, timeouts","44 engine/adversarial + 25 UI tests passing; found the backstop bug"),
 ("LLM judge on every draft","Free-text drafts need a grounded check; it's one gate, and code still decides (same vendor today)","Grounded drafts checked; same-vendor judge used as one gate"),
 ("DeepEval tool correctness (10 live runs)","Did the context agent fetch the records a certificate needs? Deterministic, no LLM grader","context@v2: 1/3 (regression caught) → v3: 3/3"),
]
PLANNED = [
 ("promptfoo red team in CI","Needs a model API key; most valuable across many attack variants"),
 ("DeepEval LLM metrics (faithfulness, G-Eval)","Need a second-vendor judge key; calibrate against advisor ratings first"),
 ("Langfuse online evals","Needs a hosted server; the trace export is already OpenTelemetry-shaped"),
]
def html():
    r="".join(f"<tr><td><b>{e(a)}</b></td><td>{e(b)}</td><td>{e(c)}</td></tr>" for a,b,c in RAN)
    p="".join(f"<tr><td><b>{e(a)}</b></td><td>{e(b)}</td></tr>" for a,b in PLANNED)
    return ('<h4 style="margin:16px 0 6px">Evals we ran, and why</h4>'
            '<p class="note" style="margin:0 0 6px"><b>How:</b> review the traces → label what went wrong → find the cause → change the prompt or code → add a test that fails without the fix → replay.</p>'
            f'<table class="sc"><tr><th>Eval</th><th>Why this one</th><th>Result</th></tr>{r}</table>'
            '<details style="margin-top:10px"><summary><b>Planned for production</b> (not run here, and why)</summary>'
            f'<table class="sc"><tr><th>Eval</th><th>Why not yet</th></tr>{p}</table></details>')
