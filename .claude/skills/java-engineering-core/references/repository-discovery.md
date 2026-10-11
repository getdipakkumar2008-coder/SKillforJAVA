# Repository Discovery

Goal: produce a short repository profile from evidence in the files, before planning or editing.

## 1. Instructions and conventions
Read, if present: `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, `.github/instructions/`, `README*`, `CONTRIBUTING*`, `docs/`, `.editorconfig`, ADRs, and Spec Kit artifacts (`.specify/`, `specs/`, constitution, plan, tasks). Note rules that constrain the task.

## 2. Build system and Java version

| Signal | Where |
|---|---|
| Maven | `pom.xml`, `mvnw`; look at `maven.compiler.release/source/target`, `java.version`, toolchains, parent POM / BOM |
| Gradle | `build.gradle(.kts)`, `settings.gradle(.kts)`, `gradlew`, `gradle/libs.versions.toml`; look at `java { toolchain }`, `sourceCompatibility` |
| Android | `app/build.gradle(.kts)`, `AndroidManifest.xml`, `compileSdk`, `minSdk`, `targetSdk`, `compileOptions` |
| Runtime hints | `.sdkmanrc`, `.tool-versions`, `Dockerfile` base image, CI config |

Prefer the project's wrapper (`./mvnw`, `./gradlew`) over a global install. Record the Java release level. Do not use language features above it.

### Language mix (Java / Kotlin)
- Count `.java` vs `.kt` (and `.kts`) files per module (`git ls-files '*.java' '*.kt' | ...` or a glob).
- Kotlin signals: `kotlin-maven-plugin`, `org.jetbrains.kotlin.*` / `kotlin("jvm")` / `kotlin-android` Gradle plugins, `kotlin-stdlib`, `jvmTarget` / `compilerOptions`, `kapt` or `ksp` blocks, `kotlin-spring` (all-open) and `kotlin-jpa` (no-arg) plugins, Compose compiler plugin and BOM.
- Record: primary language per module, Kotlin version, whether Java and Kotlin share modules, how annotation processing is configured, and which language new code should use (surrounding module, or what the user said).
- Never convert files between languages, or add the Kotlin toolchain to a Java-only module, without authorisation.
- Mixed repos: find the interop conventions already used (nullability annotations, `@JvmStatic`/`@JvmOverloads`, facades) and follow them.

### UI toolkit (mobile)
For Android: XML Views vs Jetpack Compose vs both; `viewBinding`/`dataBinding`; navigation library; DI (Hilt/Dagger/manual). See `java-mobile-development`.

## 3. Application type
Classify as one or more: library; backend API; server-side web (Thymeleaf, Vaadin, JSP); frontend-integrated web (Angular/React alongside Java); Android app; multi-module system. Check module list in the parent POM or `settings.gradle`.

## 4. Frameworks and versions
Read dependencies, not guesses. Identify and record versions of: Spring Boot (BOM or plugin version), Spring Framework, Spring Security, Spring Data, Hibernate, Jakarta vs `javax` namespace, JUnit 4 vs 5, Mockito, Testcontainers, Flyway/Liquibase, messaging clients, Lombok/MapStruct, OpenAPI tooling. Note the `javax.*` vs `jakarta.*` imports in use, because they follow the framework generation.

## 5. Tests and quality checks
- Test layout and naming (`src/test`, `src/integrationTest`, `*IT`, `*Test`).
- Test commands from README/CI: e.g. `./mvnw -q test`, `./mvnw verify`, `./gradlew test`, `./gradlew check`, Android `./gradlew testDebugUnitTest` and `connectedDebugAndroidTest`.
- Formatters and linters: Spotless, Checkstyle, PMD, SpotBugs, Error Prone, Sonar, OWASP dependency-check.
- CI definition (`.github/workflows`, `Jenkinsfile`, `.gitlab-ci.yml`) shows what must pass.

## 6. Architecture and security conventions
- Package layout: by feature or by layer? Hexagonal ports/adapters?
- Error handling pattern (`@ControllerAdvice`, problem details, custom exceptions).
- Auth model: session, JWT resource server, OAuth login, none.
- Configuration approach: profiles, `application.yml`, env vars, secret source.
- Data access and migrations: JPA, JDBC, jOOQ; Flyway/Liquibase location.
- Logging and observability setup.

## 7. Repository profile (output format)

```
Java: <release>  Kotlin: <none | version, where>  Build: <tool + wrapper>  Type: <app type(s)>
UI toolkit (mobile): <Views | Compose | both>  Language for new code: <Java | Kotlin per module>
Frameworks: <name version, ...>
Test cmd: <...>   Quality cmd: <...>
Conventions: <3-6 bullets>
Constraints from instructions: <bullets>
Unknowns: <what could not be determined>
```

If git exists, also check `git status` so you do not trample uncommitted user work.
