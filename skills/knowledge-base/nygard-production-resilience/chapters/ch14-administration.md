# Chapter 14 — Administration

## Core Idea

Production systems are administered under time pressure. Configuration, startup, shutdown, and administrative interfaces therefore need the same design care as customer-facing code. A system that works only when operators edit files manually, kill processes, or guess at hidden state is not production-ready.

## Frameworks Introduced

- **Environment parity:** QA must exercise the same operational assumptions that production relies on.
- **Configuration as a contract:** values need validation, ownership, safe defaults, and versioning.
- **Lifecycle discipline:** startup and shutdown must be explicit, observable, repeatable, and safe under interruption.
- **Scriptable administration:** operational actions should be automatable, authenticated, audited, and idempotent where possible.

## Key Concepts

### Does QA match production?

Differences in JVM/runtime version, operating system, network, DNS, file layout, credentials, data volume, time zone, clock behavior, and resource limits create false confidence. Full production parity may be too expensive, but every difference should be known and tested for its effect. Configuration validation should run before traffic is accepted.

### Configuration files

Configuration is executable behavior. Treat it as a typed contract with:

- required and optional values;
- ranges and cross-field constraints;
- environment-specific ownership;
- secret handling;
- reload versus restart semantics;
- version compatibility;
- safe defaults and explicit absence behavior.

Fail early on invalid configuration with an actionable error. Do not silently fall back to a dangerous default, and do not allow a partial reload to leave the process with a mixture of old and new settings unless that state is designed.

### Startup and shutdown

Startup should establish dependencies, validate configuration and credentials, publish readiness only when useful service is possible, and expose the reason for failure. Shutdown should stop admission, drain or reject new work, finish or cancel in-flight work according to policy, release resources, and leave a clear status.

An orchestrator sending a termination signal is not an exceptional edge case. Test interruption during startup, shutdown, dependency connection, cache warm-up, and long-running jobs. Make repeated start/stop safe.

### Administrative interfaces

Administrative operations should be narrow and explicit: health detail, configuration inspection without secrets, cache invalidation, drain, reload, key rotation, queue status, and controlled feature toggles. They need authentication, authorization, audit events, rate limits, and safe error handling. Prefer commands that can be invoked by scripts and return machine-readable results.

Avoid a single “do everything” admin endpoint. A broad interface becomes an attractive attack path and makes incident actions hard to reason about. Separate read-only diagnostics from state-changing operations.

## Reference Table

| Area | Unsafe behavior | Safer contract |
|---|---|---|
| Configuration | Silent defaults and ad hoc edits | Validated, owned, versioned settings |
| Readiness | Process accepts traffic immediately | Publish only after useful service is ready |
| Shutdown | Kill and hope | Drain, cancel, release, and report |
| Admin API | Hidden or unrestricted controls | Narrow, authenticated, audited operations |
| QA | Environment assumed equivalent | Differences listed and tested |

## Worked Example

A service starts successfully with a missing queue URL because it falls back to localhost. It passes a smoke test until deployed, then accepts traffic and blocks on a nonexistent local dependency. A typed startup check should reject the configuration before readiness, while the deployment system should report the exact missing value. The administrative interface should expose dependency status without revealing credentials.

## Key Takeaways

1. Configuration and lifecycle behavior are part of the product.
2. Readiness must mean the service can perform useful work.
3. Startup and shutdown require failure-path tests.
4. Make administrative actions narrow, authenticated, observable, and scriptable.

## Connects To

- Chapter 12 covers credential and privilege behavior.
- Chapter 17 provides operational transparency for lifecycle and admin actions.
- Chapter 18 treats configuration, deployment, and documentation as release design.

