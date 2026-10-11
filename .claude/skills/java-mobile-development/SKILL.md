---
name: java-mobile-development
description: Build, change, test and prepare native Android applications written in Java - project and Gradle configuration, Activities/Fragments and lifecycle, UI and event handling, navigation and state (ViewModel/LiveData), main-thread and background work, REST networking, local persistence (Room), offline sync, secure token handling, permissions, accessibility, configuration changes and process death, performance, unit and instrumentation tests, debugging and release preparation. Use for Android projects where Java is the language. Not for Spring/backend code or cross-platform frameworks.
---

# Java Mobile Development (Android)

## Purpose
Make correct, secure, lifecycle-safe changes to a native Android app in Java, following modern Android architecture guidance while respecting the project's language and existing structure.

## Scope boundaries
- **Native Android in Java.** Modern Android guidance is Kotlin- and Compose-first; many projects are mixed. Do **not** convert Java to Kotlin, or Views to Compose, without explicit authorisation. Interoperate with Kotlin/Compose code if the repo already contains it.
- **Not** Spring/server patterns: no Spring Boot layering, `@Service`/`@Transactional` thinking, or server-side persistence idioms in Android UI code.
- **Cross-platform requests** (Flutter, React Native, KMP, .NET MAUI, etc.): identify the framework first and use or create a framework-specific skill; this skill does not apply.
- The Android client is **untrusted**: it never holds server credentials or enforces authorization. The backend does (`spring-security-engineering`, `java-web-development`).

## Activation conditions
`AndroidManifest.xml`, `build.gradle(.kts)` with `com.android.application`/`library`, or a request for an Android feature, fix, test, build problem or release step. Run `java-engineering-core` discovery first and record `compileSdk`, `minSdk`, `targetSdk`, AGP/Gradle versions, Java level, UI toolkit (Views/Compose), DI, and persistence library.

## Version awareness (checked 2026-10-11)
- Android Developers architecture guide: recommends a UI layer (UI elements + state holders such as `ViewModel`), an optional domain layer (use cases), and a data layer (repositories + data sources); **unidirectional data flow**; a **single source of truth**; offline-first with a persistent database as the source of truth; DI with Hilt; coroutines/Flow listed as modern concurrency. The guide's examples are Compose/Kotlin-oriented; apply the principles in Java with `ViewModel`, `LiveData`/observers, `Executor`s, and callbacks or reactive libraries already in the repo.
- Android Gradle Plugin 8.x requires **JDK 17** to run Gradle (per developer.android.com/build/jdks); check the AGP compatibility table for the repo's AGP. Set `compileOptions` `sourceCompatibility`/`targetCompatibility` explicitly (matching) and specify a Java toolchain. Java language features are available at compile time; library APIs depend on `compileSdk` and the device API level; newer Java APIs on older devices need **core library desugaring** if on its supported list.
- Java API levels per the docs: Android 13 (API 33) -> Java 11 core libraries; Android 14 (API 34) -> Java 17.
- Do not change AGP, Gradle, `compileSdk` or `targetSdk` as a side effect; `targetSdk` bumps carry platform behaviour changes and store-policy deadlines (see developer.android.com and Play Console requirements).

## Required context
`minSdk`/`targetSdk`/`compileSdk`; Java level; UI toolkit; architecture pattern in use (MVVM/MVP/none); navigation approach; DI; networking (Retrofit/OkHttp, `HttpURLConnection`, Volley); persistence (Room, SQLite, DataStore, SharedPreferences); auth flow with the backend; backend API contract; build variants and signing setup.

## Repository inspection
1. `settings.gradle`, `build.gradle(.kts)`, version catalog, product flavors/build types, `proguard-rules.pro`, signing config handling (secrets out of VCS).
2. `AndroidManifest.xml`: components, `exported` flags, permissions, intent filters, network security config, backup rules.
3. Package layout: UI (activities/fragments/adapters), ViewModels, repositories, data sources, models, DI modules.
4. Existing state/threading approach (Executors, RxJava, coroutines via Java interop, `LiveData`).
5. Resources: strings, layouts, themes, accessibility attributes, localisation.
6. Tests: `src/test` (JVM), `src/androidTest` (instrumentation), CI commands.

