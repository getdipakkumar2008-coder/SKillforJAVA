---
name: java-testing-quality
description: Write, fix and review automated tests and quality gates for Java projects - JUnit (Jupiter), Mockito, AssertJ, parameterized tests, Spring Boot test slices, MockMvc, Testcontainers, repository/transaction tests, contract tests, Android unit and instrumentation tests, test data design, regression tests, static analysis, formatting and coverage as a diagnostic. Use whenever behaviour is added or changed, a test fails or is flaky, or quality checks need to be run or configured.
---

# Java Testing and Quality

## Purpose
Prove behaviour with the cheapest test that gives real evidence, and run the project's quality gates honestly.

## Activation conditions
New or changed behaviour; bug fix (write the failing test first); failing/flaky tests; adding integration tests; configuring or running static analysis, formatters or coverage. Run `java-engineering-core` discovery first to learn the test commands.

## Version awareness (checked 2026-10-11)
- JUnit docs (docs.junit.org) show **JUnit 6.1.3**: Java 17+ at runtime; modules Platform, Jupiter, Vintage (Vintage deprecated, migration aid only). Many repositories are still on JUnit 5 (`org.junit.jupiter`, 5.x) or JUnit 4 (`org.junit.Test`). **Use the generation in the repo**; do not mix or migrate as a side effect.
- Spring Boot 4: `@MockBean`/`@SpyBean` removed (use `@MockitoBean`/`@MockitoSpyBean`); `@SpringBootTest` does not auto-provide MockMvc/`TestRestTemplate`/`WebClient` (add `@AutoConfigureMockMvc` / `@AutoConfigureTestRestTemplate`); test starters are paired per technology. Boot 3.x keeps `@MockBean`. Details in `spring-boot-engineering`.
- Testcontainers: its getting-started guide pins example versions (e.g. 1.19.x) that may be outdated; take the version from the repo or the Spring Boot BOM, and check https://testcontainers.com/ for current coordinates and module names before adding one.

## Required context
Test framework and versions, test layout and naming (`*Test`, `*IT`), build commands, CI checks, container runtime availability, what behaviour/acceptance criteria must be proven.

## Decision rules - choose the lowest useful level
| Need | Test type |
|---|---|
| Pure business logic | Plain unit test, no Spring, no mocks of value types |
| Collaboration with a port/client | Unit test with Mockito for *outbound* collaborators only |
| Controller mapping, validation, serialization, error bodies | `@WebMvcTest` (MockMvc) |
| JPA mappings, queries, constraints, migrations | `@DataJpaTest` + real DB via Testcontainers |
| Wiring, config, security filter chain, transaction behaviour | `@SpringBootTest` (sparingly) |
| Outbound HTTP client | `@RestClientTest` / WireMock / MockWebServer |
| Messaging | Testcontainers broker or the framework's embedded/test support; assert idempotency and retry |
| API compatibility between services | Contract tests (Spring Cloud Contract/Pact) when consumers are separate teams |
| Critical user journey | A few end-to-end tests, not many |
| Android | Local JVM unit tests (`src/test`) for logic; instrumentation (`src/androidTest`) for UI/framework/device behaviour |

- Prefer **real** dependencies (Testcontainers) over mocks where semantics matter: SQL dialect, locking, transactions, JSON columns, broker delivery. H2 is not a substitute for a different production engine.
- Do not mock what you do not own (e.g. `EntityManager`, `HttpClient` internals); wrap and test at a boundary.
- Prefer state/behaviour assertions over `verify(...)` interaction assertions, except where the interaction *is* the behaviour (e.g. "email sent once").

## Workflow
1. Derive test cases from acceptance criteria: happy path, edge cases, validation failures, authorization failures, error/timeouts, idempotency/duplicates.
2. For a bug: write a test that fails for the reported reason; confirm it fails; fix; confirm it passes.
3. Write tests in the repo's style (naming, assertion library, fixtures).
4. Run the single test, then the class/module, then the wider build.
5. Run configured quality checks (formatter, static analysis, dependency/security scan).
6. Review the diff: no leftover `@Disabled`, `.only`-style focus, sleeps, or debug output.
7. Report exact commands and real outcomes, including what was skipped and why.

