# Chapter 23: Practicing

## Core Idea
Professional programmers, like musicians and athletes, must practice deliberately on their own time to keep problem/solution patterns instinctive — coding on the job alone is not practice, and speed in real work comes from a repertoire of drills executed until they're automatic.

## Frameworks Introduced
- **Coding Dojo**: A gathering (in person or solo) where programmers practice programming exercises using a martial-arts metaphor, popularized by Laurent Bossavit and Emmanuel Gaillot at XP2005, crediting Dave "Pragmatic" Thomas with the original kata idea.
  - When to use: Regularly, outside of paid work time, individually or in groups, to build and maintain fluency with tools, languages, and common problem/solution pairs.
  - How: Choose an exercise (kata), repeat it — solo, in pairs (wasa/ping-pong), or as a group (randori) — until the moves become automatic; periodically revisit multiple kata so skills don't fade.
- **Kata**: A precise, choreographed sequence of keystrokes and decisions that simulates solving a known programming problem, practiced repeatedly for fluency rather than to discover a new solution.
  - When to use: To internalize TDD rhythm, hotkeys, navigation idioms, and standard problem/solution pairs.
  - How: Pick a known exercise (e.g., The Bowling Game, Prime Factors, Word Wrap), repeat it from memory over and over, refining keystrokes and structure toward an asymptotic "perfect" execution; advanced practitioners try setting the kata to a musical rhythm.

## Key Concepts
- **Deliberate practice**: Skill-sharpening exercises done outside of "gig time" (the moment you're being paid to perform), analogous to musicians rehearsing scales or athletes running drills.
- **Kata**: A memorized, choreographed solution to a known problem, repeated for muscle-memory fluency, not to solve anything new.
- **Wasa**: Two-person paired practice (borrowed from jujitsu) where roles are swapped; in programming this maps to "ping-pong" pairing — one partner writes a failing test, the other makes it pass, then they swap.
- **Randori**: Free-form group practice; in coding dojos, one person writes a test and sits down, the next person makes it pass and writes the next test, cycling through the group.
- **Turnaround time**: The speed of the code/test/compile loop; modern tooling lets this loop run many times per minute, which is what makes rapid, reflexive coding possible and worth practicing.
- **Broadening experience**: Deliberately working in languages, platforms, or domains outside your employer's stack to avoid a narrow, stale skill set.
- **Practice ethics**: The professional norm that practice happens on the programmer's own time, not the employer's, just as doctors and musicians don't get paid to rehearse.

## Mental Models
- **Musician analogy**: A guitarist like Santana doesn't think about finger positions during a performance — his fingers execute while his mind handles higher-level melody; likewise, a practiced programmer's fingers execute known patterns while the mind handles higher-level design.
- **Martial artist analogy**: Two fighters in combat react in milliseconds without conscious deliberation because trained reflexes take over; a programmer spinning fast through the red-green-refactor loop similarly needs the low-level moves to be reflexive so the mind is free for strategy.
- **22 orders of magnitude**: Martin's hardware has grown ~10^22 times more powerful since the PDP-8, yet programmers still write the same if-statements and loops — the raw material of programming hasn't changed even though turnaround time has collapsed from days to seconds, which is precisely what makes fast, practiced reflexes newly valuable.
- **Practice vs. performance**: Kata are "beautiful to watch" but their purpose isn't the performance — it's training the body/mind so the right response is already there when a real, novel problem appears.

## Anti-patterns
- **Never practicing off the clock**: Relying solely on paid work to develop skill leaves you without a repertoire of instinctive responses, and unprepared when the field shifts — you're always solving problems for the first time under pressure.
- **Waiting for compiles**: Martin calls it "tragic and indicative of carelessness" when programmers tolerate slow build/test loops in 2010s tooling — it forecloses the fast-cycle practice that builds reflexive skill.
- **Staying single-language, single-domain**: Employers often confine programmers to one language/platform, which narrows the resume and mindset and leaves programmers unprepared when the industry shifts; open-source contribution in a different stack is the recommended antidote.
- **Expecting the employer to fund practice**: Treating skill-sharpening as the employer's responsibility mirrors expecting patients to pay doctors to practice sutures — it inverts where professional responsibility actually sits.

## Code Examples
(omit — not code-heavy)

## Reference Tables
(omit if none)

## Worked Example
Martin builds the chapter's argument by analogy before turning prescriptive. He opens with the universal observation that all professionals practice — musicians rehearse scales, athletes run drills, doctors practice sutures, lawyers rehearse arguments — and asks why programmers historically didn't. His answer: early programming's slow turnaround (minutes to hours per compile) made rapid reflexive skill useless, so there was nothing to practice for. But modern turnaround time (his FitNesse example: full build plus tests in under 4 minutes, partial tests in seconds) means a programmer can cycle the code/test loop ten times a minute — and doing that well requires the same kind of trained reflex a martial artist or guitarist relies on in real time, where there's no time to deliberate consciously. From there he introduces the Coding Dojo tradition and its three practice modes, explicitly borrowed from martial arts: kata (solo, memorized, choreographed exercises like The Bowling Game or Prime Factors, repeated until automatic), wasa (paired practice, mapped onto TDD "ping-pong" where partners alternate writing tests and making them pass), and randori (group practice where a room of programmers takes turns at a shared screen, one writing a test and the next making it pass). He closes by broadening the scope beyond kata to overall career hygiene: contribute to open-source projects outside your usual language/domain the way doctors and lawyers take pro bono work, and treat all of this practice time as unpaid, personal responsibility — "Practicing is what you do when you aren't getting paid. You do it so that you will be paid, and paid well."

## Key Takeaways
1. Practice deliberately and regularly, on your own time, using kata, wasa, and randori — don't rely on paid work to build reflexive skill.
2. Maintain a repertoire of several kata (e.g., Bowling Game, Prime Factors, Word Wrap) and repeat them often enough that they don't fade from memory.
3. Pair practice (wasa/ping-pong) and group practice (randori) expose you to other people's problem-solving approaches, broadening your own technique beyond what solo kata can teach.
4. Fast code/test turnaround is what makes rapid, reflexive coding valuable — invest in tooling that keeps build/test cycles in seconds, not minutes.
5. Deliberately broaden your experience by contributing to open-source projects in languages or domains your employer doesn't use, to avoid a narrow skill set and resume.
6. Treat practice as a professional's own responsibility, not the employer's, mirroring how doctors, musicians, and athletes rehearse unpaid.

## Connects To
- **Ch 18 (Professionalism)**: Practicing is a direct extension of the professional's duty of continuous learning and skill maintenance introduced there — professionalism demands you keep your craft sharp on your own initiative.
- **Ch 25 (TDD)**: Kata and ping-pong practice sessions are typically vehicles for rehearsing the TDD red-green-refactor loop itself, so fluency in TDD discipline is both a prerequisite and an outcome of dojo practice.
- **Ch 31 (Mentoring, Apprenticeship, and Craftsmanship)**: Coding dojos and pairing (wasa/randori) are also apprenticeship mechanisms — practicing alongside more experienced programmers transmits craft knowledge the way solo kata cannot.
- **Kata**: External term from the martial arts tradition, adopted wholesale into software practice as a named, repeatable exercise for skill-building.
- **Coding Dojo**: External community/practice format (codingdojo.org, katas.softwarecraftsmanship.org) that formalizes group kata practice for programmers.
