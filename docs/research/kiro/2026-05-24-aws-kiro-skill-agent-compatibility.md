# Research: AWS Kiro skill and agent compatibility

## Summary

AWS Kiro is an agentic IDE that uses three core mechanisms — **Specs**, **Steering**, and **Agent Skills** — to guide AI-assisted development. Kiro's Agent Skills system is built on the open **AgentSkills standard** (published at agentskills.io), which uses the same `SKILL.md` file format that Claude Code, Codex CLI, Gemini CLI, GitHub Copilot, Cursor, and Windsurf support. This means a well-formed skill written for Claude Code can, in principle, be dropped into Kiro's `.kiro/skills/` directory and work without modification. The obra/superpowers framework has also been adapted for Kiro, though the preferred integration approach uses Kiro's native skill system rather than converting skills to steering files.

---

## Key Findings

**1. Kiro is a full agentic IDE with three distinct layered systems**
- Kiro launched in mid-2025 and evolved rapidly into a production IDE with specs, steering, hooks, and agent skills as first-class concepts. [Kiro official site](https://kiro.dev/)

**2. Agent Skills use the open AgentSkills standard — the same format as Claude Code**
- The SKILL.md format is an open standard originally developed by Anthropic and published at agentskills.io. Kiro adopted it natively. Required frontmatter fields are `name` (max 64 chars, lowercase/hyphens) and `description` (max 1,024 chars). Optional fields include `license`, `compatibility`, `metadata`, and `allowed-tools`. [AgentSkills specification](https://agentskills.io/specification)

**3. Kiro loads skills from `.kiro/skills/[skill-name]/SKILL.md` (workspace) or `~/.kiro/skills/` (global)**
- Skills must live in a named subfolder, not directly in the skills root. The structure mirrors Claude Code's pattern. Workspace skills take priority over global skills on name conflict. [Kiro Agent Skills docs](https://kiro.dev/docs/skills/)

**4. Skills are invoked automatically (by description match) or manually via `/skill-name` slash command**
- Kiro uses progressive disclosure: descriptions load at startup, full SKILL.md body loads on activation, scripts/references load only as needed during execution. [Kiro Agent Skills docs](https://kiro.dev/docs/skills/)

**5. Steering files are a separate, distinct concept from skills**
- Steering files live in `.kiro/steering/` and are always-on context documents, not on-demand workflows. They are not skills. [Kiro Steering docs](https://kiro.dev/docs/steering/) | [DEV Community comparison](https://dev.to/aws-builders/aws-differences-between-kiro-steering-and-agentskills-kiro-5f3i)

**6. Hooks are event-driven automations, separate from both skills and steering**
- Hooks fire on IDE events (file save, file create, commit) and trigger agent workflows automatically — analogous to GitHub Actions for local development. [Kiro walkthrough](https://dev.to/alizgheib/kiro-from-steering-docs-to-specs-to-hooks-an-agentic-ide-walkthrough-3nbf)

**7. obra/superpowers skills are cross-compatible with Kiro**
- The community confirmed all core superpowers workflows work in Kiro. Recommended: place SKILL.md files in `.kiro/skills/` — do NOT convert them to steering files. [superpowers PR #363](https://github.com/obra/superpowers/pull/363)

**8. A cross-tool community repo confirms identical SKILL.md files work across Kiro, Claude Code, Cursor, Windsurf**
- [fabricioctelles/skills](https://github.com/fabricioctelles/skills)

---

## Trade-offs / Caveats

- **Steering vs. Skills conflation risk**: Skills and steering are architecturally different in Kiro. Don't convert SKILL.md files to steering files — that's an anti-pattern.
- **"Kiro Powers" ≠ "Agent Skills"**: Powers are curated MCP+steering bundles from a registry, not SKILL.md files and not portable to Claude Code.
- **`allowed-tools` field is experimental**: Support varies between tools — don't rely on it for cross-tool portability.
- **Claude Code `Skill` tool vs Kiro slash command**: Claude Code uses a dedicated `Skill` tool invocation; Kiro uses `/skill-name` slash commands. Skills relying on Claude Code's specific invocation pattern may need documentation updates for Kiro users.
- **Agents (`.claude/agents/`) have no Kiro equivalent**: Agent definition files are Claude Code–specific and won't port to Kiro.

---

## Sources

- [Kiro official site](https://kiro.dev/)
- [Agent Skills — Kiro docs](https://kiro.dev/docs/skills/)
- [Steering — Kiro docs](https://kiro.dev/docs/steering/)
- [AgentSkills open standard](https://agentskills.io/specification)
- [DEV: Steering vs AgentSkills](https://dev.to/aws-builders/aws-differences-between-kiro-steering-and-agentskills-kiro-5f3i)
- [obra/superpowers PR #363 — Kiro support](https://github.com/obra/superpowers/pull/363)
- [fabricioctelles/skills — cross-tool repo](https://github.com/fabricioctelles/skills)
- [VentureBeat: Kiro Powers](https://venturebeat.com/ai/aws-launches-kiro-powers-with-stripe-figma-and-datadog-integrations-for-ai)
