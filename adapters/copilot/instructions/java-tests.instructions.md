---
applyTo: "**/src/test/**,**/src/integrationTest/**,**/src/androidTest/**,**/*Test.java,**/*IT.java"
---
For tests: follow `java-testing-quality`. Use the JUnit generation, assertion library and mocking style already in the repository. Cover normal, edge and failure paths and unauthorized/invalid input at trust boundaries; test observable behavior, not implementation details. Use real dependencies (Testcontainers) where persistence or framework semantics matter. Never delete, skip or loosen a failing test to get green, and report which tests were not run and why.
