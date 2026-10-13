# Eval Instruments, Memory Writeback, and Skill-Supply-Chain Leakage — X-scout digest 2026-10-13

Curated analysis adapted from the X-scout knowledge-scout digest of
2026-10-13 (Discord thread #xTreand, cron job f933f5a8d591; consolidated
knowledge file:
`~/.hermes/profiles/architect/memories/knowledge/x-scout-2026-10-13.md`).
Theme: an eval is an instrument — record the instrument, not just the score;
and a memory layer without a real writeback path is dead weight.

## 1. Record the instrument: regrade before reword

Source: dev.to/oliverzehentleitner/the-model-changed-my-skill-didnt-the-score-still-dropped-mlj

An eval suite's score dropped although the skill was unchanged — a model
alias had switched versions behind the scenes. Rules distilled:

1. **Record the instrument** — log resolved model ID, judge-prompt hash,
   and CLI version on every run.
2. **Regrade before reword** — rerun the same grading before touching
   prompt wording.
3. **"No sentence for a single flip"** — add a rule to a skill only for a
   failure form seen ≥2 times (adding 9 sentences to fix a one-off caused
   a regression elsewhere).
4. **Series gate** — 3 runs, never one perfect run.

## 2. Aggregate benchmark equality ≠ same task-set

Source: x.com/Oluwaphilemon1/status/2100036836068340157

Same 4-bit AWQ model, same config, twice on DeepSWE: 38.94% vs 31.86%, and
32 of 113 tasks flipped outcome. In an agent loop a one-token difference
changes an edit, which changes the state all later steps build on —
non-determinism compounds through state. Honest comparison = per-task
outcome diff first, aggregate second.

## 3. Self-improvement needs a writeback loop

Source: ani.computer/writings/self-improving-fleet

A 13-agent fleet with good uptime had 5 empty memory files: consolidation
existed, writeback didn't. Fix: a midnight cron distills the day's lessons
into **append-only bullets** (never a full prompt rewrite — LLM self-rewrites
cause context collapse, per ACE), with a skeptic gate before landing.
Counterpart audit: measure `compliance_count` (did the agent follow it?),
not `used_count` (was it retrieved?) — and fire any newly wired hook once
for real; a misconfigured hook fails silently
(joeyhipolito.dev/log/2026-02-23-memory-in-practice).

## 4. Memory doesn't transfer across harnesses; shared facts need provenance

Sources: x.com/nicbstme/status/2050301124314563025 ·
x.com/0xwhrrari/status/2107093781807775896

Models are post-trained against their harness's memory layer, so ported
memory loses its read discipline. Operational rules: freeze the memory
snapshot at boot (no dynamic injection into the system prompt mid-session —
it invalidates the prompt cache); verify on read every entry that cites a
path or symbol. For shared memory: a fact needs owner + expiry + source
link before it may be written; derived context carries the source
ID/version; memory ≠ permission — re-check saved facts against the
requester's actual access.

## 5. Skill-marketplace credential leakage

Source: arxiv.org/abs/2604.03070 (ASE 2026) ·
github.com/AgentSkillsPrivacy/SkillLeakBench

17,022 marketplace skills: 520 leaked credentials (1,708 instances, 84%
negligence, 89.6% immediately usable). Dominant mechanism: frameworks pipe
tool stdout into the context window, so debug `print`/log statements become
a side channel; forks kept serving the secret after the upstream fix.
Install-gate: scan bundled scripts for secret-touching print/log calls;
check whether the framework surfaces skill stdout into context; prefer
upstream over forks.

## 6. Separating comprehension from judgment

Source: arxiv.org/abs/2610.11087 (Sakana MLR)

A reviewer pipeline forced to read and outline before judging caught 73%
of core-claim errors vs 14.81% baseline — but only 16% on retracted-paper
errors, and document-embedded prompt injection skewed every tested AI
reviewer's score. Summarize+critique+score in one prompt is the failure
shape; on untrusted text, an AI review is evidence, not a gate.

## 7. Numbers backing the house rules

- LLM-generated context files: −0.5–2% success, +>20% cost; developer files
  ~+4%, inconsistent across models (ETH + CodeIF-Bench,
  x.com/augmentcode/status/2031020977422012760) — supports the
  non-inferable-only context-file rule.
- Vercel/Next.js 16: on-demand skills didn't help; collapsing the docs
  index into an 8KB AGENTS.md reached 100% pass from 40KB
  (x.com/omarsar0/status/2026306141181898887) — index-in-context, body
  on-demand.
- Mid-session reasoning-effort switches change request shape and blow the
  prompt cache (x.com/kunchenguid/status/2103335401515819238) — decide
  effort at spawn time.
- Human message ≠ stop command: steering-gate block for long-running
  agents (x.com/altryne/status/2103310152938230256).
