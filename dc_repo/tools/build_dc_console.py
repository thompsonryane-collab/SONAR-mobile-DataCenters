#!/usr/bin/env python3
"""Build SONAR-DataCenter-Console.html from ie-SRS-ADMIN.html + cmdr/datacenter.html.
Guarded single-match substitutions (rep) — a miss or a double hit aborts the build."""
import html, re, sys, os
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
s=open(os.path.join(ROOT,'src.html'),encoding='utf-8').read()
dc_builder=open(os.path.join(ROOT,'dc_builder_srcdoc.txt'),encoding='utf-8').read()
dcmap=open(os.path.join(ROOT,'dcmap.html'),encoding='utf-8').read()
LOG=[]
def rep(a,b,n=1,tag=''):
    global s
    c=s.count(a)
    if c!=n: raise SystemExit('REP MISS %s: expected %d got %d :: %r'%(tag,n,c,a[:90]))
    s=s.replace(a,b); LOG.append((tag or a[:50],c))
def rep_between(start,end,a,b,tag=''):
    """single replacement constrained to the region between two unique anchors"""
    global s
    i=s.index(start); j=s.index(end,i); seg=s[i:j]
    c=seg.count(a)
    if c!=1: raise SystemExit('REP_BETWEEN MISS %s: got %d :: %r'%(tag,c,a[:90]))
    s=s[:i]+seg.replace(a,b)+s[j:]; LOG.append(('['+tag+'] '+a[:40],1))
def rep_all(a,b,tag=''):
    global s
    c=s.count(a)
    if c==0: raise SystemExit('REP_ALL MISS %s :: %r'%(tag,a[:90]))
    s=s.replace(a,b); LOG.append((tag or a[:50],c))

# ─────────────────────────────────────────────────────────────────────────────
# 0. SYS-03 · replace the Navy grid/AMI module with the data-center portfolio map
# ─────────────────────────────────────────────────────────────────────────────
a=s.index('<div class="app-overlay overlay-duers" id="overlay-secres">')
i=s.index('srcdoc="',a)+len('srcdoc="'); j=s.index('"\n',i)
assert s[i:i+40].startswith('&lt;!DOCTYPE html&gt;')
s=s[:i]+html.escape(dcmap,quote=True)+s[j:]
LOG.append(('SYS-03 srcdoc → dcmap.html',1))

# ─────────────────────────────────────────────────────────────────────────────
# 1. ADM-08 · swap in the data-center Drill Builder from cmdr/datacenter.html
# ─────────────────────────────────────────────────────────────────────────────
b=s.index('<div class="app-overlay overlay-duers" id="overlay-builder">')
bi=s.index('srcdoc="',b)+len('srcdoc="'); bj=s.index('"\n',bi)
dcb=dc_builder
def brep(a,b_,n=1):
    global dcb
    c=dcb.count(a)
    if c!=n: raise SystemExit('BUILDER REP MISS: expected %d got %d :: %r'%(n,c,a[:80]))
    dcb=dcb.replace(a,b_)
brep('&lt;title&gt;SONARmobile // Drill Builder&lt;/title&gt;','&lt;title&gt;SONAR DC Console // ADM-08 Drill Builder&lt;/title&gt;')
brep('title=&quot;Back to SONARmobile&quot; aria-label=&quot;Back to SONARmobile&quot;&gt;← &lt;span class=&quot;c-lbl&quot;&gt;SONARmobile&lt;/span&gt;',
     'title=&quot;Back to console&quot; aria-label=&quot;Back to console&quot;&gt;← &lt;span class=&quot;c-lbl&quot;&gt;CONSOLE&lt;/span&gt;')
brep('&lt;span class=&quot;c-lbl&quot;&gt;SONARmobile · Drill Builder · Site Outage Notification, Analysis &amp;amp; Response&lt;/span&gt;','&lt;span class=&quot;c-lbl&quot;&gt;ADM-08 · Drill Builder&lt;/span&gt;')
brep('&lt;/style&gt;\n&lt;/head&gt;','&lt;/style&gt;\n&lt;style&gt;/* console: keep the phone chrome clear of the sticky nav band */#chrome{margin-top:40px}&lt;/style&gt;\n&lt;/head&gt;')
s=s[:bi]+dcb+s[bj:]
LOG.append(('ADM-08 srcdoc → DC drill builder',1))
rep('<iframe class="overlay-frame" id="frame-builder" title="ADM-08 SONAR — Shore Outage Notification, Analysis &amp; Response"',
    '<iframe class="overlay-frame" id="frame-builder" title="ADM-08 SONAR — Site Outage Notification, Analysis &amp; Response · Drill Builder"',tag='builder iframe title')
# parent: accept BUILDER_DROP (Drill Builder → Data Drop Zone) beside BUILDER_SCENARIO
rep("  if (d.type === 'BUILDER_SCENARIO') { try { handleBuilderScenario(d.payload); } catch(ex) { console.warn('BUILDER_SCENARIO', ex); } return; }",
    "  if (d.type === 'BUILDER_SCENARIO') { try { handleBuilderScenario(d.payload); } catch(ex) { console.warn('BUILDER_SCENARIO', ex); } return; }\n"
    "  if (d.type === 'BUILDER_DROP') { try { var dz = (window.SRADropZone && SRADropZone.fromScenario(d.payload, {source:'console-builder'})) || null; closeApp('overlay-builder'); if (typeof hubToast === 'function') hubToast('Scenario sent to SYS-04 Data Drop Zone' + (dz ? ' · ' + dz.name : ''), 'ok', 3200); if (window.ADMIN_CORE) ADMIN_CORE.audit('DRILL_DROP', d.payload && d.payload.installation || '', 'drill scenario dropped from ADM-08'); } catch(ex) { console.warn('BUILDER_DROP', ex); } return; }",tag='BUILDER_DROP handler')
# builderMatchSite → data-center site keys
rep("  var keys = [['norfolk','ns-norf'],['san diego','nb-sd'],['kitsap','nb-kitsap'],['bremerton','nb-kitsap'],['new london','nsb-nl'],['key west','nas-keywest'],['jacksonville','nas-jax'],['patuxent','nas-pax'],['meridian','nas-meridian']",
    "  var keys = [['broad run','br-ldn1'],['ashburn','br-ldn1'],['cascade peak','cp-cp2'],['hillsboro','cp-cp2'],['meridian financial','mf-dc1'],['northlake','nh-dc'],['ridgeline','rl-edge'],['gulf edge','ge-s7'],['houston','ge-s7']",tag='builderMatchSite keys')

