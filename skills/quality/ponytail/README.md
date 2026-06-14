# ponytail

> The best code is the code never written.

A Claude Code skill that forces the laziest solution that actually works. Before writing anything, it walks a YAGNI-first decision ladder: does this need to exist? stdlib? native platform feature? existing dep? one liner? — and only then writes the minimum code.

Source: [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) · MIT license · pinned: v4.2.0 (June 2026)

## Intensity levels

| Level | Behavior |
|-------|----------|
| `lite` | Builds what's asked, names the lazier alternative as a comment |
| `full` | Enforces the ladder. Stdlib and native first. Default. |
| `ultra` | YAGNI extremist. Challenges the requirement before writing anything. |

Switch with `/ponytail lite`, `/ponytail full`, `/ponytail ultra`.  
Disable with `stop ponytail` or `normal mode`.

## The `ponytail:` comment

When a deliberate simplification is made, the skill marks it inline:

```python
# ponytail: global lock, per-account locks if throughput matters
```

This signals intent, not ignorance — you know the ceiling and the upgrade path.

## Never simplified away

Input validation, error handling that prevents data loss, security, accessibility, and anything explicitly requested.

## Installation

Globally active via `~/.claude/skills/ponytail/SKILL.md`.  
This copy is kept in the repo so the team can track the version in git.
