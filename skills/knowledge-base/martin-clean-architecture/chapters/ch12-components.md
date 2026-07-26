# Chapter 12: Components

## Core Idea
Components are the units of deployment (jar/gem/DLL/binary aggregate) and, historically, their entire design evolved from a decades-long battle against compile-and-link turnaround time; well-designed components remain independently deployable and independently developable regardless of how they're ultimately packaged.

## Frameworks Introduced
- **Component (definition)**: "The smallest entities that can be deployed as part of a system" — the granule of deployment in every language (jar in Java, gem in Ruby, DLL in .NET, binary aggregates in compiled languages, source aggregates in interpreted languages).
  - When to use: As the basic unit of architectural reasoning above the class level — components can be linked into a single executable, aggregated into an archive, or independently deployed as dynamically loaded plugins.
  - How: Regardless of final deployment shape, preserve independent deployability and independent developability as the design goal for each component.
- **Murphy's Law of program size** (Martin's framing): "Programs will grow to fill all available compile and link time." Used to explain why every generation of tooling improvement (relocatable binaries, linkers, separate link phase) was eventually swallowed by programmer ambition, until hardware speed (Moore's Law) finally outpaced it in the mid-1990s.

## Key Concepts
- **Relocatable binary**: Compiled code instrumented with flags telling a loader which memory references must be adjusted, so it can be loaded at any address rather than a fixed, hardcoded one.
- **External reference / external definition**: Compiler-emitted metadata — a reference is a call to a function not defined in this unit; a definition is a function this unit provides — that a linking loader resolves by matching references to definitions.
- **Linking loader**: A loader that both resolves external references/definitions and relocates code at load time; became too slow once programs and libraries grew large, motivating the split into separate linker and loader phases.
- **Linker**: A separate, slower offline tool that performs the linking step in advance, producing a linked relocatable that a fast loader can then load quickly at runtime — introduced to decouple link time from load time.
- **Component plugin architecture**: The modern arrangement (Active-X, shared libraries, .jar files) where independently compiled components are linked together at load time in seconds, enabling runtime-pluggable systems (e.g., Minecraft mods, ReSharper DLL plugins).

## Mental Models
- Think of the entire history of components as a tug-of-war between Murphy (programs grow to fill available compile/link time) and Moore (hardware gets exponentially faster) — Moore eventually won in the mid-1990s, making link-time linking cheap again and enabling the plugin architectures we use today.
- Use "independently deployable AND independently developable" as the two-part test for whether something is a well-designed component, not just "is it packaged as a jar/DLL."
- Picture early non-relocatable programs as tenants who could only live at one specific street address (origin statement) — relocatable binaries were the invention of movable housing, letting the loader decide the address at load time.

## Anti-patterns
- **Treating a component purely as a packaging artifact (jar/DLL) without independent developability**: Martin's definition explicitly requires both independent deployability and independent developability — a component that can be built into a jar but not developed/tested in isolation from the rest of the system misses the point.
- **(Historical) hardcoding load addresses (origin statements) for library code**: Forced applications to fragment around fixed library address ranges (Figure 12.2) as libraries grew, an unsustainable coupling that relocatability was invented to solve — illustrates why hardcoded positional/addressing assumptions don't scale.

## Code Examples
```
        *200
        TLS
START,  CLA
        TAD     BUFR
        JMS     GETSTR
        CLA
        TAD     BUFR
        JMS     PUTSTR
        JMP     START
BUFR,   3000
GETSTR, 0
        DCA     PTR
NXTCH,  KSF
        JMP     -1
        KRB
        DCA     I PTR
        TAD     I PTR
        AND     K177
        ISZ     PTR
        TAD     MCR
        SZA
        JMP     NXTCH
K177,   177
MCR,    -15
```
- **What it demonstrates**: A PDP-8 program with a hardcoded `*200` origin statement — illustrating the pre-relocatable era where programmers manually fixed the load address of their code, the historical starting point the rest of the chapter's narrative (relocatability → linkers → components) is built to escape from.

## Reference Tables
<!-- no comparison/decision table in this chapter -->

## Worked Example
The chapter traces one continuous historical arc rather than a single illustrative scenario:
1. **Fixed-address era**: Programmers set an explicit origin address (`*200`) and included library source directly in their compile, because programs weren't relocatable — compilation of large function libraries could take hours.
2. **Separate compiled libraries**: To cut compile time, libraries were compiled once to a fixed address (e.g., 2000₈) with a symbol table, loaded alongside the application — but applications eventually outgrew the address space left for them (Figure 12.1), forcing fragmented address segments (Figure 12.2) as libraries grew.
3. **Relocatable binaries + linking loader**: Compilers emitted relocatable code plus external-reference/external-definition metadata; a linking loader could load and relocate multiple binaries at arbitrary addresses and resolve calls between them — but reading many libraries off slow tape/disk devices made this too slow once programs got ambitious again (hour-long turnaround in the 1960s-70s).
4. **Split into linker + loader**: The slow linking step was moved into an offline linker producing a fast-loading linked relocatable — but by the 1980s (C-era, hundreds of thousands of LOC), compile-link turnaround crept back up to an hour or more (Murphy's Law of program size).
5. **Moore's Law wins**: By the mid-1990s, hardware speed (disks, RAM caching, clock rates 1MHz→100MHz) outpaced program-size growth, shrinking link time to seconds — enabling the modern component plugin architecture (.jar, DLL, shared libraries) used casually today.

## Key Takeaways
1. A component is defined by two properties together — independent deployability and independent developability — not merely by its packaging format.
2. The entire discipline of component design exists because of a decades-long engineering battle to decouple compile/link time from program size (Murphy's Law of program size vs. Moore's Law).
3. Relocatability (load-time address flexibility) and the external-reference/external-definition mechanism are the technical foundations that make independently-compiled components possible at all.
4. Modern plugin architectures (mods, IDE plugins) are only "casual" today because 1990s hardware finally made load-time linking fast — historically this was a hard-won capability, not a given.
5. When evaluating whether a piece of code is a proper "component" in the architectural sense, check both packaging (can it be deployed alone) and workflow (can it be developed/tested alone).

## Connects To
- **Ch 13-14 (Component Cohesion / Coupling, forward reference)**: This chapter sets up the physical/historical definition of components; the immediately following chapters (Part IV) define the principles — cohesion (REP, CCP, CRP) and coupling (ADP, SDP, SAP) — for how to compose classes into well-designed components.
- **Ch 7 (SRP) / Ch 10 (ISP)**: Explicitly foreshadowed as reappearing at the component level as the Common Closure Principle and Common Reuse Principle, respectively, once component boundaries (this chapter's subject) are established.
