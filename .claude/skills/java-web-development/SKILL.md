---
name: java-web-development
description: Design and implement Java web layers - REST APIs, server-side rendered pages (Thymeleaf, Vaadin), and frontend/backend integration - covering HTTP semantics, resource design, versioning, request validation, ProblemDetail error handling, DTO mapping, pagination/filtering/sorting, OpenAPI, file upload/download, session vs token auth models, CORS/CSRF, and API compatibility and contract testing. Use for controllers, endpoints, API contracts and web client integration. Pair with spring-boot-engineering and spring-security-engineering.
---

# Java Web Development

## Purpose
Build web-facing behaviour that is correct at the HTTP level, consistent with the repository's API style, and safe by default.

## Activation conditions
Adding or changing endpoints, controllers, views, request/response models, error responses, API docs, file transfer, CORS/CSRF settings, or integrating a frontend. Run `java-engineering-core` discovery first; identify the **kind** of web app below.

## Classify the application first
| Kind | Traits | Implications |
|---|---|---|
| Backend-only API | JSON over HTTP, consumed by other services/mobile | Stateless, token auth, no CSRF for pure token APIs, contract stability |
| Server-side rendered | Thymeleaf/JSP/Vaadin, sessions + forms | Session cookies, CSRF protection required, template escaping, redirect-after-post |
| Frontend-integrated | Angular/React/etc. SPA + Java API | Follow the existing frontend conventions; decide CORS vs same-origin proxy; auth model must match |
| Mobile-consumed API | Android/iOS clients | Server enforces authorization; versioned, backward-compatible contract |

## Version awareness (checked 2026-10-11)
- Spring Framework reference lists **7.0.9** stable (also 6.2.19); Boot 4 uses Spring Framework 7, Boot 3.x uses 6.x. Spring Framework 7 documents first-class **API versioning** support for MVC and WebFlux (`web/webmvc-versioning.html`) and `RestClient`/HTTP service clients. Only use what the repo's Framework version has; verify at https://docs.spring.io/spring-framework/reference/web.html.
- Boot 4 uses Jackson 3 (`tools.jackson`) by default; Boot 3 uses Jackson 2 (`com.fasterxml.jackson`). Match the repo.
- Servlet/Spring MVC vs reactive WebFlux: follow the repo; do not mix without need.
- Thymeleaf: https://www.thymeleaf.org/documentation.html · Vaadin: https://vaadin.com/docs.

## Required context
Web stack (MVC/WebFlux/Vaadin/Thymeleaf), API style and error format, auth model, existing DTO/mapping approach (MapStruct, manual), OpenAPI tooling, client consumers and compatibility promises.

## Repository inspection
1. Controller packages, naming, URL conventions, versioning scheme.
2. Error handling (`@RestControllerAdvice`, `ProblemDetail`, custom error DTO).
3. Validation approach (`@Valid`, groups, custom validators).
4. Serialization config (Jackson modules/properties), date format, null handling.
5. Security config affecting the endpoint (CSRF, CORS, authorization rules).
6. OpenAPI generation (springdoc, spec-first) and API tests/contracts.
7. Frontend project (if any), how it calls the API (proxy, base URL, auth).

## Decision rules
- **Resources and verbs:** nouns for resources, plural collections; `GET` safe/idempotent, `PUT` idempotent replace, `PATCH` partial, `POST` create/actions, `DELETE` idempotent. Do not tunnel mutations through `GET`.
- **Status codes:** `200/201 (+Location)/204`, `400` malformed or validation, `401` unauthenticated, `403` forbidden, `404` missing (or hide existence deliberately), `409` conflict (incl. optimistic lock), `415/406` media-type issues, `422` only if the repo uses it, `429` rate limits, `5xx` server faults. Consistent with existing choices.
- **Errors:** one error format app-wide. RFC 9457 `ProblemDetail` where the project/framework version supports it; include a stable machine-readable code, no stack traces, internal class names, SQL or secrets.
- **DTOs:** separate request/response models from entities and persistence types; records are good DTOs on Java 16+; map explicitly; never bind request bodies directly to entities (mass assignment).
- **Validation:** Jakarta Bean Validation at the boundary (`@Valid`, `@Validated`); bound sizes (strings, collections, page size, upload size); validate path/query params; business-rule validation in the service layer.
- **Pagination/sort/filter:** bounded `page size` with a default and max; stable sort with tie-breaker; allow-list sortable/filterable fields; return pagination metadata in the repo's format.
- **Versioning:** follow the existing scheme (URL, header, media type, or framework API versioning); additive changes are non-breaking; removing/renaming fields, changing types/semantics is breaking - requires a new version and deprecation path.
- **Caching:** use `ETag`/`Cache-Control` deliberately; never cache authenticated or personalised responses publicly.
- **Idempotency:** for retried `POST`s that create/charge, support an `Idempotency-Key` (see `java-messaging-integration`).
- **CORS:** configure explicit allowed origins/methods/headers for browser clients on a different origin; never `*` with credentials; prefer same-origin/proxy where possible. CORS is a browser rule, not authorization.
- **CSRF:** required for cookie/session-authenticated browser flows; generally not needed for stateless APIs using `Authorization` headers - decide from the actual architecture (`spring-security-engineering`), do not disable it by reflex.
- **Auth model:** session cookie (SSR, `HttpOnly`, `Secure`, `SameSite`) vs bearer token (JWT/opaque via OAuth2 resource server). Authorization decisions are made on the server per request.
- **Sync vs reactive, MVC vs WebFlux:** keep the repo's choice; blocking calls inside reactive pipelines are bugs.

