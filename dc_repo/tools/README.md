# tools/
- `build_dc_console.py` — rebuilds `SONAR-DataCenter-Console.html` from the Navy ADMIN (`ie-SRS-ADMIN.html` → `src.html`), the
  phone's Drill Builder srcdoc (`dc_builder_srcdoc.txt`, cut from `cmdr/datacenter.html`) and `dcmap.html` (the SYS-03 module).
  Every substitution is guarded: a miss or a double hit aborts the build.
- `assemble_repo.py` — applies the repo-specific patches (bus repo, Pages URLs, guides, cache-bust) and writes icons, manifests,
  data files and docs. Change `ORG` / `REPO` there if the repo is renamed.
- `qa_dc_console.py` — Playwright QA (auth, every tile, SYS-03, ADM-08 drop, ADM-11 seed, bus aliasing, BattleCat, stores).
  `python3 tools/qa_dc_console.py` from the repo root.
- `dcmap.html` — SYS-03 Portfolio Map source (escaped into the console's srcdoc at build time).
- `fetch_face.sh` — re-download face-api.js + weights into `face/`.
