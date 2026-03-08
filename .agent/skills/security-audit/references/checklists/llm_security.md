# OWASP Top 10 for LLM Applications v2.0 — Security Checklist

> **Source:** OWASP Top 10 for LLM Applications v2.0 (2025 Final).
> **Scope:** Any project that integrates LLM APIs, fine-tuned models, AI agents, or RAG pipelines.

## LLM01: Prompt Injection
- [ ] **Direct Injection:** Can a user craft input that overrides system prompts or instructions?
- [ ] **Indirect Injection:** Can external data sources (web pages, documents, emails) contain hidden instructions that alter LLM behavior?
- [ ] **Delimiter Enforcement:** Are system/user message boundaries enforced at the API level (role separation)?
- [ ] **Input Sanitization:** Is user input sanitized before inclusion in prompts (strip control characters, markdown injection)?
- [ ] **Output Validation:** Is LLM output validated before being used in downstream actions (tool calls, code execution)?

## LLM02: Insecure Output Handling
- [ ] **HTML/JS Injection:** Is LLM output rendered in a browser without escaping? (XSS via LLM)
- [ ] **SQL/Command Injection:** Is LLM output used in database queries or shell commands without parameterization?
- [ ] **Code Execution:** Is LLM-generated code executed without sandboxing?
- [ ] **Markdown Injection:** Can LLM output contain malicious links, images, or iframes rendered by the UI?
- [ ] **Content-Type:** Are LLM responses served with correct Content-Type headers (not `text/html` for API responses)?

## LLM03: Training Data Poisoning
- [ ] **Data Provenance:** Is the source and integrity of training/fine-tuning data verified?
- [ ] **Data Sanitization:** Are training datasets scanned for injected instructions, backdoors, or biased content?
- [ ] **Model Signatures:** Are model weights verified via checksums/signatures before deployment?
- [ ] **RAG Data:** Are documents in the RAG corpus validated and access-controlled?

## LLM04: Model Denial of Service
- [ ] **Input Length Limits:** Are token limits enforced on user input?
- [ ] **Rate Limiting:** Are per-user/per-IP rate limits applied to LLM API endpoints?
- [ ] **Timeout:** Are inference timeouts configured to prevent resource exhaustion?
- [ ] **Cost Controls:** Are spending caps / billing alerts configured on LLM API usage?
- [ ] **Recursive Loops:** Can the LLM trigger itself in an infinite loop (agent → tool → agent)?

## LLM05: Supply Chain Vulnerabilities
- [ ] **Model Source:** Are models downloaded from trusted registries (HuggingFace verified, official APIs)?
- [ ] **Plugin/Tool Verification:** Are third-party plugins, MCP servers, or tools verified before integration?
- [ ] **Dependency Scanning:** Are ML-specific dependencies (transformers, langchain, llamaindex) scanned for vulnerabilities?
- [ ] **Serialization:** Are models loaded via safe formats (safetensors) instead of pickle?

## LLM06: Excessive Agency
- [ ] **Least Privilege:** Does the LLM/agent have only the minimum permissions needed?
- [ ] **Human-in-the-Loop:** Are destructive actions (delete, send, purchase) gated by user confirmation?
- [ ] **Scope Limits:** Are tool/function calls restricted to an allowlist?
- [ ] **Blast Radius:** What is the worst-case outcome if the LLM executes an unintended action?
- [ ] **Audit Trail:** Are all LLM-initiated actions logged with full context?

## LLM07: System Prompt Leakage
- [ ] **Prompt Confidentiality:** Can the system prompt be extracted via "repeat your instructions" or similar attacks?
- [ ] **Meta-Prompt Defenses:** Are anti-leakage instructions included (though not sufficient alone)?
- [ ] **Sensitive Data in Prompts:** Do system prompts contain API keys, internal URLs, or business logic that should not be exposed?

## LLM08: Vector and Embedding Weaknesses
- [ ] **Access Control:** Are vector DB queries filtered by user permissions (multi-tenant RAG)?
- [ ] **Embedding Injection:** Can an attacker insert poisoned documents into the vector store?
- [ ] **Data Isolation:** Are embeddings from different security contexts stored in separate collections/namespaces?
- [ ] **Relevance Attacks:** Can adversarial documents be crafted to always appear as top results?

## LLM09: Misinformation
- [ ] **Grounding:** Are LLM responses grounded in verified data sources (RAG, search)?
- [ ] **Confidence Indicators:** Does the UI indicate when responses are AI-generated or uncertain?
- [ ] **Fact-Checking:** Are critical outputs (medical, legal, financial) validated by domain-specific checks?
- [ ] **Hallucination Detection:** Are responses cross-referenced against known facts or source documents?

## LLM10: Unbounded Consumption
- [ ] **Token Budgets:** Are per-request and per-session token budgets enforced?
- [ ] **Concurrent Requests:** Is the number of parallel LLM calls limited per user?
- [ ] **Output Length:** Are maximum output token limits configured?
- [ ] **Monitoring:** Are LLM usage metrics (tokens, cost, latency) monitored with anomaly detection?
- [ ] **Abuse Detection:** Are patterns like repeated max-length prompts or prompt stuffing detected?

## Agent-Specific Checks (Beyond OWASP LLM Top 10)
- [ ] **Tool Injection:** Can user input influence which tools/functions the agent calls?
- [ ] **Context Window Poisoning:** Can injected content persist across conversation turns?
- [ ] **Multi-Agent Trust:** In multi-agent systems, do agents validate each other's outputs?
- [ ] **Session Isolation:** Are agent sessions isolated between users (no shared state leakage)?
- [ ] **Rollback Capability:** Can agent actions be rolled back if a compromised step is detected?
