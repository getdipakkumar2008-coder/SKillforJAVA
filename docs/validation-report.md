# Validation Report

Date: 2026-10-11. Scope: the 18 skills, 3 reference files, README and docs. (The first 17 skills were checked together; `java-code-review` was added and checked afterwards, see section 4.)

**Summary:** structural checks passed (scripted). Technical and scenario review were **manual**, performed by the author of the content (the same AI session), which limits independence. **No skill has been exercised on a real repository**, and no build, test or deployment command described in the skills was executed here. Treat this as a draft ready for pilot use, not a certified library.

## 1. Structural checks (automated by shell script)

| Check | Result |
|---|---|
| Each `SKILL.md` has frontmatter starting on line 1 with `name` and `description` | Pass (17/17) |
| `name` equals the directory name; names unique | Pass |
| Description length (max observed 669 chars; Claude Code listing cap 1,536) | Pass |
| `SKILL.md` length (max 120 lines; Claude Code guidance < 500) | Pass |
| Files referenced from `java-engineering-core` exist (3 references) | Pass |
| Cross-references to other skills point to existing skill directories | Pass (the only unmatched token was `spring-boot-properties-migrator`, a Maven artifact name, not a skill) |
| Required sections present (Purpose, Activation conditions, Definition of done, Related skills, Official references) | Pass after fix: `java-engineering-core` lacked a Definition of done section; added |
| URLs appearing in skills (81 unique) reachable | 80 returned HTTP 200 after redirects; 1 returned 403 (`https://dev.mysql.com/doc/`, likely bot blocking). Reachability only, not content correctness |
| Frontmatter format vs Claude Code docs | Conforms to the documented minimum (`name`, `description`); docs fetched 2026-10-11 (the last ~7% of the page was not read) |

Not automated: duplicate or contradictory instruction detection (manual read only), YAML parsing with a real parser (checked structurally by line, not parsed).

## 2. Technical review (manual)

Version-sensitive statements were checked against official pages where fetchable (see [official-sources.md](official-sources.md)). Known limits:

| Area | Status |
|---|---|
| Spring Boot 4 / 3 baselines and breaking changes | Taken from the official migration guides, each read only in part (first ~100k characters) |
| Spring Security 7 | Migration overview read; Servlet-specific breaking changes **not read**; skills defer to the guide |
| Hibernate/Spring Data pairing per Boot version | **Not confirmed**; skills tell the agent to read the repo's resolved versions |
| Hibernate logger names, batching and statistics properties | From author knowledge; flagged "verify for the version" |
| `@ServiceConnection`, `spring.threads.virtual.enabled`, Spring Framework 7 retry/concurrency annotations | Not confirmed in fetched docs; flagged in the skills |
| Java feature-by-release table (`java-core-engineering`) | From author knowledge; not checked against JEPs |
| Spring Kafka / AMQP class and property names | From author knowledge; flagged |
| Container image commands (layered jars, build-image) | Detail pages not read; skills point to the repo's version of the docs |
| Spec Kit artifact paths, clarify/analyze/checklist commands, Claude integration | Not confirmed; skill discovers them from the repository |
| Android Room, WorkManager, Navigation, Hilt, Play `targetSdk` deadlines, Tink/Keystore library choice | From author knowledge; not fetched |
| Spring AI class/starter names across 1.x vs 2.x; Boot compatibility | Not confirmed; no matrix on the project page |
| OpenTelemetry, Resilience4j, Caffeine, ArchUnit, Gatling/k6, scanner names | Mentioned from knowledge; links only reachability-checked |

Security instructions were reviewed for consistency (deny by default, server-side authorization, no secrets, no disabling controls to pass tests, bounded timeouts/retries) and these themes appear consistently across the web, security, mobile, messaging, AI and testing skills. No independent security review was performed.

