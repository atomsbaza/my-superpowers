# Chapter 7: Measuring Engineering Productivity

## Core Idea

Measure engineering productivity only when the result will inform an actual decision. Start from goals, derive signals, choose measurable proxies, and preserve traceability; use the QUANTS dimensions to prevent optimizing velocity while silently damaging quality, attention, cognition, or satisfaction.

## Frameworks Introduced

- **Goals/Signals/Metrics (GSM)**:
  - **Goal**: The desired outcome, stated without a measurement method.
  - **Signal**: Evidence that would indicate the goal has been achieved.
  - **Metric**: A measurable proxy for the signal.
  - When to use: Designing productivity studies, dashboards, or process evaluations.
  - How: Define the decision, write goals, enumerate signals, select proxies, validate them, act, and track the result.
- **QUANTS**: Quality of code, Attention from engineers, iNtel­lectual complexity, Tempo and velocity, Satisfaction.
  - When to use: Any productivity or developer-experience measurement.
  - How: Check each dimension for goals and trade-offs; do not let an easy metric such as lines changed stand in for the whole system.
- **Actionability triage**: Do not spend measurement effort if positive or negative results would not change behavior.
  - When to use: Before launching a survey, log study, or productivity dashboard.
  - How: Name the expected result, action for each outcome, decision maker, evidence type, and time horizon.

## Key Concepts

- **Streetlight effect**: Measuring what is easy to see rather than what answers the real question.
- **Traceability**: The ability to link each metric back to a signal and goal.
- **Proxy**: An imperfect measurable stand-in for an underlying outcome.
- **Triangulation**: Combining qualitative, survey, and log evidence to reduce blind spots.
- **Vanity metric**: A number collected to support a predetermined story rather than a decision.
- **QUANTS trade-off**: The tendency for improvement in one productivity dimension to harm another.

## Mental Models

- Ask “what decision will this change?” before asking “what can we measure?”
- Treat a metric as evidence, not truth.
- If qualitative and quantitative results disagree, investigate whether the quantitative proxy missed the construct.
- Prefer workflow changes that make the desired behavior automatic or easy.

## Anti-patterns

- **Lines-of-code productivity**: It rewards output volume and can encourage needless code.
- **Metrics creep**: Changing metrics after seeing an inconvenient result.
- **Single-axis optimization**: Improving review speed while degrading quality or learning.
- **Unowned measurement**: Collecting data without an empowered decision maker.

## Worked Example

The chapter evaluates Google’s readability process. The question is not “is readability good?” but whether its cost is worth its benefits. The study maps goals across QUANTS, derives signals such as code quality and learning, and combines surveys with developer-tool logs. The result can support either publicizing the process’s value or removing it for a language where the benefits no longer justify the cost.

## Reference Table

| Layer | Question | Example for readability |
|---|---|---|
| Goal | What outcome matters? | Code quality improves |
| Signal | How would we know? | Engineers report better quality |
| Metric | What can we measure? | Survey proportion, review logs |
| Action | What will change? | Keep, change, or remove the process |

## Key Takeaways

1. Measurement is worthwhile only when it can change a decision.
2. Build metrics from goals, not available logs.
3. Cover QUANTS and make trade-offs explicit.
4. Preserve traceability and triangulate evidence.
5. Embed recommendations in daily workflow and incentives.

## Connects To

- **Chapter 8**: Rules should be adjusted using evidence.
- **Chapter 20**: Developer feedback and false-positive data determine useful analysis.
- **Chapter 23**: CI feedback is an operational measurement loop.

