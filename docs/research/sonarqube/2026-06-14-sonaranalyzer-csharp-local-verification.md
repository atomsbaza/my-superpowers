# Server-free SonarQube verification for the .NET agent (SonarAnalyzer.CSharp)

**Date:** 2026-06-14
**Goal:** Let `principal-dotnet-engineer` *know* — not guess — whether the C# it
writes will pass SonarQube, without needing a SonarQube server during the inner
dev loop.
**Scope:** Option #1 from the SonarQube discussion — the local Roslyn-analyzer
route. (Option #2, the real server quality gate, is to be checked at the
workplace. Option #3, baking rules into the agent body, follows if #1 works.)

---

## TL;DR

Add the **`SonarAnalyzer.CSharp`** NuGet package to the project (centrally via
`Directory.Build.props`). It is the *same analysis engine* SonarSource ships
inside SonarQube for C#, so `dotnet build` then emits the exact same `Sxxxx`
findings the server would — **no server, no token, no network**. Make those
findings fail the build (`-warnaserror` or per-rule severity), and the agent can
build → read the violations → fix → rebuild until clean. That converts "I think
this passes Sonar" into "the build proves there are 0 Sonar rule violations."

**Caveat:** this proves *rule compliance*, not a full **quality-gate PASS**. The
gate also weighs coverage %, duplication density, new-code conditions, and
security-hotspot review — all computed server-side and **not** enforced by the
analyzer alone. So local-clean ≈ necessary-but-not-sufficient for the real gate.

---

## What `SonarAnalyzer.CSharp` is

- A Roslyn-based static analyzer delivered as a NuGet package by SonarSource,
  from the same [`SonarSource/sonar-dotnet`](https://github.com/SonarSource/sonar-dotnet)
  codebase (470+ C# rules) that powers **SonarQube's** and **SonarLint's** C#
  analysis. The rule IDs are identical (`S1118`, `S3776` cognitive complexity,
  `S2068` hardcoded credentials, `S108` empty block, …).
- Runs **at build time**: every `dotnet build` / `dotnet test` surfaces the rule
  hits as compiler diagnostics (warnings by default).
- **Free to use**, under the *SonarSource Source-Available License v1.0* (note:
  source-available, not OSI-open-source).
- Latest line is `10.x` (e.g. `10.27.x` as of mid-2026); `8.x` exists for older
  toolchains.

When you later run **SonarScanner for .NET** against a real server, the scanner
applies the analyzer according to the server's **quality profile**; Roslyn
issues are reported to SonarQube. Keeping the local NuGet version aligned with
the server's C# plugin version is what makes local findings match the gate (see
*Version alignment*).

---

## Setup (server-free)

### 1. Add the analyzer to every project — `Directory.Build.props` at the repo root

```xml
<Project>
  <ItemGroup>
    <PackageReference Include="SonarAnalyzer.CSharp" Version="10.27.0.140913">
      <PrivateAssets>all</PrivateAssets>
      <IncludeAssets>runtime; build; native; contentfiles; analyzers</IncludeAssets>
    </PackageReference>
  </ItemGroup>

  <PropertyGroup>
    <!-- run analyzers during build -->
    <RunAnalyzersDuringBuild>true</RunAnalyzersDuringBuild>
    <!-- optional: also turn on the built-in .NET analyzers + code style -->
    <AnalysisLevel>latest</AnalysisLevel>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
  </PropertyGroup>
</Project>
```

(`PrivateAssets=all` keeps the analyzer out of the package's runtime
dependencies — it's a build-time-only tool.)

### 2. Decide how findings fail the build

Three escalating options:

- **All warnings → errors** (strictest, also catches non-Sonar warnings):
  ```xml
  <PropertyGroup><TreatWarningsAsErrors>true</TreatWarningsAsErrors></PropertyGroup>
  ```
- **Only specific Sonar rules → errors** (surgical):
  ```xml
  <PropertyGroup><WarningsAsErrors>S2068;S3776;S108</WarningsAsErrors></PropertyGroup>
  ```
- **Per-rule severity via `.editorconfig`** (most precise; mirror the server's
  quality profile here):
  ```ini
  [*.cs]
  dotnet_diagnostic.S3776.severity = error    # cognitive complexity too high
  dotnet_diagnostic.S2068.severity = error    # hardcoded credentials
  dotnet_diagnostic.S1135.severity = none     # ignore "complete the TODO"
  ```

### 3. The verification command the agent runs

```bash
dotnet build -warnaserror        # nonzero exit if any Sonar rule is violated
```

A clean (exit-0) build means **0 SonarAnalyzer rule violations**. Drop
`-warnaserror` to merely *list* them:

```bash
dotnet build 2>&1 | grep -E ' (warning|error) S[0-9]+'
```

---

## How the agent "knows"

The loop is the same discipline as compiling: the agent doesn't *assert*
compliance, it *observes* it.

1. Implement the change.
2. Run `dotnet build -warnaserror`.
3. If it fails on `Sxxxx`, read the rule message + location, fix the underlying
   issue (not suppress it — see below), rebuild.
4. Repeat until the build is clean. Only then is the work done.

**Suppression discipline:** `#pragma warning disable Sxxxx` or
`[SuppressMessage]` should be rare and justified inline — otherwise the agent
games the gate. Treat a suppression like an empty catch: explain *why* it's safe.

---

## What this does NOT give you (bridge to Option #2)

Local analyzer ≠ full SonarQube quality gate. Not covered server-free:

- **Quality-gate computation** (PASS/FAIL against conditions) — server-side only.
- **Coverage thresholds** — needs a coverage report (Coverlet → `opencover`)
  imported into the server; the analyzer doesn't enforce a % locally.
- **Duplication density** — computed/threshold-checked server-side.
- **New-code conditions** ("clean as you code" on the diff) — server-side.
- **Security hotspots review** — a manual server workflow.
- **Custom quality-profile rule selection** — the server's profile decides which
  rules run and at what severity; locally you approximate it via `.editorconfig`.

So: **local-clean is necessary but not sufficient.** It eliminates the rule-level
failures that cause most gate failures, cheaply and offline; the workplace server
(#2) remains the authority for coverage/duplication/new-code.

---

## Version alignment (important)

To make local findings match the workplace gate, **pin `SonarAnalyzer.CSharp` to
the analyzer version the server's C# plugin uses**. A newer local analyzer can
flag rules the server doesn't run yet (false friction); an older one can miss
rules the server fails on (false confidence). Once #2 is checked at work, set the
`Version` in `Directory.Build.props` to match, and mirror the server's quality
profile severities into `.editorconfig`.

---

## Integration with this repo (agent-evals + the agent)

- **Body-eval grading (objective):** set the body loop's
  `--verify-cmd "dotnet build -warnaserror"` (with the analyzer present in the
  seeded project) so **"passes Sonar rules" becomes part of the objective grade**
  — the eval *fails* the agent if its code violates Sonar rules, exactly like it
  already fails on a broken `dotnet test`.
- **Agent body (Option #3, once #1 is proven):** add a short "SonarQube
  compliance + self-verify" section to `principal-dotnet-engineer.md` — the
  high-frequency C# rules (cognitive complexity, dispose `IDisposable`, no empty
  catch, no hardcoded secrets, no `string` concat in loops) so it's
  compliant-by-default, plus the instruction to run `dotnet build -warnaserror`
  and fix `Sxxxx` before declaring done.

---

## Concrete next steps

1. Try the `Directory.Build.props` + `.editorconfig` above on a real .NET repo;
   confirm `dotnet build -warnaserror` surfaces `Sxxxx` and fails on them.
2. Check at the workplace (#2): SonarQube server version → C# plugin/analyzer
   version, and export the active quality profile's rules + severities.
3. Align the NuGet `Version` and `.editorconfig` to (2).
4. If (1) works, do Option #3 (bake rules + self-verify into the agent body) and
   wire `--verify-cmd` into the body eval.

---

## Sources

- [SonarSource/sonar-dotnet (the engine behind both the NuGet and SonarQube)](https://github.com/SonarSource/sonar-dotnet)
- [NuGet — SonarAnalyzer.CSharp](https://www.nuget.org/packages/SonarAnalyzer.CSharp/)
- [Sonar Community — configuring SonarAnalyzer.CSharp in Directory.Build.props](https://community.sonarsource.com/t/sonaranalyzer-csharp-scanning-nugets/105679)
- [SonarQube Server docs — analysis overview & quality gates](https://docs.sonarsource.com/sonarqube-server/analyzing-source-code/analysis-overview)
- [SonarQube Server docs — test/coverage analysis for .NET](https://docs.sonarsource.com/sonarqube-server/latest/analyzing-source-code/dotnet-environments/specify-test-project-analysis/)
- [Enforcing code quality in .NET — analyzers, .editorconfig, pre-commit](https://berkselvi.dev/posts/enforce-code-quality-in-net-editorconfig-analyzers-pre-commit-hooks/)
