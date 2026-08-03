# Documentation Frameworks: Diátaxis, ADRs, C4, Runbooks

## 1. The Diátaxis Framework

Created by Daniele Procida, **Diátaxis** is an intent-focused documentation architecture that categorizes technical content into four distinct, non-overlapping quadrants based on two core axes: **user activity** (*studying* vs. *working*) and **content nature** (*practical* vs. *theoretical*).

```
 DIÁTAXIS FRAMEWORK QUADRANTS
 
 PRACTICAL THEORETICAL
 ┌───────────────────┬───────────────────┐
 STUDYING │ TUTORIALS │ EXPLANATION │
 │ (Learning-Oriented)│ (Understanding-Oriented)│
 ├───────────────────┼───────────────────┤
 WORKING │ HOW-TO GUIDES │ REFERENCE │
 │ (Goal-Oriented) │ (Information-Oriented)│
 └───────────────────┴───────────────────┘
```

### Quadrant Purpose & Rules

1. **Tutorials (Learning-Oriented)**
 * **Axis**: *Practical + Studying*.
 * **Purpose**: Guiding a beginner through their first successful hands-on experience—described metaphorically as "a lesson, safely in the hands of an instructor".
 * **Rules**: Must be prescriptive, linear, and step-by-step. Focus on building user confidence through immediate success. Avoid theoretical digressions, edge cases, alternative configurations, or explaining internal mechanics during the lesson.

2. **How-To Guides (Goal-Oriented)**
 * **Axis**: *Practical + Working*.
 * **Purpose**: Providing a task-focused "recipe" to solve a specific real-world problem.
 * **Rules**: Outcome-focused and practical. Assumes the reader is a competent user with baseline domain knowledge. Provides sequential execution steps, code samples, and variations without re-explaining basic concepts.

3. **Reference (Information-Oriented)**
 * **Axis**: *Theoretical + Working*.
 * **Purpose**: Delivering factual, technical descriptions of the underlying system machinery for fast information retrieval.
 * **Rules**: Factual, dry, terse, and complete. Structure must mirror the software itself for predictable lookup (e.g., API schemas, parameter tables, CLI options). Must be completely free of instructional prose, tutorial steps, or opinions.

4. **Explanation (Understanding-Oriented)**
 * **Axis**: *Theoretical + Studying*.
 * **Purpose**: Illuminating concepts, architecture, background, and design trade-offs to build the reader's mental model ("why" things work).
 * **Rules**: Narrative, discursive, and comparative. Connects concepts, provides high-level context, explores historical choices, and explains architectural rationale.

### Common Mistakes & Content Drift
* **"Chatty" Reference Pages**: Injecting tutorial steps, setup instructions, or narrative background into reference docs, which clutters the page and slows down expert lookup.
* **How-To Guides Bloated with Explanations**: Interrupting procedural execution steps with deep theoretical rationale instead of linking out to an Explanation page.
* **Tutorials Distracted by Edge Cases**: Pausing a beginner's guided lesson to explain alternative flags or complex mechanics, causing cognitive overload.
* **Content Drift**: As products evolve, unmonitored contributions blur quadrant boundaries, degrading trust across the entire documentation suite.

---

## 2. Docs-as-Code Principles & Toolchain

The **Docs-as-Code** philosophy treats technical documentation with the exact same engineering discipline, workflows, and tools as software code.

### Core Principles
* **Version Control Co-location**: Documentation source files (plain-text markup) are stored in Git repositories alongside application source code.
* **Peer Code Review**: Documentation changes are submitted via pull/merge requests and subjected to mandatory peer review alongside code changes.
* **Automated Quality Testing**: CI/CD pipelines run automated linters, syntax checks, style guide rules, and link checkers before code is merged.
* **Automated Publishing**: Static Site Generators (SSGs) compile plain-text markup into hosted developer portals automatically upon merge.
* **Issue Tracking**: Documentation tasks, gaps, and bugs are tracked using standard issue trackers (e.g., GitHub Issues, Jira).

### Historical Lineage
* **Twitter Docbird (2014)**: Pioneered automated build pipelines for in-repo documentation templates.
* **Google g3doc (2015)**: Co-located Markdown docs inside Google's monorepo, establishing the principle that code is the ultimate authority and docs must update in the same commit.
* **Spotify TechDocs / Backstage (2019)**: Open-sourced in-repo docs rendering directly inside an Internal Developer Portal (IDP).

### Toolchain Ecosystem

#### 1. Plain-Text Markup Languages
* **CommonMark / Markdown**: Standard, lightweight plain-text format.
* **MDX**: React components embedded inside Markdown.
* **Markdoc**: Stripe’s open-source Markdown superset that parses content into a declarative Abstract Syntax Tree (AST) for static validation, safe variable interpolation, and custom UI tags without executing untrusted JavaScript.

