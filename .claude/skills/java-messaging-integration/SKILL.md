---
name: java-messaging-integration
description: Design and implement external API calls and asynchronous messaging in Java - HTTP clients (RestClient, WebClient, HTTP interfaces), Kafka, RabbitMQ/AMQP, JMS and cloud messaging; sync vs async choice, message contracts and schema evolution, delivery guarantees, idempotency and duplicate handling, retries and dead-letter queues, timeouts, circuit breakers, transactional outbox/inbox, eventual consistency and compensation, client resilience and observability. Use when integrating services or adding events. Do not add a broker or distributed architecture without a requirement.
---

# Java Messaging and Integration

## Purpose
Integrate with other systems so that failures, duplicates, slowness and schema changes are handled by design, not by hope.

## Activation conditions
Calling external HTTP APIs; publishing/consuming messages; adding retries, DLQs or circuit breakers; designing events or integration contracts; fixing duplicate, lost or stuck messages. Run `java-engineering-core` discovery first; find what integration technology already exists.

## Version awareness (checked 2026-10-11)
- Spring for Apache Kafka **4.1.1** is current; its 4.1.x matrix lists kafka-clients 4.2.x and Spring Boot 4.1.x. Spring AMQP (RabbitMQ) current is **4.1.1** (`RabbitTemplate`, listener container, `RabbitAdmin`). Boot 3.x uses earlier lines of both; use the repo's versions and Boot-managed versions. Override client versions only per the Boot reference appendix.
- Retry/concurrency-limit support was added to the core Spring Framework in recent generations (`@Retryable`, `@ConcurrencyLimit` in Framework 7); I could not confirm the exact reference page - verify in https://docs.spring.io/spring-framework/reference/ for the repo's version before using. Spring Retry (separate project) is no longer Boot-managed in Boot 4 (per Boot 4.0 migration guide), so pin deliberately if used. Resilience4j is a common circuit-breaker library; check its current Spring Boot compatibility.
- HTTP clients: `RestClient` (blocking), `WebClient` (reactive), `@HttpExchange` interface clients - use what the repo uses.

## Required context
Existing broker/clients, delivery requirements (at-most/at-least/effectively-once), ordering needs, volume and latency, consumers and their independence, data ownership, failure tolerance, who owns the contract, schema registry presence.

## Repository inspection
1. Existing client beans/config (timeouts, pools, auth), error mapping.
2. Producers/consumers, topics/queues/exchanges, naming conventions, partition/routing keys.
3. Serialization format (JSON, Avro, Protobuf) and schema management.
4. Retry/DLQ config; idempotency or dedup stores; outbox tables.
5. Existing integration tests and local broker setup (compose/Testcontainers).

## Decision rules
- **Sync vs async:** synchronous HTTP when the caller needs an immediate answer and the dependency is reliable and fast; asynchronous messaging when work can be deferred, fan-out is needed, load must be smoothed, or components should be decoupled in time. Do not add a broker, service mesh or microservice boundary without a requirement-based justification; a method call or a DB-backed job table may suffice.
- **Commands vs events:** command = request to do something (one consumer, may fail); event = fact that happened (many consumers, past tense, immutable). Name accordingly.
- **Delivery guarantees:** assume **at-least-once** and design consumers to be **idempotent**. "Exactly-once" is only achievable within specific scopes (e.g. Kafka transactions within Kafka) - not end-to-end with a database/HTTP side effect.
- **Idempotency:** unique message/business id; store processed ids with the side effect in the same DB transaction (inbox/dedup table with a unique constraint); or make the operation naturally idempotent (upsert, set-state-to). For HTTP `POST` retried by clients, accept an `Idempotency-Key`.
- **Dual-write problem:** never "update DB then publish" (or reverse) as two independent steps when consistency matters. Use the **transactional outbox**: write the event to an outbox table in the same transaction; a relay (poller/CDC) publishes it at-least-once. Consumers use an **inbox**/dedup.
- **Ordering:** guaranteed only within a partition/queue per key; choose the key (e.g. aggregate id) deliberately; parallel consumers break global order.
- **Retries:** retry only transient, idempotent-safe failures; bounded attempts; exponential backoff with jitter; separate non-blocking retry topics/queues for long delays rather than blocking the consumer; never infinite hot loops.
- **Poison messages:** classify non-retryable errors (deserialization, validation) and route straight to a **dead-letter** queue/topic with headers describing the failure; monitor and have a replay procedure.
- **Timeouts:** every remote call has connect and read/response timeouts shorter than the caller's own deadline; total retry budget bounded; propagate deadlines where possible.
- **Circuit breaker / bulkhead / rate limit:** add around unreliable or slow dependencies when evidence or SLOs justify it; define fallback behaviour (fail fast, cached/stale data, degraded response) and make it observable. Don't wrap everything by default.
- **Consistency across services:** eventual consistency by default; long-running multi-step business flows use sagas with compensating actions (orchestration or choreography); keep each local step a short ACID transaction.
- **Schema evolution:** messages are public contracts. Prefer additive, backward/forward compatible changes (new optional fields, tolerant readers); explicit version field or schema registry compatibility mode; never repurpose or remove fields without a migration window; consumers ignore unknown fields.
- **Message size and content:** small messages carrying ids/needed facts; avoid secrets/PII or encrypt/minimise; include correlation id, timestamp, type, version, producer.

