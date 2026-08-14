# Research: AWS Kiro Crew for Engineering Teams

> **Audience:** Engineer already using AWS Kiro at work
> **Goal:** Understand Kiro Crew and identify safe ways to apply it to team workflows
> **Scope:** Architecture, execution model, team adoption, security, operations, and multi-agent scaling
> **Date:** 2026-08-14

---

## Research Method

This report combines:

- **NotebookLM:** A deep research notebook named `AWS Kiro Crew - Technical Application Research` with 64 imported sources, including Kiro documentation, the Kiro Crew repository, AWS Architecture material, and independent coverage.
- **MediumLM:** Authenticated Medium research using web-search discovery because Medium's native search-results API was blocked. Full-access articles were used; preview-only content was excluded.
- **Live verification:** Current Kiro Crew documentation and the public repository were checked directly before writing this report.

NotebookLM also returned unrelated CrewAI material because the word "Crew" appears in the query. Those sources are not treated as evidence about Kiro Crew.

## Executive Summary

Kiro Crew is not CrewAI and is not primarily a hosted AWS control plane. It is an open-source, persistent development workspace that runs on a Mac, Linux host, container, or remote machine controlled by the user.

The useful mental model is:

```text
User surfaces -> Kiro Crew Gateway -> managed sessions -> Kiro CLI over ACP -> tools and MCP servers
```

Kiro IDE remains the interactive spec-driven editor. Kiro CLI is the terminal execution harness. Kiro Crew adds persistence, background execution, memory, schedules, approvals, messaging surfaces, subagents, Task Runner, and installable Apps around the CLI.

The safest adoption path is a read-only engineering assistant first, followed by bounded repository changes through Task Runner. Production deployment, destructive infrastructure operations, and unattended write access should remain outside the first pilot.

## Correct Product Boundaries

| Component | Role |
|---|---|
| Kiro IDE | Interactive editor for specs, code, tests, steering, hooks, and MCP-backed development |
| Kiro CLI | Terminal execution harness used by Crew through the Agent Client Protocol (ACP) |
| Kiro Crew | Persistent Gateway, session manager, memory, schedules, approvals, subagents, Apps, and messaging surfaces |
| Crew Apps | Packages that combine agents, skills, MCP servers, cron jobs, UI pages, and backend processes |
| `kiro-flock` | Separate AWS reference implementation for distributed shared-state agent clusters |

Kiro Crew reads existing `.kiro` configuration at launch, so steering files, skills, and custom agents can carry over from an existing Kiro workflow. Company policy should still verify that Kiro CLI authentication and entitlements are approved for the intended environment; IDE access should not be assumed to imply identical CLI or unattended-operation permissions.

## Architecture and Execution Flow

1. A request arrives through the desktop app, web dashboard, CLI, Slack, Discord, Telegram, Teams, Webex, WeCom, or WeChat.
2. The Gateway maps the request to an isolated logical agent session.
3. The session receives memory, lessons, skills, MCP tools, approval state, and security policy.
4. Kiro Crew drives `kiro-cli` over ACP and streams model and tool activity back to the surface.
5. Independent work can be delegated to isolated subagents. Their summarized results return to the parent session.
6. A Task Runner spec is decomposed into ordered steps. Each step uses a fresh session, executes tools, runs tests, receives independent review, commits on success, and retries or replans when necessary.
7. Cron jobs, heartbeats, and authenticated webhooks create background sessions. The Gateway must remain running; missed cron executions are not replayed after downtime.

The Gateway, agent runtime, ACP processes, and persistent state currently run on the same host. Remote operation uses an SSH tunnel rather than requiring a Kiro-hosted control plane. Multi-instance mode is opt-in and connects several remote Gateways through supervised loopback SSH tunnels.

## High-Value Team Uses

### 1. Read-only engineering intelligence

Start with PR summaries, CI failure diagnosis, deployment-status checks, and AWS observability queries. MCP servers can expose external APIs and AWS data, but the agent only sees the resources and permissions granted to it.

### 2. Bounded migrations and test repair

Use Task Runner for dependency updates, repetitive API migrations, test repairs, and documentation consistency work. Give it a precise spec, explicit acceptance criteria, a disposable branch or worktree, and a force-approval gate before any destructive or external side effect.

### 3. Internal workflow Apps

If a workflow repeats, package it as a Crew App with a focused UI, custom agent, skill, MCP integration, and schedule. Issue triage, deployment readiness, feature-flag operations, and incident intake are better App candidates than general-purpose chat prompts.

## Recommended 30-Day Pilot

### Days 1-3: Local and read-only setup

1. Install the stable release.
2. Run `kirocrew setup`, `kirocrew doctor`, and `kirocrew gateway`.
3. Keep the dashboard on loopback and use interactive approvals.
4. Keep the sandbox at `auto` or `strict`.
5. Confirm which `.kiro` configuration is being inherited.

### Week 1: Constrain the agent

Create a read-only reviewer agent with only the tools needed for repository inspection, such as `fs_read` and `grep`. Commit project-specific steering and skills in `.kiro/`; keep personal defaults outside the repository.

### Week 2: Add low-risk automation

Create a weekday PR and CI digest using fresh cron sessions. Send results to the dashboard first, then add Slack after the local workflow is understood. Do not grant write or deployment access.

