# tests/

Real-browser tests for the website and the shop-PC listener. Start with **[`docs/TESTING.md`](../docs/TESTING.md)**.

```bash
pip install -r tests/requirements.txt && python3 -m playwright install chromium
(cd tests && npm install)
python3 tests/run_all.py        # --fast | --slow | --only NAME
```
`common.py` = helpers · `scan_helpers.py` = scan-page helpers · `make_fixtures.py` = generates all photos/PDFs into `.fixtures/` (git-ignored).
