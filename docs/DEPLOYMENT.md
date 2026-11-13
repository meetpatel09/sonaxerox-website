# Deployment

## The normal flow (a change to the website)
```bash
git switch -c feature/short-name                  # never work directly on main
# …edit…
python3 tests/run_all.py                          # all green before you push (~4 min; --fast while editing)
git add -A && git commit -m "scan: add horizontal tilt line"      # message style below
git push -u origin feature/short-name             # GitHub runs the same tests (Actions → "tests")
# open a Pull Request → check the ✅ → Merge
```
Merging into `main` makes GitHub Pages rebuild automatically (Actions → *pages build and deployment*, ~40–60 s). Then:
```bash
python3 tools/verify_live.py                      # every live file must say OK (run again after a minute if something says DIFFERENT)
```
and open the changed page with **Ctrl/Cmd + Shift + R** (browsers cache pages).

**Put related file changes into ONE commit.** Every commit starts a Pages build; two quick commits make the second one wait ("Queued"). A "Queued" run that stays for a few minutes is GitHub, not the site — the previous version stays live meanwhile.

### Commit messages
`area: what changed` — areas: `site`, `print`, `scan`, `pdf-tools`, `aadhaar`, `voter`, `dashboard`, `backend`, `shop-pc`, `tests`, `docs`, `tools`.
Examples: `print: show the price in the footer` · `scan: fix HEIC photos` · `docs: update the deployment guide`.

## Rolling back
```bash
git revert <bad-commit-sha> && git push           # the site returns to the previous version in about a minute
```
Never force-push `main`. `git log --oneline -- print/index.html` lists the versions of one page.

## Keep these files forever
`CNAME` (the custom domain) and `google96403b7903aa5e97.html` (Google Search Console ownership). `tests/test_site_structure.py` fails if either is missing or wrong.

## Domain, DNS, HTTPS
GoDaddy, 3-year plan. DNS: four `A` records for `@` → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`; `CNAME www → meetpatel09.github.io`.
GitHub → repo → Settings → Pages: *Deploy from a branch*, `main`, `/ (root)`, custom domain `sonaxerox.in`, **Enforce HTTPS ✓**.

## Google Search Console
Property `sonaxerox.in` is verified by the HTML file above. After deploying `sitemap.xml`, open *Sitemaps* and (re)submit `sitemap.xml`
(an earlier submission pointed to a file that was not in the repository). Use *URL inspection → Request indexing* after big changes to `/` or `/print/`.

## The backend (Google Apps Script)
Not deployed from GitHub — copy the code by hand, see [`backend/README.md`](../backend/README.md). After pasting:
**Deploy → Manage deployments → ✏️ → Version: New version → Deploy** (the `/exec` URL stays the same, so the website needs no change).
The `SECRET` lives only in the Apps Script and in the shop PC's `listener.config.json`.

## The shop PC
Replace `listener.py` with the new version from GitHub; `listener.config.json` stays. Restart: double-click `stop-listener.bat`, then `start-listener-hidden.vbs`. See [`shop-pc/README.md`](../shop-pc/README.md).

## Secrets (the repo is public)
Never commit: the Apps Script `SECRET`, `listener.config.json`, API tokens, passwords. `tests/test_site_structure.py` scans for common token formats and for a non-template `SECRET`.
If one leaks anyway: **change it first** (new `SECRET` in Apps Script + shop PC), only then clean the history.

## If the site looks broken
1. Actions tab → latest *pages build and deployment* — red ✗ means the build failed (open it for the reason); the old version is still live.
2. Hard-refresh; try a private window.
3. `python3 tools/verify_live.py` — shows which file differs.
4. Roll back (above) and fix on a branch.
