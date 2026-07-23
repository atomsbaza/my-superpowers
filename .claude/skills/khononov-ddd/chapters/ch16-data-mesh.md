# Chapter 16: Data Mesh

## Core Idea
Analytical (OLAP) data deserves the same domain-driven treatment as operational (OLTP) data: instead of forcing all enterprise data into one monolithic warehouse or lake, data mesh decomposes analytical models along bounded-context boundaries and treats each context's analytical output as an owned, discoverable, versioned product.

## Frameworks Introduced
- **Data Mesh** (4 principles: Decompose Data Around Domains, Data as a Product, Enable Autonomy, Build an Ecosystem):
  - **Decompose Data Around Domains**: "Instead of building a monolithic analytical model, the data mesh architecture calls for... multiple analytical models and align them with the origin of the data," aligning analytical model ownership with bounded context boundaries.
    - When to use: whenever a single enterprise-wide analytical model becomes impractical to design and maintain (same rationale as avoiding a single enterprise-wide operational model).
    - How: each bounded context owns both its operational (OLTP) model and the corresponding analytical (OLAP) model derived from it; the product team responsible for the domain becomes responsible for its analytics too.
  - **Data as a Product**: analytical data must be treated as "a first-class citizen," exposed through well-defined output ports rather than scraped from internal databases or logs.
    - When to use: whenever analytical consumers currently pull from an operational system's internal schema or undocumented dumps.
    - How: expose data endpoints that are discoverable, have a well-defined versioned schema, carry monitored SLAs, and are polyglot (SQL, object storage, streaming, etc.) to fit different consumers; bounded-context teams add data-specialist roles to own this responsibility.
  - **Enable Autonomy**: product teams both produce their own data products and consume others' without reinventing infrastructure each time.
    - When to use: once multiple teams need to build/serve data products — duplicated bespoke tooling per team is wasteful.
    - How: a dedicated data infrastructure platform team builds a shared platform providing data product blueprints, unified access patterns, access control, and polyglot storage.
  - **Build an Ecosystem**: interoperability across data products needs federated governance.
    - When to use: once several bounded contexts are producing data products that need to interoperate.
    - How: a federated governance group — data/product owners from bounded contexts plus the platform team — defines and enforces rules ensuring the distributed ecosystem stays healthy and interoperable.

## Key Concepts
- **OLTP (operational) model**: a model built around business entities and their lifecycles, optimized for real-time transactions.
- **OLAP (analytical) model**: a model built around business activities (not entities), optimized for insight-generation and flexible querying rather than transactions.
- **Fact Table**: an append-only table recording business activities/events that already happened (e.g., `Fact_Sales`); analogous to domain events but without a past-tense verb naming convention, and never updated or deleted — state changes are captured by appending new records.
- **Dimension Table**: a normalized table describing the attributes ("adjectives") of a fact, referenced from fact tables via foreign keys, enabling flexible ad hoc querying and grouping.
- **Star Schema**: an analytical model with facts directly linked to single-level, denormalized dimension tables (many-to-one from fact to dimension).
- **Snowflake Schema**: a star schema variant where dimensions are further normalized into multiple levels — saves storage and eases dimension maintenance, at the cost of needing more joins to query.
- **Data Warehouse (DWH)**: an architecture that extracts data from operational systems, transforms it into an analytical (facts/dimensions) model via ETL, and loads it into a query-optimized database.
- **Data Mart**: a smaller database holding data scoped to one well-defined analytical need (e.g., one department), populated either directly via ETL from operational systems or downstream from the warehouse.
- **Data Lake**: an architecture that ingests operational data in its raw, untransformed form, deferring model generation until data engineers build task-specific ETL pipelines later.
- **Data Swamp**: the degraded state a schema-less data lake devolves into at scale, once uncontrolled, low-quality raw data makes the lake too chaotic to use effectively.
- **Data Mesh**: a domain-driven analytical architecture that decomposes analytical ownership along bounded-context boundaries and serves analytical data as a governed, autonomous product.

## Mental Models
- **Data mesh is DDD applied to analytical data**: the same reasoning that justifies bounded contexts for operational models (Chapter 3) — reject one universal enterprise model in favor of many purpose-fit, owned models — applies directly to analytics.
- **Facts are verbs, dimensions are adjectives**: a fact table captures "what happened" (a business activity), while a dimension table describes attributes of that activity; this framing clarifies star/snowflake schema design.
- **Coupling to internal schema is the root failure of DWH/lake architectures**: because ETL jobs typically read operational databases directly (not through public interfaces), a change to an internal operational schema silently breaks analytics — the same "leaky implementation coupling" problem DDD's bounded-context integration patterns exist to prevent.
- **Analytical output ports are just another published language / open-host service**: exposing a bounded context's data in an analytics-friendly model distinct from its operational model is literally the open-host service pattern from Chapter 4, and CQRS is the natural mechanism to generate/serve multiple analytical model versions from one operational model.