## Workflow
1. Write down the interaction: who calls/publishes what, expected latency, failure semantics, ordering, volume, ownership of the contract.
2. Choose sync vs async and, if async, the guarantees and idempotency strategy before writing code.
3. Define the contract (schema/OpenAPI/AsyncAPI), versioning and compatibility rule.
4. Implement producer/client with timeouts, auth, error mapping, and correlation id propagation.
5. Implement consumer: validate, idempotent processing, error classification, retry/DLQ, manual vs auto ack as designed, concurrency bounded.
6. Add outbox/inbox if state change + message must be consistent.
7. Add metrics (lag, retries, DLQ depth, latency, error rate), logs and traces.
8. Test with real broker/stub server, including duplicates, failures and restarts.
9. Report guarantees provided and known gaps.

## Implementation guidance
- **HTTP client:** one configured client bean (not per request); explicit timeouts; connection pool limits; map non-2xx to domain exceptions; avoid logging bodies with secrets; use TLS verification; propagate trace headers; authenticate with short-lived credentials from a secret store.
- **Kafka:** set key and partitioning intentionally; producer `acks=all` and idempotent producer for durability; consumer `enable.auto.commit` off (commit after processing) unless justified; bounded `max.poll.records`/`max.poll.interval.ms` aligned with processing time; handle rebalances; `ErrorHandlingDeserializer`; Spring Kafka `DefaultErrorHandler` with backoff and `DeadLetterPublishingRecoverer` (verify class names for the version); retry topics via the framework's non-blocking retry support.
- **RabbitMQ/AMQP:** durable queues/messages and publisher confirms for important data; consumer acknowledgements after successful processing; prefetch tuned; DLX/dead-letter exchanges; bounded listener concurrency; declare topology consistently (`RabbitAdmin`) and avoid redeclaring with conflicting arguments.
- **JMS/cloud brokers:** apply the same principles (acks, visibility timeout/redelivery, DLQs); use the provider's official SDK/Spring integration documentation.
- **Concurrency:** bound consumer threads and in-flight work; apply backpressure; virtual threads do not remove the need to limit downstream concurrency.
- **Observability:** correlation id in headers/MDC; trace context propagated through messages; metrics for consumer lag and processing time; alert on DLQ growth and lag, not on single failures.
- **Local/dev:** broker via Docker Compose or Testcontainers; no shared dev brokers in tests.

## Security and reliability requirements
- Authenticate and authorise producers/consumers (SASL/TLS for Kafka, TLS/users/vhost permissions for RabbitMQ); least-privilege topic/queue ACLs; encrypt in transit; no secrets in messages or logs.
- Treat message content as untrusted input: validate and bound size; safe deserialization (no polymorphic default typing from untrusted data).
- Prevent unbounded retries, unbounded queues/buffers and unbounded concurrency; define retention and DLQ retention.
- Make background consumption recoverable after crashes (offset/ack semantics, idempotent reprocessing).
- Ensure SSRF controls when URLs are user-influenced; allow-list hosts.

## Common anti-patterns
- Assuming exactly-once; non-idempotent consumers with at-least-once delivery.
- Dual writes (DB + broker) with no outbox; publishing before the transaction commits.
- Infinite or immediate retries; blocking retries that stall a partition; retrying non-transient errors.
- No timeouts or default infinite timeouts; creating HTTP clients per call.
- Swallowing consumer exceptions (silent message loss) or auto-acking before processing.
- Breaking schema changes without a compatibility window; leaking internal entity structures as message contracts.
- Introducing Kafka/RabbitMQ/microservices "for scalability" without requirement.
- Treating DLQ as a graveyard with no monitoring or replay.
- Circuit breaker with no fallback decision or no metrics.

## Testing and verification
- Unit-test idempotency logic and error classification.
- Integration tests with the real broker (Testcontainers) for publish/consume, retry, DLQ routing, duplicate delivery, consumer restart mid-processing, poison message, ordering per key.
- HTTP client tests with WireMock/MockWebServer: timeouts, 4xx/5xx, slow responses, malformed bodies, retry/circuit-breaker behaviour.
- Contract tests for message/API schemas (consumer-driven where multiple teams); schema compatibility checks in CI if a registry is used.
- Outbox test: transaction rollback produces no message; commit produces exactly one eventually-published message (at-least-once with dedup downstream).
- Report real command results; state when a broker/container runtime was unavailable.

## Definition of done
Interaction style and guarantees stated; contract defined and versioned; timeouts/retries/DLQ configured and bounded; idempotency and duplicate handling implemented and tested; consistency strategy (outbox/saga) used where needed; security and observability in place; tests executed with real results; no unjustified infrastructure added.

## Related skills
`java-engineering-core`, `java-web-development`, `spring-boot-engineering`, `spring-data-jpa-engineering`, `java-database-engineering`, `java-performance-resilience`, `spring-security-engineering`, `java-testing-quality`, `java-production-deployment`, `java-architecture-design`.

## Official references
- https://spring.io/projects/spring-kafka · https://docs.spring.io/spring-kafka/reference/
- https://spring.io/projects/spring-amqp · https://docs.spring.io/spring-amqp/reference/
- https://docs.spring.io/spring-framework/reference/ (REST clients, JMS, resilience features for the repo's version)
- https://kafka.apache.org/documentation/ · https://www.rabbitmq.com/docs
- Patterns: https://microservices.io/patterns/ (outbox, saga, idempotent consumer)
- https://testcontainers.com/
