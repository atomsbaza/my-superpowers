#!/usr/bin/env python3
"""Safely move listed skills into a non-scanned skill library."""

import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import re
import shutil
import sys
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
RESERVED_NAMES = {"skill-library"}
SKILL_FILE = "SKILL.md"


@dataclass(frozen=True)
class Config:
    home: Path
    library_file: Path
    repo_skills: Path
    scan_dirs: Tuple[Path, ...]
    library_dir: Path


@dataclass(frozen=True)
class Plan:
    actions: Tuple[Tuple[str, Path, Path], ...]
    warnings: Tuple[str, ...]
    trash_timestamp: str


class UserInputError(Exception):
    pass


def parse_args(argv: Sequence[str]) -> Tuple[Config, str, bool]:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--library-file", type=Path, default=None)
    parser.add_argument("--repo-skills", type=Path, default=None)
    parser.add_argument("--scan-dir", type=Path, action="append", default=[])
    parser.add_argument("--library-dir", type=Path, default=None)
    parser.add_argument("command", choices=("status", "apply", "index"))
    parser.add_argument("--apply", action="store_true", help="perform apply instead of dry-run")
    args = parser.parse_args(argv)

    script_dir = Path(__file__).resolve().parent
    home = resolve_path(args.home)
    library_file = args.library_file or script_dir / "library.txt"
    repo_skills = args.repo_skills or script_dir.parents[1] / "skills"
    unique_scan_dirs = dict.fromkeys(
        resolve_path(path)
        for path in (args.scan_dir or (home / ".claude" / "skills", home / ".agents" / "skills"))
    )
    scan_dirs = tuple(unique_scan_dirs)
    library_dir = resolve_path(args.library_dir or home / ".agents" / "skill-library")
    config = Config(home, resolve_path(library_file), resolve_path(repo_skills), scan_dirs, library_dir)
    validate_config(config)
    return config, args.command, args.apply


def resolve_path(path: Path) -> Path:
    return Path(os.path.abspath(os.path.expanduser(str(path))))


def validate_config(config: Config) -> None:
    for directory in config.scan_dirs:
        if directory.is_symlink():
            raise UserInputError(f"scan dir may not be a symlink: {directory}")
        if is_inside(config.library_dir, directory) or is_inside(directory, config.library_dir):
            raise UserInputError(f"scan and library dirs overlap: {directory}, {config.library_dir}")
    if config.library_dir.is_symlink():
        raise UserInputError(f"library dir may not be a symlink: {config.library_dir}")
    if config.repo_skills.is_symlink():
        raise UserInputError(f"repo skills dir may not be a symlink: {config.repo_skills}")


def is_inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def read_names(path: Path) -> List[str]:
    names = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, 1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            names.append(line)
    return names


def validate_names(names: Iterable[str]) -> List[str]:
    errors = []
    for name in names:
        if name in RESERVED_NAMES:
            errors.append(f"skill name refused: {name}")
        elif not NAME_PATTERN.fullmatch(name):
            errors.append(f"invalid name: {name!r}")
    return errors


def is_skill_dir(path: Path) -> bool:
    return path.is_dir() and not path.is_symlink() and (path / SKILL_FILE).is_file()


def tree_has_symlink(path: Path) -> bool:
    for current, dirs, files in os.walk(path, followlinks=False):
        current_path = Path(current)
        entries = dirs + files
        if any((current_path / entry).is_symlink() for entry in entries):
            return True
    return False


def find_repo_skill(repo_skills: Path, name: str) -> Optional[Path]:
    if not repo_skills.is_dir():
        return None
    candidates = []
    for root, dirs, files in os.walk(repo_skills, followlinks=False):
        root_path = Path(root)
        retained = []
        for dirname in sorted(dirs):
            child = root_path / dirname
            if child.is_symlink():
                continue
            retained.append(dirname)
        dirs[:] = retained
        if root_path.name == name and SKILL_FILE in files:
            skill_file = root_path / SKILL_FILE
            if not skill_file.is_symlink() and skill_file.is_file():
                candidates.append(root_path)
    return sorted(candidates, key=lambda path: (len(path.parts), str(path)))[0] if candidates else None


def scan_label(scan_dir: Path, home: Path) -> str:
    try:
        relative = scan_dir.relative_to(home)
    except ValueError:
        relative = Path(scan_dir.name)
    return "__".join(part for part in relative.parts) or scan_dir.name


