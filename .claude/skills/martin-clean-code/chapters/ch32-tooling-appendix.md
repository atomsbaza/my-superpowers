# Chapter 32: Appendix A — Tooling

## Core Idea
A professional's toolkit spans source code control, IDE/editor, issue tracking, continuous build, unit/component/integration testing tools, and (skeptically) UML/MDA — chosen for developer speed and convenience, not managerial impressiveness.

## Frameworks Introduced
- **The Professional Toolkit**: six tool categories every developer should be conversant with, treated as a coherent kit rather than isolated choices.
  - When to use: when equipping a team or evaluating what infrastructure a project actually needs.
  - How: pick the lightest tool that satisfies the category's core job (fast source control, a code-manipulation-capable editor, a small manageable issue list, an always-green build, fast unbiased test feedback, executable specifications, thin UI-layer coverage) — resist "enterprise" tools sold to managers rather than developers.

## Key Concepts
- **Source Code Control**: manages concurrent edits to shared code; the author favors open-source, developer-written tools over commercial "enterprise" systems because developers optimize for speed, not feature checklists.
- **Pessimistic vs. Optimistic Locking**: pessimistic locking (file check-out/locking, like colored pins on a board) serializes edits and blocks others; optimistic locking (edit freely, merge on commit) works because modern merge tools handle concurrent changes well — the era of locking is over.
- **Distributed Source Control (git)**: every developer holds the full project history locally; there is no single "main line," only a conventional "golden" repository for releases — this makes branching and merging cheap and frequent rather than rare and feared.
- **IDE/Editor**: the tool for reading and manipulating code; power IDEs (IntelliJ, Eclipse) shift editing from character-level typing to structural transformations (extract method, rename, convert inheritance to composition) versus lighter tools (vi, Emacs, TextMate) chosen for speed or simplicity on smaller tasks.
- **Issue Tracking**: a system for the team's task/bug list; should stay small (dozens to hundreds of items for a 5–12 person team) — start with a manual bulletin-board/card system before buying a tool, since manual practice teaches you what you actually need.
- **Continuous Build**: an automated build/test run triggered on every check-in, hooked to source control, that reports status to the team; a broken build is a "stop the presses" event, never left unresolved for a day or more.
- **Unit Testing Tools**: language-specific tools (JUnit, RSpec, NUnit, Midje, CppUTest) that must be trivially easy to run, give unambiguous pass/fail and progress feedback, enforce test independence, and make writing tests easy via a convenient assertion API.
- **Component Testing Tools**: tools (FitNesse, and similar) that let business analysts and QA write executable specifications in a business-readable format — these tools are literally how "done" gets defined: "All Tests Pass."
- **Integration Testing Tools**: tools like Selenium and Watir for the necessarily-thin layer of tests that must go through the UI, kept minimal because UI-driven tests are fragile.
- **UML/MDA**: diagram-based modeling and Model Driven Architecture, aimed at generating executable systems from diagrams instead of code — the author's stance is strongly skeptical, having watched the 1990s CASE-tool dream fail to materialize.

## Mental Models
- Tools written by developers for developers (open source) tend to out-perform tools sold to managers and "tool groups" on the dimension that matters most: speed.
- Locking is a relic of weak merge tooling; once merge algorithms became reliable, optimistic concurrency (edit freely, merge often) became strictly better — this is why distributed VCS with cheap branching (git) supplanted the austere no-branch discipline the author enforced under SVN.
- Issue trackers and test suites are definitional, not just operational: an executable component-test suite is the actual definition of "done"; an issue list that balloons into the thousands has stopped being a "tracking" system and become a "dump."
- "The problem is detail, not code": diagrams and MDA fail to reduce complexity because the accidental detail programmers manage (e.g., \n vs \r line-ending history) does not disappear in pictures — pictures accumulate their own grammar and accidental complexity, so the abstraction gain is a wash.