## Workflow
1. Define the contract first: path, method, request/response schema, status codes, error cases, auth requirement (write or update the OpenAPI/spec if the project is spec-first).
2. Add DTOs and validation constraints.
3. Implement a thin controller: validate, authorize (declaratively), call a service, map the result.
4. Handle errors centrally; add specific exceptions only where a distinct response is needed.
5. Update docs/OpenAPI and any client code/contract tests.
6. Test with MockMvc/WebTestClient and integration tests (`java-testing-quality`): success, validation failure, 401/403, 404, conflict, large/malformed input.
7. Verify compatibility: existing clients and contract tests still pass; breaking changes are explicit.
8. Report.

## Implementation guidance
- **Controllers:** `@RestController`, constructor injection, no business logic, no entity exposure, return `ResponseEntity` when headers/status vary.
- **Serialization:** explicit date/time (ISO-8601, UTC instants), enums as strings, ignore unknown properties only if the contract requires leniency; avoid exposing internal ids if the project uses public ids.
- **File upload:** limit size (`spring.servlet.multipart.max-file-size` / `max-request-size`), validate content type by inspecting content not just the header, generate server-side file names, store outside the web root, scan if required, stream large files; never trust the client filename (path traversal).
- **File download:** set `Content-Disposition` safely, correct `Content-Type`, stream with `Resource`/`StreamingResponseBody`, enforce authorization per file.
- **Server-side rendering:** let the template engine escape output (use unescaped output only for sanitized content), redirect after successful POST, keep model objects as view models not entities, include the CSRF token in forms.
- **OpenAPI:** keep the spec generated from or checked against code; document auth, error schemas and examples; do not hand-edit generated output.
- **HTTP clients (outbound):** `RestClient`/`WebClient`/`@HttpExchange` interface with explicit timeouts and error mapping; see `java-messaging-integration`.
- **Frontend integration:** reuse the frontend's existing conventions (routing, state, API client generation); do not scaffold a new frontend architecture; keep API contract changes coordinated and versioned.
- **Headers:** security headers (`X-Content-Type-Options`, HSTS, frame options/CSP) belong with the security configuration.

## Security and reliability requirements
- Authorize every non-public endpoint on the server; check object-level ownership (prevent IDOR/BOLA), not only roles.
- Validate and bound all input; encode output; parameterised data access; reject unexpected content types.
- Do not return sensitive fields; separate public vs internal DTOs; sanitize error messages.
- Timeouts, request size limits, and rate limiting (gateway or filter) for abusive clients; avoid unbounded streaming/response sizes.
- Secure cookies for sessions; no tokens in URLs; no secrets in client-delivered code or API responses.
- Consider OWASP API Security Top 10 and OWASP Top 10 for the change.

## Common anti-patterns
- Returning entities directly; binding requests to entities.
- Business logic in controllers; catching exceptions per controller instead of centrally.
- `200 OK` with an error body; inconsistent error formats; leaking stack traces.
- Unbounded `findAll` endpoints; client-controlled sort fields without allow-list.
- Disabling CSRF/CORS checks or using `*` origins to "make the frontend work".
- Breaking an API contract silently; changing semantics without a version.
- Trusting client-side checks or mobile-app logic for authorization.
- Trusting upload filenames/content types; serving uploads from a executable/static web root.
- Mixing blocking calls into WebFlux handlers; creating HTTP clients per request.

## Testing and verification
- `@WebMvcTest`/`MockMvc` (or `WebTestClient`) for mapping, validation, error bodies, content negotiation, headers and status codes.
- Security tests for 401/403 and ownership; CSRF presence for session-based forms.
- Contract tests (Spring Cloud Contract/Pact) or OpenAPI diff checks when consumers exist; verify existing contract tests still pass.
- Upload/download tests: oversize, wrong type, traversal filename, unauthorised access.
- Run the module build and, if practical, start the app and exercise the endpoint (`curl`) - report what was actually run.

## Definition of done
Contract defined and documented; correct status codes and consistent errors; input validated and bounded; authorization and object-level checks enforced server-side; DTO boundaries respected; compatibility preserved or versioned; tests (including negative and security cases) executed with real results; no CSRF/CORS/security weakening introduced.

## Related skills
`java-engineering-core`, `spring-boot-engineering`, `spring-security-engineering`, `java-testing-quality`, `java-messaging-integration`, `java-architecture-design`, `java-mobile-development`.

## Official references
- https://docs.spring.io/spring-framework/reference/web.html (MVC, error responses, validation, CORS, versioning, REST clients)
- https://docs.spring.io/spring-boot/reference/
- RFC 9110 (HTTP semantics) https://www.rfc-editor.org/rfc/rfc9110 · RFC 9457 (Problem Details) https://www.rfc-editor.org/rfc/rfc9457
- OpenAPI: https://spec.openapis.org/oas/latest.html
- OWASP: https://owasp.org/ (Top 10, API Security Top 10, Cheat Sheet Series)
- https://www.thymeleaf.org/documentation.html · https://vaadin.com/docs
