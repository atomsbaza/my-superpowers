# Chapter 28: Pressure

## Core Idea
Professionals stay calm and decisive under pressure by relying on the same disciplines they use every day; pressure is best handled by avoiding it through good habits beforehand, and by doubling down on discipline — not abandoning it — when it hits anyway.

## Frameworks Introduced
- **Avoid then Weather**: the two-part strategy for pressure — first minimize the chance and severity of high-pressure situations, then, when pressure arrives anyway, get through it without breaking down.
  - When to use: applies at both the commitment-making stage (before pressure exists) and mid-crisis (once it does).
  - How: avoid by managing commitments, staying clean, and practicing crisis discipline; weather by staying calm, communicating, relying on disciplines, and pairing.
- **Crisis Discipline test**: use your own behavior during a crisis as a diagnostic for what you actually believe about your practices.
  - When to use: anytime you notice yourself dropping TDD, cleanliness, or pairing "just for now" under deadline pressure.
  - How: if you abandon a discipline (TDD, clean code, pairing) during a crisis, that proves you never really trusted it was efficient; the fix is to only adopt disciplines you're willing to follow even under maximum stress, then never deviate from them.

## Key Concepts
- **Sweat equity trap**: the start-up-era belief that heroic overtime and hacked-together demos are rewarded and expected — Martin describes buying into this and becoming abusive to his team as a result.
- **Quick and dirty is an oxymoron**: cutting corners to "move fast" is self-defeating because dirty code is always slower, not faster.
- **Unaccepted commitments**: promises made by the business without the developer's consent are not automatically binding on the developer; professionals help find a path to the goal but don't have to accept the deadline as their own commitment.
- **Don't panic**: the first response to real pressure is to slow down and think, not to rush — rushing digs the hole deeper.
- **Communicate early**: surprises multiply pressure roughly by ten; telling your team and superiors you're in trouble, with a plan, defuses it.
- **Rely on your disciplines**: under pressure, intensify practices (write more tests, refactor more, keep functions smaller) rather than searching for shortcuts.
- **Get help / pair**: pairing under pressure produces fewer defects, helps maintain discipline, and catches things a stressed solo developer misses.

## Mental Models
- The calm surgeon under a literal deadline: professionalism is measured by composure and adherence to training precisely when stakes are highest, not by visible urgency or drama.
- Pressure as a mirror: how you behave in a crisis reveals what you truly believe about your normal practices — your crisis self is the honest audit of your daily self.
- A two-phase defense: pressure management is not one skill but two — prevention (commitments, cleanliness, discipline) and response (calm, communication, discipline, help) — treated as separate but linked phases.

## Anti-patterns
- **Accepting all commitments to be a "hero"**: rewards short-term heroics (80-hour weeks, hacked demos) but produces burnout, poor code, and abusive team dynamics, as in Martin's own start-up experience.
- **Abandoning TDD/clean code/pairing during a crisis**: cutting the very practices meant to manage complexity and risk right when complexity and risk are highest — this is the "quick and dirty" fallacy in action and makes recovery slower, not faster.
- **Rushing when behind**: attempting to move faster by skipping thought and going straight to typing; increases mistakes and rework, deepening the hole.
- **Hiding trouble from the team**: staying silent instead of communicating status creates surprises later, which are far more damaging to trust and outcomes than early bad news.
- **3,000-line functions and shouting matches under deadline**: concrete symptoms of a team that let pressure override professional discipline — messy code, interpersonal blowups, and eventually forced overtime culture.

## Worked Example
Martin recounts his time at Clear Communications (1988), a start-up whose product vision and architecture kept shifting while revenue never materialized. Under constant deadline pressure tied to trade shows and demos, the culture rewarded 80-hour weeks and punished those who wouldn't "hack something together." Martin, as development manager, wrote 3,000-line C functions at 2am, shouted at colleagues, threw pens, and pressured his team the same way he was pressured — believing this was what commitment looked like. The turning point came when his wife confronted him about who he'd become; after storming out and walking in the rain, he had a moment of clarity, laughed at his own folly, and deliberately stopped the crazy hours, the mess-making, and the abusive behavior. He left the job professionally and became a consultant, resolving to enjoy his career by doing it well rather than doing it stupidly. The anecdote grounds the chapter's claim that cutting corners and losing composure under pressure is not a temporary fix but a self-inflicted, avoidable failure mode.

## Key Takeaways
1. The best defense against pressure is avoiding it: don't accept unrealistic commitments, keep code and systems clean, and pick disciplines you'd follow even in a crisis.
2. If a practice (TDD, clean code, pairing) gets dropped the moment things get hard, you never actually trusted it — professionals only adopt disciplines they intend to keep under all conditions.
3. When pressure hits anyway, don't panic and don't rush — slow down, think, and move at a steady, deliberate pace toward the best outcome.
4. Communicate trouble early and with a plan; unannounced surprises are far more damaging to relationships and outcomes than timely bad news.
5. Under pressure, intensify your disciplines rather than searching for new shortcuts — write more tests, refactor more, keep functions smaller.
6. Pairing is a concrete, high-leverage response to pressure: it reduces defects, helps maintain discipline, and should be offered to teammates who are struggling too.
7. Commitments made by the business without your input don't automatically bind you — help find a path to the goal, but the people who made unrealistic promises must own the consequences if it can't be met.

## Connects To
- **Ch26 (Time Management)**: pressure often stems from poor time management upstream; disciplined estimation and calendar management are preventive medicine for the crises this chapter addresses.
- **Ch21 (Coding)**: staying "clean" under pressure directly extends the coding-discipline chapter's guidance — the claim that messy code is never actually faster applies with the highest stakes here.
- **Ch24 (Acceptance Testing)** and **Ch5 (TDD, Clean Code numbering varies)**: the "rely on your disciplines" framework specifically calls out intensifying TDD practice as the correct crisis response.
- **Ch25 (Practicing)** / **Ch20 (Saying Yes)**: commitments made without consent connect to the Saying Yes chapter's distinction between estimates and commitments, and to the practice ethic of only promising what's been rehearsed.
- **External concept — Deming's "quality is free"**: the chapter's "dirty always means slow" claim mirrors the quality-management principle that investing in quality reduces total cost and time rather than adding to it.
