# Official Source Register

Authoritative sources used to build the skills, their intended use, and the version snapshot observed on **2026-10-11**. Versions change; each skill tells the agent to use the **repository's** versions and re-verify version-sensitive facts.

"Fetched" = the page was read during this build. "Link-checked" = the URL returned HTTP 200 (after redirects) in a scripted check of all URLs appearing in the skills; this proves reachability, not content accuracy.

## Java platform and build

| Source | URL | Intended use | Observed |
|---|---|---|---|
| Dev.java | https://dev.java/ | Language features and tutorials | link-checked |
| Oracle Java docs | https://docs.oracle.com/en/java/ | JDK tools (JFR, jcmd), GC guides | link-checked |
| OpenJDK / JEPs | https://openjdk.org/ | Feature status (preview vs final) | link-checked |
| Maven | https://maven.apache.org/guides/ | Build/dependency commands | link-checked |
| Gradle | https://docs.gradle.org/current/userguide/userguide.html | Build/dependency commands | link-checked |
| JUnit | https://docs.junit.org/current/user-guide/ (old `junit.org/junit5/...` redirects here) | Test framework | fetched: JUnit 6.1.3, Java 17+, Vintage deprecated |
| Testcontainers | https://testcontainers.com/ | Real dependencies in tests | fetched guide pinned 1.19.x examples (likely outdated) |

## Spring ecosystem

| Source | URL | Intended use | Observed |
|---|---|---|---|
| Spring Boot project | https://spring.io/projects/spring-boot | Versions and support | fetched: 4.1.1 current; 4.0.8, 3.5.16, 3.4.13, 3.3.13 stable; 4.2.0-M2 preview |
| Spring Boot reference | https://docs.spring.io/spring-boot/reference/ | Config, testing, Actuator, packaging | fetched (TOC) |
| Spring Boot Actuator endpoints | https://docs.spring.io/spring-boot/reference/actuator/endpoints.html | Exposure, probes, security | fetched (partial) |
| Spring Boot container images | https://docs.spring.io/spring-boot/reference/packaging/container-images/index.html | Image building | fetched: index only; detail pages not read |
| Spring Boot migration guides | https://github.com/spring-projects/spring-boot/wiki | Upgrades | fetched 3.0 and 4.0 guides (each partially read) |
| Spring Framework | https://spring.io/projects/spring-framework ; https://docs.spring.io/spring-framework/reference/web.html | Web, REST clients, errors, versioning | fetched: 7.0.9 / 6.2.19 |
| Spring Security | https://docs.spring.io/spring-security/reference/ | Security configuration | fetched: 7.1.1 / 7.0.7 / 6.5.11; migration overview read, Servlet-specific guide not read |
| Spring Data JPA | https://spring.io/projects/spring-data-jpa ; https://docs.spring.io/spring-data/jpa/reference/ | Repositories, projections, auditing, locking | fetched: 4.1.1 / 4.0.7 / 3.5.13 |
| Spring Data | https://spring.io/projects/spring-data | Umbrella | link-checked |
| Spring for Apache Kafka | https://spring.io/projects/spring-kafka | Kafka integration | fetched: 4.1.1; kafka-clients 4.2.x, Boot 4.1.x |
| Spring AMQP | https://spring.io/projects/spring-amqp | RabbitMQ integration | fetched: 4.1.1 |
| Spring AI | https://spring.io/projects/spring-ai ; https://docs.spring.io/spring-ai/reference/ | AI integration | fetched: 2.0.1 (also 1.1.8, 1.0.9); no Boot matrix on page |
| Spring Modulith | https://spring.io/projects/spring-modulith | Modular monolith | fetched: 2.1.1; Boot compatibility not stated |
| Spring GraphQL, Spring Cloud | https://spring.io/projects/spring-graphql ; https://spring.io/projects/spring-cloud | Listed in the prompt | **not researched**; no skill content depends on them |

## Persistence and databases

| Source | URL | Intended use | Observed |
|---|---|---|---|
| Jakarta Persistence | https://jakarta.ee/specifications/persistence/ | JPA spec | link-checked; 3.1 (Hibernate 6.6), 3.2 (Hibernate 7.x) per hibernate.org |
| Hibernate ORM | https://hibernate.org/orm/documentation/ ; https://hibernate.org/orm/releases/ | Runtime behaviour, migration | fetched releases: 7.4 latest stable; 7.2, 6.6 limited support; 8.0 beta |
| Flyway | https://documentation.red-gate.com/flyway | Migrations | link-checked |
| Liquibase | https://docs.liquibase.com/ | Migrations | link-checked |
| HikariCP | https://github.com/brettwooldridge/HikariCP | Pool sizing | link-checked |
| PostgreSQL / MySQL docs | https://www.postgresql.org/docs/ ; https://dev.mysql.com/doc/ | Engine-specific behaviour | PostgreSQL link-checked; MySQL returned 403 to the script (likely bot blocking) |

## Web

