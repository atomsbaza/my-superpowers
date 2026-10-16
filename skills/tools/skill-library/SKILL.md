---
name: skill-library
description: Use when a task needs a specialist playbook that is not in the skills list (.NET/C#, QA process, DDD and architecture, product documents, book references, Kiro-style requirements), or when an agent definition names a skill you cannot see. Read the library index, pick at most two, read them.
---

# Skill Library

Most specialist skills are kept out of the directories that harnesses scan, so they do not cost context in every session. They live in a library and are reached through this one entry. The library is plain files, so any harness that can read files can use it.

## Where

- Library: `~/.agents/skill-library/<skill-name>/SKILL.md` (each entry is a normal skill directory).
- Index: `~/.agents/skill-library/INDEX.md`, one line per skill: name, what it is for, path. It is generated; do not edit it.
- Source of truth: the `my-superpowers` repo, which keeps every skill. Which skills are in the library is decided by `tools/skill-library/library.txt` there.

## Use it

1. Search the index for the task's keywords (`grep -i <keyword> ~/.agents/skill-library/INDEX.md`), or read it whole when unsure. It is short.
2. Pick at most two entries. More than two means the task is not yet framed; frame it first.
3. Read each chosen `SKILL.md` (and any file it points to) and follow it exactly as if it were listed.
4. If nothing fits, say so and continue without a playbook. Do not invent a skill name.
5. If an agent definition tells you to use a skill that is not in your list, look it up here before concluding it does not exist.

## Rules

- Read library skills in place. Do not copy them into a scanned directory for one task.
- A skill used more than a few times belongs in the listed set: remove its line from `library.txt` in the repo and run `python3 tools/skill-library/skill_library.py apply --apply`.
- Nothing in the library is deleted by the tool. Moving a skill in or out only moves its directory.

## Not a ranking

The library holds skills that are rarely needed on this machine, not skills that are worse. Which skill suits a task is decided from the index entry and the task, by whoever is doing the work.