## Anti-patterns
- **Enterprise/commercial version control chosen for executive comfort**: sold on feature lists to managers rather than developers; often lacks the speed developers actually need. Author's workaround: check into the mandated system at iteration boundaries while using a lightweight open-source VCS day-to-day.
- **Pessimistic locking as a default policy**: locking a file (or worse, going on vacation while it's locked) blocks the whole team; modern automatic merging makes this unnecessary friction.
- **Letting the issue list grow into the thousands**: once an "issue tracker" holds thousands of items, tracking loses meaning and it becomes an unmanaged dump.
- **Tolerating a broken continuous build**: allowing a red build to persist for a day or more is treated as a serious process failure, not a minor inconvenience.
- **Believing UML/MDA can eliminate the need for programmers**: the author's specific reservation is that MDA assumes code is the problem, when the real problem is *detail* — diagrams don't remove detail, they just relocate it, and if a genuinely useful diagrammatic language is ever invented, programmers (not architects) will be the ones drawing it, because it's still detail management.

## Code Examples
(omit — not code-heavy)

## Reference Tables
| Category | Purpose | Tool examples mentioned |
|---|---|---|
| Source Code Control | Track and merge concurrent code changes | git (favorite), Subversion (SVN), CVS |
| IDE / Editor | Read, write, and structurally manipulate code | IntelliJ (favorite), Eclipse, Emacs, vi, TextMate |
| Issue Tracking | Manage the team's task/bug backlog | Pivotal Tracker (favorite), Lighthouse, wiki, bulletin board + cards |
| Continuous Build | Auto build/test on every commit, report status | Jenkins |
| Unit Testing Tools | Fast, isolated, developer-run test feedback | JUnit (Java), RSpec (Ruby), NUnit (.NET), Midje (Clojure), CppUTest (C/C++) |
| Component Testing Tools | Business-readable executable specifications | FitNesse (favorite, author-written), RobotFX, Green Pepper, Cucumber, JBehave |
| Integration/UI Testing Tools | Thin layer of necessary UI-driven tests | Selenium, Watir |
| UML / MDA | Diagram-driven modeling / code generation | Generic CASE tools / MDA (author skeptical, no specific tool endorsed) |

## Worked Example
(omit — no specific worked example present; the FitNesse-under-SVN vs. FitNesse-under-git branching comparison is illustrative but not a step-by-step worked example)

## Key Takeaways
1. Prefer open-source, developer-written tools over "enterprise" tools bought for managers — speed is the feature developers actually need.
2. Abandon pessimistic locking; trust modern merge tooling and, where possible, adopt distributed VCS (git) for cheap, frequent branching.
3. Start issue tracking with the lightest manual tool (bulletin board and cards) before buying software, and keep the backlog small (dozens to low hundreds) — a huge backlog is a symptom, not a tooling problem.
4. Wire continuous build directly to source control and treat a broken build as a stop-everything event resolved same-day.
5. Choose unit testing tools for trivial run-ability, unambiguous pass/fail feedback, and enforced test independence.
6. Use component testing tools (e.g., FitNesse) as the literal, executable definition of "done," written collaboratively with business/QA.
7. Keep UI-driven integration tests minimal; don't expect UML/MDA to eliminate the detail work of programming.

## Connects To
- **Ch9 (Unit Tests, Clean Code)**: the "F.I.R.S.T." unit-test qualities align directly with this chapter's unit-testing-tool requirements (fast, independent, repeatable, self-validating).
- **Ch11 (Systems, Clean Code)**: continuous build and component testing tools are the operational machinery that keeps a growing system's architecture verifiably clean.
- **Ch27 (Acceptance Testing, The Clean Coder)**: component testing tools (FitNesse) are the concrete implementation of the acceptance-test/"definition of done" philosophy developed there.
- **Ch28 (Testing Strategies, The Clean Coder)**: this appendix's unit/component/integration tool categories map onto the testing pyramid described in that chapter.
- **version control**: git's distributed model and the shift from pessimistic to optimistic concurrency is the chapter's central technical argument.
- **continuous integration**: the Jenkins-based "always green, hooked to VCS" build discipline is a direct precursor to modern CI/CD practice.
- **UML**: treated as a cautionary case study in why abstraction-by-diagram fails to eliminate the essential complexity (detail) of software.
