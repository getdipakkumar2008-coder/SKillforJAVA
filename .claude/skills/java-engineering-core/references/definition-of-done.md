# Definition of Done

A task is done only when every applicable item is true and evidenced. Mark items "n/a" with a reason rather than silently skipping them.

## Behaviour
- [ ] Every acceptance criterion is met and was checked explicitly.
- [ ] Existing behaviour is unchanged unless the task asked to change it.
- [ ] Edge cases and failure paths are handled.

## Code
- [ ] Follows repository conventions and the project's Java release level.
- [ ] Change is scoped; no unrelated refactors, formatting churn or dependency changes.
- [ ] No debug code, commented-out blocks, TODOs without owner, or secrets.
- [ ] Public API and compatibility impact considered and noted.

## Tests
- [ ] New or changed behaviour has tests (normal, edge, failure).
- [ ] Trust-boundary changes have unauthorised/invalid-input tests.
- [ ] Persistence, transaction or framework behaviour is verified with a realistic integration test where mocks cannot show it.
- [ ] No test was deleted, skipped or weakened to pass.

## Verification (evidence required)
- [ ] Relevant tests were run; command and real result recorded.
- [ ] Project build was run for the affected module(s).
- [ ] Configured formatter / static analysis / security checks were run, or their absence noted.
- [ ] Anything not run is listed with the reason.

## Security and operations (when relevant)
- [ ] Input validated; queries parameterised; authorisation enforced server-side.
- [ ] No secrets in code, config or logs.
- [ ] Timeouts, retries and idempotency considered for remote calls and messages.
- [ ] Logging, health or metrics added or preserved where appropriate.
- [ ] Config is externalised; deployment assumptions documented.

## Documentation and reporting
- [ ] Docs, migration notes, specs/tasks updated to match what was actually done.
- [ ] Final report lists: files changed, decisions, commands and results, risks, remaining work.
- [ ] No claim of success that is not backed by an observed result.
