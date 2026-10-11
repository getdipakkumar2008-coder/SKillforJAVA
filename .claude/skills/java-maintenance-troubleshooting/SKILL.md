---
name: java-maintenance-troubleshooting
description: Diagnose and fix Java build failures, dependency conflicts, application startup and bean-wiring errors, security configuration failures, SQL/transaction/network/messaging failures and Android build problems, and plan or execute upgrades (Java versions, Spring Boot 2->3->4, Hibernate/Jakarta Persistence, Spring Security). Use when something is broken, a build or test fails, or a version upgrade is requested. Emphasises reproducing first, small verifiable fixes, official migration guides and regression tests.
---

# Java Maintenance and Troubleshooting

## Purpose
Find the real cause with evidence, make the smallest fix that addresses it, prove it, and prevent recurrence. Upgrades are planned, incremental and verified, not big-bang rewrites.

## Activation conditions
Build/compile/test failure; dependency or classpath error; application will not start; wrong runtime behaviour; production incident analysis from logs; upgrade of Java, Spring Boot, Hibernate, Spring Security or other libraries; Android Gradle/runtime problems. Run `java-engineering-core` discovery first (exact versions matter).

## Version awareness (checked 2026-10-11)
- Spring Boot reference lists stable 4.1.1, 4.0.8, 3.5.16, 3.4.13, 3.3.13. Official migration guides: https://github.com/spring-projects/spring-boot/wiki (e.g. Spring-Boot-3.0-Migration-Guide, Spring-Boot-4.0-Migration-Guide).
- **Boot 2.7 -> 3.0 (official guide):** upgrade to latest 2.7.x first; Java 17 minimum; Spring Framework 6; `javax.*` -> `jakarta.*` (Jakarta EE 10); add `spring-boot-properties-migrator` temporarily and remove it afterwards; Hibernate 6.1 (group `org.hibernate.orm`); Spring Security 6; trailing-slash matching off by default; Actuator `httptrace` -> `httpexchanges`; MySQL driver coordinates changed.
- **Boot 3.x -> 4.0 (official guide):** Java 17+, Jakarta EE 11 / Servlet 6.1, Spring Framework 7; starters modularised (`spring-boot-starter-web` deprecated for `-webmvc`; Flyway/Liquibase need their Boot starter); Jackson 3 by default (`tools.jackson`); `@MockBean` -> `@MockitoBean`; `@SpringBootTest` no longer auto-provides MockMvc; Undertow removed. (The guide text was read only in part - read the full guide for the actual upgrade.)
- **Spring Security 7:** upgrade to the latest Boot 4.0 patch and Security 7 patch; use 6.5.x preparation steps first; Jackson 3 serialization changes. See `spring-security-engineering`.
- Hibernate: 7.4 latest stable, 7.2/6.6 limited support (hibernate.org/orm/releases). Read that version's Migration Guide.
- Always target the **repo's** versions when diagnosing; never recommend an upgrade as the first fix unless the evidence points to a bug fixed there.

## Required context and inputs
Exact error text and full stack trace, command run, environment (JDK vendor/version, OS, build tool and wrapper version), recent changes (`git log`/diff if available), versions of relevant libraries, whether it fails locally/CI/prod.

## Repository inspection
Gather the facts a diagnosis depends on: exact versions (JDK, build tool and wrapper, Boot/Spring/Hibernate/Security, Android Gradle Plugin, Kotlin), the resolved dependency tree, profiles and config in effect, recent commits and dependency changes (`git log`, lock/catalog diffs), CI logs versus local behaviour, existing test failures at baseline, and whether the failure is deterministic.

## Workflow
1. **Reproduce.** Run the failing command; capture the first error (not the last cascade). Find the minimal repro (single test, single module, `--offline` off/on).
2. **Read the evidence.** Root cause is usually in the *first* `Caused by:` and in `FailureAnalyzer` output; read warnings above it.
3. **Form hypotheses** ranked by evidence; test one at a time with the cheapest experiment (dependency tree, debug flag, minimal test).
4. **Fix the cause**, minimally and in the correct layer. No unrelated cleanups.
5. **Prove it:** failing command now passes; add a regression test where feasible; run the wider build.
6. **Report:** cause, evidence, fix, verification, residual risk.