## Anti-patterns
- **Enterprise-wide analytical model (classic DWH/data lake)**: attempting one model to serve all analytical use cases across the whole organization is as impractical as one enterprise-wide operational model (Chapter 3) — it can't fit every consumer's needs and blurs ownership boundaries.
- **ETL scripts reading operational databases directly**: DWH/lake pipelines commonly fetch data straight from operational systems' internal schemas rather than through public interfaces, so schema changes needed for legitimate domain-model evolution silently break analytics, causing friction and stalled improvements — especially damaging in DDD projects where the operational model is expected to evolve continuously.
- **Centralized, domain-ignorant data teams**: data engineers/analysts sit in a separate organizational unit specializing in big-data tooling rather than the business domain, so they lack the domain knowledge needed to model analytical data well — creating a bottleneck and quality gap.
- **Data lake becoming a "data swamp"**: because data lakes impose no schema and no quality control on ingestion, at scale the raw data becomes too chaotic to make sense of, and data scientists spend disproportionate effort on cleanup rather than insight.
- **Multiple ETL script versions per operational model version**: data lakes' deferred transformation forces engineers to maintain parallel ETL scripts for different versions of the same evolving operational model, multiplying maintenance burden.

## Code Examples
(omit — not code-heavy)

## Reference Tables
| Architecture | Ownership Model | Key Challenge |
|---|---|---|
| Data Warehouse | Central data team owns one enterprise-wide transformed model, fed by ETL from operational systems | Impractical to model all use cases in one schema; ETL tightly coupled to operational systems' internal (non-public) schemas, breaking on change |
| Data Lake | Central data team owns raw ingested data; transformation deferred to data/BI engineers per use case | Schema-less raw data becomes a "data swamp" at scale; must maintain multiple ETL versions across operational model changes |
| Data Mesh | Each bounded context's product team owns both its operational and analytical models, served as products | Requires building shared data-infrastructure platform and federated governance to keep autonomous data products interoperable |

## Worked Example
A support-desk domain illustrates OLAP modeling: `Fact_CaseStatus` records the state of support cases as append-only snapshots (e.g., taken every 30 minutes rather than on every change, since analysts choose the granularity that balances usefulness against cost), while `Fact_CustomerOnboardings` and `Fact_Sales` record onboarding and sale events. Each fact is surrounded by dimension tables (e.g., customer, product, agent) describing its attributes, forming a star schema; further normalizing those dimensions into sub-dimensions produces a snowflake schema. Under the classic DWH/lake approach, all these facts would be centralized into one enterprise model, pulled via ETL directly from the operational databases of possibly several bounded contexts (support, sales, onboarding), coupling analytics to internal implementation details. Under data mesh, each bounded context instead owns and publishes its own analytical model as a data product: the support-desk context exposes `Fact_CaseStatus` and its dimensions through a well-defined, versioned, SLA-backed output port (e.g., queryable via SQL for one consumer and object storage for another). A cross-domain BI report that needs both support and sales data fetches each bounded context's data product independently and joins/transforms locally — analogous to how operational bounded contexts integrate via partnership, open-host service, or anticorruption layer, rather than sharing a single coupled database.

## Key Takeaways
1. OLTP and OLAP models serve fundamentally different purposes — entity lifecycles versus business-activity insight — and should be modeled differently (fact/dimension tables, not entity schemas).
2. Both data warehouse and data lake architectures fail at scale because they chase one all-encompassing model and couple ETL to operational systems' internal schemas rather than public interfaces.
3. Data mesh decomposes analytical ownership along the same bounded-context boundaries used for operational models, making each domain team responsible for both its OLTP and OLAP models.
4. Treat analytical data as a product: discoverable, well-defined schema, SLA-backed, versioned, and polyglot to serve varied consumers.
5. Enabling team autonomy in data mesh requires a dedicated data-infrastructure platform team, not ad hoc per-team tooling.
6. A federated governance body is required to keep decomposed, autonomous data products interoperable across the ecosystem.
7. Existing DDD patterns transfer directly: open-host service/published language for exposing analytical models, CQRS for generating multiple analytical model versions, and bounded-context integration patterns (partnership, ACL, separate ways) for combining analytical models across domains.

## Connects To
- **Ch 1**: subdomains provide the natural boundaries data mesh aligns analytical ownership around.
- **Ch 3**: the critique of enterprise-wide operational models directly parallels this chapter's critique of enterprise-wide analytical models (DWH/lake).
- **Ch 4**: open-host service and published language patterns explain how bounded contexts expose their analytical models as data products.
- **Ch 9**: CQRS is the mechanism used to generate and simultaneously serve multiple analytical model versions from one operational model.
- **Ch 14**: Microservices — data mesh is the analytics-domain analog of decomposing a system into autonomous, independently owned services.
- **Zhamak Dehghani's Data Mesh**: the source paradigm this chapter adapts, combining domain decomposition, product thinking, self-serve platforms, and federated governance for analytical data.
