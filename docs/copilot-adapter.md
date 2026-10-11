# GitHub Copilot Adapter

The skills use the open **Agent Skills** format (`SKILL.md` with `name` and `description` frontmatter), which GitHub Copilot also supports. The adapter therefore adds almost nothing new: it makes sure Copilot finds the skills and gives Copilot surfaces that do not load skills a lightweight fallback.

## What GitHub documents (fetched 2026-10-11)

| Topic | Per GitHub docs / Agent Skills spec |
|---|---|
| Project skill locations | `.github/skills`, **`.claude/skills`**, or `.agents/skills` in the repository |
| Personal skill locations | `~/.copilot/skills` or `~/.agents/skills` |
| Surfaces that use skills | Copilot cloud agent, Copilot code review, Copilot CLI, Copilot app, agent mode in VS Code and JetBrains IDEs |
| Frontmatter | `name` and `description` required; `license` and `allowed-tools` optional (this repo sets only the first two) |
| Activation | Copilot decides from the prompt and the skill's `description`; then injects `SKILL.md` and makes the skill folder's files available |
| Naming limits (Agent Skills spec) | `name`: 1-64 chars, lowercase letters/digits/hyphens, no leading/trailing/double hyphens, equals directory name; `description`: max **1024** chars; keep `SKILL.md` under 500 lines |
| Repository instructions | `.github/copilot-instructions.md` (all requests), `.github/instructions/*.instructions.md` with `applyTo` globs (optional `excludeAgent: "code-review"` or `"cloud-agent"`), `AGENTS.md` anywhere (nearest wins), or a root `CLAUDE.md` |
| Instruction users | Cloud agent (all three types), code review (repository-wide and path-specific, read from the PR head branch), Chat (repository-wide) |

Consequences:
- The skills in `.claude/skills/` already work in Copilot's skill-aware surfaces without modification. All 18 skills satisfy the Agent Skills limits (checked by `scripts/validate-skills.sh`, which now enforces the 1024-character description cap and naming rules).
- Copilot Chat in plain (non-agent) mode is **not** listed as a skills surface, so it only sees the instruction files. Those are the fallback.

## What the adapter adds

```text
adapters/copilot/
  copilot-instructions.md                  repository-wide bootstrap: start with java-engineering-core, task->skill table, non-negotiables
  instructions/
    java-source.instructions.md            applyTo **/*.java
    java-build.instructions.md             applyTo pom/gradle/version catalog/Dockerfile
    java-tests.instructions.md             applyTo test source sets
    java-data.instructions.md              applyTo migrations, repositories, entities
    java-web-security.instructions.md      applyTo controllers, security config, application properties
    android.instructions.md                applyTo AndroidManifest, res, app sources
scripts/install-skills.sh                  installs skills and (for Copilot) the instruction files into another repo
```

Design choices:
- The instruction files are short and **point to skills by name** instead of copying their content, so there is one source of truth.
- They restate only the non-negotiables (honest verification, no weakened tests or security, version respect), because instruction files are always in context while skills load on demand.
- `applyTo` globs are comma-separated strings in quotes, as GitHub documents. No `excludeAgent` is set, so code review and the cloud agent both read them.

## Installing

```bash
# Claude Code only
bash scripts/install-skills.sh /path/to/project --agent claude

# Copilot only (skills in .github/skills + instruction files)
bash scripts/install-skills.sh /path/to/project --agent copilot

# Both (default): skills once in .claude/skills (Copilot reads it too) + Copilot instruction files
bash scripts/install-skills.sh /path/to/project

# A subset, preview first
bash scripts/install-skills.sh /path/to/project --skills spring-boot-engineering,java-testing-quality --dry-run
```

Rules: `java-engineering-core` is always included; nothing is overwritten without `--force`; an existing `.github/copilot-instructions.md` is left alone (merge the adapter file into it by hand). If you install a subset, edit the skill table in `copilot-instructions.md` to match. Do not install the same skills in both `.claude/skills` and `.github/skills` of one repository (duplicates may confuse discovery - not tested).

Personal install for all projects: copy the skill folders to `~/.copilot/skills` (Copilot) or `~/.claude/skills` (Claude Code).

## Using Spec Kit with Copilot
Spec Kit documents `specify init <project> --integration copilot` (the integration key is replaceable per agent). The `java-spec-driven-development` skill is agent-neutral: it discovers the spec artifacts and commands from the repository. Install this skill base after `specify init` so the generated Copilot files and these skills coexist.

## Differences and limitations (be aware)

| Item | Status |
|---|---|
| Claude Code-only frontmatter (`disable-model-invocation`, `context: fork`, `paths`, hooks) | Not used by these skills, so nothing is lost in Copilot |
| `CLAUDE.md` references in skills | Skills also name `AGENTS.md` and now `.github/copilot-instructions.md` as instruction files to read |
| Skill activation quality in Copilot | **Untested.** Descriptions are written for keyword/semantic matching; no trigger tests were run in either agent |
| Copilot behaviour on `references/` files | GitHub says skill folder files are made available on activation; whether links like `references/definition-of-done.md` are followed automatically is **not documented** - the core skill states them as links and the instruction bootstrap tells the agent to open `SKILL.md` files itself |
| Code review surface | GitHub notes a review-focused directory name helps; `java-code-review` includes "code-review" in its name. Instruction length limits for code review are not documented on the page fetched - keep instruction files short |
| `allowed-tools` / permissions | Not set; Copilot will ask before tool use per its own policy |
| Windows | Scripts are Bash (Git Bash/WSL). No PowerShell installer is provided |
| Enterprise/org-level instructions | Not covered |
| Verification | The installer was tested locally on scratch directories (dry run, fresh install, re-run without overwrite, subset, claude-only) and the installed copy passes the validation script. **No live Copilot session was used.** |

## Sources
- https://docs.github.com/en/copilot/concepts/agents/about-agent-skills
- https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-skills
- https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions
- https://agentskills.io/specification
