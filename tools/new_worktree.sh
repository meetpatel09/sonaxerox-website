#!/usr/bin/env bash
# Create an isolated worktree for one update or bug fix, branched from fresh origin/main.
#   bash tools/new_worktree.sh <area/short-name>      e.g.  bash tools/new_worktree.sh print/fix-margin
# Worktrees live in ../sona-xerox-worktrees/<area>-<short-name>.
# .venv, tests/node_modules and tests/.fixtures are linked from the main checkout (no re-setup).
# Clean up after merging:  git worktree remove ../sona-xerox-worktrees/<folder> && git branch -D <branch>
set -euo pipefail
branch="${1:-}"
[[ "$branch" =~ ^[a-z0-9-]+/[a-z0-9._-]+$ ]] || { echo "Usage: bash tools/new_worktree.sh area/short-name  (lowercase, e.g. site/fix-footer)"; exit 1; }

main_dir="$(cd "$(dirname "$0")/.." && git rev-parse --path-format=absolute --git-common-dir)"
main_dir="$(dirname "$main_dir")"          # the main checkout (parent of .git)
dest="$(dirname "$main_dir")/sona-xerox-worktrees/${branch//\//-}"
[ -e "$dest" ] && { echo "Already exists: $dest"; exit 1; }

git -C "$main_dir" fetch origin main
mkdir -p "$(dirname "$dest")"
git -C "$main_dir" worktree add -b "$branch" "$dest" origin/main --no-track

for p in .venv tests/node_modules tests/.fixtures; do
  [ -e "$main_dir/$p" ] && ln -s "$main_dir/$p" "$dest/$p"
done
echo; echo "Ready: $dest  (branch $branch, from latest origin/main)"
echo "Next:  cd \"$dest\""
