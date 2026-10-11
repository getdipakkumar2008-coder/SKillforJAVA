# SKILL.md Template

Every skill in `.claude/skills/` follows this template. It is the 12-part structure from section 7 of the original master prompt (with "Related skills and official references" kept as two headings). The `scripts/validate-skills.sh` check enforces the format.

> Note: a second "mandatory template" was referenced in a later request but its text was not received. If it differs from this one, replace this file and the `required` list in `scripts/validate-skills.sh`, then re-align.

## Frontmatter (Claude Code)

```yaml
---
name: <directory-name>            # lowercase letters, numbers, hyphens; equals the folder name
description: <what it does and when to use it, key use case first; under 1,536 characters>
---
```

Frontmatter occupies lines 1-4. Only `name` and `description` are used, which also keeps the skills portable to other uploads that allow few keys. Keep `SKILL.md` under 500 lines; put detail in `references/` and link to it.

## Mandatory headings (exact text, `##` level)

| # | Heading | Contents |
|---|---|---|
| 1 | `Purpose` | One short paragraph: the responsibility and its boundary |
| 2 | `Activation conditions` | Signals (files, dependencies, request types) that trigger the skill and what is out of scope |
| 3 | `Required context and inputs` | What the agent must know before acting (versions, constraints, requirements) |
| 4 | `Repository inspection` | Concrete files/commands to read to learn the repo's setup and conventions |
| 5 | `Decision rules` | If/then rules that choose between approaches; defaults and exceptions |
| 6 | `Workflow` | Ordered steps from understanding to report |
| 7 | `Implementation guidance` | How to write the change: patterns, idioms, config, version notes |
| 8 | `Security and reliability requirements` | Controls and failure handling this area must enforce |
| 9 | `Common anti-patterns` | Concrete mistakes to avoid |
| 10 | `Testing and verification` | Tests and checks to run; how to prove the change; what to report as not run |
| 11 | `Definition of done` | Checklist-style completion criteria, evidence required |
| 12 | `Related skills` | Names of skills to combine or hand off to (backticked) |
| 13 | `Official references` | Authoritative URLs (never copied content) |

## Allowed extra sections
Add skill-specific sections where they help, placed near related content (typically between Activation conditions and Required context, or between Decision rules and Workflow / after Implementation guidance). Existing examples:

- `Version awareness (checked YYYY-MM-DD)` - verified versions and what could not be confirmed
- `Scope boundaries`, `Classify the application first`, `Portable vs engine-specific`
- `Java/Kotlin interoperability`, `Jetpack and Compose`, `Kotlin in Spring Boot projects`
- `Diagnose with evidence`, `Diagnostic toolbox by symptom`, `Upgrade workflow`
- `Review lenses`, `Severity and confidence`, `Report format`, `Self-review mode`
- `Task-to-skill mapping`, `Release preparation`, `ADR guidance`

Do not duplicate a mandatory heading and do not rename one. Section order for the mandatory headings should follow the table; extras may sit between them.

## Writing rules
- Actionable and repository-aware: procedures an agent follows inside an existing codebase, not tutorials.
- Respect the repository's versions and conventions; state version-sensitive facts with a "checked on" date, and say what was not verified.
- Reference other skills by backticked name; keep technology boundaries (Boot vs Security vs JPA vs Hibernate vs web vs Android) distinct.
- Never claim a check passed unless it was run; the Testing section tells the agent to report what was not run.
- Link to official sources; do not paste documentation.

## Checking
```bash
bash scripts/validate-skills.sh          # from the repository root; exit code 1 on any failure
```
It verifies frontmatter, name equals directory, description and file length, all mandatory headings, no duplicate headings, valid cross-references to other skills, and links to files inside the skill folder. It does not check technical accuracy or URL reachability.
