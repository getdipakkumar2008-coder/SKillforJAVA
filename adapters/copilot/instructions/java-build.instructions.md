---
applyTo: "**/pom.xml,**/build.gradle,**/build.gradle.kts,**/settings.gradle,**/settings.gradle.kts,**/gradle/libs.versions.toml,**/Dockerfile"
---
For build and packaging files: use `java-maintenance-troubleshooting` for dependency or build problems and upgrades, `spring-boot-engineering` for Boot starters and plugins, and `java-production-deployment` for Docker, CI and release. Align versions through the BOM or version catalog, do not add version overrides that fight it, and do not upgrade Java, Spring Boot, Kotlin, Compose or Android Gradle Plugin versions as a side effect. Use the project's wrapper (`./mvnw`, `./gradlew`). Never put secrets in build files or images.
