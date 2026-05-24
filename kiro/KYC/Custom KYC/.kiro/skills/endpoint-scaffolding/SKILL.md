---
name: endpoint-scaffolding
description: Scaffold a new API endpoint with MediatR handler, FluentValidation, and xUnit tests. Use when adding a new endpoint to any KYC project. Pairs with: api-contract-designer subagent.
---

# Endpoint Scaffolding

## Structure by Project Type

### Clean Architecture (identification, kyc-customer-due-diligence, cdd-business, verification)

```
src/
├── {Project}.API/Controllers/{Domain}Controller.cs      # Add action method
├── {Project}.Application/Handler/V{n}/{Action}/
│   ├── {Action}Request.cs          # IRequest<{Action}Response>
│   ├── {Action}Handler.cs          # IRequestHandler
│   ├── {Action}RequestValidator.cs # AbstractValidator
│   └── {Action}Response.cs         # Response DTO
tests/
├── {Project}.Test.API/Controller/{Domain}ControllerTest.cs
└── {Project}.Test.Application/Handler/V{n}/{Action}/{Action}HandlerTest.cs
```

### Layered Architecture (kyc-partner-api, kyc-e-kyc-api)

```
{Project}.AppCommon/Handlers/V{n}/{Domain}/{Action}Handler.cs
{Project}.AppCommon.Data/Message/Request/V{n}/{Action}Request.cs
{Project}.AppCommon.Data/Message/Response/V{n}/{Action}Response.cs
{Project}.API/Controllers/{Domain}Controller.cs
{Project}.Test/Handler/V{n}/{Domain}/{Action}HandlerTest.cs
```

## Controller Pattern

```csharp
[HttpPost("{action-route}")]
public async Task<IActionResult> {Action}([FromBody] {Action}Request? request)
{
    if (request is null)
        return BadRequest(new { error = "Invalid Request" });

    var result = await _mediator.Send(request);
    return result.Code switch
    {
        ResultCode.SUCCESS => Ok(result),
        ResultCode.INVALID_REQUEST => BadRequest(new { error = result.Error }),
        _ => StatusCode(500, new { error = result.Error ?? "Internal error" })
    };
}
```

## Request Pattern

```csharp
public class {Action}Request : IRequest<{Action}Response>
{
    // Properties here
}
```

## Handler Pattern

```csharp
public class {Action}Handler : IRequestHandler<{Action}Request, {Action}Response>
{
    private readonly ILogger<{Action}Handler> _logger;
    // Inject repositories, services

    public async Task<{Action}Response> Handle({Action}Request request, CancellationToken cancellationToken)
    {
        try
        {
            // Business logic
            return new {Action}Response { Code = ResultCode.SUCCESS };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in {Action}");
            return new {Action}Response { Code = ResultCode.FAIL, Error = "System error" };
        }
    }
}
```

## Validator Pattern

```csharp
public class {Action}RequestValidator : AbstractValidator<{Action}Request>
{
    public {Action}RequestValidator()
    {
        RuleFor(x => x.RequiredField).NotEmpty();
        // Add rules
    }
}
```

## Test Pattern

```csharp
public class {Action}HandlerTest
{
    private readonly {Action}Handler _handler;
    // Faked dependencies

    public {Action}HandlerTest()
    {
        // Setup with FakeItEasy
    }

    [Fact]
    public async Task When_ValidRequest_Then_ReturnsSuccess()
    {
        // Arrange
        var request = new {Action}Request { /* valid data */ };
        // Act
        var result = await _handler.Handle(request, CancellationToken.None);
        // Assert
        Assert.Equal(ResultCode.SUCCESS, result.Code);
    }

    [Fact]
    public async Task When_InvalidInput_Then_ReturnsInvalidRequest()
    {
        // Arrange / Act / Assert
    }
}
```

## Checklist
- [ ] Request implements `IRequest<TResponse>`
- [ ] Validator registered via `AddValidatorsFromAssembly`
- [ ] Handler registered via `AddMediatR` assembly scanning
- [ ] Controller uses `[Authorize]` and `[ApiVersion]`
- [ ] PII fields have encryption/masking configured
- [ ] Tests cover: success, validation failure, not found, system error
- [ ] URL versioning: `/api/v{version}/...`
- [ ] If adding a new external service client: add health check (use `health-check-generator` skill)
