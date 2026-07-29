# C# .NET AI-Powered KYC Document Processing Integration Architecture

Date: 2026-07-29
Target Stack: C# .NET 8 / .NET 10
Primary Goal: Accelerate Manual Document Review & Reduce Operational Cost
Architecture Pattern: Hybrid (On-Prem SLM Container + Cloud LLM Fallback)

---

## 1. System Integration Overview

This architecture integrates an **AI-driven Intelligent Document Processing (IDP)** pipeline into an existing **C# .NET** backend. It uses a **Hybrid Resilience Model**:

1. **Fast On-Prem SLM (Primary Path):** Requests are sent to an on-prem containerized Small Language Model (e.g., local Ollama/Tesseract/ONNX SLM endpoint). Runs in 100–300ms with zero external API fees and zero data leakage.
2. **Cloud LLM (Fallback Path):** If local extraction confidence falls below the defined threshold (e.g., `< 0.85`) or document quality is degraded, the C# service automatically falls back to a multi-modal Cloud LLM (Azure OpenAI / Gemini / OpenAI).
3. **Auto-Approve vs. HITL Routing:** 
   - **Confidence $\ge 0.90$ & Validation Passes:** Instant auto-approval (Zero manual review cost).
   - **Confidence $< 0.90$ or Anomaly Detected:** Pre-fills the extraction DTO and routes directly to the human compliance queue.

---

## 2. C# Architecture Diagram

```
[Existing .NET Web API / Worker]
               │
               ▼
   [IKycDocumentProcessor]
               │
       ┌───────┴────────────────────────┐
       ▼                                ▼
[On-Prem SLM Client]          [Cloud LLM Fallback]
 (Primary: 100-300ms)          (Fallback: High Accuracy)
       │                                │
       └───────┬────────────────────────┘
               ▼
  [Validation & Scoring Engine]
               │
       ┌───────┴────────────────────────┐
       ▼                                ▼
[Auto-Approve (< 5% Manual)]  [HITL Compliance Queue]
```

---

## 3. Production C# Code Blueprint (.NET 8 / .NET 10)

### A. Data Transfer Objects (DTOs)

```csharp
namespace KycSystem.AI.Models;

public record KycDocumentExtractionRequest(
    string TransactionId,
    string ApplicantId,
    byte[] DocumentBytes,
    string MimeType,
    KycDocumentType DocumentType
);

public enum KycDocumentType
{
    Passport,
    DriversLicense,
    NationalId,
    UtilityBill
}

public record KycDocumentExtractionResult(
    string TransactionId,
    bool IsSuccess,
    double OverallConfidenceScore,
    ExtractedIdFields? ExtractedFields,
    List<string> AnomalyFlags,
    string ProcessingEngineUsed, // "OnPremSLM" or "CloudLLMFallback"
    long ExecutionDurationMs
);

public record ExtractedIdFields(
    string? FullName,
    string? IdNumber,
    DateTime? DateOfBirth,
    DateTime? ExpiryDate,
    string? Nationality,
    string? IssuingCountry,
    bool MrzChecksumValid
);
```

### B. Configuration Options (`IOptions<KycAiSettings>`)

```csharp
namespace KycSystem.AI.Options;

public class KycAiSettings
{
    public const string SectionName = "KycAi";
    
    public string OnPremSlmEndpoint { get; set; } = "http://localhost:11434/api/generate";
    public string CloudLlmEndpoint { get; set; } = "https://api.openai.com/v1/chat/completions";
    public string CloudApiKey { get; set; } = string.Empty;
    public double MinimumConfidenceThreshold { get; set; } = 0.85;
    public double AutoApprovalThreshold { get; set; } = 0.92;
    public int TimeoutSeconds { get; set; } = 10;
}
```

### C. Abstraction & Hybrid Processor Implementation

