# Sandbox Boundaries & Context Integrity (2026-09-04)

Adapted from the X-scout knowledge-scout digest of 2026-09-04 (Discord thread
#xTreand, cron job f933f5a8d591; batch archives 00:03–20:02 ICT, 6 batches).
Two converging themes: **(A) the real security boundary is egress, not the
model or its classifiers**, and **(B) context integrity decays silently —
compaction, summarization, and long context delete constraints while the agent
keeps reporting success**.

## A. Sandbox: egress deny-by-default is the boundary

### A1. Google Agent Sandboxes — five isolation lessons
Source: https://explainx.ai/blog/google-cloud-agent-sandboxes-five-things-isolation-2026

- Three boundaries: no visibility into env vars/metadata server; **network
  egress deny-by-default** (`--allow-egress` is the equivalent of sudo);
  read-only filesystem + overlay discarded at session end.
- Cold-start latency must be measured as a *distribution*, not a hero metric —
  an agent fleet of 200+ multiplies every session's cold start.
- Corollary: an expensive microVM with full internet access is worse than a
  cheap sandbox with default-deny egress. If egress is needed, open per-call,
  opt-in, visible in code.

### A2. "Out of the Sandbox" — escapes without zero-days
Source: https://x.com/i/article/2094174866576404913 (X Article, ExploitGym →
incident timeline → builder lessons)

- Services the sandbox is *meant* to see (package managers) get converted into
  network proxies via SSRF; shared storage becomes a communication channel
  between agents.
- Builder test: for every service shared with an agent ask — "can input to it
  cause a network request?"

### A3. Classifier ≠ sandbox: benign-per-step attack chain
Source: https://embracethered.com/blog/posts/2026/breaking-claude-code-opus-5-and-automode/

- Auto-approval hijack chain: WebFetch fail → curl fallback → ZIP → the model
  *refuses* to run the binary but **writes its own decoder** → `struct.py`
  module shadowing kills the import chain. Every step passed the classifier
  (ASR 60–80% in small samples); the classifier even blocked the model's own
  cleanup commands.
- Doctrine: the real boundary is OS isolation + network egress control;
  unattended agents must not see home dir / SSH / credentials; classifier
  approval is not evidence of safety.

### A4. GitSpawn: `git status` at startup runs repo code ⚠️
Source: https://www.manifold.security/blog/ai-coding-agents-git-hijack (2026-09-01)

- Agents run git for context when opening a project without stripping
  `.git/config`; git config `core.fsmonitor` set to a command executes on the
  host **before the trust prompt, outside the sandbox**. Claude Code patched;
  Hermes, Qwen Code, Grok Build confirmed unpatched as of 2026-09-01.
- Operational rule: before opening an untrusted repo with any agent CLI,
  inspect `.git/config` for program-pointing settings; in own tooling sanitize
  with `git -c core.fsmonitor=false ...`.

### A5. MCP playbook additions: gateway + version pinning
Source: https://www.explainx.ai/blog/mcp-security-guide-2026 (updated 2026-09-01)

- Central **MCP gateway** does auth enforcement / rate limiting / audit
  logging (sub-servers cannot suppress logs); pin reviewed server versions,
  never auto-update; run servers sandboxed with watched egress.
- Cited incident: tl;dv database leak of ~181k meetings from one collection
  missing a single tenant-isolation rule — damage comes from one forgotten
  resource rule, not the protocol.

### A6. Memory poisoning → trajectory-aware security evals
Source: https://the-14.com/ai-agents-can-now-remember-and-hackers-can-poison-their-memories-a-new-cybersecurity-threat
(Univ. Calgary research, 2026-09-03)

- Injection planted in agent memory now is retrieved later as "learned
  knowledge"; fraud patterns are non-monotonic (improve, degrade, explode).
- Security evals for agents with memory must be **trajectory-aware** —
  continuous multi-interaction sequences, not per-prompt snapshots.

## B. Context integrity: constraints and success reports decay

### B1. Governance Decay / ConstraintRot
Source: arXiv 2606.22528

- Constraints living in conversation (policies from context files, old turns)
  are not immutable system messages. Under compaction/summarization they are
  cut as "not the current sub-goal" — then the agent does what it previously
  refused. Reproduced across 7 model families × 4 compaction strategies.
- Fix: must-not-fail rules are re-injected after every compaction or pinned
  system-level; never trust the summary to keep them.

