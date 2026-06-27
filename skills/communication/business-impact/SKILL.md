---
model: sonnet
name: business-impact
description: >
  Translates a technical proposal, change, or incident into quantified business impact:
  revenue at risk, customer churn %, uptime hours, cost per hour of downtime, or
  developer productivity delta. Teaches engineers to pitch the operational consequence,
  not the technical mechanism. "You don't pitch database optimization — you pitch
  preventing life-threatening delays and $50k/hr losses." Trigger on /business-impact
  or when a technical proposal needs to be justified to non-engineering stakeholders.
---

# Business Impact

Reframe technical work as business consequences. Stakeholders do not act on
engineering metrics — they act on revenue, churn, uptime, and cost.

The container terminal analogy: at 12% capacity, operations generate $50,000/hour.
A server going hot halts the crane offloading 10,000 containers. You do not pitch
"database optimization" to the terminal operator. You pitch preventing life-threatening
delays and $50k/hr losses. The technical mechanism is irrelevant to the decision.

In highly effective tech companies, reward is tied to landed business impact, not
engineering purity. Building the largest Kubernetes cluster = $0 value. Reducing
customer churn 4% via API optimization = promoted.

## When to invoke

- A technical proposal needs budget, headcount, or executive approval
- An incident post-mortem must be communicated to leadership
- Tech debt or refactoring work needs to be prioritized on a roadmap
- A performance improvement needs a business case
- An engineer is describing their work in terms of "elegance" or "correctness" to
  a business audience
- `/business-impact` is typed

## Impact dimensions

For any technical work, identify which of these it affects and quantify it:

| Dimension | How to express it |
|---|---|
| **Revenue** | $/hour at risk, conversion rate delta, deals unblocked |
| **Churn** | % of users hitting this, estimated churn risk per % affected |
| **Uptime** | Minutes/hours of downtime × MAU or revenue per hour |
| **Cost** | Infrastructure cost reduction, engineering hours saved per week |
| **Developer velocity** | Features unblocked, deployment frequency change, on-call burden |
| **Risk** | Regulatory exposure, data breach blast radius, SLA penalty |

## Workflow

### 1. Identify the technical change
State the change in one technical sentence (internal — this does not appear in output).

### 2. Find the operational consequence
Ask: if this change does NOT happen, what does the user or business experience?
Work from the physical/operational world inward:
- What does the end user see or fail to do?
- What does the operator's workflow look like when this breaks?
- What is the cost per hour/day of that failure state?

### 3. Anchor to a number
Even rough numbers are better than none. Use:
- Known uptime figures (hours × revenue per hour)
- Publicly known or internally stated ARR (1% churn on $10M ARR = $100k)
- Engineering time (X hours/week × fully-loaded hourly cost)
- Industry benchmarks when internal numbers are unavailable (flag when using these)

### 4. Reframe the pitch
Replace the technical mechanism with the business consequence:

| Instead of... | Say... |
|---|---|
| "We need to optimize the query" | "The checkout page times out for 8% of users during peak hours, costing ~$X in abandoned carts daily" |
| "We should refactor the auth module" | "Every new OAuth provider takes 3 engineer-weeks; we've declined 2 partnership integrations this quarter because of it" |
| "The p99 latency is 2.4s" | "1 in 100 users sees a 2.4s stall on the primary action — industry data shows >2s increases abandonment by 12%" |
| "We're accumulating tech debt" | "We ship 1 feature per sprint instead of 3; the delta is costing us ~6 weeks of roadmap per quarter" |

### 5. Name the investment ask
State what is needed (time, headcount, infrastructure cost) against what it unlocks.
This is the close:
> "2 engineer-weeks to fix the checkout timeout unlocks an estimated $X/month in
> recovered conversions."

## Output format

```
## Business Impact

**Technical change:** [one sentence, internal framing]
**Business consequence if deferred:** [what the user/operator experiences]

**Impact quantification:**
- [dimension]: [number or range] — [how derived]
- [dimension]: [number or range] — [how derived]

**The pitch:**
[2–3 sentences in plain business language. No function names, no architectural terms.
Lead with the operational pain; end with what the investment unlocks.]

**Investment ask:** [time / cost] → [what it unlocks]
```

## Rules

- Never invent numbers. If no data is available, state the range and its source
  ("industry benchmark", "rough estimate based on MAU × conversion rate").
- Never strip the technical summary entirely — it lives as one internal sentence for
  alignment, not for the stakeholder audience.
- The pitch must not contain: function names, file paths, DB table names, framework names,
  architectural pattern names, or latency in milliseconds without a business translation.
- If the impact is genuinely unclear or unquantifiable, say so explicitly rather than
  manufacturing a number. "We cannot quantify this yet — here is what we would need
  to measure" is a valid output.
- Do not advocate for the change — present the trade-off and let the stakeholder decide.
