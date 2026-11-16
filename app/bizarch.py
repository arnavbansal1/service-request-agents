from html import escape as e
C = {"person":("#E1F5EE","#0F6E56","#04342C"),"agent":("#EEEDFE","#534AB7","#26215C"),"code":("#F1EFE8","#5F5E5A","#2C2C2A"),"ext":("#FFFFFF","#8A887F","#2C2C2A"),"kpi":("#FAEEDA","#9A5B00","#4A2B00")}
STAKE = [("ext","Client (insured)","Sends requests"),("ext","Certificate holder","Landlord, shipper"),("ext","Carrier","Endorsements, claims"),
         ("person","Risk advisor","Approves every send"),("person","Claims advisor","Owns possible claims"),("person","Firm leadership","E&O risk, capacity")]
STAGES = [("Receive","Email or portal","code","Dedupe, scan"),("Understand","Split and type","agent","Orchestrator agent"),("Gather context","Policy, holder","agent","Context agent"),
          ("Fulfill","Certificate or reply","agent","Fulfillment agent"),("Review","Grounded check","agent","LLM judge + code gates"),("Deliver","Send, update client","person","Person approves")]
CAPS = [("Certificates","agent","Agents draft, person OKs"),("Policy questions","agent","Agents draft, person OKs"),("Possible claims","person","Escalated at once"),
        ("Coverage changes","person","To risk advisor"),("Billing","person","To billing team"),("Risk requests","person","To an advisor")]
KPIS = ["Turnaround per request","Drafts approved without edits","Wrong sends (E&O): 0","Claim escalation time","Service hours freed"]
def box(o,x,y,w,h,k,t,sub,fs=21):
    f,s,c=C[k]; o.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="10" fill="{f}" stroke="{s}" stroke-width="2"/>')
    o.append(f'<text x="{x+w/2:.1f}" y="{y+h/2-4 if sub else y+h/2+7}" text-anchor="middle" font-family="Inter, sans-serif" font-size="{fs}" font-weight="700" fill="{c}">{e(t)}</text>')
    if sub: o.append(f'<text x="{x+w/2:.1f}" y="{y+h/2+20}" text-anchor="middle" font-family="Inter, sans-serif" font-size="16.5" fill="{s}">{e(sub)}</text>')
def row(o,y,label,items,h,k_of,t_of,s_of,lbl=210,W=1664,fs=21):
    o.append(f'<text x="0" y="{y+h/2+8}" font-family="Inter, sans-serif" font-size="22" font-weight="700" fill="#16213A">{e(label)}</text>')
    n=len(items); g=12; bw=(W-lbl-(n-1)*g)/n
    for i,it in enumerate(items): box(o,lbl+i*(bw+g),y,bw,h,k_of(it),t_of(it),s_of(it),fs)
    return bw
def svg():
    W=1664; o=[f'<svg class="arch" viewBox="0 0 {W} 640" role="img" aria-label="Business architecture: stakeholders, a six-stage value stream from receive to deliver showing which stages agents, code or people perform, capabilities split between agents and people, and the outcomes measured.">',
             '<defs><marker id="ba-ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1L9 5L1 9z" fill="#7A7870"/></marker></defs>']
    row(o,0,"Stakeholders",STAKE,78,lambda i:i[0],lambda i:i[1],lambda i:i[2])
    y=120; o.append(f'<text x="0" y="{y+22}" font-family="Inter, sans-serif" font-size="22" font-weight="700" fill="#16213A">Value stream</text><text x="0" y="{y+48}" font-family="Inter, sans-serif" font-size="16" fill="#5B6476">request → resolved</text>')
    n=len(STAGES); g=26; lbl=210; bw=(W-lbl-(n-1)*g)/n
    for i,(t,sub,k,who) in enumerate(STAGES):
        x=lbl+i*(bw+g); f,s,c=C[k]
        o.append(f'<path d="M{x:.1f} {y} h{bw-14:.1f} l14 40 l-14 40 h-{bw-14:.1f} l14 -40 z" fill="#FFFFFF" stroke="#B4B2A9" stroke-width="2"/>')
        o.append(f'<text x="{x+bw/2+4:.1f}" y="{y+36}" text-anchor="middle" font-family="Inter, sans-serif" font-size="20" font-weight="700" fill="#16213A">{e(t)}</text><text x="{x+bw/2+4:.1f}" y="{y+60}" text-anchor="middle" font-family="Inter, sans-serif" font-size="15.5" fill="#5B6476">{e(sub)}</text>')
        o.append(f'<rect x="{x:.1f}" y="{y+94}" width="{bw:.1f}" height="44" rx="8" fill="{f}" stroke="{s}" stroke-width="2"/><text x="{x+bw/2:.1f}" y="{y+122}" text-anchor="middle" font-family="Inter, sans-serif" font-size="15.5" font-weight="700" fill="{c}">{e(who)}</text>')
    y=310; row(o,y,"Capabilities",CAPS,78,lambda i:i[1],lambda i:i[0],lambda i:i[2])
    y=420; o.append(f'<text x="0" y="{y+46}" font-family="Inter, sans-serif" font-size="22" font-weight="700" fill="#16213A">Outcomes</text>')
    n=len(KPIS); g=12; bw=(W-210-(n-1)*g)/n
    for i,k in enumerate(KPIS): box(o,210+i*(bw+g),y+10,bw,64,"kpi",k,"",19)
    y=530; L=[("agent","Agent (Claude)"),("code","Code: workflow engine, gates"),("person","Person"),("ext","Outside the agency"),("kpi","Measured outcome")]
    x=210
    for k,t in L:
        f,s,c=C[k]; o.append(f'<rect x="{x}" y="{y}" width="26" height="26" rx="6" fill="{f}" stroke="{s}" stroke-width="2"/><text x="{x+36}" y="{y+20}" font-family="Inter, sans-serif" font-size="17" fill="#3D4454">{e(t)}</text>'); x+=36+len(t)*9.6+40
    o.append(f'<text x="210" y="{y+70}" font-family="Inter, sans-serif" font-size="18" fill="#3D4454">Agents take the reading and drafting. People keep judgment, client relationships and every send.</text><text x="210" y="{y+96}" font-family="Inter, sans-serif" font-size="18" fill="#3D4454">Claims and coverage changes stay with people until evidence says otherwise.</text>')
    o.append('</svg>'); return "".join(o)
