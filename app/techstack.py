import pathlib as _pl
HERE = _pl.Path(__file__).resolve().parent
ROOT = HERE.parent
# Services + tech stack architecture (hardcoded colors so it renders in app, slides and PDF)
from html import escape as e
STY = {"ext":("#FFFFFF","#8A887F","#2C2C2A"),"code":("#F1EFE8","#5F5E5A","#2C2C2A"),"agent":("#EEEDFE","#534AB7","#26215C"),
       "human":("#E1F5EE","#0F6E56","#04342C"),"data":("#E6F1FB","#1E6091","#0B2F4D"),"ops":("#FAEEDA","#9A5B00","#4A2B00")}
BANDS = [
 ("Channels", [("ext","Email inbox","Microsoft Graph or Gmail API webhook"),("ext","Client portal","REST API (application programming interface)")]),
 ("Ingestion", [("code","API gateway","Auth, rate limits"),("code","Message queue","Amazon SQS or Kafka"),("data","Idempotency store","Redis: email fingerprints")]),
 ("Workflow", [("code","Workflow engine (code)","Temporal: checks the plan, state, retries"),("code","Kill switch","Feature flag, e.g. LaunchDarkly")]),
 ("Agents", [("agent","Orchestrator","agent · plans"),("agent","Context","agent · lookups"),("agent","Fulfillment","agent · drafts"),("agent","LLM judge","agent · verifies"),("ext","LLM gateway","→ Claude models")]),
 ("Guardrails", [("code","Policy engine","OPA or Cedar: tool permissions"),("code","Safety gates","Deterministic rules, unit-tested"),("code","Input scanner","Injection and PII checks")]),
 ("Tools (MCP)", [("data","Agency system, read-only","Applied Epic or AMS360"),("code","Certificate builder","ACORD 25 form"),("human","Send service","Runs only after approval, once")]),
 ("People + data", [("human","Review console","Approve, reject, edit"),("data","Postgres","Tasks, state history, audit log"),("data","Object store","Emails, drafts (S3)")]),
]
SIDE = [
 ("Observability", "ops", ["OpenTelemetry collector","Langfuse or LangSmith: agent traces","Datadog: infrastructure and alerts"]),
 ("Evals and delivery", "ops", ["CI/CD in GitHub Actions","Eval suite as a merge gate","Prompt registry, versioned","Second-vendor judge (GPT)"]),
 ("Security", "ops", ["SSO (single sign-on), e.g. Okta","Secrets in KMS or Vault","Least-privilege service accounts","Data retention and vendor terms"]),
]
def svg():
    W, MAINW, LBL, BH, GAP = 1664, 1190, 222, 86, 30
    H = len(BANDS)*(BH+GAP) - GAP + 4
    o = [f'<svg class="arch" viewBox="0 0 {W} {H}" role="img" aria-label="Services architecture: channels feed an API gateway and queue; a Temporal workflow engine runs four Claude agents through an LLM gateway; a policy engine, safety gates and an input scanner guard tools exposed over MCP; a review console, Postgres and object storage hold people and data; observability, evals and security run across all layers.">',
         '<defs><marker id="ts-ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1L9 5L1 9z" fill="#7A7870"/></marker></defs>']
    for i,(name,boxes) in enumerate(BANDS):
        y = i*(BH+GAP)+2
        o.append(f'<rect x="0" y="{y}" width="{MAINW}" height="{BH}" rx="14" fill="{"#F7F7F3" if i%2==0 else "#FFFFFF"}" stroke="#E1E2DB" stroke-width="2"/>')
        o.append(f'<text x="18" y="{y+BH/2+8}" font-family="Inter, sans-serif" font-size="23" font-weight="700" fill="#16213A">{e(name)}</text>')
        n=len(boxes); avail=MAINW-LBL-14; g=12; bw=(avail-(n-1)*g)/n
        for j,(k,t,sub) in enumerate(boxes):
            f,s,c = STY[k]; x = LBL + j*(bw+g); by=y+9; bh=BH-18
            o.append(f'<rect x="{x:.1f}" y="{by}" width="{bw:.1f}" height="{bh}" rx="10" fill="{f}" stroke="{s}" stroke-width="2"/>')
            cx = x+bw/2
            if sub:
                o.append(f'<text x="{cx:.1f}" y="{by+29}" text-anchor="middle" font-family="Inter, sans-serif" font-size="21" font-weight="700" fill="{c}">{e(t)}</text>')
                o.append(f'<text x="{cx:.1f}" y="{by+55}" text-anchor="middle" font-family="Inter, sans-serif" font-size="16.5" fill="{s}">{e(sub)}</text>')
            else:
                o.append(f'<text x="{cx:.1f}" y="{by+bh/2+8}" text-anchor="middle" font-family="Inter, sans-serif" font-size="21" font-weight="700" fill="{c}">{e(t)}</text>')
        if i < len(BANDS)-1:
            o.append(f'<line x1="{LBL-26}" y1="{y+BH+3}" x2="{LBL-26}" y2="{y+BH+GAP-3}" stroke="#7A7870" stroke-width="2.5" marker-end="url(#ts-ah)"/>')
    sx, sw = MAINW+34, W-MAINW-36
    sh = (H - 2*24)/3
    for i,(name,k,items) in enumerate(SIDE):
        f,s,c = STY[k]; y = i*(sh+24)+2
        o.append(f'<rect x="{sx}" y="{y:.1f}" width="{sw}" height="{sh:.1f}" rx="14" fill="{f}" stroke="{s}" stroke-width="2"/>')
        o.append(f'<text x="{sx+20}" y="{y+38:.1f}" font-family="Inter, sans-serif" font-size="23" font-weight="700" fill="{c}">{e(name)}</text>')
        for m,it in enumerate(items):
            o.append(f'<text x="{sx+20}" y="{y+76+m*34:.1f}" font-family="Inter, sans-serif" font-size="18.5" fill="{c}">· {e(it)}</text>')
    o.append(f'<text x="{sx+sw/2}" y="{H-2}" text-anchor="middle" font-family="Inter, sans-serif" font-size="15" fill="#5B6476">Across every layer</text>')
    o.append('</svg>')
    return "".join(o)
PROTO_ROWS = [
 ("Channels","Fictional inbox (JSON)","Email webhook + portal API"),
 ("Workflow engine","State machine in the page (JavaScript)","Temporal workflow workers"),
 ("Agents","Claude via the artifact's Claude access","Claude via LLM gateway, prompt registry"),
 ("Permissions","Policy table in code","OPA or Cedar policy service"),
 ("Tools","Mock read-only agency records","MCP servers over Applied Epic or AMS360"),
 ("Dedupe","In-memory fingerprints","Redis idempotency keys"),
 ("Trace","OpenTelemetry-shaped spans, JSON export","OTel collector → Langfuse / Phoenix / Datadog"),
 ("Evals","Frozen blind case, scored in app","Eval suite in CI, merge gate, shadow-mode metrics"),
 ("Run history","Artifact database","Postgres audit log"),
]
def table():
    r = "".join(f"<tr><td><b>{e(a)}</b></td><td>{e(b)}</td><td>{e(c)}</td></tr>" for a,b,c in PROTO_ROWS)
    return f'<table class="sc" style="margin-top:8px"><tr><th>Layer</th><th>In this prototype</th><th>In production</th></tr>{r}</table>'
if __name__ == "__main__":
    import pathlib; (HERE/'techstack.svg').write_text(svg()); print(len(svg()))
