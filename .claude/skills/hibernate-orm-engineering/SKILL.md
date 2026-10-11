---
name: hibernate-orm-engineering
description: Diagnose and tune Hibernate ORM runtime behaviour in Java/Spring apps - persistence context and entity lifecycle, lazy vs eager loading, N+1 queries, fetch joins, entity graphs, projections, cascades and orphan removal, dirty checking and flush, first/second-level cache, batching, optimistic/pessimistic locking, equals/hashCode pitfalls, SQL inspection and schema generation vs migrations. Use for slow or incorrect persistence behaviour, LazyInitializationException, hundreds of SELECTs, save or merge of a detached entity overwriting fields with null, unexpected updates or deletes, or mapping design. Pair with spring-data-jpa-engineering.
---

# Hibernate ORM Engineering

## Purpose
Understand and control what Hibernate does between your entities and SQL. Fix persistence problems with evidence (SQL and statistics), not guesses.

Relationship: Jakarta Persistence is the spec; Hibernate is the provider implementing it; Spring Data JPA and Spring Boot sit on top (see `spring-data-jpa-engineering`). Prefer standard JPA APIs; use `org.hibernate.*` features (`@BatchSize`, `@NaturalId`, `StatelessSession`, `@Formula`, filters) only when needed, and say so.

## Activation conditions
LazyInitializationException, N+1 or slow queries, unexpected updates/deletes, mapping or cascade design, batch import, caching, locking, flush-order bugs, or a Hibernate/JPA migration question. Run `java-engineering-core` discovery first.

## Version awareness (checked 2026-10-11)
Per hibernate.org: 7.4 latest stable; 7.2 and 6.6 limited support; 8.0 beta. 7.x targets Jakarta Persistence 3.2 (Java 17+); 6.6 targets 3.1 (Java 11+). Use the version the repo resolves (`mvn dependency:tree` / `gradle dependencies`). Do not rely on remembered property names or HQL behaviour across 5 -> 6 -> 7: check https://hibernate.org/orm/documentation/ (User Guide and Migration Guide for that version).

## Required context and inputs
Hibernate version, Spring Data/Boot versions, DB engine, mapping of the affected entities, the failing use case (endpoint/method), actual SQL and row counts, transaction boundaries.

## Repository inspection
1. Entities and mappings involved (fetch types, cascades, `mappedBy`, ids, versions, `@Cacheable`).
2. Service methods/transactions that load and use them; any `open-in-view` setting.
3. Hibernate properties: `hibernate.jdbc.batch_size`, `order_inserts/order_updates`, `default_batch_fetch_size`, cache config, `generate_statistics`.
4. Logging config for SQL; test infrastructure.

## Diagnose with evidence
Enable temporarily (never leave verbose SQL/parameters on in production):
- `spring.jpa.show-sql` is crude; prefer logger `org.hibernate.SQL=DEBUG` (and `org.hibernate.orm.jdbc.bind=TRACE` on Hibernate 6.x+ for parameters; verify logger name for the version).
- `hibernate.generate_statistics=true` for query counts/cache hits; or a datasource proxy / test assertion on statement count.
- DB: `EXPLAIN`/`EXPLAIN ANALYZE`; slow-query log.
Record: SQL statement count per request, rows fetched, time. Optimise only against these numbers.

## Decision rules
- **Entity states:** transient -> persistent (`persist`/`merge`/load) -> detached (session closed) -> removed. Changes to *managed* entities are flushed automatically (dirty checking); changes to detached entities are lost unless `merge`d. `save()` on Spring Data calls `persist` for new and `merge` for existing - `merge` copies state into a managed instance and may issue a SELECT.
- **Lazy loading:** keep associations `LAZY`. `LazyInitializationException` means you touched an uninitialised proxy outside a session - fix by fetching what the use case needs *inside* the transaction (fetch join, entity graph, projection, DTO mapping in the service). Do not "fix" by switching to `EAGER` or relying on `open-in-view`.
- **N+1:** one query for parents + N for children. Fixes, in order of preference: (1) DTO/interface projection selecting exactly needed columns; (2) `JOIN FETCH` or `@EntityGraph` for the use case; (3) `@BatchSize` / `hibernate.default_batch_fetch_size` to turn N into N/batch; (4) restructure the query. Fetch-joining **one** collection is fine; multiple bag collections cause `MultipleBagFetchException` or cartesian products - fetch in separate queries instead.
- **Pagination + collection fetch join** makes Hibernate paginate in memory (warning `HHH000104` / "firstResult/maxResults specified with collection fetch"). Page parent ids first, then fetch children for those ids.
- **Cascades/orphanRemoval:** only from aggregate root to owned children; `CascadeType.REMOVE`/`ALL` on `@ManyToOne` or shared entities is a bug. `orphanRemoval = true` for exclusively-owned children; replace collection contents, do not reassign a new collection instance on a managed parent.
- **Flush behaviour:** default `AUTO` flushes before queries touching affected tables and at commit; manual `flush()` only for ordering/constraint timing or batching memory control; `clear()` after large batches.
- **Batching:** set `hibernate.jdbc.batch_size` (e.g. 20-50, measure), `order_inserts`, `order_updates`; avoid `IDENTITY` ids for batch inserts (use sequence); flush and clear periodically; for massive loads consider `StatelessSession` or JDBC/bulk operations.
- **Caching:** first-level cache is the per-session persistence context (always on). Second-level/query cache is opt-in per entity with a provider (JCache/Ehcache/Infinispan); use only for read-mostly data after measurement, define eviction/TTL, and remember multi-node invalidation. Do not use as a fix for N+1.
- **Locking:** `@Version` optimistic locking by default for concurrent updates; pessimistic (`PESSIMISTIC_WRITE`, `SKIP LOCKED` for queues) only with justification, timeouts and consistent lock order to avoid deadlocks.
- **equals/hashCode:** do not use generated id alone if entities enter `Set`s before persist (hash changes); use a natural/business key (`@NaturalId`) or a stable approach (constant `hashCode` per class with id-based `equals` guarded for null/proxy). Compare via `Hibernate.getClass`/`instanceof` to handle proxies. No Lombok-generated versions that touch associations.
- **Schema generation vs migrations:** `hbm2ddl` is for prototypes/tests only. Production schema is owned by Flyway/Liquibase; validate mappings with `validate`.

