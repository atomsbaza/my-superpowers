#!/usr/bin/env python3
"""Integration tests for the safe skill-library tool."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("skill_library.py")


class SkillLibraryTestCase(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="skill-library-test-"))
        self.home = self.root / "home"
        self.repo_skills = self.root / "repo-skills"
        self.library_file = self.root / "library.txt"
        self.library_dir = self.home / ".agents" / "skill-library"
        self.claude_skills = self.home / ".claude" / "skills"
        self.agents_skills = self.home / ".agents" / "skills"
        for directory in (self.claude_skills, self.agents_skills):
            directory.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def write_skill(self, root: Path, name: str, description: str = "desc") -> Path:
        directory = root / name
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "SKILL.md").write_text(
            "---\n"
            f"name: {name}\n"
            f"description: {description}\n"
            "---\n\nBody\n",
            encoding="utf-8",
        )
        return directory

    def set_names(self, *names: str) -> None:
        self.library_file.write_text(
            "# listed\n\n" + "".join(name + "\n" for name in names),
            encoding="utf-8",
        )

    def run_tool(self, *arguments: str):
        command = [
            sys.executable,
            "-I",
            str(SCRIPT),
            "--home",
            str(self.home),
            "--library-file",
            str(self.library_file),
            "--repo-skills",
            str(self.repo_skills),
            *arguments,
        ]
        return subprocess.run(command, text=True, capture_output=True, check=False)

    def snapshot(self) -> dict:
        result = {}
        for directory in (self.home, self.repo_skills):
            if directory.exists():
                for path in directory.rglob("*"):
                    key = str(path.relative_to(self.root))
                    if path.is_symlink():
                        result[key] = ("link", os.readlink(path))
                    elif path.is_file():
                        result[key] = ("file", path.read_bytes())
                    elif path.is_dir():
                        result[key] = ("dir",)
        return result


class ApplyTests(SkillLibraryTestCase):
    def test_dry_run_changes_nothing(self):
        self.set_names("wanted")
        self.write_skill(self.claude_skills, "wanted", "installed")
        self.write_skill(self.repo_skills / "tools", "wanted", "repo")
        self.write_skill(self.claude_skills, "other")
        before = self.snapshot()

        result = self.run_tool("apply")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("[dry-run] move", result.stdout)
        self.assertIn("[dry-run] regenerate", result.stdout)
        self.assertEqual(before, self.snapshot())
        self.assertFalse(self.library_dir.exists())

    def test_installed_only_skill_is_moved(self):
        self.set_names("wanted")
        source = self.write_skill(self.claude_skills, "wanted", "installed")
        target = self.library_dir / "wanted"

        result = self.run_tool("apply", "--apply")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertFalse(source.exists())
        self.assertEqual("installed", self.read_description(target / "SKILL.md"))
        self.assertTrue((self.library_dir / "INDEX.md").exists())

    def test_repo_only_skill_is_copied(self):
        self.set_names("wanted")
        self.write_skill(self.repo_skills / "quality", "wanted", "repo copy")
        target = self.library_dir / "wanted"

        result = self.run_tool("apply", "--apply")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("repo copy", self.read_description(target / "SKILL.md"))

    def test_identical_copies_move_one_and_trash_the_other(self):
        self.set_names("wanted")
        first = self.write_skill(self.claude_skills, "wanted", "same")
        second = self.write_skill(self.agents_skills, "wanted", "same")

        result = self.run_tool("apply", "--apply")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertFalse(first.exists())
        self.assertFalse(second.exists())
        self.assertEqual("same", self.read_description(self.library_dir / "wanted" / "SKILL.md"))
        trashed = list((self.library_dir / ".trash").rglob("wanted/SKILL.md"))
        self.assertEqual(1, len(trashed))
        self.assertEqual("same", self.read_description(trashed[0]))

    def test_conflicting_copies_are_preserved_with_warning(self):
        self.set_names("wanted")
        library_copy = self.write_skill(self.library_dir, "wanted", "library")
        first = self.write_skill(self.claude_skills, "wanted", "first")
        second = self.write_skill(self.agents_skills, "wanted", "second")

        result = self.run_tool("apply", "--apply")

        self.assertEqual(2, result.returncode)
        self.assertIn("differed", result.stderr)
        self.assertEqual("library", self.read_description(library_copy / "SKILL.md"))
        trashed = list((self.library_dir / ".trash").rglob("wanted/SKILL.md"))
        descriptions = sorted(self.read_description(path) for path in trashed)
        self.assertEqual(["first", "second"], descriptions)
        self.assertFalse(first.exists())
        self.assertFalse(second.exists())

    def test_symlink_is_skipped_and_warning_is_returned(self):
        self.set_names("linked")
        target = self.write_skill(self.root / "outside", "linked", "target")
        source = self.claude_skills / "linked"
        source.symlink_to(target, target_is_directory=True)

        result = self.run_tool("apply", "--apply")

        self.assertEqual(2, result.returncode)
        self.assertIn("symlink", result.stderr)
        self.assertTrue(source.is_symlink())
        self.assertFalse((self.library_dir / "linked").exists())

    def test_invalid_names_are_rejected(self):
        self.set_names("../escape", "Bad Name")

        result = self.run_tool("apply", "--apply")

        self.assertEqual(1, result.returncode)
        self.assertIn("invalid name", result.stderr)
        self.assertFalse(self.library_dir.exists())

    def test_skill_library_name_is_refused(self):
        self.set_names("skill-library")

        result = self.run_tool("apply", "--apply")

        self.assertEqual(1, result.returncode)
        self.assertIn("refused", result.stderr)
        self.assertFalse(self.library_dir.exists())

    def test_non_library_name_is_untouched(self):
        self.set_names("wanted")
        self.write_skill(self.claude_skills, "wanted")
        unlisted = self.write_skill(self.claude_skills, "unlisted", "do not touch")

        result = self.run_tool("apply", "--apply")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("do not touch", self.read_description(unlisted / "SKILL.md"))

    def test_second_apply_is_a_no_op(self):
        self.set_names("wanted")
        self.write_skill(self.claude_skills, "wanted", "installed")
        first = self.run_tool("apply", "--apply")
        self.assertEqual(0, first.returncode, first.stderr)
        before = self.snapshot()

        second = self.run_tool("apply", "--apply")

        self.assertEqual(0, second.returncode, second.stderr)
        self.assertEqual(before, self.snapshot())
        self.assertNotIn("trash", second.stdout)

    def read_description(self, path: Path) -> str:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("description:"):
                return line.split(":", 1)[1].strip()
        raise AssertionError(f"no description in {path}")


class IndexTests(SkillLibraryTestCase):
    def test_index_ordering_truncation_and_folded_description(self):
        self.library_dir.mkdir(parents=True)
        (self.library_dir / "z-skill").mkdir()
        (self.library_dir / "z-skill" / "SKILL.md").write_text(
            "---\n"
            "name: z-skill\n"
            "description: >\n"
            "  first folded part\n"
            "    second folded part\n"
            "---\n",
            encoding="utf-8",
        )
        (self.library_dir / "a-skill").mkdir()
        (self.library_dir / "a-skill" / "SKILL.md").write_text(
            '---\nname: "a-skill"\ndescription: "quoted | text"\n---\n',
            encoding="utf-8",
        )
        long_description = "x" * 180
        (self.library_dir / ".hidden").mkdir()
        (self.library_dir / ".hidden" / "SKILL.md").write_text("---\nname: hidden\n---\n")
        (self.library_dir / "long-skill").mkdir()
        (self.library_dir / "long-skill" / "SKILL.md").write_text(
            f"---\nname: long-skill\ndescription: {long_description}\n---\n",
            encoding="utf-8",
        )

        result = self.run_tool("index")

        self.assertEqual(0, result.returncode, result.stderr)
        index = (self.library_dir / "INDEX.md").read_text(encoding="utf-8")
        lines = index.splitlines()
        self.assertEqual(4, len(lines))
        self.assertIn("generated", lines[0].lower())
        self.assertEqual(
            "- a-skill | quoted | text | a-skill/SKILL.md",
            lines[1],
        )
        self.assertTrue(lines[2].startswith("- long-skill | " + "x" * 140 + "... | "))
        self.assertEqual(
            "- z-skill | first folded part second folded part | z-skill/SKILL.md",
            lines[3],
        )


class InstallScriptTests(SkillLibraryTestCase):
    def test_install_script_skips_library_names(self):
        fake_repo = self.root / "fake-repo"
        (fake_repo / "tools" / "skill-library").mkdir(parents=True)
        shutil.copy2(Path(__file__).parents[2] / "install.sh", fake_repo / "install.sh")
        (fake_repo / "tools" / "skill-library" / "library.txt").write_text(
            "library-skill\n",
            encoding="utf-8",
        )
        self.write_skill(fake_repo / "skills" / "kept", "kept-skill", "kept")
        self.write_skill(fake_repo / "skills" / "library", "library-skill", "library")
        fake_home = self.root / "fake-home"

        whole = subprocess.run(
            ["bash", str(fake_repo / "install.sh")],
            env={**os.environ, "HOME": str(fake_home)},
            text=True,
            capture_output=True,
            check=False,
        )
        named = subprocess.run(
            ["bash", str(fake_repo / "install.sh"), "--skill", "library-skill"],
            env={**os.environ, "HOME": str(fake_home)},
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(0, whole.returncode, whole.stderr)
        self.assertEqual(2, whole.stdout.count("[library] skipped library-skill"))
        self.assertTrue(
            (fake_home / ".claude" / "skills" / "kept-skill" / "SKILL.md").is_file()
        )
        self.assertFalse((fake_home / ".claude" / "skills" / "library-skill").exists())
        self.assertEqual(0, named.returncode, named.stderr)
        self.assertIn("[library] skipped library-skill", named.stdout)


if __name__ == "__main__":
    unittest.main()