If the problem cannot be reproduced locally (missing infrastructure, prod-only), say so, analyse logs/config, state hypotheses with confidence, and propose the narrowest verification.

## Diagnostic toolbox by symptom
**Build and dependencies**
- Maven: `./mvnw -e -X ...`, `./mvnw dependency:tree -Dverbose`, `dependency:analyze`, `help:effective-pom`, `enforcer`. Gradle: `./gradlew dependencies --configuration runtimeClasspath`, `dependencyInsight --dependency <x>`, `--stacktrace --info`, `--refresh-dependencies` (only when caching is suspected).
- Typical causes: wrong Java version/toolchain; BOM override pinning an incompatible version; duplicate classes from two artifacts (`NoSuchMethodError`, `ClassNotFoundException`, `NoClassDefFoundError`); `javax` vs `jakarta` mix; annotation processor order (Lombok + MapStruct); stale local repository/wrapper; offline/proxy/credential issues for repositories.
- Fix by aligning versions through the BOM/`dependencyManagement`, excluding the conflicting transitive, or removing the explicit override - not by adding more overrides.

**Application startup (Spring)**
- Read the `APPLICATION FAILED TO START` description/action first. Use `--debug` (conditions report) or `/actuator/conditions` when running.
- `NoSuchBeanDefinitionException` / `UnsatisfiedDependencyException`: component scan root, missing starter, `@Profile`/`@Conditional`, qualifier needed, bean in test slice not imported.
- `NoUniqueBeanDefinitionException`: use `@Primary`/`@Qualifier` or reduce duplicates.
- Circular dependency: redesign the dependency direction, do not turn on circular-reference allowance.
- `ConfigurationPropertiesBindException`: property name/type/validation; check relaxed binding, profile, env var names.
- Port in use, DataSource/URL errors, Flyway checksum or out-of-order errors (never edit applied migrations or disable validation to bypass; repair deliberately with team agreement), `ddl-auto=validate` schema mismatch.
- Class version errors (`UnsupportedClassVersionError`): runtime JDK older than compile target.

**Security**
- 401 vs 403 vs redirect-to-login; CSRF 403 on POST; CORS preflight failing before auth; wrong `SecurityFilterChain` matched; token validation failures (issuer, audience, clock skew, JWK fetch). Turn on `org.springframework.security` DEBUG temporarily. Fix configuration - never disable the control. See `spring-security-engineering`.

**Data, transactions, network, messaging**
- SQL: capture the statement and parameters (temporary logging), run `EXPLAIN`, check constraints/migrations. Lock waits/deadlocks: DB lock views and lock ordering; connection exhaustion: Hikari logs, long transactions, leaks. See `java-database-engineering`, `hibernate-orm-engineering`.
- `LazyInitializationException`, N+1, unexpected updates: `hibernate-orm-engineering`.
- Network: timeouts vs refused vs TLS (`-Djavax.net.debug=ssl:handshake` temporarily), DNS, proxy, certificate chain; check timeouts and retries; correlation ids across services.
- Messaging: duplicate/lost/poison messages, consumer lag, rebalances, deserialization errors; check idempotency, DLQ and retry config. See `java-messaging-integration`.

**Runtime/performance**
- `jcmd <pid> Thread.print`, `jstack` for hangs/deadlocks; heap dump + analyser or JFR for memory/CPU; GC logs. Evidence first (`java-performance-resilience`).

**Android**
- Gradle sync/build: AGP vs Gradle vs JDK compatibility, `compileSdk/minSdk/targetSdk`, duplicate classes, R8/ProGuard missing rules, manifest merger conflicts, `java.lang.OutOfMemoryError` in dexing. Runtime: `adb logcat`, ANRs from main-thread work, lifecycle/config-change state loss, permission denials. Do not convert Java to Kotlin as a fix.

