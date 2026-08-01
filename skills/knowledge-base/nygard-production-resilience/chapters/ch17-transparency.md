# Chapter 17 — Transparency

## Core Idea

Transparency means making the system’s important state, behavior, and trends visible to the people and automation responsible for operating it. It has multiple time perspectives: historical trends, future prediction, present status, and instantaneous behavior. A single dashboard or log stream cannot answer all four.

## Frameworks Introduced

- **Historical perspective:** understand baseline, seasonality, growth, and regressions.
- **Predictive perspective:** use trends and capacity models to anticipate limits.
- **Present perspective:** know whether useful service is available now.
- **Instantaneous perspective:** explain what a failing request, thread, or dependency is doing at this moment.
- **Observability as an operating process:** telemetry must connect to ownership, thresholds, runbooks, and action.

## Key Concepts

### Designing for transparency

For each critical flow, identify the questions an operator must answer:

- Are users succeeding?
- Which operation is failing or slow?
- Where is work waiting?
- Which dependency is contributing?
- Is the system recovering after an intervention?
- What changed before the symptom?

Instrumentation should answer these questions with stable names, meaningful dimensions, and controlled cardinality. A metric that cannot be interpreted or acted upon is noise.

### Logging

Logs provide event detail and context. Use structured records with timestamp, severity, component, operation, correlation/request identifier, outcome, duration, and safe relevant fields. Log boundaries and state transitions, not every internal loop. Protect privacy and secrets, and make volume bounded during failure; an error storm should not consume the disk needed for recovery.

### Monitoring systems

Monitor user-visible service-level indicators alongside resource and dependency signals. Alert on symptoms that require action, with thresholds tied to duration, rate, and affected scope. A constantly red dashboard trains operators to ignore it; a constantly green dashboard that omits tail latency is equally dangerous.

Health checks should have distinct purposes: liveness, readiness, dependency status, and deep diagnostics. Do not make a liveness probe perform an expensive business transaction or make every health check call every dependency.

### Standards and enabling technologies

Consistent naming, correlation IDs, time synchronization, trace context, metric units, and status semantics make data joinable across services. The specific tools may change; the operational contract should remain. Establish retention, access, sampling, redaction, and cost policies as part of the design.

### Operations database and supporting processes

An operations database or equivalent shared record can preserve configuration ownership, service dependencies, deployment history, incidents, maintenance, and known exceptions. It is useful only when kept current and connected to processes: review, escalation, change management, post-mortem, and capacity planning. Tools do not replace responsibility.

## Reference Table

| Perspective | Best question | Typical evidence |
|---|---|---|
| Historical | What changed over time? | Trends, baselines, incident history |
| Predictive | When will a limit be reached? | Growth and capacity forecasts |
| Present | Is useful service available now? | SLI, error, latency, saturation |
| Instantaneous | What is this request/thread doing? | Logs, traces, dumps, dependency detail |

## Worked Example

A service dashboard shows CPU at 40% and green health checks while users report timeouts. The present-service view is incomplete. Adding pool wait, queue depth, p95/p99 latency, dependency timings, and request correlation reveals that all workers are blocked on a third-party API. A circuit-breaker state and rejected-work count then show whether the mitigation is working.

## Key Takeaways

1. Transparency is about actionable questions, not maximum telemetry.
2. Combine service-level, resource-level, dependency, and event data.
3. Support historical, predictive, present, and instantaneous views.
4. Pair telemetry with ownership, runbooks, thresholds, and safe incident processes.

## Connects To

- Chapter 16 uses these perspectives during an incident.
- Chapter 14 exposes lifecycle and administrative state.
- Chapter 18 uses operational feedback to guide adaptation and release safety.

