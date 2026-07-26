# Chapter 4: Comments

## Core Idea
Comments are, at best, a necessary evil — a confession of failure to express intent in code. Since comments cannot be maintained as reliably as code, they should be minimized in favor of clear, self-explanatory code, and used only when no code construct can carry the same meaning.

## Frameworks Introduced
- **Comments Do Not Make Up for Bad Code**: when code is confusing, the fix is to clean the code, not to explain the mess with a comment.
  - When to use: whenever the urge to write a comment arises from code being disorganized or unclear.
  - How: refactor — extract functions, rename variables — until the code says what the comment would have said, then delete the comment impulse entirely.
- **Explain Yourself in Code**: most intent that programmers try to capture in comments can instead be captured by a well-named function or variable.
  - When to use: any time a comment is about to restate what a conditional or block of code does.
  - How: replace the comment with a descriptive function/method extraction, e.g. turn a flag-checking `if` into `if (employee.isEligibleForFullBenefits())`.
- **Good Comments vs. Bad Comments taxonomy**: comments are sorted into a small set of justified categories (legal, informative, intent, clarification, warning, TODO, amplification, public API docs) versus a much larger set of anti-patterns to eliminate.
  - When to use: as a checklist when reviewing whether an existing or proposed comment earns its place.
  - How: ask "could this be a function/variable name instead?" first; if truly not, check it against the good-comment categories; if it doesn't fit one, delete it.

## Key Concepts
- **Necessary evil**: Martin's framing that comments are never a source of celebration — every comment written is evidence of a failure to express oneself in code.
- **Comment rot**: comments drift from the code they describe as code changes, since programmers cannot realistically keep both in sync — the older and farther from its code, the more likely a comment is wrong.
- **Truth in code**: only the code itself is a fully accurate source of what a program does; comments are a secondary, unverified account.
- **Mumbling**: a comment written half-heartedly (because "the process requires it") that fails to actually communicate meaning to future readers.
- **Nonlocal information**: a comment that describes something about the system far away from the code it sits next to, so it goes stale independently of the code it's attached to.
- **Inobvious connection**: a comment whose relationship to the code it annotates isn't clear even after reading both — the comment itself then needs explaining.
- **Function Headers**: for short, well-named functions, a header comment is superfluous — the name should already carry the description.

## Mental Models
- Think of writing a comment as pulling an emergency brake: pause and ask "can this be code instead?" before committing to it.
- Use a comment only when you've exhausted the option of a better function name, extracted method, or clearer variable — comments are the last resort, not the first tool.
- Treat an inaccurate comment as strictly worse than no comment: silence forces the reader to check the code; a wrong comment actively misleads them into false confidence.
- Think of source control (not comments) as the correct home for authorship, history, and "who changed what when" — journal entries and bylines belong in `git log`, not in the file.