# ─────────────────────────────────────────────────────────────────────────────
# 2. ADMIN_CORE · data-center portfolio replaces the 70 Navy installations
# ─────────────────────────────────────────────────────────────────────────────
a=s.index("  var REG={\n    NDW:"); b=s.index("  var FIRST=")
NEW_CORE = r"""  var REG={
    NOVA:'Northern Virginia', MIDATL:'Mid-Atlantic', SE:'Southeast', TX:'Texas', MW:'Midwest',
    SW:'Southwest', PNW:'Pacific Northwest', CA:'California', EU:'Europe', APAC:'Asia-Pacific'
  };
  var REGC={NOVA:'#18d4f8',MIDATL:'#6e90b0',SE:'#4db88a',TX:'#e08a45',MW:'#9ebc52',
            SW:'#d4a05a',PNW:'#29d3c8',CA:'#c3aaf8',EU:'#a07cf0',APAC:'#e05555'};

  // [id, name, market, lat, lon, mapId, type (COLO|ENT|EDGE), utility, IT MW, racks, gens online, tier]
  var LIST=[
    ['br-ldn1','Broad Run Data Center · LDN1','NOVA',39.0437,-77.4875,null,'COLO','Dominion Energy',18,'1,860','6/8','III'],
    ['br-ldn2','Broad Run Data Center · LDN2','NOVA',39.0062,-77.4286,null,'COLO','Dominion Energy',24,'2,400','8/8','III'],
    ['mn-ma1','Manassas Gateway · MA1','NOVA',38.7509,-77.4753,null,'COLO','NOVEC',36,'3,600','10/10','III'],
    ['rk-pa1','Riverkeep Enterprise DC · PA1','MIDATL',40.2732,-76.8867,null,'ENT','PPL Electric',5,'380','2/2','II'],
    ['ne-nj1','Newark Edge · NJ1','MIDATL',40.7895,-74.0565,null,'COLO','PSE&G',14,'1,200','4/4','III'],
    ['at-ga1','Peachtree Colo · ATL1','SE',33.7490,-84.3880,null,'COLO','Georgia Power',20,'1,900','6/6','III'],
    ['mi-fl1','Biscayne NAP · MIA1','SE',25.7617,-80.1918,null,'COLO','FPL',12,'1,050','4/4','IV'],
    ['ch-nc1','Catawba Enterprise DC','SE',35.2271,-80.8431,null,'ENT','Duke Energy',8,'640','3/3','III'],
    ['mf-dc1','Meridian Financial · Primary DC','TX',32.7767,-96.7970,null,'ENT','Oncor',6,'420','3/4','III'],
    ['ge-s7','Gulf Edge Modular · Site 7','TX',29.7604,-95.3698,null,'EDGE','CenterPoint',0.8,'64','1/1','II'],
    ['sa-tx1','Alamo Colo · SAT1','TX',29.4241,-98.4936,null,'COLO','CPS Energy',16,'1,500','5/5','III'],
    ['nh-dc','Northlake Health System DC','MW',39.9612,-82.9988,null,'ENT','AEP Ohio',4,'310','2/2','III'],
    ['ch-il1','Lakeshore Colo · CHI1','MW',42.0039,-87.9703,null,'COLO','ComEd',30,'3,000','9/9','III'],
    ['mn-mn1','Northstar Edge · MSP1','MW',44.9778,-93.2650,null,'EDGE','Xcel Energy',1.5,'110','1/1','II'],
    ['rl-edge','Ridgeline Edge · 12-site portfolio','SW',33.4484,-112.0740,null,'EDGE','APS',1.2,'96','11/12','II'],
    ['ph-az1','Sonoran Colo · PHX1','SW',33.4152,-111.8315,null,'COLO','SRP',40,'4,100','12/12','III'],
    ['lv-nv1','Silver State Colo · LAS1','SW',36.1699,-115.1398,null,'COLO','NV Energy',22,'2,100','7/7','III'],
    ['cp-cp2','Cascade Peak Colocation · CP2','PNW',45.5229,-122.9898,null,'COLO','PGE',32,'3,200','9/10','III'],
    ['qc-wa1','Columbia Basin · QCY1','PNW',47.2343,-119.8526,null,'COLO','Grant PUD',48,'4,800','14/14','III'],
    ['sj-ca1','Bayshore Colo · SJC1','CA',37.3541,-121.9552,null,'COLO','Silicon Valley Power',28,'2,700','8/8','III'],
    ['la-ca1','El Segundo Enterprise DC','CA',33.9192,-118.4165,null,'ENT','SCE',7,'520','3/3','III'],
    ['fr-de1','Main Campus · FRA1','EU',50.1109,8.6821,null,'COLO','Mainova',26,'2,500','8/8','III'],
    ['db-ie1','Liffey Colo · DUB1','EU',53.3498,-6.2603,null,'COLO','ESB Networks',18,'1,800','6/6','III'],
    ['am-nl1','Schiphol Edge · AMS1','EU',52.3105,4.7683,null,'EDGE','Liander',2,'150','2/2','II'],
    ['sg-sg1','Jurong Colo · SIN1','APAC',1.3521,103.8198,null,'COLO','SP Group',20,'2,000','6/6','III'],
    ['tk-jp1','Inzai Colo · TYO1','APAC',35.8320,140.1450,null,'COLO','TEPCO',24,'2,300','8/8','III'],
    ['sy-au1','Macquarie Park · SYD1','APAC',-33.7770,151.1160,null,'COLO','Ausgrid',14,'1,300','4/4','III']
  ];

"""
s=s[:a]+NEW_CORE+s[b:]; LOG.append(('ADMIN_CORE REG/REGC/LIST → DC portfolio',1))
rep("id:a[0], name:a[1], region:a[2], regionName:REG[a[2]], regionColor:REGC[a[2]],",
    "id:a[0], name:a[1], region:a[2], regionName:REG[a[2]], regionColor:REGC[a[2]], ty:a[6]||'COLO', utility:a[7]||'', mw:a[8]||0, racks:a[9]||'', gens:a[10]||'', tier:a[11]||'III',",tag='site record extra fields')
rep("lat:a[3], lon:a[4], mapId:a[5], uic:'N'+String(60000+((seedOf(a[0])%39999))).slice(0,5),",
    "lat:a[3], lon:a[4], mapId:a[5], uic:'DC-'+String(10000+((seedOf(a[0])%89999))).slice(0,5),",tag='site code')
rep("fm:{first:'Facility', last:'Manager', name:'Facility Manager', email:('fm.'+slug+'@example.mil'), role:'FM — Facility Manager',",
    "fm:{first:'Critical Facilities', last:'Manager', name:'Critical Facilities Manager', email:('cfm.'+slug+'@example.com'), role:'CFM — Critical Facilities Manager',",tag='fm seat')
rep("backup:{first:'Backup', last:'Support', name:'Backup Support', email:('bfs.'+slug+'@example.mil'), role:'Backup Facilities Support',",
    "backup:{first:'Facilities', last:'On-call', name:'Facilities On-call', email:('oncall.'+slug+'@example.com'), role:'Facilities On-call',",tag='backup seat')
rep("return slug+(w==='primary'?'-FM-01':'-BFS-02');","return slug+(w==='primary'?'-CFM-01':'-OC-02');",tag='instance name')
rep_all('example.mil','example.com',tag='email domain')

# ─────────────────────────────────────────────────────────────────────────────
# 3. Standalone stores · the console never shares state with the Navy ADMIN on the same origin
#    (bus channel, data/bus.json and sra_dropzone stay shared — that is the wire to the phone)
# ─────────────────────────────────────────────────────────────────────────────
rep_all("'adm_","'dcc_",tag='adm_* stores → dcc_*')
rep_all("'ie-srs-","'sonar-dc-",tag='ie-srs-* stores → sonar-dc-*')
rep("var CFG_KEY='sra_bus_cfg_'+NODE, LOG_KEY='sra_bus_log', SEEN_KEY='sra_bus_seen_'+NODE;",
    "var CFG_KEY='dcc_bus_cfg_'+NODE, LOG_KEY='dcc_bus_log', SEEN_KEY='dcc_bus_seen_'+NODE;",tag='bus store keys')
rep("localStorage.getItem('ined-theme')","localStorage.getItem('dcc-theme')",tag='theme get')
rep("localStorage.setItem('ined-theme', theme)","localStorage.setItem('dcc-theme', theme)",tag='theme set')

