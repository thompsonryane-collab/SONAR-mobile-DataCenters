# SONAR-mobile · Data Center

Site Outage Notification, Analysis & Response for a portfolio of colocation, enterprise and edge data centers.
Two surfaces, one bus:

| Surface | File | What it is |
|---|---|---|
| Data Center Console | `SONAR-DataCenter-Console.html` | Desktop console — accounts, SONAR alert routing, instance health, portfolio map, drill builder, black start planning, audit and comms logs |
| SONARmobile · Data Center | `cmdr/datacenter.html` | The phone app for the Critical Facilities Manager — alerts, outages, tenant impact, live campus map, BattleCat, black start, drills |

Live: `https://thompsonryane-collab.github.io/sonar-mobile-dc/` (GitHub Pages from `main`, repo root — keep `.nojekyll`).

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
