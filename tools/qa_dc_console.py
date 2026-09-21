#!/usr/bin/env python3
"""Behavioral QA: auth flow, portfolio core, every remaining tile opens, SYS-03 map, ADM-08 builder,
ADM-11 seed, bus site aliasing + BattleCat envelope, store namespacing, two-device (phone HELLO)."""
import http.server, threading, socketserver, os, json, sys, time
from playwright.sync_api import sync_playwright
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
srv=socketserver.TCPServer(('127.0.0.1',0),Q); port=srv.server_address[1]
threading.Thread(target=srv.serve_forever,daemon=True).start()
URL='http://127.0.0.1:%d/SONAR-DataCenter-Console.html'%port
fails=[]
def check(cond,msg):
    print(('PASS ' if cond else 'FAIL ')+msg); 
    if not cond: fails.append(msg)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':1440,'height':900})
    pg=ctx.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('dialog',lambda d:d.accept())
    pg.goto(URL); pg.wait_for_timeout(1500)
    check(pg.evaluate("typeof window.__DC_CONSOLE_BUILD")=='string','build marker present')
    check(pg.evaluate("document.title").startswith('SONAR // DATA CENTER CONSOLE'),'title')
    check(pg.evaluate("document.querySelector('#gh-gate .gg-t1').textContent")=='SONAR-mobile','gate wordmark SONAR-mobile')
    check(pg.evaluate("document.querySelector('.c-esr-lbl').textContent")=='SONAR-mobile','chrome wordmark SONAR-mobile')
    # ── auth: step 1 skip → step 2 master pin
    check(pg.evaluate("document.body.classList.contains('adm-locked')"),'body starts adm-locked')
    pg.evaluate("GHGATE.skip()"); pg.wait_for_timeout(600)
    for d in '201219': pg.evaluate("ADMLOCK.press(%s)"%d)
    pg.wait_for_timeout(1500)
    check(pg.evaluate("!ADMLOCK.isLocked()"),'master pin unlocks step 2')
    check(pg.evaluate("!document.body.classList.contains('adm-locked')"),'adm-locked released')
    # ── core
    core=pg.evaluate("(function(){var C=ADMIN_CORE,s=C.summary();return {sites:s.sites,inst:s.instances,regs:Object.keys(C.REG),br:!!C.SITE['br-ldn1'],nb:!!C.SITE['nb-sd'],ty:C.SITE['br-ldn1'].ty,fm:C.SITE['br-ldn1'].fm,util:C.SITE['mf-dc1'].utility,navy:C.SITES.filter(function(x){return /\\bNAS\\b|Naval|NSA /.test(x.name);}).length};})()")
    check(core['sites']==27 and core['inst']==54,'27 sites / 54 instances (%s)'%core)
    check(core['br'] and not core['nb'] and core['navy']==0,'portfolio ids: br-ldn1 in, nb-sd + Navy out')
    check(core['fm']['role'].startswith('CFM') and core['fm']['email'].endswith('@example.com'),'CFM seat + example.com')
    check(core['util']=='Oncor' and core['ty']=='COLO','site extras (utility/type) present')
    # ── card grid
    cards=pg.evaluate("Array.from(document.querySelectorAll('#card-grid .app-card')).map(function(c){return c.id;})")
    check('card-adm-strategy' not in cards and 'card-ie-srs-hub' not in cards,'ADM-07 + Core Hub removed')
    check(len(cards)==13,'13 tiles remain (%d)'%len(cards))
    seats=pg.evaluate("document.getElementById('card-users-seats').textContent")
    check(seats=='54 Seats','ADM-01 seat count computed: '+seats)
    pairs=pg.evaluate("document.getElementById('card-health-pairs').textContent")
    check(pairs=='27 Pairs','ADM-04 pair count computed: '+pairs)
    check(pg.evaluate("getComputedStyle(document.getElementById('demo-chrome-btn')).display")=='none','Navy demo button hidden')
    # ── every tile opens without a page error
    for cid in cards:
        ov=pg.evaluate("document.getElementById('%s').getAttribute('onclick')"%cid)
        n0=len(errs)
        pg.evaluate("document.getElementById('%s').click()"%cid); pg.wait_for_timeout(700)
        vis=pg.evaluate("Array.from(document.querySelectorAll('.app-overlay.visible')).map(function(o){return o.id;})")
        check(len(vis)>=1 and len(errs)==n0,'tile %s opens → %s (errors %d)'%(cid,vis,len(errs)-n0))
        if cid=='card-secres-hub':
            fr=pg.frame(name='frame-secres') or [f for f in pg.frames if 'Portfolio Map' in (f.title() or '')]
            frame=[f for f in pg.frames if f!=pg.main_frame and 'Portfolio' in f.title()]
            check(bool(frame),'SYS-03 map frame present')
            if frame:
                f=frame[0]; f.wait_for_timeout(1500)
                n=f.evaluate("document.querySelectorAll('#tbl tbody tr').length")
                check(n==27,'SYS-03 roll-up rows = 27 (%d)'%n)
                hasL=f.evaluate("!!window.L")
                mk=f.evaluate("document.querySelectorAll('.leaflet-marker-icon').length")
                check((mk==27) if hasL else ('unavailable' in f.evaluate("document.getElementById('map').textContent")),'SYS-03 markers = 27 or offline fallback (L=%s, %d)'%(hasL,mk))
                f.evaluate("selectAdminSite('br-ldn1')"); f.wait_for_timeout(500)
                check('Broad Run' in f.evaluate("document.getElementById('side').textContent"),'SYS-03 site panel selects Broad Run')
                f.evaluate("setTy('EDGE')"); f.wait_for_timeout(300)
                check(f.evaluate("document.querySelectorAll('#tbl tbody tr').length")==4,'SYS-03 EDGE filter → 4 sites')
                f.evaluate("setTy('ALL')"); f.evaluate("act('sync')"); f.wait_for_timeout(300)
                check(pg.evaluate("ADMIN_CORE.listAudit()[0].action")=='FORCE_SYNC','SYS-03 action → parent audit FORCE_SYNC')
        if cid=='card-adm-wargame':
            bf=[f for f in pg.frames if f!=pg.main_frame and 'Drill Builder' in (f.title() or '')]
            check(bool(bf),'ADM-08 drill builder frame present')
            if bf:
                f=bf[0]; f.wait_for_timeout(800)
                inst=f.evaluate("INSTALLATIONS.map(function(i){return i.branch;})")
                check(set(inst)=={'COLO','ENT','EDGE'},'builder installations are data-center types %s'%sorted(set(inst)))
                check('CONSOLE' in f.evaluate("document.querySelector('.c-back').textContent"),'builder back button says CONSOLE')
                # drop to zone through the parent bridge
                pg.evaluate("window.postMessage({type:'BUILDER_DROP',payload:{installation:'Broad Run Data Center - LDN1',trigger:'Utility feed A loss',severity:'P1',warningOrders:[{type:'SONAR',priority:'P1',tag:'Feed A'}],assets:[]}},'*')")
                pg.wait_for_timeout(600)
                dz=pg.evaluate("JSON.parse(localStorage.getItem('sra_dropzone')||'[]').length")
                check(dz>=1,'BUILDER_DROP → Data Drop Zone (%d items)'%dz)
                check(pg.evaluate("ADMIN_CORE.listAudit()[0].action")=='DRILL_DROP','BUILDER_DROP audited')
        if cid=='card-adm-bs':
            st=pg.evaluate("ADM_BS._S().list[0]")
            check(st['site']=='br-ldn1' and st['excl'].get('office') is True and st['assets'][0]['tier']=='T1','ADM-11 seed is Broad Run / Tier model')
            txt=pg.evaluate("document.getElementById('bs-strip').textContent")
            check('Pull-the-plug' in txt and 'Director approval' in txt and '2920' not in txt,'ADM-11 strip relabelled')
        pg.evaluate("document.querySelectorAll('.app-overlay.visible').forEach(function(o){closeApp(o.id);})"); pg.wait_for_timeout(300)
    # ── routing labels
    pg.evaluate("openApp('overlay-adm-routing')"); pg.wait_for_timeout(500)
    mt=pg.evaluate("document.getElementById('ar-matrix').textContent")
    check('Critical Facilities Manager' in mt and 'Base Commander' not in mt,'ADM-03 recipients relabelled')
    pg.evaluate("closeApp('overlay-adm-routing')")
    # ── stores namespaced
    keys=pg.evaluate("Object.keys(localStorage)")
    check(not [k for k in keys if k.startswith('adm_') or k.startswith('ie-srs-')],'no adm_/ie-srs- keys written: %s'%[k for k in keys if k.startswith('adm_') or k.startswith('ie-srs-')])
    check(any(k.startswith('dcc_') for k in keys),'dcc_ keys present')
    # ── bus: phone HELLO as nb-sd (data-center phone default) → STATUS for br-ldn1 ; BC_ASSESS audited
    pg.evaluate("SRABus.configure({transport:'broadcast'})"); pg.wait_for_timeout(300)
    ph=ctx.new_page(); ph.goto('http://127.0.0.1:%d/tools/blank.html'%port)
    ph.evaluate("""()=>{window.got=[];var bc=new BroadcastChannel('ie-sra-bus');bc.onmessage=function(e){window.got.push(e.data);};window.bc=bc;
      function env(type,payload,site){return {id:Date.now().toString(36)+Math.random().toString(36).slice(2,8),type:type,ts:Date.now(),from:'cmdr',to:'admin',site:site,payload:payload};}
      bc.postMessage(env('HELLO',{commander:'R. Thompson',app:'SONARmobile DC',siteName:'Broad Run Data Center · LDN1',sector:'UTILITY',utilType:'COLO'},'nb-sd'));
      setTimeout(function(){bc.postMessage(env('BC_ASSESS',{cat:'BC-2',target:'Utility feed A · 34.5 kV',v:'Fault is upstream',c:92,etr:['45 min','40 min'],rec:'Keep ATS-1 in GEN',site:'nb-sd'},'nb-sd'));},400);}""")
    pg.wait_for_timeout(1500)
    got=ph.evaluate("window.got")
    types=[g['type'] for g in got]
    st=[g for g in got if g['type']=='STATUS']
    check('STATUS' in types and st and st[0]['payload']['site']=='br-ldn1','phone HELLO as nb-sd → STATUS for br-ldn1 (%s)'%types)
    hello=[g for g in got if g['type']=='HELLO']
    check(hello and hello[0]['payload']['app']=='SONAR-mobile DC Console','console HELLO reply app name')
    check(pg.evaluate("ADMIN_CORE.listAudit().some(function(a){return a.action==='BATTLECAT_ASSESS'&&/92%/.test(a.detail);})"),'BC_ASSESS audited with confidence')
    check(pg.evaluate("CMDR_LINK.peers()['nb-sd']&&CMDR_LINK.peers()['nb-sd'].ty")=='COLO','peer records utilType from HELLO')
    # ── ADM-10 phone URL
    pg.evaluate("openApp('overlay-adm-cmdr')"); pg.wait_for_timeout(500)
    check('cmdr/datacenter.html' in pg.evaluate("document.getElementById('cx-url').textContent"),'ADM-10 phone URL → cmdr/datacenter.html')
    check(pg.evaluate("document.getElementById('cx-site').value")=='br-ldn1','ADM-10 default site br-ldn1')
    # ── ARIA prompt
    check(pg.evaluate("admAriaContext?admAriaContext().indexOf('70')<0:true"),'ARIA live context has no Navy counts')
    pg.screenshot(path='/tmp/dc_console_hub.png')
    print('page errors:',errs[:5])
    check(len(errs)==0,'no page errors (%d)'%len(errs))
    b.close()
srv.shutdown()
print('\n%d FAIL'%len(fails) if fails else '\nALL PASS')
sys.exit(1 if fails else 0)