# ─────────────────────────────────────────────────────────────────────────────
# 4. Bus · site aliasing for the data-center phone, BattleCat envelopes, sector on HELLO
# ─────────────────────────────────────────────────────────────────────────────
rep("site:'nb-sd', repo:","site:'br-ldn1', repo:",tag='bus default site')
rep("sel.value='nb-sd';","sel.value='br-ldn1';",tag='cx-site default')
rep("var siteId=(acct&&acct.siteId&&acct.siteId!=='custom')?acct.siteId:(site&&site!=='*'?site:'nb-sd');",
    "var siteId=(acct&&acct.siteId&&acct.siteId!=='custom')?acct.siteId:(site&&site!=='*'&&C.SITE[site]?site:'br-ldn1');",tag='key-auth site fallback')
rep("('site:'+(env.site||'nb-sd'))","('site:'+(C.SITE[env.site]?env.site:'br-ldn1'))",tag='MSG channel alias')
rep("      bus.publish('HELLO',{node:'admin',app:'ie-SRS ADMIN'},{site:env.site||'*'});\n      sendStatus(env.site||'nb-sd');",
    "      bus.publish('HELLO',{node:'admin',app:'SONAR DC Console'},{site:env.site||'*'});\n      sendStatus(C.SITE[env.site]?env.site:'br-ldn1');   /* the data-center phone still says hello as nb-sd · alias to the flagship site */",tag='HELLO site alias')
rep("if(p.commander)pr.name=p.commander;if(p.by&&!pr.name)pr.name=p.by;if(p.app)pr.app=p.app;pr.last=env.type;}",
    "if(p.commander)pr.name=p.commander;if(p.by&&!pr.name)pr.name=p.by;if(p.app)pr.app=p.app;if(p.utilType)pr.ty=p.utilType;if(p.sector)pr.sector=p.sector;pr.last=env.type;}",tag='peer sector')
rep("    }else if(env.type==='HELLO'){\n      if(replay)return;\n      C.audit('CMDR_HELLO'",
    "    }else if(env.type==='BC_ASSESS'||env.type==='BC_EVENT'){\n"
    "      if(replay)return;\n"
    "      var bsite=C.SITE[env.site]||C.SITE[p.site]||{};var conf=(p.c!=null?p.c:p.confidence!=null?p.confidence:'—');\n"
    "      if(env.type==='BC_ASSESS'){C.audit('BATTLECAT_ASSESS',bsite.name||env.site||'',String(p.cat||'BattleCat')+' · '+String(p.target||'')+' · '+String(p.v||'')+' · confidence '+conf+'% · ETR '+(Array.isArray(p.etr)?p.etr.join(' → '):(p.etr||'—'))+' · '+String(p.rec||'').slice(0,90));\n"
    "        toast('BattleCat '+(p.cat||'')+' · '+(p.target||'')+' · '+conf+'%','ok');ev('BC_ASSESS ← '+(p.cat||'')+' · '+(p.target||''));}\n"
    "      else{C.audit('BATTLECAT_EVENT',bsite.name||env.site||'',String(p.cat||'')+' '+String(p.ev||'')+' → '+String(p.target||''));ev('BC_EVENT '+(p.ev||'')+' · '+(p.cat||''));}\n"
    "      if(typeof admPaintAudit==='function'&&$('overlay-adm-audit')&&$('overlay-adm-audit').classList.contains('visible'))try{admPaintAudit();}catch(e){}\n"
    "    }else if(env.type==='HELLO'){\n      if(replay)return;\n      C.audit('CMDR_HELLO'",tag='BattleCat bus handler')

# ADM-10 · the phone is the data-center edition
rep("window.admCmdrOpen=function(){window.open('cmdr/index.html'","window.admCmdrOpen=function(){window.open('cmdr/datacenter.html'",tag='open phone')
rep("new URL('cmdr/',location.href)","new URL('cmdr/datacenter.html',location.href)",tag='phone url')
rep("return 'https://thompsonryane-collab.github.io/cmdr/';","return 'https://thompsonryane-collab.github.io/ie-SRS/cmdr/datacenter.html';",tag='phone url fallback')

# ─────────────────────────────────────────────────────────────────────────────
# 5. Branding · title, chrome, gates (auth flow itself unchanged)
# ─────────────────────────────────────────────────────────────────────────────
rep("<title>ie-SRS // SYSTEM ADMIN PLATFORM — ie-SRS // SONAR | Reconnaissance | Simulation","<title>SONAR // DATA CENTER CONSOLE — Site Outage Notification, Analysis &amp; Response",tag='title')
rep('<span class="c-esr-hub">ADMIN</span>','<span class="c-esr-hub">DC CONSOLE</span>',tag='chrome hub label')
rep('<span class="c-esr-lbl">SRS</span>','<span class="c-esr-lbl">SONAR</span>',tag='chrome wordmark')
rep_all('System admin platform</div>','Data center console</div>',tag='gate subtitle')
rep('<div id="ai-status" class="offline" style="margin-left:10px;">','<span style="margin-left:6px;font-family:var(--mono);font-size:9px;letter-spacing:2px;color:#18d4f8;border:1px solid rgba(24,212,248,.45);border-radius:3px;padding:2px 8px;white-space:nowrap;">COLO · ENT · EDGE</span>\n    <div id="ai-status" class="offline" style="margin-left:10px;">',tag='chrome edition badge')
# Navy demo videos are not part of the data-center product · hide the pickers
rep('</style>\n<!-- ── ARIA KEY MODAL ── -->','</style>\n<style>#demo-btn,#demo-chrome-btn{display:none!important}</style>\n<!-- ── ARIA KEY MODAL ── -->',tag='hide demo buttons') if '</style>\n<!-- ── ARIA KEY MODAL ── -->' in s else None
if '#demo-btn,#demo-chrome-btn{display:none!important}' not in s:
    rep('#hub-toast-wrap {','#demo-btn,#demo-chrome-btn{display:none!important}\n#hub-toast-wrap {',tag='hide demo buttons (alt)')

# ─────────────────────────────────────────────────────────────────────────────
# 6. Card grid · copy for the tiles that stay, drop the Navy-only tiles (ADM-07, Core Hub)
# ─────────────────────────────────────────────────────────────────────────────
def drop_card(marker_start, marker_end, tag):
    global s
    i=s.index(marker_start); j=s.index(marker_end,i)
    s=s[:i]+'<!-- '+tag+' · removed from the data-center console -->\n'+s[j:]; LOG.append(('drop '+tag,1))
drop_card('        <!-- ── CARD ADM-07: Deployment Strategy ── -->','        <!-- ── CARD ADM-08: SONAR','ADM-07 Deployment Strategy (Navy enterprise rollout deck)')
drop_card('        <!-- ── CARD: ie-SRS Core Hub ── -->','</div><!-- #card-grid -->','ie-SRS Core Hub (Navy hub)')

# SYS-03
rep('<div class="card-title"><span style="color:#a07cf0;">Security &amp; Resiliency</span> <span style="color:#ffffff;">· Global Map</span></div>',
    '<div class="card-title"><span style="color:#a07cf0;">Portfolio Map</span> <span style="color:#ffffff;">· Site Health</span></div>',tag='SYS-03 title')
