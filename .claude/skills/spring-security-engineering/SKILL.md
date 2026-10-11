---
name: spring-security-engineering
description: Configure, review and test application security in Spring apps - SecurityFilterChain, authentication and authorization, OAuth 2.0 / OpenID Connect login, JWT and opaque-token resource servers, role/scope/permission rules, method security, sessions, CORS, CSRF, password storage, secure headers and cookies, actuator/management endpoint protection, audit logging, and security tests. Use for any change touching login, tokens, access rules or secrets, and when reviewing a Java service for security. Default is least privilege and deny-by-default.
---

# Spring Security Engineering

## Purpose
Make authentication and authorization correct, minimal and verifiable, enforced on trusted server boundaries. Never trade security for convenience.

## Activation conditions
Adding/changing authentication, authorization rules, token validation, login flows, session or CORS/CSRF behaviour, password handling, secret handling, management endpoint exposure; reviewing security; security test failures (401/403/CSRF/CORS). Run `java-engineering-core` discovery first.

## Version awareness (checked 2026-10-11)
- Spring Security reference lists **7.1.1** stable (also 7.0.7 and 6.5.11); 7.2.0-M2 preview. Spring Boot 4 pairs with Spring Security 7; Boot 3.x with 6.x. Use the version in the repo.
- Official 7.0 migration guide: upgrade first to the latest 6.5.x and apply its opt-in preparation steps; Jackson 2 -> Jackson 3 changes for Security's serialization modules (`SecurityJacksonModules`); authorization-server module defaults to Jackson 3. Servlet-specific breaking changes are on the Servlet migration page - read it before an upgrade (`java-maintenance-troubleshooting`); do not guess them.
- Idioms stable across 6.x/7.x: `SecurityFilterChain` beans, lambda DSL, `authorizeHttpRequests`, `@EnableMethodSecurity`. `WebSecurityConfigurerAdapter` and `authorizeRequests` are legacy - do not introduce them.
- Reference pages: Servlet > OAuth2 Resource Server (JWT, Opaque Token, DPoP), OAuth2 Log In, Authorization Architecture / Authorize HTTP Requests, Method Security, CSRF, CORS, Session Management, Password Storage, Testing. https://docs.spring.io/spring-security/reference/

## Required context and inputs
Architecture (SSR with sessions vs stateless API vs SPA vs mobile client), identity provider (Keycloak, Entra ID, Okta, Auth0, in-house), token format and issuer, required roles/scopes/permissions model, tenancy, existing `SecurityFilterChain`s, Spring Security + Boot versions, current test setup.

## Repository inspection
1. All `SecurityFilterChain` beans, their order and `securityMatcher`s; custom filters.
2. `spring.security.*` and `spring.security.oauth2.*` properties; issuer/JWK URIs; where secrets come from.
3. How authorities are mapped (scope -> authority, claim -> role); custom `JwtAuthenticationConverter`.
4. Method security annotations in use; where ownership checks happen.
5. CORS/CSRF settings; session creation policy; cookie flags.
6. Actuator exposure/security; Swagger/OpenAPI exposure.
7. Existing security tests and test helpers.

## Decision rules
- **Deny by default:** the last rule is `anyRequest().authenticated()` (or `denyAll()` for APIs with an explicit allow-list). Public endpoints are listed explicitly and minimal.
- **Model by architecture:**
  - Stateless API behind an IdP: **OAuth2 resource server**; sessions `STATELESS`; CSRF usually not needed for bearer-only APIs, but never disable it for cookie-authenticated flows.
  - Server-rendered app: form login or **OAuth2/OIDC login** with sessions; CSRF **on**; secure cookies.
  - SPA: prefer backend-for-frontend / authorization code + PKCE; avoid storing long-lived tokens in browser storage; CORS only for needed origins.
  - Mobile client: authorization code + PKCE via system browser; server still authorizes every request.
- **JWT vs opaque:** JWT when local validation is wanted (validate signature via issuer/JWK Set, `iss`, `exp`, `nbf`, and audience `aud` where applicable); opaque with introspection when immediate revocation matters. Never accept unsigned tokens or trust claims without verification; never decode-without-verify.
- **Authorization:** coarse rules in the filter chain by path/method; fine-grained and ownership checks in method security (`@PreAuthorize`) or service logic. Enforce **object-level** ownership (no IDOR) - roles alone are not enough. Map scopes/roles deliberately (`SCOPE_` vs `ROLE_` prefixes).
- **Passwords:** if the app stores them, use `DelegatingPasswordEncoder`/`PasswordEncoder` (bcrypt, Argon2, scrypt, or PBKDF2 per policy); never plain/MD5/SHA-1; prefer delegating to an IdP.
- **CORS:** configure via Spring Security's `CorsConfigurationSource` (so it applies before security filters); explicit origins/methods/headers; no `*` with credentials. CORS is not an access control.
- **CSRF:** keep enabled for session/cookie auth; for SPAs use the cookie token repository pattern per the reference; disable only for provably stateless bearer-token endpoints, scoped to those paths, with a comment.
- **Sessions:** fixation protection on (default), timeouts, concurrent-session limits if required, `HttpOnly`, `Secure`, `SameSite` cookies; invalidate and clear cookies on logout; OIDC logout per IdP.
- **Method security:** enable `@EnableMethodSecurity`; put checks on service methods, not only controllers; remember proxies (self-invocation bypasses).
- **Management endpoints:** expose minimum Actuator endpoints; require authentication/role (or separate port/network); never expose `env`, `heapdump`, `configprops`, `threaddump` publicly. Health probes for orchestrators can be unauthenticated only where intentionally scoped.
- **Multiple filter chains:** order explicitly with `@Order` and `securityMatcher`; ensure no request falls to an unintended permissive chain.

