# Adoption Guide: making the Java Skill Base the default

This repository is both a **plugin** (`java-skills`) and the **marketplace** (`java-skill-base`) that serves it. Installed once, it applies to every Java, Spring Boot and Android project without anyone typing "use these skills".

## How the automatic part works

1. The plugin contributes the 18 skills (the manifest points at `.claude/skills/`, so there is one copy).
2. A `SessionStart` hook (`hooks/java-session-start.js`, Node.js) looks at the project. If it finds `pom.xml`, `build.gradle(.kts)` or an `AndroidManifest.xml` (up to 3 folders deep), it injects a short factual note into Claude's context: what was detected, the team convention that Java tasks start with `java-skills:java-engineering-core`, and the list of specialised skills. Non-Java projects get nothing.
3. The hook re-runs on `startup`, `resume`, `clear` and `compact`, so the convention survives context compaction.

A plugin cannot ship a `CLAUDE.md` (Claude Code ignores one at a plugin root), which is why the hook, not a file, supplies the convention.

## Who does what

| Audience | One-time action | Applies to | Can the user turn it off? |
|---|---|---|---|
| **Individual** | `node scripts/configure.js user --run` (or the two `claude plugin` commands it prints) | every project on this machine | yes (`claude plugin disable java-skills`) |
| **Team** | `node scripts/configure.js project <repo>` and commit `.claude/settings.json` | everyone who opens the repository, after they trust the folder and accept the install prompt | yes, by declining the prompt or disabling the plugin locally |
| **Organisation** | deploy `templates/managed-settings.json` (or `.strict.json`) as managed settings | every machine that receives the policy | **no** - managed settings take precedence over every other scope |

Managed settings can be delivered as a file (`/Library/Application Support/ClaudeCode/managed-settings.json` on macOS, `/etc/claude-code/managed-settings.json` on Linux/WSL, `C:\Program Files\ClaudeCode\managed-settings.json` on Windows), via MDM, or from the claude.ai admin console (Organization settings > Claude Code > Managed settings). `node scripts/configure.js managed [--strict] [--out file]` prints the policy:

- default: registers the marketplace and force-enables `java-skills@java-skill-base`, with `autoUpdate`
- `--strict`: additionally allow-lists only this marketplace, Anthropic's official one and skills-directory plugins (`strictKnownMarketplaces`), so users cannot add other sources

If your organisation sets `allowManagedHooksOnly`, hooks from plugins that are force-enabled in managed settings still run (per the Claude Code docs), so the force-enable above keeps the session hook working.

### Without the plugin (fallback)
`bash scripts/install-skills.sh --user` copies the skills to `~/.claude/skills` and adds a managed block (the same convention) to `~/.claude/CLAUDE.md`; `bash scripts/install-skills.sh <repo>` does it per repository, including `CLAUDE.md` and the GitHub Copilot instruction files. This works, but has no hook, no auto-update and no policy enforcement.

## What "by default" does and does not guarantee

- **Guaranteed (organisation scope):** the plugin is installed, enabled and cannot be switched off by users; the hook fires in every Java project.
- **Not guaranteed:** that the model always loads every relevant skill. The hook gives Claude the convention as context; it does not force tool calls. Measured result (see [validation-report.md](validation-report.md)): with the convention present, the core skill loaded in all measured cases and specialised skills loaded when the task touched their area; without it, loading was weak. Claude Code has no mechanism that forces a skill to run on every prompt.
- **Cost:** every enabled skill's name and description is in context on every turn (18 skills, about 600 characters each, roughly 3k tokens), plus one 2.4k-character note per session in Java projects.

## Releases and updates
`plugin.json` sets `"version"`, which pins users to that version until it changes. **Bump `version` in `.claude-plugin/plugin.json` for every release** (tag it too); otherwise installed users do not receive changes. Marketplace auto-update is on in the managed template. The default branch of the repository is what `github` marketplace sources fetch; merge to it (or set a `ref` with `--ref`) before rolling out.

## Opt-outs and requirements
- Per project: create `.claude/java-skills.off`. Per shell: `JAVA_SKILLS_DISABLE=1`.
- The hook needs `node` on `PATH`. If it is missing the hook fails without blocking the session, and only the skills (not the convention note) are active.
- Skills are namespaced by the plugin: invoke as `/java-skills:java-engineering-core`. Skill names inside the skill texts are bare; Claude resolves them (checked in the test run below).

## Verifying an installation
- `claude plugin list` shows `java-skills@java-skill-base` enabled; `/plugin` shows its components.
- Start a session in a Java project and ask "which Java skill convention applies to this project?": Claude can quote the note from the hook.
- Run the plugin-path trigger tests: `python scripts/check-triggers.py claude --plugin --ids core-01,web-01,neg-01 --yes` (spends API credits).
- Organisation rollout: `claude -p "hi" --output-format stream-json --verbose` shows the loaded plugins in the `init` event.

## Not yet verified
- A real managed-settings rollout on a fleet, and the claude.ai admin-console path (documented by Anthropic, not exercised here).
- Adding the marketplace from GitHub (validated locally with `claude plugin validate`; the end-to-end test loaded the plugin with `--plugin-dir`). The `--ref` form `owner/repo#branch` for `marketplace add` is assumed from the documentation, not tested.
- The hook on Windows machines without Node.js, and on other operating systems (tested on Windows 11 only).
- GitHub Copilot has no equivalent session hook that I verified; use `.github/copilot-instructions.md` (see [copilot-adapter.md](copilot-adapter.md)).
