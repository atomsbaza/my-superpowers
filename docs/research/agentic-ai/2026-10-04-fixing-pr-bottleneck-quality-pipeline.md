# Fixing the PR Bottleneck with a Layered Agent Quality Pipeline (2026-10-04)

Source: Matt Pocock, *Fixing the PR Bottleneck*, AIHero /
[YouTube](https://www.youtube.com/watch?v=LlgiOCmFG_w). Captured through the
author's NotebookLM notebook on 2026-10-04. This note summarizes the argument
and turns it into an implementation checklist; it does not independently
verify the talk transcript or add new empirical measurements.

## Thesis

Autonomous coding agents remove the drafting bottleneck but create a review
bottleneck: uncontrolled generation produces many plausible-looking PRs that
do not survive scrutiny. The answer is not "prompt the implementer harder."
It is to treat code generation as a software factory with deliberate quality
gates. Good brakes make the factory faster because fewer bad PRs reach a
human and fewer reviews repeat the same correction.

## Three-layer quality filter

1. **Deterministic checks**
   - Lint, type checking, static analysis, formatting, and unit/integration
     tests.
   - Cheap, repeatable, and free of model variance.
   - Necessary but insufficient: green checks can still hide low-value code.

2. **AI review sub-agents**
   - Review the diff against architecture rules and team-specific standards.
   - Act as a second context with a different objective from the implementer.
   - Prefer direct commits for mechanical fixes; reserve prose comments for
     decisions a human must make.

3. **Targeted human review**
   - Focus on intent, product consequences, irreversible changes, and
     architecture-level risk.
   - Delegate bulk consistency, naming, test-shape, and style checks to the
     first two layers.

## Tests can lie

Green CI is not evidence of behavior when the tests were optimized to pass
rather than to constrain the implementation. Three anti-patterns are common:

- **Tautological tests.** They assert a constant or internal variable that the
  implementation also controls. They pass without proving user-visible
  behavior.
- **Structure-sensitive tests.** They parse or assert source-file layout
  instead of behavior. They break harmless refactors and miss real regressions.
- **Unfalsifiable tests.** They mock so much of the dependency graph that
  runtime failures cannot occur inside the test.

Countermeasures:

- Require tests to exercise public behavior and observable state.
- Distinguish acceptance tests that constrain outcomes from low-level tests
  that guide design.
- Review test diffs before implementation details, and reject tests that
  cannot fail under a plausible defect.

## Architecture makes review cheaper

Agents are more reliable in codebases designed for narrow interfaces:

- **Deep modules** hide complex decisions behind simple interfaces, so agents
  and tests operate at behavior boundaries rather than reaching into private
  structure.
- **Local seams** give tests and agents a stable interception point without
  exposing the whole module.
- **High locality** keeps a feature's blast radius small, which makes review
  and rollback easier.
- A shared vocabulary for locality, leverage, and seams lets standards be
  taught to both humans and review agents without bespoke explanations.

## Separate implementation from review

Putting "make it work" and "make it comply with every standard" in one agent
context overloads the prompt and dilutes both goals. Split the work:

| Role | Context objective | Output |
| --- | --- | --- |
| Implementer | Explore the code, change it, and make the chosen behavior work | A focused draft branch or diff |
| Reviewer agent | Compare the diff against standards and architecture rules | Fixes committed to the branch, plus a concise risk summary |
| Human reviewer | Decide whether the change is desirable and safe | Approve, redirect, or reject |

This separation also preserves context: the reviewer does not need the full
exploration history, only the diff, standards, and enough surrounding state to
understand intent.

## Human review should grade risk first

Not every PR deserves the same scrutiny. Use a reversible-change test before
reading code:

- **Two-way door:** reversible, local blast radius. Review lightly after
  automated gates pass.
- **One-way door:** migration, deletion, external side effects, security or
  data-integrity changes. Review deeply and specify rollback before merge.

A PR should end with an explicit **merge danger summary**: door type, blast
radius, affected users or systems, and the rollback path. Visual artifacts
— Mermaid sequence diagrams, component diagrams, CLI flow sketches, or short
pseudocode — can communicate intent faster than long prose.

## Turn review into a system-level feedback loop

The goal of human review is not only to accept or reject one diff. Each
repeated correction is evidence that the generating system needs a rule. A
retrospective should convert findings into:

- deterministic checks when a defect can be caught mechanically;
- additions to `coding-standards.md` when judgment is required;
- navigation pointers in `agents.md` when the agent could not find the right
  context;
- tool or workflow changes when the process wasted tokens or made verification
  difficult;
- pruning of stale instructions that now add noise rather than prevent a known
  failure.

This creates a compounding loop: today's review raises the quality floor for
tomorrow's generated PR.

## Candidate application to this repository

- Keep research and skill changes small enough for a two-way-door review.
- Add a merge danger summary to user-visible or destructive workflow changes.
- Prefer merging new guidance into existing skills instead of adding another
  skill file.
- Treat NotebookLM, web pages, issue comments, and tool output as research
  inputs: preserve provenance and verify load-bearing claims before promoting
  them into operational standards.
- When an agent review finds the same defect twice, convert it into a check
  or standard rather than fixing the occurrence alone.

## Sources

- Matt Pocock, *Fixing the PR Bottleneck*, AIHero —
  <https://www.youtube.com/watch?v=LlgiOCmFG_w>
- NotebookLM notebook: *Fixing the Pull Request Bottleneck* —
  <https://notebook.google.com/notebook/282b71f8-e226-4c66-b776-aba3fd10a821>
  (retrieved 2026-10-04)
