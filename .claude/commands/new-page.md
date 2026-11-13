---
description: Create a new page the Sona Xerox way (file, dashboard button, noindex, Gujarati + English, tests)
---
Create a new page: $ARGUMENTS

Follow the `sonaxerox-site-conventions` skill:
1. Run `python3 tools/new_page.py <slug> "<English title>" "<Gujarati title>"` and add `--public` (customers should find it on Google), `--paper` (cream main-site style) and `--rupee` (shows prices) only when they apply. If unsure whether it is public, ask me one short question.
2. Build the page. Every visible text must exist in Gujarati AND English.
3. Run `.venv/bin/python tests/run_all.py` and look at the page on desktop and phone size (Playwright screenshot).
4. Do not push. Tell me what to check and suggest `/ship`.
