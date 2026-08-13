# Research Report: Technical Validation of "Agent Engineering" Harness Patterns

Date: 2026-08-12  
Status: Completed  
NotebookLM Notebook: `Agent Engineering Harnesses: Research from Sprytix Article` (`1d0daffb-f6d6-475e-a377-e09260931ee3`)

## 1. Executive Summary
This report analyzes the technical viability of "Agent Engineering" as a methodology for long-horizon task automation, contrasting claims in popular industry commentary with primary research from Anthropic, METR, and MoonshotAI. The core proposition—that a specific "formula" for delegation exists—is a stylized interpretation of Anthropic’s findings on the "division of labor," where humans provide ~70% of planning decisions while AI handles ~80% of execution decisions. 

Primary evidence supports treating the harness as part of the system, not as a substitute for model capability. For `my-superpowers` maintainers, the practical lesson is to externalize state and make verification explicit before adding more orchestration.
1.  **Enforced Verification (Default-FAIL):** The companion Anthropic repository demonstrates a contract that starts with every criterion failing and requires evidence before a pass is recorded.
2.  **State Externalization:** Continuity across context windows is supported by structured progress files, feature state, and granular `git` history.

**Verdict:** "Agent Engineering" is best understood here as a practical label for applying software-engineering primitives—modularization, state restoration, and independent verification—to LLM orchestration.

## 2. Fact-Check: Sprytix X Article Claims Analysis

| Claim | Status | Evidence/Source Basis |
| :--- | :--- | :--- |
| The "$1.2M Senior AI Engineer" salary at Anthropic. | **Unsupported** | This figure appears in the Sprytix commentary but is absent from all primary Anthropic research papers and technical reports. |
| The existence of an "exact formula" for agent delegation. | **Commentary/Interpretation** | Anthropic research identifies a "clear division of labor" (70% human planning / 20% human execution decisions), but does not formalize this as a mathematical "formula." |
| The 50% task horizon doubling every seven months. | **Verified** | METR (May 2026) measurements confirm that the 50% task-completion time horizon for frontier agents doubled approximately every seven months. |
| Kimi K3's ability to make these skills accessible "in a week." | **Unsupported** | MoonshotAI documentation provides no learning-curve timeline; this is a subjective claim from the secondary source. |
| "Agent Engineering" is a new role distinct from Prompt Engineering. | **Commentary/Interpretation** | Sources differentiate between prompt-tuning and environment design (ACI), but the formalization of a new job title is an industry interpretation. |

## 3. Technical Breakdown: Anthropic’s Long-Running Agent Harness
Drawing from Anthropic's *"Effective harnesses for long-running agents"* article and the `cwc-long-running-agents` architecture, the harness implements the following primitives:

### 3.1 Initializer Agent Pattern
The initializer session intercepts the high-level user prompt to establish a baseline repository state. It executes an `init.sh` script to configure the development server and expands the user request into a granular `test-results.json` requirements list. This list acts as a structural contract, preventing the agent from "one-shotting" and subsequently failing due to context exhaustion.

### 3.2 Feature-by-Feature Implementation
The harness strictly constrains the coding agent to a single discrete JSON-defined feature per session. This forces modular progress and ensures each unit of work is completed and committed before the next context window begins.

### 3.3 State Restoration & Progress Handoff
To bridge context gaps, the harness implements a dual-memory system:
*   **`claude-progress.txt` / `PROGRESS.md`:** A high-level state file maintained by the agent to record pending and completed tasks.
*   **`git log --oneline`:** Used as a technical recovery log to orient new sessions.
*   **`commit-on-stop.sh`:** A hook backstop that ensures all session work is persisted to the repository upon session termination.

### 3.4 Default-FAIL Contract
The companion repository, rather than the Anthropic article itself, enforces a "Done means Done" structural gate via `verify-gate.sh`.
*   All features in the contract default to `"passes": false`. 
*   The `track-read.sh` script monitors the environment for evidence (screenshots/logs).
*   A **PreToolUse hook** denies any write operation to the results file unless the agent has used the `Read` tool on evidence files in the current context.

### 3.5 Fresh-Context Evaluation & Operator Control
Validation is delegated to the `evaluator.md` subagent—an instance initialized with a fresh context window and no memory of the build process. It lacks `Write/Edit` tools, forcing an unbiased review of diffs and evidence. 
*   **`kill-switch.sh`:** Halts tool calls if an `AGENT_STOP` file is present.
*   **`steer.sh`:** Intercepts the loop to surface `STEER.md` contents for mid-run redirection.

## 4. Comparative Evidence Synthesis: Industry & Academic Benchmarks

