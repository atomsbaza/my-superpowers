# Monitoring & Alerting Strategy

## Status: DECISION MADE — DingTalk-based alerts

## Alert Categories by Team

### Fraud/Compliance Team (DingTalk: KYC-Fraud-Alert)

**Immediate alerts (🔴):**
- CDD Blacklist Hit (`CddAutoResultStatus = Matched` on sanctions/blacklist)
- Same CitizenId across multiple partners in short window

**Within 1hr (🟡):**
- High-volume NotPass from single partner (>N in 1 hour)
- PEP/Influencer match (`CddType = PepInfluencer`)
- Bankruptcy match (Kateraengpetch positive)

**Daily digest:**
- Applications processed, approval/rejection/manual review breakdown
- CDD hits summary (sanctions, PEP, bankruptcy, watchlist)
- Top flagged partners
- Manual review queue age

### L1 Support / Operations (DingTalk: KYC-Ops-Alert)

**Immediate (🔴):**
- Service health check failure (`/hc` unhealthy)
- Error rate spike (>5% 5xx in 5-min window)
- DB replica lag (>5s behind primary)

**Within 15min (🟡):**
- Partner API latency (P95 > 5s)
- SQS DLQ growing (count > 0)
- External provider down (DOPA/DBD/Refinitiv/Zoloz errors)
- Application stuck in Processing (status 5 for >1 hour)

**Daily:**
- Certificate/token expiry warnings (7 days out)

**Real-time dashboard:**
- Service health + latency
- Error rates
- SQS queue depths
- External provider status

### L2 Engineering (DingTalk: KYC-Engineering)

**Immediate (🔴):**
- Encryption key mismatch (decryption failures)
- DB replica lag (>5s)

**Within 15min (🟡):**
- Repeated same error (>10 in 10 min)
- Contract mismatch (deserialization errors)
- Approval job not running (no status transitions for >30 min)

**Weekly summary:**
- Uptime %, error budget remaining
- Top errors + root causes
- Performance trends
- Action items

## Implementation Plan

1. **OpenSearch alerts** (L1/L2) — query existing logs, send to DingTalk webhook
2. **Quartz job** (business alerts) — new job in `approval` service or dedicated `monitoring` service
   - Queries DB for CDD hits, stuck applications, duplicate CitizenIds
   - Sends markdown messages to DingTalk groups
3. **CloudWatch dashboards** (optional) — infra metrics (CPU, memory, DB lag)

## DingTalk Integration

All alerts use webhook POST:
```
POST https://oapi.dingtalk.com/robot/send?access_token={token}
Content-Type: application/json

{
  "msgtype": "markdown",
  "markdown": {
    "title": "Alert Title",
    "text": "### Details\n- **Field:** value"
  }
}
```

Supports markdown, @mentions, action cards.

## Next Steps

- [ ] Create monitoring service or Quartz job for business alerts
- [ ] Set up OpenSearch alert rules for L1/L2
- [ ] Configure DingTalk group webhooks (3 groups)
- [ ] Build real-time dashboard (CloudWatch or custom)