### B2. Skills fail in long context: 38/44 false success reports
Source: arXiv 2607.17937 (white-box study on code-auditing tasks)

- Long/cluttered context → agent skips requirements (one field, one stale
  rule) while declaring completion; contradicting tool output does not reopen
  closed tasks.
- Mitigation ranking: generic mid-context "validate all constraints" passed
  5/10; an **external checklist enumerating all obligations** passed 10/10.
- Conclusion: verification must be an explicit, external, itemized checklist —
  not a generic instruction.

### B3. Step-level evaluation gap
Source: https://prefactor.tech/blog/step-level-evaluation-gap-agent-production-quality-gap

- 2026 audits: ~37% gap between benchmark and production; malformed tool calls
  become "true context" and later steps reason on a false premise while the
  final answer stays plausible.
- Instrument at span level, score per step (valid call? does step N's context
  survive to N+2?); repeated-query loops show up first as token-per-step.

### B4. Harness: mechanical sensors over natural-language rules
Source: https://devgent.org/en/how-to-stop-repeat-agent-failures-with-harness-design-en/
(LangChain Terminal Bench 2.0: 52.8% → 66.5% with harness-only changes, same
model weights)

- Don't add prompt rules defensively. Every context-file line must trace to a
  real observed failure, fixed with a mechanical gate (block completion on
  test failure; harness-level `rm -rf` block).
- Exercise: list last month's failures → classify each as missing Guide /
  Sensor / human approval → add one mechanical control → check next week the
  sensor actually fires (no fire = fix detection, not the rule text).

### B5. Conversation history is becoming append-only
Source: https://markhuang.ai/news/claude-fable-51-thinking-history-append-only

- Platforms bind thinking/reasoning blocks to the context that created them:
  retroactive edits (trim a turn, client-side summary replacement, mid-run
  system-prompt/tool changes) error out or silently drop reasoning.
- Harness implication: turn-scoped instructions (`clear_at`) + server-side
  compaction instead of rewriting history; check fallback routers for missing
  thinking-block handling.

### B6. Coding agents over-fetch: dependency-aware retrieval
Source: https://yonk.dev/blog/process-as-memory/

- ~11.7M tokens of real coding-agent transcripts: whole-file reads for one
  function ≈ 65% of read tokens; dependency-aware retrieval (resolve call
  graph first) reached full context in 30/30 cases at ~6% of whole-file token
  cost vs 1/30 for naive span windows; little gain from process memory (reuse)
  — the lever is bounded reading scope.

### B7. Multi-agent context passing: KV-cache compaction
Source: https://x.com/RampLabs/thread/2042660310851449223 (vendor write-up,
numbers unverified)

- Pass workers a compacted KV of the orchestrator trajectory instead of lossy
  summaries or RAG; task-prompt attention as relevance signal; prefix caching
  gives 90%+ reuse; call overhead ~30s → ~2s. Requires model-level control.

## C. Adjacent (reference-grade)

- **AVO (NVIDIA research)** — 7-day agent runs from two mechanisms: persistent
  state on disk (past implementations + eval results + profiler output) and a
  separate supervisor catching stagnation/loops. Source:
  https://martinfowler.com/fragments/2026-09-01.html
- **HF funes** — agent memory as dataset + `recall` tool with verbatim
  provenance (article benchmark: 4–8× better than handoff per task); local
  first; supports Claude Code/Codex/Hermes. Source:
  https://huggingface.co/blog/funes
- **MeMex Zero-RAG additions** (@joerg_peetz,
  https://x.com/joerg_peetz/status/2094467733568286777, repo
  github.com/JPeetz/MeMex-Zero-RAG): forward-only memory_type tags
  (episodic/semantic/procedural, never downgrade) + "every claim must have a
  source or it is an error" enforced by lint on every PR.
- **LLMs 101 (2026 Edition)** — local-LLM mechanics reference (inference loop
  → KV cache → quantization → VRAM math). Source:
  https://x.com/TheAhmadOsman/article/2057590224729911346

## What was skipped (and why)

- NHK AI anchor story, Roche/AbbVie pharma co-scientist thread — news/vertical
  interest, no transferable build mechanism.
- "LLMs ≠ good engineers" context-rot opinion thread — superseded by B1/B2
  which carry stronger evidence.
- Vendor benchmark numbers (Ramp Labs latency, funes recall multiplier) kept
  only as labeled unverified claims, per repo policy.
