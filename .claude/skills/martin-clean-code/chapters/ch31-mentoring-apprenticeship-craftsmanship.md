# Chapter 31: Mentoring, Apprenticeship, and Craftsmanship

## Core Idea
Programming skill and professional values are not taught by universities; they are transmitted from person to person through mentoring, observation, and years of supervised practice — the software industry needs a real apprenticeship system, not the "hire a graduate, throw them at production code" status quo.

## Frameworks Introduced
- **The Software Craftsmanship Apprenticeship Model**: A three-stage career progression borrowed from medieval guild tradition and adapted from how medicine trains doctors (internship → residency → fellowship) — Apprentice/Intern → Journeyman → Master.
  - When to use: as an organizing model for how a software organization should onboard, supervise, and grow new developers instead of granting autonomy by default at hire.
  - How: apprentices are paired intensely with journeymen and given no autonomy; journeymen are supervised (closely at first, then via peer review) while they build breadth; after roughly a year of apprenticeship, journeymen recommend the apprentice to masters, who examine and promote by interview and review of work — the same peer-vetted transition pattern used for medical board certification.

## Key Concepts
- **Craftsmanship**: The mindset held by craftsmen — a meme containing values, disciplines, techniques, attitudes, and answers, not a checklist of skills.
- **Meme**: A unit of culture (here, professional values and technique) that spreads by contagion — observed and caught, not argued into someone.
- **Mentoring**: Any process, formal or accidental, by which a less experienced person absorbs knowledge and values from someone more experienced; it need not be intentional to be effective (learning by watching people ignore you still counts).
- **Apprentice/Intern**: A graduate with no autonomy, closely supervised by journeymen, who at first only assists rather than owns tasks; this is when disciplines and values are formed.
- **Journeyman**: A trained, competent, energetic programmer (roughly ~5 years average experience) who knows one language/system/platform deeply but is still building breadth; supervised early, gains autonomy over time, eventually becomes a teacher of apprentices.
- **Master**: A programmer with 10+ years across multiple systems/languages, who leads and coordinates teams, designs and architects fluently, and stays technical by reading, studying, practicing, doing, and teaching — the person a company assigns technical responsibility for a project.
- **Degrees of failure**: Martin's framing that CS education failure is a spectrum, from graduates who can't code at all to those who are simply unprepared for industry reality — the common factor among the strong ones is self-teaching before and despite university.
- **Unconventional mentoring**: Mentoring that doesn't look like mentoring — learning from a well-written manual's authors, or from watching skilled people work while being ignored — still transfers profound, foundational knowledge.

## Mental Models
- **Software as a high-stakes profession, treated like a low-stakes one**: society trusts software with banking, medical devices, transportation, and communication, yet the industry inducts new developers with less rigor than medicine, and arguably less than short-order cooks or licensed trades (plumbers, electricians, painters).
- **Craftsmanship spreads by contagion, not persuasion**: you cannot argue, data-point, or case-study someone into caring about quality — you can only become a visible role model and let the meme propagate by observation.
- **The elder's obligation**: responsibility for developing the next generation of professionals falls on senior practitioners in industry, not on universities — school teaches theory, industry must teach craft.
- **Supervision must be technical, not just organizational**: today's "supervision" (team leads, project leads) is usually managerial, not code- and craft-focused, which is precisely the gap the apprenticeship model is meant to close.

## Anti-patterns
- **Sink-or-swim onboarding**: hiring CS graduates and immediately forming them into "teams" to build critical systems with no supervised training period — treated by Martin as insane given what's at stake, and a pattern no other high-consequence trade tolerates.
- **Promotion by tenure instead of technical vetting**: programmers get raises and titles "because that's what you do with programmers," with no equivalent of a master's technical interview and review of accomplishments before advancement.
- **Mistaking classroom theory for job readiness**: assuming a CS degree equips someone for professional software work; even strong degree programs teach theory divorced from the practical, on-the-job disciplines industry actually requires.
- **Trying to argue people into craftsmanship**: using arguments, data, or case studies to convince someone to value quality — Martin states plainly this doesn't work; the meme must be caught, not taught by lecture.

## Code Examples
(omit — not code-heavy)

## Reference Tables
| Stage | Experience | Autonomy | Supervision | Focus |
|---|---|---|---|---|
| Apprentice/Intern | New graduate, ~first year | None | Very close; intense pair programming with journeymen | Learning design principles, patterns, disciplines (TDD, refactoring, estimation), and values |
| Journeyman | ~5 years average | Grows over time | Close at first from masters/senior journeymen, becoming peer review | Deepening one language/system/platform, learning to lead teams, becoming a teacher |
| Master | 10+ years | Full; leads multiple teams | Peer-level; assigned technical responsibility for projects | Designing/architecting, coding at high skill, staying technical via reading, studying, practicing, doing, teaching |

## Worked Example
Martin traces his own development through a string of informal mentors: a manual on boolean algebra (purchased for a dollar) that taught him to program his childhood Digi-Comp I toy computer; watching technicians and a teacher operate a school's ECP-18 minicomputer without anyone directly teaching him, from which he reverse-engineered opcodes by observation alone; and later, as a working programmer, Jim Carlin, a BAL programmer who saved him from being fired by helping debug a Cobol program beyond his depth, teaching him to read core dumps and format code cleanly — his "first push towards craftsmanship." Contrasted against this is Martin's own firing from a 1976 factory automation job: he was technically competent but had no mentor to teach him to respect deadlines and business goals, and he learned those lessons the hard way, through job loss, rather than through guided apprenticeship. The chapter uses this contrast to argue that lucky, informal mentoring is not a substitute for a real, designed apprenticeship system.

## Key Takeaways
1. Universities teach the theory of programming but cannot teach the discipline, practice, and skill of craftsmanship — that requires years of personal mentoring.
2. Organizations should treat junior developer training with the same seriousness as medicine treats internship/residency/fellowship — supervised, staged, and technically rigorous.
3. Craftsmanship is caught, not taught by argument — you spread it by becoming a visible role model, not by persuading people with data.
4. Apprentices need real, close, technical supervision (intense pairing) — not just organizational reporting lines — and initially should have zero autonomy.
5. Journeymen advance by increasing demonstrated competence and peer trust, not by tenure alone; promotion to master should involve interview and review by masters, mirroring board certification.
6. The responsibility for growing the next generation of professional developers belongs to the industry's senior practitioners now, since universities do not and cannot fill that role.
7. Even accidental or informal mentoring (a good manual, watching a skilled peer) can be profoundly formative — but it is not a reliable substitute for a deliberate program.

## Connects To
- **Ch 18 (Professionalism)**: apprenticeship and mentoring are the mechanism by which the professional values and standards defined in the Professionalism chapter get transmitted to new developers — this chapter answers "how do you make more professionals?"
- **Ch 23 (Practicing)**: the deliberate practice ethic described there is exactly what masters are expected to keep doing ("reading, studying, practicing, doing, and teaching") to remain technical, and what journeymen are still building toward.
- **Ch 21 (Collaboration)**: intense pair programming is named explicitly as the apprentice-stage teaching method, tying this chapter to the collaboration practices discussed elsewhere in the book.
- **Software Craftsmanship movement**: this chapter is Martin's articulation of the broader Software Craftsmanship movement's apprentice/journeyman/master model, positioning the book as part of that movement's argument for treating programming as a craft-guild discipline rather than an assembly-line skill.
