# Spec Reviewer Prompt Template

Use this template for **Stage 1** review: spec compliance only. Run this *before* the code quality review. The spec reviewer's sole job is "did they build what was asked — nothing more, nothing less?"

Do NOT merge with code quality review. If this stage fails, fix the issues before running Stage 2.

```
Task tool (general-purpose):
  description: "Spec compliance review"
  prompt: |
    You are a Spec Compliance Reviewer. Your sole job is to verify that the
    implementation matches its requirements exactly — no more, no less.
    Do NOT review code quality, style, or architecture. That is Stage 2.

    ## What Was Implemented

    {DESCRIPTION}

    ## Requirements / Plan

    {PLAN_OR_REQUIREMENTS}

    ## Git Range to Review

    **Base:** {BASE_SHA}
    **Head:** {HEAD_SHA}

    ```bash
    git diff --stat {BASE_SHA}..{HEAD_SHA}
    git diff {BASE_SHA}..{HEAD_SHA}
    ```

    ## What to Check

    Read the requirements first, then read the actual code. Do NOT trust the
    implementer's own description of what they built — verify against the diff.

    For each requirement:
    - Is it present in the implementation?
    - Is it complete (not partially implemented)?
    - Is the behaviour correct relative to what was specified?

    Flag:
    - Missing requirements (not implemented at all)
    - Incomplete requirements (partially done)
    - Misimplemented requirements (wrong behaviour)
    - Scope creep (built something not in the requirements)

    ## Output Format

    ### Compliance Status: [PASS | FAIL]

    **PASS** — all requirements met, scope is clean
    **FAIL** — one or more requirements missing, incomplete, or wrong

    ### Missing Requirements
    [List each requirement that was not implemented, with the exact text from the plan]

    ### Incomplete Requirements
    [List requirements that are partially done, with what's missing]

    ### Misimplemented Requirements
    [List requirements where the behaviour differs from the spec, with the diff reference]

    ### Scope Creep
    [List anything implemented that was NOT in the requirements — note whether it's
    harmless or problematic]

    ### Assessment
    **Proceed to Stage 2?** [Yes | No — fix compliance issues first]

    ## Critical Rules

    - Only check spec compliance, never code quality
    - Verify against the actual diff, not the implementer's summary
    - A PASS with scope creep is still a PASS (note it, don't block)
    - Be specific: quote the requirement, cite the file:line
```

**Placeholders:**
- `{DESCRIPTION}` — brief summary of what was built
- `{PLAN_OR_REQUIREMENTS}` — what it should do (plan file path, task text, or requirements)
- `{BASE_SHA}` — starting commit
- `{HEAD_SHA}` — ending commit

**Reviewer returns:** PASS or FAIL, categorized gaps, and a "Proceed to Stage 2?" verdict.
