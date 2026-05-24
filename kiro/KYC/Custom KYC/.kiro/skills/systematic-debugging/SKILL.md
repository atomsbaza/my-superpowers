---
name: systematic-debugging
description: "Structured debugging loop for bugs, production failures, and hard-to-reproduce issues in the KYC platform. Use as a discipline layer before hypothesizing — ensures you reproduce first, minimise second, then prove the root cause. Pairs with: bug-investigator, incident-debugger, log-investigator subagents."
---

# Systematic Debugging

Discipline over intuition. Reproduce → minimise → hypothesise → instrument → prove → fix → regression test.

## The Loop

```
1. REPRODUCE   — confirm you can trigger the failure consistently
2. MINIMISE    — reduce scope to the smallest failing case
3. HYPOTHESISE — form one specific, falsifiable theory
4. INSTRUMENT  — add just enough visibility to test it
5. PROVE       — test confirms or refutes the hypothesis
6. FIX         — minimal code change that targets the root cause
7. REGRESSION  — write a test that would have caught this earlier
```

Never jump to Fix before Prove. Never add logging everywhere — add just enough to test your hypothesis.

---

## 1. Reproduce

Before anything else, confirm the failure is reproducible.

**Questions to answer:**
- Can you trigger it with a specific request, data, or state?
- Is it consistent or intermittent? (If intermittent → timing/race condition → go to Phase 3 with that lens)
- Does it reproduce in SIT? Locally? (If only in prod → environmental difference is a clue)

**KYC-specific reproduction steps:**
1. Get the `RequestId` or `CorrelationId` from the reporter
2. Find the log entry in OpenSearch → extract exact request body from `fields.ClientReq`
3. Replay the request to SIT with the same payload
4. If the bug is state-dependent (e.g., application stuck at status 5), check DB first

**If you can't reproduce:**
- Broaden: Is it happening to many requests or just one?
- Check if environment config differs (Secrets Manager values, appsettings overrides)
- Check recent deploys — was a service updated between "worked" and "broken"?

---

## 2. Minimise

Shrink the failing case to its essential elements.

- Remove optional request fields — which ones are required to trigger the bug?
- Identify the service boundary where it breaks (stops reproducing after you remove a service from the chain?)
- For data bugs: which row/application ID triggers it? Can you find a pattern?
- For SQS bugs: can you reproduce by sending the message manually?

Goal: a single HTTP call or SQL query that demonstrates the failure.

---

## 3. Hypothesise

Form **one** specific, falsifiable theory. Not "something is wrong with the DB" but "the handler returns D01 because `GetById` queries Replica and there's replica lag after the INSERT."

**KYC hypothesis templates:**

| Symptom | Hypothesis |
|---------|-----------|
| Status stuck at 5 (Processing) | SQS message was never sent (IAM denied) OR consumer never received it (wrong QueueUrl) OR consumer crashed on deserialization |
| 401 from service-to-service call | HMAC key mismatch OR clock skew > tolerance OR scheme mismatch (basic vs ApiKey) |
| Null/missing field in response | PII field not decrypted (crypto service not injected OR field name mismatch in EntitiesExtra) |
| Data not found (D01) immediately after save | Read-after-write on Replica — use PrimaryDbContext for immediate reads |
| Intermittent failures under load | Connection pool exhausted OR unbounded query without `.Take()` hitting MySQL timeout |
| CDD not triggered | SQS publish succeeded but consumer index missing in OpenSearch — check Argo logs |
| Wrong audit record | `ModifiedBy` vs `CreatedBy` assigned from wrong source |

Write the hypothesis as: **"The bug occurs because X, which means if I check Y I should see Z."**

---

## 4. Instrument

Add the minimum visibility to test your hypothesis. Don't add logging everywhere.

**OpenSearch queries:**
```json
// Find by CorrelationId across all services
{"query": {"match": {"fields.CorrelationId": "<uuid>"}}, "sort": [{"@timestamp": "asc"}]}

// Find exception in a service
{"query": {"bool": {"must": [
  {"match": {"fields.CorrelationId": "<uuid>"}},
  {"exists": {"field": "exceptions"}}
]}}}
```

**Local instrumentation (when you need more):**
```csharp
// Temporary: log the exact value causing the issue
_logger.LogDebug("[DEBUG] entity.StatusCode={StatusCode}, handler={Handler}",
    entity.StatusCode, nameof(YourHandler));
```

**Database inspection:**
```sql
-- Check actual row state
SELECT Id, StatusCode, ModifiedDate, ModifiedBy
FROM KycApplication
WHERE Id = {applicationId};

-- Check if DESCRIBE matches entity
DESCRIBE KycApplication;
```

**SQS inspection:**
- Check queue depth in AWS Console → is the message sitting there?
- Check DLQ → did it fail processing?
- Check CloudWatch Logs for IAM denial: `not authorized to perform: sqs:SendMessage`

---

## 5. Prove

Run the reproduction case with instrumentation active and check if your hypothesis holds.

**Hypothesis confirmed** → you know the root cause, go to Fix.

**Hypothesis refuted** → don't add more logging, form a new hypothesis. Common second-round hypotheses:
- You tested the wrong service (the failure is upstream)
- The failure is intermittent and your timing was off
- There's a caching layer hiding the real state (Redis TTL, EF tracking cache)

---

## 6. Fix

Minimal code change that targets the root cause — not the symptom.

**Checklist before fixing:**
- [ ] Does the fix address the root cause or mask the symptom?
- [ ] Does the fix affect both Primary and Replica paths?
- [ ] Does the fix preserve backward compatibility for existing partners?
- [ ] Does the fix expose any PII in logs?
- [ ] Does the fix require a DB migration or stored procedure change?

**Don't:**
- Add null-checks everywhere "just in case" — target the specific null
- Widen catch blocks to swallow the exception
- Add retry logic on top of a broken query — fix the query

---

## 7. Regression Test

Write a test that would have caught this bug before it reached production.

**Match the failure type:**

| Bug type | Test type |
|----------|-----------|
| Handler logic error | xUnit unit test on the handler |
| Validation gap | xUnit test with invalid input |
| EF query returning wrong data | Repository test with EF InMemory |
| Cross-service contract mismatch | Integration test with faked downstream |
| SQS message deserialization | Unit test deserializing the exact JSON shape |
| Read-after-write on Replica | Handler test asserting PrimaryDbContext is used |

**Naming:** `When_{ConditionThatCausedTheBug}_Then_{CorrectBehavior}`

---

## Quick Reference: Common KYC Root Causes

| Bug signal | Root cause | Fix |
|-----------|-----------|-----|
| D01 after save | Read from Replica before lag syncs | Use `PrimaryDbContext` for read-after-write |
| 401 between services | HMAC clock skew or scheme mismatch | Sync server time; verify `Authentication.Key`; check basic vs ApiKey |
| Status stuck at 5 | SQS not sent or consumer crashed | Check SQS queue depth → DLQ → IAM permissions → QueueUrl format |
| Null decrypted PII | `IDatabaseCryptography` not injected via constructor | Use `new Entity(crypto)` constructor, not default constructor |
| `Entity.SomeField` always 0 | Column name mismatch in EF config | Run `DESCRIBE TableName`, match `HasColumnName()` |
| SQS consumer NullReferenceException | `response.Messages` is null (wrong QueueUrl format) | Use full URL; add `?? []` null-safe iteration |
| SQS deserialization failure | Producer sends `string`, consumer expects `sbyte` (or vice versa) | Align DTO types; check LogOrigin enum (sbyte, not string) |
