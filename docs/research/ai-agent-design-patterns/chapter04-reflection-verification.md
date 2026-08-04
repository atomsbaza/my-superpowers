# Reflection & Self-Verification

Both patterns in this chapter trade latency and inference cost for correctness by adding a second pass over the agent's own output before it is treated as final. They differ in *what* they check: Reflection critiques quality and reasoning; Self-Verification checks a narrower, often mechanically checkable claim (does this SQL parse, does this total sum correctly).

## 1. Reflection Pattern

**Definition.** Before returning a response, the agent (or a second model call) critiques the draft answer, then produces an improved version. Flow: Draft → Review → Improve → Final Response.

**When to use it.** Tasks where output quality benefits from a second, more critical pass — open-ended writing, complex reasoning chains, code generation — where a single-pass answer plausibly contains an error a fresh read would catch.

**Production tradeoffs.** Reflection roughly doubles (or more) the inference cost and latency of the interaction, since it's at minimum two model calls instead of one. It measurably improves output quality and logical consistency, but the improvement is bounded by whether the critiquing pass has a genuinely different vantage point — a reflection pass using the same model, same context, and no additional grounding information often just re-states the same reasoning with more confidence rather than catching a real error. The strongest implementations pair Reflection with retrieved ground truth or a distinct evaluation rubric rather than relying on undirected self-critique.

```csharp
var draft = await kernel.InvokePromptAsync(userPrompt);
var review = await kernel.InvokePromptAsync($"Review this answer.\n\n{draft}\n\nImprove accuracy and clarity.");
```

## 2. Self-Verification Pattern

**Definition.** The agent validates its own output against an explicit, often mechanically checkable rule before using or returning it — e.g. validating generated SQL syntax, checking that a financial calculation's totals reconcile, or confirming a tool call's parameters satisfy a schema — retrying if the check fails.

**When to use it.** Domains where correctness is checkable by a deterministic rule, not just plausible-sounding: code generation, SQL generation, financial calculations, structured data extraction. This is the pattern that converts probabilistic generation into something closer to a deterministic contract.

**Production tradeoffs.** Self-Verification is cheaper and more targeted than Reflection when a deterministic check exists, because the check itself doesn't require another model call — only the *retry* does, and only on failure. Its ceiling is the quality of the check: a self-verification loop is only as good as its validator, and a validator that merely re-asks the model "is this correct?" without an external ground truth inherits the same blind spots as the original generation.

```csharp
var sql = await kernel.InvokePromptAsync("Generate SQL");
bool valid = SqlValidator.Validate(sql);
if (!valid)
{
    sql = await kernel.InvokePromptAsync($"Fix this SQL:\n{sql}");
}
```

## 3. The Critic/Evaluator Pattern in Multi-Agent Systems

In multi-agent architectures, both patterns generalize into a dedicated **Critic** or **Evaluator agent**: rather than an agent critiquing itself, a structured payload is routed to a separate agent tasked with verifying correctness against objective guidelines or ground-truth documentation. Malformed or incorrect outputs are rejected and routed back to the producing agent with structured feedback for iterative correction, and the workflow only proceeds once a quality threshold is met. This is one of the concrete mitigations for task-verification failures identified in the MAST taxonomy (see [Chapter 10](chapter10-anti-patterns-failure-modes.md)), where "incorrect self-verification" and "incomplete quality checks" account for a meaningful share of observed multi-agent failures.

**Design guidance:** bound these loops with an explicit step budget (e.g. `max_iter=3`). An unbounded reflection or verification loop that never converges is not a safety net — it's a silent cost and latency sink, and production systems should hard-kill the loop and escalate to a Human-in-the-Loop exception ([Chapter 6](chapter06-control-safety-patterns.md)) rather than retry indefinitely.
