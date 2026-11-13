---
description: Check and finish the local development setup (tools, tests, GitHub login) and report in plain words
---
Check this project's local setup and fix what is safe to fix. Work step by step and explain in simple English.

1. Print the git, python3 and node versions. If one is missing, say exactly how to install it (git: `xcode-select --install`; Python: python.org; Node: nodejs.org) and stop.
2. Show `git branch --show-current` and `git status --short`.
3. If the `.venv` folder is missing, run `bash tools/setup_dev.sh`. Otherwise run `.venv/bin/python tests/run_all.py --fast`.
4. Run `.venv/bin/python tests/run_all.py` (about 4 minutes) and summarise which suites passed. For any failure show the failing lines and your best guess why (the tests were written on Linux, so Mac fonts or pixels may differ). Do NOT edit tests or pages to make them pass without asking me first.
5. Run `gh auth status`. If I am not logged in, tell me to run `gh auth login` in my own terminal. Never ask for, read or handle tokens or passwords.
6. End with a ✅/❌ checklist and the ONE next thing I should do.

Do not push, merge, or delete anything.
