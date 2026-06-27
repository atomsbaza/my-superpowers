---
model: sonnet
name: benchmark-sprint
description: >
  Uses parallel AI agents to benchmark N architectural variants simultaneously and
  produce a comparison report in minutes. Implements the "3 days → 20 minutes"
  pattern from multiplying architectural output: instead of manually testing cache
  key structures, data access patterns, API designs, or query strategies one by one,
  spawn one agent per variant and collect structured results concurrently. Trigger on
  /benchmark-sprint when comparing 2+ architectural approaches that can be tested
  independently.
---

# Benchmark Sprint

Replace manual multi-day architectural benchmarking with a parallel agent fleet.
Each variant gets its own agent. They run concurrently. You get a comparison
report in minutes instead of days.

At GitHub, prompting agents to test different data access patterns and analyze their
impact on Redis turned 3 days of manual testing into 20 minutes. AI is not just for
writing functions — it is a strategic tool for rapid architectural benchmarking.

## When to invoke

- Comparing 2+ cache key structures, DB index strategies, or query patterns
- Evaluating multiple API design alternatives before committing
- Testing different serialization formats, data models, or access patterns
- Any decision where "let's prototype both and see" is the right answer but
  the cost of doing it sequentially is too high
- `/benchmark-sprint` is typed

## What makes a good benchmark-sprint candidate

**Good fit:**
- Variants are independent (testing A does not affect testing B)
- Each variant can be evaluated against a concrete, measurable criterion
- The decision is reversible (choosing wrong is expensive but recoverable)
- 2–6 variants exist (more than 6 and the synthesis stage becomes complex)

**Poor fit:**
- Variants share mutable state or a live database (agents would interfere)
- The correct answer is already known and this is rationalization
- The evaluation criterion is purely subjective ("which looks cleaner")

## Workflow

### 1. Define the variants
State each variant precisely. Give each a short label (A, B, C or a descriptive name).
Each variant description must include:
- What specifically differs from the others
- What the agent should implement or simulate
- Any constraints (must stay compatible with X, must run on Y)

### 2. Define the evaluation criteria
State what "better" means before the agents run. Do not let agents define the
criteria — they will optimize for different things if left unconstrained.

Examples:
- Throughput under N concurrent requests
- Latency at p50, p95, p99
- Lines of code to implement a new integration
- Number of DB queries for a common operation
- Memory footprint under a defined load profile
- Time to implement + test a defined feature

### 3. Dispatch agents in parallel
Each agent receives:
- The variant specification (what to implement/simulate/analyze)
- The evaluation criteria (what to measure)
- The constraints (what must not change)
- The output format (structured — see below)

Agents run concurrently via the Agent tool or Workflow with `parallel()`.

### 4. Collect and synthesize
After all agents return, produce a comparison table and a verdict.

## Agent prompt template

Use this structure for each agent, substituting the variant details:

```
You are benchmarking [VARIANT_NAME] for [PROBLEM_STATEMENT].

## Variant specification
[Exact description of this variant — what to implement, configure, or simulate]

## Evaluation criteria
Measure and report ONLY these metrics:
- [metric 1]: [how to measure it]
- [metric 2]: [how to measure it]

## Constraints
- [constraint 1]
- [constraint 2]

## Output format (strict)
Return a JSON object with this exact shape:
{
  "variant": "[VARIANT_NAME]",
  "metrics": {
    "[metric_1_key]": <value>,
    "[metric_2_key]": <value>
  },
  "tradeoffs": ["[one tradeoff]", "..."],
  "blockers": ["[anything that prevented measurement]"],
  "recommendation": "[recommend / do not recommend / conditional]",
  "recommendation_reason": "[one sentence]"
}
```

## Synthesis

After all agents return, produce:

```
## Benchmark Sprint Results

**Problem:** [what was being benchmarked]
**Variants tested:** [N]
**Criteria:** [list]

### Results table

| Variant | [metric 1] | [metric 2] | Recommendation |
|---|---|---|---|
| A | ... | ... | recommend / conditional / no |
| B | ... | ... | ... |

### Verdict
**Winner:** [variant] — [one sentence reason]
**Runner-up:** [variant] — [one sentence on when to prefer it instead]
**Eliminated:** [variant] — [one sentence on the disqualifying finding]

### Trigger conditions
When to revisit this decision: [specific metric or load condition that would change
the verdict]
```

## Rules

- Define evaluation criteria before dispatching agents, not after. Criteria defined
  after results are available are post-hoc rationalization.
- If an agent returns a blocker (could not measure the criterion), surface it in the
  results table — do not silently drop the variant.
- The verdict must pick a winner. "It depends" without a default recommendation
  is not a useful output. State the default and the conditions under which the
  runner-up is preferred.
- Benchmark sprints answer "which is better for our current context" — they do not
  answer "which is architecturally correct in the abstract." Keep the verdict grounded
  in the specific criteria and load profile tested.
- If fewer than 2 variants exist, this skill is not needed — there is nothing to
  compare. Say so and stop.