## Implementation guidance
- **Naming/structure:** behaviour-describing names (`rejectsOrderWhenStockInsufficient`); arrange-act-assert; one reason to fail per test; `@Nested` for grouping if the repo uses it.
- **Parameterized tests** (`@ParameterizedTest` + `@CsvSource`/`@MethodSource`) for input tables and boundaries.
- **Assertions:** use the repo's library (AssertJ/Hamcrest/JUnit); assert on meaningful fields, not whole-object `toString`.
- **Test data:** builders/object mothers kept small and local; unique values per test; no shared mutable fixtures; no dependence on execution order or wall-clock (inject `Clock`).
- **Spring slices:** keep the context minimal; import only needed config; prefer `@MockitoBean` (Boot 4) / `@MockBean` (Boot 3) sparingly because each distinct combination creates a new cached context.
- **Testcontainers:** share containers per test class/suite (static/`@ServiceConnection` bean or singleton) rather than per test; pin image tags; reuse across tests only if state is reset (truncate/transaction rollback). Requires a running container runtime - state clearly if absent.
- **Security tests:** use Spring Security test support (`@WithMockUser`, JWT post-processors) and assert 401/403 for unauthenticated/unauthorized, plus allowed paths. Never disable security in tests to make them pass.
- **Async:** await conditions (Awaitility) with timeouts; never `Thread.sleep` as synchronization.
- **Flakiness:** find the root cause (time, ordering, shared state, ports, async); do not add retries or ignore the test as the fix.
- **Static analysis/formatting:** run what the build already defines (Spotless, Checkstyle, PMD, SpotBugs, Error Prone, Sonar); do not weaken rules or add suppressions without a reason recorded in code.
- **Coverage (JaCoCo etc.):** a diagnostic for untested areas, not a target to game; check that new branches of changed code are exercised by meaningful assertions.
- **Android:** JUnit + Mockito/Robolectric for local tests; Espresso/AndroidX Test (and Compose test APIs if Compose is used) for instrumentation on an emulator/device; keep logic out of Activities/Fragments so it is unit-testable; instrumentation tests cannot run without an emulator/device - report that honestly.

## Security and reliability requirements
- No real credentials, tokens or production data in tests, fixtures or logs; use generated/fake values.
- Tests must be hermetic and repeatable: no dependence on external networks or shared environments unless explicitly an end-to-end suite.
- Cover unauthorized, forbidden, invalid-input and failure/timeout paths for anything on a trust boundary.
- Clean up resources (containers, temp files, threads); bounded timeouts so a hung test fails fast.

## Common anti-patterns
- Deleting, skipping (`@Disabled`) or loosening a failing test to get green; swallowing exceptions in tests.
- Tests that restate the implementation, over-specify mocks, or assert private details.
- `@SpringBootTest` for everything; slow suites from many distinct contexts.
- H2 "because it's faster" for database-specific behaviour; mocking repositories to test queries.
- Shared state between tests; order dependence; `Thread.sleep`; time/locale/timezone dependence.
- Chasing 100% coverage with assertion-free tests.
- Reporting "tests pass" without running them or without noting which tests were not run.

## Testing and verification (of this skill's own work)
Show the test command and its real result. Confirm the new test fails without the fix (for bugs) and passes with it. Run the module build and configured quality tasks (`./mvnw verify`, `./gradlew check`, Android `./gradlew testDebugUnitTest`, `connectedDebugAndroidTest`). List anything that could not run (no Docker, no emulator, offline dependency resolution).

## Definition of done
Acceptance criteria each map to at least one test; normal, edge and failure paths covered; tests are deterministic and in the repo's style; relevant suite and quality checks were executed with real results reported; no test removed/weakened/disabled to pass; skipped checks disclosed.

## Related skills
`java-engineering-core`, `spring-boot-engineering`, `spring-data-jpa-engineering`, `hibernate-orm-engineering`, `spring-security-engineering`, `java-web-development`, `java-messaging-integration`, `java-mobile-development`, `java-maintenance-troubleshooting`.

## Official references
- https://docs.junit.org/current/user-guide/ (previously junit.org/junit5/docs/current/user-guide/, which redirects)
- https://docs.spring.io/spring-boot/reference/testing/index.html and the Test Slices appendix
- https://testcontainers.com/
- https://site.mockito.org/ · https://assertj.github.io/doc/
- Android testing: https://developer.android.com/training/testing
- OWASP Testing Guide: https://owasp.org/www-project-web-security-testing-guide/
