# Topic 4: Connection Pooling and Background-Job Resource Consumption

## The failure mode

A recurring production incident pattern in .NET 5+ services using MySQL-family databases (MySQL, Aurora MySQL, OceanBase MySQL-mode) plus **Hangfire** for background jobs: the database rejects new connections with a "max connections" / "too many connections" error under otherwise-normal load.

## Root cause

Hangfire's default configuration runs **10 worker threads per process**, and each worker holds its own polling connection to the job storage database in addition to any connections used by application requests. Scale to multiple app instances/processes (common in containerized deployments) and the per-process worker connections alone can exhaust the database's configured max-connections limit — before application traffic is even accounted for.

## Mitigations (in order of preference)

1. **Reduce Hangfire's worker count** from the default 10 to a number sized for actual job throughput needs — most services don't need 10 concurrent background workers per process.
2. **Raise the database's max-connections parameter** if worker count is already right-sized and connections are still tight — but treat this as a capacity increase, not a fix for an unbounded consumer.
3. **Check connection pooling configuration** on the ADO.NET provider side (e.g. Pomelo's `MySqlConnectorFactory` pool size) — a pool sized far above what the database allows will surface as intermittent connection failures under load rather than a clean rejection.

## Applies beyond Hangfire

The general lesson: any background-processing framework that polls a shared database (schedulers, outbox processors, distributed cron) multiplies its connection footprint by worker count × process count. Audit that multiplication explicitly against the database's connection ceiling before scaling out process count as a fix for job throughput — scaling out often makes a marginal connection-pressure problem into an outage.
