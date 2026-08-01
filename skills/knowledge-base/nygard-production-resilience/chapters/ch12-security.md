# Chapter 12 — Security

## Core Idea

Security failures can become stability failures. Excess privilege increases blast radius; poorly managed credentials create emergency outages, unsafe workarounds, and difficult rotation. Security controls should reduce what a component can do while preserving a clear operational path for legitimate work.

## Frameworks Introduced

- **Principle of least privilege:** grant only the actions and resources required by a component, identity, or operator.
- **Credential indirection:** keep secrets out of source, command lines, logs, and ordinary configuration distribution paths.
- **Operational security:** make rotation, revocation, auditing, and failure behavior part of the design.

## Key Concepts

### Principle of least privilege

Separate identities by service, environment, role, and administrative purpose. A web process should not use a database account that can drop schemas or read unrelated tenants. A deployment identity should not be the same as a runtime identity. Privileges should be narrow enough that a compromised component cannot turn one defect into a system-wide event.

Least privilege applies to:

- database tables, procedures, and schemas;
- files, sockets, devices, and operating-system capabilities;
- network destinations and ports;
- cloud resources and APIs;
- administrative actions and production data.

Make permissions observable and test them in an environment that resembles production. A permission that is “temporarily” broad tends to become an undocumented dependency.

### Configured passwords and secrets

Passwords embedded in source code, deployment scripts, command-line arguments, or widely readable configuration files leak through repositories, process listings, backups, logs, and support bundles. The book’s older configuration examples should be interpreted with current practice: use a secret manager or protected runtime injection, rotate credentials, and avoid exposing values to unrelated operators or processes.

The application still needs a defined failure mode when a secret is missing, expired, or rejected. Startup validation can fail before serving traffic; runtime rotation may require a controlled reload. Do not log the secret while diagnosing authentication failures.

### Security and availability tradeoffs

Removing authentication or widening access may appear to restore service, but it creates a larger incident. Prefer a controlled degraded mode, a temporary scoped credential, or a fail-closed administrative path with an audited emergency procedure. Security controls must be operable under stress.

## Reference Table

| Practice | Avoid | Prefer |
|---|---|---|
| Runtime identity | Shared superuser | Narrow per-service identity |
| Secret delivery | Source, CLI, or plaintext logs | Protected secret manager/injection |
| Rotation | Manual emergency edits | Tested, documented rotation path |
| Failure | Silent retries or leaked values | Clear error, bounded retry, safe alert |
| Emergency access | Untracked privilege expansion | Scoped, time-limited, audited access |

## Review Checklist

- Can this component perform only its required operations?
- Are production and non-production identities separate?
- Can credentials be rotated without a code change?
- Do startup and reload paths validate credentials safely?
- Are secrets absent from logs, crash reports, process arguments, and support bundles?
- Is there an audited emergency procedure that does not disable unrelated controls?

## Worked Example

An order service needs to insert orders and read product prices. Its shared database account also has schema-alter and customer-export permissions. A compromise or SQL injection now has a large blast radius. Create a dedicated account with only the required operations, expose credentials through a secret manager, test rotation in staging, and alert on denied operations. The narrower account may reveal hidden dependencies during rollout; that discovery is useful design feedback.

## Key Takeaways

1. Least privilege limits both security impact and operational blast radius.
2. Credentials need lifecycle design: delivery, rotation, revocation, and failure behavior.
3. Modern secret management is the safe interpretation of older “configured password” practices.
4. Never make a security bypass the default incident response.

## Connects To

- Chapter 11 limits network exposure and path ambiguity.
- Chapter 14 covers safe configuration and administrative interfaces.
- Chapter 17 supplies the audit and monitoring perspective needed to operate controls.

