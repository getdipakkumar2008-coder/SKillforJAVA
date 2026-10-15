#!/usr/bin/env bash
# Structural validation of the skill base. Usage: scripts/validate-skills.sh [skills-dir]
# Checks: frontmatter, name == directory, description length, SKILL.md length,
# mandatory template headings, cross-references to other skills, referenced files.
# Does NOT check technical accuracy or that URLs are reachable.
set -u
root="${1:-.claude/skills}"
max_lines=500
max_desc=1024   # Agent Skills open spec (Copilot and others); Claude Code allows 1536
required=(
  "Purpose"
  "Activation conditions"
  "Required context and inputs"
  "Repository inspection"
  "Decision rules"
  "Workflow"
  "Implementation guidance"
  "Security and reliability requirements"
  "Common anti-patterns"
  "Testing and verification"
  "Definition of done"
  "Related skills"
  "Official references"
)
fail=0
err() { echo "FAIL: $*"; fail=$((fail + 1)); }

[ -d "$root" ] || { echo "no such directory: $root"; exit 2; }
names=$(ls "$root")

for d in $names; do
  f="$root/$d/SKILL.md"
  [ -f "$f" ] || { err "$d: SKILL.md missing"; continue; }

  [ "$(sed -n '1p' "$f")" = "---" ] || err "$d: frontmatter must start on line 1"
  [ "$(sed -n '4p' "$f")" = "---" ] || err "$d: frontmatter must close on line 4 (name, description)"
  [ "$(sed -n '2p' "$f")" = "name: $d" ] || err "$d: 'name:' must equal directory name"
  # Agent Skills open spec: 1-64 chars, lowercase letters/digits/hyphens, no leading/trailing/double hyphen
  { [ "${#d}" -le 64 ] && echo "$d" | grep -Eq '^[a-z0-9]+(-[a-z0-9]+)*$'; } || err "$d: name violates Agent Skills naming rules"
  desc=$(sed -n '3p' "$f")
  case "$desc" in description:\ *) ;; *) err "$d: line 3 must be 'description: ...'";; esac
  [ "${#desc}" -le "$max_desc" ] || err "$d: description over $max_desc chars (${#desc})"

  lines=$(wc -l < "$f")
  [ "$lines" -le "$max_lines" ] || err "$d: $lines lines (limit $max_lines)"

  for h in "${required[@]}"; do
    grep -qx "## $h" "$f" || err "$d: missing heading '## $h'"
  done

  # duplicate top-level headings
  dups=$(grep '^## ' "$f" | sort | uniq -d)
  [ -z "$dups" ] || err "$d: duplicate headings: $dups"

  # cross-references to other skills (backticked names that look like skills)
  for ref in $(grep -oE '`(java|spring|hibernate)-[a-z-]+`' "$f" | tr -d '`' | sort -u); do
    case "$ref" in spring-boot-starter*|spring-boot-properties-migrator) continue;; esac
    [ -d "$root/$ref" ] || err "$d: references unknown skill '$ref'"
  done

  # relative links to files inside the skill directory
  for l in $(grep -oE '\]\((references/[^)#]+)\)' "$f" | sed -E 's/^\]\(//; s/\)$//' | sort -u); do
    [ -f "$root/$d/$l" ] || err "$d: broken link $l"
  done
done

# Copilot adapter: instruction templates need applyTo frontmatter; the index must name every skill
adapter="$(dirname "$root")/../adapters/copilot"
if [ -d "$adapter" ]; then
  for i in "$adapter"/instructions/*.instructions.md; do
    [ "$(sed -n '1p' "$i")" = "---" ] && sed -n '2p' "$i" | grep -q '^applyTo: ' || err "adapter: $(basename "$i") needs applyTo frontmatter"
  done
  for d in $names; do
    grep -q "\`$d\`" "$adapter/copilot-instructions.md" || err "adapter: copilot-instructions.md does not mention skill '$d'"
  done
fi

# Claude bootstrap: must tell the agent to invoke the core skill first and name every skill
cm="$(dirname "$root")/../adapters/claude/CLAUDE.md"
if [ -f "$cm" ]; then
  grep -q 'invoke the `java-engineering-core` skill first' "$cm" || err "adapter: adapters/claude/CLAUDE.md lacks the 'invoke java-engineering-core first' rule"
  for d in $names; do
    grep -q "\`$d\`" "$cm" || err "adapter: adapters/claude/CLAUDE.md does not mention skill '$d'"
  done
fi


# Plugin packaging: manifests, hook and templates must be valid and consistent
repo_root="$(dirname "$root")/.."
if command -v node >/dev/null 2>&1; then
  node - "$repo_root" <<'NODE' || fail=$((fail + 1))
const fs = require('fs'), path = require('path');
const root = path.resolve(process.argv[2]);
let bad = 0;
const err = (m) => { console.log('FAIL: plugin: ' + m); bad++; };
function load(rel) {
  try { return JSON.parse(fs.readFileSync(path.join(root, rel), 'utf8')); }
  catch (e) { err(rel + ' is missing or not valid JSON (' + e.message + ')'); return null; }
}
const plugin = load('.claude-plugin/plugin.json');
const market = load('.claude-plugin/marketplace.json');
const hooks = load('hooks/hooks.json');
if (plugin) {
  if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(plugin.name || '')) err('plugin.json name must be kebab-case');
  for (const s of [].concat(plugin.skills || [])) {
    if (!s.startsWith('./')) err('plugin.json skills path must start with ./ : ' + s);
    else if (!fs.existsSync(path.join(root, s))) err('plugin.json skills path not found: ' + s);
  }
}
if (plugin && market) {
  const entry = (market.plugins || []).find((p) => p.name === plugin.name);
  if (!entry) err('marketplace.json has no plugin entry named "' + plugin.name + '"');
}
if (hooks) {
  const cmds = JSON.stringify(hooks);
  const m = cmds.match(/\$\{CLAUDE_PLUGIN_ROOT\}\/([^"]+\.js)/);
  if (!m) err('hooks/hooks.json does not reference a hook script');
  else if (!fs.existsSync(path.join(root, m[1]))) err('hook script not found: ' + m[1]);
}
for (const f of fs.readdirSync(path.join(root, 'templates')).filter((x) => x.endsWith('.json'))) load('templates/' + f);
console.log(bad ? 'plugin packaging: FAILED' : 'plugin packaging: OK (plugin.json, marketplace.json, hooks.json, templates)');
process.exit(bad ? 1 : 0);
NODE
  node --check "$repo_root/hooks/java-session-start.js" 2>/dev/null || err "hooks/java-session-start.js has a syntax error"
  node --check "$repo_root/scripts/configure.js" 2>/dev/null || err "scripts/configure.js has a syntax error"
else
  echo "note: node not found - plugin packaging checks skipped"
fi
if command -v claude >/dev/null 2>&1; then
  vout="$(cd "$repo_root" && claude plugin validate . 2>&1)" || true
  echo "$vout" | grep -q "Validation failed" && err "claude plugin validate reported failures"
  echo "$vout" | grep -q "Validation passed" && echo "claude plugin validate: passed" || true
fi

# every skill name must be unique (directories are unique by construction)
echo "skills checked: $(echo "$names" | wc -w)"
if [ "$fail" -eq 0 ]; then echo "OK: all structural checks passed"; else echo "FAILED: $fail problem(s)"; exit 1; fi