### Week 3: Run one bounded change

Execute one non-production migration with Task Runner. Require tests, independent review, a clean branch/worktree, and explicit approval before publish, deploy, delete, or infrastructure mutation steps.

### Week 4: Evaluate

Compare against a baseline using human triage time, time to useful diagnosis, test-pass rate, retry count, false alerts, manual corrections, and model/credit usage. Keep the pilot only if it reduces toil without increasing review or incident risk.

## Security and Operational Guardrails

- The default `kirocrew` agent has broad file, shell, web, and MCP access. Use custom agents for shared or automated workflows.
- Interactive approval is the default. Autopilot removes the human approval loop, although Crew deny rules and sensitive-path blocks still apply.
- Use Task Runner force-approval gates for deploy, delete, publish, and other irreversible actions.
- Crew's local protections do not replace AWS IAM. Use a dedicated least-privilege role, preferably read-only during the pilot.
- Keep the dashboard on localhost. Use SSH tunneling for remote hosts; do not expose port `5476` directly to the Internet.
- Keep the OS sandbox enabled. Windows does not provide the Linux namespace or macOS Seatbelt layer and requires an explicit unsandboxed opt-in for agent execution.
- Treat third-party Apps as untrusted. They are disabled by default, and several declared permissions are advisory rather than enforced in-process.
- Do not paste credentials into chat. Output redaction is not a substitute for safe input handling.
- Review persistent lessons and memory because stale or incorrect guidance can affect future sessions.
- Do not use Task Runner's self-review as the final release gate. CI, branch protection, and human review remain authoritative.
- Treat cron as a scheduler, not a durable queue. Use an external queue or CI system for critical work that must not be lost during Gateway downtime.
- Review the repository's telemetry behavior with the company privacy team. The public repository documents an anonymous daily heartbeat and provides `kirocrew telemetry disable`.

## Crew Subagents versus `kiro-flock`

Use normal Crew subagents or Task Runner when the task has dependencies, needs central verification, is interactive, or requires a human approval gate.

Use the AWS `kiro-flock` pattern only for experiments or workloads with many quasi-independent contributions where diversity and throughput matter more than centralized verification. AWS describes the sample as a reference implementation, not a production system. Its documented failure modes include groupthink, stale shared state, agent drift, and hotspot concentration.

The supervisor-style Task Runner should remain the default for production engineering work.

## Medium Findings and Confidence

Medium articles were useful for workflow examples, not as authoritative product documentation:

- [Custom agents, steering, skills, and hooks](https://medium.com/@manojkumars.msec/ai-team-in-your-terminal-mastering-custom-agents-with-kiro-cli-49449ade69ad) demonstrates role-separated agent workflows.
- [Kiro at Lap 1 Labs](https://medium.com/@dustin_44710/how-we-use-kiro-at-lap-1-labs-q2-update-26fa6c8cebf9) describes multi-root workspaces, global/project steering, spec traceability, Secrets Manager, and least-privilege patterns.
- [AWS monitoring agents with Kiro and MCP](https://medium.com/@akgmt20/building-ai-powered-aws-monitoring-agents-with-kiro-ide-and-mcp-022061bc2c4a) shows an anecdotal infrastructure, cost, and DevOps-agent workflow.
- [AWS networking troubleshooting with Kiro MCP servers](https://medium.com/@pooriaghaedi/can-ai-troubleshoot-aws-networking-testing-mcp-servers-with-kiro-5df2a149d0d5) illustrates that MCP can inspect AWS topology while still lacking application-level instance context.
- [Full-stack AWS application with Kiro, Powers, and MCP](https://medium.com/awsfullstack/i-built-a-full-stack-app-with-kiro-in-under-two-hours-56f8b55f6cfc) illustrates spec-driven requirements, design, tasks, and AWS implementation.

Claims about pricing, internal incidents, proprietary implementation details, compliance, or measured productivity were not carried into this report unless corroborated by current official documentation.

## Primary Sources

- [Introducing Kiro Crew](https://kiro.dev/blog/introducing-kiro-crew/)
- [Kiro Crew quick start](https://kiro.dev/docs/crew/)
- [Installation](https://kiro.dev/docs/crew/installation/)
- [Agents](https://kiro.dev/docs/crew/capabilities/agents/)
- [Subagents](https://kiro.dev/docs/crew/features/subagents/)
- [Task Runner](https://kiro.dev/docs/crew/features/task-runner/)
- [Cron and scheduling](https://kiro.dev/docs/crew/features/cron/)
- [Security](https://kiro.dev/docs/crew/security/)
- [Apps](https://kiro.dev/docs/crew/apps/)
- [Interfaces](https://kiro.dev/docs/crew/interfaces/)
- [Running 24/7](https://kiro.dev/docs/crew/running-24-7/)
- [Multi-instance](https://kiro.dev/docs/crew/features/multi-instance/)
- [Kiro Crew GitHub repository](https://github.com/kirodotdev/KiroCrew)
- [AWS: Scaling patterns for self-organizing multi-agent clusters](https://aws.amazon.com/blogs/architecture/scaling-patterns-for-self-organizing-multi-agent-clusters-with-kiro/)
