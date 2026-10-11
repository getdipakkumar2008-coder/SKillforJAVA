---
name: java-performance-resilience
description: Measure, diagnose and improve Java application performance and resilience - profiling (JFR, async-profiler, thread/heap dumps), JVM memory and GC behaviour, thread and connection pool sizing, database query optimisation, HTTP client configuration, timeouts and bounded retries, circuit breakers and bulkheads, caching and invalidation, load testing, graceful degradation, failure recovery and shutdown. Use when latency, throughput, memory, CPU or stability problems are reported or when designing for load. Requires evidence before any optimisation.
---

# Java Performance and Resilience

## Purpose
Improve performance and failure behaviour using measurements, targeted changes and re-measurement. No guess-driven tuning.

## Activation conditions
Slow endpoints, high CPU/memory, GC pauses, thread starvation, pool exhaustion, timeouts, cascading failures, capacity planning, load-test requests, or reviewing a design for resilience. Run `java-engineering-core` discovery first.

## Required context and inputs
Symptom and target (SLO: p95/p99 latency, throughput, error rate, memory), when it happens (load, data size, time), environment parity (prod vs local), Java version and runtime flags, container limits, recent changes, existing metrics/traces.

## Core rule: evidence before optimisation
1. Define the metric and target; capture a **baseline** under representative conditions.
2. Find the bottleneck with profiling/measurement (not intuition).
3. Change **one** thing; re-measure under the same conditions.
4. Keep the change only if it improves the target measurably and does not hurt correctness, readability or resilience disproportionately.
5. Record before/after numbers and conditions. If you cannot measure (no load, no profiler access), say so and give hypotheses, not claims.

Premature micro-optimisation (manual loops over streams, object pooling, caching "just in case") is an anti-pattern. Algorithmic and I/O changes (queries, round-trips, data volume) almost always dominate.

## Measurement toolbox
- **Metrics/traces first** (Micrometer/Actuator, OpenTelemetry): where does request time go - app CPU, DB, downstream, queueing? See `java-production-deployment`.
- **JFR** (Java Flight Recorder, built into modern JDKs): low-overhead CPU, allocation, lock, GC, I/O profiling (`jcmd <pid> JFR.start ...`, `-XX:StartFlightRecording`); analyse in JDK Mission Control. async-profiler for CPU/alloc flame graphs where permitted.
- **Threads:** `jcmd <pid> Thread.print` / `jstack` repeated samples for hangs, lock contention, pool saturation.
- **Memory:** GC logs (`-Xlog:gc*`), heap histogram (`jcmd <pid> GC.class_histogram`), heap dump + analyser for leaks; check `OutOfMemoryError` type (heap, metaspace, direct, native, "unable to create thread", container OOM-kill).
- **Database:** slow-query log, `EXPLAIN (ANALYZE)`, statement counts (`hibernate-orm-engineering`), pool metrics (`java-database-engineering`).
- **Load testing:** Gatling, k6, JMeter or the project's tool; realistic data volume and mix, warm-up, steady state, ramp to and beyond expected peak, separate load generator host, record percentiles (not just averages), error rates and saturation signals. JMH for isolated micro-benchmarks only, correctly configured (forks, warm-up, blackhole).

## Repository inspection
Find what already exists before adding anything: Actuator/Micrometer/OpenTelemetry setup and dashboards, existing timeouts, retry, circuit-breaker and cache configuration, pool and executor settings (`spring.datasource.hikari.*`, thread pools, HTTP clients), JVM flags in Dockerfile/manifests, existing load-test or benchmark suites (Gatling/k6/JMH), slow-query logging, and recent changes that correlate with the symptom (`git log`).

## Decision rules
- **Where to look first:** (1) number of remote calls/queries per request (N+1, chatty APIs); (2) slow queries/missing indexes; (3) payload/result-set size and pagination; (4) serialization cost; (5) lock contention/thread pool queueing; (6) GC/memory; (7) code-level hot spots.
- **JVM memory/GC:** modern defaults (G1; ZGC/Shenandoah options) with container-aware heap are usually adequate. Tune only with GC logs/JFR evidence; set heap via percentage of container memory, leave headroom for metaspace, thread stacks, direct/native memory. Frequent full GCs or growing old gen after GC -> look for leaks/retention, not flags. Don't copy flag lists from the internet.
- **Threads/concurrency:** size pools by workload type: CPU-bound ~ number of cores; blocking I/O pools larger but **bounded** with bounded queues and a rejection policy; virtual threads (Java 21+) reduce thread cost for blocking I/O but you still need limits (semaphores/connection pools/bulkheads) on downstream resources. Avoid `parallelStream` on shared pools in servers.
- **Connection pools:** database pool small and bounded (see `java-database-engineering`); HTTP client pools with per-route limits and **timeouts** (connect, response, pool acquisition); pool exhaustion is a symptom - find slow holders.
- **Timeouts and retries:** every remote call has timeouts; propagate a deadline; retries only for idempotent/transient failures, bounded attempts, exponential backoff with jitter, a retry budget (avoid retry storms); don't retry on overload (429/503 with `Retry-After` respected).
- **Circuit breaker / bulkhead / rate limiter / load shedding:** add where a dependency can fail or slow and drag the caller down; configure thresholds from observed behaviour; define fallback (fail fast, cached/stale, degraded feature) and expose state as metrics. Bulkheads isolate resource pools per dependency.
- **Caching:** cache only measured hot, read-heavy, expensive-to-compute data; define key, TTL, size bound, eviction, invalidation/consistency model, stampede protection, and per-user/tenant isolation (never leak across users); local (Caffeine) vs distributed (Redis); cache is not a fix for an unindexed query or N+1. Measure hit rate.
- **Async/batching:** batch DB/API operations, use streaming/pagination for large data, move non-critical work off the request path via queues (`java-messaging-integration`) - with idempotency.
- **Graceful degradation:** identify essential vs optional functionality; optional features fail closed to a reduced response with clear signals; protect core paths with priority/quotas.
- **Failure recovery and shutdown:** health/readiness reflect ability to serve; graceful shutdown drains in-flight work within the grace period; background jobs are restartable and idempotent; startup tolerates dependency unavailability with retries/backoff rather than crash-loop where appropriate.

