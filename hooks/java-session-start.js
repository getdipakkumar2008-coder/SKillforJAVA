#!/usr/bin/env node
'use strict';
/*
 * SessionStart hook of the java-skills plugin.
 *
 * Detects whether the project is a Java / Kotlin / Android project and, if so, injects a short
 * factual description of the team's Java engineering convention into Claude's context, so the
 * skills are applied by default instead of relying on Claude choosing them from descriptions.
 * Prints nothing (and therefore adds nothing to the context) for projects that are not Java.
 *
 * Opt out: set JAVA_SKILLS_DISABLE=1, or create the file .claude/java-skills.off in the project.
 * Requires only Node.js; no dependencies.
 */
const fs = require('fs');
const path = require('path');

const MAX_DEPTH = 3;
const MAX_ENTRIES = 4000;
const SKIP = new Set(['.git', 'node_modules', 'target', 'build', 'out', '.gradle', '.idea', '.mvn', 'dist', 'vendor', '.claude']);
const BUILD_FILES = new Set(['pom.xml', 'build.gradle', 'build.gradle.kts', 'settings.gradle', 'settings.gradle.kts', 'AndroidManifest.xml']);

function readInput() {
  try {
    const raw = fs.readFileSync(0, 'utf8');
    return raw ? JSON.parse(raw) : {};
  } catch (e) {
    return {};
  }
}

function exists(p) {
  try { fs.accessSync(p); return true; } catch (e) { return false; }
}

function read(p) {
  try { return fs.readFileSync(p, 'utf8'); } catch (e) { return ''; }
}

function scan(root) {
  const found = [];
  let seen = 0;
  const queue = [[root, 0]];
  while (queue.length && seen < MAX_ENTRIES) {
    const [dir, depth] = queue.shift();
    let entries = [];
    try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch (e) { continue; }
    for (const ent of entries) {
      seen += 1;
      if (ent.isDirectory()) {
        if (depth < MAX_DEPTH && !SKIP.has(ent.name)) queue.push([path.join(dir, ent.name), depth + 1]);
      } else if (BUILD_FILES.has(ent.name)) {
        found.push(path.join(dir, ent.name));
      }
    }
  }
  return found;
}