## Decision rules
- **Architecture:** follow the repo's pattern; for new code prefer `Activity/Fragment` (UI only) -> `ViewModel` (state holder) -> repository -> data sources (remote/local). State flows down, events flow up; the UI observes immutable state. Introduce a domain/use-case layer only for reused or complex logic.
- **Single source of truth:** for offline-capable data, the local database is the source of truth; network refreshes write to it; UI observes it.
- **Don't keep data in components:** Activities/Fragments/Services can be destroyed anytime; hold state in `ViewModel` (survives configuration change) and persist anything that must survive **process death** (`SavedStateHandle`, `onSaveInstanceState`, database/DataStore).
- **Threading:** never block the main thread (no network, disk, or heavy CPU); use background executors/`WorkManager`; deliver results to the UI via `LiveData`/main-thread handlers; avoid leaking Activities/Contexts into long-lived tasks (use application context, lifecycle-aware observers, cancel on clear).
- **Background work:** `WorkManager` for deferrable, guaranteed work; foreground services only for user-visible ongoing work with the required type/permissions; respect Doze/background limits; avoid polling.
- **Networking:** HTTPS only; a single configured client with timeouts; map errors to UI states (loading, content, empty, error, offline); never log tokens/bodies with secrets; use the backend's versioned API and tolerate unknown fields.
- **Persistence:** Room for structured data (typed DAOs, migrations with tests, schema export); DataStore/SharedPreferences for small settings only; no secrets in plain preferences or databases.
- **Offline and sync:** queue writes locally with idempotency keys; sync via `WorkManager` with backoff; define conflict resolution (last-write-wins, server wins, merge) with the backend contract; show sync state; handle partial failure.
- **Navigation:** the repo's mechanism (Navigation component, FragmentManager, intents); pass ids not large objects; handle deep links defensively (validate inputs).
- **Compatibility:** respect `minSdk`; guard newer APIs with `Build.VERSION.SDK_INT` checks or AndroidX compat/desugaring; test on min and target API levels where possible.
- **UI:** support configuration changes without data loss; use resources for strings/dimensions/colours (no hardcoded text); responsive layouts (ConstraintLayout/size-class-aware resources), dark theme, RTL, font scaling.
- **Accessibility:** `contentDescription` for images/icons, labels for inputs, minimum touch targets (48dp), sufficient contrast, logical focus order, no information by colour alone; test with TalkBack.

## Workflow
1. Profile the app (versions, architecture, toolkit) and the requested feature's contract with the backend.
2. Plan state and data flow: UI states, events, data sources, offline behaviour, permissions, lifecycle/process-death handling.
3. Implement from the data layer up (model, remote/local source, repository), then ViewModel, then UI; keep logic out of Activities/Fragments.
4. Add accessibility, localisation, error/empty/loading states.
5. Handle permissions and security (below).
6. Test: JVM unit tests for ViewModels/repositories/mappers; instrumentation/UI tests for flows needing the framework; run lint.
7. Build debug and release variants; check R8/ProGuard rules; run on emulator/device if available.
8. Report with what ran on which API level/device and what could not be run.

## Implementation guidance
- Use AndroidX libraries (`androidx.lifecycle`, `androidx.room`, `androidx.work`, `androidx.navigation`); keep versions aligned via the repo's catalog/BOM.
- Lifecycle-aware observation (`getViewLifecycleOwner()` in Fragments); remove listeners/callbacks; avoid static references to Views/Contexts; use `ViewBinding` per repo convention.
- One-off events (navigation, toasts) must not re-fire on rotation: model as consumed events or state per repo convention.
- Immutable models for UI state; mappers between network DTOs, database entities and UI models.
- `ProGuard/R8`: keep rules for reflection-based libraries (JSON, Retrofit models) and test the release build; do not disable minification to hide a crash without diagnosing.
- Dependency injection: Hilt/Dagger/manual per repo; no service locators in new code.
- Logging: a wrapper or Timber-style tree; no PII/tokens; reduced in release.
- Strings and plurals via resources; dates/times via `java.time` (with desugaring if `minSdk` requires).

## Security and privacy requirements (per developer.android.com security guidance)
- **No server secrets in the app.** Anything in the APK can be extracted; API keys are not secrets - restrict them server-side by package/signature; keep keys out of source control (e.g. via a secrets Gradle plugin).
- **Tokens:** authenticate with the backend via OAuth 2.0 / OIDC (authorization code + PKCE through the system browser/Custom Tabs, or Credential Manager for passkeys/federated sign-in); store only short-lived tokens, encrypted with Android Keystore-backed keys (e.g. Tink or `EncryptedFile`-style wrappers - verify the maintained library); do not store passwords; clear on logout; support refresh/rotation.
- **Authorization is server-side.** UI hiding is cosmetic; never rely on client checks or client-held roles; handle 401/403 properly (re-auth vs access denied).
- **Network:** HTTPS everywhere; Network Security Config (no cleartext in release; certificate pinning only with a rotation plan); validate hostnames; never disable certificate validation.
- **Storage:** internal storage by default; external storage is untrusted and world-readable - no sensitive data; no `MODE_WORLD_*`; parameterised queries in `ContentProvider`/SQLite; consider backup/auto-backup exclusion for sensitive data.
- **Permissions:** request the minimum, at point of use, with rationale and graceful denial; prefer permission-free alternatives (photo picker, scoped storage, UUIDs instead of device identifiers).
- **Components:** set `android:exported` explicitly; `false` unless another app needs it; protect with permissions; explicit intents; validate all intent extras and deep link data; avoid sensitive data in broadcasts.
- **WebView:** JavaScript off unless needed; `addJavascriptInterface` only with trusted bundled content; restrict navigation to allowed origins; clear sensitive cache.
- **Crypto:** vetted libraries and modes (AES-GCM etc.), `SecureRandom`; no custom crypto.
- **Privacy:** minimise collected data; no PII in logs/analytics; honour consent and deletion requirements; update the Play Data safety declarations when behaviour changes.
- **Integrity (when required):** Play Integrity API for sensitive backends; the *server* verifies the verdict.
- **Release:** signing keys and keystore passwords outside VCS and CI logs; enable R8; strip debug flags; `debuggable=false`.