def file_manifest(root: Path) -> Optional[Dict[str, str]]:
    manifest = {}
    try:
        for current, dirs, files in os.walk(root, followlinks=False):
            current_path = Path(current)
            for dirname in dirs:
                if (current_path / dirname).is_symlink():
                    manifest[str((current_path / dirname).relative_to(root))] = "symlink"
            dirs[:] = [name for name in dirs if not (current_path / name).is_symlink()]
            for filename in files:
                path = current_path / filename
                relative = str(path.relative_to(root))
                if path.is_symlink():
                    manifest[relative] = "symlink:" + os.readlink(path)
                elif path.is_file():
                    manifest[relative] = "file:" + path.read_bytes().hex()
                else:
                    manifest[relative] = "special"
    except OSError as error:
        print(f"warning: cannot read skill tree {root}: {error}", file=sys.stderr)
        return None
    return manifest


def same_tree(left: Path, right: Path) -> bool:
    left_manifest = file_manifest(left)
    right_manifest = file_manifest(right)
    return left_manifest is not None and left_manifest == right_manifest


def timestamp_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def unique_path(path: Path) -> Path:
    if not (path.exists() or path.is_symlink()):
        return path
    for number in range(1, 1000):
        candidate = path.with_name(path.name + f"-{number}")
        if not (candidate.exists() or candidate.is_symlink()):
            return candidate
    raise UserInputError(f"cannot choose an unused trash path for {path}")


def make_plan(config: Config, names: Sequence[str]) -> Plan:
    errors = validate_names(names)
    if errors:
        return Plan((), tuple(errors), timestamp_now())

    actions = []
    warnings = []
    trash_timestamp = timestamp_now()
    used_labels = set()
    missing_scan_dirs = []

    for scan_dir in config.scan_dirs:
        if not scan_dir.exists():
            missing_scan_dirs.append(scan_dir)

    for name in names:
        sources = []
        for scan_dir in config.scan_dirs:
            candidate = scan_dir / name
            if candidate.is_symlink():
                warnings.append(f"skipping symlink in scan dir: {candidate}")
            elif is_skill_dir(candidate) and tree_has_symlink(candidate):
                warnings.append(f"skipping skill containing symlink: {candidate}")
            elif is_skill_dir(candidate):
                sources.append(candidate)
        target = config.library_dir / name
        target_exists = is_skill_dir(target)

        if not target_exists:
            if sources:
                actions.append(("move", sources[0], target))
                trash_sources = sources[1:]
            else:
                repo_skill = find_repo_skill(config.repo_skills, name)
                if repo_skill is None:
                    warnings.append(f"missing source for {name} (not in scan dirs or repo)")
                    continue
                actions.append(("copy", repo_skill, target))
                trash_sources = []
        else:
            trash_sources = sources

        for source in trash_sources:
            source_dir = source.parent
            label = scan_label(source_dir, config.home)
            original_label = label
            number = 2
            while label in used_labels:
                label = f"{original_label}-{number}"
                number += 1
            used_labels.add(label)
            label_base = unique_path(config.library_dir / ".trash" / trash_timestamp / label)
            compare_target = target if target_exists else actions[-1][1]
            if same_tree(source, compare_target):
                reason = "trash"
            else:
                reason = "trash-different"
                warnings.append(
                    f"contents differed for {name} in {source}; preserving in trash"
                )
            actions.append((reason, source, label_base / name))

    for scan_dir in missing_scan_dirs:
        warnings.append(f"scan dir does not exist: {scan_dir}")

    if config.library_dir.exists() and not config.library_dir.is_dir():
        raise UserInputError(f"library path is not a directory: {config.library_dir}")
    actions.append(("index", config.library_dir / "INDEX.md", config.library_dir))
    return Plan(tuple(actions), tuple(warnings), trash_timestamp)