Boundary checks: Spring Boot, Spring Data JPA, Hibernate, Spring Security and Jakarta Persistence are distinguished in the JPA, Hibernate, Boot and security skills and in the technology map; Android guidance explicitly excludes Spring/backend patterns and Kotlin conversion; AI guidance keeps deterministic rules and authorization outside the model.

## 3. Scenario walkthroughs (desk review only)

For each scenario: skills the core skill would select, and whether a practical implementation and verification workflow exists in them. "Verified" here means the instructions exist and are coherent; it does **not** mean the workflow was run.

| # | Scenario | Skills | Verification workflow present? | Gaps / notes |
|---|---|---|---|---|
| 1 | Java utility library | core, java-core-engineering, testing | Yes: release gating, API compatibility, tests, build commands | Library publishing (Maven Central, versioning, module-info) only lightly covered |
| 2 | Spring Boot REST API | web, spring-boot, testing | Yes: contract, validation, `ProblemDetail`, slices, MockMvc | No project-scaffolding guide (assumes an existing repo) |
| 3 | JPA entities and relationships | boot, spring-data-jpa, hibernate, database, testing | Yes: migrations, lazy defaults, DataJpaTest with real DB, statement counts | Depends on container runtime for real-DB tests |
| 4 | Diagnose N+1 | hibernate, database, performance, testing | Yes: measure, fix order, regression assertion | Logger/property names need version check |
| 5 | OAuth2 resource-server JWT | security, web, boot, testing | Yes: access matrix, validation, 401/403 test matrix | Exact property/DSL names to verify for the repo's version |
| 6 | Native Android feature in Java | mobile, java-core, testing | Yes: architecture, threading, tests, release | Instrumentation tests need emulator; Compose-heavy repos need extra guidance |
| 7 | Android + Spring Boot backend | mobile + web + security + boot | Partially: both sides covered separately, contract points to each other | No single combined end-to-end workflow or contract-testing recipe across the two |
| 8 | Async messaging, retry, idempotency | messaging, boot, database, testing | Yes: outbox/inbox, DLQ, duplicate tests | Class and property names to verify; no JMS/cloud-broker specifics |
| 9 | Containerize and deploy Spring Boot service | deployment, boot, security | Partially: strategy, probes, shutdown, scans present | Exact image-build commands deferred to docs; no platform-specific manifests |
| 10 | Build/startup failure | maintenance + framework skill | Yes: symptom toolbox, reproduce-first workflow | Generic; real failures will expose missing cases |
| 11 | Upgrade Spring Boot | maintenance, boot, security, hibernate, testing | Yes: stepwise process, guides cited | Security 7 Servlet breaking changes and Boot guide tails unread |
| 12 | Feature from a Spec Kit spec | spec-driven + task skills | Yes: 11-step flow, traceability table | Spec Kit paths/commands unverified; never run against a real Spec Kit project |
| 13 | AI-assisted feature | ai-integration, security, web, testing | Yes: threat model, evaluation, approvals | Spring AI API names unverified; live-provider tests excluded |

## 4. Known gaps against the original requirements

