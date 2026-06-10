# INVEST + SPIDR Reference

## INVEST Criteria

| Letter | Criterion | What It Means | Failure Sign |
|--------|-----------|---------------|--------------|
| **I** | Independent | Can be developed and delivered without another story | "This story requires US-002 to be done first" |
| **N** | Negotiable | Scope is a starting point, not a contract | Story has no flexibility — change is expensive |
| **V** | Valuable | Delivers standalone value to a user or the business | "As a developer, I want to…" with no user outcome |
| **E** | Estimable | Team can assign story points | "We don't know enough to estimate" |
| **S** | Small | Completable in one sprint | Points ≥ 8 before splitting |
| **T** | Testable | Has verifiable acceptance criteria | "System should feel responsive" |

---

## SPIDR Splitting Techniques

### 1. Spike (S)
**When:** The team has too much uncertainty to estimate.
**How:** Create a time-boxed research or prototyping story first. Output is knowledge (design doc, PoC, ADR), not production code.
**Example:**
- Original: "Integrate real-time notifications" (8 pts — too uncertain)
- Spike: "Research WebSocket vs SSE for real-time notifications" (2 pts, output: ADR)
- Story: "Implement WebSocket notification channel" (5 pts, uses ADR output)

### 2. Path (P)
**When:** A story covers multiple user flows or decision branches.
**How:** Split the happy path from alternative paths or error paths.
**Example:**
- Original: "User can log in" (includes forgot password, MFA, locked account)
- Split 1: "User logs in with email + password" (happy path)
- Split 2: "User resets forgotten password"
- Split 3: "User logs in with MFA"

### 3. Interface (I)
**When:** The same capability is needed across multiple channels or UIs.
**How:** Deliver one interface at a time.
**Example:**
- Original: "User can view their order history" (web + mobile)
- Split 1: "User views order history on web"
- Split 2: "User views order history on mobile app"

### 4. Data (D)
**When:** A story handles multiple data types, formats, or sources.
**How:** Deliver one data type or source at a time.
**Example:**
- Original: "User can import contacts" (CSV, vCard, Google Contacts)
- Split 1: "User imports contacts from CSV file"
- Split 2: "User imports contacts from vCard"
- Split 3: "User imports contacts from Google Contacts"

### 5. Rules (R)
**When:** Business logic has simple and complex variations.
**How:** Deliver the simple rule first, complex variations later.
**Example:**
- Original: "System calculates order total" (simple + bulk + loyalty + promo codes)
- Split 1: "System calculates order total (unit price × quantity)"
- Split 2: "System applies bulk pricing discount"
- Split 3: "System applies loyalty points redemption"
- Split 4: "System applies promotional codes"

---

## Story Format

```
As a [persona — role or JTBD situation],
I want to [specific action or capability],
so that [measurable outcome or benefit].
```

**JTBD variant (when persona is unclear):**
```
When [situation the user is in],
I want [motivation or goal],
so I can [outcome].
```

---

## Story Size Guide

| Points | Size | Description |
|--------|------|-------------|
| 1 | XS | Trivial change — a config, a label, a single-field validation |
| 2 | S | Small, well-understood, no surprises |
| 3 | M | Medium complexity, some design decisions |
| 5 | L | Large, multiple components or integration |
| 8 | XL | Too large — apply SPIDR before sprint planning |
| 13+ | XXL | Epic — must be decomposed |

> **Rule:** No story > 5 points enters a sprint without being split first.

---

## Forbidden Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| "As an admin, I want a dashboard" | Too broad — no single deliverable | Split by widget, metric, or user task |
| "As a user, I want everything to work" | No scope, not testable | Split by specific workflow |
| "As a developer, I want to refactor X" | No user value stated | Rephrase with business justification or use technical story format |
| No acceptance criteria | Not testable | Add ACs before backlog refinement |
| Acceptance criteria that reference UI mockups only | Mockups change; behavior must be specified | Rewrite as behavioral Given/When/Then |
| "The system should be fast / secure / easy to use" | Not testable | Write as NFR with measurable threshold |
