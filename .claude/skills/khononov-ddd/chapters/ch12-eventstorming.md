# Chapter 12: EventStorming

## Core Idea
EventStorming is a low-tech, collaborative workshop technique for rapidly modeling a business process by covering a wall with sticky notes representing domain events, commands, and other DDD building blocks. Its resultant models are a nice bonus — the real value is the knowledge-sharing and ubiquitous-language alignment that happens among the participants during the session.

## Frameworks Introduced
- **EventStorming**: the collaborative workshop technique invented by Alberto Brandolini for a group of people to brainstorm and rapidly model a business process by exploring it as a series of domain events over a timeline, then progressively enriching the model with commands, policies, read models, external systems, aggregates, and bounded contexts.
  - When to use: to build a ubiquitous language, model a business process, explore new business requirements, recover lost domain knowledge (especially in legacy systems), explore ways to improve an existing process, or onboard new team members. Less useful for simple, sequential processes with no interesting business logic.
  - How: the 10-step process — Unstructured Exploration, Timelines, Pain Points, Pivotal Events, Commands, Policies, Read Models, External Systems, Aggregates, Bounded Contexts.

## Key Concepts
- **Domain event**: something interesting that has happened in the business, formulated in the past tense and written on orange sticky notes.
- **Pain point**: a bottleneck, manual step, or missing knowledge/documentation identified along the timeline, marked with a rotated (diamond) pink sticky note.
- **Pivotal event**: a significant domain event indicating a change in context or phase (e.g., "order shipped"), marked with a vertical divider bar; an indicator of potential bounded context boundaries.
- **Command**: an operation that triggers an event or flow of events, formulated in the imperative (e.g., "Submit order") and written on light blue sticky notes, placed before the events it produces.
- **Actor**: the user persona (customer, administrator, editor) who executes a command, noted on a small yellow sticky note attached to the command when the association is obvious.
- **Policy (automation policy)**: a scenario where a domain event automatically triggers a command, with no human actor involved; represented as a purple sticky note connecting the event to the command, optionally annotated with decision criteria.
- **Read model**: the view of data (screen, report, notification) an actor consults to decide to execute a command; represented on green sticky notes, positioned before the relevant command.
- **External system**: any system outside the domain being explored that can execute commands (input) or be notified of events (output); represented on pink sticky notes.
- **Aggregate**: a cluster that receives commands and produces events, represented as a large yellow sticky note with commands placed on the left and events on the right.
- **Bounded context**: a group of related or policy-coupled aggregates identified as a natural boundary, forming the final output of the workshop.
- **Sticky note color coding**: orange = domain events, light blue = commands, small yellow = actors, purple = policies, green = read models, pink (flat) = external systems, pink diamond (rotated) = pain points, large yellow = aggregates.

## Mental Models
- The workshop itself is the deliverable, not just the wall of sticky notes: knowledge sharing, alignment of mental models, discovery of conflicting understanding, and formulation of ubiquitous language are the primary payoff; the model, aggregates, and bounded-context candidates are "nice bonuses."
- The process is guidance, not hard rules — Brandolini explicitly encourages adapting the recipe rather than following it dogmatically.
- A two-tier facilitation strategy works well in practice: run steps 1–4 ("big picture EventStorming") across the whole business domain first to build a shared foundation and rough bounded-context candidates, then run full 10-step sessions per individual business process.
- EventStorming is learned by doing, not by reading — it's compared to riding a bicycle.

## Anti-patterns
- **Worrying about ordering or redundancy during Step 1**: slows the brainstorm and suppresses idea generation; unstructured exploration should stay chaotic until the rate of new events slows significantly.
- **Skipping the unstructured exploration phase or rushing to structure early**: cuts off the raw knowledge-surfacing that later steps depend on.
- **Too much facilitator control**: EventStorming is a group activity; a facilitator who dominates modeling or lets quiet participants disengage loses the cross-role knowledge-sharing that is the whole point. Watch group energy and actively draw in participants who are shying away.
- **Running remote sessions like in-person ones**: Brandolini himself resisted remote EventStorming because collaboration and participation degrade when the group isn't colocated; treating a large remote session the same as an in-person one reduces effectiveness.
- **Facilitating EventStorming for trivial, sequential processes**: with no real business logic or complexity, the technique offers little over simply writing the steps down.
- **Resuming after a break before everyone is back**: breaks the collaborative modeling mood; the facilitator should walk the group through the current model state when resuming.

## Code Examples
(omit — this is a workshop technique, not code)