## Common anti-patterns
- Blocking the main thread; `AsyncTask` (deprecated) or raw `Thread` for new code; leaking Activity/Context into singletons, callbacks, or static fields.
- Holding state only in Activity/Fragment fields (lost on rotation/process death); ignoring process-death testing.
- Business/authorization logic in the client; secrets, admin keys or backend credentials in code/resources/BuildConfig.
- Storing tokens or PII in plain SharedPreferences/SQLite/logs; enabling cleartext traffic or trusting all certificates.
- Exported components with intent filters by accident; implicit intents for internal services; unvalidated deep links.
- Requesting broad permissions up front; polling in the background; wake locks without need.
- Converting to Kotlin/Compose or bumping SDK/AGP versions as a side effect; mixing `javax`-server idioms into the app.
- Catching and ignoring errors; no loading/error/offline states; hardcoded strings; ignoring accessibility and font scaling.
- Disabling R8/lint to get a green build; shipping untested release builds.

## Testing and verification
- **JVM unit tests** (`./gradlew testDebugUnitTest`): ViewModels (with `InstantTaskExecutorRule`/executors replaced), repositories, mappers, validators, sync logic; Mockito per repo convention; Robolectric only when framework classes are needed and it is already used.
- **Instrumentation tests** (`./gradlew connectedDebugAndroidTest`, needs an emulator/device): Espresso/AndroidX Test for UI flows, Room DAOs and migrations (`MigrationTestHelper`), permissions, lifecycle/rotation, process-death restoration; Compose test APIs if Compose exists.
- **Static checks:** `./gradlew lint` (or `lintDebug`), configured formatters/static analysis; accessibility checks (Espresso accessibility checks, manual TalkBack).
- **Network behaviour:** MockWebServer for API contract, error and timeout cases; verify behaviour offline and on slow networks.
- **Release check:** `./gradlew assembleRelease` (or `bundleRelease`) with R8; smoke-test the release build; verify the manifest merge and permissions (`aapt`/Studio APK analyzer); check size and startup where relevant.
- Report exactly which commands ran, on which API level/emulator, and which tests could not run (no emulator, no signing keys).

## Release preparation
Version code/name bump per repo convention; changelog; signing via secure config; R8 mapping file archived for crash deobfuscation; verify `targetSdk` meets store requirements; update store listing, Data safety and permission declarations; staged rollout and crash/ANR monitoring plan; keep backward compatibility with the backend API versions still in the wild (old app versions persist).

## Definition of done
Feature works across lifecycle events (rotation, background/foreground, process death) and API levels in scope; no main-thread blocking; UI states cover loading/empty/error/offline; accessibility and localisation handled; permissions minimal and justified; no secrets or sensitive data stored insecurely; backend authorization assumed and verified server-side; unit and (where relevant) instrumentation tests plus lint executed with real results reported; release build verified or limitation stated; no unrequested language/toolkit/SDK changes.

## Related skills
`java-engineering-core`, `java-core-engineering`, `java-web-development` and `spring-security-engineering` (the backend side of the contract), `java-testing-quality`, `java-architecture-design`, `java-messaging-integration` (HTTP client resilience), `java-maintenance-troubleshooting` (Android build/runtime problems), `java-spec-driven-development`.

## Official references
- https://developer.android.com/ · architecture: https://developer.android.com/topic/architecture · offline-first guidance linked from the architecture pages
- Security checklist: https://developer.android.com/privacy-and-security/security-tips (the general landing page `.../privacy-and-security` returned 404 when checked; use the sub-pages)
- Java/JDK support for builds: https://developer.android.com/build/jdks
- Testing: https://developer.android.com/training/testing · Accessibility: https://developer.android.com/guide/topics/ui/accessibility
- Background work: https://developer.android.com/develop/background-work
- Release: https://developer.android.com/studio/publish
- OWASP MASVS/MASTG: https://mas.owasp.org/
