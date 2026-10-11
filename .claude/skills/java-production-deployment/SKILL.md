---
name: java-production-deployment
description: Make Java services production-ready and deployable - logging, metrics, tracing and correlation ids, Spring Boot Actuator health/readiness/liveness, OpenTelemetry, Docker/OCI images (Dockerfile or Cloud Native Buildpacks), environment-specific configuration, secrets management, CI/CD pipelines, startup/readiness/graceful shutdown, container resource limits, dependency and image scanning, rollback and release verification. Use when containerizing, wiring observability, writing pipelines or preparing a release. Adapt to the project's actual cloud and infrastructure.
---

# Java Production Deployment and Observability

## Purpose
Ship Java services that start predictably, report their health, emit usable telemetry, handle configuration and secrets safely, and can be rolled back.

## Activation conditions
Dockerfile/image work; Kubernetes/ECS/Cloud Run/VM deployment descriptors; CI/CD pipeline changes; Actuator/metrics/tracing/logging setup; environment configuration and secrets; shutdown/readiness issues; release or rollback preparation. Run `java-engineering-core` discovery first and identify the **actual** target platform; do not impose a cloud or tool the project does not use.

## Version awareness (checked 2026-10-11)
- Spring Boot reference (4.1.1 current): container images via Dockerfiles or Cloud Native Buildpacks (`spring-boot:build-image` / `bootBuildImage`); Actuator exposes only `health` over HTTP by default; liveness and readiness probe groups at `/actuator/health/liveness` and `/actuator/health/readiness`; `management.endpoint.health.probes.add-additional-paths=true` serves `/livez` and `/readyz` on the main port; Boot 4 enables probes by default; `shutdown` and `heapdump` endpoints are restricted by default.
- Layered-jar / jarmode extraction command names and image-build options change between Boot versions: read the "Efficient Container Images", "Dockerfiles" and "Cloud Native Buildpacks" pages for the repo's version rather than copying recalled commands.
- Docker: https://docs.docker.com/ · OpenTelemetry: https://opentelemetry.io/docs/ (Java agent/SDK versions and semantic conventions evolve - check current docs).
- Use the Java version and Boot version already in the repo; base-image choice must match the supported Java runtime.

## Required context and inputs
Target platform (Kubernetes, ECS, Cloud Run, VM, PaaS), registry, CI system, environments (dev/test/stage/prod) and promotion rules, secret store, observability stack (Prometheus/Grafana, Datadog, ELK, OTLP backend), traffic pattern and SLOs, database migration timing, rollback policy.

## Repository inspection
1. Existing `Dockerfile`, `.dockerignore`, compose files, Helm/Kustomize/Terraform, CI files (`.github/workflows`, `Jenkinsfile`, `.gitlab-ci.yml`).
2. `application*.yml` profiles, env var usage, secret sourcing.
3. Actuator/metrics/tracing/logging dependencies and config.
4. Resource requests/limits, probes, replicas, shutdown settings.
5. How migrations run (app start vs separate job).
6. Existing scanning (Trivy, Grype, dependency-check, secret scanning).

## Decision rules
- **Image build:** use the project's existing approach. Otherwise Cloud Native Buildpacks for minimal maintenance, or a multi-stage Dockerfile with layered jar extraction for control. Pin base image tags (digest for high assurance), use a maintained minimal JRE image matching the Java release, run as **non-root**, no build tools or secrets in the final image, `.dockerignore` present, one process per container.
- **Configuration:** build once, configure per environment (twelve-factor). Environment variables/config maps/secret mounts; profiles select non-secret behaviour; no environment-specific values baked into the image.
- **Secrets:** from a secret manager or orchestrator secrets, injected at runtime; never in images, repos, build args, logs or `application.yml`; rotation supported (restart or reload strategy documented); least-privilege service identities.
- **Health:** liveness = "process is not wedged" (no external dependencies, to avoid restart storms); readiness = "can serve traffic" (include critical dependencies deliberately); startup probe or generous initial delay for slow starts. Health details hidden from unauthenticated callers.
- **Actuator exposure:** expose `health` (and `info`/`prometheus` etc. only as needed); keep management on a separate port/network or behind authentication; never expose `env`, `heapdump`, `threaddump`, `configprops` publicly (see `spring-security-engineering`).
- **Resource limits:** set container memory/CPU limits; rely on container-aware JVM defaults and set explicit heap percentage (e.g. `-XX:MaxRAMPercentage`) deliberately, leaving room for metaspace/threads/native memory; measure before tuning GC flags (`java-performance-resilience`). JVM options via `JAVA_TOOL_OPTIONS` or the buildpack config.
- **Graceful shutdown:** `server.shutdown=graceful` with `spring.lifecycle.timeout-per-shutdown-phase` less than the orchestrator's termination grace period; stop accepting traffic (readiness down) before draining; make consumers/schedulers stop cleanly.
- **Migrations in deploys:** apply forward-compatible migrations (expand/contract) so old and new versions can run together; run as a separate job or guarded startup step per project convention (`java-database-engineering`).
- **Release strategy:** rolling by default; blue/green or canary where risk justifies; define success metrics and automatic/manual rollback triggers; keep the previous artifact deployable.
- **CI/CD:** pipeline stages = build -> unit tests -> static analysis -> integration tests -> dependency/image scan -> package/image -> deploy to non-prod -> smoke/verification -> promote. Fail the pipeline on failing tests/scans per policy; no `|| true` masking; cache dependencies; reproducible builds with wrappers and pinned tool versions; least-privilege pipeline credentials (prefer short-lived OIDC federation over long-lived keys); protected branches/environments for production.

