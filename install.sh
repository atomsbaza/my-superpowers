#!/bin/bash
# install.sh — sets up skills and agents for Claude Code (and Codex CLI)
#
# Structure:
#   agents/*.md                → ~/.claude/agents/         (flat agent definitions)
#   skills/<category>/<name>/  → ~/.claude/skills/         (skills, organized by category)
#
# Skills are discovered by their SKILL.md — the category folders under skills/
# are organizational only and are flattened at install time.
#
# Usage:
#   ./install.sh           — install new items, skip existing
#   ./install.sh --force   — replace existing copies/links and reinstall everything
#   ./install.sh --skill book-to-skill --codex-only

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
FORCE=false
SKILL_NAME=""
CODEX_ONLY=false
CLAUDE_ONLY=false

while [ "$#" -gt 0 ]; do
  case "$1" in
    --force|-f) FORCE=true ;;
    --skill)
      [ "$#" -ge 2 ] || { echo "Missing skill name after --skill" >&2; exit 1; }
      SKILL_NAME="$2"
      shift
      ;;
    --codex-only) CODEX_ONLY=true ;;
    --claude-only) CLAUDE_ONLY=true ;;
    -h|--help)
      echo "Usage: ./install.sh [--force] [--skill NAME] [--codex-only|--claude-only]"
      exit 0
      ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
  shift
done

if $CODEX_ONLY && $CLAUDE_ONLY; then
  echo "Choose only one of --codex-only or --claude-only" >&2
  exit 1
fi

install_or_skip() {
  local src="$1"
  local dest="$2"
  local label="$3"

  if [ -e "$dest" ] || [ -L "$dest" ]; then
    if $FORCE; then
      rm -rf "$dest"
      if [ -d "$src" ]; then
        cp -R "$src" "$dest"
      else
        cp "$src" "$dest"
      fi
      echo "  [reinstall] $label"
    else
      echo "  [skip]   $label (use --force to reinstall)"
    fi
  else
    if [ -d "$src" ]; then
      cp -R "$src" "$dest"
    else
      cp "$src" "$dest"
    fi
    echo "  [install] $label"
  fi
}

install_agents() {
  local src_root="$1"   # e.g. REPO_DIR/agents (flat *.md)
  local dest_dir="$2"   # e.g. ~/.claude/agents
  [ -d "$src_root" ] || return 0
  mkdir -p "$dest_dir"
  for agent_file in "$src_root"/*.md; do
    [ -f "$agent_file" ] || continue
    name=$(basename "$agent_file")
    install_or_skip "$agent_file" "$dest_dir/$name" "$name"
  done
}

install_skills() {
  local dest_dir="$1"   # e.g. ~/.claude/skills
  mkdir -p "$dest_dir"
  # A skill is any directory containing a SKILL.md, discovered under skills/.
  local root="$REPO_DIR/skills"
  [ -d "$root" ] || return 0
  local found=false
  while IFS= read -r skill_md; do
    skill_dir="$(dirname "$skill_md")"
    name="$(basename "$skill_dir")"
    if [ -n "$SKILL_NAME" ] && [ "$name" != "$SKILL_NAME" ]; then
      continue
    fi
    found=true
    install_or_skip "$skill_dir" "$dest_dir/$name" "$name"
  done < <(find "$root" -name SKILL.md)
  if [ -n "$SKILL_NAME" ] && ! $found; then
    echo "Skill not found in $root: $SKILL_NAME" >&2
    return 1
  fi
}

echo "=== my-superpowers install ==="
$FORCE && echo "Mode: --force (reinstalling selected skills)" || echo "Mode: skip existing (run --force to reinstall)"
[ -n "$SKILL_NAME" ] && echo "Skill: $SKILL_NAME"
echo ""

# ── Claude Code ──────────────────────────────────────────────
if ! $CODEX_ONLY; then
  echo "Claude Code:"
  if [ -z "$SKILL_NAME" ]; then
    echo "  agents → ~/.claude/agents/"
    install_agents "$REPO_DIR/agents" "$HOME/.claude/agents"
  fi
  echo "  skills → ~/.claude/skills/"
  install_skills "$HOME/.claude/skills"
  echo ""
fi

# ── Codex CLI ────────────────────────────────────────────────
if $CLAUDE_ONLY; then
  echo "Codex CLI: skipped (--claude-only)"
  echo ""
  echo "Done. Restart your AI tool to pick up new skills and agents."
  exit 0
fi
echo "Codex CLI:"
echo "  skills → ~/.agents/skills/"
install_skills "$HOME/.agents/skills"
echo ""

echo "Done. Restart your AI tool to pick up new skills and agents."
