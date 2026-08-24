---
name: agent-change-locality
description: Evaluate AI-assisted changes for locality, proportionate boundaries, and evidence-backed refactoring decisions.
triggers: AI refactor, agent change locality, review agent diff, too many files to change, should I split this module, SOLID for AI coding
---

# Agent Change Locality

## When to use

Use this skill when an AI-assisted task or diff may be crossing too many module
boundaries, adding speculative abstractions, creating shallow/pass-through
layers, or making a small behavior change require too much repository context.
Use it for new design, existing-code refactors, agent-diff reviews, and
post-change locality audits.

This is a read-first assessment skill. Its goal is not to assign a SOLID score;
it is to produce an evidence-backed decision to keep, split, deepen, or
merge/inline a boundary while keeping abstraction discovery under human control.

This is a behavioral guide, not production code. It does not grant credentials,
permissions, API access, or tool access automatically.

## How to invoke

Direct invocation:

```text
$agent-change-locality
Task: Review whether this AI-generated refactor keeps the change local.
```

Natural-language fallback:

```text
Use agent change locality to review this AI-generated diff and recommend whether
to keep, split, deepen, or merge the affected boundary.
```

## Composition

Compose with these existing skills rather than redefining their vocabulary or
procedures:

- `codebase-design` for modules, interfaces, seams, the deletion test, and
  approval boundaries;
- `deep-module-design` for information hiding, deep interfaces,
  pass-through detection, and locality verification;
- `code-review` for changed-line smells such as divergent change, shotgun
  surgery, speculative generality, and middle man.

Do not create a second definition of module, interface, seam, depth, or
locality.

## Workflow

### 1. Establish scope and evidence

1. Restate the requested behavior and the exact assessment boundary.
2. Classify the task as a new design, existing-code refactor, agent-diff review,
   or post-change audit.
3. Read the smallest relevant code scope, current diff when present, callers,
   tests, standards, ADRs, and recent history when available.
4. Record missing evidence explicitly. Do not infer business rules from names
   alone.
5. Mark generated churn, deleted or skipped tests, and files outside the task
   boundary as separate evidence.

### 2. Map pressure and locality

1. List the distinct reasons each affected module changes. Responsibility is
   about reasons to change, not method count or file length.
2. Trace one representative behavior from entry point to side effect or result.
3. Count the files and symbols needed to explain that behavior. Treat the count
   as a smell signal, never as a hard threshold.
4. Identify leaked decisions: formats, protocols, algorithms, lifecycle,
   timing, error policy, configuration, and ownership that callers must know.
5. Apply the deletion test to each abstraction: would removing it move
   meaningful complexity into callers, or merely remove a pass-through layer?
6. Compare the requested scope with the actual diff and identify unrelated
   edits or change amplification.

### 3. Compare proportionate boundary options

Compare at least two options when the boundary decision is non-trivial:

- **Keep local:** make the smallest direct change while preserving a coherent
  module.
- **Split:** separate genuinely different reasons to change when divergent
  change is evidenced.
- **Deepen:** hide a consequential decision behind a smaller, more useful
  interface.
- **Merge/inline:** remove a shallow abstraction or middle-man layer when it
  hides no meaningful decision.
- **Introduce a seam:** use DIP or an adapter only when a concrete variation,
  second consumer, test boundary, or ownership boundary justifies it.

For every option, state affected scope, hidden or exposed decisions, migration
risk, verification seam, and reversibility. Prefer incremental changes over
rewrites.

### 4. Apply SOLID as conditional diagnostics

- **SRP:** report multiple independent reasons to change; do not require one
  function or one class per file.
- **DIP:** report concrete coupling only when it blocks a real variation, test
  boundary, or ownership boundary. Direct coupling may be the simpler choice.
- **OCP:** report repeated expansion of a stable conditional only when a real
  variation axis is recurring.
- **LSP:** report a substitutability violation when an implementation cannot
  honor the consumer's contract. Do not introduce inheritance merely to use
  polymorphism.
- **ISP:** report a consumer forced to depend on unused contract surface. Do
  not split interfaces without an affected consumer.

### 5. Produce an approval-gated result

Return a compact report with:

1. **Decision:** keep, split, deepen, merge/inline, or insufficient evidence.
2. **Evidence:** concrete files, symbols, callers, diff hunks, tests, or
   history.
3. **Reasoning:** change reasons, locality, leaked decisions, and applicable
   conditional principles.
4. **Options considered:** at least two when the decision is non-trivial.
5. **Recommended boundary:** what callers should know and what the module
   should hide.
6. **Expected change scope:** files likely to change and files that should
   remain untouched.
7. **Verification plan:** targeted tests, diagnostics, diff-scope checks, and
   regression checks.
8. **Human decisions required:** domain or architecture choices the Agent must
   not silently make.
9. **Evidence status:** `VERIFIED`, `PARTIAL`, or `UNVERIFIED` for each area.

If implementation is requested, stop at the report and request explicit approval
for the selected option before using write-capable tools.

## Guardrails

- A file-count or three-file heuristic prompts investigation; it never causes
  an automatic failure.
- A single implementation is not evidence that an interface is wrong. Inspect
  the decision it hides and the seam it provides.
- A smaller class is not automatically a better module. Prefer depth and
  coherent leverage over class count.
- Do not manufacture a second consumer, future variation, or domain rule.
- Do not accept unrelated diff scope merely because the prompt was broad.
- Do not hide errors, reduce observability, weaken tests, or delete failing
  tests to make a boundary look clean.
- If code, task, or history is unavailable, report the evidence gap and remain
  `UNVERIFIED`.
- Do not automatically refactor, commit, push, or alter repository state during
  assessment.
- Respect the project's permissions, security policy, repository policy, and
  approval gates.
- Never copy credentials, tokens, browser state, private transcripts, runtime
  databases, or unrelated project source as part of this skill.

## Smoke scenarios

Use these bounded scenarios when validating the skill:

1. A module handles calculation, rendering, and persistence: recommend a
   proportionate split based on independent change reasons.
2. A stable concrete dependency has no real variation or test seam: do not
   invent DIP or an interface.
3. A feature travels through several pass-through files: consider merge/inline
   and explain the deletion-test evidence.
4. A valid change touches unrelated files or weakens tests: flag scope drift
   and require verification.

The skill is successful when it distinguishes facts from recommendations, does
not enforce SOLID mechanically, presents trade-offs for non-trivial boundaries,
stops before mutation without approval, and names unresolved evidence gaps.

## Portable verification

After copying the skill to a runtime's supported skills directory:

1. Confirm the `SKILL.md` file exists in that directory.
2. Start a new session or reload skills using the runtime's supported mechanism.
3. Invoke `$agent-change-locality` directly or use the natural-language fallback.
4. Run the four smoke scenarios with bounded synthetic examples.
5. Record Pass/Fail and evidence separately from fresh-session routing evidence.