i=s.index('<em>Global map, admin view</em>'); j=s.index('</div>',i)
s=s[:i]+'<em>Portfolio map, admin view</em> &mdash; every data center plotted and coloured by instance health. Select any site for type, tier, market and utility, IT load, feeds and generators, primary/secondary status, sync lag, the two account holders and open SONAR alerts. Force sync, restart, close an alert, message the site lead, push a status snapshot or fire a test SONAR alert to the phone. Filter by type, market or health; roll-up table below the map.\n          '+s[j:]
LOG.append(('SYS-03 desc',1))
rep('<span class="meta-pill">70 Sites</span>\n            <span class="meta-pill">Instance Health</span>','<span class="meta-pill">Portfolio</span>\n            <span class="meta-pill">Instance Health</span>',tag='SYS-03 pill')
# SYS-04
rep("upload account rosters, device-enrollment lists, CFE/DUERS asset extracts and installation records to seed or update all 70 sites.",
    "upload account rosters, device-enrollment lists, EPMS / BMS asset extracts, tenant lists and site records to seed or update every site in the portfolio. Drill scenarios from ADM-08 land here too.",tag='SYS-04 desc')
# ADM-01
rep("<em>Enterprise account management</em> &mdash; provision, enable, disable and reset the Facility Manager and Backup Facilities Support accounts at all 70 installations. CAC/PIV binding, government-device enrollment and role templates from one console.",
    "<em>Portfolio account management</em> &mdash; provision, enable, disable and reset the Critical Facilities Manager and Facilities On-call accounts at every site. SSO / MFA binding, device enrollment, Face ID and role templates from one console.",tag='ADM-01 desc')
rep('<span class="meta-pill">140 Seats</span><span class="meta-pill">RBAC</span><span class="meta-pill">Device Enrollment</span>',
    '<span class="meta-pill" id="card-users-seats">Seats</span><span class="meta-pill">RBAC</span><span class="meta-pill">Device Enrollment</span>',tag='ADM-01 pills')
# ADM-02
rep("<em>Live users &amp; secure comms</em> &mdash; see exactly who is connected right now (System Admin on web, base commanders on CMDR mobile), open channels by region or installation, and broadcast admin notices or maintenance windows to the field.",
    "<em>Live users &amp; secure comms</em> &mdash; see exactly who is connected right now (System Admin on web, critical facilities managers on SONARmobile), open channels by market or site, and broadcast admin notices or maintenance windows to the field.",tag='ADM-02 desc')
rep("var list=[{id:'all',label:'#all-hands',sub:'every FM + Backup'},{id:'admins',label:'#sysadmins',sub:'platform admins'},{id:'outages',label:'#outage-watch',sub:'sites with open WO'}];",
    "var list=[{id:'all',label:'#all-hands',sub:'every CFM + On-call'},{id:'admins',label:'#sysadmins',sub:'platform admins'},{id:'outages',label:'#outage-watch',sub:'sites with open SONAR alerts'}];",tag='ADM-02 channels')
rep("MC.ch.indexOf('dm:')===0?'direct message':'installation channel'","MC.ch.indexOf('dm:')===0?'direct message':'site channel'",tag='ADM-02 sub')
rep("var t=prompt('Broadcast to all 140 field users:','ADMIN NOTICE: Enterprise maintenance window tonight 0200-0400Z. Both instances at every installation will restart. Backup instances retain SONAR-alert authority throughout.');",
    "var t=prompt('Broadcast to all '+(C.SITES.length*2)+' field users:','ADMIN NOTICE: Portfolio maintenance window tonight 0200-0400Z. Both instances at every site will restart. Secondary instances retain SONAR-alert authority throughout.');",tag='ADM-02 broadcast prompt')
rep("toastOk('Broadcast delivered to 140 use","toastOk('Broadcast delivered to '+(C.SITES.length*2)+' use",tag='ADM-02 broadcast toast')
# ADM-03
rep("var RECIP=[['commander','Base Commander'],['hq','Installation / Regional HQ'],['sysadmin','System Admin'],['backup','Backup Facilities Support'],['dasn','DASN / Enterprise rollup']];",
    "var RECIP=[['commander','Critical Facilities Manager'],['hq','NOC / Site Lead'],['sysadmin','Platform Admin'],['backup','Facilities On-call'],['dasn','Tenants / Customer Success digest']];",tag='ADM-03 recipients')
rep("var CH=[['email','Email'],['mobile','Mobile alert (gov phone)'],['dash','Dashboard flag']];","var CH=[['email','Email'],['mobile','Mobile alert (SONARmobile)'],['dash','Dashboard flag']];",tag='ADM-03 channels')
rep("var trig={commander:'mission-affecting outage',hq:'above severity threshold',sysadmin:'all outages (audit)',backup:'always',dasn:'aggregated digest'}[r[0]];",
    "var trig={commander:'tenant-affecting outage',hq:'above severity threshold',sysadmin:'all outages (audit)',backup:'always',dasn:'SLA-impacting · aggregated digest'}[r[0]];",tag='ADM-03 triggers')
rep("<em>Permission-gated dispatch engine</em> &mdash; define which roles receive outage SONAR alerts (SONAR: Shore Outage Notification, Analysis &amp; Response) on email, government-mobile push, and dashboard. Set severity thresholds, escalation timers, and run end-to-end test dispatches per installation.",
    "<em>Permission-gated dispatch engine</em> &mdash; define which roles receive outage SONAR alerts (SONAR: Site Outage Notification, Analysis &amp; Response) on email, SONARmobile push, and dashboard. Set severity thresholds, escalation timers, and run end-to-end test dispatches per site.",tag='ADM-03 desc')
rep("[['ts','Time','num'],['kind','Type','cat'],['code','Code','text'],['siteName','Installation','text'],['channels','Channels','text']]","[['ts','Time','num'],['kind','Type','cat'],['code','Code','text'],['siteName','Site','text'],['channels','Channels','text']]",tag='ADM-03 log col')
# ADM-04
rep("<em>Fleet operations for 140 instances</em> &mdash; primary/secondary status, sync lag, build versions and uptime for every installation pair. Force sync, restart, lock, or push a build wave by region.",
    "<em>Fleet operations for every instance pair</em> &mdash; primary/secondary status, sync lag, build versions and uptime for every site. Force sync, restart, lock, or push a build wave by market.",tag='ADM-04 desc')
rep('<span class="meta-pill">70 Pairs</span><span class="meta-pill">Sync</span>','<span class="meta-pill" id="card-health-pairs">Pairs</span><span class="meta-pill">Sync</span>',tag='ADM-04 pill')
rep("mini('Instances',s.instances,'#ffffff','70 pairs')","mini('Instances',s.instances,'#ffffff',s.sites+' pairs')",tag='ADM-04 strip')
rep("C.audit('FORCE_SYNC','ALL SITES','140 instances');toastOk('Sync forced on all 140 instances');","C.audit('FORCE_SYNC','ALL SITES',C.summary().instances+' instances');toastOk('Sync forced on all '+C.summary().instances+' instances');",tag='ADM-04 sync all')
rep("'ah-region':{label:'REGION',plural:'REGIONS',all:'ALL REGIONS'","'ah-region':{label:'MARKET',plural:'MARKETS',all:'ALL MARKETS'",tag='ADM-04 region filter')
rep("'ah-site':{label:'INSTALLATION',plural:'INSTALLATIONS',all:'ALL INSTALLATIONS'","'ah-site':{label:'SITE',plural:'SITES',all:'ALL SITES'",tag='ADM-04 site filter')
# ADM-06 · settings banner only
rep("NAVY-WIDE DEPLOYMENT · 70 INSTALLATIONS · 140 INSTANCES · FOUNDRY ADVANA HOSTED · ","DATA CENTER PORTFOLIO · COLO / ENT / EDGE · 2 INSTANCES PER SITE · FOUNDRY ADVANA HOSTED · ",tag='ADM-06 banner')
# ADM-08
rep('<div class="card-title"><span style="color:#9ebc52;">SONAR</span> <span style="color:#ffffff;">Outage Detection</span></div>','<div class="card-title"><span style="color:#9ebc52;">SONAR</span> <span style="color:#ffffff;">Drill Builder</span></div>',tag='ADM-08 title')
rep("<em>Shore Outage Notification, Analysis &amp; Response</em> &mdash; build a base outage scenario with an AI analyst at your side: queue SONAR alerts from a template library, select the installation, set the trigger and severity, place SMR / BESS / microgrid assets against peak demand, size manpower and reporting, then hand the scenario to the Admin Platform for dispatch review.",
    "<em>Site Outage Notification, Analysis &amp; Response</em> &mdash; the same Drill Builder that ships on the data-center phone: queue SONAR alerts from a template library, pick the site or portfolio (colocation, enterprise, edge), set the trigger and severity, place generator / UPS / BESS assets against IT load, size the on-call crew and reporting, then release the drill for dispatch review or send it to the Data Drop Zone.",tag='ADM-08 desc')
rep('<span class="meta-pill">7-Step Builder</span><span class="meta-pill">AI Analyst</span><span class="meta-pill">SONAR Alerts</span><span class="meta-pill">16 Installations</span>',
    '<span class="meta-pill">7-Step Builder</span><span class="meta-pill">Drop Zone</span><span class="meta-pill">SONAR Alerts</span><span class="meta-pill">COLO · ENT · EDGE</span>',tag='ADM-08 pills')
# ADM-09
rep("<em>Ledger of every ADMIN &harr; CMDR mobile envelope</em> &mdash; SONAR alerts, acknowledgments, messages, status and hello handshakes in both directions, with transport, delivery latency and commander ack round-trip.",
    "<em>Ledger of every console &harr; SONARmobile envelope</em> &mdash; SONAR alerts, acknowledgments, messages, status, BattleCat assessments and hello handshakes in both directions, with transport, delivery latency and ack round-trip.",tag='ADM-09 desc')
# ADM-10
rep('<div class="card-title"><span style="color:#4db88a;">CMDR</span> <span style="color:#ffffff;">Mobile</span></div>','<div class="card-title"><span style="color:#4db88a;">SONARmobile</span> <span style="color:#ffffff;">Data Center</span></div>',tag='ADM-10 title')
rep("<em>Base commander companion app</em> &mdash; open the phone app, see which commanders are linked, push a test SONAR alert or a health snapshot, watch acknowledgments come back, and set the transport (same-browser or GitHub cross-device). Every envelope lands in ADM-09.",
    "<em>Critical facilities companion app</em> &mdash; open the data-center edition of SONARmobile (Broad Run · LDN1 sample), see which site leads are linked, push a test SONAR alert or a health snapshot, watch acknowledgments and BattleCat assessments come back, and set the transport (same-browser or GitHub cross-device). Every envelope lands in ADM-09.",tag='ADM-10 desc')
rep('<span class="overlay-app-name" style="color:#4db88a;">ADM-10 // CMDR MOBILE</span>','<span class="overlay-app-name" style="color:#4db88a;">ADM-10 // SONARMOBILE · DATA CENTER</span>',tag='ADM-10 overlay name')
rep('<div class="cm-box"><h4>LINKED COMMANDERS <span id="cx-peer-n"></span></h4>','<div class="cm-box"><h4>LINKED SITE LEADS <span id="cx-peer-n"></span></h4>',tag='ADM-10 peers hdr')
rep("chip.innerHTML='<i></i><span id=\"cl-txt\">CMDR LINK</span>';chip.title='Open ADM-10 CMDR Mobile';","chip.innerHTML='<i></i><span id=\"cl-txt\">PHONE LINK</span>';chip.title='Open ADM-10 SONARmobile';",tag='link chip')
# ADM-11 card
rep("<em>Exercise planning &amp; commander authorization</em> &mdash; build the black start exercise record (10 USC 2920), critical-asset and mitigation lists, and findings; request CO approval and go / no-go on SONARmobile, track statutory count and the DoN five-year cadence, and push the exercise to the phone.",
    "<em>Pull-the-plug planning &amp; director authorization</em> &mdash; build the black start test record (Uptime Institute Tier III · NFPA 110), critical-load and mitigation lists, and findings; request Facility Director approval and go / no-go on SONARmobile, track the annual test cadence, and push the drill to the phone.",tag='ADM-11 desc')
rep('<span class="meta-pill" id="card-bs-fy">FY26 · 0/5</span><span class="meta-pill" id="card-bs-auth">CO · —</span><span class="meta-pill">10 USC 2920</span><span class="meta-pill">DoDI 4170.11</span>',
    '<span class="meta-pill" id="card-bs-fy">FY26 · 0/1</span><span class="meta-pill" id="card-bs-auth">DIR · —</span><span class="meta-pill">Uptime Tier III</span><span class="meta-pill">NFPA 110</span>',tag='ADM-11 pills')

# ─────────────────────────────────────────────────────────────────────────────
# 7. ADM-11 module · data-center black start (matches the phone's Tier III / NFPA 110 model)
# ─────────────────────────────────────────────────────────────────────────────
BS0='/* ══ ADM-11 BLACK START · exercise planning + commander authorization ══ */'; BS1='  window.ADM_BS={select:select'
def bs(a,b_,tag): rep_between(BS0,BS1,a,b_,'ADM-11 '+tag)
bs("var OBJ=[['A','Start independently, transfer and carry the load','until off-installation energy is restored'],['B','Align organizations with critical missions','tenant commands · PWD · EM · Mission Assurance'],['C','Validate mission operation plans','COOP and continuity procedures'],['D','Identify infrastructure interdependencies','comms · water · fuel · HVAC · access control'],['E','Verify backup electric power performance','start / transfer / carry · power quality']];",
   "var OBJ=[['A','Start · generators start and ATS transfers inside the UPS runtime','NFPA 110 · 10 s start / transfer target'],['B','UPS · every hall rides through on battery with margin','runtime measured against the 11-minute floor'],['C','Cool · chillers and CRAH loops restart before inlet temperature drifts','ASHRAE A1 envelope held'],['D','N+1 · lose one generator and still carry the full IT load','concurrent maintainability per Tier III'],['E','Sync · resynchronise to the utility with no tenant impact','closed-transition retransfer · power quality']];",'objectives')
bs("var MS=[['M1','Kickoff & planning','CO approval · interviews with infrastructure and mission personnel · tentative date and scope'],['M3','Mitigation planning','Align with other exercises · mission impacts · stage mitigations'],['M6','Outage planning','Finalize scope and scenario · notify utility · build outage/restoration sequence'],['M8','Final planning','Verify mitigations · finalize sequence · notify personnel'],['M9','Conduct & collect','Walk-through · comms check · metering · mission verification'],['M12','Findings & COAs','Compile findings · brief CO · Corrective Action Plan to CNIC / NAVFAC']];",
   "var MS=[['M1','Kickoff & planning','Facility Director approval · tenant notice · vendor scheduling · scope'],['M3','EOP / MOP review','Update switching order · ATS and UPS procedures · stage mitigations'],['M6','Outage planning','Notify utility · tenant change windows · fuel top-off · restoration sequence'],['M8','Final planning','Verify mitigations · vendor standby · staff briefing · notify tenants'],['M9','Conduct & collect','Pull-the-plug · EPMS trend data · runtime verification'],['M12','Findings & CAPs','Compile findings · brief the Director · corrective actions into the CAPEX plan']];",'milestones')
bs("var AUTH=[['approve','CO approval','kickoff · scope, notice, exclusions, tentative date','Request approval','approved','declined'],['go','Go / No-go','day of exercise · weather, ships in port, ops, utility','Request go / no-go','go','nogo'],['abort','Abort authority','during execution · commander may halt and restore','Arm abort','armed','aborted'],['aar','AAR acceptance','after action · findings and corrective-action priority','Request acceptance','accepted','returned']];",
   "var AUTH=[['approve','Director approval','kickoff · scope, notice, exclusions, tentative date','Request approval','approved','declined'],['go','Go / No-go','day of test · weather, tenant change freeze, utility, fuel','Request go / no-go','go','nogo'],['abort','Abort authority','during execution · the Director may halt and retransfer','Arm abort','armed','aborted'],['aar','Findings acceptance','after action · findings and corrective-action priority','Request acceptance','accepted','returned']];",'auth')
bs("var TIERS=['DCA','TCA-1','TCA-2','TCA-3','TA-4'], BK=['GEN','GEN+UPS','UPS','MICROGRID','BESS','NONE'], FUND=['ERCIP','O&M','UESC','ESPC','UP','IEP'], SEV=['P1','P2','P3'], CAT=['Comms','HVAC / cold storage','Water / wastewater','Fuel / refueling','Backup location','Access / security','Key person','Equipment misconfig','Unidentified load'];",
   "var TIERS=['T1','T2','T3','MECH','NOC','SUPPORT'], BK=['GEN','UPS+GEN','UPS','BESS','NONE'], FUND=['CAPEX','OPEX','TENANT','VENDOR','INSURANCE'], SEV=['P1','P2','P3'], CAT=['NOC / BMS','Cooling','Fuel / refueling','ATS / switchgear','UPS / battery','Access / security','Key person','Equipment misconfig','Unidentified load'];",'lists')
bs("function seed(){return {id:'BSE-26-03',site:'nb-sd',siteName:'Naval Base San Diego',type:'BSE',date:'2026-10-14',durH:12,notice:'no-notice',scope:'whole-base',excl:{housing:true,commissary:true,exchange:true,mwr:true},utility:'SDG&E',observer:'MIT Lincoln Laboratory',fy:2026,statutory:true,status:'planned',phase:-1,",
   "function seed(){return {id:'BSE-26-01',site:'br-ldn1',siteName:'Broad Run Data Center · LDN1',type:'BSE',date:'2026-10-14',durH:4,notice:'announced',scope:'whole-site',excl:{office:true,noc:false,cooling:false,security:true},utility:'Dominion Energy',observer:'Uptime Institute (M&O)',fy:2026,statutory:true,status:'planned',phase:-1,",'seed head')
i=s.index("      assets:[{n:'Regional Ops Center',tier:'DCA'"); j=s.index("]};}\n",i)+4
s=s[:i]+("      assets:[{n:'Hall A · Tier 1 racks',tier:'T1',owner:'Hall A tenants',bk:'UPS+GEN',kw:1800,fuel:71,r:[1,1,1]},{n:'Hall B · Tier 2 racks',tier:'T2',owner:'Hall B tenants',bk:'UPS+GEN',kw:2400,fuel:71,r:[1,1,1]},{n:'Hall B · Tier 3 racks',tier:'T3',owner:'Hall B tenants',bk:'UPS+GEN',kw:600,fuel:71,r:[1,0,1]},{n:'Chiller plant · CH1, CH2, CRAH loop',tier:'MECH',owner:'Mechanical',bk:'GEN',kw:1400,fuel:71,r:[1,1,0]},{n:'NOC · BMS / EPMS servers',tier:'NOC',owner:'NOC',bk:'UPS+GEN',kw:120,fuel:71,r:[1,1,1]},{n:'Fuel polishing & transfer pumps',tier:'SUPPORT',owner:'Facilities',bk:'GEN',kw:40,fuel:71,r:[0,0,1]}],\n"
    "      findings:[{sev:'P1',cat:'ATS / switchgear',f:'ATS-2 transferred at 14 s vs 10 s NFPA 110 target',ca:'Replace ATS-2 controller; monthly loaded transfer test',owner:'Facilities',fund:'CAPEX',st:'open'},{sev:'P1',cat:'Cooling',f:'CRAH-14 loop soft-started 4 min after generators · Hall 1 inlet drifted to 27 °C',ca:'Move CRAH-14 to the generator-priority bus; verify BMS restart sequence',owner:'Mechanical',fund:'CAPEX',st:'open'},{sev:'P2',cat:'Fuel / refueling',f:'Fuel transfer pumps unpowered for first 9 minutes',ca:'Backup feed to pump house; written refuel sequence with vendor',owner:'Facilities',fund:'VENDOR',st:'open'},{sev:'P2',cat:'Key person',f:'Only one operator can reset the chiller plant after a trip',ca:'Cross-train 3 operators; post reset SOP at the plant',owner:'Mechanical',fund:'OPEX',st:'funded'},{sev:'P3',cat:'Access / security',f:'Loading-dock access control fell back to manual',ca:'UPS + PoE backup for ACS panels',owner:'Security',fund:'OPEX',st:'open'},{sev:'P3',cat:'Unidentified load',f:'Tenant cage 2B lab bench not on the critical-load register',ca:'Add to the EPMS critical-load list',owner:'Customer Success',fund:'TENANT',st:'closed'}]};}\n")+s[j:]
LOG.append(('ADM-11 seed assets/findings',1))
bs("function blank(){var c=C(),site=(c&&c.SITES&&c.SITES[0])||{id:'nb-sd',name:'Naval Base San Diego'};return {id:nextId(),site:site.id,siteName:site.name,type:'BSE',date:'',durH:8,notice:'limited',scope:'whole-base',excl:{housing:true,commissary:true,exchange:true,mwr:true},",
   "function blank(){var c=C(),site=(c&&c.SITES&&c.SITES[0])||{id:'br-ldn1',name:'Broad Run Data Center · LDN1'};return {id:nextId(),site:site.id,siteName:site.name,type:'BSE',date:'',durH:4,notice:'announced',scope:'whole-site',excl:{office:true,noc:false,cooling:false,security:true},",'blank')
