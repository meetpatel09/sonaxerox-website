# Commands

```bash
# start a change
git fetch origin && git switch main && git pull --ff-only
git switch -c print/price-footer

# test & commit (one commit for related files)
python3 tests/run_all.py
git add -A && git commit -m "print: show the price in the footer"

# publish for review
git push -u origin print/price-footer
# → open the Pull Request on GitHub (or with the connector), wait for the green tick, Merge (squash is fine)

# verify
python3 tools/verify_live.py            # all OK?  (DIFFERENT right after a deploy = still building, retry in a minute)

# undo a bad release
git switch main && git pull --ff-only
git revert <sha> && git push

# which version of a page was live when?
git log --format='%h %ad %s' --date=short -- print/index.html
git show <sha>:print/index.html > /tmp/old-print.html
```

Pages build status: <https://github.com/meetpatel09/sonaxerox-website/actions> → *pages build and deployment*.
Live hash check of one file: `curl -s https://sonaxerox.in/print/ | sha256sum` vs `sha256sum print/index.html`.
