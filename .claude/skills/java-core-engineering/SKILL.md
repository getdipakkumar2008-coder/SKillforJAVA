---
name: java-core-engineering
description: Core Java language and runtime guidance for writing or modifying plain Java code - records, sealed types, generics, collections, streams, exceptions, immutability, concurrency, virtual threads, CompletableFuture, java.time, I/O, JVM memory/GC, null handling and API design. Use for any Java code change that is not framework-specific, or when choosing language features for a project's Java release. Pair with java-engineering-core.
---

# Java Core Engineering

## Purpose
Write correct, readable, version-appropriate Java. Language features are chosen by the project's release level and by clarity, not novelty.

## Activation conditions
Java code is being written, changed or reviewed: libraries, domain logic, utilities, concurrency, I/O, API design, JVM behaviour. Framework-specific concerns go to the matching skill (Spring Boot, JPA, Android, ...). Run `java-engineering-core` discovery first.

## Required context and inputs
Java release level (from build file/toolchain), whether the code is a public library API (compatibility rules apply), threading context, and existing style in neighbouring code.

## Feature gating by release
Check the project's `release`/toolchain before using a feature. Use the table as a guide and confirm against https://dev.java/ or the JEP if unsure.

| Feature | Final in |
|---|---|
| `var` (locals), `List.of`/`Map.of` | 10 / 9 |
| `switch` expressions, text blocks | 14 / 15 |
| Records, `instanceof` pattern matching | 16 |
| Sealed classes | 17 |
| Pattern matching for `switch`, record patterns | 21 |
| Virtual threads, sequenced collections | 21 |
| Structured concurrency, scoped values, string templates, unnamed variables | check current status; several were preview in 21-24 - do not use preview features unless the project already enables them |

Never enable `--enable-preview` or raise the release level as a side effect of a task.

## Repository inspection
Confirm from the build files: the Java release (`release`/toolchain), preview flags, Kotlin presence, language-level lint or static-analysis rules (Error Prone, SpotBugs, Checkstyle), whether the module is a published library (public API compatibility, `module-info`), logging and testing libraries, and the style of neighbouring code (immutability, exceptions, null handling, naming). Do not use a feature above the release level.

## Decision rules
- **Value carrier** with no behaviour beyond data: record (if release >= 16). Needs identity, mutation or inheritance: class.
- **Closed set of variants** handled exhaustively: sealed interface + records + `switch` (release >= 21 for patterns). Otherwise enum or plain interface.
- **Collections:** choose by access pattern; expose interface types (`List`, `Map`); return unmodifiable or copied collections from public APIs; never return `null` for a collection.
- **Streams** for simple transform/filter/collect pipelines; a plain loop when there is mutation, checked exceptions, early exit with side effects, or the pipeline needs comments to be understood. No side effects in `map`/`filter`. Avoid parallel streams unless measured and the workload is CPU-bound and stateless.
- **Optional:** return type only. Not for fields, parameters or collections.
- **Concurrency model:** prefer immutability and confinement, then `java.util.concurrent` (executors, `ConcurrentHashMap`, atomics, locks), then `synchronized`. Hand-rolled `wait/notify` and raw `Thread` management are last resorts.
- **Virtual threads (21+):** good for many blocking, I/O-bound tasks; use one-task-per-thread executors (`Executors.newVirtualThreadPerTaskExecutor()`); do not pool them; limit concurrency with a semaphore when a downstream resource is limited; be aware of pinning with `synchronized` around blocking calls in older releases. Not a fix for CPU-bound work.
- **CompletableFuture:** always supply an explicit executor for blocking work, set timeouts (`orTimeout`/`completeOnTimeout`), handle failures (`exceptionally`/`handle`), and never `join()` inside the pool you are running on.
- **Time:** `java.time` only (`Instant` for timestamps, `ZonedDateTime`/`LocalDate` for civil time, inject a `Clock` for testability). Store/transmit UTC instants.
- **Numbers:** `BigDecimal` (explicit scale and `RoundingMode`) for money; never `double`. Beware `int` overflow (`Math.addExact`).
- **Text:** specify `StandardCharsets.UTF_8`; use `Locale.ROOT` for case-insensitive technical comparisons; `String.format`/text blocks for readability.

## Workflow
1. Read adjacent code and tests; mirror naming, error handling and style.
2. Model the domain: types, invariants, immutability. Validate in constructors/factories.
3. Write the simplest implementation that passes the tests.
4. Define error handling: unchecked exceptions for programmer errors/violated preconditions, checked or typed results for recoverable conditions per project convention. Preserve causes.
5. Review concurrency: what is shared, who mutates it, what is the visibility guarantee?
6. Review API surface: minimal public API, documented contract (Javadoc on public types), null-ness and thread-safety stated.
7. Add tests (see below), run them.