## Workflow
1. Identify architecture and trust boundaries; list endpoints and who may call them (access matrix).
2. Configure/adjust the `SecurityFilterChain` with the most restrictive rules that meet the matrix.
3. Configure token validation or login against the IdP using properties (issuer-uri) rather than hand-rolled code; add custom authority mapping only as needed.
4. Add method/object-level authorization for resources owned by users/tenants.
5. Configure CORS, CSRF, sessions, headers deliberately for this architecture.
6. Add audit logging for authentication and access-denied events (no secrets/tokens in logs).
7. Write security tests (below) and run them; also run the app and probe key endpoints without credentials if practical.
8. Report the access matrix, assumptions, and what was verified.

## Implementation guidance
- Configuration shape (verify against the repo's version): one `@Configuration @EnableWebSecurity` class exposing `SecurityFilterChain` using `http.authorizeHttpRequests(...)`, `http.oauth2ResourceServer(o -> o.jwt(...))`, `http.sessionManagement(...)`, `http.csrf(...)`, `http.cors(...)`.
- Prefer `spring.security.oauth2.resourceserver.jwt.issuer-uri` (discovery + JWK) or `jwk-set-uri` plus an audience validator. Set clock-skew deliberately; cache JWKs per defaults.
- `JwtAuthenticationConverter` maps claims to `GrantedAuthority`s; keep mapping in one place and unit-test it.
- Provide `PasswordEncoder` and `UserDetailsService`/IdP integration; no default generated users in production.
- Secure headers: keep Spring Security defaults (no-sniff, frame options, HSTS on HTTPS, cache control for sensitive pages); add CSP deliberately for SSR apps.
- Handle `AuthenticationEntryPoint` (401) and `AccessDeniedHandler` (403) so API clients get consistent `ProblemDetail`/JSON without leaking details.
- Secrets/keys: from environment or a secret manager; rotate; never in source, tests, logs, images or client code. Use `SecureRandom` and vetted libraries - no custom crypto.
- Input validation and injection prevention are part of security: Bean Validation at boundaries, parameterised queries, output encoding in templates, safe deserialization, SSRF controls on outbound URLs derived from user input.
- Rate limiting/brute-force protection for login and token endpoints at gateway or filter level; account lockout/backoff where applicable.

## Security and reliability requirements
- Least privilege for users, service accounts, DB credentials and tokens' scopes.
- Authorization on the server for every request; the client (browser/mobile) is never trusted.
- Fail closed: misconfiguration or IdP unavailability must deny, not allow; handle JWK/introspection timeouts with bounded timeouts and clear errors.
- Do not disable CSRF/CORS/authorization/TLS verification, add `permitAll()` broadly, or add test-only backdoors to make a test or demo pass.
- Log security events (login success/failure, access denied, privilege changes) with correlation ids; never log credentials, tokens, full PII.
- Protect against the OWASP Top 10 and OWASP API Security Top 10 as relevant (https://owasp.org/ - check the current edition).

## Common anti-patterns
- `anyRequest().permitAll()`; broad `permitAll` on `/**` or on actuator/swagger in production.
- Disabling CSRF globally; `*` CORS with credentials; relying on CORS for protection.
- Roles-only checks with no ownership checks (IDOR/BOLA); authorization only in the UI or mobile app.
- Parsing JWTs manually or skipping signature/issuer/audience/expiry validation; long-lived tokens in local storage.
- Hardcoded secrets/keys/test credentials; secrets in `application.yml`.
- Custom crypto/password hashing; unsalted or fast hashes.
- Using legacy `WebSecurityConfigurerAdapter`/`authorizeRequests`; mixed generations of configuration.
- Method security on a private/self-invoked method; relying on `@Secured` without enabling it.
- Returning detailed auth errors that enable enumeration; logging tokens.
- Tests that pass by setting `@AutoConfigureMockMvc(addFilters = false)` or mocking security out entirely when the behaviour under test is security.

## Testing and verification
- Spring Security test support: `@WithMockUser`, `SecurityMockMvcRequestPostProcessors` (`jwt()`, `opaqueToken()`, `csrf()`), `@WithUserDetails`; method-security tests.
- Test matrix per endpoint: no credentials (401), valid but insufficient authority (403), valid and owns resource (2xx), valid but not owner (403/404), invalid/expired/wrong-issuer/wrong-audience token (401), CSRF missing on state-changing session requests (403), CORS preflight from allowed vs disallowed origin.
- Unit-test the authority/claims converter and custom validators.
- Integration test with a real IdP container (e.g. Keycloak via Testcontainers) or mock JWKS when token validation wiring matters.
- Dependency/vulnerability scanning (OWASP dependency-check / SCA tool in CI) and secret scanning if configured.
- Report what was executed and what was only reviewed manually.

## Definition of done
Access matrix implemented and tested including negative cases; deny-by-default in place; token validation/login configured through supported mechanisms; object-level authorization enforced; CORS/CSRF/session/header choices justified for this architecture; no secrets in code/logs; management endpoints protected; security tests executed with real results; no controls disabled to pass tests.

## Related skills
`java-engineering-core`, `spring-boot-engineering`, `java-web-development`, `java-testing-quality`, `java-mobile-development` (client side), `java-production-deployment` (secrets, TLS), `java-ai-integration` (tool authorization), `java-maintenance-troubleshooting` (security config failures, upgrades).

## Official references
- https://spring.io/projects/spring-security and https://docs.spring.io/spring-security/reference/
- Migration: https://docs.spring.io/spring-security/reference/migration/index.html
- OWASP: https://owasp.org/ (Top 10, ASVS, Cheat Sheet Series) · OAuth 2.0 / OIDC specs (RFC 6749, 7636 PKCE, OpenID Connect Core)
