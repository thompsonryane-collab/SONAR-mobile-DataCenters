#!/usr/bin/env python3
"""Assemble the standalone data-center repo (thompsonryane-collab/sonar-mobile-dc).
Inputs (built earlier in /home/claude/dc): SONAR-DataCenter-Console.html, dc.html (cmdr/datacenter.html upload),
dcmap.html, tools/*.py, face/ (fetched from justadudewhohacks/face-api.js).  Output: /home/claude/repo/"""
import os, re, json, shutil, html
from PIL import Image, ImageDraw
SRC='/home/claude/dc'; OUT='/home/claude/repo'
ORG='thompsonryane-collab'; REPO='sonar-mobile-dc'
PAGES='https://%s.github.io/%s/'%(ORG,REPO); OLDPAGES='https://thompsonryane-collab.github.io/ie-SRS/'
V='20260921'
for d in ['cmdr','data','docs/blackstart','tools']: os.makedirs(os.path.join(OUT,d),exist_ok=True)

def rep(s,a,b,n=1,tag=''):
    c=s.count(a)
    if c!=n: raise SystemExit('REP MISS %s: expected %d got %d :: %r'%(tag,n,c,a[:80]))
    return s.replace(a,b)

# ── console ───────────────────────────────────────────────────────────────────
c=open(os.path.join(SRC,'SONAR-DataCenter-Console.html'),encoding='utf-8').read()
c=rep(c,"repo:'thompsonryane-collab/ie-SRS', branch:'main', path:'data/bus.json'","repo:'%s/%s', branch:'main', path:'data/bus.json'"%(ORG,REPO),tag='console bus repo')
c=rep(c,"return 'https://thompsonryane-collab.github.io/ie-SRS/cmdr/datacenter.html';","return '%scmdr/datacenter.html';"%PAGES,tag='console phone url fallback')
c=rep(c,"  const pdfUrl = 'https://thompsonryane-collab.github.io/ie-SRS/docs/ie-SRS-ADMIN-Users-Guide.pdf';\n  window.open(pdfUrl, 'ie-SRS-ADMIN-Guide', 'width=1000,height=800,resizable=yes,scrollbars=yes');",
        "  window.open('docs/console-guide.html', 'SONAR-mobile-DC-Guide', 'width=1000,height=800,resizable=yes,scrollbars=yes');",tag='console guide')
c=rep(c,'href="apple-touch-icon.png?v=20260908"','href="apple-touch-icon.png?v=%s"'%V,tag='console icon bust')
c=rep(c,'window.__DC_CONSOLE_BUILD="2026-09-21";','window.__DC_CONSOLE_BUILD="2026-09-21 · %s";'%REPO,tag='build marker')
# the drill builder's chain-of-command defaults come from the phone · same fix on both
BR=[('id=&quot;wo-recip&quot; value=&quot;Installation CO · NAVFAC · DLA Energy&quot;','id=&quot;wo-recip&quot; value=&quot;Facility Director · NOC · Utility provider&quot;'),
    ('id=&quot;notif-recipients&quot; style=&quot;min-height:44px&quot;&gt;NAVFAC Atlantic · CINCLANTFLT · Installation CO · DLA Energy&lt;','id=&quot;notif-recipients&quot; style=&quot;min-height:44px&quot;&gt;Facility Director · NOC · Customer Success · Utility provider&lt;')]
for a,b in BR: c=rep(c,a,b,tag='console builder recipients')
open(os.path.join(OUT,'SONAR-DataCenter-Console.html'),'w',encoding='utf-8').write(c)

