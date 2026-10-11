# Java Technology Skill Base

A modular library of **Claude Code skills** that guide an AI coding agent through real Java engineering work inside an existing repository: core Java, Spring Boot, Spring Data JPA, Hibernate, Spring Security, web/REST, Android (Java), databases, testing, messaging, performance, deployment, AI integration, and Spec Kit workflows.

The skills are actionable procedures, not tutorials. A task activates only the skills it needs; `java-engineering-core` is the shared foundation that discovers the repository, selects the other skills, and enforces honest verification.

> Status: all 18 skills and the supporting docs are written. They were validated by **structural checks and manual review only** - they have not yet been exercised on real projects. See [docs/validation-report.md](docs/validation-report.md).

## Contents

| Path | Purpose |
|---|---|
| `.claude/skills/<name>/SKILL.md` | The 18 skills (see catalog) |
| `.claude/skills/java-engineering-core/references/` | Shared discovery, principles and definition-of-done references |
| [docs/skill-catalog.md](docs/skill-catalog.md) | Task-to-skill activation guide |
| [docs/technology-map.md](docs/technology-map.md) | How Java, Spring, JPA, Hibernate, web and Android relate |
| [docs/official-sources.md](docs/official-sources.md) | Source register and version snapshot |
| [docs/validation-report.md](docs/validation-report.md) | What was checked, what was not, known gaps |
| `Requirement.md` | Requirements analysis of the original master prompt |
| `New Text Document.txt` | The original master prompt |

## Install

Skills follow the Claude Code format (`.claude/skills/<name>/SKILL.md`, frontmatter with `name` and `description`). Per the Claude Code docs they can live in three places:

1. **Into one project** - copy the skill folders you want into that repository:
   ```
   <project>/.claude/skills/<skill-name>/SKILL.md
   ```
   Copy `java-engineering-core` (including `references/`) plus the skills relevant to that project. Skills refer to each other by name; a missing skill is tolerated (the core skill says to continue and note the gap), but you get the best results with the set you need.
2. **For all your projects** - copy into `~/.claude/skills/` (Windows: `%USERPROFILE%\.claude\skills\`).
3. **Work inside this repository** - the skills are already in `.claude/skills/` here.

Suggested sets:

| Project type | Install |
|---|---|
| Any Java project | `java-engineering-core`, `java-core-engineering`, `java-testing-quality`, `java-maintenance-troubleshooting`, `java-code-review` |
| Spring Boot REST API | + `spring-boot-engineering`, `java-web-development`, `java-architecture-design` |
| Database-backed service | + `spring-data-jpa-engineering`, `hibernate-orm-engineering`, `java-database-engineering` |
| Secured / production service | + `spring-security-engineering`, `java-production-deployment`, `java-performance-resilience` |
| Event-driven / integrations | + `java-messaging-integration` |
| Android (Java) | `java-engineering-core`, `java-core-engineering`, `java-mobile-development`, `java-testing-quality` |
| AI-backed features | + `java-ai-integration` |
| Spec Kit projects | + `java-spec-driven-development` |

Keeping this repository as the single source and copying (or symlinking) into projects lets you improve standards once and reuse them everywhere. Nothing in the skills is specific to one application.

## Use

Skills load automatically when a task matches their `description`; you can also name one in your prompt (e.g. "use spring-security-engineering"). Typical flow:

1. `java-engineering-core` runs **Discover** (Java version, build tool, frameworks, test commands, conventions).
2. It **selects** only the relevant skills (e.g. REST endpoint -> web + Spring Boot + testing).
3. The agent **plans, implements, verifies, reports**, following those skills.
4. Reports state exactly which commands ran and their real results, and what could not be verified.

More examples in [docs/skill-catalog.md](docs/skill-catalog.md).

## Using with Spec Kit

Spec Kit (or an equivalent workflow) stays the authority for requirements, plan, tasks and acceptance criteria; these skills guide the Java implementation and verification.

1. Install and initialise Spec Kit for your agent per its current docs (`specify` CLI; see https://github.com/github/spec-kit).
2. Install this skill base into the project (above).
3. Write the project **constitution** so it references the Java standards (target Java/Boot versions, test and security gates, "follow `java-engineering-core`").
4. Per feature: specify -> plan -> tasks -> implement using `java-spec-driven-development` -> converge/analyze until clean.
5. Keep specs technology-neutral; put stack decisions in the plan; leave Java-specific *how* to these skills.

Spec Kit command names and file layout have changed between versions; the skill tells the agent to discover them from the repository and the installed version's docs.

## Design principles

- **One shared foundation** (`java-engineering-core`) for repository analysis, implementation quality, and verification.
- **Separate technology skills** - Spring Boot, Spring Security, JPA, Hibernate, web, and Android stay distinct so irrelevant instructions are not loaded.
- **Respect the repository** - existing Java/framework versions, conventions and architecture win over "latest".
- **Official sources first** - see the source register; version-sensitive claims carry a "checked on" date.
- **Honest verification** - never claim a check passed unless it was run and observed.
- **Security and reliability by default** - least privilege, server-side authorization, no secrets in code, bounded timeouts/retries/concurrency, tests for negative cases.

## Maintaining

- Re-check the "Version awareness" section of each skill when major releases ship (Spring Boot, Spring Security, Hibernate, Spring AI, JUnit, AGP, Spec Kit). The snapshot is in [docs/official-sources.md](docs/official-sources.md).
- Claude Code guidance: keep `SKILL.md` under 500 lines and descriptions well under the 1,536-character listing cap; put detail in `references/`.
- Re-run the structural checks described in the validation report after any edit.
- Add a framework-specific skill (rather than stretching an existing one) when a new stack is needed, for example a cross-platform mobile framework, Quarkus, or Micronaut.

## Limitations

See [docs/validation-report.md](docs/validation-report.md). In short: not yet exercised on real repositories; some version details and API names are flagged "verify for the repo's version"; scope is focused on Spring and native Android and does not include Quarkus, Micronaut, Jakarta EE servers, GraphQL, or Spring Cloud in depth.
