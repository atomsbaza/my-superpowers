---
name: analyzing-requirements
description: >
  Analyzes a BRD, PRD, requirements document, product specification, or feature
  brief and produces a structured intake artifact. Use when the user provides
  a requirements document, business requirements, product specification, or
  feature brief that needs to be broken down before design or implementation
  begins. Outputs to workflow-state.json for downstream skills to consume.
---

## Purpose

Transform raw business or product requirements into a structured artifact that a principal engineer can act on directly. Every engagement that involves a requirements document must pass through this skill before design or coding begins.

## Input

Accept requirements as any of:
- A file path to read (BRD, PRD, feature spec, user story document)
- Pasted text in the conversation
- A combination of both

If no requirements are provided, ask: "Please share the BRD, PRD, or feature specification — either paste it or give me a file path."

## Process

Work through the document in this order:

### 1. Bounded Context Identification

Identify the distinct business domains the requirements touch. For each bounded context:
- Name it (e.g., `OrderManagement`, `InventoryTracking`, `UserIdentity`)
- Describe its responsibility in one sentence
- List the entities it owns
- Note which other contexts it depends on or collaborates with

### 2. Functional Requirements Extraction

List every functional requirement as a numbered, testable statement:
- Use the form: "The system shall [do X] when [condition Y]"
- Flag any requirement that is ambiguous or untestable with `[AMBIGUOUS]`
- Group by bounded context

### 3. Non-Functional Requirements Extraction

Extract or infer NFRs across these dimensions:
- **Performance:** response time targets, throughput, query SLAs
- **Availability:** uptime targets, DR requirements
- **Scalability:** expected data volume, concurrent users, growth rate
- **Security:** auth requirements, data sensitivity, compliance (GDPR, etc.)
- **Observability:** logging, metrics, tracing expectations
- **Maintainability:** deployment frequency, team size constraints

If an NFR is not stated but implied (e.g., a payment feature implies PCI concern), surface it explicitly as `[INFERRED]`.

### 4. Open Questions

List every ambiguity, contradiction, or missing detail as a numbered question. Be specific: quote the problematic text. Prioritize by impact — BLOCKER questions (cannot proceed without answer) first, then CLARIFYING (can proceed with assumption).

### 5. Recommended ADRs

Based on the requirements, list the architecture decisions that must be made before implementation. For each:
- State the decision to be made
- State why it is architecturally significant
- Suggest 2–3 options to consider (not the decision itself — that comes in the ADR skill)

## Output

Write a `workflow-state.json` file in the project root (create if missing, update if exists) with this structure:

```json
{
  "stage": "requirements_analyzed",
  "requirements_analysis": {
    "source": "<file path or 'inline'>",
    "bounded_contexts": [
      {
        "name": "string",
        "responsibility": "string",
        "entities": ["string"],
        "dependencies": ["string"]
      }
    ],
    "functional_requirements": [
      {
        "id": "FR-001",
        "context": "string",
        "statement": "string",
        "status": "clear | ambiguous"
      }
    ],
    "non_functional_requirements": {
      "performance": "string",
      "availability": "string",
      "scalability": "string",
      "security": "string",
      "observability": "string",
      "maintainability": "string"
    },
    "open_questions": [
      {
        "id": "Q-001",
        "priority": "blocker | clarifying",
        "quote": "string",
        "question": "string"
      }
    ],
    "recommended_adrs": [
      {
        "title": "string",
        "why_significant": "string",
        "options_to_consider": ["string"]
      }
    ]
  },
  "history": []
}
```

Also print the full analysis to the conversation as a well-formatted markdown document so the user can review it immediately.

## Validation

Before finishing, verify:
- Every bounded context has at least one entity
- Every `[AMBIGUOUS]` requirement has a corresponding open question
- At least one ADR is recommended for any feature involving persistence, external APIs, or auth
- NFRs are present even if inferred