## Workflow
1. Reproduce the problem in a test or local run; capture SQL/stat counts (baseline).
2. Identify cause (loading strategy, missing index, flush, cascade, detached state, id strategy).
3. Make the smallest targeted fix (query/graph/projection/mapping/batching) - not global setting changes first.
4. Re-measure; assert the improvement in a regression test (statement count or behaviour).
5. Check side effects: other use cases using the same mapping, transaction scope, memory.
6. Report with before/after numbers.

## Implementation guidance
- Prefer per-query fetch plans over global `EAGER`. Use `@EntityGraph` on repository methods for repeated plans.
- Read paths: projections/DTOs; write paths: load aggregate, mutate, let dirty checking flush.
- Mark read-only transactions `readOnly = true` (skips dirty checking where supported).
- Large collections: avoid mapping huge `@OneToMany` at all - query the many side by parent id with paging.
- Use `getReferenceById` when only an FK reference is needed (no SELECT) and you know the id exists.
- Custom types/JSON/enums: follow the version's native mapping support; test round-trips.
- Avoid entity listeners performing I/O or touching other aggregates.

## Security and reliability requirements
- Never concatenate user input into HQL/JPQL/native SQL; use parameters. Allow-list dynamic sort/filter fields.
- Don't leak entity internals or lazy proxies through serialization; map to DTOs.
- Do not log bound parameters containing PII/secrets in production.
- Bound batch sizes and result sets; apply query timeouts (`jakarta.persistence.query.timeout`/`@QueryHints`) for risky queries; handle lock timeouts and deadlocks with bounded retry of the whole transaction.

## Common anti-patterns
- "Fix" LazyInitializationException with `EAGER` or `open-in-view`.
- Fetching a collection per row in a loop (N+1) hidden behind a mapper or `toString`/JSON serialization.
- `findAll()` then filtering in Java; entity-per-row processing for million-row jobs without clear().
- `CascadeType.ALL` everywhere; replacing managed collections; `merge` of partially populated detached DTO-built entities (nulls overwrite data).
- Second-level cache to mask bad queries; caching mutable, frequently updated data.
- `hashCode` on a generated id; Lombok `@Data` entities.
- `ddl-auto=update` in production; ignoring Hibernate warnings in logs.
- Native queries by habit; premature global tuning without measurement.

## Testing and verification
- Integration tests on the real DB engine (Testcontainers) with Flyway/Liquibase applied.
- Assert SQL statement count (Hibernate `Statistics` or datasource-proxy) for N+1 regressions; assert lazy fields are not touched outside the transaction.
- Test cascade/orphan removal, optimistic-lock conflicts, flush-order/constraint failures, batch behaviour with realistic volume.
- Check `EXPLAIN` for new/changed queries and confirm indexes (`java-database-engineering`).
- State the Hibernate version and DB used for the verification; say what could not be run.

## Definition of done
Cause identified with evidence; fix is targeted and scoped to the use case; before/after measurements recorded; regression test added and executed; no API entities leaked; no global tuning left without justification; no verbose SQL logging left enabled; report lists commands and real results.

## Related skills
`java-engineering-core`, `spring-data-jpa-engineering`, `java-database-engineering`, `java-performance-resilience`, `java-testing-quality`, `java-maintenance-troubleshooting`.

## Official references
- https://hibernate.org/orm/documentation/ (User Guide, Migration Guide, Query Language Guide for the repo's version)
- https://jakarta.ee/specifications/persistence/
- https://docs.spring.io/spring-data/jpa/reference/
- https://docs.spring.io/spring-boot/reference/ (data/sql, application properties)
