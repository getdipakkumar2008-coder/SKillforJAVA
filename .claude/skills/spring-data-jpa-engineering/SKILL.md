---
name: spring-data-jpa-engineering
description: Design and change the Spring Data JPA layer - entities, repositories, derived/JPQL/native/Specification queries, projections, pagination and sorting, relationships and aggregate boundaries, service-layer transactions, auditing, optimistic locking, Flyway/Liquibase migrations and persistence tests. Use when a repository has spring-boot-starter-data-jpa / spring-data-jpa. For Hibernate runtime behaviour (N+1, fetching, flush, caching, batching) also load hibernate-orm-engineering.
---

# Spring Data JPA Engineering

## Purpose
Implement persistence features at the **Spring Data repository** abstraction level, correctly and with verified behaviour.

How the pieces relate (do not conflate them):
- **Jakarta Persistence (JPA)**: the specification (`jakarta.persistence.*`: `@Entity`, `EntityManager`, JPQL).
- **Hibernate ORM**: the JPA provider that actually generates SQL, manages the persistence context and caches. Hibernate-specific features live in `org.hibernate.*`.
- **Spring Data JPA**: repository abstraction (`JpaRepository`, derived queries, `@Query`, specifications, auditing) that calls `EntityManager`.
- **Spring Boot**: auto-configures the `DataSource`, `EntityManagerFactory`, transaction manager and Spring Data via `spring-boot-starter-data-jpa`.

Use the highest level that does the job; drop to JPQL/`EntityManager`/Hibernate APIs only when the abstraction cannot express it.

## Activation conditions
Task adds/changes entities, repositories, queries, migrations, transactions, auditing or locking in a Spring Data JPA project. Run `java-engineering-core` discovery first.

## Version awareness (checked 2026-10-11)
- Spring Data JPA current stable per spring.io: **4.1.1** (also 4.0.7, 3.5.13). Boot 3.x uses Spring Data 3.x; Boot 4.x uses Spring Data 4.x - confirm in the repo's BOM and in the "Dependency Versions" appendix of the Boot reference.
- Hibernate ORM per hibernate.org: 7.4 latest stable, 7.2 and 6.6 limited support, 8.0 in beta; 7.x implements Jakarta Persistence 3.2, 6.6 implements 3.1.
- Namespaces: `jakarta.persistence` (Boot 3+/Hibernate 6+); `javax.persistence` only in legacy Boot 2.
- Use the versions the repository already pins. Hibernate 6 -> 7 and Boot 3 -> 4 upgrades are a separate task (`java-maintenance-troubleshooting`).
- Verify annotations and properties in https://docs.spring.io/spring-data/jpa/reference/ for the repo's version before using them.

## Required context
Database engine and version, migration tool, existing entity/repository conventions, transaction style, test setup (Testcontainers vs H2), Hibernate and Spring Data versions, whether schema is shared with other services.

## Repository inspection
1. Dependencies: `spring-boot-starter-data-jpa`, JDBC driver, Flyway/Liquibase (and on Boot 4 their starters), Testcontainers.
2. `spring.jpa.*`, `spring.datasource.*`, `spring.jpa.hibernate.ddl-auto`, `open-in-view`.
3. Existing entities (id strategy, equals/hashCode, relationships, auditing base class), repositories, services (`@Transactional` placement).
4. Migration folder and naming (`db/migration/V<version>__*.sql`, Liquibase changelog), history of applied migrations.
5. Persistence tests and how the database is provided.

## Decision rules
- **Schema changes go through migrations** (Flyway/Liquibase) and are reviewed; `ddl-auto` is `validate` or `none` outside throwaway local/test use. Never `update`/`create` against shared or production data.
- **Aggregate boundaries:** repository per aggregate root; reference other aggregates by id when they have separate lifecycles; cascade only inside an aggregate.
- **Relationships:** default to `LAZY` for `@ManyToOne`/`@OneToOne` (JPA defaults those to eager); keep collections `LAZY`; prefer unidirectional; if bidirectional, maintain both sides in helper methods and mark the inverse with `mappedBy`. Prefer `Set` or `List` consistently with the repo; avoid `@ManyToMany` with extra attributes - model a join entity.
- **Identity:** `IDENTITY` disables JDBC insert batching in Hibernate; sequences (`SEQUENCE` with allocation size matching the DB sequence increment) allow batching. Follow existing choice unless there is a reason.
- **Query choice, simplest first:** derived query method (short names only) -> `@Query` JPQL -> projection (interface/record/DTO) -> `Specification`/Criteria for dynamic filters -> native SQL only when needed (document why; keep portable fallback in mind).
- **Return only what is needed:** DTO/interface projections for read endpoints; do not expose entities in API responses (lazy loading, over-posting, leaking fields).
- **Pagination:** `Pageable` with a bounded max page size and stable sort including a unique tie-breaker; use `Slice` when total count is unnecessary; beware count query cost; collection fetch-join with pagination causes in-memory pagination (see Hibernate skill).
- **Transactions:** `@Transactional` at the service layer (Spring proxies; self-invocation bypasses it); `readOnly = true` for query-only methods; keep transactions short; no remote calls inside; define rollback rules for checked exceptions explicitly; repository methods are already transactional individually.
- **Concurrency:** `@Version` for optimistic locking on contended aggregates and handle `ObjectOptimisticLockingFailureException` (retry or 409); pessimistic locks (`@Lock`) only with evidence, plus timeouts.
- **Auditing:** `@EnableJpaAuditing` with `@CreatedDate`, `@LastModifiedDate`, `@CreatedBy`, `@LastModifiedBy` and an `AuditorAware` bean; keep on a `@MappedSuperclass`.
- **Bulk operations:** `@Modifying` queries bypass the persistence context - use `clearAutomatically`/`flushAutomatically` deliberately.

