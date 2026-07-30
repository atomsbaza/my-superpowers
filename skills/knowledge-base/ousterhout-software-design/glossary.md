# Glossary

**Change Amplification** — A symptom of complexity where a seemingly simple change requires code modifications in many different places across the system. (Ch 2)
**Cognitive Load** — The amount of knowledge a developer must hold in their head in order to complete a task. (Ch 2)
**Deep Module** — A module whose interface is significantly simpler than its implementation. It hides a large amount of complexity from its callers. (Ch 4)
**Information Hiding** — Designing a module to encapsulate specific knowledge or design decisions, hiding them from the rest of the system. (Ch 5)
**Information Leakage** — When a design decision is reflected in multiple modules, forcing them all to change if the decision changes. (Ch 5)
**Interface** — Everything a developer needs to know in order to use a module (method signatures, comments, side effects). (Ch 4)
**Pass-through Method** — A method that does little to no work other than calling another method with the exact same signature. A sign of shallow modules. (Ch 7)
**Shallow Module** — A module whose interface is relatively complex compared to the functionality it provides. (Ch 4)
**Strategic Programming** — An approach where the primary goal is to produce a great design that makes future changes easier, rather than just getting the immediate feature to work. (Ch 3)
**Tactical Programming** — An approach focused entirely on getting the current feature to work quickly, often at the expense of system design. (Ch 3)
**Temporal Decomposition** — An anti-pattern where a system is structured based on the order in which operations happen (e.g., Read, Parse, Write), rather than by information hiding, causing knowledge to leak across the modules. (Ch 5)
**Unknown Unknowns** — A symptom of complexity where it is not obvious which pieces of code must be modified, or what information a developer must have, to complete a task. (Ch 2)\n