## Upgrade workflow
1. **Scope and baseline:** record current versions; ensure the build and tests are green first (note pre-existing failures).
2. **Read the official migration guide and release notes** for every major step; upgrade one major at a time (e.g. 2.7 -> 3.0 -> 3.5 -> 4.0), through the latest patch of the starting line before crossing a major.
3. **Prepare:** remove deprecated API usage on the current version; add migration helpers (e.g. properties migrator) temporarily; consider automated recipes (OpenRewrite) but review their diff.
4. **Upgrade in small steps:** Java baseline/toolchain -> framework BOM -> dependent libraries (Hibernate, Security, Flyway/Liquibase, drivers) -> code changes. Commit/verify at each step.
5. **Fix compile errors, then test failures, then runtime/behaviour differences** (defaults changed: trailing slash, probes, Jackson, Hibernate SQL generation). Compare behaviour with tests; add tests for risky areas.
6. **Verify:** full build, integration tests on real DB, startup check, health, key flows, performance smoke if relevant; remove temporary helpers.
7. **Report** versions before/after, breaking changes handled, deviations, risks, rollback path.

## Decision rules
- Prefer small, verifiable fixes over broad speculative refactoring.
- Fix root causes; do not suppress (`@SuppressWarnings`, `exclude` autoconfig, `-DskipTests`, `ignoreFailures`, disabling validation/security) to get green.
- Do not upgrade, downgrade or add dependencies beyond what the fix requires; if a version bump is the fix, explain the evidence (release notes/issue) and verify.
- One change at a time when diagnosing; revert failed experiments.
- Never run destructive commands against shared environments (drop, clean, repair, force-push) without explicit authorisation.
- Do not paste secrets from logs/config into reports.

## Implementation guidance
- Fix at the layer where the cause lives (build configuration, dependency alignment, wiring, mapping, query, configuration) with the smallest change; keep the diff reviewable.
- Align versions through the BOM/`dependencyManagement` or version catalog rather than adding overrides; remove temporary diagnostics, properties migrators and debug logging before finishing.
- Prefer deprecation-free replacements named in the official migration guide; apply automated refactoring recipes only after reviewing their diff.
- Add a regression test for the failure mode where feasible; document non-obvious fixes in the commit message or a short comment explaining *why*.
- For upgrades, commit per step (Java baseline, BOM, dependent libraries, code changes) so any step can be reverted.

## Security and reliability requirements
Logs, dumps and configs may contain secrets/PII: redact before sharing; do not commit dumps. Temporary debug logging must be removed before finishing. Upgrades must keep security fixes (do not pin vulnerable versions to "make it work"). Have a rollback plan for production-facing upgrades.

## Common anti-patterns
- Fixing the last error in a cascade; guessing without reproducing.
- Adding explicit versions that fight the BOM; wildcard/range versions.
- Mixing Boot/Spring/Hibernate generations in one classpath.
- `skipTests`, deleting tests, catching and ignoring exceptions, `ddl-auto=update`, disabling Flyway validation or TLS verification to "fix" a failure.
- Big-bang upgrades across several majors with no intermediate green build.
- Trusting blog posts/Stack Overflow over official migration guides and release notes.
- Leaving debug logging, properties-migrator or temporary hacks in place.

## Testing and verification
Re-run the exact failing command and show the real result; add a regression test (unit/integration) that fails before and passes after, where feasible; run the module and dependent module builds and configured quality checks; for upgrades run the full suite and a startup/health check. State clearly anything not run (no container runtime, no access to prod data, no device).

## Definition of done
Root cause identified and evidenced; minimal fix applied at the right layer; original failure no longer reproduces; regression test added or reason given; wider build/tests run with real results; no suppression or weakening used; temporary diagnostics removed; versions/migration steps and residual risks documented.

## Related skills
`java-engineering-core`, `spring-boot-engineering`, `spring-security-engineering`, `spring-data-jpa-engineering`, `hibernate-orm-engineering`, `java-database-engineering`, `java-testing-quality`, `java-messaging-integration`, `java-performance-resilience`, `java-mobile-development`.

## Official references
- Spring Boot release notes and migration guides: https://github.com/spring-projects/spring-boot/wiki
- https://docs.spring.io/spring-boot/reference/ · https://docs.spring.io/spring-security/reference/migration/index.html
- Hibernate migration guides: https://hibernate.org/orm/documentation/
- Maven: https://maven.apache.org/guides/ · Gradle: https://docs.gradle.org/current/userguide/userguide.html
- JDK tools: https://docs.oracle.com/en/java/ · Android: https://developer.android.com/studio/build
- OpenRewrite (optional automation): https://docs.openrewrite.org/
