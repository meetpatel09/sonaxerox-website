## What changed and why
<!-- one or two lines, in plain words -->

## Checklist
- [ ] `python3 tests/run_all.py` is green (CI also runs it)
- [ ] New page? Made with `tools/new_page.py` (dashboard button ✔, `noindex` unless public ✔)
- [ ] Every new text exists in **Gujarati and English**
- [ ] Shows ₹? The rupee glyph is bundled
- [ ] Checked on a **phone** (or the phone-size tests cover it)
- [ ] No secrets in the diff (`SECRET`, tokens, `listener.config.json`)
- [ ] Related changes are in **one** commit where possible (each commit = one Pages build)
- [ ] After merge: `python3 tools/verify_live.py` shows all OK
