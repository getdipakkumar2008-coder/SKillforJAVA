---
name: java-database-engineering
description: Relational database engineering for Java applications - schema design, keys, constraints, indexes and normalization, SQL query design, transactions and isolation levels, connection pool sizing (HikariCP), migrations with Flyway/Liquibase and rollback planning, execution-plan analysis, deadlocks and concurrency, data integrity, test database strategy and data-access security. Use for schema or migration changes, slow queries, locking problems or connection exhaustion. Database-specific tuning is kept separate from portable guidance.
---

# Java Database Engineering

## Purpose
Get the data layer right regardless of the access technology (JPA, JDBC, jOOQ, MyBatis): correct schema, safe migrations, predictable transactions, evidence-based query tuning.

## Activation conditions
New/changed tables, columns, indexes or constraints; migration scripts; slow queries or timeouts; deadlocks, lock waits, lost updates; connection pool exhaustion; test database strategy; data-access permissions. For ORM mapping and fetching use `spring-data-jpa-engineering` and `hibernate-orm-engineering` alongside. Run `java-engineering-core` discovery first.

## Required context and inputs
DB engine and **version** (PostgreSQL, MySQL/MariaDB, SQL Server, Oracle, ...), hosting (managed/self), data volume and growth, read/write ratio, migration tool and conventions, deployment style (rolling, blue/green; multiple app versions at once?), and who else uses the schema.

## Portable vs engine-specific
- Portable core: normalization, keys, constraints, standard SQL, transaction semantics, index theory.
- Engine-specific: index types (partial/GIN/BRIN, clustered), `EXPLAIN` output format, default isolation level and lock behaviour (MVCC vs locking reads), `SKIP LOCKED`/`FOR UPDATE` variants, JSON/array types, online DDL support, sequence vs identity behaviour.
Mark engine-specific changes clearly, check that engine's official docs for the deployed version, and do not assume behaviour from another engine.

## Repository inspection
1. Migration tool, directory, naming and checksum rules; latest applied version; repeatable/undo conventions.
2. Existing schema conventions: naming, id strategy, audit columns, timestamp types, soft-delete, tenancy columns.
3. `spring.datasource.*` / Hikari settings, timeouts, JDBC URL flags.
4. How tests obtain a database; whether migrations run in tests.
5. DB users/roles used by the app vs by migrations.

## Decision rules
- **Schema design:** model the domain, then normalise (typically 3NF); denormalise only for measured read needs, with a plan for keeping copies consistent. Every table has a primary key.
- **Constraints belong in the database:** `NOT NULL`, `UNIQUE`, `CHECK`, foreign keys with deliberate `ON DELETE` behaviour. Application validation is not a substitute for integrity.
- **Keys:** surrogate keys (sequence/identity/UUID) with natural keys enforced via unique constraints; random UUIDs as clustered PKs can hurt locality on some engines - consider time-ordered UUIDs; match the repo's choice.
- **Types:** exact numeric for money (`NUMERIC/DECIMAL` with scale); timestamps with time zone semantics decided (store UTC); right-sized strings; avoid storing structured data as unqueryable blobs unless JSON features are intended.
- **Indexes:** create for foreign keys, frequent filters/joins and sort orders; composite index column order follows equality-then-range predicates and selectivity; avoid redundant indexes (each costs writes and storage); verify with the execution plan; partial/covering indexes where the engine supports them.
- **Isolation:** know the engine's default (e.g. READ COMMITTED on PostgreSQL, REPEATABLE READ on MySQL/InnoDB). Raise isolation or use explicit locking/optimistic versioning only for specific invariants; handle serialization failures with bounded retry of the whole transaction.
- **Concurrency control:** optimistic (`version` column) for typical aggregate updates; pessimistic (`SELECT ... FOR UPDATE`, `SKIP LOCKED` for work queues) when contention is high and short; consistent lock ordering to prevent deadlocks; unique constraints as the arbiter for "create if absent" races (catch the violation) rather than check-then-insert.
- **Transactions:** short; no network calls or user waits inside; one clear unit of work; explicit read-only where beneficial.
- **Migrations:** versioned, immutable once applied (never edit applied migrations); small, reviewed, testable from scratch and from the previous release. Use **expand/contract** for zero-downtime: add nullable/new structures -> deploy code that writes both/reads new -> backfill in batches -> enforce constraints -> remove old later. Destructive changes (drop/rename/narrow type) are separate, later releases. Long-running DDL/backfills on large tables: use engine online-DDL features, batches and off-peak scheduling.
- **Rollback:** decide up front - forward-fix, undo script, or backup/restore. Many DDL changes are not safely reversible; state this in the plan. Keep application code compatible with both the old and new schema during rollout.
- **Connection pools (HikariCP default in Boot):** pool size is small and bounded - start near `cores * 2 + effective spindles` for the DB server, then measure; total connections across all app instances must fit the DB's `max_connections`; set connection/idle/max-lifetime timeouts below infrastructure timeouts; never size the pool to "number of request threads". Pool exhaustion usually means slow queries or leaked/long transactions, not "too few connections".