#### 2. Static Site Generators (SSGs) & Renderers
* **Docusaurus**: Meta's React/MDX site generator with native versioning, localization, and search integrations.
* **MkDocs / Material for MkDocs**: Fast Python-based static site builder widely used for platform documentation.
* **Nextra**: Lightweight Next.js/MDX framework featuring file-system routing.
* **Docsify**: Client-side Markdown rendering engine with zero build step.
* **Read the Docs**: Automated build and hosting platform for Markdown and Sphinx docs.

#### 3. CI/CD Quality Linters & Gates
* **`markdownlint`**: Enforces Markdown syntax formatting, list indentation, and heading hierarchies.
* **`Vale`**: Customizable prose linter enforcing style guide compliance, terminology consistency, active voice, and readability scores.
* **`Lychee` / `Baler`**: Fast, async link-checking tools that scan for broken internal paths, dead external URLs, and expired domains.
* **`lint-doc.sh`**: Custom repository scripts enforcing mandatory YAML frontmatter, long-form `curl` parameters, and lower-case file naming.

---

## 3. Architecture Decision Records (ADRs)

Coined by Michael Nygard in 2011, an **Architecture Decision Record (ADR)** is a short, immutable document capturing a single architecturally significant decision, its context, and its consequences. ADRs are stored in version control co-located with source code (Docs-as-Code).

### When to Write vs. Skip
* **Write an ADR**: For architecturally significant requirements (ASRs), structural changes, technology/database selection, API design patterns, security architecture, or "one-way door" decisions that are hard to reverse, contentious, or non-obvious.
* **Skip an ADR**: For minor implementation details, bug fixes, routine patch updates, formatting rules, or temporary workarounds.

### Lifecycle & Governance Rules
* **Lifecycle States**: `Initiating` $\rightarrow$ `Researching` $\rightarrow$ `Evaluating` $\rightarrow$ `Implementing` $\rightarrow$ `Maintaining` $\rightarrow$ `Sunsetting` (or state tracking: `Proposed` $\rightarrow$ `Accepted` $\rightarrow$ `Deprecated` / `Superseded`).
* **Immutability Rule**: Accepted ADRs are **immutable**. Rather than editing an accepted record when architecture evolves, create a new ADR that explicitly **supersedes** the prior record.
* **One Decision Per Record**: Do not bundle multiple architectural choices into one file.

### Standard Templates

#### Classic Nygard Template (5 Core Sections)
* **Title**: Short noun phrase or present-tense imperative verb phrase with sequential ID (e.g., `ADR-0007: Use PostgreSQL for Multi-Tenant Storage`).
* **Status**: Current state (`Proposed`, `Accepted`, `Superseded`, etc.).
* **Context**: Architectural drivers, organizational constraints, and business priorities motivating the decision.
* **Decision**: Clear statement of the architecture change agreed upon.
* **Consequences**: Explicit trade-offs, negative impacts, and follow-up needs.

#### MADR Template (Markdown Architectural Decision Records)
Expands Nygard by adding explicit sections for **Decision Drivers**, **Considered Options** (with rationale for rejected alternatives), and **Pros/Cons Comparison Matrices**.

#### Agent-Optimized ADR Schema (For Coding Agents)
* **Frontmatter Scope**: Uses an `applies_to` file-glob array so AI tools load records only when editing relevant files.
* **Normative Directives**: Replaces conversational prose with RFC 2119 keywords (`MUST`, `MUST NOT`, `SHOULD`).
* **Verifiable Checks**: Includes a `verify:` linter or script command for automated CI/agent compliance validation.
* **Token Budget**: Enforces a strict line budget (<200 lines) to maximize LLM context window efficiency.

---

## 4. The C4 Model for Visual Architecture

Created by Simon Brown, the **C4 Model** provides a hierarchical approach to diagramming software architecture across four levels of abstraction.

```
 THE C4 MODEL HIERARCHY
 ┌────────────────────────────────────────────────────────┐
 │ LEVEL 1: SYSTEM CONTEXT │
 │ [System Boundaries, Users, External Dependencies] │
 └───────────────────────────┬────────────────────────────┘
 │ (Zoom in)
 ▼
 ┌────────────────────────────────────────────────────────┐
 │ LEVEL 2: CONTAINERS │
 │ [Deployable Units: Web Apps, Databases, Microservices] │
 └───────────────────────────┬────────────────────────────┘
 │ (Zoom in)
 ▼
 ┌────────────────────────────────────────────────────────┐
 │ LEVEL 3: COMPONENTS │
 │ [Internal Modules, Controllers, Services] │
 └───────────────────────────┬────────────────────────────┘
 │ (Zoom in)
 ▼
 ┌────────────────────────────────────────────────────────┐
 │ LEVEL 4: CODE │
 │ [Class Diagrams, Interfaces, Code Structures] │
 └───────────────────────────┴────────────────────────────┘
```

### The Four Abstraction Levels

