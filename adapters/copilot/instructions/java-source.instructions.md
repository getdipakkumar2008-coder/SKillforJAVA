---
applyTo: "**/*.java"
---
For Java source changes: follow `java-engineering-core` (discover versions and conventions first) and `java-core-engineering`. Do not use language features above the project's Java release or enable preview features. Keep business rules explicit and testable, handle errors without swallowing causes, close resources, validate input, and keep the diff scoped. Add or update tests and run them; report only observed results. For Spring code also use `spring-boot-engineering`; for persistence `spring-data-jpa-engineering` and `hibernate-orm-engineering`; for security-relevant code `spring-security-engineering`.
