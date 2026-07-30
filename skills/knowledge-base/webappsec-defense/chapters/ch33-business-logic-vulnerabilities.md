# Chapter 33: Business Logic Vulnerabilities

## Core Idea
Unlike archetypal vulnerabilities (injection, DoS) that recur in consistent shapes across applications, business logic vulnerabilities are unique to a single application's specific rules — they are the hardest to find and almost impossible to catch with automated tooling, but often the most profitable to exploit.

## Frameworks Introduced
- **Application logic vs. business rules distinction**: Separates generic computing tasks from business-specific policy, to locate where unique vulnerabilities can hide.
  - When to use: When triaging whether a bug is a known archetype (injection, DoS) or something specific to this business.
  - How: Application logic performs generic tasks (rendering, network calls); business rules encode business-specific policy (e.g., "cancellation allowed only >24 hours before booking"). A flaw in the implementation of a business rule is a business logic vulnerability.
- **Custom Math Vulnerabilities**: Exploiting missing or incorrect validation around an application's bespoke mathematical/financial operations.
  - When to use: Anywhere an app performs custom calculations (transfers, balances, pricing) rather than delegating to a hardened, audited library.
  - How: Identify a multi-step operation with a math component; check whether every input to that math is validated (e.g., sufficient balance) as rigorously as the math itself is correct; if either check is missing, the operation can be driven into an unintended state.
- **Programmed Side Effects**: Finding unintended consequences that emerge only when intended functionality is used in combination or at scale.
  - When to use: Against systems with dynamic/market-driven internal state (pricing engines, liquidity pools, reward systems) where the developer modeled the common case but not edge-case interactions.
  - How: Reverse-engineer the system's operating assumptions (e.g., "local price should approximate global price"), then find the scale or timing threshold at which those assumptions break down and can be manipulated for profit.
- **Quasi-Cash Attacks**: Chaining multiple interworking financial systems to convert a promotional incentive into unlimited real cash.
  - When to use: Against reward/cashback programs that don't distinguish "real" purchases from self-referential, near-zero-cost transactions routed through a financial intermediary.
  - How: Find an intermediary payment processor with a low fee that is lower than the reward rate; create a self-paid invoice through it; collect the reward minus the intermediary's fee as pure profit; automate the cycle.
- **Vulnerable Standards and Conventions (IEEE754 edge case)**: Using known limitations of standardized number formats as a low-cost signal for where logic bugs might live.
  - When to use: When you have no visibility into server-side implementation but know it runs on a mainstream language (JavaScript, Java, Ruby, Python) using IEEE754 floats.
  - How: Look for compounding/repeated decimal arithmetic (especially multiplication or exponentiation of many small transactions) where accumulated floating-point precision loss could diverge recorded and true balances over enough iterations.

## Key Concepts
- **Business logic vulnerability**: A flaw in the implementation of business-specific rules, as opposed to a flaw in generic, cross-application logic.
- **Archetypal vulnerability**: A consistently-shaped, categorizable vulnerability (injection, DoS) that recurs across many applications and is catchable by generic tooling.
- **Edge case**: An input or usage pattern outside the developer's modeled "primary use case," which is where business logic vulnerabilities concentrate.
- **Liquidity pool manipulation**: Exploiting a limited local reserve of an asset (e.g., cryptocurrency) whose price is assumed to track a larger global market, by cornering the local supply.
- **Quasi-cash intermediary**: A payment processor or merchant service (not itself a bank) that lets programmatic, self-directed transactions be settled as if real, exploitable purchases.
- **IEEE754 precision loss**: The floating-point standard's trade-off of numeric precision for storage efficiency, producing approximated (not exact) results for many decimal calculations.
- **Edge-case mapping methodology**: The practice of writing down every intended use case and then deliberately listing what's NOT handled for each, turning gaps into attack vectors.

## Mental Models
- Think of business logic vulnerabilities as bugs in the business plan encoded as code, not bugs in the code itself — you're attacking a policy gap, not a syntax error.
- Use "walk the primary use case, then ask what's NOT covered" as the standard discovery loop: map the intended customer journey first, then brainstorm every edge case the map doesn't account for.
- Treat automated scanners as structurally blind here: a tool tuned to detect injection or DoS has no model of "should a customer be allowed to invoice themselves," so business logic hunting is inherently manual and domain-specific.
- Treat compounding/automation as the amplifier: a $40 quasi-cash arbitrage or a fraction-of-a-cent precision loss is trivial once, but becomes $57,600/day or a material balance drift once scripted and repeated at machine speed.

