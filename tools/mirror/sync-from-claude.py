#!/usr/bin/env python3
"""Mirror ~/.claude/agents/*.md into the `agents` map of opencode.json.

Re-runnable: only the `agents` key is rewritten; every other key is kept.
Claude-only agents (SKIP) are left out. A Claude `tools` line is an allowlist:
unlisted edit/shell/web/read tools are denied. No `tools` line = all tools (as Claude).
"""
import glob, json, os, re

HOME = os.path.expanduser("~")
CFG = os.path.join(HOME, ".config/opencode/opencode.json")
SRC = os.path.join(HOME, ".claude/agents")
SKIP = {"haiku-engineer", "qa-execution-operator"}  # engineer joined the OpenCode workflow 2026-10-17 (IMPLEMENT stage)
TOOL_ACTION = {"Read": "read", "Grep": "grep", "Glob": "glob", "Write": "edit", "Edit": "edit",
               "MultiEdit": "edit", "NotebookEdit": "edit", "Bash": "shell",
               "WebFetch": "webfetch", "WebSearch": "websearch"}
GATED = ["read", "grep", "glob", "edit", "shell", "webfetch", "websearch"]

# Skill / MCP hardening (2026-10-16). Appended AFTER the generic rules so the
# last matching rule wins. Baseline is `* allow`, so mapping = explicit denies.
# Memory writes stay with interactive/orchestrator sessions only — a subagent
# fed web content must never write memory (injection channel).
MCP_ALWAYS_DENY = ["my-memory_*", "drawdy_*", "figcraft_*", "figcraft-live_*"]
# XcodeBuildMCP stays available to: debugger (logs/LLDB), quality-engineering
# (test runs), devops-engineer (build automation).
XCODE_DENY = [
    "code-reviewer", "swift-reviewer", "ui-reviewer", "security-engineer",
    "research", "solution-architect", "tech-lead", "api-designer",
    "ai-engineer", "data-engineer", "docs", "wiki-updater", "sre",
    "qa-incident-investigator", "qa-requirements-risk-analyst", "qa-test-architect",
    "performance-reviewer", "dependency-reviewer", "web-ui-reviewer",
    "architect-reviewer",
]
# Only agents whose prompts never load skills. Removed over time as prompts
# gained skill references: swift-reviewer (domain skills), then tech-lead /
# docs / research / ui-reviewer (2026-10-16 skill-gap pass). code-reviewer
# (scrutinize), debugger (diagnose, test-verdict-triage) and the
# qa/security/architect/sre/data/ai group keep skill access. engineer was
# removed 2026-10-17: it loads taste-skill for public-facing web pages.
SKILL_DENY = ["api-designer", "wiki-updater",
              "performance-reviewer", "dependency-reviewer"]
# Review roles report findings only — the implementer applies fixes. (Agents
# without a Claude `tools:` line get all tools; this pins them read-only.)
# debugger stays full-tools: it fixes and verifies bugs.
READ_ONLY = ["code-reviewer", "swift-reviewer", "ui-reviewer",
             "performance-reviewer", "dependency-reviewer", "web-ui-reviewer",
             "architect-reviewer"]
# wiki-updater writes vault files by design but never runs commands.
NO_SHELL = ["wiki-updater"]
# Artifact stages must write their handoff files (research.md / design.md /
# plan.md) but nothing else. Appended AFTER the edit deny, so the scoped
# allow wins for this path only — last matching rule wins.
ARTIFACT_WRITERS = ["research", "solution-architect", "tech-lead"]
WORKFLOW_DIR = "docs/workflow/*"
# Playwright MCP (browser automation) is for roles that build or verify web
# behavior. Everyone else gets playwright_* denied.
PLAYWRIGHT_ALLOW = ["engineer", "web-ui-reviewer", "debugger",
                    "quality-engineering", "devops-engineer"]
