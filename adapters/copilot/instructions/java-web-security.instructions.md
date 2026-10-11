---
applyTo: "**/*Controller.java,**/*SecurityConfig*.java,**/*Security*.java,**/application*.yml,**/application*.yaml,**/application*.properties"
---
For controllers, security configuration and application properties: use `java-web-development`, `spring-security-engineering` and `spring-boot-engineering`. Authenticate and authorize on the server (deny by default, check object-level ownership), validate and bound input, return consistent error bodies without internals, and keep DTOs separate from entities. Do not disable CSRF, CORS, TLS or authorization to make something work. Keep secrets out of properties files and expose only the Actuator endpoints that are needed.
