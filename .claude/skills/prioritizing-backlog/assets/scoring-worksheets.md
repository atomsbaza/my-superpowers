# Backlog Prioritization Scoring Worksheets

## RICE Scoring Worksheet

### Formula
`RICE Score = (Reach × Impact × Confidence) / Effort`

### Scale Reference

| Factor | Value | Meaning |
|--------|-------|---------|
| **Reach** | Actual number | Users/requests affected per quarter |
| **Impact** | 3.0 | Massive — changes core user behavior |
| **Impact** | 2.0 | High — significant improvement to key flow |
| **Impact** | 1.0 | Medium — noticeable improvement |
| **Impact** | 0.5 | Low — small improvement |
| **Impact** | 0.25 | Minimal — edge case improvement |
| **Confidence** | 100% | Based on validated data (user research, analytics) |
| **Confidence** | 80% | Based on reasonable assumptions |
| **Confidence** | 50% | Best guess — limited data |
| **Effort** | Person-months | Engineering team estimate |

### Worksheet

| Feature / Epic | Reach | Impact | Confidence | Effort | Score | Notes |
|---|---|---|---|---|---|---|
| | | | | | =R×I×C/E | |
| | | | | | | |
| | | | | | | |

---

## WSJF Scoring Worksheet (SAFe)

### Formula
`WSJF = Cost of Delay / Job Duration`

`Cost of Delay = User/Business Value + Time Criticality + Risk Reduction/Opportunity Enablement`

### Scale Reference (Fibonacci: 1, 2, 3, 5, 8, 13, 20)

**User/Business Value:**
| Score | Meaning |
|-------|---------|
| 20 | Provides extraordinary value; competitors do not have it |
| 13 | Critical to business outcomes |
| 8 | Very important; users request frequently |
| 5 | Important but not urgent |
| 3 | Moderate value |
| 1–2 | Minimal value |

**Time Criticality:**
| Score | Meaning |
|-------|---------|
| 20 | Fixed deadline (regulatory, contractual, market window) |
| 13 | Significant decay — value drops quickly if delayed |
| 8 | Moderate decay |
| 3–5 | Low urgency |
| 1–2 | No time pressure |

**Risk Reduction / Opportunity Enablement:**
| Score | Meaning |
|-------|---------|
| 20 | Eliminates existential risk or enables major opportunity |
| 13 | Reduces significant risk or enables important capability |
| 8 | Moderate risk/opportunity |
| 3–5 | Low |
| 1–2 | Negligible |

**Job Duration (Size):**
| Score | Meaning |
|-------|---------|
| 20 | Very large — months of work |
| 13 | Large |
| 8 | Medium-large |
| 5 | Medium |
| 3 | Small |
| 1–2 | Very small |

### Worksheet

| Feature | User Value | Time Crit. | Risk/OE | CoD Total | Job Size | WSJF | Rank |
|---|---|---|---|---|---|---|---|
| | | | | =U+T+R | | =CoD/Size | |

---

## MoSCoW Sprint Scope Worksheet

### Capacity Planning
**Total sprint capacity:** _____ story points
**Must capacity (max 60%):** _____ points
**Should capacity (max 20%):** _____ points
**Could capacity (max 20%):** _____ points

### Classification

| ID | Title | MoSCoW | Points | Rationale |
|---|---|---|---|---|
| | | Must | | |
| | | Should | | |
| | | Could | | |
| | | Won't | | |

**Must total:** _____ / _____ capacity (should be ≤ 60%)

---

## Kano Classification Worksheet

### Survey Questions (for each feature)
Ask users two questions:
1. **Functional:** "If this feature is present, how do you feel?" (1=Dislike, 2=Tolerate, 3=Neutral, 4=Expect, 5=Delight)
2. **Dysfunctional:** "If this feature is absent, how do you feel?" (1=Dislike, 2=Tolerate, 3=Neutral, 4=Expect, 5=Delight)

### Classification Matrix

| Functional↓ / Dysfunctional→ | Dislike | Tolerate | Neutral | Expect | Delight |
|------------------------------|---------|----------|---------|--------|---------|
| **Delight** | Q | A | A | A | O |
| **Expect** | R | I | I | I | A |
| **Neutral** | R | I | I | I | A |
| **Tolerate** | R | I | I | I | A |
| **Dislike** | R | R | R | R | Q |

> A = Attractive (Delighter), O = One-dimensional (Performance), M = Must-be (Basic), R = Reverse, I = Indifferent, Q = Questionable

### Classification Results

| Feature | Category | Priority Action |
|---|---|---|
| | Must-be | Ship before launch; table stakes |
| | Performance | Include in roadmap; drives satisfaction |
| | Delighter | Ship when capacity allows; competitive advantage |
| | Indifferent | Defer or cut |
| | Reverse | Do not build |

---

## Impact / Effort Matrix (Quick Sort)

Place each item in a quadrant:

```
HIGH IMPACT │ Quick Wins    │ Major Projects
            │ Do first ✅   │ Schedule 📅
────────────┼───────────────┼───────────────
LOW IMPACT  │ Fill-ins      │ Time Sinks
            │ When free 🕐  │ Cut or defer ❌
            │               │
            └───────────────┴───────────────
              LOW EFFORT      HIGH EFFORT
```

| ID | Feature | Impact | Effort | Quadrant | Action |
|---|---|---|---|---|---|
| | | H/L | H/L | Quick Win / Major / Fill-in / Time Sink | |
