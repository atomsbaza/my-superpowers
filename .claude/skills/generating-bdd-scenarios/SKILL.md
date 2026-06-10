---
name: generating-bdd-scenarios
description: >
  Generates Gherkin feature files in Reqnroll format (.NET) from requirements,
  acceptance criteria, or manual test cases. Produces .feature files with
  Feature, Background, Scenario, Scenario Outline, and Examples sections, plus
  skeleton C# step definition files. Use when the team practices BDD, when
  product owners need readable specs, or when automation will be Gherkin-driven.
  Trigger keywords: Gherkin, BDD, feature file, scenario, Given When Then,
  Reqnroll, behavior-driven, acceptance test, executable spec, step definitions.
---

## Purpose

Produce Reqnroll-compatible `.feature` files that serve as both human-readable specifications and executable test drivers.

## CRITICAL: Use Reqnroll, Not SpecFlow

SpecFlow's official support ended December 31, 2024. **All generated code uses Reqnroll** (package: `Reqnroll.xUnit`). Step definitions use `[Binding]`, `[Given]`, `[When]`, `[Then]` from the `Reqnroll` namespace, not `TechTalk.SpecFlow`.

## Input

- `.qa-workflow-state.json` → `test_cases_file` (manual test cases, preferred)
- Requirements analysis file or direct acceptance criteria
- Direct user description of the feature behavior

## Feature File Structure Rules

- **One Feature per functional module** (e.g., Authentication, Order Management)
- **Background:** Shared preconditions that apply to every Scenario in the file
- **Scenario:** Single, named test case — always title-cased with a clear description
- **Scenario Outline + Examples:** Data-driven cases (EP/BVA sets, multiple actors)
- **Tags:** `@P0`, `@P1`, `@P2` for priority; `@smoke` for smoke suite; `@regression`; `@manual-only` for cases not yet automated

## Process

### Step 1 — Map Test Cases to Gherkin

For each manual test case:
- Positive P0/P1 test cases → individual `Scenario`
- Negative test cases with the same structure but different data → `Scenario Outline` + `Examples`
- Complex multi-step flows → `Scenario` with Background for shared setup

### Step 2 — Write Feature Files

**Target path:** `tests/BDD/Features/<Module>.feature`

Example output:
```gherkin
@P0 @smoke
Feature: User Authentication
  As a registered user
  I want to log in to the application
  So that I can access my personalized content

  Background:
    Given the application is running
    And the database has been seeded with test users

  @P0
  Scenario: Successful login with valid credentials
    Given I am on the login page
    When I enter email "user@test.com" and password "ValidPass1!"
    And I click the "Sign In" button
    Then I should be redirected to "/dashboard"
    And I should see the welcome message "Welcome, Test User"
    And the auth_token cookie should be set with HttpOnly and Secure flags

  @P1
  Scenario Outline: Login fails with invalid credentials
    Given I am on the login page
    When I enter email "<email>" and password "<password>"
    And I click the "Sign In" button
    Then I should see the error message "<error_message>"
    And I should remain on the login page

    Examples:
      | email              | password      | error_message              |
      | wrong@test.com     | ValidPass1!   | Invalid email or password  |
      | user@test.com      | WrongPass     | Invalid email or password  |
      |                    | ValidPass1!   | Email is required          |
      | user@test.com      |               | Password is required       |
      | not-an-email       | ValidPass1!   | Invalid email format       |

  @P1
  Scenario: Login blocked after 5 failed attempts
    Given I am on the login page
    And I have failed to login 4 times
    When I enter email "user@test.com" and password "WrongPass"
    And I click the "Sign In" button
    Then I should see the message "Account locked. Try again in 15 minutes."
    And the account should be locked for 15 minutes
```

### Step 3 — Generate Skeleton Step Definitions

**Target path:** `tests/BDD/Steps/<Module>Steps.cs`

```csharp
// tests/BDD/Steps/AuthenticationSteps.cs
using Reqnroll;
using Microsoft.Playwright;

namespace MyApp.Tests.BDD.Steps;

[Binding]
public sealed class AuthenticationSteps(IPage page)
{
    [Given(@"I am on the login page")]
    public async Task GivenIAmOnTheLoginPage()
    {
        await page.GotoAsync("/login");
        await page.WaitForLoadStateAsync(LoadState.NetworkIdle);
    }

    [When(@"I enter email ""(.*)"" and password ""(.*)""")]
    public async Task WhenIEnterEmailAndPassword(string email, string password)
    {
        await page.FillAsync("[data-testid='email']", email);
        await page.FillAsync("[data-testid='password']", password);
    }

    [When(@"I click the ""(.*)"" button")]
    public async Task WhenIClickTheButton(string buttonText)
    {
        await page.ClickAsync($"button:has-text('{buttonText}')");
    }

    [Then(@"I should be redirected to ""(.*)""")]
    public async Task ThenIShouldBeRedirectedTo(string path)
    {
        await page.WaitForURLAsync($"**{path}");
    }

    [Then(@"I should see the error message ""(.*)""")]
    public async Task ThenIShouldSeeTheErrorMessage(string message)
    {
        var errorText = await page.TextContentAsync("[data-testid='error-msg']");
        errorText.Should().Be(message);
    }

    [Then(@"the auth_token cookie should be set with HttpOnly and Secure flags")]
    public async Task ThenAuthTokenCookieShouldBeSecure()
    {
        var cookies = await page.Context.CookiesAsync();
        var authCookie = cookies.FirstOrDefault(c => c.Name == "auth_token");
        authCookie.Should().NotBeNull("auth_token cookie should be set");
        authCookie!.HttpOnly.Should().BeTrue();
        authCookie.Secure.Should().BeTrue();
    }
}
```

### Step 4 — Reqnroll Project Setup Snippet

Include this once per feature set if the project doesn't have Reqnroll yet:

```xml
<!-- tests/BDD/MyApp.Tests.BDD.csproj -->
<PackageReference Include="Reqnroll.xUnit" Version="2.1.1" />
<PackageReference Include="Microsoft.Playwright.Xunit" Version="1.46.0" />
<PackageReference Include="FluentAssertions" Version="6.12.0" />
```

```json
// tests/BDD/reqnroll.json
{
  "$schema": "https://reqnroll.net/reqnroll-json-schema",
  "bindingCulture": { "language": "en-US" }
}
```

### Step 5 — Output

Write `.feature` files to `tests/BDD/Features/<Module>.feature`.
Write step definition stubs to `tests/BDD/Steps/<Module>Steps.cs`.

Update `.qa-workflow-state.json`:
```json
{
  "stage": "bdd_scenarios_generated",
  "feature_files": ["tests/BDD/Features/Authentication.feature"],
  "step_definition_stubs": ["tests/BDD/Steps/AuthenticationSteps.cs"],
  "scenario_count": 0,
  "error": null
}
```
