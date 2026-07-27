# Chapter 27: Estimation

## Core Idea
An estimate is not a commitment — it is a probability distribution over how long a task might take. Professionals communicate that distribution honestly (using techniques like PERT) instead of collapsing it into a single number that business then treats as a promise.

## Frameworks Introduced
- **PERT (Program Evaluation and Review Technique)**: created in 1957 for the U.S. Navy's Polaris submarine project; converts three-point ("trivariate") task estimates into a probability distribution.
  - When to use: for any task or project where you need to communicate not just a duration but the confidence/uncertainty around it, and especially when combining many task estimates into a project-level forecast.
  - How: for each task, gather three numbers — Optimistic (O), Nominal (N), Pessimistic (P) — then compute expected duration µ = (O + 4N + P) / 6 and standard deviation σ = (P − O) / 6. For a sequence of tasks, sum the µ values and combine σ values via root-sum-of-squares (σ_sequence = √(σ₁² + σ₂² + ... )).
- **Wideband Delphi**: introduced by Barry Boehm in the 1970s; a consensus-based estimation technique where a team discusses, estimates, and iterates until they agree. Variants covered: Flying Fingers, Planning Poker, and Affinity Estimation.
  - When to use: to generate the nominal (and, with adaptation, optimistic/pessimistic) estimates for a task using the collective judgment of the team rather than one person's guess.
  - How (Flying Fingers): discuss the task, then everyone simultaneously reveals 0–5 fingers representing their estimate; repeat discussion until convergence. Planning Poker is the same mechanic using numbered cards (Martin favors 0, 1, 3, 5, 10). Affinity Estimation: silently sort task cards left-to-right by relative size on a table/wall, then draw bucket lines (often Fibonacci: 1, 2, 3, 5, 8).

## Key Concepts
- **Estimate**: a guess about duration with no promise attached; missing an estimate is not dishonorable, unlike missing a commitment.
- **Commitment**: something you must achieve — professionals only commit when they are certain they can deliver, even if it means extraordinary effort.
- **Probability distribution**: the correct mental model for an estimate — a spread of possible durations, each with a likelihood, rather than a single point value.
- **Optimistic estimate (O)**: the duration if virtually everything goes right; should have well under a 1% chance of actually happening.
- **Nominal estimate (N)**: the most likely duration — the tallest bar on the probability chart.
- **Pessimistic estimate (P)**: the duration if nearly everything goes wrong (short of catastrophe); also under a 1% chance of occurrence.
- **Standard deviation (σ)**: a measure of uncertainty in the estimate — larger σ means less confidence in the duration.
- **Implied commitment**: agreeing to "try" for a date is functionally agreeing to succeed, since "trying" implicitly commits to extra hours, weekends, and sacrificed personal time.
- **Law of Large Numbers (applied to estimation)**: breaking a large task into many smaller independently-estimated tasks tends to produce a more accurate total, because individual errors partially cancel out — though Martin notes this effect is imperfect since estimation errors skew toward underestimation.
- **Trivariate analysis**: the practice of stating three numbers (O, N, P) per task instead of one, enabling a real probability distribution instead of a false-precision single figure.

## Mental Models
- An estimate is a probability distribution, not a commitment — the number you say out loud ("three days") is just the peak of a curve that has a long tail of worse outcomes.
- "Trying" to hit a date is not neutral language — it is an implied commitment, and professionals recognize that agreeing to try means agreeing to sacrifice (overtime, weekends, vacations) to succeed.
- Uncertainty compounds across a sequence of tasks — the combined estimate for several uncertain tasks is not just the sum of nominal estimates; the expected value and the spread both grow in ways that feel counterintuitive but are mathematically real.
- The people around you are an estimation resource — teammates see risks and complications you don't, so estimates produced through team consensus (wideband delphi) tend to be more accurate than solo estimates.

## Anti-patterns
- **Treating an estimate as a promise**: business often converts "three days" into a hard deadline; this destroys trust when reality (the distribution) diverges from the number, and punishes honest estimation.
- **Giving a single-point estimate**: a bare number like "three days" hides all information about confidence and risk; without O/N/P, the listener cannot judge how likely the number is to hold.
- **Agreeing to "try"**: sounds harmless but is an implied commitment to do whatever it takes (overtime, weekends, skipped vacations) to hit the number — professionals decline to "try" and instead restate the honest distribution.
- **Ignoring compounding uncertainty in sequences**: assuming a project's total time is just the sum of nominal estimates understates both expected duration and risk; the PERT sequence math (sum of µ, root-sum-square of σ) is needed to see the real picture.
- **Boehm's original heavyweight Delphi process**: Martin notes the original wideband delphi (with formal meetings and documents) has too much ceremony/overhead; lightweight variants (Flying Fingers, Planning Poker, Affinity Estimation) achieve the same consensus goal more efficiently.

