---
name: spring-boot-engineering
description: Implement, configure, test, troubleshoot and package Spring Boot applications (3.x and 4.x) - project setup, auto-configuration, starters, dependency injection, configuration properties and profiles, REST controllers, validation and error handling, Boot test slices, Actuator, logging, graceful shutdown and container images. Use when a repository contains Spring Boot (spring-boot-starter-*, @SpringBootApplication). Not for Spring Data JPA/Hibernate internals, Spring Security design, or Android.
---

# Spring Boot Engineering

## Purpose
Make correct, idiomatic changes to a Spring Boot application while respecting its installed Boot generation. Boot is an opinionated layer (auto-configuration, starters, externalised config, Actuator, testing support) over Spring Framework and other Spring projects. It is not the persistence, security or web-API design layer.

## Activation conditions
`pom.xml`/`build.gradle*` has `spring-boot-starter-parent`, the Boot BOM or the Boot Gradle plugin, or code uses `@SpringBootApplication`. Run `java-engineering-core` discovery first and record the **exact Boot version**.

## Version awareness (verified against official sources on 2026-10-10)
- Spring Boot reference lists stable: **4.1.1**, 4.0.8, 3.5.16, 3.4.13, 3.3.13; preview 4.2.0-M2. Support windows change; check https://spring.io/projects/spring-boot (Support / Version Mappings) before advising on upgrades.
- Boot 4.0 baseline (per the official 4.0 migration guide): Java 17+, Jakarta EE 11 / Servlet 6.1, Spring Framework 7.x.
- Boot 4 changes that commonly bite: modularised starters (`spring-boot-starter-web` deprecated for `spring-boot-starter-webmvc`; Flyway/Liquibase need their Boot starter; test starters paired per technology); **Jackson 3 by default** (`tools.jackson` packages; `@JsonComponent` becomes `@JacksonComponent`); `@MockBean`/`@SpyBean` removed for `@MockitoBean`/`@MockitoSpyBean`; `@SpringBootTest` no longer provides MockMvc/`TestRestTemplate`/`WebClient` automatically (add `@AutoConfigureMockMvc` / `@AutoConfigureTestRestTemplate`); liveness/readiness probes on by default; Undertow removed.
- Boot 3.x: Java 17+, Jakarta namespace (`jakarta.*`), Spring Framework 6.x. Boot 2.x uses `javax.*` and is out of OSS support.
- **Rule:** use the APIs of the version in the repo. Do not upgrade, switch Jackson generation or rename starters as a side effect. For upgrades use `java-maintenance-troubleshooting` and the official migration guides (https://github.com/spring-projects/spring-boot/wiki).

## Required context and inputs
Boot version, build tool, Java release, web stack (Spring MVC vs WebFlux), existing starters, profiles/config files, test setup, how the app is run/packaged.

## Repository inspection
1. Parent/BOM/plugin version; list `spring-boot-starter-*` and other Spring dependencies.
2. Main class and component-scan base package; `@Configuration` classes; custom auto-configuration.
3. `application.yml|properties`, `application-<profile>.*`, `@ConfigurationProperties` classes, env var conventions.
4. Controller/service/repository package layout and error handling (`@RestControllerAdvice`, `ProblemDetail`).
5. Existing tests and which slices/annotations they use.
6. Actuator exposure, logging config, Dockerfile/buildpacks/CI.

## Decision rules
- Add a **starter** rather than individual libraries; let the BOM manage versions (no explicit version unless required).
- Prefer **constructor injection** (single constructor needs no `@Autowired`); no field injection in new code.
- Typed configuration via `@ConfigurationProperties` (records or immutable classes with constructor binding; check the reference for the repo's version) + `@Validated`; use `@Value` only for trivial one-offs.
- Override auto-configuration with your own bean (`@ConditionalOnMissingBean` semantics) rather than excluding it; use `--debug` / `/actuator/conditions` to see why something did or did not configure.
- Web stack follows the repo (MVC vs WebFlux); never mix without need. Web API conventions live in `java-web-development`.
- Persistence beyond wiring a `DataSource` belongs to `spring-data-jpa-engineering` / `hibernate-orm-engineering`. Security design belongs to `spring-security-engineering`.
- Profiles select environment-specific *non-secret* config; secrets come from the environment or a secret store.
- Use `@Transactional` at the service layer only if the persistence skill/conventions say so; never on controllers.

## Workflow
1. Profile the repo (above). Identify Boot generation.
2. Place new code in the existing package structure; keep `@SpringBootApplication` at the root package so scanning covers it.
3. Wire dependencies via constructors; define configuration properties for any tunable value.
4. Implement controllers thin: validate (`@Valid`), delegate to a service, map to response DTOs.
5. Centralise errors in one `@RestControllerAdvice` returning consistent bodies (`ProblemDetail`/RFC 9457 if the project uses it).
6. Add tests at the lowest layer that proves the behaviour (below).
7. Run the build and tests; start the app if practical and check health endpoint and logs.
8. Report (see core skill).

## Implementation guidance
- **Configuration:** relaxed binding (`my.app.some-value` in files, `MY_APP_SOME_VALUE` env). Property precedence: command line > env > profile files > default files. Never commit real secrets; provide `application-example` or documented env vars.
- **Beans:** avoid circular dependencies (redesign, do not enable circular references); use `@Bean` methods in `@Configuration` for third-party types; scope singleton by default and keep singletons stateless.
- **Lifecycle:** `ApplicationRunner`/`CommandLineRunner` for startup tasks (keep short and idempotent); `@PreDestroy`/`SmartLifecycle` for cleanup.
- **Validation:** Jakarta Bean Validation annotations on request DTOs; `@Validated` on config properties; custom constraint for cross-field rules.
- **Async/scheduling:** configure executors explicitly (bounded); enable virtual threads only via supported property (`spring.threads.virtual.enabled`, Java 21+, Boot 3.2+) after checking the project's needs.
- **HTTP clients:** use the client type the version supports (`RestClient`, `WebClient`, `@HttpExchange` interfaces) with explicit connect/read timeouts; do not create a client per request.
- **Actuator:** add `spring-boot-starter-actuator`; expose only needed endpoints (`management.endpoints.web.exposure.include`); health groups for liveness/readiness; metrics via Micrometer; tracing via the observability starters/OpenTelemetry per project. Secure and, where possible, network-isolate the management endpoints (`management.server.port`).
- **Logging:** SLF4J + the default Logback unless the project differs; structured logging if the version supports it and the project uses it; no sensitive data; set levels in config, not code.
- **Shutdown:** `server.shutdown=graceful` plus `spring.lifecycle.timeout-per-shutdown-phase`; ensure in-flight work completes within the orchestrator's termination grace period.
- **Packaging:** executable jar via the Boot Maven/Gradle plugin; container images with layered jars/Dockerfile or `bootBuildImage`/`spring-boot:build-image` (Cloud Native Buildpacks); run as non-root; set memory via container limits. Detail in `java-production-deployment`.
- **DevTools** only in development scope; never in production artifacts.

## Kotlin in Spring Boot projects (mixed or Kotlin modules)
Spring Framework has first-class Kotlin support (the reference's Kotlin section covers requirements, null-safety, classes and interfaces, annotations, bean registration DSL, web, coroutines). The fetched page was only the intro, so the points below are general knowledge to **verify in https://docs.spring.io/spring-framework/reference/languages/kotlin.html**:
- Follow the language of the surrounding module; never convert files or add Kotlin to a Java-only module without authorisation.
- Build: Kotlin Gradle/Maven plugin with the `kotlin-spring` (all-open) plugin so Spring-annotated classes can be proxied, and `kotlin-jpa` (no-arg) for JPA entities; `kotlin-reflect`; the Jackson Kotlin module for data classes; keep `jvmTarget` aligned with the Java release.
- Idioms: constructor injection with `val` parameters; `@ConfigurationProperties` on data classes (constructor binding); null-safety honours Spring's nullability annotations; coroutine/`Flow` controllers need the reactive stack and coroutine-reactor bridge.
- Entities: avoid `data class` for JPA entities (generated `equals/hashCode/toString` touch lazy associations; see `hibernate-orm-engineering`); use classes with `var` properties and the no-arg plugin.
- Java/Kotlin interop in shared modules: annotate nullability in Java APIs, use `@JvmStatic`/`@JvmOverloads`/`@Throws` on Kotlin APIs consumed from Java, avoid exposing `suspend`/`Flow` to Java callers (see the interop rules in `java-mobile-development`, which apply equally on the JVM).
- Tests: JUnit works unchanged; MockK is common in Kotlin (check the repo); `@MockitoBean`/`@MockBean` rules above still apply when Mockito is used.

## Testing and verification
- **Unit tests** with no Spring context for logic.
- **Slices** for focused context: `@WebMvcTest` (controllers; add `@MockitoBean` for collaborators on Boot 4, `@MockBean` on 3.x), `@DataJpaTest`, `@JsonTest`, `@RestClientTest`. Slice annotation packages and starters changed in Boot 4 - check the repo's imports and the Test Slices appendix of the reference.
- **`@SpringBootTest`** for wiring and end-to-end behaviour; on Boot 4 add `@AutoConfigureMockMvc` when MockMvc is needed. Use `RANDOM_PORT` for real HTTP.
- **Real dependencies:** Testcontainers with `@ServiceConnection` (Boot 3.1+) for databases and brokers; avoid H2 as a stand-in when behaviour is database-specific.
- Override properties with `@TestPropertySource`/`@DynamicPropertySource`, not by editing main config.
- Keep contexts cacheable: avoid needless `@MockitoBean`/`@DirtiesContext` variations.
- Commands: `./mvnw test`, `./mvnw verify` or `./gradlew test`/`check`. For startup verification run the app and query `/actuator/health`.
- Troubleshooting startup: read the `FailureAnalyzer` message first; use `--debug` for the conditions report; check bean definition conflicts, missing starters, property binding errors, port conflicts, Jakarta/javax mismatches, version mismatches from overriding managed versions.

## Security and reliability requirements
- Do not expose Actuator `env`, `heapdump`, `configprops` or similar publicly; sanitise values; require authentication for management endpoints.
- No secrets in `application*.yml`, logs, images or tests. Use env/secret stores; check `@ConfigurationProperties` `toString` does not leak.
- Do not disable CSRF, security or TLS verification to make something work - route to `spring-security-engineering`.
- Bind configuration with validation so misconfiguration fails fast at startup.
- Set timeouts for outbound calls; bound thread pools and connection pools; implement readiness so traffic is only sent when ready.
- Error responses must not leak stack traces or internal details (`server.error.include-*` defaults off; keep it so).

## Common anti-patterns
- Field injection; `@Autowired` everywhere; service locators via `ApplicationContext.getBean`.
- Business logic in controllers or `@Configuration` classes.
- Pinning dependency versions that the BOM manages, causing conflicts.
- Mixing Boot generations' APIs (e.g. `@MockBean` on Boot 4, `javax.*` on Boot 3+).
- `@SpringBootTest` for every test; mocking the framework instead of using slices.
- Excluding auto-configuration to hide a startup error instead of fixing it.
- Exposing all Actuator endpoints; using `spring.jpa.hibernate.ddl-auto=update` in production.
- Component-scanning huge packages or putting the main class in the default package.
- Assuming every Spring capability (Security, Data, Kafka, AI) is part of "core Boot".

## Definition of done
Builds and passes tests with the repo's Boot version; configuration externalised and validated; new beans wired via constructors; error handling consistent; tests at appropriate slice plus integration where behaviour depends on the framework or database; app starts and health is up (or inability to run is stated); Actuator/logging/secrets reviewed; no unrequested version or starter changes; report lists commands and real results.

## Related skills
`java-engineering-core`, `java-web-development`, `spring-data-jpa-engineering`, `hibernate-orm-engineering`, `spring-security-engineering`, `java-testing-quality`, `java-production-deployment`, `java-maintenance-troubleshooting`.

## Official references
- https://spring.io/projects/spring-boot (current versions, support)
- https://docs.spring.io/spring-boot/reference/ (reference: features/external-config, testing, actuator, packaging/container-images, web/graceful-shutdown)
- https://github.com/spring-projects/spring-boot/wiki (release notes, migration guides)
- https://spring.io/projects/spring-framework