## Anti-patterns
- **Mumbling**: a vague, half-explained comment (e.g., an empty catch block with `// No properties files means all defaults are loaded`) that leaves the reader needing to dig through other code to understand it — fails to communicate and isn't worth the bits it consumes.
- **Redundant Comments**: comments that take longer to read than the code and add no information beyond what the code already states plainly (e.g., a javadoc restating a getter's obvious behavior).
- **Misleading Comments**: comments that are subtly inaccurate about what the code actually does (e.g., claiming a method "returns when X becomes true" when it actually polls with a timeout), causing bugs in code written against the false claim.
- **Mandated Comments**: comments forced by a blanket rule ("every function must have a javadoc") that add clutter and create fresh opportunities for lies, regardless of whether the comment adds value.
- **Journal Comments**: change-log entries accumulated at the top of a file over years — made obsolete by source control and should be deleted entirely.
- **Noise Comments**: comments that restate the obvious (`/** Default constructor. */`) so relentlessly that the eye learns to skip all comments, including the useful ones.
- **Scary Noise**: noisy javadoc-style comments (often copy-pasted, sometimes with copy-paste errors) that exist only to look like documentation without providing any.
- **Position Markers**: banner comments like `// Actions ////////` used to divide a file — become background noise if overused; only justified rarely, for genuinely long files.
- **Closing Brace Comments**: `} // while`, `} // try` on nested closing braces — a signal that the function is too long; shorten the function instead of decorating the braces.
- **Attributions and Bylines**: `/* Added by Rick */`-style tags — go stale and are redundant with what source control already tracks accurately.
- **Commented-Out Code**: dead code left in comments — nobody dares delete it, so it accumulates as clutter; source control already preserves history, so just delete it.
- **HTML Comments**: HTML markup embedded in source comments — makes the comment unreadable in the one place it should be easy to read (the editor); HTML rendering should be a tool's job, not the source's.
- **Nonlocal Information**: a comment describing systemwide facts (e.g., a default port value) in a place that has no control over that fact, so it silently rots when the real value changes elsewhere.
- **Too Much Information**: dumping irrelevant historical or technical detail (e.g., pasting the RFC spec text) into a comment where the reader needs none of it.
- **Inobvious Connection**: a comment whose link to the specific line/expression it annotates isn't clear, forcing the reader to reverse-engineer what it's even talking about.

## Code Examples
```java
// Before: comment explains an unreadable condition
// Check to see if the employee is eligible for full benefits
if ((employee.flags & HOURLY_FLAG) && (employee.age > 65))

// After: comment eliminated by expressive code
if (employee.isEligibleForFullBenefits())
```
- **What it demonstrates**: the central technique of the chapter — replacing a comment with a self-explanatory function name so the code itself carries the intent.

## Reference Tables
| Good Comment Category | Purpose | Example |
|---|---|---|
| Legal Comments | satisfy corporate/license requirements | copyright header, ideally collapsed by the IDE |
| Informative Comments | convey basic facts not obvious from the signature | comment describing what a regex pattern matches |
| Explanation of Intent | document the reasoning behind a decision | comment explaining why an odd sort order was chosen |
| Clarification | translate an obscure value into readable terms, esp. in code you can't change | `assertTrue(a.compareTo(b) == -1); // a < b` |
| Warning of Consequences | flag risk or non-obvious constraints | `// SimpleDateFormat is not thread safe, so we need to create each instance independently` |
| TODO Comments | flag known, deferred work | `//TODO-MdM these are not needed` |
| Amplification | stress the importance of something that looks trivial | `// the trim is real important. It removes...` |
| Javadocs in Public APIs | document a public API surface for consumers | Java standard library javadocs |

| Bad Comment Category | Why it fails |
|---|---|
| Mumbling, Redundant, Misleading | fail to inform or actively mislead |
| Mandated, Journal, Noise, Scary Noise | clutter added by process/habit, not need |
| Position Markers, Closing Brace, Attributions | low-value bookkeeping better handled by tooling/structure |
| Commented-Out Code, HTML Comments | pollute readability, better served by source control / rendering tools |
| Nonlocal Info, Too Much Info, Inobvious Connection | comment and code/context mismatch, breaking trust |

## Worked Example
Martin presents `GeneratePrimes.java` (Listing 4-7), written as a deliberately "well-documented" bad example: a large class-level javadoc with unrelated biographical trivia about Eratosthenes, a `@param` comment restating the obvious, and inline comments on nearly every line (`// size of array`, `// bump count.`, `// return the primes`) that just restate what the adjacent code already says. He then shows the refactored `PrimeGenerator.java` (Listing 4-8): the sieve logic is broken into well-named private methods (`uncrossIntegersUpTo`, `crossOutMultiples`, `determineIterationLimit`, `putUncrossedIntegersIntoResult`), leaving only two comments in the entire class — a brief class-level explanation of the algorithm, and one explaining the nonobvious rationale for using the square root as the iteration limit. The reduction from a dozen line comments to two shows that expressive decomposition removes the need for almost all of them; the two that remain survive because no naming or restructuring could carry that specific piece of reasoning.

## Key Takeaways
1. Before writing a comment, ask whether a better function or variable name would make it unnecessary — try that first.
2. Treat every comment as a maintenance liability that will drift from the code it describes; keep the ones you must write as close and as accurate as possible.
3. Delete journal comments, commented-out code, and attribution comments outright — source control already does that job better.
4. Reserve comments for the few things code truly cannot say: legal notices, non-obvious warnings, intent behind a debatable decision, and public API documentation.
5. A rule that mandates comments (e.g., "every method needs a javadoc") produces net-negative clutter; comments should be earned case by case, not mandated wholesale.
6. When refactoring toward fewer comments, prefer extracting well-named functions over adding explanatory prose — this was the primary technique in the chapter's worked example.
7. If a comment needs its own explanation to be understood, it has already failed its purpose.

## Connects To
- **Ch 2 (Meaningful Names)**: the primary substitute for most comments is a well-chosen function or variable name — the naming discipline from Ch. 2 is what makes "Explain Yourself in Code" possible.
- **Ch 3 (Functions)**: the worked example's fix relies on extracting small, well-named functions (`crossOutMultiplesOf`, `notCrossed`), the exact discipline covered in the Functions chapter.
- **Ch 17 (Smells and Heuristics)**: several bad-comment categories here (Commented-Out Code, Mandated Comments) reappear as catalogued code smells later in the book.
- **Version control systems (external concept)**: repeatedly cited as the correct replacement for journal comments, attributions, and commented-out code — Martin assumes source control makes these comment types obsolete.
