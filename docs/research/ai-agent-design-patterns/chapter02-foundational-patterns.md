# Foundational Patterns

Three patterns turn a single LLM call into something that can actually accomplish a multi-step, grounded task: **Planner**, **Tool Calling**, and **Retrieval-Augmented Generation (RAG)**. Almost every production agent needs at least the second of these; the first and third depend on whether the task is genuinely multi-step and genuinely needs external/private knowledge, respectively.

## 1. Planner Pattern

**Definition.** Instead of attempting a complex objective in one pass, the agent first decomposes it into a structured sequence of smaller, more tractable steps, then executes (or delegates) each step in order, combining the results into a final answer.

**When to use it.** Complex, multi-step requests where the end goal implies an ordered set of sub-tasks — e.g. "build an employee onboarding portal" implying create-database → build-API → generate-UI → write-tests → deploy. Skip it for single-step lookups or simple transformations, where planning overhead adds latency without adding correctness.

**Production tradeoffs and failure modes.** The single most important predictor of whether the overall task succeeds is the *quality* of the decomposition: research into multi-agent failures repeatedly identifies "poor task decomposition" — steps that are too coarse-grained, not independently verifiable, or based on an incorrect understanding of the goal — as a root cause of downstream failure (see [Chapter 10](chapter10-anti-patterns-failure-modes.md)). A plan is only useful if each step can be independently checked for success or failure; a plan of vague, unverifiable steps just moves the ambiguity one level down instead of resolving it.

**Frameworks.** Semantic Kernel Planners (`FunctionCallingStepwisePlanner`), Microsoft AutoGen, Azure AI Agent Service. LangGraph and CrewAI implement planning implicitly through graph/flow definitions rather than a dedicated "planner" object (see [Chapter 8](chapter08-framework-landscape.md)).

```
User Request → Break into Steps → Execute Step 1 → Execute Step 2 → … → Combine Results
```

## 2. Tool Calling Pattern

**Definition.** The LLM is treated strictly as a *reasoning engine*, never an *execution engine*. It identifies when a specific action is required (a calculation, a database query, an API call) and emits a structured, schema-validated request; a separate, deterministic layer executes that request and returns the result to the model.

**When to use it.** Essentially always, the moment an agent needs to do anything beyond generating text — fetch live data, mutate state, or perform precise computation the model itself is unreliable at (arithmetic, exact string operations, current facts).

**Production tradeoffs and failure modes.** This pattern is high-reliability *because* it removes execution from the model's own unreliable generation — but it pushes the reliability burden onto tool schema design. Poorly described tool schemas (ambiguous names, missing parameter constraints, overlapping tool purposes) lead the model to select the wrong tool or hallucinate parameters. This compounds badly at scale: empirical benchmarks cited in the research show tool-selection accuracy dropping sharply once an agent has more than roughly 10–15 tools available simultaneously (see the "God Agent" anti-pattern in [Chapter 10](chapter10-anti-patterns-failure-modes.md)) — which is the core argument for scoping each agent to a small, coherent toolset rather than attaching every capability to one agent.

**Frameworks.** Semantic Kernel plugins (`[KernelFunction]`), the Model Context Protocol (MCP) as a cross-framework standard for exposing and discovering tools, OpenAI Agents SDK function tools, LangGraph/LangChain tools, Google ADK tool callbacks, AWS Bedrock action groups.

```csharp
public class CustomerPlugin
{
    [KernelFunction]
    public async Task<Customer> GetCustomerAsync(int id) => await repository.GetByIdAsync(id);
}
kernel.Plugins.AddFromObject(new CustomerPlugin());
```

## 3. Retrieval-Augmented Generation (RAG)

**Definition.** Rather than relying solely on the model's training data, the agent retrieves relevant documents or records from an external knowledge source (typically a vector store, sometimes a hybrid lexical/semantic index) and injects them into the prompt as grounding context before generation.

**When to use it.** The agent must answer from current, private, or frequently changing information — internal documentation, product catalogs, customer records — where training-data knowledge is absent, stale, or a hallucination risk.

**Benefits and tradeoffs.** RAG reduces hallucination by grounding responses in retrieved fact, but it introduces its own failure surface: retrieval quality bounds answer quality. Flat vector search optimizes for *semantic similarity*, not logical or relational structure, which under production load produces two specific failure patterns — "chunk-shredding" (losing document boundaries and headings so retrieved fragments lose context) and multi-hop queries where the needed fact is split across non-adjacent chunks that never get retrieved together. See [Chapter 3](chapter03-memory-pattern.md) for the deeper treatment of retrieval drift, since in practice RAG and long-term memory share the same underlying vector-store mechanics and the same failure modes.

**Frameworks.** Google Gemini Enterprise / Vertex AI Search, AWS Bedrock Knowledge Bases, Azure AI Search, pgvector/Qdrant as backing stores accessed through any framework's retriever abstraction (LangChain/LangGraph retrievers, Semantic Kernel memory connectors).

```csharp
var documents = await vectorStore.SearchAsync("Refund policy", top: 3);
var prompt = $"Answer using only this context:\n\n{documents}";
var response = await kernel.InvokePromptAsync(prompt);
```

## Composing the Three

In practice these three patterns compose rather than compete: a Planner may generate a step that requires a Tool Call; a Tool Call may itself be a RAG lookup against a vector store; and the result of either feeds back into the next planning step. This composition — reasoning, retrieval, and action interleaved rather than run once in sequence — is what several frameworks call "agentic RAG," and it is the seed of the full Orchestrator pattern covered in [Chapter 9](chapter09-composing-architectures.md).