| Source | Key Findings / Ground Truth |
| :--- | :--- |
| **Anthropic Research** | **Returns to Expertise:** Domain expertise (problem understanding) is the primary multiplier for success. Experts elicit 12 actions vs. 5 for novices per prompt. This validates the **Planner Agent** pattern as a tool to capture expertise before execution. |
| **METR** | **Time Horizon:** Measures task difficulty, not wall-clock speed. A "16-hour task" is a coherent unit of work for a human expert. Agents are **"several times faster than humans"** on successful tasks because they take fewer iterative actions. |
| **SWE-agent (Princeton)** | **Agent-Computer Interface (ACI):** Performance jumps are attributed to interfaces optimized for agents (e.g., specialized file editors) rather than standard human-centric CLI/UI tools. |
| **Agentless** | **Simple Pipeline:** Simple localize-repair-validate pipelines can outperform autonomous agents on routine bugs, suggesting complexity should only be reserved for long-horizon tasks. |

## 5. Technical Assessment: Kimi K3 and Kimi Code CLI
Kimi K3 is a 2.8T-parameter Mixture-of-Experts (MoE) model optimized for long-horizon agentic work.

*   **Architecture & Scaling:** Implements Kimi Delta Attention (KDA), SiTU-GLU activation, and a **Stable LatentMoE** framework. It activates **16 out of 896 experts** (104B parameters), achieving a 2.5× scaling efficiency improvement.
*   **Multimodality:** Uses the **MoonViT-V2** vision encoder (401M parameters) for native "vision-in-the-loop" testing, allowing the agent to verify UI state without OCR.
*   **Preserved Thinking History Mode:** Kimi K3 requires a specific session logic flow. The API returns `reasoning_content` which **must** be passed back in the `messages` array as-is for multi-turn sessions to maintain reasoning continuity.
*   **Internal Subagent Architecture:** Kimi Code utilizes Plan, Explore, and Coder subagents to isolate research and planning from the primary execution context.
*   **Deployment:** Supports **MXFP4 weights** and **MXFP8 activations** via quantization-aware training. Recommended engines: vLLM, SGLang, and TokenSpeed.

## 6. Repository Mapping: Integrating Patterns into `my-superpowers`
The repository already contains partial analogues, but not the full harness described by the X article:

*   `skills/execution/loop/` provides an iteration state file and an independent Stop-hook verifier.
*   `skills/quality/verification-before-completion/` provides the evidence-before-claim principle.
*   `skills/communication/handoff/` and `skills/communication/session-summary/` provide handoff-oriented documentation patterns.
*   `skills/execution/subagent-driven-development/` provides implementer/reviewer separation for focused tasks.
*   The repository does **not** currently contain `skill-handoff-manager`, `skill-fresh-evaluator`, or `skill-gatekeeper`; those are proposed extensions, not existing capabilities.

## 7. Prioritized Implementation Backlog

1.  **Technical Action:** Pilot a handoff template for one long-running workflow before adding automatic commit-on-stop hooks.
    *   **Associated Risk:** **Repository bloat** and meaningless commit history if the agent loops unsuccessfully. Reference the "Re-simplify on model upgrades" principle to prune these hooks as model intelligence increases.
    *   **Validation Criteria:** A fresh agent instance successfully restores context using only `git log` and `PROGRESS.md`.

2.  **Technical Action:** Add a small, reusable Default-FAIL contract example to the execution/quality skills.
    *   **Associated Risk:** **JSON syntax errors** if the agent improperly edits the results file.
    *   **Validation Criteria:** Agent is structurally unable to set `"passes": true` without a preceding `Read` operation on validated test output.

3.  **Technical Action:** Do not add Kimi-specific reasoning-history logic to this model-agnostic content repository. Benchmark a Kimi workflow separately if there is a concrete deployment need.
    *   **Associated Risk:** Context window degradation if `reasoning_content` is not properly handled in the message history.
    *   **Validation Criteria:** Model maintains reasoning consistency across three or more tool-use turns.

## 8. Source Reference List

### Primary Evidence
*   **Anthropic:** Effective harnesses for long-running agents (Nov 2025). https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
*   **Anthropic:** Agentic coding and persistent returns to expertise (Jun 2026). https://www.anthropic.com/research/claude-code-expertise
*   **METR:** Task-Completion Time Horizons of Frontier AI Models (May 2026). https://metr.org/time-horizons
*   **MoonshotAI:** Kimi-K3 Technical Report. https://github.com/MoonshotAI/Kimi-K3
*   **MoonshotAI:** Kimi Code CLI. https://github.com/MoonshotAI/kimi-cli
*   **Princeton (SWE-agent):** Agent-Computer Interfaces Enable Automated Software Engineering. https://arxiv.org/abs/2405.15793
*   **Agentless:** Agentless: Demystifying LLM-based Software Engineering. https://arxiv.org/abs/2407.01489
*   **Anthropic Repository:** Harness Primitives for Long-Running Claude Agents. https://github.com/anthropics/cwc-long-running-agents

### Commentary/Secondary Analysis
*   **Sprytix X Article:** The $1.2M Agent Engineering skill is now open source. https://x.com/Sprytixl/status/2087066798608752671 (Commentary/secondary source)
