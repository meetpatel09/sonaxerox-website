# Guide for AI assistants (Claude Code, Claude in chat)

You are working on the **Sona Xerox** website and shop tools (sonaxerox.in). Read `README.md` first (2 minutes), then use the skills in `.claude/skills/`:

| Skill | Use it when |
|---|---|
| `sonaxerox-site-conventions` | building or changing any page; Gujarati/English; design; the dashboard-button rule |
| `sonaxerox-testing` | testing, debugging, or before handing over a file |
| `sonaxerox-deploy` | pushing to GitHub, pull requests, going live, rolling back |
| `sonaxerox-print-pipeline` | print orders, Apps Script, the shop-PC listener, prices, payments |
| `sonaxerox-image-tools` | /scan, the /print photo editor, HEIC, the Aadhaar tools |

## Slash commands (`.claude/commands/`)
`/setup-project` (check tools, tests, GitHub login) · `/ship <note>` (branch → tests → commit → push → PR, never merges) · `/verify-live` (live site == repo?) · `/new-page <what>` (new page the right way).

## Non-negotiables
1. **Every new page gets a button on `/our-tools/`** → `python3 tools/new_page.py …`.
2. Private tools are `noindex`; only pages in `sitemap.xml` are public.
3. All visible text in **Gujarati and English**; bundle the ₹ glyph on any page that shows prices.
4. **The repo is public — never write a secret, token or `listener.config.json` into a file, commit or message.**
5. Change through a branch + pull request; **never force-push `main`**; never delete `CNAME` or `google96403b7903aa5e97.html`.
6. Run `python3 tests/run_all.py` before saying it works, and say what you could not test.
7. Start from the repo's **current** file — the owner also edits files on GitHub.

## Commands
```bash
python3 -m http.server 8000                         # preview
python3 tests/run_all.py [--fast|--slow|--only X]   # tests
python3 tools/new_page.py slug "Title" "ગુજરાતી"    # new page (+ dashboard button + noindex)
python3 tools/verify_live.py                        # live site == repo?
```

## Style of work with the owner
Short, informal messages; he wants complete, immediately usable files, concise bullet answers, a screenshot/measurement for visual work, and honesty about what wasn't tested. When something is ambiguous ask **one** short question.