# ── phone (cmdr/datacenter.html) ─────────────────────────────────────────────
p=open(os.path.join(SRC,'dc.html'),encoding='utf-8').read()
p=rep(p,"repo:'thompsonryane-collab/ie-SRS', branch:'main', path:'data/bus.json'","repo:'%s/%s', branch:'main', path:'data/bus.json'"%(ORG,REPO),tag='phone bus repo')
p=rep(p,"window.open('https://thompsonryane-collab.github.io/ie-SRS/docs/cmdr-guide.html','ie-SRS-SONARmobile-Guide')","window.open('../docs/phone-guide.html','SONARmobile-DC-Guide')",tag='phone guide')
p=rep(p,'href="manifest.json?v=20260914d"','href="manifest.json?v=%s"'%V,tag='phone manifest bust')
for old in ['../favicon.svg?v=20260910','../favicon.ico?v=20260910','../favicon-32x32.png?v=20260910','../favicon-16x16.png?v=20260910','../apple-touch-icon.png?v=20260910']:
    p=rep(p,old,old.replace('20260910',V),tag='phone icon bust')
p=rep(p,'<title>SONARmobile · Data Center · sample','<title>SONARmobile · Data Center',tag='phone title')
for a,b in BR: p=rep(p,a,b,tag='phone builder recipients')
# the pitch video still lives in the ie-SRS repo · PUB stays; make that explicit
p=rep(p,"  var PUB='https://thompsonryane-collab.github.io/ie-SRS/';","  var PUB='https://thompsonryane-collab.github.io/ie-SRS/';   /* pitch/SONARmobile-release.html is published from the ie-SRS repo */",tag='phone pitch PUB note')
open(os.path.join(OUT,'cmdr','datacenter.html'),'w',encoding='utf-8').write(p)

# ── icons (Pillow · no cairosvg here) ────────────────────────────────────────
def icon(size):
    im=Image.new('RGBA',(size,size),(0,0,0,0)); d=ImageDraw.Draw(im); s=size
    r=int(s*0.22); d.rounded_rectangle([0,0,s-1,s-1],radius=r,fill=(4,23,36,255))
    cx,cy=s*0.5,s*0.56
    for i,k in enumerate([0.44,0.32,0.20]):
        w=max(1,int(s*0.035)); col=(24,212,248,int(120+40*i))
        d.arc([cx-k*s,cy-k*s,cx+k*s,cy+k*s],start=200,end=340,fill=col,width=w)
    dot=s*0.075; d.ellipse([cx-dot,cy-dot,cx+dot,cy+dot],fill=(255,71,87,255))
    tri=[(cx,s*0.14),(cx-s*0.09,s*0.30),(cx+s*0.09,s*0.30)]; d.polygon(tri,fill=(255,255,255,235))
    return im
for name,sz in [('icon-512.png',512),('icon-192.png',192),('apple-touch-icon.png',180),('favicon-32x32.png',32),('favicon-16x16.png',16)]:
    icon(sz).save(os.path.join(OUT,name))
icon(64).save(os.path.join(OUT,'favicon.ico'),sizes=[(16,16),(32,32),(48,48)])
open(os.path.join(OUT,'favicon.svg'),'w').write('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#041724"/><g fill="none" stroke="#18d4f8" stroke-width="2.4" stroke-linecap="round"><path d="M9 33a24 24 0 0 1 46 0" opacity=".55"/><path d="M15 36a17 17 0 0 1 34 0" opacity=".75"/><path d="M22 39a10.5 10.5 0 0 1 20 0"/></g><circle cx="32" cy="36" r="4.8" fill="#ff4757"/><path d="M32 9l-6 10h12z" fill="#fff" opacity=".92"/></svg>''')

# ── manifests ────────────────────────────────────────────────────────────────
json.dump({"name":"SONAR-mobile · Data Center Console","short_name":"SONAR DC","start_url":"./SONAR-DataCenter-Console.html","display":"standalone","background_color":"#041724","theme_color":"#041724",
           "icons":[{"src":"icon-192.png","sizes":"192x192","type":"image/png"},{"src":"icon-512.png","sizes":"512x512","type":"image/png"}]},open(os.path.join(OUT,'site.webmanifest'),'w'),indent=1)
json.dump({"name":"SONARmobile · Data Center","short_name":"SONARmobile","start_url":"./datacenter.html","scope":"./","display":"standalone","orientation":"portrait","background_color":"#041724","theme_color":"#041724",
           "icons":[{"src":"../icon-192.png","sizes":"192x192","type":"image/png"},{"src":"../icon-512.png","sizes":"512x512","type":"image/png"},{"src":"../apple-touch-icon.png","sizes":"180x180","type":"image/png"}]},open(os.path.join(OUT,'cmdr','manifest.json'),'w'),indent=1)