## Workflow
1. Clarify the data requirement and invariants; list queries/access patterns.
2. Design/adjust tables, constraints and indexes; write the migration (and rollback/forward-fix plan, backfill plan if needed).
3. Run migrations on an empty database and on a database at the previous version (with representative data when risk is high).
4. Write/adjust queries; check parameterisation; run `EXPLAIN (ANALYZE)` or the engine equivalent on realistic data volume; add indexes only for confirmed plans.
5. Test concurrency-sensitive paths (duplicates, simultaneous updates, deadlock retry).
6. Review security and operational impact (locks, duration, size, privileges).
7. Report with plans/timings and what could not be tested (e.g. production-size data).

## Implementation guidance
- SQL: explicit column lists (no `SELECT *` in application queries); joins over N queries; set-based operations over row loops; keyset pagination for deep paging; `EXISTS` over `COUNT` for presence; avoid functions on indexed columns in predicates; bind parameters, never concatenate.
- Batch writes with JDBC batching; bounded batch and transaction sizes; idempotent upserts via the engine's mechanism (`ON CONFLICT`, `MERGE`, `ON DUPLICATE KEY`) - engine-specific, label it.
- Flyway/Liquibase: one change per migration; ensure the migration user has DDL rights while the runtime user has only DML; keep reference data migrations idempotent; check checksum validation is not disabled to "fix" a failure.
- Auditing/history: use audit columns or history tables per repo convention; avoid triggers unless the repo uses them.
- Data lifecycle: retention, archival and deletion (including privacy requirements) designed, not an afterthought.

## Test database strategy
- Use the **same engine and major version as production** via Testcontainers for anything touching SQL, locking, types or migrations. In-memory databases (H2/HSQLDB) only for logic that is genuinely engine-independent.
- Apply the real migrations in tests; assert the ORM `validate` passes.
- Reset state per test (transaction rollback, truncate, or fresh container per suite); no dependency on order.
- Seed minimal, deterministic data; use larger generated datasets for plan/performance checks outside the unit-test suite.

## Security and reliability requirements
Reliability: short transactions, retry whole transactions on deadlock/serialization failure with bounds, migrations safe under concurrent starts and rolling deploys, bounded pools and batch sizes, tested backup/restore assumptions. Security:
- Parameterised queries only; allow-list dynamic identifiers (sort columns, table names).
- Least-privilege DB accounts: separate migration and runtime roles; no superuser/DBA in app config; per-service schemas/users.
- Credentials from secret stores, not source/config files; TLS to the database where supported; rotate credentials.
- Encrypt or hash sensitive columns as policy requires (application-level or engine features); mask PII in logs and non-production copies.
- Row-level access via application checks or engine row-level security where used; never rely on the client.
- Do not log SQL parameters containing secrets/PII.

## Common anti-patterns
- Editing an already-applied migration; `ddl-auto=update` in production; schema changes outside migrations.
- No foreign keys/unique constraints "for flexibility"; integrity only in application code.
- Adding indexes blindly; indexing every column; missing indexes on FKs and filtered/sorted columns.
- Oversized connection pools; long transactions holding locks; network calls inside transactions.
- Check-then-insert races; read-modify-write without versioning or locking.
- `SELECT *`, `OFFSET` deep paging, N+1 patterns, row-by-row loops over large sets.
- Storing money as floating point; local-time timestamps without a policy.
- Using H2 to "verify" engine-specific behaviour; testing migrations never.
- Breaking old app versions during rolling deploys (drop/rename in the same release).

## Testing and verification
Run migrations from scratch and upgrade-from-previous in a container of the production engine and version; run repository/integration tests; capture `EXPLAIN` before/after for changed queries; run concurrency tests for new invariants; report commands, engine/version, data volume used and any gaps (no prod-sized data, no container runtime).

## Definition of done
Schema, constraints and indexes justified; migrations versioned, immutable, tested from scratch and incremental; rollout/rollback plan stated and compatible with rolling deploys; queries parameterised and verified with plans; transaction and concurrency behaviour tested; pool settings reasoned; privileges least-privilege; engine-specific parts labelled; real results reported.

## Related skills
`java-engineering-core`, `spring-data-jpa-engineering`, `hibernate-orm-engineering`, `spring-boot-engineering`, `java-testing-quality`, `java-performance-resilience`, `java-production-deployment`, `spring-security-engineering`.

## Official references
- Flyway: https://documentation.red-gate.com/flyway · Liquibase: https://docs.liquibase.com/
- Your engine's official docs for the deployed version (e.g. https://www.postgresql.org/docs/ , https://dev.mysql.com/doc/ , SQL Server and Oracle docs)
- HikariCP: https://github.com/brettwooldridge/HikariCP (including "About Pool Sizing")
- https://docs.spring.io/spring-boot/reference/data/sql.html
- Testcontainers: https://testcontainers.com/
- OWASP SQL Injection Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/