bs("f.textContent='FY'+String(fy()).slice(-2)+' · '+fyCount()+'/5';var a=$('card-bs-auth');if(a)a.textContent='CO · '","f.textContent='FY'+String(fy()).slice(-2)+' · '+fyCount()+'/1';var a=$('card-bs-auth');if(a)a.textContent='DIR · '",'card paint')
bs("mini('DoN BSEs · FY'+String(fy()).slice(-2),fyCount()+' / 5',fyCount()>=5?'#4db88a':'#ffb340')","mini('Pull-the-plug tests · FY'+String(fy()).slice(-2),fyCount()+' / 1',fyCount()>=1?'#4db88a':'#ffb340')",'strip fy')
bs("mini('§2920 objectives',pass+' / 5','#38e8ff')","mini('Tier III objectives',pass+' / 5','#38e8ff')",'strip obj')
bs("mini('CO approval',e.auth.approve?","mini('Director approval',e.auth.approve?",'strip approval')
bs("row('INSTALLATION','<select class=\"adm-sel\" onchange=\"ADM_BS.setSite(this.value)\">'","row('SITE','<select class=\"adm-sel\" onchange=\"ADM_BS.setSite(this.value)\">'",'row site')
bs("opts(['BSE','ERRE','ERTTX','CRRE'],e.type)","opts(['BSE','IST','LOADBANK','TTX'],e.type)",'type opts')
bs("hours · statute caps 5 days","hours · inside the tenant change window",'duration hint')
bs("opts(['whole-base','feeder','facility-set'],e.scope)","opts(['whole-site','hall','utility-feed','generator-only'],e.scope)",'scope opts')
bs("['housing','commissary','exchange','mwr'].map(function(k){","['office','noc','cooling','security'].map(function(k){",'excl labels')
bs("row('OBSERVER ORG',","row('WITNESS / AUDITOR',",'observer row')
bs("Counts toward the 5-per-year DoN floor (10 USC 2920(d)) through FY2032","Counts as the annual Tier III pull-the-plug test (Uptime Institute · NFPA 110 annual load test)",'statutory row')
bs("function addAsset(){cur().assets.push({n:'New facility',tier:'TCA-2',owner:'',bk:'GEN',kw:0,fuel:0,r:[null,null,null]});","function addAsset(){cur().assets.push({n:'New load',tier:'T2',owner:'',bk:'UPS+GEN',kw:0,fuel:0,r:[null,null,null]});",'add asset')
bs("function addFinding(){cur().findings.push({sev:'P2',cat:CAT[0],f:'',ca:'',owner:'',fund:'O&M',st:'open'});","function addFinding(){cur().findings.push({sev:'P2',cat:CAT[0],f:'',ca:'',owner:'',fund:'OPEX',st:'open'});",'add finding')
# ADM-11 markup
rep('<div class="bs-box"><h4>COMMANDER AUTHORIZATION <span style="color:#ffb340">SONARmobile</span></h4>','<div class="bs-box"><h4>DIRECTOR AUTHORIZATION <span style="color:#ffb340">SONARmobile</span></h4>',tag='ADM-11 auth hdr')
rep("Each request publishes a BSE_AUTH envelope to the installation channel. The commander answers from the Black start tile on SONARmobile;","Each request publishes a BSE_AUTH envelope to the site channel. The Facility Director answers from the Black start tile on SONARmobile;",tag='ADM-11 auth hint')
rep("Tier per DoDI 3020.45 &middot; Start / Xfer / Carry are the &sect;2920(h)(2)(A) results &mdash; click to cycle pass / fail / untested.","Tier per Uptime Institute / ANSI/TIA-942 &middot; Start / Xfer / Carry are the NFPA 110 start, transfer and carry results &mdash; click to cycle pass / fail / untested.",tag='ADM-11 assets hint')
rep('<div class="bs-box"><h4>&sect;2920 OBJECTIVES <span id="bs-obj-n"></span></h4>','<div class="bs-box"><h4>TIER III OBJECTIVES <span id="bs-obj-n"></span></h4>',tag='ADM-11 obj hdr')
rep('<table class="adm-tbl" id="bs-assets"><thead><tr><th>Asset / facility</th>','<table class="adm-tbl" id="bs-assets"><thead><tr><th>Load / hall</th>',tag='ADM-11 asset col')

# ─────────────────────────────────────────────────────────────────────────────
# 8. ARIA · persona and module map (the AI tile itself is unchanged)
# ─────────────────────────────────────────────────────────────────────────────
rep("'You are ARIA — AI Reconnaissance & Intelligence Assistant embedded in the ie-SRS ' +\n    'SYSTEM ADMIN PLATFORM, the enterprise control console for ie-SRS (Intelligent Energy ' +\n    'SONAR — Shore Outage Notification, Analysis & Response — Reconnaissance, Simulation) deployed across 70 Navy installations and hosted on Foundry ADVANA. ' +",
    "'You are ARIA — AI Reconnaissance & Intelligence Assistant embedded in the SONAR ' +\n    'DATA CENTER CONSOLE, the portfolio control console for SONAR (Site Outage Notification, Analysis & Response) ' +\n    'deployed across a portfolio of colocation, enterprise and edge data centers and hosted on Foundry ADVANA. ' +",tag='ARIA persona')
rep("'military and energy-domain terminology where appropriate.","'critical-facilities and energy-domain terminology (NOC, halls, racks, UPS, ATS, generators, tenants, SLAs) where appropriate.",tag='ARIA tone')
rep("'- ADM-01: User Accounts — 140 seats (a Facility Manager and a Backup Facilities Support account at each of 70 installations). Enable, disable, reset keys, enroll government devices, export CSV, provision new accounts with role templates and CAC/PIV binding.\\n' +",
    "'- ADM-01: User Accounts — two seats per site (a Critical Facilities Manager and a Facilities On-call account). Enable, disable, reset keys, enroll devices, Face ID, export CSV, provision new accounts with role templates.\\n' +",tag='ARIA ADM-01')
rep("'- ADM-02: Message Center — presence of every field user, channels (#all-hands, #sysadmins, #outage-watch, one per CNR region, per-site and direct messages), broadcasts and maintenance notices.\\n' +",
    "'- ADM-02: Message Center — presence of every field user, channels (#all-hands, #sysadmins, #outage-watch, one per market, per-site and direct messages), broadcasts and maintenance notices.\\n' +",tag='ARIA ADM-02')
rep("'- ADM-03: SONAR Alert Routing — recipient by channel matrix (Base Commander, Regional HQ, System Admin, Backup Facilities Support, DASN rollup against email, government-mobile alert, dashboard flag), severity threshold, escalation timer, failover authority, and test dispatches with a dispatch log.\\n' +",
    "'- ADM-03: SONAR Alert Routing — recipient by channel matrix (Critical Facilities Manager, NOC / Site Lead, Platform Admin, Facilities On-call, tenant digest against email, SONARmobile alert, dashboard flag), severity threshold, escalation timer, failover authority, and test dispatches with a dispatch log.\\n' +",tag='ARIA ADM-03')
rep("'- ADM-04: Instance Health and Deploy — primary and secondary instance status, sync lag, build versions, uptime for all 70 pairs; force sync, restart, close SONAR alerts, push build waves.\\n' +",
    "'- ADM-04: Instance Health and Deploy — primary and secondary instance status, sync lag, build versions, uptime for every site pair; force sync, restart, close SONAR alerts, push build waves by market.\\n' +",tag='ARIA ADM-04')
rep("'- ADM-07: Deployment Strategy — fourteen slides, one per page of the Enterprise Outage Visibility and SONAR Alert System document (10 pages plus addendum A-1 to A-4): mission, architecture, installation pair, outage-to-SONAR-alert workflow with a simulator, notification matrix, integration and connectivity map, engineering team, phased implementation with trackable checklists (the rollout tracker), risk register with status, and instance enrollment and call-home model.\\n' +",
    "'- ADM-08: SONAR Drill Builder — seven-step outage drill builder (alerts, site, trigger, assets, crew, reporting, review) for colocation, enterprise and edge sites; releases drills for dispatch review or drops them into SYS-04.\\n' +\n    '- ADM-09: Comms Log — every console ↔ SONARmobile envelope. ADM-10: SONARmobile Data Center — the phone app, linked site leads, test alerts, status snapshots, transport. ADM-11: Black Start — pull-the-plug test planning with Facility Director authorization on the phone. BattleCat assessments (BC_ASSESS) from the phone are audited here.\\n' +",tag='ARIA ADM-07→08-11')
