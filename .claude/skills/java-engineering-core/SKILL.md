---
name: java-engineering-core
description: Shared foundation workflow for any Java task in an existing repository (Spring Boot, web/REST, JPA/Hibernate, Android, libraries, multi-module builds). Use at the start of any Java implementation, bug fix, refactor, upgrade or review to discover the repository, choose which other Java skills apply, plan, implement, verify and report honestly. Not for non-Java work.
---

# Java Engineering Core

## Purpose
Common operating procedure for every Java task. It defines how to discover a repository, pick only the relevant specialised skills, implement within the project's conventions, verify with real command output, and report truthfully. Specialised skills (Spring Boot, JPA, security, Android, ...) build on this one.

## Activation conditions
Activate when the task involves Java source, a Java build (Maven/Gradle), a Java framework, or an Android Java project. Activate first; it then selects the others. If a Spec Kit workflow is present (`.specify/`, `specs/`, constitution), `java-spec-driven-development` governs requirements and planning, and this skill governs execution.

## Required context and inputs
- The requested behaviour and any acceptance criteria.
- Project instruction files (`CLAUDE.md`, `AGENTS.md`, `README`, `CONTRIBUTING`, constitution/specs if present).
- Permission to run builds and tests. If unavailable, say so in the report.

## Workflow

### Phase 1: Discover
Follow [references/repository-discovery.md](references/repository-discovery.md). Output a short "repository profile" (Java version, build tool, app type, frameworks and versions, test and quality commands, conventions). Do not guess what can be read from files.

### Phase 2: Select skills
Activate only what the task needs. Examples:

| Task | Skills |
|---|---|
| Plain library or utility | `java-core-engineering`, `java-testing-quality` |
| Spring REST endpoint | `java-web-development`, `spring-boot-engineering`, `java-testing-quality` |
| DB-backed feature | `spring-boot-engineering`, `spring-data-jpa-engineering`, `hibernate-orm-engineering`, `java-database-engineering`, `java-testing-quality` |
| Secured API | `java-web-development`, `spring-boot-engineering`, `spring-security-engineering`, `java-testing-quality` |
| Android feature | `java-mobile-development`, `java-testing-quality` (plus API integration) |
| Deployment | `spring-boot-engineering`, `java-production-deployment`, `spring-security-engineering` |
| AI-backed feature | applicable backend skills, `java-ai-integration`, `spring-security-engineering` |
| Build/startup failure, upgrade | `java-maintenance-troubleshooting` |

If a named skill is not installed, continue with this skill's principles and the official documentation, and mention the gap in the report. Keep Spring Boot, Spring Security, JPA, Hibernate, web and Android guidance separate. Never apply backend patterns to Android UI code.

### Phase 3: Plan
1. Restate the behaviour and acceptance criteria in your own words.
2. Choose the smallest change that satisfies them, reusing existing code and patterns.
3. Check security, data integrity, compatibility and failure handling.
4. List the tests and checks you will run.
5. Ask a focused question only if a missing decision materially affects correctness, security or architecture. Otherwise state assumptions and proceed.

For non-trivial work, write the plan (a few lines) before editing.

### Phase 4: Implement
- Follow the repository's conventions (naming, package layout, formatting, error handling). Read neighbouring code first.
- Use only APIs available in the project's Java and framework versions. Verify signatures, annotations and properties against official docs when unsure. Do not use preview features unless the project already does.
- Keep the diff scoped. No drive-by refactors, no new dependencies or architecture without a stated need.
- Keep business logic separate from framework and infrastructure code.
- Preserve existing behaviour unless asked to change it.
- Add validation, error handling, security controls and logging where the change warrants them, in proportion to risk.
- Details: [references/engineering-principles.md](references/engineering-principles.md).

### Phase 5: Verify
1. Run the narrowest relevant test first, then the module's tests, then the wider build when the change touches shared code.
2. Run configured formatting, static analysis and dependency or security checks if the project has them.
3. Review your own diff for unintended changes, leftover debug code and secrets.
4. Check each acceptance criterion explicitly.
5. If a check fails, fix the cause. Never delete, skip or weaken a failing test, or disable a security control, to get green.

Never claim a check passed unless you ran it and saw the result. If you could not run something, say what and why.

### Phase 6: Report
Summarise concisely:
- What changed (files, behaviour).
- Key decisions and assumptions.
- Exact commands run and their real results.
- Acceptance criteria status.
- Known risks, unverified items and remaining work.

Use the checklist in [references/definition-of-done.md](references/definition-of-done.md).

## Decision rules
- Existing convention beats personal preference. Existing Java and framework versions beat "latest".
- Prefer the simplest design that meets the requirement. Add abstraction only for a present need.
- When two skills conflict, security and data integrity win, then repository conventions, then style.
- Evidence before optimisation: measure first.
- Unfamiliar or version-sensitive API: check official docs (see the source list in `docs/official-sources.md` if present) rather than recalling from memory.

## Security and reliability baseline
Least privilege; validate untrusted input; no hardcoded secrets or credentials in code, tests or logs; enforce authorisation on the server; bounded timeouts and retries for remote calls; consider duplicate requests; protect data consistency. Scale effort to the risk and size of the task.

## Common anti-patterns
- Editing before reading the repository's conventions and build setup.
- Loading every skill "just in case".
- Upgrading Java, Spring or dependencies as a side effect of an unrelated task.
- Reporting "tests pass" without running them.
- Mocking away the very behaviour (queries, transactions, security) the change depends on.
- Broad speculative refactoring while fixing a bug.
- Converting Java to Kotlin, or Maven to Gradle, without authorisation.

## Definition of done
Every applicable item in [references/definition-of-done.md](references/definition-of-done.md) is true and evidenced: acceptance criteria met, tests added and run, build and quality checks run with observed results, no weakened tests or security controls, scope respected, and the report lists commands, results, risks and anything not verified.

## Related skills
`java-core-engineering`, `java-architecture-design`, `java-testing-quality`, `java-maintenance-troubleshooting`, `java-spec-driven-development`, and the framework skills listed in Phase 2.

## Official references
Java: https://dev.java/ and https://docs.oracle.com/en/java/ · Maven: https://maven.apache.org/guides/ · Gradle: https://docs.gradle.org/current/userguide/userguide.html · JUnit: https://junit.org/junit5/docs/current/user-guide/ · OWASP: https://owasp.org/