def safe_move_directory(source: Path, target: Path) -> None:
    if source.is_symlink() or not source.is_dir():
        raise UserInputError(f"refusing to move non-directory: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        raise UserInputError(f"refusing to overwrite target: {target}")
    os.replace(source, target)


def safe_copy_directory(source: Path, target: Path) -> None:
    if source.is_symlink() or not source.is_dir():
        raise UserInputError(f"refusing to copy non-directory: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        raise UserInputError(f"refusing to overwrite target: {target}")
    shutil.copytree(source, target, symlinks=True)


def execute_plan(plan: Plan) -> None:
    for action, source, target in plan.actions:
        if action == "move":
            safe_move_directory(source, target)
        elif action == "copy":
            safe_copy_directory(source, target)
        elif action in ("trash", "trash-different"):
            safe_move_directory(source, target)
        elif action == "index":
            write_index(target, source)


def parse_frontmatter(path: Path) -> Tuple[Optional[str], Optional[str]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return None, None
    if not lines or lines[0].strip() != "---":
        return None, None
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration:
        return None, None

    values = {}
    index = 1
    while index < end:
        line = lines[index]
        match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):(.*)$", line)
        if match:
            key = match.group(1).lower()
            value = match.group(2).strip()
            if value in (">", "|", ">-", "|-", ">+", "|+"):
                block = []
                index += 1
                while index < end and (not lines[index].strip() or lines[index].startswith((" ", "\t"))):
                    if lines[index].strip():
                        block.append(lines[index].strip())
                    index += 1
                values[key] = " ".join(block)
                continue
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                quote = value[0]
                value = value[1:-1].replace("\\" + quote, quote).replace("\\\\", "\\")
            values[key] = value
        index += 1
    return values.get("name"), values.get("description")


def collapse_description(description: str) -> str:
    collapsed = " ".join(description.split())
    if len(collapsed) > 140:
        return collapsed[:140] + "..."
    return collapsed


def write_index(library_dir: Path, output: Path) -> None:
    entries = []
    if library_dir.is_dir():
        for child in sorted(library_dir.iterdir(), key=lambda path: path.name):
            if child.name.startswith(".") or not is_skill_dir(child):
                continue
            name, description = parse_frontmatter(child / SKILL_FILE)
            entries.append(
                (
                    child.name,
                    name or child.name,
                    collapse_description(description or ""),
                    child.relative_to(library_dir) / SKILL_FILE,
                )
            )
    entries.sort(key=lambda entry: entry[0])
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("<!-- Generated by skill_library.py. Do not edit. -->\n")
        for _, name, description, path in entries:
            handle.write(f"- {name} | {description} | {path}\n")
    os.replace(temporary, output)


def library_locations(config: Config, name: str) -> Dict[str, object]:
    scan_matches = [scan_dir / name for scan_dir in config.scan_dirs if is_skill_dir(scan_dir / name)]
    library = config.library_dir / name
    repo = find_repo_skill(config.repo_skills, name)
    return {
        "scan": scan_matches,
        "library": library if is_skill_dir(library) else None,
        "repo": repo,
    }


def run_status(config: Config) -> int:
    names = read_names(config.library_file)
    errors = validate_names(names)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    counts = {"library": 0, "scan": 0, "repo-only": 0, "nowhere": 0}
    for name in names:
        locations = library_locations(config, name)
        scan_matches = locations["scan"]
        if scan_matches:
            state = "scan"
            counts["scan"] += 1
        elif locations["library"]:
            state = "library"
            counts["library"] += 1
        elif locations["repo"]:
            state = "repo-only"
            counts["repo-only"] += 1
        else:
            state = "nowhere"
            counts["nowhere"] += 1
        parts = []
        for label in ("scan", "library", "repo"):
            value = locations[label]
            if label == "scan":
                parts.extend(f"scan={path}" for path in value)
            elif value:
                parts.append(f"{label}={locations[label]}")
        print(f"{name}: {state}" + (("; " + "; ".join(parts)) if parts else ""))
    print("counts: " + " ".join(f"{key}={value}" for key, value in counts.items()))
    return 0


def run_apply(config: Config, apply: bool) -> int:
    names = read_names(config.library_file)
    errors = validate_names(names)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    plan = make_plan(config, names)
    prefix = "apply" if apply else "dry-run"
    for action, source, target in plan.actions:
        if action == "move":
            print(f"[{prefix}] move {source} -> {target}")
        elif action == "copy":
            print(f"[{prefix}] copy {source} -> {target}")
        elif action == "trash":
            print(f"[{prefix}] trash identical copy {source} -> {target}")
        elif action == "trash-different":
            print(f"[{prefix}] trash differing copy {source} -> {target}")
        else:
            print(f"[{prefix}] regenerate {target}")
    for warning in plan.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    if apply and plan.actions:
        execute_plan(plan)
    return 2 if plan.warnings else 0


def run_index(config: Config) -> int:
    output = config.library_dir / "INDEX.md"
    try:
        write_index(config.library_dir, output)
    except OSError as error:
        print(f"warning: cannot write index {output}: {error}", file=sys.stderr)
        return 2
    print(f"wrote {output}")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    try:
        config, command, apply = parse_args(sys.argv[1:] if argv is None else argv)
        if command == "status":
            return run_status(config)
        if command == "apply":
            return run_apply(config, apply)
        return run_index(config)
    except (UserInputError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
