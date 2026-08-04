# Reactive & Workflow Patterns

These two patterns govern *when* and *how constrained* an agent's execution is — reacting to external events versus following a predefined, auditable sequence. Both trade some agent autonomy for predictability and system decoupling.

## 1. Event-Driven Agent Pattern

**Definition.** Agents behave as reactive microservices, triggered by events on a message bus rather than being invoked synchronously by a caller waiting on the response.

```
New Ticket Created → Event Bus → Support Agent → Classify → Assign Priority
```

**When to use it.** Any scenario where work arrives asynchronously and doesn't need to block a caller — support ticket triage, order processing, log analysis — and, critically, any multi-agent system where agents would otherwise call each other synchronously in a chain.

**Why it matters for multi-agent reliability, not just architecture style.** A synchronous chain (Agent A calls Agent B calls Agent C calls a Tool) accumulates latency additively and creates a single point of failure at every hop — if any link times out, the whole chain fails. An event-driven backbone decouples agents temporally: they subscribe to a topic, reason, and publish facts, never invoking each other directly. If one specialist agent goes down or hits a rate limit, the event bus buffers messages and the rest of the fleet keeps operating — containing the failure instead of propagating it. This is one of the concrete mitigations for cascading-failure and coordination-overhead problems documented in [Chapter 10](chapter10-anti-patterns-failure-modes.md).

**Tooling.** Azure Service Bus, Apache Kafka, RabbitMQ, AWS SQS.

```csharp
public async Task Handle(OrderCreated @event)
{
    await agent.RunAsync($"Analyze order {@event.Id}");
}
```

## 2. Workflow Pattern

**Definition.** The agent follows a predefined, auditable sequence of steps rather than freely deciding its own path at each turn.

```
Receive Resume → Extract Skills → Match Jobs → Score Candidate → Generate Report
```

**When to use it.** Tasks where predictability and auditability outrank flexibility — compliance-sensitive processing, support ticket classification, legal term extraction, financial auditing — anywhere a regulator, auditor, or downstream system needs to be able to say exactly what steps a given case went through and why.

```csharp
await workflow
    .StartWith(ExtractResume)
    .Then(MatchJobs)
    .Then(RankCandidates)
    .Then(GenerateReport)
    .Execute();
```

**Tradeoff against the Planner pattern ([Chapter 2](chapter02-foundational-patterns.md)).** Where the Planner pattern lets the model *decide* the decomposition dynamically per request, the Workflow pattern *fixes* the decomposition in advance. Use Workflow when the process itself is stable and known (the same regulatory process applies to every case); use Planner when the decomposition genuinely varies by request and can't be enumerated in advance. Many production systems combine both: a fixed Workflow skeleton with a Planner-driven sub-step for the one stage that requires dynamic reasoning.

## 3. Composing Event-Driven and Workflow

The two patterns are not mutually exclusive: a workflow's individual steps can each be triggered by an event rather than called synchronously, giving you both the auditability of a fixed sequence and the resilience of asynchronous, decoupled execution. This combination — an explicit, checkpointed state machine whose transitions are driven by events rather than direct calls — is the backbone several production frameworks converge on for durable, resumable agent execution (see [Chapter 8](chapter08-framework-landscape.md), particularly LangGraph's persistent-checkpointer model).
