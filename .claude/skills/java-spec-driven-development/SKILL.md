---
name: java-spec-driven-development
description: Implement Java features from a specification-driven workflow (GitHub Spec Kit or an equivalent) - read the constitution, spec, plan, tasks and acceptance criteria, map tasks to the right Java skills, plan small reviewable changes, implement, write tests mapped to acceptance criteria, run checks, record deviations, verify against the spec and update task status truthfully. Use whenever a repo has Spec Kit artifacts (.specify/, specs/) or the user says "implement the spec/tasks". Spec Kit stays the authority for requirements and planning; this skill governs Java execution.
---

# Java Spec-Driven Development

## Purpose
Turn specification artifacts into verified Java code without re-deciding requirements. The spec workflow owns *what* and *why*; the Java skill base owns *how* and *proof*.

## Activation conditions
- `.specify/` or a `specs/` directory (or similar spec/plan/task files) exists, or the user refers to a spec, plan, tasks or acceptance criteria.
- The user asks to implement, verify or update status of spec-defined work.
- Run `java-engineering-core` discovery too: it supplies the repository profile; this skill supplies the spec-to-code procedure.

## Spec Kit awareness (checked 2026-10-11 from the project's README and docs site; incomplete)
- Spec Kit (`github/spec-kit`, MIT) is an open-source toolkit; CLI `specify` (`uv tool install specify-cli`; `specify init <project> --integration <agent>`; Claude is among its listed integrations, and `init` generates the agent's command files).
- The documented core workflow is **Specify -> Plan -> Tasks -> Implement -> Converge**, with a one-time **constitution** step, plus clarification, quality checklists and cross-artifact analysis. Commands are typed in the agent chat as `/speckit-constitution`, `/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-implement`, `/speckit-converge`. Repeat implement and converge until converge reports "Converged". Opt-in extensions exist for bug fixing (`/speckit-bug-assess|fix|test`, artifacts in `.specify/bugs/<slug>/`) and idea assessment (`.specify/assessments/<slug>/`).
- I could **not** confirm from the fetched pages: exact artifact file names/paths (commonly `specs/<feature>/spec.md`, `plan.md`, `tasks.md`, and a constitution under `.specify/`), clarify/analyze/checklist command names, or what the Claude integration generates. Command names and layout have changed between Spec Kit versions. **Therefore: discover the layout and commands from the repository itself** (below) and from the installed version's docs (`specify --help`, README, the generated command files), never from memory.
- If the project uses a different spec workflow (OpenSpec, Kiro-style specs, plain ADR/PRD markdown), apply the same procedure to its artifacts.

## Required context and inputs
Constitution/principles, the feature spec (user stories, functional requirements, acceptance scenarios, success criteria, edge cases), plan (architecture, data model, contracts, tech choices), tasks (ordered, with dependencies/parallel markers and status), plus project instruction files.

## Repository inspection
1. List `.specify/` (templates, memory/constitution, scripts, bugs, assessments) and `specs/` (feature folders). Identify the **current feature** from the branch name, the user's message, or the most recently changed feature folder; if ambiguous, ask.
2. Read in order: constitution -> spec -> plan -> data model/contracts/research notes -> tasks.
3. Note: unresolved `[NEEDS CLARIFICATION]`-style markers, checklists and their state, task ids/status markers (`[ ]`/`[x]`), and any analysis/converge reports.
4. Read repo instruction files (`CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`) and the `java-engineering-core` repository profile.

## Workflow
The 11 steps:
1. **Read** instructions, constitution, spec, plan, tasks and acceptance criteria (above).
2. **Respect decisions:** the constitution and plan are binding (architecture, libraries, versions, conventions). Do not substitute technologies or restructure because you prefer something else.
3. **Map tasks to skills:** for each task, activate only the relevant Java skills (see mapping table). Record the mapping briefly.
4. **Check readiness:** find missing requirements, ambiguities, conflicts between spec/plan/tasks/constitution/code, and unmet prerequisites (e.g. spec needs auth, plan omits it). Resolve small ones with a stated assumption; for consequential gaps (security, data integrity, public contract, architecture) stop and ask - or recommend running the workflow's clarify/analyze step - rather than inventing requirements.
5. **Plan small, reviewable changes:** take tasks in dependency order; one task (or a tight group) per change; honour `[P]`-style parallel markers only when work truly is independent; keep each step buildable.
6. **Implement per spec:** follow `java-engineering-core` and the mapped skills; stay within the task's scope; if the spec's wording conflicts with correctness/security, flag it rather than silently deviating.
7. **Tests mapped to acceptance criteria:** every acceptance scenario and success criterion gets at least one test; negative/edge cases from the spec's edge-case section too; name tests so the mapping is visible (e.g. include the story/requirement id in the test name or a short comment). Follow the spec's test-first ordering if the tasks prescribe it.
8. **Run checks:** targeted tests, then module/full build, plus configured quality/security checks (`java-testing-quality`). Observe real results.
9. **Record deviations and risks:** any departure from spec/plan (with reason and impact), assumptions made, unresolved risks, follow-ups. Put them where the project expects (spec/plan notes, tasks file comments, PR description) - do not silently edit the spec to match the code.
10. **Verify against the spec:** walk each requirement and acceptance criterion; mark it met, partially met, or not met with evidence (test name + result, manual check). If the workflow provides a converge/analyze/verify step, run or recommend it and treat its report as input.
11. **Update status and docs from actual results:** tick tasks only when implemented **and** verified; leave failing/blocked tasks unchecked with a note; update README/API docs/migration notes that the change affects. Never mark work done that was not done.

## Task-to-skill mapping
| Task type | Skills |
|---|---|
| Domain model / pure logic | `java-core-engineering`, `java-architecture-design` (if available), `java-testing-quality` |
| REST endpoint, DTOs, validation | `java-web-development`, `spring-boot-engineering`, `java-testing-quality` |
| Entities, repositories, migrations | `spring-data-jpa-engineering`, `hibernate-orm-engineering`, `java-database-engineering` |
| AuthN/AuthZ, secrets | `spring-security-engineering` (+ web/boot) |
| Events, external APIs | `java-messaging-integration`, `java-performance-resilience` (resilience parts) |
| Android UI/feature | `java-mobile-development` (if available), `java-testing-quality` |
| Config, Docker, CI, observability | `java-production-deployment`, `spring-boot-engineering` |
| AI-backed feature | `java-ai-integration` (if available), `spring-security-engineering` |
| Failing build/regression/upgrade task | `java-maintenance-troubleshooting` |
Always include `java-engineering-core`. If a listed skill is not installed, proceed with core principles and official docs, and note the gap.

## Decision rules
- Spec Kit (or the equivalent) is the **workflow authority** for requirements, plan, tasks and acceptance criteria. This skill does not rewrite them; it implements and verifies them. Propose spec/plan changes explicitly and let the owner accept them.
- Constitution > spec > plan > tasks when they conflict; surface the conflict.
- Implement only what tasks/spec require (no gold-plating); note beneficial extras as suggestions.
- Prefer the smallest implementation that satisfies acceptance criteria; keep business rules explicit and traceable to requirements.
- Task status reflects verified reality; incomplete verification means the task is not done.
- When the user asks to bypass the spec workflow, comply with their instruction but state the traceability trade-off in one line.

## Implementation guidance
- Implement one task (or a tight group) at a time in dependency order; keep each step buildable and reviewable.
- Follow the plan's architecture, libraries and contracts; use the Java skills for *how* (conventions, frameworks, tests) without changing *what* the spec requires.
- Name tests and commits so they trace to requirement or task ids; keep a running list of deviations, assumptions and open questions.
- Do not edit the constitution, spec or plan to match the code; propose changes and let the owner accept them.
- Update task checkboxes and docs only after verification.

## Security and reliability requirements
Specs often omit non-functional needs. Check each task against: authorization, input validation, data integrity/transactions, secrets, error handling, idempotency, observability, performance limits. If the spec is silent on something consequential, ask or record an explicit assumption; do not skip it. Apply the constitution's security/quality gates literally.

## Common anti-patterns
- Coding before reading the constitution and plan; substituting your own stack or architecture.
- Inventing requirements to fill gaps; silently dropping inconvenient ones.
- Marking tasks complete without running tests, or when tests fail; editing the spec to match what was built without recording the deviation.
- Giant changes covering many tasks at once; ignoring task dependencies.
- Tests that don't trace to acceptance criteria, or only cover the happy path.
- Treating generated Spec Kit command names/paths as fixed across versions.
- Using the Java skills to re-run requirements discovery that the spec workflow already did.

## Testing and verification
Maintain a short traceability table in your report (and in the project's artifact if conventional):

| Requirement / acceptance criterion | Task(s) | Test(s) | Result |
|---|---|---|---|
Report the exact commands run and real outcomes; list criteria not verified and why (no container runtime, external dependency, manual UAT needed). If the workflow has an analysis/converge step, state whether it was run and its result.

## Recommended workflow with Spec Kit (summary)
1. Once per project: install `specify`, `specify init` for your agent, install the Java skill base (`scripts/install-skills.sh`; `.claude/skills/` for Claude Code and Copilot, or `.github/skills/` for Copilot only), write a **constitution** that references Java standards (Java/Boot versions, test and security gates, "use java-engineering-core").
2. Per feature: specify -> (clarify) -> plan (stack, data model, contracts) -> tasks -> **implement using this skill** -> converge/analyze until clean.
3. Keep specs technology-neutral (what/why); put stack decisions in the plan; keep Java-specific *how* in these skills, not in every spec.
4. Review small diffs per task; verify; update task status; merge.

## Definition of done
All targeted tasks implemented in dependency order; each acceptance criterion traced to executed tests with real results; deviations, assumptions and risks recorded; task statuses and docs updated truthfully; spec/plan/constitution unchanged unless explicitly agreed; relevant build and quality checks run; remaining work and unverified items listed.

## Related skills
`java-engineering-core` (always), plus every skill in the mapping table; `java-testing-quality` for acceptance-criteria tests; `java-maintenance-troubleshooting` for failures.

## Official references
- https://github.com/github/spec-kit and https://github.github.io/spec-kit/ (workflow, integrations reference, quickstart - read the installed version's docs for exact commands and paths)
- Project files: constitution, `specs/`, `.specify/`