# Per-agent model pins (OpenCode Go Plus, provider opencode-go) — chosen from
# the 2026-10-17 model research (benchmarks + Go Plus rate limits). Unlisted
# agents inherit the session model. See docs/opencode-workflow-setup.md §12.
MODEL = {
    "research": "opencode-go/deepseek-v4.1-flash",
    "solution-architect": "opencode-go/qwen3.8-max",
    "architect-reviewer": "opencode-go/qwen3.8-max",
    "tech-lead": "opencode-go/glm-5.2",
    "engineer": "opencode-go/kimi-k2.7-code",
    "code-reviewer": "opencode-go/claude-haiku-5-5",
    "swift-reviewer": "opencode-go/claude-haiku-5-5",
    "security-engineer": "opencode-go/claude-haiku-5-5",
    "performance-reviewer": "opencode-go/claude-haiku-5-5",
    "dependency-reviewer": "opencode-go/claude-haiku-5-5",
    "web-ui-reviewer": "opencode-go/claude-haiku-5-5",
    "quality-engineering": "opencode-go/glm-5.3-flash",
    "debugger": "opencode-go/glm-5.3",
    "docs": "opencode-go/deepseek-v4.1-flash",
    "wiki-updater": "opencode-go/mimo-v2.6-flash",
}


def hardening(name):
    rules = [rule(a, "deny") for a in MCP_ALWAYS_DENY]
    if name in XCODE_DENY:
        rules.append(rule("XcodeBuildMCP_*", "deny"))
    if name in SKILL_DENY:
        rules.append(rule("skill", "deny"))
    if name in READ_ONLY:
        rules += [rule("edit", "deny"), rule("shell", "deny")]
    if name in NO_SHELL:
        rules.append(rule("shell", "deny"))
    if name in ARTIFACT_WRITERS:
        rules.append(rule("edit", "allow", WORKFLOW_DIR))
    if name not in PLAYWRIGHT_ALLOW:
        rules.append(rule("playwright_*", "deny"))
    return rules


def frontmatter(text):
    head, body = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S).groups()
    fields, key = {}, None
    for line in head.splitlines():
        if line[:1] not in (" ", "\t") and ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            fields[key] = val.strip()
        elif key:
            cur = fields[key]
            fields[key] = line.strip() if cur in (">", "|", "") else cur + " " + line.strip()
    return fields, body.strip()


def rule(action, effect, resource="*"):
    return {"action": action, "resource": resource, "effect": effect}


def permissions(name, tools):
    rules = [rule("*", "allow"), rule("read", "ask", "*.env"),
             rule("read", "ask", "*.env.*"), rule("read", "allow", "*.env.example")]
    if tools:
        listed = {TOOL_ACTION[t] for t in re.split(r",\s*", tools) if t in TOOL_ACTION}
        rules += [rule(a, "deny") for a in GATED if a not in listed]
    return rules + [rule("subagent", "deny")] + hardening(name)


def main():
    cfg = json.load(open(CFG, encoding="utf-8"))
    agents = {}
    for path in sorted(glob.glob(os.path.join(SRC, "*.md"))):
        fields, body = frontmatter(open(path, encoding="utf-8").read())
        if fields["name"] in SKIP:
            continue
        agents[fields["name"]] = (fields["description"], body, permissions(fields["name"], fields.get("tools")))
    lines = []
    for name, (desc, body, rules) in agents.items():
        lines += [f"    {json.dumps(name)}: {{",
                  f'      "description": {json.dumps(desc, ensure_ascii=False)},',
                  '      "mode": "subagent",']
        if name in MODEL:
            lines.append(f'      "model": {json.dumps(MODEL[name])},')
        lines += [f'      "system": {json.dumps(body, ensure_ascii=False)},',
                  f'      "permissions": [{", ".join(json.dumps(r) for r in rules)}]',
                  "    },"]
    lines[-1] = "    }"
    rest = {k: v for k, v in cfg.items() if k != "agents"}
    text = json.dumps(rest, indent=2, ensure_ascii=False)[:-2]
    text += ',\n  "agents": {\n' + "\n".join(lines) + "\n  }\n}\n"
    json.loads(text)
    tmp = CFG + ".tmp"
    open(tmp, "w", encoding="utf-8").write(text)
    os.replace(tmp, CFG)
    print(f"agents written: {len(agents)}; skipped: {sorted(SKIP)}")


if __name__ == "__main__":
    main()
