---
applyTo: "**/AndroidManifest.xml,**/src/main/res/**,**/app/src/**/*.java,**/app/src/**/*.kt"
---
For Android code: use `java-mobile-development`. Write Java in Java files and idiomatic Kotlin in Kotlin files; do not convert languages or Views to Compose without authorization, and keep Java/Kotlin boundaries safe (nullability annotations, `@JvmStatic`/`@JvmOverloads`, no `suspend`/`Flow` exposed to Java). Never block the main thread, keep state in a ViewModel and persist what must survive process death, set `android:exported` explicitly, use HTTPS only, store tokens with Keystore-backed encryption, and never rely on the client for authorization. Do not bump AGP, SDK, Kotlin or Compose versions as a side effect.