function detect(cwd) {
  const files = scan(cwd);
  if (!files.length) return null;
  const facts = { build: new Set(), springBoot: null, java: null, kotlin: false, android: false, files: files.length };
  for (const f of files) {
    const name = path.basename(f);
    const text = read(f);
    if (name === 'pom.xml') {
      facts.build.add('Maven');
      const parent = text.match(/<artifactId>spring-boot-starter-parent<\/artifactId>\s*<version>([^<]+)<\/version>/);
      if (parent) facts.springBoot = parent[1];
      else if (/spring-boot/.test(text) && !facts.springBoot) facts.springBoot = 'present (version managed elsewhere)';
      const j = text.match(/<(?:java\.version|maven\.compiler\.release|maven\.compiler\.source)>\s*([\d.]+)\s*</);
      if (j && !facts.java) facts.java = j[1];
      if (/kotlin-maven-plugin|kotlin-stdlib/.test(text)) facts.kotlin = true;
    } else if (name === 'AndroidManifest.xml') {
      facts.android = true;
    } else {
      facts.build.add('Gradle');
      const sb = text.match(/org\.springframework\.boot['")\s:]*(?:version\s*)?['"]?([\d.]+[\w.-]*)?/);
      if (/org\.springframework\.boot/.test(text) && !facts.springBoot) facts.springBoot = (sb && sb[1]) || 'present';
      if (/com\.android\.(application|library)/.test(text)) facts.android = true;
      if (/kotlin/.test(text)) facts.kotlin = true;
      const j = text.match(/JavaVersion\.VERSION_(\d+)|JavaLanguageVersion\.of\((\d+)\)|sourceCompatibility\s*=?\s*['"]?([\d.]+)/);
      if (j && !facts.java) facts.java = j[1] || j[2] || j[3];
    }
  }
  facts.specKit = exists(path.join(cwd, '.specify')) || exists(path.join(cwd, 'specs'));
  facts.projectSkills = exists(path.join(cwd, '.claude', 'skills', 'java-engineering-core'));
  return facts;
}

function buildContext(f) {
  const bits = [];
  if (f.build.size) bits.push([...f.build].join(' + ') + ' build');
  if (f.java) bits.push('Java ' + f.java);
  if (f.springBoot) bits.push('Spring Boot ' + f.springBoot);
  if (f.android) bits.push('Android');
  if (f.kotlin) bits.push('Kotlin present');
  if (f.specKit) bits.push('Spec Kit artifacts present');
  const p = 'java-skills:';
  return [
    'The Java Skill Base plugin (java-skills) is active in this project. Detected: ' + (bits.join(', ') || 'Java build files') + '.',
    '',
    'Team convention for this project: any task that involves Java or Kotlin code, build files, tests, configuration or code review starts with the ' + p + 'java-engineering-core skill. That skill discovers the repository (versions, build tool, frameworks, conventions, test commands) and selects the specialised skills the task touches; those are then loaded with the Skill tool before work begins, including for small changes. Conceptual questions that need no code or repository facts can be answered directly.',
    '',
    'Specialised skills available (all prefixed ' + p + '):',
    '- java-core-engineering: plain Java, release-level language features, concurrency, java.time/money, API compatibility',
    '- java-architecture-design: structure, boundaries, modular monolith vs services, ADRs',
    '- java-web-development: REST/web layer, validation, error contracts, OpenAPI, CORS/CSRF',
    '- spring-boot-engineering: Boot configuration, auto-configuration, Actuator, Boot tests, packaging',
    '- spring-data-jpa-engineering: entities, repositories, queries, transactions, migrations',
    '- hibernate-orm-engineering: N+1, lazy loading, flush, cascades, caching, batching, locking',
    '- spring-security-engineering: authN/authZ, OAuth2/JWT, method security, CORS/CSRF, secrets',
    '- java-database-engineering: schema, indexes, isolation, pools, Flyway/Liquibase',
    '- java-testing-quality: JUnit, Mockito, slices, Testcontainers, static analysis',
    '- java-messaging-integration: HTTP clients, Kafka/RabbitMQ, idempotency, retries, outbox',
    '- java-performance-resilience: profiling, timeouts, circuit breakers, caching, load tests',
    '- java-production-deployment: Docker, CI/CD, observability, config and secrets, rollout',
    '- java-mobile-development: native Android in Java, Kotlin interop, Jetpack/Compose',
    '- java-ai-integration: LLM/RAG/tool-calling features',
    '- java-maintenance-troubleshooting: build/startup failures and upgrades',
    '- java-code-review: reviewing diffs, PRs and release readiness',
    '- java-spec-driven-development: implementing from Spec Kit specs and tasks',
    '',
    'Standards the skills apply: respect the repository\'s existing Java, Kotlin and framework versions; report only checks that were actually run; do not weaken tests or security controls to get a green build; enforce authorization on the server; keep secrets out of code, config and logs.'
  ].join('\n');
}

function main() {
  if (process.env.JAVA_SKILLS_DISABLE === '1') return;
  const input = readInput();
  const cwd = input.cwd || process.env.CLAUDE_PROJECT_DIR || process.cwd();
  if (exists(path.join(cwd, '.claude', 'java-skills.off'))) return;
  const facts = detect(cwd);
  if (!facts) return;
  const out = {
    hookSpecificOutput: {
      hookEventName: 'SessionStart',
      additionalContext: buildContext(facts)
    }
  };
  process.stdout.write(JSON.stringify(out));
}

try {
  main();
} catch (e) {
  // never block a session because of this hook
  process.exit(0);
}