## Reference Tables
| Step # | Name | Purpose |
|---|---|---|
| 1 | Unstructured Exploration | Brainstorm domain events (orange notes, past tense) with no concern for order or duplication, until ideas slow down |
| 2 | Timelines | Arrange events chronologically starting with the happy path, then branch in alternative/error flows; fix and dedupe events |
| 3 | Pain Points | Mark bottlenecks, manual steps, or missing knowledge with rotated pink diamond notes for later attention |
| 4 | Pivotal Events | Identify domain events that mark a significant change of context/phase; mark with a vertical divider — hints at bounded context boundaries |
| 5 | Commands | Add imperative-form commands (light blue) before the events they trigger; attach actor (yellow note) where obvious |
| 6 | Policies | Identify automation policies (purple) connecting events to commands with no human actor, optionally with decision criteria |
| 7 | Read Models | Add the data view (green) an actor consults before executing a command, placed before that command |
| 8 | External Systems | Add systems outside the domain (pink) that execute commands or receive event notifications; every command should now trace to an actor, policy, or external system |
| 9 | Aggregates | Group related commands/events into aggregates (large yellow notes), commands on left, events on right |
| 10 | Bounded Contexts | Cluster related or policy-coupled aggregates into candidate bounded context boundaries |

## Worked Example
Consider EventStorming an online order fulfillment process. In Step 1, participants scatter orange notes: "Order submitted," "Payment charged," "Shipment approved," "Order shipped," "Order delivered," "Order returned." In Step 2, these are lined up chronologically along the happy path, with a branch drawn for the return scenario. In Step 3, a pink diamond is placed near "Shipping cost calculated" flagging that nobody in the room understands how comparison pricing works across carriers — a documented pain point. In Step 4, "Order initialized," "Order shipped," and "Order returned" are marked pivotal, hinting at three phases of the process. In Step 5, the command "Submit Order" (light blue) is placed before "Order initialized," tagged with the "Customer" actor (yellow note); "Ship Order" is placed before "Order shipped." In Step 6, since "Ship Order" has no obvious human actor, a purple policy note is added: "when Shipment Approved occurs, trigger Ship Order." In Step 7, a green "Shopping cart" read-model note is placed before "Submit Order," since the customer views the cart before submitting. In Step 8, a pink external-system note for the CRM is added, showing it both triggers "Ship Order" and receives notification of "Shipment Approved" via a policy. In Step 9, "Submit Order," "Order initialized," "Shipping cost calculated," and "Order shipped" are grouped into an "Order" aggregate (large yellow note, commands left, events right); shipment-related commands/events might form a separate "Shipment" aggregate. In Step 10, the "Order" and "Shipment" aggregates, being tightly coupled through the shipping policy, are grouped as candidates within an "Order Fulfillment" bounded context, while a loosely related "Returns" aggregate cluster is flagged as a possible separate bounded context.

## Key Takeaways
1. Run EventStorming as a full 10-step sequence — Unstructured Exploration through Bounded Contexts — but treat the steps as adaptable guidance, not a rigid script.
2. Invite a diverse cross-functional group (engineers, domain experts, PMs, QA, support, design) capped around 10 in-person participants (5 for remote) so everyone can actively contribute.
3. Use a large wall/whiteboard, colored sticky notes per the standard legend, and no chairs — physical setup drives the collaborative energy that produces knowledge sharing.
4. Facilitators should watch group dynamics continuously: reignite flagging energy with questions, draw in quiet participants, and never resume after a break until everyone is back.
5. Prefer starting with a "big picture" pass (steps 1–4) across the whole domain, then run dedicated full sessions per business process once major processes are identified.
6. For remote EventStorming (e.g., via Miro), expect reduced collaboration effectiveness, keep groups smaller, and merge results from multiple parallel sessions rather than forcing one large remote room.
7. Value the process over the artifact: the ubiquitous language and shared mental model built during the session matter more than the final diagram, though the diagram can seed an event-sourced implementation if the domain warrants it.

## Connects To
- **Ch 2 (Discovering Domain Knowledge)**: EventStorming is a concrete facilitation technique for the knowledge-discovery and ubiquitous-language-building goals introduced there.
- **Ch 13 (DDD in the Real World)**: pivotal events, aggregates, and bounded-context candidates surfaced in an EventStorming session feed directly into the real-world adoption and modeling decisions covered next.
- **Ch 4 (Integrating Bounded Contexts)**: aggregates and policy-coupling discovered in Step 9–10 inform how bounded contexts are later integrated.
- **Ch 7 (Modeling the Dimension of Time)**: domain events and pivotal events map onto event-based/event-sourced modeling discussed there.
- **Alberto Brandolini, Event Storming workshops**: the technique's creator and the canonical external reference (also miro.com as a common remote-facilitation tool).
