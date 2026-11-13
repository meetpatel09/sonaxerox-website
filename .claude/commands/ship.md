---
description: Test, commit, push a branch and open a pull request (never merges)
---
Ship my current work safely. Extra instructions from me: $ARGUMENTS

1. If the current branch is `main`, create a branch named `area/short-name` that describes the change (areas: site, print, scan, pdf-tools, aadhaar, voter, dashboard, backend, shop-pc, tests, docs, tools). Never commit on `main`.
2. Run `.venv/bin/python tests/run_all.py`. If anything fails, stop and show me the failures.
3. Show `git diff --stat`. Make sure no secret, token, Apps Script SECRET or `listener.config.json` is in the changes (this repository is PUBLIC). Stop if you find one.
4. Commit with the message `area: what changed`. Put related files in ONE commit (every commit starts a GitHub Pages build).
5. Ask me to confirm. Then run `git push -u origin <branch>` and `gh pr create` with a short plain description and the checklist from `.github/pull_request_template.md`. Show me the pull request link.
6. Do NOT merge. Tell me to wait for the green ✅ on GitHub, merge it myself, and then run `/verify-live`.
