# WikiSkill: Compiling Agent Experience into Persistent Knowledge — Research Note

Source: [arXiv:2608.27454](https://arxiv.org/abs/2608.27454) — Liyan Tang, Cyrus
Rashtchian, Chun-Sung Ferng, Andrew Tomkins, Da-Cheng Juan, Tu Vu (Google
Research, submitted 27 Aug 2026). Read from the HTML full text (arxiv.org/html/2608.27454v1).

**One-line summary:** skills alone decay; pair them with a persistent,
never-rolled-back knowledge base (wiki) that skill evolution builds on, and
skill-evolution quality jumps ~15 points while producing transferable skills.

---

## TL;DR for practitioners

1. **Separate three layers**: raw execution traces (immutable) / accumulated
   knowledge (persistent wiki) / active skills (procedural, evolvable).
2. **The wiki is the engine, not the skill.** Ablation: Skill Proposer with
   wiki access scores 63.7% avg vs 48.7% without (+15.0pt); LiveMath 51.3→72.6,
   SpreadSheetBench 49.9→76.6 (Gemini-3.5-Flash).
3. **Keep the wiki away from the executor.** Giving the Inference Agent wiki
   access during training rollouts *degrades* final skill quality (63.7→60.9):
   knowledge taken from the wiki instead of skills makes trajectories less
   informative. Executors read skills only; analysts read the wiki.
4. **Log every rejected proposal.** A `skill-impact.md` audit trail (proposal
   diff + accept/reject + score) prevents re-proposing failed ideas — this is
   what unblocked the paper's case study from iteration 0's rejection to
   iteration 1's accepted skill.
5. **Sample, don't dump.** Per iteration: ≤5 failing traces (root cause) +
   ≤3 passing traces (protect working behaviors), each capped at 15k chars.
6. **Gating is strict**: accept a skill change only if validation score beats
   the best so far; otherwise roll the *skill* back. The **wiki is never rolled
   back** — knowledge persists regardless of acceptance.
7. **Skills stay concise** (45–129 lines across models); the wiki absorbs the
   history (6–9 patterns, 7–18 edits per run).

## The framework

### Three-layer workspace

| Layer | Contents | Mutability |
|---|---|---|
| `raw/` | Full execution traces: reasoning, tool calls, outputs, answers | Immutable |
| `wiki/` | `patterns/` (one markdown page per failure mode / successful strategy), `index.md` catalog, `logs.md` (evolution log), `skill-impact.md` (programmatic audit trail) | Append/patch; **never rolled back** |
| `skills/` | Active skills: `SKILL.md` + `PURPOSE.md` (maps skill back to motivating wiki patterns) | Gated changes only |

### The loop (per iteration k)

1. **Inference Agent** runs tasks with skills injected (no wiki access).
2. **Wiki Maintainer** receives the full wiki + stratified trace sample;
   root-causes failures, extracts successful strategies; creates/patches
   pattern pages (incremental edits), updates `index.md`, appends `logs.md`.
3. **Skill Proposer** (ReAct agent, 10–20 turns) starts from the wiki index +
   skill-impact history + pass/fail summary, then *pulls* specific pattern
   pages and raw traces on demand via `read_file`; emits **one atomic
   proposal** (create one skill or patch one existing skill).
4. **Gating**: apply proposal → evaluate on validation split → accept iff
   score > best-so-far, else rollback skills. Harness appends the outcome
   (diff, score, Accepted/Rejected) to `skill-impact.md`.

## Key results

- Outperforms no-skill and SOTA skill-evolution baselines (Trace2Skill,
  EvoSkill, SkillOpt) across 5 benchmarks (LiveMath, SealQA, SpreadSheetBench,
  OfficeQA, ALFWorld) × 5 models (Qwen-3.5-4B/9B, Qwen-3.6-27B, Gemma-4-31B,
  Gemini-3.5-Flash); best-vs-best margins +3.3 to +12.0 points.
- **Skill evolution complements scale**: Qwen-4B/9B/27B gain +12.3/+17.5/+23.9
  (bigger models extract more from skills).
- **Skills transfer across model families**: Qwen-9B with a Qwen-27B-evolved
  skill (70.2%) beats its own self-evolved skill (63.4%) on ALFWorld — skill
  discovery and skill execution are distinct capabilities.
- Skill refinement continues throughout iterations (39–52% of accepted updates
  land in iterations 0–1, the rest in middle/late stages) — persistent
  knowledge is what makes late-stage refinement possible.

## Limitations (from the paper itself)

- No skill retrieval/triggering evaluated (skills force-injected into prompts).
- Strict validation gating rejects neutral proposals that could enable later
  gains.
- **No automated wiki pruning** — patterns/logs/diffs accumulate; long runs
  will need a pruning mechanism.
- Benchmarks don't cover very-long-horizon tasks.

---

## Adaptation: the "Wiki loop" for a personal agent (no training loop)

This repo's parent system (Hermes agent, see also
[agent memory research](../2026-09-01-agent-memory-and-context.md)) implements
a lightweight adaptation. Map the paper's machinery onto filesystem memory:

| WikiSkill | Adaptation |
|---|---|
| `raw/` traces | Session history DB (automatic, no work needed) |
| `wiki/patterns/*.md` + `index.md` | `knowledge/patterns/` — one file per failure mode, fixed schema: *symptom → root cause → workaround → source*; `index.md` catalog with status (in-effect / rejected) |
| `skill-impact.md` | `patterns/impact-log.md` — every pattern→rule/skill conversion logged with outcome |
| Inference Agent reads skills only | Workers/coders never receive the pattern catalog; the orchestrator reads `index.md` at triage and pulls only relevant pattern files |
| Wiki Maintainer | A daily consolidation job: review yesterday's failures (≤5) + successes (≤3), create/patch pattern files, sync the index |
| Skill Proposer + gating | A pattern that recurs ≥2 times may be promoted to a skill/rule (human-approved); if it fails again *after* promotion → log **Rejected**, fix the existing rule, **never** write a new rule on top |

Implementation notes from live use:

- Pattern-per-file beats one big lessons file: it keeps orchestrator context
  small (read the index, then one relevant file) and avoids concurrent-write
  conflicts when several sessions patch lessons at once.
- The wiki-not-rolled-back principle translates to: lessons survive even when
  the rule they produced is rejected — you keep the diagnosis and rewrite the
  prescription.
- The paper's no-pruning limitation is already handled by the existing memory
  policy: knowledge older than a month that is unused and covered by a skill
  gets pruned.

## Reproduce / verify

- Paper HTML: <https://arxiv.org/html/2608.27454v1> (ablation table 3, case
  study §5.3, sampling budget appendix C)
- All numbers above are quoted from the paper, not third-party summaries.
