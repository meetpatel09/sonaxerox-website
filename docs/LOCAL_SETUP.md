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

## Daily flow
```bash
git switch main && git pull --ff-only
git switch -c print/my-change      # …edit, test…  .venv/bin/python tests/run_all.py
git add -A && git commit -m "print: my change" && git push -u origin print/my-change   # → pull request → merge
```
