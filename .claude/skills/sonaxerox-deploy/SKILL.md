---
name: sonaxerox-deploy
description: How to ship changes to sonaxerox.in through GitHub (repo meetpatel09/sonaxerox-website, GitHub Pages) — branch, tests, pull request, merge, verify the live files, roll back. Use whenever the user says push, deploy, commit, GitHub, "update the site", "upload this file", "it's not showing live", "workflow queued", pull request, rollback, DNS/domain, Search Console, or gives GitHub access — and whenever you finish a change that has to reach the live site.
---

# Deploying Sona Xerox

The site is served by **GitHub Pages from branch `main`, folder `/`**. A merge to `main` = live in about a minute. Pages are static; the Apps Script backend and the shop-PC listener are **not** deployed from GitHub (copied by hand — see `sonaxerox-print-pipeline`).

## Access
Prefer the **GitHub connector** (one-click, no secrets in chat). If a token is used, it must be a **fine-grained token limited to this repository** with *Contents: read/write* (+ *Pull requests: read/write*, *Actions: read*), short expiry, and it must never be written into a file, commit, log or message. Ask the user to revoke it when done. Never ask for the account password.

## Flow
1. `git switch -c <area>/<short-name>` (never commit to `main`).
2. Edit. Put related files in **one commit** (each commit starts a Pages build; two quick ones queue).
3. `python3 tests/run_all.py` — all green (CI runs the same on the pull request).
4. Commit message `area: what` (areas: site, print, scan, pdf-tools, aadhaar, voter, dashboard, backend, shop-pc, tests, docs, tools).
5. Push the branch, open a **pull request** (template has the checklist), wait for ✅, **merge**.
6. After ~1 minute: `python3 tools/verify_live.py` → every file `OK`. Open the changed page with Ctrl/Cmd+Shift+R.
7. Tell the user: what changed, which URL to open, what to look for, and that a hard refresh may be needed.

API checks without the UI (public repo, no token needed for reads):
`GET https://api.github.com/repos/meetpatel09/sonaxerox-website/actions/runs?per_page=3` (conclusion: success/failure) and `…/pages/builds/latest`.

## Rules
- **Never force-push `main`.** Roll back with `git revert <sha> && git push` (about a minute).
- **Never delete `CNAME` or `google96403b7903aa5e97.html`** (domain, Search Console). A test guards them.
- **No secrets in commits** (public repo). If one leaks: rotate it first, clean history after.
- Changing a page that is already live? Check `git log -- <file>`: the user sometimes edits files on GitHub directly, so **start from the repo's current file, not an old copy** (the live files were byte-identical to our latest on 13 Nov 2026, except the home page and pdf-tools which the user had edited).
- "Queued" Pages runs that sit for minutes are GitHub, not the site; the previous version stays live.
- Developer folders (`backend/ shop-pc/ tools/ tests/ docs/ assets-src/`) are kept off the website by `_config.yml`; add any new developer folder to its `exclude` list (a test fails otherwise).
- Domain/DNS (GoDaddy): four A records `185.199.108.153`, `.109.153`, `.110.153`, `.111.153` for `@`, `CNAME www → meetpatel09.github.io`; HTTPS enforced. Don't touch unless asked.

## First push of the project setup
Branch `project-setup` (several commits: scaffolding, docs, tests, skills, and one tiny head-only fix adding noindex/favicons). Push the branch → PR → check CI → merge → `verify_live.py`. After merging, re-submit `sitemap.xml` in Search Console.

See `references/commands.md` for copy-paste commands.
