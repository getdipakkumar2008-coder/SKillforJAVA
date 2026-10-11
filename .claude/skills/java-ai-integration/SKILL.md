---
name: java-ai-integration
description: Add AI/LLM capabilities to Java applications safely - model-provider abstraction (Spring AI ChatClient or a provider SDK), structured outputs with schema validation, tool calling and its authorization, retrieval-augmented generation, embeddings and vector search, prompt and context management, timeouts, rate limits, token budgets and cost control, evaluation and regression testing, prompt-injection and hallucination mitigation, data privacy, auditability and human approval for consequential actions. Use when a feature calls an LLM or embedding model. Keeps probabilistic AI behaviour separate from deterministic business rules and security controls.
---

# Java AI Integration

## Purpose
Integrate model-backed features so that the model is an untrusted, probabilistic component behind deterministic, secured application code - with measurable quality, bounded cost and auditable behaviour.

## Activation conditions
A task adds or changes LLM chat/completion, embeddings, RAG, vector search, tool/function calling, agents, MCP clients/servers, prompt templates, AI evaluation, or AI cost/limits. Run `java-engineering-core` discovery first; check whether the repo already uses an AI library or provider. **Only add AI where the requirement calls for it** - deterministic logic is cheaper, testable and safer.

## Version awareness (checked 2026-10-11)
- Spring AI (https://spring.io/projects/spring-ai): current stable **2.0.1**, with 1.1.8 and 1.0.9 also listed; 2.1.0-M1 preview. Reference sections (2.0.1): ChatClient API, Advisors, Structured Output (with schema validation and self-correction, provider-native structured output), Tool Calling, RAG (incl. ETL pipeline), Vector Databases (portable API, metadata filters), Model Evaluation, Observability, Model Context Protocol (client/server starters; MCP security noted as work in progress), Chat Memory. Providers listed: Anthropic, OpenAI, Microsoft, Amazon, Google, Ollama; vector stores include PGVector, Redis, Qdrant, Pinecone, Milvus, Weaviate, Chroma, MongoDB Atlas, Neo4j, Oracle, Cassandra, Azure.
- The Spring AI page gave **no Spring Boot compatibility matrix**; check the project's upgrade notes/release notes for which Boot generation each line supports. Use the Spring AI version already in the repo; do not upgrade as a side effect. APIs differ between 1.x and 2.x - verify class and starter names in the reference for the repo's version.
- Provider SDKs (Anthropic, OpenAI, etc.) and model ids change often: take model ids and parameters from the provider's current official docs, not memory. For Claude models use the Anthropic documentation (and the `claude-api` skill if available).
- OWASP Top 10 for LLM Applications **2025**: Prompt Injection, Sensitive Information Disclosure, Supply Chain, Data and Model Poisoning, Improper Output Handling, Excessive Agency, System Prompt Leakage, Vector and Embedding Weaknesses, Misinformation, Unbounded Consumption (https://genai.owasp.org/llm-top-10/). Treat as the baseline threat model.

## Required context and inputs
The user-facing behaviour and what a wrong answer costs; data sensitivity (PII, secrets, regulated data) and whether it may leave the organisation; provider/hosting constraints (cloud API vs self-hosted, region); latency and cost budgets; which actions the AI may trigger; existing auth model; existing observability and test setup.

## Repository inspection
1. AI dependencies (Spring AI starters, provider SDKs, vector store clients) and versions; configuration of models/keys.
2. Existing prompts/templates, where stored, how versioned.
3. Where model output flows (UI, DB, other services, tool execution).
4. Existing tools/functions exposed to the model and their authorization.
5. Existing evaluation datasets/tests; logging and metrics for AI calls.
6. Data flows into prompts: what user/tenant data is included.

## Decision rules
- **Deterministic first:** if rules can be coded, code them. Use the model for language understanding/generation, classification, extraction, summarisation, retrieval-augmented answers - not for authorization decisions, financial calculations, transaction integrity or validation that must be exact.
- **Separation of concerns:** keep the model call behind an application port/service (e.g. `SummaryGenerator`) so it can be stubbed, swapped, rate-limited and tested; business rules and persistence stay outside the model path.
- **Provider abstraction:** use Spring AI (`ChatClient`/`ChatModel`, `EmbeddingModel`, `VectorStore`) when the repo is Spring-based and portability matters; use the provider SDK when you need provider-specific features and accept the coupling. Do not build your own abstraction on top of an abstraction. Keep provider/model name, temperature, max tokens and timeouts in configuration.
- **Structured outputs:** request a schema (provider-native structured output where available, or output converters), **validate** the result with Bean Validation/JSON Schema, and handle invalid output by bounded retry/repair or a safe fallback. Never parse free text with regexes for control flow.
- **Tool calling:** expose the **minimum** set of narrowly scoped tools; each tool validates its arguments like any untrusted API input, runs with the **end user's** authorisation (not a super-user service account), enforces tenant/ownership checks server-side, is idempotent or guarded, and is rate-limited and audited. The model never receives credentials; tool results are treated as untrusted data too. Read-only tools by default; any state-changing or irreversible tool requires **human approval** (explicit confirmation step in the application, not a model-generated "yes").
- **RAG:** retrieval must respect authorization - filter by user/tenant/ACL metadata **at query time** in the vector store, not after generation. Ingest only content the data owner approves; chunk with overlap suited to the content; store source ids/URLs for citations; choose embedding model once (changing it requires re-embedding); consider hybrid (keyword + vector) search; re-rank when precision matters; evaluate retrieval separately from generation. Treat retrieved text as untrusted (indirect prompt injection).
- **Prompt and context management:** prompts are code - versioned, reviewed, tested; separate system instructions from user input and retrieved content with clear delimiters; no secrets in prompts; keep context within the token budget (summarise/trim/memory limits); cap conversation memory per user and expire it.
- **Cost, latency and limits:** set max input/output tokens, per-user and per-tenant rate limits and budgets, request timeouts and bounded retries with backoff (respect provider `429`/`Retry-After`), concurrency caps (bulkhead), caching of deterministic or repeated requests where safe, smaller/cheaper models for simple tasks, streaming for perceived latency. Expose token and cost metrics. (OWASP LLM10 Unbounded Consumption.)
- **Failure behaviour:** define fallback when the model is slow, down, or returns invalid/unsafe output (cached answer, rule-based answer, "unavailable" message). Never silently return a fabricated result.
- **Data privacy:** minimise what is sent; redact/mask PII and secrets; confirm provider data-retention/training terms and region; no regulated data to a provider without approval; encrypt at rest/in transit; honour deletion requests for stored prompts, embeddings and memory.
- **Agents and MCP:** autonomous multi-step agents multiply risk (excessive agency). Bound steps, tools, time and spend; require approvals for consequential actions; for MCP servers/clients authenticate and authorise (the reference marks MCP security as work in progress - add your own controls), allow-list servers/tools, and treat third-party tool descriptions as untrusted.

## Workflow
1. Define the task, success metric (quality, latency, cost) and failure cost; confirm AI is warranted.
2. Define the port, input/output schema, allowed data, and fallback behaviour.
3. Design the threat model (prompt injection direct/indirect, data leakage, tool abuse, cost abuse) using the OWASP LLM list.
4. Implement behind the port with configuration-driven provider settings, timeouts, limits and structured validated output.
5. Add tools/RAG only as required, with authorization and approval gates.
6. Add observability: request/response metadata (not raw sensitive content by default), token counts, latency, cost, tool calls, retrieval hits, validation failures; correlation ids; audit log of consequential actions and approvals.
7. Build an **evaluation set** and tests (below); establish a baseline; run before changing prompts, models or retrieval settings.
8. Run security/negative tests; run the usual build/tests.
9. Report quality numbers, limits, residual risks and what could not be tested (e.g. live provider access).

## Implementation guidance
- Configuration: API keys from environment/secret manager (`java-production-deployment`); never commit; separate keys per environment; use provider spend limits.
- Use `temperature` low for extraction/classification; set `max tokens`; pin model versions/ids where reproducibility matters and plan for model deprecation.
- Spring AI: configure through Boot properties and starters; use `ChatClient` with advisors for memory/RAG/logging; use structured output converters; verify advisor and tool annotations against the repo's Spring AI version. Spring AI's observability and evaluation utilities can supply metrics and relevance/hallucination checks - verify availability for the version.
- Embeddings/vector store: pick a store the team already operates when possible (e.g. PGVector in the existing PostgreSQL); define index type and dimensions to match the embedding model; manage schema via migrations (`java-database-engineering`); batch ingestion with idempotent upserts and re-ingestion/versioning strategy; delete embeddings when source data is deleted.
- Streaming: bound stream duration and size; handle client disconnects; moderate or validate before display if needed.
- Output handling: encode/escape model output before rendering (XSS), never execute it as code/SQL/shell, validate URLs and file paths it produces, and label AI-generated content in the UI where appropriate.
- Human-in-the-loop: present the proposed action with parameters to the user/approver; approval is checked server-side; log who approved what.

## Security and reliability requirements
- Treat **all** model inputs and outputs, retrieved documents and tool results as untrusted. Instructions in data must not be able to change tool permissions or policies.
- Authorization is enforced by application code on every tool call and retrieval; the model cannot grant itself access (OWASP LLM06 Excessive Agency, LLM01 Prompt Injection).
- Do not put secrets, system internals or other users' data in prompts; assume system prompts can leak (LLM07).
- Validate and sanitise outputs before use (LLM05); constrain output formats.
- Protect vector stores like databases: auth, tenant isolation, encryption, access logging (LLM08); vet embedding/model/library supply chain and pin versions (LLM03); control what enters the knowledge base (LLM04).
- Rate limit, cap tokens, concurrency and spend; alert on anomalies (LLM10).
- Mitigate misinformation: grounded answers with citations, confidence/"I don't know" behaviour, disclaimers where stakes are high (LLM09).
- Logging/audit: record that an AI decision/action occurred, inputs' references, model/version, output, approver; redact sensitive content; retention per policy.
- Fail closed on security checks; fail soft (degraded feature) on model unavailability.

## Common anti-patterns
- Using an LLM where a rule, query or regex-free parser would do; letting the model decide authorization or compute exact values.
- Giving the model a broad super-user tool or database access; tools that run with service-account privileges instead of the user's.
- Concatenating untrusted text into the system prompt; trusting retrieved documents; filtering RAG results by permission *after* retrieval/generation.
- Parsing free-form text for control flow; no schema validation; no fallback for invalid output.
- Unbounded loops, retries, tokens, conversation history or agent steps; no per-user budgets.
- Secrets or PII in prompts and logs; logging full prompts/responses by default.
- Prompts edited ad hoc in production with no version control or evaluation; changing the model without re-running evaluation.
- Treating demo-quality outputs as tested; no regression dataset; asserting exact strings from nondeterministic output.
- Letting AI-generated actions execute without approval for consequential operations.
- Rendering model output as trusted HTML or executing it.

## Testing and verification
- **Unit tests** with a stubbed model port: prompt construction, schema validation, fallback paths, tool argument validation, authorization checks, token/budget enforcement - fully deterministic.
- **Contract/integration tests** against a fake or recorded provider (WireMock/Testcontainers-style) for timeouts, 429/5xx, malformed/invalid structured output, streaming interruptions.
- **Security tests:** prompt-injection corpus (direct and via retrieved documents), attempts to call unauthorised tools, cross-tenant retrieval, data exfiltration via output, oversized inputs/cost abuse; verify the application-level controls hold regardless of model behaviour.
- **Evaluation:** a versioned dataset of representative and adversarial cases with expected properties; metrics suited to the task (exact match/schema validity for extraction, retrieval hit rate/MRR for search, groundedness/faithfulness and relevance for RAG answers, task success rate, refusal correctness), run via a repeatable harness (Spring AI evaluators or an LLM-as-judge/human review - note judge bias and use spot checks). Track results over time; set pass thresholds; run on prompt/model/retriever changes. Use fixed seeds/low temperature where available, and assert on properties, not exact wording.
- **Live-provider tests** are optional, tagged and separated from the default build (cost, flakiness, secrets); state clearly when they were not run.
- Report which tests ran, evaluation scores with dataset size and model/version, and unverified risks.

## Definition of done
AI use justified; model behind a port with config-driven provider, limits and timeouts; outputs schema-validated with defined fallback; tools minimal, user-authorised, audited, and approval-gated for consequential actions; RAG enforces authorization at retrieval; PII/secrets handled per policy; cost and rate controls in place; observability and audit logging present; evaluation dataset and regression tests exist and were run with real results reported; security/injection tests executed; no deterministic rule, transaction or authorization outsourced to the model.

## Related skills
`java-engineering-core`, `spring-boot-engineering`, `spring-security-engineering`, `java-web-development`, `java-database-engineering` (vector storage), `java-messaging-integration` (async processing, retries), `java-performance-resilience`, `java-production-deployment` (secrets, observability), `java-testing-quality`, `java-architecture-design`, `java-spec-driven-development`.

## Official references
- https://spring.io/projects/spring-ai and https://docs.spring.io/spring-ai/reference/
- OWASP Top 10 for LLM Applications: https://genai.owasp.org/llm-top-10/
- Anthropic API docs (for Claude models): https://docs.claude.com/ · other providers' official docs for their SDKs and models
- Vector store docs for the chosen store (e.g. pgvector https://github.com/pgvector/pgvector)
- Model Context Protocol: https://modelcontextprotocol.io/
- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework
