---
name: async-messaging
description: 'Async patterns bundle: async/await/Channels concurrency, SQS publisher/consumer, BackgroundService + DLQ pattern, Quartz scheduled jobs. Pairs with: cross-project, db-migration subagents.'
---

# Async & Messaging

Four sections:
1. **Concurrency primitives** — async/await, Channels, locks (when to use what)
2. **SQS publisher/consumer** — sending and receiving AWS SQS messages
3. **BackgroundService + DLQ** — scaffolding a new SQS consumer worker
4. **Quartz scheduled jobs** — cron-triggered background tasks

---

## 1. Concurrency Primitives

### Philosophy

**Start simple, escalate only when needed.** Most concurrency problems can be solved with `async/await`. Only reach for more sophisticated tools when async/await can't address the need cleanly.

**Avoid shared mutable state.** Best handled by:
1. Redesign to avoid it (immutability, message passing, actor isolation)
2. Use `System.Collections.Concurrent` (ConcurrentDictionary, etc.)
3. Use `Channel<T>` to serialize access through message passing
4. Use `lock` only for simple, short-lived critical sections (last resort)

### Decision Tree

```
What are you trying to do?
│
├─► Wait for I/O (HTTP, database, file)?
│   └─► async/await
│
├─► Process a collection in parallel (CPU-bound)?
│   └─► Parallel.ForEachAsync
│
├─► Producer/consumer pattern (work queue)?
│   └─► System.Threading.Channels
│
├─► Coordinate multiple async operations?
│   └─► Task.WhenAll / Task.WhenAny
│
├─► Stateful entity with concurrent access?
│   └─► Actor pattern (Akka.NET) or Channel-per-entity
│
└─► Truly need a lock?
    └─► lock { } for critical section
```

### async/await Rules

- Use `Task` (not `void`) for async methods
- Use `ConfigureAwait(false)` in library code (not in ASP.NET Core handlers)
- Use `CancellationToken` parameters for cancellable operations
- Don't `.Wait()` or `.Result` on a Task — deadlock risk

### Channel<T> Pattern

```csharp
var channel = Channel.CreateBounded<MyMessage>(100);

// Producer
await channel.Writer.WriteAsync(message);

// Consumer (in BackgroundService)
await foreach (var msg in channel.Reader.ReadAllAsync(stoppingToken))
{
    await ProcessAsync(msg);
}
```

### Anti-Patterns

- ❌ `Task.Run` to wrap synchronous code in a hot path (just call sync)
- ❌ `async void` (except event handlers)
- ❌ Sync-over-async (`.Result`, `.Wait()`)
- ❌ Manual locking for thread safety when ConcurrentDictionary works

---

## 2. SQS Publisher/Consumer

### Publisher Pattern

```csharp
public interface ISqsPublisher
{
    Task SendCddMessage(long applicationId);
}

public class SqsPublisher : ISqsPublisher
{
    private readonly IAmazonSQS _sqsClient;
    private readonly ILogger<SqsPublisher> _logger;
    private readonly string _queueUrl;

    public SqsPublisher(IAmazonSQS sqsClient, IConfiguration configuration, ILogger<SqsPublisher> logger)
    {
        _sqsClient = sqsClient;
        _logger = logger;
        _queueUrl = configuration["Amazons:CddSqsUrl"] ?? string.Empty;
    }

    public async Task SendCddMessage(long applicationId)
    {
        var message = JsonSerializer.Serialize(new { Id = applicationId, Origin = (sbyte)5, UpdateBy = 1 });
        var request = new SendMessageRequest(_queueUrl, message);
        var result = await _sqsClient.SendMessageAsync(request);
        _logger.LogInformation("SQS sent. MessageId={MessageId}, ApplicationId={ApplicationId}",
            result.MessageId, applicationId);
    }
}
```

### DI Registration

```csharp
services.AddAWSService<IAmazonSQS>();
services.AddScoped<ISqsPublisher, SqsPublisher>();
```

### Critical Rules

- **QueueUrl must be full URL**: `https://sqs.{region}.amazonaws.com/{account-id}/{queue-name}` — never just the queue name
- **Null-safe iteration**: Always use `response.Messages ?? []` — AWS SDK can return null Messages
- **Match producer/consumer types exactly**: If consumer expects `sbyte Origin`, producer must send a number, not a string

> **Source of truth for KYC SQS contracts:** See `.kiro/steering/shared-conventions.md` → "SQS Message Contracts" and "LogOrigin Enum Values" tables.

### Publisher Checklist

- [ ] Queue URL is full URL (not just queue name) in appsettings or Secrets Manager
- [ ] `IAmazonSQS` registered via `AddAWSService<IAmazonSQS>()`
- [ ] Logs MessageId for tracing
- [ ] IAM role has `sqs:SendMessage` permission on the target queue
- [ ] Message JSON types match consumer DTO types exactly

---

## 3. BackgroundService + DLQ Pattern

### When to Use

- Consuming messages from an SQS queue
- Adding async processing triggered by another service
- Setting up a DLQ consumer for failed messages

### Steps

#### 1. Create SQS setting

```csharp
// Infrastructure/Setting/{Feature}SqsSetting.cs
public class {Feature}SqsSetting
{
    public string QueueUrl { get; set; } = null!;
    public string DlqUrl { get; set; } = null!;
    public int WaitTimeSeconds { get; set; } = 20;
    public int MaxNumberOfMessages { get; set; } = 1;
}
```

#### 2. Main consumer

```csharp
// Background/{Feature}Background.cs
public class {Feature}Background(
    ILogger<{Feature}Background> logger,
    IServiceScopeFactory scopeFactory,
    {Feature}SqsSetting sqsSetting) : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken ct)
    {
        if (!sqsSetting.QueueUrl.StartsWith("https://"))
            logger.LogCritical("QueueUrl is not a valid URL: {QueueUrl}. Messages will NOT be received.", sqsSetting.QueueUrl);

        logger.LogInformation("{Feature}Background started, QueueUrl={QueueUrl}", sqsSetting.QueueUrl);
        var sqsClient = new AmazonSQSClient();

        while (!ct.IsCancellationRequested)
        {
            try
            {
                var response = await sqsClient.ReceiveMessageAsync(new ReceiveMessageRequest
                {
                    QueueUrl = sqsSetting.QueueUrl,
                    MaxNumberOfMessages = sqsSetting.MaxNumberOfMessages,
                    WaitTimeSeconds = sqsSetting.WaitTimeSeconds
                }, ct);

                if (response.Messages is null)
                {
                    logger.LogCritical("SQS returned null Messages. QueueUrl is likely invalid: {QueueUrl}", sqsSetting.QueueUrl);
                    await Task.Delay(30000, ct);
                    continue;
                }

                foreach (var message in response.Messages)
                {
                    using var _ = LogContext.PushProperty("MessageId", message.MessageId);
                    try
                    {
                        using var scope = scopeFactory.CreateScope();
                        var mediator = scope.ServiceProvider.GetRequiredService<IMediator>();
                        var request = JsonConvert.DeserializeObject<{Feature}Request>(message.Body)!;
                        await mediator.Send(request, ct);
                        await sqsClient.DeleteMessageAsync(sqsSetting.QueueUrl, message.ReceiptHandle, ct);
                        logger.LogInformation("SQS message processed: MessageId={MessageId}", message.MessageId);
                    }
                    catch (Exception ex) when (ex is IAppException)
                    {
                        await sqsClient.DeleteMessageAsync(sqsSetting.QueueUrl, message.ReceiptHandle, ct);
                        logger.LogWarning(ex, "Business exception, message deleted: MessageId={MessageId}", message.MessageId);
                    }
                    catch (Exception ex)
                    {
                        logger.LogError(ex, "Message left for redelivery: MessageId={MessageId}", message.MessageId);
                    }
                }
            }
            catch (OperationCanceledException) when (ct.IsCancellationRequested) { break; }
            catch (Exception ex)
            {
                logger.LogError(ex, "Error receiving SQS messages");
                await Task.Delay(5000, ct);
            }
        }
        logger.LogInformation("{Feature}Background stopped");
    }
}
```

#### 3. DLQ consumer

```csharp
// Background/{Feature}BackgroundDlq.cs
public class {Feature}BackgroundDlq(
    ILogger<{Feature}BackgroundDlq> logger,
    {Feature}SqsSetting sqsSetting) : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken ct)
    {
        if (!sqsSetting.DlqUrl.StartsWith("https://"))
            logger.LogCritical("DlqUrl is not a valid URL: {DlqUrl}", sqsSetting.DlqUrl);

        var sqsClient = new AmazonSQSClient();
        while (!ct.IsCancellationRequested)
        {
            var response = await sqsClient.ReceiveMessageAsync(new ReceiveMessageRequest
            {
                QueueUrl = sqsSetting.DlqUrl,
                MaxNumberOfMessages = 1,
                WaitTimeSeconds = 20
            }, ct);

            foreach (var message in response.Messages ?? [])
            {
                logger.LogError("DLQ message: MessageId={MessageId}, Body={Body}", message.MessageId, message.Body);
                await sqsClient.DeleteMessageAsync(sqsSetting.DlqUrl, message.ReceiptHandle, ct);
            }
        }
    }
}
```