## Workflow
1. Clarify symptom, target and measurement method; reproduce under controlled load if possible.
2. Gather baseline metrics/profiles; identify the dominant cost (CPU, I/O wait, lock, GC, downstream).
3. Form a hypothesis tied to the evidence; choose the smallest change that tests it.
4. Implement; keep behaviour identical (tests green).
5. Re-measure with the same method; compare; check side effects (memory, correctness, resilience).
6. Add regression guards: a performance-sensitive test where practical (statement counts, benchmark thresholds with tolerance), dashboards/alerts.
7. Report: baseline, change, result, conditions, remaining bottlenecks.

## Implementation guidance
- Prefer fewer round-trips and less data over faster code; use projections, pagination, batch APIs, compression where appropriate.
- Avoid unnecessary object creation in proven hot paths only; use `StringBuilder`/streams idiomatically elsewhere; don't hand-roll data structures.
- Make resource limits explicit in config: max pool sizes, queue sizes, request body sizes, max concurrency, timeouts - and expose them as properties.
- Use `@Async`/executors with named, bounded pools and error handling; propagate MDC/security context when needed.
- Resilience libraries: Resilience4j (or framework-native retry/concurrency features per the repo's Spring version - verify) configured per dependency; test failure modes.
- Document performance-relevant assumptions (expected load, data volumes) next to the configuration.

## Security and reliability requirements
- Performance changes must not weaken validation, authorization, auditing or encryption.
- Caches must respect authorization boundaries and data sensitivity (no cross-tenant/user leakage; TTLs for sensitive data).
- Rate limiting/quotas protect against abuse and resource exhaustion; bound request sizes and concurrency.
- Do not enable remote profiling/JMX/heap dump endpoints without authentication and network restriction; heap dumps contain secrets/PII - handle and delete securely.
- Load tests must not target production without explicit approval, and must not use real personal data.

## Common anti-patterns
- Optimising without a baseline or profile; changing many things at once; trusting averages instead of percentiles.
- Tuning GC flags/heap sizes from blog posts; heap equal to container limit.
- Unbounded thread pools/queues/caches/retries; infinite or missing timeouts.
- Retrying everything, immediately, from every client (retry storm).
- Caching without invalidation or size bounds; caching per-user data in a shared key.
- Increasing pool sizes to hide slow queries or leaks.
- Micro-benchmarks outside JMH; benchmarking cold JVMs; load-testing a laptop against a toy dataset and extrapolating.
- Circuit breakers/fallbacks that silently return wrong data.
- Parallel streams in request threads; blocking calls on reactive/event-loop threads.

## Testing and verification
Re-run the same measurement before/after and report numbers with conditions (data volume, concurrency, JVM/version, hardware). Run the functional test suite to prove behaviour unchanged. Run failure-injection tests where resilience was added: downstream timeout, 5xx, slow responses, dependency down, pool exhaustion, shutdown during load. Say clearly what could not be measured (no prod-like environment, no profiler).

## Definition of done
Target metric and baseline recorded; bottleneck identified with evidence; change is minimal and justified; measurable improvement (or documented no-op) shown; tests green; limits, timeouts and fallbacks explicit and observable; no security or correctness regression; findings and residual risks reported honestly.

## Related skills
`java-engineering-core`, `java-core-engineering`, `hibernate-orm-engineering`, `java-database-engineering`, `java-messaging-integration`, `spring-boot-engineering`, `java-production-deployment`, `java-testing-quality`, `java-maintenance-troubleshooting`.

## Official references
- https://docs.oracle.com/en/java/ (JFR, `jcmd`, GC tuning guides for the repo's JDK) · https://openjdk.org/
- https://dev.java/
- https://docs.spring.io/spring-boot/reference/ (Actuator metrics, observability)
- https://opentelemetry.io/docs/ · https://micrometer.io/docs
- https://resilience4j.readme.io/ (if used) · https://github.com/ben-manes/caffeine/wiki
- https://openjdk.org/projects/code-tools/jmh/ · https://gatling.io/docs/ · https://k6.io/docs/
