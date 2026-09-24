---
name: prompt-engineering-patterns
description: Use when writing or improving system prompts, agent definitions, or skill instructions — designing role prompts, fixing an agent that ignores instructions, structuring output contracts, or when asked "write a prompt for X" or "why does my agent not do Y"
---

# Prompt Engineering Patterns

Patterns for writing system prompts, agent definitions, and skill instructions
that models actually follow. Apply the smallest set that fixes the problem.

## Structure patterns

- **Role → context → method → output contract.** Open with who the agent is and
  the single sentence that changes its behavior. Put routing ("use when…") in
  the frontmatter description, never in the body — the body is read after
  routing already happened.
- **Lead with the decision, not the background.** Models weight early tokens;
  the first paragraph should contain the rule that matters most.
- **Say what TO do, then the boundary.** "Read only the supplied paths; do not
  broaden the search" beats a page of restrictions with no positive instruction.
- **One instruction, one place.** The same rule stated twice with different
  wording invites the model to follow the weaker version.

## Behavior patterns

- **Show the procedure as numbered steps** when order matters; as a checklist
  when completeness matters. Prose hides steps; models skip prose.
- **Give an output contract** — exact sections, field names, or a format
  skeleton. "Report findings" produces essays; the contract produces reports.
  Include one worked example for formats a model gets wrong.
- **State the empty/degenerate case** — what to output when there are no
  findings, no input, or the evidence is missing. Otherwise the model invents
  content to fill the shape.
- **Name the failure you are preventing.** "Do not treat a green pipeline as
  proof the fix landed — grep the diff" works because it names the exact wrong
  behavior. Abstract warnings ("be careful") do nothing.

## Anti-patterns

- **ALL-CAPS NEVER/ALWAYS stacking** — rigid directives decay into noise;
  explain *why* instead and the model generalizes correctly to new cases.
- **Persona fluff** ("you are the world's greatest…") — role definition helps
  only when it changes behavior ("you are a reviewer; you do not edit files").
- **Everything is critical** — when ten rules are marked critical, none are.
  Rank implicitly by position and specificity.
- **Instructions the context can't satisfy** — an agent told to "always run the
  full test suite" without test-running tools will hallucinate results. Only
  instruct what the tools allow; verify tool access matches the prompt.

## Debugging an agent that misbehaves

1. Find the transcript failure and ask which instruction should have caught it.
2. If none exists — add the specific rule naming this exact behavior.
3. If the rule exists — it is buried, ambiguous, or contradicted elsewhere;
   move it earlier, make it concrete, remove the contradiction.
4. If the rule is correct but ignored — shrink the prompt (diluted prompts lose
   rules) or convert the rule into a verifiable output contract.

## Verification

A prompt change is done when a fresh run on the failing case produces the
correct behavior — not when the prompt reads better. Keep the failing case as a
regression example when practical.

## Cost and cache patterns (2026-09-24)

- **Instruction churn burns prompt-cache money** (@neil_xbt,
  x.com/neil_xbt/status/2100984702492405891): a *stable* instruction set rides
  the prompt cache (~1/10 the cost of fresh input); instructions edited every
  session pay full price on every turn. Batch instruction edits into
  consolidation cycles instead of tweaking per session. Skill descriptions that
  are too broad "false-fire" in unrelated turns and eat context — keep the
  description a routing rule for what the skill can actually do.
- **Trigger Audit + Dedupe Pass** (same source): periodic audit with two passes
  — (1) Trigger Audit: each skill/rule description fires only for what it can
  actually do; (2) Dedupe Pass: collapse duplicated rules, but **never** collapse
  commands, paths, URLs, or never/must rules — those are load-bearing literals.
- **Grade agents from tool-call trajectory, not their summary**
  (Google Cloud Tech, x.com/GoogleCloudTech/status/2102068464512864475): an
  LLM-as-judge reading only the final message marked 3 prompts red that actually
  passed — the agent did the work but didn't brag about it in the summary. If a
  rubric asks "did it run X?", the judge must read the raw tool-call log. And
  don't flatten telemetry into a single event sequence: it hides concurrent tool
  dispatch, a leading cause of behavioral bugs. (Corroborates the
  verification-before-completion rule that agent self-reports need external
  evidence.)
