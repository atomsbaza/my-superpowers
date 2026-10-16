# skill-library tool

`skill_library.py` moves skills listed in `library.txt` out of harness scan
directories and into `~/.agents/skill-library/`. It can copy a repo-only skill
into the library, preserve extra or differing installed copies under
`.trash/<UTC timestamp>/`, and generate `INDEX.md`.

```sh
python3 tools/skill-library/skill_library.py status
python3 tools/skill-library/skill_library.py apply          # dry run
python3 tools/skill-library/skill_library.py apply --apply  # perform moves
python3 tools/skill-library/skill_library.py index
```

Use `--home`, `--library-file`, `--repo-skills`, `--scan-dir`, and
`--library-dir` for tests or non-default locations. The repo `skills/` tree is
read-only to this tool. It never deletes user data: moves are atomic where
possible, and apply is dry-run unless `--apply` is supplied.