- **Layer 4 lifecycle items:** repository discovery is in the core references; architecture decisions, troubleshooting and (added after the first validation pass) `java-code-review` have skills; quality gates and release readiness are covered by `java-code-review`, the core definition of done, and the testing and deployment skills rather than a dedicated skill. `java-code-review` passed the same structural checks (frontmatter, 129 lines, 528-char description, cross-references, required sections) but was **not** part of the 13-scenario desk review and has not been tried on a real diff.
- **Prompt-listed technologies not covered in depth:** Spring GraphQL, Spring Cloud, Spring Modulith (architecture skill only mentions it), Thymeleaf and Vaadin (named, not detailed), JMS/cloud messaging specifics, Quarkus/Micronaut/Jakarta EE servers (out of scope).
- **Kotlin and Jetpack (addressed 2026-10-11, second pass):** discovery now detects the Java/Kotlin mix and UI toolkit; `java-mobile-development` gained "Java/Kotlin interoperability" and "Jetpack and Compose" sections; Kotlin notes were added to `spring-boot-engineering`, `spring-data-jpa-engineering`, `java-core-engineering`, `java-testing-quality` and `java-code-review`. Basis: the Android Kotlin-interop page (fetched), the Compose interop overview (names APIs only), and the Spring Kotlin page (intro only). **Unverified:** coroutines/`suspend`/`Flow` from Java, Jetpack Java-friendly artefact names, Compose composition strategy and state-observation APIs, and the `kotlin-spring`/`kotlin-jpa` plugin details - flagged "verify" in the skills. Kotlin-only repositories remain out of scope, and there is no dedicated Kotlin or Compose authoring skill (Compose/Kotlin code idioms are only touched on, not taught).
- **Template alignment (done 2026-10-11, third pass):** all 18 skills now carry the same 13 mandatory headings with exact names (see [skill-template.md](skill-template.md)); a repeatable script `scripts/validate-skills.sh` enforces them and reports OK for all 18. Changes: renamed inconsistent headings (e.g. "Required context" -> "Required context and inputs", "Security requirements" -> "Security and reliability requirements", "Troubleshooting workflow" -> "Workflow", "Review procedure" -> "Workflow"), and added missing sections to `java-code-review`, `java-core-engineering`, `java-engineering-core` (short pointer sections to its references), `java-maintenance-troubleshooting`, `java-performance-resilience`, `java-spec-driven-development` and `java-testing-quality`. The template is the one from the original master prompt (section 7); the second template mentioned in a later request was cut off and never received, so conformance to it is **unverified**. The script checks structure only: it cannot tell whether a section is good, only that it exists.
- **GitHub Copilot adapter (added 2026-10-11, fourth pass):** the skills already conform to the Agent Skills spec that Copilot reads (names, 1024-character description cap, under 500 lines); `scripts/validate-skills.sh` now enforces the 1024 cap and naming rules and checks that the Copilot instruction templates have `applyTo` and that `copilot-instructions.md` names every skill (all pass). Added `adapters/copilot/` (1 repository-wide file, 6 path-specific files), `scripts/install-skills.sh` (tested on scratch directories: dry run, fresh install, re-run without overwrite, subset, claude-only, and validation of the installed copy) and `docs/copilot-adapter.md`. **Not verified:** any live Copilot session; whether Copilot follows `references/` links inside skills; activation quality of the descriptions in Copilot or Claude Code (no trigger tests); instruction-length limits for code review; whether installing the same skills into both `.claude/skills` and `.github/skills` causes conflicts (installer avoids it). No PowerShell installer.
- **Frontend frameworks:** intentionally only "follow the repo's conventions"; no Angular/React skill.
- **No `docs`-level installation automation:** install is manual copy, per the README.
- **The Requirement.md assumption "target agent is Claude Code"** was confirmed only as far as the skill format; other agents would need a format conversion.

## 5. Limitations and honesty notes

- All checks were run by the same session that wrote the content; no peer review.
- Link checks prove reachability only.
- Several official pages were partially read or only navigation pages; claims from them were limited accordingly.
- No code was compiled, no Spring/Android project was built, no container was run, no Spec Kit workflow was executed.
- A stray temporary URL list was written to the scratchpad during link checking; it is not part of the deliverable.

## 6. Recommended next steps

1. Pilot on 2-3 real repositories (a Spring Boot + JPA service, an Android Java app, a Spec Kit project) and record where agents mis-select skills or follow bad advice.
2. Resolve the "verify" items in section 2 against the pilot repos' actual versions and update the skills.
3. Read the unread tails of the migration guides and the Spring Security Servlet migration page.
4. Decide whether to add a code-review/release-readiness skill and any missing frameworks (GraphQL, Cloud, Quarkus/Micronaut).
5. Add an independent review (human or separate agent) of the security guidance.
6. Re-run the structural checks after each edit.