#### 4. Register in DI

```csharp
services.AddSingleton(sqsSetting);
services.AddHostedService<{Feature}Background>();
services.AddHostedService<{Feature}BackgroundDlq>();
```

#### 5. Config

```json
{
  "{Feature}Sqs": {
    "QueueUrl": "+++ FROM SECRET MANAGER (full URL) +++",
    "DlqUrl": "+++ FROM SECRET MANAGER (full URL) +++",
    "WaitTimeSeconds": 20,
    "MaxNumberOfMessages": 1
  }
}
```

### Consumer Checklist

- [ ] Main consumer deletes on success or known business exception
- [ ] Unknown exceptions leave message for SQS redelivery → DLQ
- [ ] DLQ consumer logs full message body for investigation
- [ ] LogContext pushes MessageId for correlation
- [ ] Graceful shutdown on cancellation token
- [ ] Validates QueueUrl format at startup (LogCritical if invalid)
- [ ] Handles null Messages from SDK (`?? []` or null check)
- [ ] Unit tests for the MediatR handler (not the BackgroundService itself)
- [ ] IAM role has `sqs:ReceiveMessage` + `sqs:DeleteMessage` permissions

---

## 4. Quartz Scheduled Jobs

### When to Use

- Adding a new scheduled/recurring background task
- Polling database on interval (e.g., every 2 minutes)
- Batch processing on a schedule

### Prerequisites

- Quartz NuGet package installed
- `BackgroundProcessExtension` exists in Infrastructure
- `JobConfig` class exists for job registration
- MediatR configured

### Steps

#### 1. Create the MediatR Request/Response

```csharp
// Application/{JobName}Request.cs, {JobName}Response.cs
public class {JobName}Request : IRequest<{JobName}Response> { }
public class {JobName}Response { public bool Success { get; set; } }
```

#### 2. Create the Handler

```csharp
public class {JobName}Handler(
    ILogger<{JobName}Handler> logger)
    : IRequestHandler<{JobName}Request, {JobName}Response>
{
    public async Task<{JobName}Response> Handle({JobName}Request request, CancellationToken ct)
    {
        var stw = logger.LogStartProcessing();
        // Business logic here
        logger.LogEndProcessing(stw);
        return new {JobName}Response { Success = true };
    }
}
```

#### 3. Create the Quartz Job

```csharp
// Infrastructure/Background/{JobName}Batch.cs
public class {JobName}Batch(
    ILogger<{JobName}Batch> logger,
    IMediator mediator,
    JobSchedulerSetting jobSchedulerSetting) : IJob
{
    public async Task Execute(IJobExecutionContext context)
    {
        var stw = logger.LogStartProcessing(Batch.{JobName}.Name, string.Empty);
        LogContext.PushProperty(LogPropertyName.EnvironmentName, Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT"));
        LogContext.PushProperty(LogPropertyName.MachineName, Environment.MachineName);
        LogContext.PushProperty(LogPropertyName.RequestId, Guid.NewGuid().ToString());

        try
        {
            await mediator.Send(new {JobName}Request());
        }
        catch (Exception ex)
        {
            logger.LogWarning(ex, "Error in {JobName}: {Message}", "{JobName}", ex.Message);
        }
        finally
        {
            logger.LogEndProcessing(stw, Batch.{JobName}.Name, string.Empty);
        }
    }
}
```

#### 4. Register in JobConfig

```csharp
jobs.Add(new JobDefinition(typeof({JobName}Batch), nameof(jobScheduler.{JobName}Batch), jobScheduler.{JobName}Batch.Cron));
```

#### 5. Add cron config

```json
{
  "JobScheduler": {
    "{JobName}Batch": {
      "Enable": true,
      "Cron": "0 0/2 * * * ?"
    }
  }
}
```

### Quartz Job Checklist

- [ ] Job registered in `JobConfig`
- [ ] Setting class has the new property
- [ ] appsettings.json has cron expression
- [ ] Handler has unit tests
- [ ] Logs use structured parameters, no raw PII
- [ ] LogContext sets RequestId for traceability

---

## When to Use Which

| Scenario | Use |
|----------|-----|
| Triggered by another service | SQS BackgroundService (Section 3) |
| Recurring on a schedule | Quartz job (Section 4) |
| In-process producer/consumer | Channel<T> (Section 1) |
| One-shot async I/O | async/await (Section 1) |
| Parallel CPU work | Parallel.ForEachAsync (Section 1) |