| Source | URL | Intended use | Observed |
|---|---|---|---|
| Thymeleaf | https://www.thymeleaf.org/documentation.html | SSR templates | link-checked |
| Vaadin | https://vaadin.com/docs | Server-side UI | link-checked |
| HTTP semantics / problem details | https://www.rfc-editor.org/rfc/rfc9110 ; https://www.rfc-editor.org/rfc/rfc9457 | Status codes, errors | link-checked |
| OpenAPI | https://spec.openapis.org/oas/latest.html | API contracts | link-checked |

## Mobile

| Source | URL | Intended use | Observed |
|---|---|---|---|
| Android Developers | https://developer.android.com/ | Platform docs | link-checked |
| Architecture | https://developer.android.com/topic/architecture | Layers, UDF, offline-first | fetched |
| Security checklist | https://developer.android.com/privacy-and-security/security-tips | Network, storage, IPC, WebView, tokens | fetched. Note: `.../privacy-and-security` (landing page in the prompt) returned 404 |
| Java/JDK for Android builds | https://developer.android.com/build/jdks | JDK and source levels | fetched: AGP 8.x requires JDK 17 |
| Kotlin-Java interop | https://developer.android.com/kotlin/interop | Nullability, `@Jvm*`, SAM, `Unit`, lint `Interoperability` | fetched. Does **not** cover coroutines/`suspend`/`Flow` from Java or varargs |
| Compose and Views interop | https://developer.android.com/develop/ui/compose/migrate/interoperability-apis | `ComposeView`, `AndroidView` | fetched: overview only; composition strategy, `observeAsState`/`collectAsStateWithLifecycle`, theming from general knowledge |
| Jetpack | https://developer.android.com/jetpack | Library overview; Java-friendly artefact variants | **not fetched**; artefact names from general knowledge |
| Kotlin in Spring | https://docs.spring.io/spring-framework/reference/languages/kotlin.html | `kotlin-spring`/`kotlin-jpa` plugins, null-safety, coroutines | fetched: intro and section list only; details from general knowledge |
| OWASP MASVS/MASTG | https://mas.owasp.org/ | Mobile security verification | link-checked |

## Operations and security

| Source | URL | Intended use | Observed |
|---|---|---|---|
| Docker | https://docs.docker.com/ | Images, best practices | link-checked |
| OpenTelemetry | https://opentelemetry.io/docs/ | Tracing/metrics | link-checked |
| Micrometer | https://micrometer.io/docs | Metrics | link-checked |
| OWASP | https://owasp.org/ | Top 10, cheat sheets | link-checked; Top 10 page redirects to top10.owasp.org (edition not read) |
| OWASP LLM Top 10 | https://genai.owasp.org/llm-top-10/ | AI threat model | fetched: 2025 edition, 10 risks |

## Specification workflow and agent format

| Source | URL | Intended use | Observed |
|---|---|---|---|
| Spec Kit | https://github.com/github/spec-kit ; https://github.github.io/spec-kit/ | Spec-driven workflow | fetched: Specify -> Plan -> Tasks -> Implement -> Converge; hyphenated `/speckit-*` commands; artifact paths and Claude integration details **not confirmed** |
| Claude Code skills | https://code.claude.com/docs/en/skills (redirect from docs.claude.com) | Skill format | fetched: only `name`/`description` needed; keep SKILL.md under 500 lines; description cap 1,536 chars; project path `.claude/skills/` |
| GitHub Copilot agent skills | https://docs.github.com/en/copilot/concepts/agents/about-agent-skills ; https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-skills | Copilot skill locations, surfaces, frontmatter | fetched 2026-10-11: reads `.github/skills`, `.claude/skills`, `.agents/skills`; frontmatter fields not fully documented on the concept page |
| GitHub Copilot custom instructions | https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions | `copilot-instructions.md`, `*.instructions.md` with `applyTo`, `AGENTS.md` | fetched 2026-10-11 |
| Agent Skills specification | https://agentskills.io/specification | Portable SKILL.md rules (name <= 64, description <= 1024) | fetched 2026-10-11 |
| Claude Code plugins | https://code.claude.com/docs/en/plugins ; /plugins/create ; /plugins/manifest-reference ; /plugins/create-marketplace | Plugin and marketplace formats, `skills` key, hooks | fetched 2026-10-15 |
| Claude Code hooks | https://code.claude.com/docs/en/hooks | SessionStart `additionalContext`, plugin `hooks/hooks.json`, 10,000-character limit | fetched 2026-10-15 (page partly read) |
| Manage plugins for your organization | https://code.claude.com/docs/en/plugins/org ; /managed-settings | `extraKnownMarketplaces`, `enabledPlugins`, `strictKnownMarketplaces`, file locations | fetched 2026-10-15 |

## Maintenance procedure

1. Before relying on a version-specific statement, re-read the relevant page above.
2. After a major release (Boot, Security, Hibernate, Spring AI, JUnit, AGP, Spec Kit), update the "Version awareness" section of the affected skills and the snapshot here.
3. Prefer official migration guides over blog posts. Never copy documentation pages into skills.
