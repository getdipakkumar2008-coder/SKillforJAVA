# Java engineering skills

This repository uses a Java engineering skill base (`.claude/skills/`). Skills load on demand from their descriptions, but simple-looking tasks often skip them, so follow this rule:

**For any task that involves Java (or Kotlin on the JVM/Android) code, build files, tests, configuration or review, invoke the `java-engineering-core` skill first.** It discovers the repository (versions, build tool, frameworks, conventions, test commands), selects only the specialised skills the task needs, and sets the plan, implement, verify and report workflow. Then invoke the specialised skills it selects. Skip this only for trivial questions that need no code or repository facts.

## Skills
| Task | Skill |
|---|---|
| Plain Java code: release-level language features, concurrency/async, `java.time`/money, API compatibility | `java-core-engineering` |
| Structure, boundaries, ADRs | `java-architecture-design` |
| REST/web layer, validation, errors, OpenAPI | `java-web-development` |
| Spring Boot config, tests, Actuator, packaging | `spring-boot-engineering` |
| Entities, repositories, queries, migrations | `spring-data-jpa-engineering` |
| N+1, lazy loading, flush, caching, locking | `hibernate-orm-engineering` |
| AuthN/AuthZ, OAuth2/JWT, CORS/CSRF, secrets | `spring-security-engineering` |
| Schema, indexes, isolation, pools | `java-database-engineering` |
| Tests and quality gates | `java-testing-quality` |
| HTTP clients, Kafka/RabbitMQ, idempotency, retries | `java-messaging-integration` |
| Profiling, timeouts, circuit breakers, caching | `java-performance-resilience` |
| Docker, CI/CD, observability, rollout | `java-production-deployment` |
| Android (Java, Kotlin interop, Jetpack/Compose) | `java-mobile-development` |
| LLM/RAG/tool-calling features | `java-ai-integration` |
| Build/startup failures, upgrades | `java-maintenance-troubleshooting` |
| Reviewing a diff or PR | `java-code-review` |
| Spec Kit / spec-driven work | `java-spec-driven-development` |

## Non-negotiables
- Respect the repository's Java, Kotlin and framework versions; do not upgrade, convert languages, or add dependencies as a side effect.
- Never claim a build, test or check passed unless you ran it and saw the result; say what was not run.
- Never delete, skip or weaken a failing test, and never disable a security control, to get a green build.
- Enforce authorization on the server; no secrets in code, config, tests or logs; validate untrusted input; bound timeouts, retries and concurrency.
- Keep Spring Boot, Spring Security, JPA, Hibernate, web and Android guidance separate.
- Spec Kit (if used) owns requirements, plan and tasks; implement and verify them and record deviations instead of editing the spec to fit the code.
