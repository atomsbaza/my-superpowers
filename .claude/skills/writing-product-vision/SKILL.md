---
name: writing-product-vision
description: >
  Creates a product vision statement and vision board from business goals,
  stakeholder input, or initial product ideas. Produces a one-sentence
  elevator pitch, a Geoffrey Moore-format vision statement, target customer
  definition using JTBD, and a Now/Next/Later north-star roadmap direction.
  Use when starting a new product, rebranding, or realigning the team.
  Trigger keywords: vision, product vision, north star, product purpose,
  vision board, elevator pitch, mission statement, why are we building this.
---

## Purpose

Give the team a shared, written product north star that answers: Who is the customer? What problem do we solve? Why us? What does success look like in 1–3 years?

## Input

Accept any of:
- Business goal or executive brief
- Existing BRD/PRD to distill vision from
- Direct user description of the product idea

If the user provides nothing, ask: "What is the product idea, business opportunity, or problem you want to solve?"

## Process

### Step 1 — Extract Core Elements

From the input, identify:
- **Primary customer:** Who has the problem? (Role, context, not demographics)
- **Problem statement:** What pain or friction exists today?
- **Current solution gap:** Why do existing solutions fall short?
- **Proposed solution:** What does this product do differently?
- **Business outcome:** Revenue, retention, efficiency, or other measurable goal?

If any element is unclear, ask one focused question before proceeding.

### Step 2 — Write the Vision Statement

Use Geoffrey Moore's Positioning Statement format:

```
FOR [target customer]
WHO [has this problem or need],
[Product Name] IS A [product category]
THAT [key benefit / reason to choose].
UNLIKE [current alternative],
OUR PRODUCT [primary differentiator].
```

Then write a one-sentence version (the elevator pitch):

> "[Product name] helps [target customer] [achieve outcome] by [key mechanism]."

### Step 3 — Define the Target Customer (JTBD)

Write a primary and secondary Job-to-be-Done:

```
Primary JTBD:
When [situation the customer is in],
I want to [the motivation or goal],
So I can [the outcome they're trying to achieve].

Secondary JTBD (optional):
When [situation],
I want to [motivation],
So I can [outcome].
```

Avoid demographic descriptions ("35-year-old male"). Use situational framing.

### Step 4 — Write the Vision Board

```markdown
# Vision Board: [Product Name]

## Elevator Pitch
[One sentence]

## Vision Statement
FOR [target customer] WHO [need]...
[Full Moore format]

## Target Customer
**Primary JTBD:** When [situation], I want [motivation], so I can [outcome].

## Key Business Goals
1. [Goal 1 — measurable, e.g., "Increase customer retention by 20% in 12 months"]
2. [Goal 2]
3. [Goal 3]

## What Success Looks Like (12 months)
- [Metric 1: e.g., 10,000 MAU]
- [Metric 2]
- [Metric 3]

## North Star Themes
| Horizon | Theme | Why |
|---------|-------|-----|
| Now (0–3 mo) | [Theme] | [Business rationale] |
| Next (3–9 mo) | [Theme] | [Business rationale] |
| Later (9–18 mo) | [Theme] | [Business rationale] |

## What We Are NOT Building
- [Explicit exclusion 1 — reduces scope creep]
- [Explicit exclusion 2]

## Open Questions
- [Question 1 that must be answered before PRD]
- [Question 2]
```

### Step 5 — Write Output File

Save to `docs/product/vision.md`. Create the directory if it doesn't exist.

Update `.po-workflow-state.json`:
```json
{
  "current_phase": "vision",
  "last_artifact": "docs/product/vision.md",
  "product_vision": "[one-sentence elevator pitch]",
  "target_customer": "[primary JTBD summary]",
  "business_goals": ["goal 1", "goal 2"],
  "open_questions": ["question 1"],
  "last_updated": "[ISO 8601 timestamp]"
}
```

## Quality Check

Before finalizing, verify:
- [ ] Vision statement answers: who, problem, differentiator
- [ ] At least one measurable success metric defined
- [ ] JTBD is solution-agnostic (no technology named)
- [ ] "What we are NOT building" section exists
- [ ] Open questions are listed (not buried in prose)