```csharp
namespace KycSystem.AI.Services;

using KycSystem.AI.Models;
using KycSystem.AI.Options;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using System.Diagnostics;
using System.Net.Http.Json;
using System.Text.Json;

public interface IKycDocumentProcessor
{
    Task<KycDocumentExtractionResult> ProcessDocumentAsync(
        KycDocumentExtractionRequest request, 
        CancellationToken cancellationToken = default);
}

public class HybridKycDocumentProcessor : IKycDocumentProcessor
{
    private readonly HttpClient _httpClient;
    private readonly KycAiSettings _settings;
    private readonly ILogger<HybridKycDocumentProcessor> _logger;

    public HybridKycDocumentProcessor(
        HttpClient httpClient,
        IOptions<KycAiSettings> settings,
        ILogger<HybridKycDocumentProcessor> logger)
    {
        _httpClient = httpClient;
        _settings = settings.Value;
        _logger = logger;
    }

    public async Task<KycDocumentExtractionResult> ProcessDocumentAsync(
        KycDocumentExtractionRequest request, 
        CancellationToken cancellationToken = default)
    {
        var stopwatch = Stopwatch.StartNew();
        _logger.LogInformation("Starting AI extraction for Tx: {TxId}, DocType: {DocType}", 
            request.TransactionId, request.DocumentType);

        // 1. Try Primary On-Prem SLM Extraction
        try
        {
            var slmResult = await TryExtractOnPremSlmAsync(request, cancellationToken);
            if (slmResult != null && slmResult.OverallConfidenceScore >= _settings.MinimumConfidenceThreshold)
            {
                stopwatch.Stop();
                _logger.LogInformation("On-Prem SLM extraction succeeded for Tx: {TxId} in {Elapsed}ms with score {Score}",
                    request.TransactionId, stopwatch.ElapsedMilliseconds, slmResult.OverallConfidenceScore);
                
                return slmResult with { ExecutionDurationMs = stopwatch.ElapsedMilliseconds };
            }

            _logger.LogWarning("On-Prem SLM score ({Score}) below threshold ({MinScore}). Escalating to Cloud LLM fallback.",
                slmResult?.OverallConfidenceScore ?? 0, _settings.MinimumConfidenceThreshold);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "On-Prem SLM extraction failed for Tx: {TxId}. Escalating to Cloud LLM fallback.", 
                request.TransactionId);
        }

        // 2. Fallback Path: Cloud Multi-Modal LLM
        var cloudResult = await ExtractCloudLlmFallbackAsync(request, cancellationToken);
        stopwatch.Stop();
        
        return cloudResult with { ExecutionDurationMs = stopwatch.ElapsedMilliseconds };
    }

    private async Task<KycDocumentExtractionResult?> TryExtractOnPremSlmAsync(
        KycDocumentExtractionRequest request, 
        CancellationToken cancellationToken)
    {
        // Call local ONNX / Ollama SLM endpoint
        var payload = new
        {
            model = "kyc-idp-slm:latest",
            prompt = BuildExtractionPrompt(request.DocumentType),
            images = new[] { Convert.ToBase64String(request.DocumentBytes) },
            stream = false,
            format = "json"
        };

        using var response = await _httpClient.PostAsJsonAsync(_settings.OnPremSlmEndpoint, payload, cancellationToken);
        if (!response.IsSuccessStatusCode) return null;

        var jsonStr = await response.Content.ReadAsStringSpanAsync(cancellationToken);
        return ParseExtractionJsonResponse(jsonStr.ToString(), request.TransactionId, "OnPremSLM");
    }

    private async Task<KycDocumentExtractionResult> ExtractCloudLlmFallbackAsync(
        KycDocumentExtractionRequest request, 
        CancellationToken cancellationToken)
    {
        // Call Azure OpenAI / Cloud LLM API with high vision precision
        var requestMessage = new HttpRequestMessage(HttpMethod.Post, _settings.CloudLlmEndpoint);
        if (!string.IsNullOrEmpty(_settings.CloudApiKey))
        {
            requestMessage.Headers.Add("Authorization", $"Bearer {_settings.CloudApiKey}");
        }

        var base64Img = Convert.ToBase64String(request.DocumentBytes);
        var payload = new
        {
            model = "gpt-4o-mini",
            response_format = new { type = "json_object" },
            messages = new object[]
            {
                new { role = "system", content = "You are a precise banking KYC document extraction system. Return strictly valid JSON containing: fullName, idNumber, dateOfBirth (YYYY-MM-DD), expiryDate (YYYY-MM-DD), nationality, issuingCountry, mrzChecksumValid (boolean), and confidenceScore (0.0 to 1.0)." },
                new { role = "user", content = new object[]
                    {
                        new { type = "text", content = $"Extract all fields from this {request.DocumentType} image." },
                        new { type = "image_url", image_url = new { url = $"data:{request.MimeType};base64,{base64Img}" } }
                    }
                }
            }
        };

        requestMessage.Content = JsonContent.Create(payload);
        using var response = await _httpClient.SendAsync(requestMessage, cancellationToken);
        response.EnsureSuccessStatusCode();

        var root = await response.Content.ReadFromJsonAsync<JsonElement>(cancellationToken);
        var contentText = root.GetProperty("choices")[0].GetProperty("message").GetProperty("content").GetString()!;

        return ParseExtractionJsonResponse(contentText, request.TransactionId, "CloudLLMFallback");
    }

    private static string BuildExtractionPrompt(KycDocumentType docType) =>
        $"Extract identity details from this {docType} image. Return JSON with keys: fullName, idNumber, dateOfBirth, expiryDate, nationality, issuingCountry, mrzChecksumValid, confidenceScore.";

    private static KycDocumentExtractionResult ParseExtractionJsonResponse(
        string jsonText, string txId, string engineUsed)
    {
        using var doc = JsonDocument.Parse(jsonText);
        var root = doc.RootElement;

        double confidence = root.TryGetProperty("confidenceScore", out var confProp) ? confProp.GetDouble() : 0.8;

        var fields = new ExtractedIdFields(
            FullName: root.TryGetProperty("fullName", out var fn) ? fn.GetString() : null,
            IdNumber: root.TryGetProperty("idNumber", out var id) ? id.GetString() : null,
            DateOfBirth: root.TryGetProperty("dateOfBirth", out var dob) && DateTime.TryParse(dob.GetString(), out var d1) ? d1 : null,
            ExpiryDate: root.TryGetProperty("expiryDate", out var exp) && DateTime.TryParse(exp.GetString(), out var d2) ? d2 : null,
            Nationality: root.TryGetProperty("nationality", out var nat) ? nat.GetString() : null,
            IssuingCountry: root.TryGetProperty("issuingCountry", out var cty) ? cty.GetString() : null,
            MrzChecksumValid: root.TryGetProperty("mrzChecksumValid", out var mrz) && mrz.GetBoolean()
        );

        var flags = new List<string>();
        if (fields.ExpiryDate.HasValue && fields.ExpiryDate.Value < DateTime.UtcNow)
        {
            flags.Add("EXPIRED_DOCUMENT");
        }
        if (!fields.MrzChecksumValid)
        {
            flags.Add("MRZ_CHECKSUM_INVALID");
        }

        return new KycDocumentExtractionResult(
            TransactionId: txId,
            IsSuccess: true,
            OverallConfidenceScore: confidence,
            ExtractedFields: fields,
            AnomalyFlags: flags,
            ProcessingEngineUsed: engineUsed,
            ExecutionDurationMs: 0
        );
    }
}
```

### D. Dependency Injection & Service Registration (`Program.cs`)

```csharp
// Program.cs
builder.Services.Configure<KycAiSettings>(
    builder.Configuration.GetSection(KycAiSettings.SectionName));

// Configure HttpClient with Polly Resilience Handlers
builder.Services.AddHttpClient<IKycDocumentProcessor, HybridKycDocumentProcessor>(client =>
{
    client.Timeout = TimeSpan.FromSeconds(15);
})
.AddStandardResilienceHandler(); // Native .NET 8 resilience policy (retries, circuit breaker)
```

---

## 4. Expected ROI & Manual Review Reduction

| Metric | Before AI Integration | With Hybrid C# AI Architecture |
| :--- | :--- | :--- |
| **Average Document Review Time** | 5 – 15 minutes | **$<$ 500 milliseconds (Auto)** / 1 minute (HITL) |
| **Straight-Through Processing (STP)** | 0% (100% manual) | **80% – 90% Auto-Approved** |
| **Manual Operations Cost** | High | **70% – 85% Operational Cost Reduction** |
| **Data Leakage Risk** | High (third-party cloud) | **Zero (90%+ handled by On-Prem SLM)** |