## Anti-patterns
- **Validating one side of a transaction but not both**: MegaBank's transfer checked that the recipient existed but never checked the sender's balance, allowing unlimited value creation between colluding accounts.
- **Assuming local market behavior mirrors global market behavior at any scale**: MegaCrypto assumed its liquidity pool rates would track global crypto prices without accounting for how small a local pool is relative to a determined buyer.
- **Designing rewards programs without modeling self-dealing**: MegaCard's 5% cashback didn't anticipate a customer also acting as their own merchant via a low-fee intermediary, turning an acquisition incentive into an arbitrage machine.
- **Relying on manual/automated security tooling to find business logic bugs**: These tools scan for generic vulnerability shapes and structurally cannot express "is this specific business rule enforced correctly."

## Code Examples
```text
0.1 + 0.2   // returns 0.30000000000000004 in JavaScript's V8 interpreter
```
- **What it demonstrates**: IEEE754 floating-point precision loss — a tiny, universally-reproducible arithmetic error that can compound into material balance drift under high-frequency or multiplicative financial calculations.

## Reference Tables
Quasi-cash attack cycle (MegaCard + PayBuddy), reconstructed step-by-step from the chapter:

| Step | Action | Running effect |
|---|---|---|
| 1 | Create a $1,000 invoice on PayBuddy (merchant account Henry controls) | — |
| 2 | Pay the $1,000 invoice using the MegaCard | +$1,000 credit on card |
| 3 | PayBuddy settles, minus its 1% fee | $990 credited to merchant account |
| 4 | MegaCard issues 5% cashback on the $1,000 purchase | +$50 to personal bank account |
| 5 | Transfer the $990 from PayBuddy to personal bank account | +$990 to personal bank account |
| 6 | Net result per cycle | $1,040 in, $1,000 spent = **+$40 profit** |

Automated at one cycle/minute: $2,400/hour, ≈$57,600/24 hours.

## Worked Example
The chapter's MegaBank transfer flow is used as the canonical custom-math vulnerability walkthrough.

1. **Intended flow**: User A designates a $500 transfer to User B; server validates User B exists; server sends/receives a confirmation; server debits User A's balance by $500; server credits User B's balance by $500; server confirms completion to User A.
2. **The gap**: The server validates that the recipient (User B) exists, but never validates that the sender (User A) actually has $500 available to send.
3. **Best case**: A database-level constraint (e.g., a non-negative balance check) catches the missing application-level validation and the transaction errors out — the bug exists but is contained by a lower layer.
4. **Worst case**: No such constraint exists. User A's balance floors at $0 while User B's balance keeps incrementing by $500 per repeated transaction. Because User A and User B can collude (or be the same attacker's two accounts), they can extract thousands of dollars before the bank's monitoring notices.
5. **Root cause framing**: The vulnerability requires no injection, no malformed request, and no protocol violation — it is a hacker "finding a way to bypass intended functionality while staying in line with the programmed rules," which is precisely why static analysis tooling cannot find it.

## Key Takeaways
1. Business logic vulnerabilities require deep domain knowledge of a specific application's rules, not generic vulnerability-pattern matching — they are largely invisible to automated scanners.
2. Always check that both sides of a financial or stateful operation are validated: verifying a recipient exists is meaningless if the sender's sufficient balance is never checked.
3. Assumptions that local system behavior will mirror a larger external market (or any external invariant) become exploitable the moment someone can outspend or corner the local pool.
4. Reward/incentive programs must be modeled against self-dealing and intermediary-routed transactions, not just the archetypal "honest customer" journey.
5. Use the "map primary use cases, then enumerate what's not handled" method as the core, repeatable technique for discovering business logic vulnerabilities in any target application.
6. Compounding, low-value bugs (precision loss, small arbitrage margins) become material once an attacker automates and repeats them at machine speed — always evaluate a bug's impact at scale, not per-transaction.

## Connects To
- **Mitigating Business Logic Vulnerabilities**: Directly addresses the gaps shown here — balance/state validation on both sides of a transaction, rate-limiting/anomaly detection on liquidity and rewards systems, and decimal/fixed-point arithmetic instead of raw floating point for financial calculations.
- **Ch 31 Client-Side Attacks / Ch 32 Exploiting Third-Party Dependencies (this book)**: Contrasted directly in the text as archetypal, tool-discoverable vulnerability classes, versus the application-unique, manually-discovered nature of business logic flaws.