## Implementation guidance
- **Immutability:** `final` fields, defensive copies in/out, `List.copyOf`. Records are shallowly immutable - copy mutable components.
- **equals/hashCode:** consistent and based on the same fields; use records or `Objects.equals/hash`; never include mutable state in keys of hash collections.
- **Exceptions:** specific types; messages with actionable context but no secrets; no empty `catch`; no `catch (Throwable)` except at a top-level boundary; do not log-and-rethrow the same exception repeatedly.
- **Resources:** try-with-resources for every `AutoCloseable`; `Files`/NIO.2 over `File`; bound read sizes from untrusted sources.
- **Null handling:** `Objects.requireNonNull(x, "x")` at public entry points; document nullable parameters; prefer empty collections/`Optional` returns over `null`.
- **Generics:** use bounded wildcards (PECS) on inputs; avoid raw types and unchecked casts; no generic arrays.
- **Logging:** SLF4J parameterised logging if the project uses it; never `System.out` in library code.
- **Serialization:** avoid Java native serialization, especially of untrusted data; use JSON/Protobuf with explicit schemas.
- **JVM/runtime:** do not tune GC or heap flags without measurements (GC logs, JFR, heap dumps). Know common leaks: static collections, unclosed resources, `ThreadLocal` on pooled threads, listener registrations. Default collector and container-aware heap sizing are usually adequate.
- **Kotlin consumers of a Java API:** annotate nullability on every non-primitive parameter, return and field (JSR 305 / `androidx.annotation` / JSpecify per the repo) - unannotated types become Kotlin "platform types"; put functional-interface parameters last; use bean-style accessor names; avoid Kotlin keywords as member names. In a mixed repo, do not convert Java to Kotlin as an interop fix.
- **Public library API:** treat public signatures as a contract. Prefer adding over changing; deprecate with `@Deprecated(since=..., forRemoval=...)` and Javadoc replacement; keep binary compatibility; use `module-info` or package conventions to hide internals when the project uses them.

## Security and reliability requirements
- Validate input size/shape; never build SQL, shell commands or paths by concatenating untrusted strings (use parameters, `ProcessBuilder` arg lists, path normalisation + base-directory check).
- Use `SecureRandom` for security tokens; standard crypto APIs, never custom crypto; no hardcoded keys.
- No unbounded queues/pools/caches; apply timeouts to I/O and futures.
- Thread safety documented; shared mutable state minimised; interrupt status restored on `InterruptedException`.

## Common anti-patterns
- Using the newest syntax the project's release does not support, or enabling preview features silently.
- `Optional` as field/parameter; `Optional.get()` without check.
- Streams with side effects or nested streams that obscure intent.
- `double` for money; `Date`/`Calendar`/`SimpleDateFormat` in new code.
- Mutable static state; double-checked locking without `volatile`; `synchronized` on public objects.
- Catch-and-ignore; catching `Exception` to hide bugs; exceptions for control flow.
- `new Thread()`/unbounded `Executors.newCachedThreadPool()` for server work.
- Returning internal mutable collections; `equals` without `hashCode`.
- Premature optimisation or micro-benchmarks without JMH/profiling.

## Testing and verification
- JUnit (match the project's version: JUnit 5 `org.junit.jupiter` vs JUnit 4) with behaviour-named tests; parameterised tests for input tables; AssertJ/Hamcrest per project convention.
- Test edge cases: null/empty, boundaries, overflow, time zones/DST, locale, encoding, large input, failure paths and exceptions (type and message).
- Concurrency: deterministic tests where possible (inject executors/clocks); use timeouts; stress tests supplement, not replace, reasoning.
- Run the module build (`./mvnw test` / `./gradlew test`) and any configured static analysis.

## Definition of done
Compiles at the project's release level; behaviour covered by tests that were run; public API and compatibility reviewed; no resource, concurrency or null-handling hazards left unexplained; follows existing style; report lists commands run and real results (see `java-engineering-core` definition of done).

## Related skills
`java-engineering-core`, `java-architecture-design`, `java-testing-quality`, `java-performance-resilience`, `java-maintenance-troubleshooting`.

## Official references
https://dev.java/ · https://docs.oracle.com/en/java/ · https://openjdk.org/jeps/0 (JEP index) · https://junit.org/junit5/docs/current/user-guide/
