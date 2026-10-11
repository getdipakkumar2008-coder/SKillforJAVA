# Technology Relationship Map

Understanding which layer a piece of technology belongs to keeps changes at the right abstraction level. The skills use these boundaries.

## Stack overview (server side)

```text
Application code (your domain, services, controllers)
  |
Spring Boot  -- starters, auto-configuration, externalised config, Actuator, test support
  |-- Spring Framework  -- IoC/DI, MVC/WebFlux, RestClient, transactions, validation
  |-- Spring Security   -- filters, authN/authZ, OAuth2/OIDC, method security
  |-- Spring Data (JPA) -- repositories, derived queries, auditing, specifications
  |        |
  |        v  uses
  |     Jakarta Persistence (JPA)  -- specification: @Entity, EntityManager, JPQL
  |        |
  |        v  implemented by
  |     Hibernate ORM  -- persistence context, SQL generation, caching, fetching
  |        |
  |        v  via JDBC
  |     Connection pool (HikariCP) -> Database (+ Flyway/Liquibase migrations)
  |-- Spring Kafka / AMQP / Integration -- messaging
  |-- Spring AI -- model, vector store, tool-calling abstractions
  |
Jakarta EE APIs (Servlet, Validation, ...)  +  Java SE (JDK, JVM)
```

| Layer | Is | Is not |
|---|---|---|
| Java SE | Language, JDK, JVM | A framework |
| Jakarta EE | Specifications (`jakarta.*`: Servlet, Persistence, Validation) | An application server you must use; Spring uses the APIs |
| Spring Framework | Core container and web/data/transaction infrastructure | Opinionated defaults (that is Boot) |
| Spring Boot | Opinionated configuration and packaging over Spring | Persistence, security or API design guidance |
| Spring Security | Authentication, authorization, protections | A substitute for server-side ownership checks |
| Jakarta Persistence | Persistence API specification | An implementation |
| Hibernate ORM | The JPA provider (also native APIs) | The repository abstraction |
| Spring Data JPA | Repository abstraction on top of JPA | An ORM |

Skills: `spring-boot-engineering` (Boot), `spring-data-jpa-engineering` (Spring Data/JPA level), `hibernate-orm-engineering` (provider runtime behaviour), `spring-security-engineering`, `java-database-engineering` (SQL, schema, migrations).

## Version generations (snapshot checked 2026-10-11; verify before relying)

| Line | Spring Framework | Jakarta | Notes |
|---|---|---|---|
| Spring Boot 4.x (4.1.1 current stable) | 7.x | Jakarta EE 11, Servlet 6.1 | Jackson 3 default; modular starters; Java 17+ baseline |
| Spring Boot 3.x (3.5.16 latest listed) | 6.x | Jakarta EE 10 | `jakarta.*` namespace; Java 17+ |
| Spring Boot 2.x | 5.x | `javax.*` | Out of open-source support; legacy only |

Related lines seen on the official pages: Spring Security 7.1.1 / 6.5.11; Spring Data JPA 4.1.1 / 3.5.13; Hibernate ORM 7.4 (latest stable, Jakarta Persistence 3.2), 7.2 and 6.6 (limited support), 8.0 in beta; Spring Framework 7.0.9 / 6.2.19; Spring AI 2.0.1; JUnit 6.1.3. The exact pairing of each Boot version with Spring Data and Hibernate must be read from the repository's resolved dependencies or the Boot "dependency versions" appendix.

## Web

```text
Browser / SPA / mobile client
   |  HTTPS (CORS if cross-origin; CSRF if cookie sessions)
   v
Spring MVC (servlet) or WebFlux (reactive)
   |  controllers -> DTOs -> services
   v
Thymeleaf / Vaadin (server-side UI)   or   JSON REST API (+ OpenAPI)
```

Skills: `java-web-development` (HTTP contract), `spring-security-engineering` (auth, CORS, CSRF), `spring-boot-engineering` (wiring). Frontend frameworks (Angular, React) are separate technology areas: follow the repository's own conventions.

## Mobile

```text
Android app (Java)                          Spring Boot backend
 UI (Activity/Fragment) -> ViewModel         controllers -> services -> JPA
   -> repository -> Room (local SSOT)          Spring Security (authoritative authz)
              \-> HTTPS client  ------------>  versioned REST API
```

- The Android client is **untrusted**: no server credentials, no authoritative authorization; tokens via OAuth 2.0 + PKCE, stored with Keystore-backed encryption.
- Do not apply Spring layering or `javax`/server idioms inside the app.
- Skill: `java-mobile-development` for the client; `java-web-development`, `spring-security-engineering` for the server side of the contract. Cross-platform mobile frameworks need their own skill.

## Build and test tooling

| Tool | Where | Skill |
|---|---|---|
| Maven / Gradle (wrappers) | All Java builds; Android uses Gradle + AGP (JDK 17 for AGP 8.x) | `java-engineering-core`, `java-maintenance-troubleshooting` |
| JUnit (Jupiter), Mockito, AssertJ | Unit/integration tests | `java-testing-quality` |
| Boot test slices, MockMvc | Spring tests | `spring-boot-engineering`, `java-testing-quality` |
| Testcontainers | Real DB/broker in tests | `java-testing-quality`, `java-database-engineering` |
| Flyway / Liquibase | Schema migrations | `java-database-engineering`, `spring-data-jpa-engineering` |
| Docker / buildpacks, CI | Packaging and pipeline | `java-production-deployment` |
| Micrometer, OpenTelemetry, Actuator | Observability | `java-production-deployment`, `spring-boot-engineering` |

## Integration and AI

```text
Service A --HTTP (timeouts, retries, circuit breaker)--> Service B
Service A --outbox--> Kafka / RabbitMQ --> consumers (idempotent, DLQ)
Application --port--> Spring AI ChatClient / provider SDK --> model
                      \-> VectorStore (authorization-filtered retrieval)
```

Skills: `java-messaging-integration`, `java-performance-resilience`, `java-ai-integration`. The model is an untrusted, probabilistic component; transactions, validation and authorization remain deterministic application code.

## Skill dependency sketch

```text
java-engineering-core  (always)
  |-- java-core-engineering --- java-architecture-design
  |-- spring-boot-engineering --- java-web-development --- spring-security-engineering
  |        |-- spring-data-jpa-engineering --- hibernate-orm-engineering --- java-database-engineering
  |        |-- java-messaging-integration --- java-performance-resilience
  |        `-- java-production-deployment
  |-- java-mobile-development
  |-- java-ai-integration
  |-- java-testing-quality   (used by nearly every task)
  |-- java-maintenance-troubleshooting
  |-- java-code-review  (applies the other skills as review lenses)
  `-- java-spec-driven-development  (maps tasks to the skills above)
```
