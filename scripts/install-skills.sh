#!/usr/bin/env bash
# Install the Java skill base into another repository.
#
# Usage: scripts/install-skills.sh <target-repo> [options]
#   --agent claude|copilot|both   default: both
#       claude  -> skills in <target>/.claude/skills
#       copilot -> skills in <target>/.github/skills + Copilot instruction files
#       both    -> skills in <target>/.claude/skills (GitHub Copilot also reads this folder)
#                  + Copilot instruction files in <target>/.github
#   --skills a,b,c                install only these skills (java-engineering-core is always added)
#   --force                       overwrite existing skill folders / instruction files
#   --dry-run                     print what would happen, change nothing
# Existing files are never overwritten without --force.
set -eu

here="$(cd "$(dirname "$0")/.." && pwd)"
src_skills="$here/.claude/skills"
src_copilot="$here/adapters/copilot"

target=""; agent="both"; only=""; force=0; dry=0
while [ $# -gt 0 ]; do
  case "$1" in
    --agent) agent="${2:?--agent needs a value}"; shift 2;;
    --skills) only="${2:?--skills needs a value}"; shift 2;;
    --force) force=1; shift;;
    --dry-run) dry=1; shift;;
    -h|--help) sed -n '2,15p' "$0"; exit 0;;
    -*) echo "unknown option: $1" >&2; exit 2;;
    *) [ -z "$target" ] && target="$1" || { echo "unexpected argument: $1" >&2; exit 2; }; shift;;
  esac
done

[ -n "$target" ] || { echo "usage: $0 <target-repo> [--agent claude|copilot|both] [--skills a,b] [--force] [--dry-run]" >&2; exit 2; }
[ -d "$target" ] || { echo "target directory does not exist: $target" >&2; exit 2; }
case "$agent" in claude|copilot|both) ;; *) echo "--agent must be claude, copilot or both" >&2; exit 2;; esac
target="$(cd "$target" && pwd)"
verb="installed"; [ "$dry" -eq 1 ] && verb="would install"
[ "$target" != "$here" ] || { echo "target is this repository; nothing to install" >&2; exit 2; }

run() { if [ "$dry" -eq 1 ]; then echo "[dry-run] $*"; else "$@"; fi; }

# which skills
if [ -n "$only" ]; then
  list="java-engineering-core $(echo "$only" | tr ',' ' ')"
else
  list="$(ls "$src_skills")"
fi
list="$(for s in $list; do echo "$s"; done | sort -u)"
for s in $list; do
  [ -d "$src_skills/$s" ] || { echo "unknown skill: $s" >&2; exit 2; }
done

case "$agent" in
  claude|both) skills_dest="$target/.claude/skills";;
  copilot) skills_dest="$target/.github/skills";;
esac

installed=0; skipped=0
run mkdir -p "$skills_dest"
for s in $list; do
  dest="$skills_dest/$s"
  if [ -e "$dest" ] && [ "$force" -eq 0 ]; then
    echo "skip (exists): $dest  (use --force to overwrite)"; skipped=$((skipped + 1)); continue
  fi
  [ -e "$dest" ] && run rm -rf "$dest"
  run cp -R "$src_skills/$s" "$dest"
  echo "$verb skill: $s -> $dest"; installed=$((installed + 1))
done

if [ "$agent" = "copilot" ] || [ "$agent" = "both" ]; then
  gh="$target/.github"
  run mkdir -p "$gh/instructions"
  if [ -e "$gh/copilot-instructions.md" ] && [ "$force" -eq 0 ]; then
    echo "skip (exists): $gh/copilot-instructions.md  - merge adapters/copilot/copilot-instructions.md into it manually"
  else
    run cp "$src_copilot/copilot-instructions.md" "$gh/copilot-instructions.md"
    echo "$verb: $gh/copilot-instructions.md"
  fi
  for f in "$src_copilot"/instructions/*.instructions.md; do
    b="$(basename "$f")"
    if [ -e "$gh/instructions/$b" ] && [ "$force" -eq 0 ]; then
      echo "skip (exists): $gh/instructions/$b"
    else
      run cp "$f" "$gh/instructions/$b"
      echo "$verb: $gh/instructions/$b"
    fi
  done
fi

echo "done: $installed skill(s) installed, $skipped skipped$([ "$dry" -eq 1 ] && echo ' (dry run)')"
if [ "$agent" != "claude" ]; then
  echo "note: the Copilot instruction files reference every skill by name; if you installed a subset, trim the table in copilot-instructions.md."
fi
