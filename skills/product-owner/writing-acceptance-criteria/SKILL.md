---
name: writing-acceptance-criteria
description: >
  Writes SMART, Gherkin-format acceptance criteria for user stories or PRD
  requirements. Covers happy path, negative cases, boundary values, and
  authorization scenarios. Language- and technology-agnostic. Use when a user
  story exists but lacks verifiable acceptance criteria, or when a PO needs to
  define "done" precisely before sprint starts. Trigger keywords: acceptance
  criteria, ACs, definition of done, given when then, Gherkin, test scenarios
  from story, story acceptance, what does done look like, when is this done.
---

## Purpose

Define precisely when a story is complete — in terms a developer can implement against and a QA engineer can test without ambiguity.

## Input

Accept any of:
- User story text (paste or file path)
- Story ID and title (read story file to find it)
- PRD functional requirement
- Direct description: "Write ACs for: [feature behavior]"

Read `.po-workflow-state.json` for product context.

If nothing is provided, ask: "Which user story or requirement needs acceptance criteria?"

## SMART Criteria for ACs

Every acceptance criterion must be:
- **Specific:** Describes one observable behavior, not a category
- **Measurable:** Can be determined pass or fail by a person or test
- **Agreed:** Written before development starts, not after
- **Realistic:** Achievable within the story's scope
- **Testable:** A QA engineer can write an automated or manual test for it

## Gherkin Format

```
Given [precondition — system state or user state before the action],
When [the actor takes a specific action],
Then [observable, measurable outcome — what the user or system sees].
```

**And / But** for additional conditions:
```
Given [precondition]
  And [additional precondition],
When [action],
Then [primary outcome]
  And [secondary outcome]
  But [negative outcome that must NOT occur].
```

## AC Coverage Checklist

For every story, produce ACs covering:

| Scenario Type | Required? | Example |
|---|---|---|
| Happy path | Always | Valid input → success state |
| Invalid input | Always | Missing required field → inline error |
| Boundary values | When numeric or length limits exist | Max length = 255 chars → 255 passes, 256 fails |
| Unauthorized access | When auth is relevant | Non-admin tries admin action → 403 |
| Empty state | When listing or displaying data | No records → empty state message shown |
| Error / failure state | Always | Server error → user-friendly error, data not lost |
| Concurrent action | When race conditions are possible | Two users edit same record → last-write-wins or conflict detected |

## Process

### Step 1 — Parse the Story

Read the story title, persona, value statement, and any existing notes. Identify:
- What action the user takes
- What system state is required before the action
- What the observable outcome must be

### Step 2 — Identify AC Scenarios

List all scenarios before writing Gherkin. Include:
1. Happy path (1 or more paths to success)
2. All invalid input variations that the requirement implies
3. Edge cases based on the data domain (empty, max, boundary)
4. Authorization edge cases (if auth is part of the story)
5. Failure / error recovery cases

### Step 3 — Write Gherkin ACs

Write one Gherkin scenario per AC. Group them under the story ID.

```markdown
## Acceptance Criteria: [US-NNN] [Story Title]

### AC-001: Happy path — [brief scenario name]
**Scenario:** [Short scenario description]
```gherkin
Given [precondition]
When [user action]
Then [expected outcome]
```

### AC-002: Validation — [brief scenario name]
**Scenario:** [Short scenario description]
```gherkin
Given [precondition]
When [user provides invalid input]
Then [error is shown]
  And [user can correct and retry]
  And [no data is lost or partially saved]
```

### AC-003: Authorization — [brief scenario name]
```gherkin
Given [user is not authenticated / does not have permission]
When [user attempts restricted action]
Then [system returns 401 / 403]
  And [user is redirected to login / shown permission error]
```

### AC-004: Empty state — [brief scenario name]
```gherkin
Given [no records exist for the user / filter]
When [user navigates to the list view]
Then [empty state message is displayed]
  And [call-to-action is shown to create first item]
```

### AC-005: Error recovery — [brief scenario name]
```gherkin
Given [user has filled in the form]
  And [server is unavailable]
When [user submits]
Then [user-friendly error message is displayed]
  And [form data is preserved]
  And [user can retry without re-entering data]
```
```

### Step 4 — Append to Story File

If the story file exists, append the ACs under the correct story section.

If no story file exists, write the ACs to a standalone file: `docs/requirements/ac-<story-id>-<date>.md`.

Update `.po-workflow-state.json`:
```json
{
  "current_phase": "acceptance_criteria",
  "last_artifact": "docs/requirements/stories-<epic>-<date>.md",
  "last_updated": "[ISO 8601 timestamp]"
}
```

## Output Quality Rules

1. **Never write ACs after development starts.** If asked to write ACs for code that already exists, flag this and write them anyway — but note they describe discovered behavior, not agreed behavior.
2. **Never use vague outcome language.** "The page loads correctly" → rewrite as "The user is redirected to `/dashboard`".
3. **Cover negative cases.** A story with only happy-path ACs is incomplete.
4. **Keep each AC atomic.** One scenario per criterion. If you need "and" in the Then clause, verify it's the same scenario (not two different outcomes that should be separate ACs).
5. **Reference real values.** Use actual field names, endpoints, error messages, and limits from the PRD rather than placeholders.
