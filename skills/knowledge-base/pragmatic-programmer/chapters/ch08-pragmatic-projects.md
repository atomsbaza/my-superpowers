# Chapter 8: Pragmatic Projects

## Core Idea
Everything that makes an individual programmer pragmatic — no broken windows, DRY, orthogonality, ruthless testing, honest documentation — must be scaled up to the team and project level through relentless automation, functional (not job-title) team organization, project-wide testing discipline, treating documentation as just another view of the same model, and actively managing (and occasionally exceeding) user expectations.

## Frameworks Introduced
- **Organize Around Functionality, Not Job Functions**: split teams into small, functionally cohesive, largely self-contained groups rather than by job role (analyst/architect/coder/tester).
  - When to use: whenever a project has more than one person and needs to allocate responsibility.
  - How: apply the same criteria used to modularize code — contracts, decoupling (Law of Demeter), orthogonality — to team boundaries; two subteams working on the same module is a warning sign; pair a technical head (development philosophy, orthogonality across teams) with an administrative head (scheduling, business priorities, external liaison).
- **Ubiquitous Automation**: automate every repeatable project procedure — build, test, release, administrivia, web publishing, approvals — because manual procedures are neither repeatable nor consistent across people.
  - When to use: for any operation performed more than once, especially compiling, testing, releasing, and paperwork.
  - How: drive builds through makefiles/scripts (not IDE-only clicking) so `check out, build, test, ship` is a single command; use `make`'s dependency rules to generate code automatically from other sources; schedule unattended jobs with cron; separate nightly builds (frequent, full test suite) from final/release builds (locked/tagged repository, different optimization flags); publish web content automatically from the repository, never by hand.
- **Ruthless Testing**: test relentlessly and automatically across unit, integration, validation/verification, resource-exhaustion, performance, and usability dimensions, treating the found-bug net as something that must only ever get finer.
  - When to use: from the moment any production code exists, continuously through the project.
  - How: build up from unit tests (module contracts) to integration tests (subsystem contracts) to validation/verification (does it meet the actual need, not just the stated spec); explicitly test resource exhaustion and graceful failure; use both real-world and synthetic test data; test the tests themselves by deliberately injecting bugs and confirming detection (consider a "project saboteur" role); apply Tip 66 — every bug found by a human becomes a permanent, automated regression test ("Find Bugs Once").
- **It's All Writing**: treat all documentation — code comments, specs, user manuals — as different views of one underlying model, generated and kept in sync via the same DRY and automation discipline as code.
  - When to use: for both internal (comments, design/test docs) and external (manuals, help) documentation, regardless of whether a technical writer or a developer authors it.
  - How: comment the *why*, not the *how* (the code already shows how); choose one authoritative source of truth per piece of information (a spec, a schema) and derive all other forms (SQL DDL, record structures, web pages) automatically from it; publish documentation online with hyperlinks and date/version stamps rather than static, print-bound copies; use markup languages (DocBook, XSL/CSS) to separate content from presentation so one source serves manuals, web pages, online help, and slideshows alike.

## Key Concepts
- **Quality officer anti-pattern**: delegating "responsibility for quality" to one role is described as ridiculous — quality can only come from every individual contributor's own standards.
- **Chief water tester**: an informal team role whose job is to actively watch for gradual scope/schedule/requirement drift (the team-level version of the boiled frog).
- **Team branding**: giving a project a distinct, even zany, name/logo as a lightweight way to give the team a communicable identity to the rest of the organization.
- **Recursive make pitfalls**: hierarchical makefiles can miss cross-invocation dependencies, since `make` only reasons about dependencies within a single invocation.
- **Final build**: a distinct build target (e.g., `make final`) with its own optimization/debug flags and repository locking/tagging, requiring its own fresh round of testing since it isn't identical to the nightly build.
- **McCabe Cyclomatic Complexity / response set / class coupling ratios**: code and design metrics used comparatively across a codebase (not as absolute pass/fail grades) to spot modules that deviate suspiciously from their peers.
- **Stroop Effect**: misleading names (e.g., a function called `getData` that actually writes to disk) cause a documented cognitive interference effect — the same mechanism that makes it hard to read the word "blue" printed in red ink.
- **Great Expectations / managing (not just meeting) expectations**: project success is measured against user expectations, not just against the written specification — falling short of or (less obviously) drastically overshooting expectations both register as a kind of failure.
- **Pride and Prejudice (signing your work)**: attaching your name to code as a mark of accountability and craftsmanship, balanced against the risk of territorial "prejudice" against others' code or foundational shared modules.

## Mental Models
- Think of bug-finding as fishing with nets: fine nets (unit tests) catch minnows, coarse nets (integration tests) catch sharks — and any bug that slips through means the net itself needs mending (add a regression test), never just a one-off fix.
- Think of automation the way a modern car's ignition replaced the multi-page Model-T starting procedure: once the "starter" is built, you just turn the key — repeatable, foolproof, no room for human variation.
- Think of the team as a modular system: apply the exact same decoupling/orthogonality/contract criteria used for code modules to team boundaries, and the same warning signs (two teams touching one module) apply.
- Think of documentation as a view over a model, exactly like the MVC pattern from Chapter 5 — the source of truth lives in one place, and every published form (manual, web page, help file) is generated, not hand-maintained.