rep("'- SYS-03: Global Map — all 70 installations coloured by instance health (healthy, degraded, offline, outage) with per-site instance, accounts, sync, routing and SONAR-alert panes and admin actions; 16 sites also carry full grid telemetry and an enterprise roll-up table.\\n' +",
    "'- SYS-03: Portfolio Map — every data center coloured by instance health (healthy, degraded, offline, outage) with per-site type, tier, market, utility, IT load, instances, accounts and SONAR-alert panes plus admin actions and a roll-up table.\\n' +",tag='ARIA SYS-03')
rep("'- SYS-04: Data Drop Zone — bulk ingest of rosters, device lists and CFE/DUERS extracts (XLSX, CSV, JSON).\\n\\n' +","'- SYS-04: Data Drop Zone — bulk ingest of rosters, device lists, EPMS / BMS extracts and drill scenarios (XLSX, CSV, JSON).\\n\\n' +",tag='ARIA SYS-04')
rep("'Two ie-SRS instances per installation: a Facility Manager primary and a Backup Facilities Support secondary that mirrors the primary and assumes SONAR-alert authority if the primary is unreachable. All 140 instances are provisioned and monitored from this Admin Platform on Foundry ADVANA. When a Facility Manager releases an outage SONAR alert it is routed by role and dispatched by email, government-mobile alert and dashboard flag to the Base Commander, Regional HQ and the System Admin; unacknowledged orders escalate. Every dispatch is audited.\\n\\n' +",
    "'Two SONAR instances per site: a Critical Facilities Manager primary and a Facilities On-call secondary that mirrors the primary and assumes SONAR-alert authority if the primary is unreachable. Every instance is provisioned and monitored from this console. When a site releases an outage SONAR alert it is routed by role and dispatched by email, SONARmobile alert and dashboard flag to the Critical Facilities Manager, the NOC / Site Lead and the Platform Admin; unacknowledged alerts escalate. Every dispatch is audited.\\n\\n' +",tag='ARIA deployment model')

# ─────────────────────────────────────────────────────────────────────────────
# 9. Computed seat / pair counts on the cards + minor labels
# ─────────────────────────────────────────────────────────────────────────────
rep("t(\"sp-t-dev\",s.devicesPending+\" DEVICES NOT ENROLLED\");}",
    "t(\"sp-t-dev\",s.devicesPending+\" DEVICES NOT ENROLLED\");t(\"card-users-seats\",(s.sites*2)+\" Seats\");t(\"card-health-pairs\",s.sites+\" Pairs\");}",tag='card counters')
rep("(x.w==='fm'?'FM':'BACKUP')","(x.w==='fm'?'CFM':'ON-CALL')",tag='presence role label')
rep("C.audit('CMDR_ACK',p.siteName||p.site||'',p.code+' acknowledged by '+p.by+' ('+(p.role||'Base Commander')+')","C.audit('CMDR_ACK',p.siteName||p.site||'',p.code+' acknowledged by '+p.by+' ('+(p.role||'Critical Facilities Manager')+')",tag='ack role')
rep("C.sendMsg(ch,p.text,'CMDR '+(p.by||'Base Commander')+' (mobile)');","C.sendMsg(ch,p.text,'CMDR '+(p.by||'Critical Facilities Manager')+' (mobile)');",tag='msg role')
rep("name:p[k].name||'Base Commander',app:p[k].app||'ie-SRS CMDR'","name:p[k].name||'Critical Facilities Manager',app:p[k].app||'SONARmobile DC'",tag='presence peer defaults')


# hub KPI strip + ARIA live context
rep("      k('Installations',s.sites,'#ffffff','11 CNR regions')+","      k('Sites',s.sites,'#ffffff',Object.keys(C.REG).length+' markets · COLO / ENT / EDGE')+",tag='strip sites')
rep("      k('Users online',s.usersOnline,'#18d4f8','FM + Backup seats')+","      k('Users online',s.usersOnline,'#18d4f8','CFM + On-call seats')+",tag='strip users')
rep("'- Installations under management: '+s.sites+' across 11 CNR regions; instances: '","'- Data centers under management: '+s.sites+' across '+Object.keys(C.REG).length+' markets (colocation, enterprise, edge); instances: '",tag='ARIA live context sites')
rep("'1 admin (web) · '+lp.mobile+' CMDR mobile'","'1 admin (web) · '+lp.mobile+' SONARmobile'",tag='strip mobile label')
rep("No CMDR mobile device linked","No SONARmobile device linked",tag='presence empty')
rep("<option>L1 — Responder · receive and acknowledge SONAR alerts (CMDR mobile)</option>","<option>L1 — Responder · receive and acknowledge SONAR alerts (SONARmobile)</option>",tag='L1 option')

rep_all('>&#8592; ADMIN</button>','>&#8592; CONSOLE</button>',tag='overlay back buttons')


# ─────────────────────────────────────────────────────────────────────────────
# 10. Brand · ie-SRS → SONAR-mobile everywhere a person reads it (repo paths, file names and the
#     ie-sra-bus wire channel stay as they are)
# ─────────────────────────────────────────────────────────────────────────────
rep_all('<span class="wm-ie">ie</span><span class="wm-dash">-</span><span class="wm-s">S</span>RS','<span class="wm-s">SONAR</span><span class="wm-dash">-</span><span class="wm-ie">mob<span class="wm-s">i</span>le</span>',tag='wordmark spans')
rep_all('wm-ie&quot;&gt;ie&lt;/span&gt;&lt;span class=&quot;wm-dash&quot;&gt;-&lt;/span&gt;&lt;span class=&quot;wm-s&quot;&gt;S&lt;/span&gt;RS','wm-s&quot;&gt;SONAR&lt;/span&gt;&lt;span class=&quot;wm-dash&quot;&gt;-&lt;/span&gt;&lt;span class=&quot;wm-ie&quot;&gt;mobile&lt;/span&gt;',tag='wordmark spans (srcdoc)') if 'wm-ie&quot;&gt;ie&lt;/span&gt;' in s else None
rep('<span class="c-esr-i">i<span class="c-esr-e">e</span></span>\n      <span class="c-esr-lbl">SONAR</span>','<span class="c-esr-i">SM</span>\n      <span class="c-esr-lbl">SONAR-mob<span style="color:#ff4757">i</span>le</span>',tag='chrome wordmark → SONAR-mobile')
rep_all("app:'ie-SRS ADMIN'","app:'SONAR-mobile DC Console'",tag='HELLO/KILL app name')
rep("app: 'ie-SRS ADMIN', linkCheck: true","app: 'SONAR-mobile DC Console', linkCheck: true",tag='link-check app name')
rep("bus.publish('HELLO',{node:'admin',app:'SONAR DC Console'},{site:env.site||'*'});","bus.publish('HELLO',{node:'admin',app:'SONAR-mobile DC Console'},{site:env.site||'*'});",tag='HELLO reply app name')
rep("real record in ie-srs-live. A heartbeat","real record in sonar-dc-live. A heartbeat",tag='live key comment')
_n=len(re.findall(r"(?<![/A-Za-z0-9_])ie-SRS(?![/._A-Za-z0-9]|-ADMIN)",s))
s=re.sub(r"(?<![/A-Za-z0-9_])ie-SRS(?![/._A-Za-z0-9]|-ADMIN)","SONAR-mobile",s); LOG.append(('ie-SRS text mentions → SONAR-mobile',_n))

# build marker
rep('</head>','<script>window.__DC_CONSOLE_BUILD="2026-09-21";</script>\n</head>',tag='build marker')

out=os.path.join(ROOT,'SONAR-DataCenter-Console.html')
open(out,'w',encoding='utf-8').write(s)
for t,c in LOG: print('%3d  %s'%(c,t))
print('wrote',out,len(s),'bytes')
