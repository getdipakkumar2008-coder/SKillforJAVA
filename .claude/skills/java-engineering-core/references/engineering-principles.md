# Engineering Principles

Applied proportionately: a one-line fix does not need a design document.

## Correctness and maintainability
- Match existing architecture, naming and formatting.
- Make business rules explicit, named and unit-testable. Keep them out of controllers, entities' persistence hooks and framework glue.
- No duplicated logic; but do not extract an abstraction until there is a second real use.
- Preserve public API and behaviour unless the task requires a change; if it does, call out the compatibility impact.
- Record consequential decisions (code comment for local, ADR/doc for architectural).

## Java conventions
- Use language features available at the project's release level. Use records, `switch` expressions, pattern matching, text blocks, `var` and virtual threads only if the level supports them and the code stays readable.
- Prefer immutability: `final` fields, unmodifiable collections, records for value carriers.
- Depend on interfaces at boundaries; prefer constructor injection.
- Model absence deliberately: `Optional` for return values, not fields or parameters; validate arguments with `Objects.requireNonNull` or bean validation at boundaries.
- Handle exceptions at the right layer; never swallow them; preserve the cause; do not use exceptions for normal control flow.
- Close resources with try-with-resources.
- Use `java.time` for dates; `BigDecimal` for money; explicit charsets.
- Avoid clever code. Readability beats brevity.

## Security
- Least privilege; deny by default.
- Validate and bound all untrusted input; use parameterised queries.
- No secrets in code, tests, logs or config committed to source control.
- Authorisation is enforced server-side, never by a client.
- Never disable security controls to make a test pass; fix the test setup instead.
- Add tests for unauthorised and invalid requests where the change touches a trust boundary.

## Reliability
- Bounded timeouts and bounded, backed-off retries for remote calls. Retry only idempotent operations.
- Assume duplicate requests and messages; design for idempotency.
- Keep transactions short and consistent; no remote calls inside DB transactions unless justified.
- Avoid unbounded queues, thread pools, caches and result sets.
- Make background work restartable.

## Testing
- Unit tests for isolated business logic; integration tests where framework, DB or network semantics matter (prefer real dependencies such as Testcontainers over mocks for persistence behaviour).
- Cover normal, edge and failure paths.
- Test observable behaviour, not implementation details.
- Name tests by behaviour; keep fixtures small and local.
- Coverage is a diagnostic, not the goal.
- Never delete or skip a failing test to pass a build.

## Production readiness
- Externalise environment-specific configuration.
- Log actionable events with context, without sensitive data.
- Provide health/readiness where the app is deployed as a service.
- Consider resource limits and graceful shutdown.
- State deployment assumptions in the report or docs.

## Dependencies and versions
- Do not add or upgrade dependencies without need; prefer what the BOM already manages.
- Check that a library version matches the Java and framework generation (e.g. Jakarta vs javax).
- Distinguish Java SE, Jakarta EE, Spring Framework, Spring Boot, Android SDK and third-party APIs.
- Treat deprecated, preview and experimental features as exceptions requiring justification.
- Prefer official documentation over blog posts or recalled examples.
