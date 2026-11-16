import json, hashlib, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from content import ARCH_SVG, HOW_HTML
from evalstack import html as evalstack_html
from spec import spec_html, write_md
import re as _re
C = pathlib.Path('/home/claude/mock4/case'); A = pathlib.Path('/home/claude/mock4/app')
def j(p): return json.loads(p.read_text())
sha = hashlib.sha256((C/'blind_expected_v1.json').read_bytes()).hexdigest()
def _skill(p):
    t=p.read_text(); m=_re.match(r'---\n(.*?)\n---\n(.*)',t,_re.S); meta=dict(l.split(': ',1) for l in m.group(1).splitlines()); return meta['name'],{'version':meta['version'],'used_by':meta['used_by'],'body':m.group(2).strip()}
skills=dict(_skill(p) for p in sorted((A/'skills').glob('*.md')))
write_md()
block = (f"const AMS={json.dumps(j(C/'ams.json'))};\nconst INBOX={json.dumps(j(C/'inbox.json'))};\n"
         f"const EXPECTED={json.dumps(j(C/'blind_expected_v1.json'))};\nconst EXPECTED_SHA={json.dumps(sha)};\n"
         f"const SKILLS={json.dumps(skills)};\nconst SPEC_HTML={json.dumps(spec_html())};\nconst EVALSTACK_HTML={json.dumps(evalstack_html())};\nconst SAVED={json.dumps(j(A/'saved.json'))};\nconst ARCH_SVG={json.dumps(ARCH_SVG)};\nconst HOW_HTML={json.dumps(HOW_HTML)};\n")
out = (A/'body.html').read_text().replace('/*__DATA__*/', block)
(A/'index.html').write_text(out)
print('built', len(out), 'bytes; expected sha', sha[:12])