# ── data ─────────────────────────────────────────────────────────────────────
json.dump({"v":1,"messages":[],"updated":0},open(os.path.join(OUT,'data','bus.json'),'w'))
json.dump({"exported":None,"stats":{},"rows":[]},open(os.path.join(OUT,'data','comms-log.json'),'w'))

# ── face/ ────────────────────────────────────────────────────────────────────
if os.path.isdir('/home/claude/repo/face') and OUT!='/home/claude/repo': shutil.copytree('/home/claude/repo/face',os.path.join(OUT,'face'),dirs_exist_ok=True)
open(os.path.join(OUT,'face','README.md'),'w').write('''# face/
face-api.js (MIT · justadudewhohacks/face-api.js, `dist/face-api.min.js`) and the three model weight sets the
console and the phone lazy-load on first Face ID use: `tiny_face_detector`, `face_landmark_68_tiny`, `face_recognition`.
Re-fetch with `tools/fetch_face.sh` if these are ever removed.
''')
open(os.path.join(OUT,'tools','fetch_face.sh'),'w').write('''#!/usr/bin/env bash
# Re-download face-api.js + weights into face/ (run from the repo root)
set -e; B=https://raw.githubusercontent.com/justadudewhohacks/face-api.js/master; mkdir -p face/models
curl -sSfL -o face/face-api.min.js $B/dist/face-api.min.js
for f in tiny_face_detector_model-weights_manifest.json tiny_face_detector_model-shard1 face_landmark_68_tiny_model-weights_manifest.json face_landmark_68_tiny_model-shard1 face_recognition_model-weights_manifest.json face_recognition_model-shard1 face_recognition_model-shard2; do curl -sSfL -o face/models/$f $B/weights/$f; done
echo "face/ ready"
''')

# ── tools ────────────────────────────────────────────────────────────────────
for f in ['build_dc_console.py','qa_dc_console.py']: shutil.copy(os.path.join(SRC,'tools',f),os.path.join(OUT,'tools',f))
shutil.copy(os.path.join(SRC,'dcmap.html'),os.path.join(OUT,'tools','dcmap.html'))
shutil.copy(os.path.abspath(__file__),os.path.join(OUT,'tools','assemble_repo.py'))
open(os.path.join(OUT,'tools','README.md'),'w').write('''# tools/
- `build_dc_console.py` — rebuilds `SONAR-DataCenter-Console.html` from the Navy ADMIN (`ie-SRS-ADMIN.html` → `src.html`), the
  phone's Drill Builder srcdoc (`dc_builder_srcdoc.txt`, cut from `cmdr/datacenter.html`) and `dcmap.html` (the SYS-03 module).
  Every substitution is guarded: a miss or a double hit aborts the build.
- `assemble_repo.py` — applies the repo-specific patches (bus repo, Pages URLs, guides, cache-bust) and writes icons, manifests,
  data files and docs. Change `ORG` / `REPO` there if the repo is renamed.
- `qa_dc_console.py` — Playwright QA (auth, every tile, SYS-03, ADM-08 drop, ADM-11 seed, bus aliasing, BattleCat, stores).
  `python3 tools/qa_dc_console.py` from the repo root.
- `dcmap.html` — SYS-03 Portfolio Map source (escaped into the console's srcdoc at build time).
- `fetch_face.sh` — re-download face-api.js + weights into `face/`.
''')