## Code Examples
(omit — not code-heavy)

## Reference Tables
| PERT term | Formula / meaning |
|---|---|
| O (Optimistic) | Best-case duration; <1% chance of occurring |
| N (Nominal) | Most likely duration; tallest bar of the distribution |
| P (Pessimistic) | Worst-case (short of catastrophe) duration; <1% chance of occurring |
| µ (expected duration, single task) | (O + 4N + P) / 6 |
| σ (standard deviation, single task) | (P − O) / 6 |
| µ (expected duration, task sequence) | Sum of each task's µ: Σ µ_task |
| σ (standard deviation, task sequence) | Square root of the sum of squares of each task's σ: √(Σ σ_task²) |
| Confidence bands | ~68% chance actual falls within µ ± 1σ; ~95% within µ ± 2σ |

## Worked Example
Peter estimates the "Frazzle" task as O=1, N=3, P=12 days, giving µ = (1 + 4×3 + 12)/6 ≈ 4.2 days and σ = (12 − 1)/6 ≈ 1.8 days — so Mike should expect roughly five days, with a real (if smaller) chance of nine.

Extending this to a project: Peter has three sequential tasks — Alpha (µ=4.2, σ=1.8), Beta (µ=3.5, σ=2.2), Gamma (µ=6.5, σ=1.3). Summing the µ values gives a total expected duration of 4.2 + 3.5 + 6.5 = 14.2 (~14) days — far more than the naive sum of nominal estimates (3 + 1.5 + 6.25 ≈ 10.75 days) or the wildly optimistic sum of best cases (1+1+3=5 days). The sequence's standard deviation is √(1.8² + 2.2² + 1.3²) ≈ 3 days. So Mike should plan for the work likely taking 14 days, plausibly 17 days (µ+1σ), and possibly as much as 20 days (µ+2σ) — a picture completely invisible from single-point nominal estimates alone.

## Key Takeaways
1. Never collapse an estimate into a single number when you can convey a distribution — give optimistic, nominal, and pessimistic values so others can judge the real risk.
2. Never confuse an estimate with a commitment; only commit when you are certain you can deliver, and be willing to say no to commitments you can't guarantee.
3. Watch for implied commitments hidden in soft language like "try" — agreeing to try is agreeing to succeed, with all the personal sacrifice that implies.
4. Use PERT math (µ = (O+4N+P)/6, σ = (P−O)/6) to combine individual task estimates into realistic project-level forecasts — expect the total to be larger and less certain than naive nominal sums suggest.
5. Estimate with your team, not alone — lightweight wideband delphi techniques (Flying Fingers, Planning Poker, Affinity Estimation) surface risks a solo estimator would miss and converge faster than heavyweight formal Delphi processes.
6. Break large tasks into smaller ones and estimate them independently — the Law of Large Numbers means the summed small-task estimates tend to be more accurate than one big guess, even though the effect isn't perfect (errors skew toward underestimation).
7. When asked for a hard date, professionals hold the line and communicate the honest distribution rather than caving to pressure to name a single optimistic number.

## Connects To
- **Ch20 Saying Yes**: the direct companion chapter — it examines the language of commitment (the deeper meaning of "yes," "I'll try," and honoring commitments) that this chapter's "implied commitment" discussion depends on.
- **Ch19 Saying No**: professionals must be willing to decline a commitment they can't guarantee, the same discipline this chapter demands when refusing to convert an estimate into a promise.
- **Ch28 Pressure**: estimation is where business pressure to commit to optimistic dates is most acute; the practices here (trivariate estimates, refusing "try") are a defense against that pressure.
- **Ch31 Teams and Projects / Ch23 Practicing**: wideband delphi techniques rely on team collaboration and shared understanding of tasks, tying estimation accuracy to team dynamics and shared codebase knowledge.
- **PERT**: external framework (US Navy, 1957) providing the statistical machinery (trivariate analysis, µ and σ formulas) this chapter builds its entire estimation practice on.
- **Law of Large Numbers**: external statistical principle justifying why decomposing large tasks into smaller independently-estimated pieces improves aggregate accuracy.