## Workflow
1. Model: write/adjust entity with invariants, constraints (`nullable`, `unique`, length) matching the DB.
2. Write the migration first (or alongside): table/column, constraints, indexes (foreign keys, query predicates, sort columns). Make it forward-compatible and describe rollback/backfill; avoid destructive changes in the same release as code that needs the old shape.
3. Add repository method(s); choose projection and pagination.
4. Implement service logic with transaction boundaries; map entity -> DTO inside the transaction or via projection.
5. Test against the real database engine (below). Inspect generated SQL.
6. Verify migrations apply from scratch and on top of the previous version.
7. Report.

## Implementation guidance
- Entities: no-arg constructor (protected), no `final` on class/persistent fields where the provider needs proxies; avoid Lombok `@Data`/`@EqualsAndHashCode`/`@ToString` on entities (loads lazies, breaks proxies, cycles).
- `equals/hashCode`: based on a business key or a stable id strategy; never on mutable fields; see Hibernate skill for pitfalls.
- Enums: `@Enumerated(EnumType.STRING)`, never ordinal.
- Time: `Instant`/`OffsetDateTime`/`LocalDate`; store UTC.
- Money: `BigDecimal` with explicit `precision/scale`.
- Derived query names stay readable; otherwise use `@Query` with named parameters (`:name`), never string concatenation.
- Use `existsBy...`/`count` for checks instead of loading entities.
- Soft delete, multi-tenancy, JSON columns: follow existing repo mechanism; these are Hibernate/DB-specific features.
- Do not rely on `open-in-view` for lazy loading in controllers; fetch what the use case needs in the service.

## Security and reliability requirements
- Parameterised queries only; validate sort property names from clients against an allow-list (a client-supplied `sort` can reference any property or fail with errors).
- Enforce row-level/tenant authorization in the service/query, not only the UI or controller; never trust client-provided ids without ownership checks.
- Do not log SQL parameters/PII in production; restrict DB account privileges (no DDL rights for the runtime user if migrations run separately).
- Migrations must be idempotent per tool semantics and safe under concurrent app start (Flyway/Liquibase locking); plan data backfills for large tables.
- Handle constraint violations (`DataIntegrityViolationException`) with meaningful, non-leaking error responses.

## Common anti-patterns
- Exposing entities from controllers; `FetchType.EAGER` everywhere; `ddl-auto=update` in production.
- Bidirectional relationships without sync helpers; cascade `REMOVE` across aggregates.
- `findAll()` on large tables; unbounded pagination; sorting on unindexed columns.
- `@Transactional` on private/self-invoked methods; on controllers; wrapping remote calls.
- Business logic in repositories or in entity lifecycle callbacks that hit other services.
- Testing persistence only with mocks, or with H2 when the real DB differs in SQL/locking/JSON/type behaviour.
- Lombok `@Data` on entities; ordinal enums; `IDENTITY` assumed to batch.

## Testing and verification
- `@DataJpaTest` (slice; replaces DataSource with embedded DB by default - override to use Testcontainers via `@ServiceConnection` and `@AutoConfigureTestDatabase(replace = NONE)`) for repositories and mappings.
- Run Flyway/Liquibase in tests so migrations are exercised; also validate `ddl-auto=validate` passes against migrated schema.
- Assert behaviour and query count/SQL for critical paths (e.g. Hibernate statistics or a datasource proxy) to catch N+1.
- Test transactions: rollback on exception, optimistic-lock conflict, constraint violation, pagination/sort stability, projections.
- Run `./mvnw verify` / `./gradlew check`; state clearly if a container runtime was unavailable and which tests did not run.

## Definition of done
Entity, migration and repository agree; schema validated by migration (not auto-DDL); queries bounded, indexed and parameterised; transactions at service layer; DTO/projection boundaries respected; tests ran against a realistic database with real results reported; authorization/ownership enforced; no unrelated version or schema changes.

## Related skills
`java-engineering-core`, `spring-boot-engineering`, `hibernate-orm-engineering`, `java-database-engineering`, `java-testing-quality`, `spring-security-engineering`, `java-maintenance-troubleshooting`.

## Official references
- https://spring.io/projects/spring-data-jpa and https://docs.spring.io/spring-data/jpa/reference/ (query methods, projections, auditing, locking, specifications)
- https://spring.io/projects/spring-data
- https://jakarta.ee/specifications/persistence/
- https://hibernate.org/orm/documentation/
- Flyway: https://documentation.red-gate.com/flyway · Liquibase: https://docs.liquibase.com/