# ── docs ─────────────────────────────────────────────────────────────────────
CSS='''<style>:root{--bg:#060c14;--card:#0e1a28;--border:#1a2d42;--tx:#cce0f2;--txd:#6e90b0;--cyan:#18d4f8;--red:#ff4757}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--tx);font:14px/1.6 "Share Tech Mono",ui-monospace,Menlo,monospace;padding:28px 24px 60px}
main{max-width:900px;margin:0 auto}h1{font:800 26px/1.1 Rajdhani,Orbitron,sans-serif;letter-spacing:1px;color:#fff;margin:0 0 4px}h1 b{color:var(--red)}h1 i{font-style:normal;font-size:.8em}
.sub{color:var(--txd);letter-spacing:2px;font-size:11px;text-transform:uppercase;margin-bottom:26px}h2{font:700 12px Orbitron,monospace;letter-spacing:2.5px;color:var(--cyan);margin:28px 0 8px;text-transform:uppercase}
.card{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:14px 16px;margin-bottom:10px}.card b{color:#fff}ul{margin:6px 0 0;padding-left:18px}li{margin:3px 0}a{color:var(--cyan)}
code{background:rgba(24,212,248,.08);border:1px solid rgba(24,212,248,.25);border-radius:3px;padding:0 5px;font-size:12px}.ref{display:grid;grid-template-columns:1fr auto;gap:8px 14px;align-items:center}.ref small{color:var(--txd)}</style>'''
WM='<h1><b>SONAR</b>-mob<b>i</b>le <i>· Data Center</i></h1>'
open(os.path.join(OUT,'docs','console-guide.html'),'w',encoding='utf-8').write('''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SONAR-mobile · Data Center Console · Guide</title>'''+CSS+'''</head><body><main>'''+WM+'''<div class="sub">Console guide · v1 · '''+V+'''</div>
<div class="card"><b>What it is.</b> The desktop console for a portfolio of colocation, enterprise and edge data centers. It provisions the accounts the SONARmobile phone app signs in with, routes SONAR alerts (Site Outage Notification, Analysis &amp; Response), watches every site's instance pair, and talks to the phones over the SRABus (same-browser BroadcastChannel or the GitHub <code>data/bus.json</code> file for cross-device demos).</div>
<h2>Signing in</h2><div class="card"><ul><li><b>Step 1 · PASS key</b> — a fine-grained GitHub token with Contents read/write on this repo turns on the cross-device bus. <i>Continue without link</i> keeps everything same-browser.</li><li><b>Step 2 · Security key</b> — the six-digit master console pin. User security keys belong to the phone and are refused here.</li><li><b>LOCK</b> re-arms step 2; <b>LOGOUT</b> returns to step 1.</li></ul></div>
<h2>Tiles</h2><div class="card"><ul>
<li><b>AI-01 ARIA</b> — admin-aware assistant; reads live console state on every message. Needs an AI key in ADM-06.</li>
<li><b>SYS-03 Portfolio Map</b> — every site coloured by health (● colocation, ■ enterprise, ◆ edge). Filter by type, market, health; select a site for instances, seats, alerts and actions (force sync, restart, close alert, message, push status, test alert to the phone).</li>
<li><b>SYS-04 Data Drop Zone</b> — XLSX / CSV / JSON ingest and the landing spot for drill scenarios sent from ADM-08 or the phone.</li>
<li><b>ADM-01 User Accounts</b> — two seats per site (Critical Facilities Manager, Facilities On-call) plus custom accounts. Assign security keys, enroll Face ID portraits, PING a phone, grant OT (secure) sessions.</li>
<li><b>ADM-02 Message Center</b> — presence, channels per market and site, broadcasts.</li>
<li><b>ADM-03 SONAR Alert Routing</b> — recipient × channel matrix, test dispatches, dispatch log.</li>
<li><b>ADM-04 Instance Health &amp; Deploy</b> — primary / secondary status, sync lag, build waves by market.</li>
<li><b>ADM-05 Audit Log</b> — every admin action, dispatch, phone ACK and BattleCat assessment.</li>
<li><b>ADM-06 Platform Settings</b> — AI provider / key, endpoints, demo reset.</li>
<li><b>ADM-08 SONAR Drill Builder</b> — the phone's seven-step drill builder; RUN releases the alert queue for dispatch review, the drop button sends the scenario to SYS-04.</li>
<li><b>ADM-09 Comms Log</b> — every envelope in both directions with latency and ack round-trip; export or push to <code>data/comms-log.json</code>.</li>
<li><b>ADM-10 SONARmobile · Data Center</b> — the phone app, linked site leads, test alerts, status snapshots, transport settings and the phone URL.</li>
<li><b>ADM-11 Black Start</b> — pull-the-plug test record (Uptime Tier III · NFPA 110), Facility Director authorization on the phone, findings and corrective actions.</li></ul></div>
<h2>Phone link, step by step</h2><div class="card"><ol><li>ADM-01 → create an account or pick a seat → <b>SET KEY</b> (six digits).</li><li>ADM-10 → copy the phone URL, open it on the iPhone, Share → Add to Home Screen.</li><li>On the phone: PASS key (same GitHub token for cross-device, or tap Connect with no key on the same browser) → security key.</li><li>The HELLO lands in ADM-02 / ADM-09; the console answers with a STATUS snapshot for the flagship site (Broad Run · LDN1).</li></ol></div>
<h2>Deploying</h2><div class="card">GitHub Pages from <code>main</code>, root. Every bus write from a linked console is a commit to <code>data/bus.json</code>, and each commit restarts the Pages deploy — a freshly uploaded surface only goes live once the bus goes quiet. Cache-bust with <code>?v=YYYYMMDD</code> and check <code>window.__DC_CONSOLE_BUILD</code> in the console.</div>
</main></body></html>''')
open(os.path.join(OUT,'docs','phone-guide.html'),'w',encoding='utf-8').write('''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SONARmobile · Data Center · Guide</title>'''+CSS+'''</head><body><main>'''+WM+'''<div class="sub">SONARmobile phone guide · v1 · '''+V+'''</div>
<div class="card"><b>What it is.</b> The critical-facilities companion app for a data center. It receives SONAR alerts from the console, lets the Critical Facilities Manager acknowledge, release and message, and carries the site's live map, tenants, fuel &amp; vendors, SLA lamps, BattleCat fleet, black start drill and drill builder. The in-app <b>Guide</b> tile is the hands-on tutorial; this page is the short version.</div>
<h2>Signing in</h2><div class="card"><ul><li><b>Industry</b> — COLO / ENT / EDGE picks the sample site (Broad Run · LDN1, Meridian Financial, Ridgeline Edge).</li><li><b>PASS key</b> — the GitHub token for the cross-device bus, or tap <i>Connect</i> with no key to sign in on this device only.</li><li><b>Security key</b> — the six digits the console assigned in ADM-01. <b>Face ID</b> works after one key sign-in on this phone.</li><li><b>CORP ⇄ OT</b> — the OT (facility control) session needs console acceptance; only Log out stays live in OT.</li></ul></div>
<h2>Tiles</h2><div class="card"><ul><li><b>Message</b> — site channel, quick replies, NOC / facilities compose.</li><li><b>Outages</b> — live list with ETR; <b>SONAR</b> releases a new alert to the routing roles.</li><li><b>Tenant impact</b> — halls, racks and customers at risk.</li><li><b>On-call · Fuel &amp; vendors · SLA &amp; compliance · Tenants</b> — the crews, generator fuel, SLA lamps and restoration priority list.</li><li><b>BattleCat</b> — dispatches an assessment vehicle to the outage; the assessment (confidence, revised ETR, recommendation) posts to the site channel and the console audit.</li><li><b>Black start</b> — the Tier III pull-the-plug drill: Director decisions, objectives, halls &amp; loads.</li><li><b>Live map</b> — rotatable isometric campus with outage pins, satellite by toggle.</li><li><b>Drill</b> — the seven-step drill builder; RUN queues alerts as an exercise, or send the scenario to the Drop Zone.</li><li><b>Link</b> — transport, site and industry settings, ping sound.</li></ul></div>
<h2>Sounds &amp; pings</h2><div class="card">Console PINGs vibrate and show a card (Android buzzes; the iPhone shows the card). Turn on <i>Ping sound</i> in Link if you want a tone — the iPhone ringer switch mutes it.</div>
</main></body></html>''')
open(os.path.join(OUT,'docs','blackstart','index.html'),'w',encoding='utf-8').write('''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Black start · reference · SONAR-mobile Data Center</title>'''+CSS+'''</head><body><main>'''+WM+'''<div class="sub">ADM-11 · black start / pull-the-plug reference</div>
<div class="card"><b>The drill.</b> Open the utility feed(s) with the site carrying live IT load and prove the critical-power chain end to end: UPS rides through, generators start and the ATS transfers inside the UPS runtime, cooling restarts before inlet temperature drifts, one generator can be lost with the full load still carried (N+1), and the site resynchronises to the utility with no tenant impact. Five objectives — <b>Start · UPS · Cool · N+1 · Sync</b> — scored pass / partial / fail.</div>
<h2>Authorities &amp; standards</h2><div class="card ref">
<span><b>Uptime Institute · Tier Standard: Topology &amp; Operational Sustainability</b><br><small>Tier III concurrently maintainable · annual pull-the-plug / integrated systems test</small></span><a href="https://uptimeinstitute.com/tiers" target="_blank" rel="noopener">uptimeinstitute.com</a>
<span><b>ANSI/TIA-942</b><br><small>Telecommunications infrastructure standard for data centers · rated-level topology</small></span><a href="https://tiaonline.org/products-and-services/tia942certification/" target="_blank" rel="noopener">tiaonline.org</a>
<span><b>NFPA 110 · Emergency and Standby Power Systems</b><br><small>10 s start / transfer classes · monthly load test · annual 4-hour load bank</small></span><a href="https://www.nfpa.org/codes-and-standards/nfpa-110-standard-development/110" target="_blank" rel="noopener">nfpa.org</a>
<span><b>NFPA 70E · Electrical Safety in the Workplace</b><br><small>Energized-work procedures for switching</small></span><a href="https://www.nfpa.org/codes-and-standards/nfpa-70e-standard-development/70e" target="_blank" rel="noopener">nfpa.org</a>
<span><b>EPA 40 CFR 60 Subpart IIII · Stationary CI engines</b><br><small>Generator run-hour and emissions limits</small></span><a href="https://www.ecfr.gov/current/title-40/chapter-I/subchapter-C/part-60/subpart-IIII" target="_blank" rel="noopener">ecfr.gov</a>
<span><b>ASHRAE TC 9.9 thermal guidelines</b><br><small>A1 inlet envelope held through the cooling restart</small></span><a href="https://www.ashrae.org/technical-resources/bookstore/datacom-series" target="_blank" rel="noopener">ashrae.org</a>
</div>
<h2>Record model (what the console stores)</h2><div class="card">Exercise id · site · type (BSE / IST / LOADBANK / TTX) · date · planned hours · notice · scope (whole-site / hall / utility-feed / generator-only) · excluded areas · utility partner · witness / auditor · fiscal year · annual-test flag · status · milestones M1–M12 · Director authorizations (approval, go / no-go, abort, findings acceptance — each a BSE_AUTH envelope the phone answers) · critical loads with tier, backup, kW, fuel hours and start / transfer / carry lamps · findings with severity, category, corrective action, owner, funding line and status.</div>
</main></body></html>''')