| Level | Diagram Name | Primary Audience | Core Elements Shown | Best Practices |
|:--- |:--- |:--- |:--- |:--- |
| **Level 1** | **System Context** | Non-technical & technical stakeholders, product managers. | High-level system boundaries, user personas/roles, external system dependencies. | Keep technology-agnostic; hide internal code details. |
| **Level 2** | **Container** | Architects, developers, operations engineers. | Deployable units (applications, microservices, databases, mobile apps, message queues) & protocols. | Specify technology choices (e.g., Node.js, PostgreSQL, gRPC). |
| **Level 3** | **Component** | Developers & component architects. | Internal modules, controllers, repositories, and interfaces inside one container. | Focus on logical code boundaries rather than external frameworks. |
| **Level 4** | **Code** | Software engineers. | Class diagrams, interfaces, functions, and code structures. | **Optional**: Auto-generate from IDE/code to prevent maintenance toil. |

### Core Notation & Rules
* **Core Elements**: *Person* (human actor), *Software System* (highest boundary), *Container* (deployable unit), and *Component* (modular unit).
* **Explicit Relationship Labeling**: Arrows MUST be directional and explicitly state **purpose**, **protocol**, and optional **data format** (e.g., `"Submits payment via HTTPS/JSON"`) rather than ambiguous terms like `"uses"`.
* **Progressive Disclosure**: Limit canvas complexity to 5–9 elements per view; never mix abstraction levels on a single diagram canvas.

---

## 5. Runbooks & Operational Playbooks

Runbooks are prescriptive, step-by-step operational guides used by on-call engineers to diagnose failures, execute remediations, and minimize Mean Time to Resolution (MTTR).

* **Runbook vs. Playbook**: A **runbook** provides granular instructions for a specific technical failure mode. A **playbook** defines broader role responsibilities, escalation rules, and communication workflows across incident categories.

### Standard Runbook Template Sections
1. **Metadata**: Service name, severity level (P1/P2), owner team handle (DRI), and primary observability dashboard links.
2. **Trigger & Symptoms**: Firing PagerDuty/Slack alert names, metric anomalies, and observable user impact.
3. **Diagnostic Steps**: Exact CLI commands, database checks, and log queries to verify the root cause.
4. **Remediation & Mitigation**: Ordered execution steps for immediate recovery (e.g., scaling pool replicas, initiating feature flags, rolling back deployments).
5. **Escalation & Communication**: Next-tier escalation timeouts and status page update commands.

### Operational Governance
* **The "Fix-PR" Rule**: During on-call onboarding or incident retrospectives, any runbook step found to be unclear or incorrect MUST be updated via a documentation PR before closing the task.

---

## 6. Developer Onboarding Documentation

Developer onboarding provides a structured trajectory to transition new hires from setup to operational autonomy.

### Core Onboarding Artifacts & Patterns
* **`START_HERE.md`**: A root repository file designed to be read in <5 minutes by human developers and entering AI agents. Contains: (1) System overview, (2) Team roster & Slack channels, (3) Current sprint state, (4) Pointers to Tier 1 ADRs and C4 diagrams, and (5) Local setup/sandbox links.
* **The Onboarding "Fix-PR"**: During Week 1, new hires execute setup guides, document friction or stale commands, and submit a documentation pull request by Day 3–5 to establish an immediate contribution habit.
* **Internal Developer Portals (IDPs)**: Centralized catalogs (e.g., Backstage, Port) aggregating service ownership metadata, API schemas, scorecards, and self-service "golden paths".

### 90-Day Onboarding Trajectory
* **Week 1 (Setup & Orientation)**: Account provisioning, environment setup, and submitting the onboarding "Fix-PR".
* **Days 6–30 (Observation & Shadowing)**: Attending post-mortems, performing on-call shadow shifts, and conducting codebase walkthroughs.
* **Days 30–60 (Technical Autonomy)**: Owning a service domain, leading sprint tasks end-to-end, and participating in architecture reviews.
* **Days 60–90 (Operational Independence)**: Conducting **reverse shadow shifts** (driving incident response while a senior SRE observes), joining the primary on-call rotation, and updating service runbooks.

---

← [Prev: Information Architecture](chapter02-information-architecture.md) | [Index](README.md) | [Next: Tooling Landscape](chapter04-tooling-landscape.md) →

## Related chapters
- [chapter02-information-architecture](chapter02-information-architecture.md) — page templates and quadrant diagram this builds on
- [chapter05-maintenance-governance](chapter05-maintenance-governance.md) — governance rhythm that keeps these frameworks alive
- [chapter09-case-studies](chapter09-case-studies.md) — AWS, Microsoft, Red Hat, and UK Government ADR adoption in practice
- [chapter12-implementation-roadmap](chapter12-implementation-roadmap.md) — where ADRs, C4 diagrams, and runbooks fit in a rollout
