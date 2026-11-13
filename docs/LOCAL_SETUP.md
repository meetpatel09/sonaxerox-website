# Working on your Mac (`/Users/meetpatel/sona-xerox-website`)

The repo lives on GitHub (`meetpatel09/sonaxerox-website`). Your Mac folder is a **clone** of it: you edit and test there, and `git push` sends changes to GitHub.

## 1. Get the folder (once)
```bash
cd /Users/meetpatel
git clone https://github.com/meetpatel09/sonaxerox-website.git sona-xerox-website
cd sona-xerox-website
# bring in the project-setup commits that were prepared in chat (the .bundle file from Downloads):
git fetch ~/Downloads/sonaxerox-project-setup.bundle project-setup:project-setup
git switch project-setup
```
Needs: **git** (`xcode-select --install`), **Python 3**, **Node.js**. Check with `git --version`, `python3 --version`, `node --version`.

## 2. Install the tools (once)
```bash
bash tools/setup_dev.sh
```
It creates a private Python environment (`.venv`), downloads the test browser, installs the test libraries, generates the test photos and runs a quick check.

## 3. Connect to GitHub (once)
GitHub does not accept your account password for `git push`. Easiest: the GitHub CLI.
```bash
brew install gh        # or download from cli.github.com
gh auth login          # GitHub.com → HTTPS → "Login with a web browser"
git push -u origin project-setup
```
Then open the pull request on GitHub, wait for the green ✅ (tests run there too), **Merge**, and run `.venv/bin/python tools/verify_live.py`.

## 4. Protect `main` (recommended, 2 minutes)
GitHub → repo → Settings → Branches → *Add branch ruleset* for `main`: **Require a pull request**, **Require status checks** (choose `tests` — it appears after the first run), **Block force pushes**. Then nothing, including an AI assistant with your credentials, can break the live site without a reviewed pull request.

## 5. Work with Claude Code in this folder
```bash
curl -fsSL https://claude.ai/install.sh | bash     # or: brew install --cask claude-code
cd /Users/meetpatel/sona-xerox-website
claude                                             # sign in with your Claude account the first time
```
Claude Code reads `CLAUDE.md` and the five skills in `.claude/skills/` automatically, and `.claude/settings.json` sets what it may do:
* **runs without asking:** read-only git, `git add/commit/switch`, `python3 tests/…`, `python3 tools/…`
* **asks first:** `git push`, `git pull/merge/rebase/reset`, installing packages
* **never:** `sudo`, `rm -rf`, force-push, pushing straight to `main`, reading `.env` or the shop PC's `listener.config.json`, editing `CNAME` or the Google verification file
Use `/permissions` inside Claude Code to see or change these rules.

## Let Claude Code do the whole setup itself
Things only **you** can do (they need your account / browser): sign in to Claude, click "trust this folder", approve each command it asks about, and log in to GitHub (`gh auth login`).
Everything else Claude Code does by itself.

**Stage 1 — first time (the project is not on the Mac yet).** Download `sonaxerox-project-setup.bundle` into Downloads, then:
```bash
cd /Users/meetpatel && claude
```
and paste this message:
```
You are setting up my Sona Xerox website project on this Mac. Do every step yourself and tell me in simple English what you did.
Stop and ask me only if a step fails or needs my login.

Goal: /Users/meetpatel/sona-xerox-website is a git clone of https://github.com/meetpatel09/sonaxerox-website.git, on the branch project-setup, with the tools installed.

1. Print the versions of git, python3 and node. If one is missing, tell me exactly how to install it and stop.
2. If /Users/meetpatel/sona-xerox-website does not exist, run: git clone https://github.com/meetpatel09/sonaxerox-website.git /Users/meetpatel/sona-xerox-website
   If it exists, never overwrite it: show git status, and continue only if it is that repository with no uncommitted changes.
3. Find the newest file matching ~/Downloads/sonaxerox-project-setup*.bundle (ls -t). If there is none, tell me to download it from our chat and stop.
   Otherwise, inside the repo run: git fetch <that bundle file> project-setup:project-setup   then: git switch project-setup
   (if a local branch project-setup already exists, fetch into the name project-setup-new instead and tell me).
4. Run: bash tools/setup_dev.sh   and show me the summary.
5. Run: .venv/bin/python tests/run_all.py   and tell me which suites passed. If any failed, show the failing lines and your guess why (the tests were written on Linux, so Mac fonts/pixels may differ). Do NOT change any test or page.
6. Run: gh auth status. If I am not logged in, tell me to run "gh auth login" in my own terminal. Never ask for or handle a token or password.
7. Do NOT push, merge, delete, or edit any file. End with a checklist (✅/❌ per step) and the one next thing I should do.
```

**Stage 2 — restart inside the project** (Claude Code reads `CLAUDE.md`, the skills, the slash commands and the permission rules from the folder you start it in):
```bash
cd /Users/meetpatel/sona-xerox-website && claude
```
then type `/setup-project` (re-checks everything and tells you what is left).

**Slash commands in this project** (type `/` to see them)
| Command | What Claude Code does by itself |
|---|---|
| `/setup-project` | checks tools, runs the tests, checks the GitHub login, reports ✅/❌ |
| `/ship <note>` | new branch → full tests → secret check → commit → (asks you) push → pull request. **Never merges.** |
| `/verify-live` | compares sonaxerox.in with the repo, retries once after 60 s |
| `/new-page <what>` | creates the page + dashboard button + noindex, builds it in Gujarati and English, tests it |

## Daily flow
```bash
git switch main && git pull --ff-only
git switch -c print/my-change      # …edit, test…  .venv/bin/python tests/run_all.py
git add -A && git commit -m "print: my change" && git push -u origin print/my-change   # → pull request → merge
```
