"""Safe writer for the Kiro Crew markdown memory. Run with Kiro Crew's own interpreter:

  PY=/Applications/KiroCrew.app/Contents/Resources/backend-dist/kirocrew-backend-arm64/bin/python3.12
  $PY -s -P kc_memory.py backup [tag]
  $PY -s -P kc_memory.py log        < entry.md     # append to workspace/learning-log.md
  $PY -s -P kc_memory.py project    < section.md   # replace/insert one `## ` section of memory/projects.md

`project` takes the FULL new section (first line is its `## ` heading). The existing section with the same
leading text (before the first " (" or " —" date marker) is replaced; otherwise the section is inserted before
`## Archive`. The write is a compare-and-swap through MemoryStore.write_projects, so a concurrent change makes
it exit 3 instead of overwriting. Nothing here touches the SQLite stores or credential folders.
"""
import shutil
import sys
import time
from pathlib import Path

WORKSPACE = Path.home() / ".kiro" / "crew" / "workspace"
LOG = WORKSPACE / "learning-log.md"
PROJECTS = WORKSPACE / "memory" / "projects.md"


def backup(tag: str = "claude") -> Path:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    dest = WORKSPACE / "backups" / f"{tag}-{stamp}"
    n = 1
    while dest.exists():  # two writes in the same second must not overwrite the earlier backup
        n += 1
        dest = WORKSPACE / "backups" / f"{tag}-{stamp}-{n}"
    dest.mkdir(parents=True)
    for source in (LOG, PROJECTS):
        shutil.copy2(source, dest / source.name)
    return dest


def heading_key(line: str) -> str:
    text = line.lstrip("#").strip()
    for marker in (" (", " —", " --"):
        if marker in text:
            text = text.split(marker)[0]
    return text.strip()


def replace_section(current: str, section: str) -> str:
    section = section.strip("\n") + "\n"
    first = section.splitlines()[0]
    if not first.startswith("## "):
        sys.exit("section must start with a '## ' heading")
    key = heading_key(first)
    lines = current.splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if line.startswith("## ")]
    for n, start in enumerate(starts):
        if heading_key(lines[start]) == key:
            end = starts[n + 1] if n + 1 < len(starts) else len(lines)
            return "".join(lines[:start]) + section + "\n" + "".join(lines[end:])
    for start in starts:
        if lines[start].strip() == "## Archive":
            return "".join(lines[:start]) + section + "\n" + "".join(lines[start:])
    return current.rstrip("\n") + "\n\n" + section


def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command == "backup":
        print(backup(sys.argv[2] if len(sys.argv) > 2 else "claude"))
        return 0
    text = sys.stdin.read()
    if not text.strip():
        sys.exit("nothing on stdin")
    if command == "log":
        print("backup:", backup())
        existing = LOG.read_text(encoding="utf-8")
        separator = "" if existing.endswith("\n") else "\n"
        LOG.write_text(existing + separator + "\n" + text.strip("\n") + "\n", encoding="utf-8")
        return 0
    if command == "project":
        from kiro_crew.memory import MemoryStore

        print("backup:", backup())
        store = MemoryStore()
        current = store.read_projects()
        if not store.write_projects(replace_section(current, text), expected_baseline=current):
            print("projects.md changed while writing; nothing was written. Re-run.", file=sys.stderr)
            return 3
        return 0
    sys.exit(__doc__)


if __name__ == "__main__":
    raise SystemExit(main())
