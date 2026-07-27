# Chapter 26: Time Management

## Core Idea
A professional treats time and focus as scarce, deliberately managed resources — declining or leaving unproductive meetings, protecting blocks of concentrated work, and recognizing (rather than rationalizing) avoidance, blind alleys, and messes before they consume a project.

## Frameworks Introduced
- **Focus-Manna**: focus is treated as a depletable, rechargeable resource, like "manna" in role-playing games.
  - When to use: as a mental model for planning your day around when you're capable of deep concentration versus when you're not.
  - How: spend focus-manna on coding when it's high; do unfocused/administrative work when it's low; recharge through sleep, de-focusing activities (walks, naps, conversation), and "muscle focus" (physical disciplines like biking, martial arts, yoga); avoid burning it in meetings, worry, or distraction.
- **Time Boxing / Pomodoro Technique ("tomatoes")**: work in fixed, protected 25-minute intervals using a timer, deferring all interruptions until the timer ends.
  - When to use: any time deep, uninterrupted focus is needed on a task; especially useful for measuring how much of a day is actually productive.
  - How: set a timer for 25 minutes; defend that window against all interruptions (ask people to check back later); stop immediately when the timer dings; handle deferred interruptions; take a ~5-minute break; every fourth tomato take a longer ~30-minute break; optionally track tomatoes completed per day/week as a velocity metric.

## Key Concepts
- **Meetings discipline**: professionals actively decline meetings without immediate, significant benefit to their current work, and politely exit meetings that turn out to be a poor use of time.
- **Agenda and goal**: a meeting worth attending has a clear agenda, time allocations per topic, and a stated goal; if the agenda is hijacked, request it be restored or leave.
- **Focus-manna**: a scarce, decaying mental resource consumed by intellectual work, meetings, worry, and distraction, and recharged by sleep, de-focusing, and physical (muscle) focus activities.
- **Priority inversion**: raising the apparent priority of a lesser task to avoid or postpone the task that truly has priority — a self-deception used to build a defense against others' judgment.
- **Avoidance**: procrastinating on scary, uncomfortable, or boring work by convincing yourself something else is more urgent.
- **Blind alleys**: technical pathways that lead nowhere; the more personally/professionally vested you are in the decision, the longer you'll wander before backing out.
- **The Rule of Holes**: when you realize you're in a blind alley (a hole), stop digging — recognize it quickly and have the courage to reverse course.
- **Marshes, bogs, swamps (messes)**: worse than blind alleys — they don't stop progress but slow it to a crawl through accumulating complexity; the way forward always looks shorter than the way back, but usually isn't.
- **Inflection point**: the moment in a growing mess when you realize the original design choice was wrong and going back is still possible but looks expensive — the earliest and cheapest point to reverse course.

## Mental Models
- **Manna as a decaying resource**: like a role-playing game's magic points, focus recharges slowly at a fixed rate and is easy to burn through in a few "spell-casting" sessions (meetings, context switches); if unused when available, it's lost, not banked.
- **Tomato time vs. non-tomato time**: the day divides into genuinely productive intervals and everything else (distractions, meetings, breaks); counting tomatoes reveals the real ratio of productive to non-productive time, which is often surprising.
- **The swamp's optical illusion**: in a mess, forward always looks like the shorter path even though going back never gets easier than it is right now — treating "sunk cost forward" as safer is itself a lie you tell yourself and others.
- **Data over will in disagreements**: technical arguments that can't be settled in five to thirty minutes aren't lacking persistence, they're lacking data; force of character or passive-aggressive false agreement never substitutes for evidence.

## Anti-patterns
- **Attending every meeting invited to**: erodes focus-manna and consumes the limited hours available for actual work; professionals decline unless their presence is immediately and significantly necessary.
- **Staying in a meeting that's become useless**: wastes the employer's time and money; the professional obligation is to negotiate a polite, timely exit, not silently endure.
- **Passive-aggressive "agreement"**: pretending to accept a decision in an argument, then sabotaging or disengaging from it — described as the worst kind of unprofessional behavior.
- **Priority inversion / avoidance**: reprioritizing to dodge scary or boring work while lying to yourself about why.
- **Pushing forward through a recognized mess**: continuing to "make progress" in a swamp you know is a swamp is itself a priority inversion — it lies to yourself, your team, your company, and your customers about the true state of the work.
- **Over-caffeinating for focus**: moderate caffeine can extend usable focus-manna, but excess produces a "jitter" that hyper-focuses effort in the wrong directions, wasting the day.

## Worked Example
Martin recounts running a 15-person department where hectic days of calls and interruptions forced a strict schedule: arriving at 6am to get 2.5 quiet hours before chaos, blocking the calendar in 15-minute increments, front-loading three fully scheduled hours, then from 9am leaving one 15-minute gap per hour to absorb interruptions without breaking flow, and leaving afternoons deliberately unscheduled once reactive mode set in. This illustrates protecting focus-manna proactively rather than reacting to whatever meeting or interruption shows up.

On meetings specifically, he distinguishes types worth different handling: standup meetings should take under a minute per person (what I did yesterday, what I'll do today, what's in my way) and finish a ten-person team in under ten minutes; iteration planning should consume no more than 5% of the iteration (two hours for a one-week iteration), moving quickly through each backlog item and tabling longer discussions; retrospectives and demos should be capped (20 minutes retro, 25 minutes demo) and scheduled right before quitting time so they can't sprawl. Applying the Pomodoro technique on top of this schedule, a developer facing a request mid-tomato responds "can I get back to you in 25 minutes?" rather than breaking focus, then handles the backlog of interruptions in the break between tomatoes — treating the 25-minute window as inviolable while still remaining responsive on a bounded delay.

## Key Takeaways
1. Decline meeting invitations unless your participation is immediately and significantly necessary to your current work — your time management is your own responsibility, not the inviter's.
2. It is professional, not rude, to politely leave or renegotiate your presence in a meeting that has become unproductive or off-agenda.
3. Treat focus as a depleting resource: protect it from meetings, worry, and distraction, and deliberately recharge it with sleep, de-focusing breaks, and physical activity.
4. Use time boxing (Pomodoro/tomatoes) to create hard-protected 25-minute focus windows, deferring interruptions rather than absorbing them immediately.
5. Watch for priority inversion and avoidance — recurring excuses to work on something other than the truly important task are a warning sign, not a legitimate reprioritization.
6. Recognize blind alleys quickly and back out (Rule of Holes) rather than doubling down out of vested pride.
7. Fear messes more than blind alleys: catch the inflection point where a design stops scaling and fix it while going back is still cheaper than it will ever be again.

## Connects To
- **Ch28 Pressure**: time-management discipline (meeting discipline, focus-manna, avoiding swamps) is the everyday practice that keeps pressure situations from arising, and is the first thing to abandon under panic — this chapter is the preventive counterpart to Pressure's crisis response.
- **Ch18 Professionalism**: declining meetings, avoiding priority inversion, and refusing to push forward through a known mess are all instances of the broader professional obligation to manage one's own time and tell the truth about project state.
- **Ch22 TDD / Ch23 Practicing**: sustained focus-manna and tomato-protected blocks are what make disciplined TDD rhythm (red-green-refactor) practical without constant context switching.
- **Ch9 Unit Tests / Clean Code refactoring discipline**: catching a "mess" at its inflection point mirrors the Boy Scout Rule and continuous refactoring — cheap fixes now versus compounding technical debt later.
- **External concept**: Pomodoro Technique (Francesco Cirillo) — the source technique behind the chapter's "tomatoes" time-boxing method.
