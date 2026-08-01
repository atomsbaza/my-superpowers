# Chapter 2: Data Models and Query Languages

## Core Idea

Choose a data model by the shape of the data and the queries that must be easy, not by fashion. Document, relational, and graph models can represent much of the same information, but they make different relationships, locality assumptions, and query paths natural.

## Frameworks Introduced

- **Document model and aggregate locality**: Put data that is normally read and written together into a self-contained document.
  - When to use: records have a mostly tree-shaped structure, relationships across records are limited, and the aggregate is a natural transaction boundary.
  - How: identify the unit of access; embed bounded, owned data; use references for independently managed or high-cardinality entities; avoid unbounded documents.
- **Normalization versus denormalization**: Normalization stores each fact once and uses joins; denormalization duplicates data to make a read path local.
  - When to use: decide whether simpler writes and integrity or simpler reads and locality dominate.
  - How: map the actual access paths, update fan-out, and consistency cost; duplicate only when the update path is explicit and affordable.
- **Relational model for many-to-many data**: Tables and joins separate entities from relationships and support flexible ad hoc queries.
  - When to use: relationships are rich, cross-aggregate queries matter, or integrity constraints are important.
  - How: model entities and relations separately, use keys/foreign keys, and let declarative queries describe the result rather than traversal steps.
- **Graph model for variable traversals**: Vertices represent entities and edges represent relationships; the useful operation is following paths of unknown or changing length.
  - When to use: anything may relate to anything, relationship types evolve, and multi-hop traversal is central.
  - How: index incoming and outgoing edges, label relationship types, and express reusable traversal patterns in Cypher, SPARQL, or Datalog.
- **Declarative query as optimization boundary**: State the result, not the algorithm. The database can choose indexes, join order, and execution strategy.
  - When to use: query plans may evolve or the same data must support several access paths.
  - How: express predicates and relationships declaratively; inspect plans and indexes rather than hand-coding one traversal prematurely.

## Key Concepts

- **Aggregate**: A unit of data treated as one document or transaction boundary.
- **Normalization**: Representing each fact once and connecting facts through references/joins.
- **Denormalization**: Deliberately duplicating data for read locality or performance.
- **Schema-on-write**: The database validates structure before storing data.
- **Schema-on-read**: The application interprets structure when data is read.
- **Declarative query**: A description of the desired result rather than control flow.
- **Property graph**: Vertices and labeled, directed edges with properties.
- **Triple store**: Facts represented as subject–predicate–object triples.
- **Datalog**: A rule-based query model that derives predicates recursively from facts.
- **Data locality**: Keeping data needed by a common query physically/logically close.

## Mental Models

- Think of a document as an aggregate, not as a replacement for every relational table.
- Use embedding when the child has the same lifecycle and bounded cardinality as its parent; use references when it does not.
- Use a graph when the question is “what is connected through this path?” rather than “which rows match these columns?”
- Treat an implicit schema as a schema still: it is enforced by application code, tests, and migration logic instead of the database.

## Anti-patterns

- **Mapping an object tree blindly to tables**: It creates awkward joins or duplicated facts without respecting real access paths.
- **Choosing document storage to avoid all joins**: References and application-side joins can be more complex and less consistent than a relational join.
- **Using unbounded arrays inside documents**: A single hot aggregate becomes large, slow to update, and difficult to partition.
- **Using graph storage for simple keyed lookups**: A flexible model does not compensate for ignoring the dominant access pattern.

## Code Examples

```cypher
MATCH (person:Person)-[:BORN_IN]->()-[:WITHIN*0..]->(country:Location),
      (person)-[:LIVES_IN]->()-[:WITHIN*0..]->(continent:Location)
WHERE country.name = 'United States' AND continent.name = 'Europe'
RETURN person.name;
```

- **What it demonstrates**: Variable-length traversal is compact in a graph query; expressing the same path in a relational recursive query is possible but more verbose.

## Reference Tables

| Model | Natural shape | Strength | Main cost |
|---|---|---|---|
| Relational | entities + arbitrary relations | joins, constraints, ad hoc queries | impedance mismatch/locality work |
| Document | self-contained aggregates | locality, flexible structure | cross-document joins and duplication |
| Graph | arbitrary connections | multi-hop traversal and changing relationships | simple keyed workloads may be over-modeled |

## Worked Example

Model a résumé-like profile with a person, contact details, education, and employment. If the profile is always fetched as one bounded page and schools/jobs are not shared entities, one document is a good aggregate. If the application asks “which people worked at companies acquired by X?” or shares company and school records across many profiles, references plus relational joins or a graph become more natural. If the product must support both profile reads and network traversal, keep a system of record in one model and derive a specialized graph/search view rather than forcing one model to make every query easy.

## Key Takeaways

1. Model around access patterns and lifecycle boundaries.
2. Embed bounded, owned data; reference independently evolving or high-cardinality data.
3. Normalize when integrity and flexible queries dominate; denormalize when locality is worth the update cost.
4. Use declarative queries to preserve an optimization boundary.
5. Graph databases are about relationship traversal, not merely storing JSON without a schema.

## Connects To

- **Chapter 3**: The model determines which storage and index structures fit the workload.
- **Chapter 4**: Every model still needs an explicit evolution strategy.
- **Chapter 10–12**: Derived views let specialized models coexist without forcing one database to do everything.

