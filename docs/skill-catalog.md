# Skill Catalog and Activation Guide

All skills live in `.claude/skills/<name>/SKILL.md`. Always start with `java-engineering-core`; it selects the rest.

## Catalog

| Layer | Skill | Use when | Key boundaries |
|---|---|---|---|
| 1 Foundation | `java-engineering-core` | Any Java task: discover repo, choose skills, plan, implement, verify, report | Process only; no framework detail |
| 1 Foundation | `java-core-engineering` | Plain Java code: language features by release, collections, streams, concurrency, virtual threads, `java.time`, I/O, JVM, API design | No framework specifics |
| 2 Domain | `java-architecture-design` | Structure and boundaries, layered/hexagonal, modular monolith vs services, ADRs | Prefers the existing structure and simplest design |
| 2 Domain | `java-web-development` | Controllers, REST contracts, validation, errors, pagination, OpenAPI, uploads, CORS/CSRF, SSR, frontend integration | Security design lives in the security skill |
| 2 Domain | `java-database-engineering` | Schema, indexes, SQL, isolation, pools, migrations, test DB strategy | Engine-specific advice is labelled |
| 2 Domain | `java-testing-quality` | Writing/fixing tests, slices, Testcontainers, static analysis, coverage | Uses the repo's JUnit generation |
| 2 Domain | `java-messaging-integration` | HTTP clients, Kafka/RabbitMQ/JMS, idempotency, retries, DLQ, outbox | No new broker without a requirement |
| 2 Domain | `java-performance-resilience` | Profiling, GC, pools, timeouts, circuit breakers, caching, load tests | Evidence before optimisation |
| 2 Domain | `java-production-deployment` | Logging/metrics/tracing, Actuator probes, Docker, CI/CD, secrets, rollout/rollback | Fits the project's actual platform |
| 2 Domain | `java-mobile-development` | Native Android in Java | Not Spring; not cross-platform frameworks |
| 2 Domain | `java-ai-integration` | LLM calls, RAG, tools, evaluation, cost and safety | Model is untrusted; rules stay deterministic |
| 3 Framework | `spring-boot-engineering` | Boot config, beans, auto-configuration, Boot tests, Actuator, packaging | Not persistence or security design |
| 3 Framework | `spring-data-jpa-engineering` | Entities, repositories, queries, transactions, migrations, auditing | Pair with Hibernate skill for runtime behaviour |
| 3 Framework | `hibernate-orm-engineering` | N+1, lazy loading, flush, cascades, caching, batching, locking | Diagnosis with SQL/statistics evidence |
| 3 Framework | `spring-security-engineering` | AuthN/AuthZ, OAuth2/OIDC, JWT, method security, CORS/CSRF, secrets | Deny by default; never weaken to pass tests |
| 4 Lifecycle | `java-maintenance-troubleshooting` | Failures, dependency conflicts, startup errors, upgrades | Small verified fixes; official migration guides |
| 4 Lifecycle | `java-code-review` | Reviewing a diff/PR/branch, pre-merge or release readiness, self-review | Reports ranked, evidence-backed findings; does not edit code unless asked |
| 4 Lifecycle | `java-spec-driven-development` | Implementing from Spec Kit or similar artifacts | Spec workflow stays the authority |

## Task-to-skill map

| Task | Activate (plus `java-engineering-core`) |
|---|---|
| Java utility library | `java-core-engineering`, `java-testing-quality` |
| Spring Boot REST endpoint | `java-web-development`, `spring-boot-engineering`, `java-testing-quality` |
| Add entities / relationships | `spring-boot-engineering`, `spring-data-jpa-engineering`, `hibernate-orm-engineering`, `java-database-engineering`, `java-testing-quality` |
| Slow query / N+1 | `hibernate-orm-engineering`, `java-database-engineering`, `java-performance-resilience`, `java-testing-quality` |
| Secure an API (JWT resource server) | `spring-security-engineering`, `java-web-development`, `spring-boot-engineering`, `java-testing-quality` |
| Android feature | `java-mobile-development`, `java-core-engineering`, `java-testing-quality` |
| Android + Spring backend | `java-mobile-development` (client) + `java-web-development`, `spring-security-engineering`, `spring-boot-engineering` (server) |
| Async messaging / events | `java-messaging-integration`, `spring-boot-engineering`, `java-database-engineering` (outbox), `java-testing-quality` |
| Containerize / deploy | `java-production-deployment`, `spring-boot-engineering`, `spring-security-engineering` |
| Build or startup failure | `java-maintenance-troubleshooting` + the relevant framework skill |
| Upgrade Spring Boot / Hibernate | `java-maintenance-troubleshooting`, `spring-boot-engineering`, `hibernate-orm-engineering`, `spring-security-engineering`, `java-testing-quality` |
| Restructure / new module | `java-architecture-design`, `java-core-engineering`, `java-testing-quality` |
| Latency / memory / stability | `java-performance-resilience`, `java-production-deployment`, DB or Hibernate skills as evidence points |
| Feature from a Spec Kit spec | `java-spec-driven-development` + skills per task type |
| AI-assisted feature | `java-ai-integration`, `spring-security-engineering`, `java-web-development`, `java-testing-quality` |
| Schema / migration change | `java-database-engineering`, `spring-data-jpa-engineering`, `java-production-deployment` (rollout) |
| Code review / PR review / release readiness | `java-code-review` + the lens skills for what the diff touches (security, JPA/Hibernate, web, messaging, Android, testing, deployment) |

## Activation rules

1. Activate only what the task needs; do not load the whole library.
2. Keep Spring Boot, Spring Security, JPA, Hibernate, web and Android guidance distinct.
3. When skills conflict: security and data integrity first, then repository conventions, then style.
4. If a referenced skill is not installed, continue with core principles and official docs, and note the gap.
5. If the repo uses another stack (Quarkus, Micronaut, a cross-platform mobile framework), say so and use only the general skills (core, testing, database, architecture, maintenance); consider adding a framework-specific skill.