# ── root ─────────────────────────────────────────────────────────────────────
open(os.path.join(OUT,'index.html'),'w',encoding='utf-8').write('''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>SONAR-mobile · Data Center</title>
<link rel="icon" href="favicon.svg"><link rel="apple-touch-icon" href="apple-touch-icon.png">'''+CSS+'''<style>body{min-height:100vh;display:flex;align-items:center;justify-content:center}main{text-align:center}.go{display:block;margin:12px auto;max-width:420px;padding:16px 20px;border-radius:10px;border:1px solid rgba(24,212,248,.45);background:rgba(24,212,248,.08);color:#fff;text-decoration:none;font:700 16px Rajdhani,Orbitron,sans-serif;letter-spacing:2px}.go small{display:block;font:12px/1.5 "Share Tech Mono",monospace;color:var(--txd);letter-spacing:.5px;margin-top:4px}.go:hover{background:rgba(24,212,248,.16)}.go.ph{border-color:rgba(255,71,87,.5);background:rgba(255,71,87,.08)}.go.ph:hover{background:rgba(255,71,87,.16)}</style></head>
<body><main><h1><b>SONAR</b>-mob<b>i</b>le</h1><div class="sub">Site Outage Notification, Analysis &amp; Response · Data Center</div>
<a class="go" href="SONAR-DataCenter-Console.html">DATA CENTER CONSOLE<small>desktop · accounts · routing · portfolio map · drills</small></a>
<a class="go ph" href="cmdr/datacenter.html">SONARmobile<small>phone · Critical Facilities Manager companion app</small></a>
<div class="sub" style="margin-top:22px"><a href="docs/console-guide.html">console guide</a> · <a href="docs/phone-guide.html">phone guide</a> · <a href="docs/blackstart/index.html">black start reference</a></div></main></body></html>''')
open(os.path.join(OUT,'.nojekyll'),'w').write('')
open(os.path.join(OUT,'.gitignore'),'w').write('.DS_Store\n__pycache__/\n*.pyc\nnode_modules/\ntools/src.html\ntools/dc_builder_srcdoc.txt\n')
open(os.path.join(OUT,'README.md'),'w',encoding='utf-8').write('''# SONAR-mobile · Data Center

Site Outage Notification, Analysis & Response for a portfolio of colocation, enterprise and edge data centers.
Two surfaces, one bus:

| Surface | File | What it is |
|---|---|---|
| Data Center Console | `SONAR-DataCenter-Console.html` | Desktop console — accounts, SONAR alert routing, instance health, portfolio map, drill builder, black start planning, audit and comms logs |
| SONARmobile · Data Center | `cmdr/datacenter.html` | The phone app for the Critical Facilities Manager — alerts, outages, tenant impact, live campus map, BattleCat, black start, drills |

Live: `'''+PAGES+'''` (GitHub Pages from `main`, repo root — keep `.nojekyll`).

## Layout
```
index.html                      launcher (console / phone / guides)
SONAR-DataCenter-Console.html   desktop console
cmdr/datacenter.html            phone app        cmdr/manifest.json  PWA manifest (Add to Home Screen)
data/bus.json                   SRABus shared transport (GitHub mode) — written by linked consoles/phones
data/comms-log.json             ADM-09 export target
face/                           face-api.js + model weights (Face ID, lazy-loaded)
docs/                           console-guide.html · phone-guide.html · blackstart/index.html
tools/                          build, assemble and QA scripts (see tools/README.md)
favicon.* icon-192/512 apple-touch-icon.png site.webmanifest
```

## First run
1. Push to `main`, enable Pages (Deploy from branch · main · /root).
2. Open the console, **Continue without link** for a same-browser demo, or paste a fine-grained GitHub token
   (Contents read/write on this repo) as the PASS key to turn on the cross-device bus through `data/bus.json`.
3. Step 2 is the master console pin. ADM-01 → set a security key on a seat; ADM-10 → copy the phone URL.
4. On the phone use the same PASS key (or tap Connect with no key on the same browser) and the six-digit security key.

## Notes
- Every bus write in GitHub mode is a commit to `data/bus.json`; each commit restarts the Pages deploy, so a freshly uploaded
  surface only goes live once the bus goes quiet. Verify uploads with `window.__DC_CONSOLE_BUILD` in the console.
- Storage is namespaced (`dcc_*`, `sonar-dc-*`, `sonarmobile_dc_*`), so this repo can also be served beside the Navy ie-SRS
  surfaces on the same origin without sharing state. The bus channel name `ie-sra-bus` is the wire protocol and is unchanged.
- The phone's pitch video (`pitch/SONARmobile-release.html`) is still published from the ie-SRS repo.
- Sample data: the 27-site portfolio, Broad Run · LDN1, tenants, crews and BattleCat sorties are demo content.
''')
print('assembled →',OUT)
for root,dirs,files in os.walk(OUT):
    dirs[:]=[d for d in dirs if d!='.git']
    for f in files: print(' ',os.path.relpath(os.path.join(root,f),OUT),os.path.getsize(os.path.join(root,f)))
