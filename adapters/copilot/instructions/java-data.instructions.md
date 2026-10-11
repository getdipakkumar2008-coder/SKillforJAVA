---
applyTo: "**/db/migration/**,**/db/changelog/**,**/resources/db/**,**/*Repository.java,**/*Entity.java"
---
For persistence and schema work: use `spring-data-jpa-engineering`, `hibernate-orm-engineering` and `java-database-engineering`. Schema changes go through versioned migrations; never edit an applied migration and never rely on `ddl-auto=update` outside throwaway environments. Keep associations lazy, avoid exposing entities from the API, use parameterized queries, bound result sets, put transactions at the service layer, and make migrations compatible with rolling deploys. Test against the real database engine.
