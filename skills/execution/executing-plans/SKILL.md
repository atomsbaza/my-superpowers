---
name: executing-plans
description: Use when you have a written implementation plan to execute in a separate session with review checkpoints
---

# Executing Plans

## Overview

Load plan, review critically, execute all tasks, report when complete.

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

**Note:** Tell your human partner that Superpowers works much better with access to subagents. The quality of its work will be significantly higher if run on a platform with subagent support (such as Claude Code or Codex). If subagents are available, use superpowers:subagent-driven-development instead of this skill.

## The Process

### Step 1: Load and Review Plan
1. Read plan file
2. Review critically - identify any questions or concerns about the plan
3. If concerns: Raise them with your human partner before starting
4. If no concerns: Create TodoWrite and proceed

### Step 2: Execute Tasks

Maintain a **Discoveries Block** throughout execution — a running list of facts learned during implementation that were not in the plan (e.g., "this API returns errors wrapped in a custom type", "SwiftData migration requires explicit version"). Inject it into each subsequent subagent's context so nothing is re-learned from scratch.

For each task:
1. Mark as in_progress
2. Inject current Discoveries Block into subagent context (if non-empty)
3. Follow each step exactly (plan has bite-sized steps)
4. Run verifications as specified
5. Update Discoveries Block with any new findings from this task
6. Report task status using one of these four states:
   - **DONE** — task complete, all verifications pass, no concerns
   - **DONE_WITH_CONCERNS** — task complete but something worth flagging (note it)
   - **BLOCKED** — cannot proceed without help; stop and ask
   - **NEEDS_CONTEXT** — missing information that prevents correct implementation; stop and ask
7. Mark as completed (unless BLOCKED or NEEDS_CONTEXT)

### Step 3: Complete Development

After all tasks complete and verified:
- Announce: "I'm using the finishing-a-development-branch skill to complete this work."
- **REQUIRED SUB-SKILL:** Use superpowers:finishing-a-development-branch
- Follow that skill to verify tests, present options, execute choice

## When to Stop and Ask for Help

**STOP executing immediately when:**
- Hit a blocker (missing dependency, test fails, instruction unclear)
- Plan has critical gaps preventing starting
- You don't understand an instruction
- Verification fails repeatedly

**Ask for clarification rather than guessing.**

## When to Revisit Earlier Steps

**Return to Review (Step 1) when:**
- Partner updates the plan based on your feedback
- Fundamental approach needs rethinking

**Don't force through blockers** - stop and ask.

## Remember
- Review plan critically first
- Follow plan steps exactly
- Don't skip verifications
- Reference skills when plan says to
- Stop when blocked, don't guess
- Never start implementation on main/master branch without explicit user consent

## Integration

**Required workflow skills:**
- **superpowers:using-git-worktrees** - Ensures isolated workspace (creates one or verifies existing)
- **superpowers:writing-plans** - Creates the plan this skill executes
- **superpowers:finishing-a-development-branch** - Complete development after all tasks