## Workflow
1. Identify platform and constraints; list what exists vs what is missing.
2. Make the application runnable/observable: config externalised, health probes, graceful shutdown, structured logging.
3. Build the image (or buildpack config); verify it builds, starts non-root and passes health.
4. Add/adjust deployment descriptors (probes, resources, env/secret references, replicas, disruption budgets) in the project's existing tooling.
5. Add/adjust CI/CD stages and scanning.
6. Define release verification (smoke tests, key metrics/dashboards, alerts) and rollback steps.
7. Verify locally as far as possible (image build, container run, probes, shutdown with `docker stop`, scans); document what only the real environment can confirm.
8. Report with assumptions about the target environment.

## Implementation guidance
Build images and pipelines per the decision rules and workflow above; observability implementation:

- **Logging:** SLF4J/Logback (or the repo's choice); structured (JSON) logs to stdout where the platform collects them; include trace/correlation ids (MDC); consistent levels; actionable messages; no secrets/PII/tokens; avoid per-request debug in production; log security events.
- **Metrics:** Micrometer via Actuator; RED/USE signals (rate, errors, duration; saturation of pools/queues/threads); JVM metrics (heap, GC, threads); DB pool metrics; business metrics sparingly; control tag cardinality (no user ids/URLs with ids as tags).
- **Tracing:** OpenTelemetry (Java agent for quick coverage or Micrometer Tracing/OTel SDK integration) with W3C trace context propagation across HTTP and messaging; sampling configured; exporter endpoint via env vars (`OTEL_*`); check the repo's existing choice before adding another.
- **Alerting/SLOs:** alert on symptoms (error rate, latency, saturation, queue lag) with runbook links; do not alert on every log error.
- **Diagnostics:** ability to capture thread/heap dumps securely on demand; JFR enabled only as needed.

## Security and reliability requirements
- Non-root containers, read-only root filesystem where feasible, dropped capabilities, no privileged mode; network policies/security groups restrict ingress/egress.
- TLS in transit (terminate at ingress/mesh or in-app, consistently); verify certificates on outbound calls.
- Scan dependencies (SCA) and images (e.g. Trivy/Grype) in CI; track and patch base images; generate an SBOM if policy requires; secret scanning on commits.
- Sign/verify artifacts where policy requires; immutable tags/digests for deployment.
- Resource limits and autoscaling bounds prevent noisy-neighbour failures; bounded thread/connection pools sized with DB limits.
- Backups and restore tested for stateful dependencies (out of app scope, but documented as an assumption).
- Rollback tested or at least rehearsed; data migrations compatible with rollback.

## Common anti-patterns
- Baking environment config or secrets into images; `latest` tags; running as root; fat images with build tools.
- Liveness probes that check the database (cascading restarts); no readiness probe; probes hitting authenticated endpoints without credentials.
- Exposing all Actuator endpoints publicly; verbose health details to anonymous users.
- JVM heap = container limit (OOM-kill); unbounded thread pools; ignoring container memory in sizing.
- Shutdown timeout longer than the orchestrator's grace period; killing in-flight work.
- Pipelines that ignore test/scan failures; manual production changes outside the pipeline; long-lived cloud keys in CI.
- High-cardinality metric tags; logging secrets; unstructured logs with no correlation id.
- Schema migrations that break the previous version during rolling deploys.
- Introducing Kubernetes/service mesh/new observability stacks the project did not ask for.

## Testing and verification
- Build the image and run it: container starts, non-root user (`id`), health endpoints return expected status, `docker stop` triggers graceful shutdown within the grace period, logs are structured and free of secrets.
- Run image/dependency scans and report findings honestly (severity, fixable or not).
- Validate manifests/pipelines with the platform's tooling (`kubectl --dry-run`, `helm lint`, `terraform validate`, workflow linter) where available.
- Smoke test post-deploy: health, a read endpoint, a write path if safe; check dashboards/alerts; confirm rollback works.
- State precisely what was verified locally vs what requires the target environment; never claim a deployment succeeded unless it was observed.

## Definition of done
Config and secrets externalised; image builds reproducibly and runs non-root; liveness/readiness/shutdown behave correctly; logs/metrics/traces available with correlation; CI/CD stages and scans defined and executed where possible; resource limits set; rollout and rollback described and compatible with migrations; deployment assumptions documented; verification results reported honestly.

## Related skills
`java-engineering-core`, `spring-boot-engineering`, `spring-security-engineering`, `java-database-engineering`, `java-performance-resilience`, `java-testing-quality`, `java-maintenance-troubleshooting`, `java-messaging-integration`.

## Official references
- https://docs.spring.io/spring-boot/reference/packaging/container-images/index.html and `actuator/` and `web/graceful-shutdown.html`
- https://docs.docker.com/ (build best practices, multi-stage builds, security)
- https://opentelemetry.io/docs/ (Java)
- https://micrometer.io/docs
- https://owasp.org/ (Docker/CI-CD/Secrets cheat sheets)
- Platform docs for the project's actual target (Kubernetes, ECS, Cloud Run, etc.)
