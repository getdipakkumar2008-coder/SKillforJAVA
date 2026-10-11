---
name: java-architecture-design
description: Make and review software design and architecture decisions in Java codebases - SOLID and dependency direction, layered vs hexagonal (ports and adapters), package-by-feature vs by-layer, domain models and invariants, DDD where it pays off, modular monolith vs microservices, module and API boundaries, dependency injection and composition, design patterns, architecture decision records, and avoiding over-engineering. Use when adding a module, restructuring, choosing between designs, or reviewing structure. Choose the simplest structure that satisfies the requirements; never impose one architecture.
---

# Java Architecture and Design

## Purpose
Choose and apply the simplest structure that meets current requirements, keeps business rules explicit and testable, and makes likely future change cheap - without speculative abstraction.

## Activation conditions
New module/service/package design; "where should this code live?"; restructuring or modularising; choosing monolith vs services; boundary or dependency problems (cycles, god classes, leaking entities); design reviews; writing or updating an ADR. Run `java-engineering-core` discovery first: **the existing architecture is the default**.

## Version awareness (checked 2026-10-11)
- Spring Modulith (https://spring.io/projects/spring-modulith) lists **2.1.1**: application modules organised around the domain, structure verification, per-module integration tests, module-level observability, generated component documentation. Its Boot compatibility is on the project's Version Mappings page - check before use. It is an option for modular monoliths on Spring Boot, not a requirement.
- Architecture guidance here is version-independent; language features (records, sealed types, pattern matching) depend on the repo's Java release - see `java-core-engineering`.

## Required context and inputs
Business capabilities and rate of change, team size/structure, deployment constraints, scale and availability needs, data ownership, existing architecture and ADRs, non-functional requirements (latency, compliance, security), what is painful today.

## Repository inspection
1. Package/module layout (by layer, by feature, hexagonal); Maven/Gradle modules and their dependency graph.
2. Dependency direction: do domain classes import framework/persistence/web types? Cycles between packages?
3. Where business rules live (services, entities, controllers, SQL, listeners).
4. Existing ADRs, diagrams, architecture tests (ArchUnit, Spring Modulith verification).
5. Integration points and data ownership (shared database? shared entities?).
6. Hotspots: largest classes, most-changed files, most-coupled packages.

## Decision rules
- **Existing convention first.** Extend the established structure; propose structural change only when it solves a demonstrated problem, and do it incrementally.
- **Simplest thing that works.** A straightforward layered/feature-based Spring Boot app is the right answer for many services. Add ports/adapters, DDD tactical patterns, CQRS, event sourcing or microservices only for a stated need (testability of complex rules, multiple adapters, independent scaling/deployment, team autonomy).
- **Dependency rule:** dependencies point toward business/domain code; domain code does not depend on web, persistence, messaging or framework APIs *when the domain is rich enough to justify that isolation*. For thin CRUD, using Spring Data/JPA types directly in the service is acceptable and simpler.
- **Package by feature over by layer** for growing systems (cohesion, encapsulation via package-private visibility); by-layer is fine for small apps. Be consistent with the repo.
- **Layered:** controller -> service -> repository; controllers thin, services own use-case orchestration and transactions, repositories own persistence. Avoid skipping layers or calling upward.
- **Hexagonal (ports and adapters):** worth it when the domain logic is complex or the system has multiple inbound/outbound technologies; ports are interfaces owned by the domain/application layer, adapters implement them. Don't create an interface per class "just in case" - one implementation with no boundary reason doesn't need one.
- **DDD where useful:** ubiquitous language, bounded contexts, aggregates enforcing invariants, value objects, domain events - when the domain is complex and the business is a differentiator. Skip tactical DDD for CRUD/reporting. Aggregates are small, reference each other by id across boundaries, and are loaded/saved as a unit (see `spring-data-jpa-engineering`).
- **Domain model:** put invariants in constructors/factories/aggregate methods so invalid states are unrepresentable; prefer immutability and value objects (records) for values; avoid anemic models only when rules are non-trivial; separate persistence entities from domain objects only if the mapping cost is justified.
- **Modular monolith vs microservices:** default to a **modular monolith** (clear modules, enforced boundaries, one deployable). Move to services only with evidence: independent scaling or release cadence, team boundaries, fault isolation, or divergent technology needs - and accept costs (network failure modes, distributed data consistency, operational overhead; see `java-messaging-integration`, `java-production-deployment`). Never split by technical layer; split by business capability. Don't share a database schema across services.
- **Boundaries:** expose a small public API per module (facade/service interface, events, DTOs); keep internals package-private; no cross-module access to another module's entities/repositories; communicate via public APIs or events. Enforce with Spring Modulith verification, ArchUnit, or Java modules if the repo uses them.
- **API/contract boundaries:** external contracts (REST, messages) are separate from internal models and versioned (`java-web-development`).
- **Dependency injection and composition:** constructor injection; wiring in one composition root/configuration; depend on abstractions at real boundaries; avoid service locators, static singletons and hidden `ApplicationContext` lookups; keep beans stateless.
- **Cross-cutting concerns** (security, transactions, logging, validation, metrics) via framework mechanisms (filters, AOP, annotations) - not copy-pasted - but keep business flow readable.
- **Design patterns:** use a pattern when it removes a concrete problem (Strategy for interchangeable algorithms, Factory/Builder for complex creation, Adapter at integrations, Decorator for layered behaviour, Observer/events for decoupled reactions). Name the problem first. Prefer language features (lambdas, records, sealed types) over ceremonial patterns.
- **Data and consistency:** decide transaction boundaries and ownership with the design; across modules/services prefer eventual consistency with outbox/sagas over distributed transactions.
- **Non-functional design:** capture security, performance, resilience, observability and operability as design inputs, not afterthoughts (link to the relevant skills).

## Workflow
1. Restate the requirement and constraints; identify what is changing and why a design decision is needed.
2. Inspect the current structure and constraints; list options (usually 2-3), **including "keep the current structure"**.
3. Compare options on: fit to requirements, complexity, testability, change cost, operability, risk, consistency with the repo. Prefer reversible decisions.
4. Choose the simplest viable option; state trade-offs and assumptions briefly.
5. Apply in small steps (strangler/incremental refactoring); keep the build green and behaviour unchanged during refactors (characterisation tests first when coverage is thin).
6. Add enforcement where cheap (architecture test, module verification, package-private visibility).
7. Record consequential decisions in an ADR; update diagrams/docs if the project keeps them.
8. Verify with tests and builds; report.

## ADR guidance
For consequential, hard-to-reverse decisions create a short record in the project's ADR location (e.g. `docs/adr/NNNN-title.md`), following existing format; otherwise use MADR-style: Title, Status, Context, Decision, Options considered, Consequences. One decision per ADR; immutable once accepted - supersede rather than edit. Don't write ADRs for routine choices.

## Implementation guidance
- Refactor toward the target structure with behaviour-preserving steps: extract class/method, introduce interface at a real seam, move package, then change dependencies.
- Break dependency cycles by extracting an interface owned by the consumer, moving shared concepts to a lower module, or using events - not by merging everything.
- Replace inheritance with composition where behaviour varies; keep interfaces small and cohesive.
- Keep modules cohesive: things that change together live together; minimise what is public.
- Avoid shared "common/util" dumping grounds; shared kernels are small, stable and deliberate.
- Enforce rules automatically (ArchUnit/Modulith) rather than via documentation alone.
- Android: apply its own architecture guidance (UI, domain, data layers; ViewModel/state) via `java-mobile-development`; do not transplant Spring layering.

## Security and reliability requirements
- Trust boundaries are explicit in the design; authorization enforced server-side at module/API boundaries (`spring-security-engineering`).
- Data ownership, PII locations and retention are part of boundary decisions.
- Failure isolation: timeouts/bulkheads at remote boundaries; no hidden synchronous chains between modules/services (`java-performance-resilience`).
- Architectural changes must remain compatible with deployment and rollback plans.

## Common anti-patterns
- Over-engineering: interfaces with one implementation and no seam, hexagonal/DDD/CQRS for CRUD, microservices for a small team, generic frameworks nobody asked for.
- Under-structuring: business logic in controllers or SQL, god services, shared mutable global state, entity classes used as API, domain, and message models all at once.
- Distributed monolith: services sharing a database or requiring lockstep releases.
- Layer-per-technology packages that force every feature to touch every package; "utils" dumping grounds.
- Circular dependencies between packages/modules; cross-module repository access.
- Big-bang rewrites; architecture changes bundled into feature work without tests.
- Pattern worship: forcing patterns without a problem; naming classes after patterns instead of domain concepts.
- Undocumented consequential decisions; documentation that diverges from code.

## Testing and verification
- Characterisation/regression tests around code being restructured; run the full relevant suite before and after.
- Architecture tests (ArchUnit or Spring Modulith `verify()`) for dependency direction, cycles and module boundaries, if present or newly justified.
- Module-level integration tests; contract tests at service boundaries.
- Build and run; confirm no behavioural change; report real command results and what was not verified.

## Definition of done
Decision fits stated requirements and existing conventions; simplest viable option chosen with trade-offs recorded (ADR if consequential); dependencies point the intended direction without cycles; boundaries are small and enforced where practical; behaviour preserved with tests green; no speculative abstractions added; docs/diagrams updated if the project keeps them; verification results reported honestly.

## Related skills
`java-engineering-core`, `java-core-engineering`, `spring-boot-engineering`, `spring-data-jpa-engineering`, `java-web-development`, `java-messaging-integration`, `java-testing-quality`, `java-performance-resilience`, `java-production-deployment`, `java-mobile-development`, `java-spec-driven-development`.

## Official references
- https://spring.io/projects/spring-modulith and https://docs.spring.io/spring-modulith/reference/
- https://docs.spring.io/spring-framework/reference/core/beans.html (IoC container, dependency injection)
- https://dev.java/ (language features for domain modelling)
- https://www.archunit.org/userguide/html/000_Index.html
- ADR practice: https://adr.github.io/ · Microservices patterns: https://microservices.io/patterns/
- Android architecture: https://developer.android.com/topic/architecture