## Anti-patterns
- **Manual, IDE-click-driven installation/build procedures**: the chapter's cited example (developers each installing IDE add-ons via multi-page manual instructions) shows how "people just aren't as repeatable as computers," producing per-machine bugs that "appear on one machine but not others."
- **Leaving testing to the last minute**: testing "cut against the sharp edge of a deadline" means bugs are found (or missed) too late and too expensively; testing should start as soon as any production code exists.
- **Meetings-only code review with no automated tracking**: cited research (Glass, CACM 1999) found code inspection effective but conducting the review itself in a meeting is not — approval workflows should still be automated even if a walkthrough happens.
- **Documentation as an afterthought "thrown over the wall" to technical writers**: breaks the DRY/model-view principle and lets code and docs drift out of sync.
- **Over-precise dead metrics ("passing grade" thinking) instead of comparative analysis**: chasing a single metric threshold per module misses that most design metrics are only meaningful compared across the codebase's own modules.
- **Rigid job-function team silos** (coders can't talk to testers, who can't talk to the architect): produces poor context-sharing and an us-vs-them culture between roles.

## Code Examples
```makefile
.SUFFIXES: .java .class .xml
.xml.java:
	perl convert.pl $< > $@
.java.class:
	$(JAVAC) $(JAVAC_FLAGS) $<
```
- **What it demonstrates**: using `make`'s dependency mechanism to automatically regenerate a `.java` file from an `.xml` source and compile it, so `make test.class` alone drives the whole chain — a concrete instance of Ubiquitous Automation and of generating code from a single authoritative source (DRY).

## Reference Tables
| Testing dimension (What to Test) | Concern |
|---|---|
| Unit testing | Does each module honor its own contract? |
| Integration testing | Do subsystems work and play well together? |
| Validation and verification | Does it meet the actual need, not just the stated spec? |
| Resource exhaustion, errors, recovery | Memory, disk, CPU, bandwidth limits; graceful failure |
| Performance testing | Does it meet real-world load/throughput requirements? |
| Usability testing | Does it fit the user "like an extension of the hand"? |

| Common resource limits to test | |
|---|---|
| Memory | Disk space |
| CPU bandwidth | Wall-clock time |
| Disk bandwidth | Network bandwidth |
| Color palette | Video resolution |

## Worked Example
The code-review approval automation example: a team wants to automate the scheduling and approval of code reviews without losing the paper trail. Developers mark a source file with a status comment, `/* Status: needs_review */`. A script scans all source files for this marker and posts the resulting list as a web page, automatically emailing the relevant reviewers or even scheduling a meeting via calendar software. Reviewers register approval or disapproval on a web form, and the script flips the marker to `reviewed` once done — whether or not an actual walkthrough meeting happens is left up to the team, since (per cited research) the meeting itself isn't what makes inspection effective; the paperwork is what gets automated regardless. This threads together three of the chapter's threads at once: Ubiquitous Automation (approval workflow driven by scripts, not manual tracking), It's All Writing (the status marker lives in the source itself, one authoritative location), and Ruthless Testing's project-wide quality culture (reviews are treated as a first-class, tracked process, not an afterthought).

## Key Takeaways
1. Organize teams the same way you organize code: by functional cohesion and low coupling, not by job title.
2. Automate the entire build/test/release pipeline down to a single command; anything done by hand across multiple people will drift.
3. Treat every found bug as a permanent addition to the regression suite — "Find Bugs Once," never twice.
4. Test resource exhaustion, performance, and usability explicitly; a bug-free system solving the wrong problem, or failing ungracefully under load, is still a failure.
5. Pick one authoritative source per piece of information and generate every other form (schema, docs, web page) from it automatically — documentation is a view, not a separate deliverable.
6. Comment the *why* behind code, never the *how* the code already shows; misleading names actively fight your reader's brain (Stroop Effect).
7. Success is measured against user expectations, not the written spec — communicate expectations continuously, and occasionally add small delighters beyond what was asked.
8. Sign your work and take pride in it, while still respecting and being willing to touch others' code — communal ownership, not fiefdoms.

## Connects To
- **Ch 6 (Code That's Easy to Test)**: unit testing there is the foundation Ruthless Testing here builds integration/validation/performance/usability testing on top of.
- **Ch 5 (Decoupling and the Law of Demeter, It's Just a View)**: cited directly as the basis for organizing teams functionally and for treating documentation as a view of the model.
- **Ch 1 (Software Entropy / No Broken Windows, Stone Soup and Boiled Frogs)**: scaled up here to "No Broken Windows" and "Boiled Frogs" as team-level (not just individual) responsibilities.
- **Ch 7 (The Requirements Pit, Great Expectations)**: rapport built with users during requirements digging is the foundation for managing expectations described here.
