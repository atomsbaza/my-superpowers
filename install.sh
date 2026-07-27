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
#   ./install.sh           — link new items, skip existing
#   ./install.sh --force   — remove existing copies/links and re-link everything

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
FORCE=false

for arg in "$@"; do
  case "$arg" in
    --force|-f) FORCE=true ;;
    *) echo "Unknown argument: $arg"; exit 1 ;;
  esac
done

link_or_skip() {
  local src="$1"
  local dest="$2"
  local label="$3"

  if [ -e "$dest" ] || [ -L "$dest" ]; then
    if $FORCE; then
      rm -rf "$dest"
      ln -s "$src" "$dest"
      echo "  [relink] $label"
    else
      echo "  [skip]   $label (use --force to relink)"
    fi
  else
    ln -s "$src" "$dest"
    echo "  [link]   $label"
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
    link_or_skip "$agent_file" "$dest_dir/$name" "$name"
  done
}

install_skills() {
  local dest_dir="$1"   # e.g. ~/.claude/skills
  mkdir -p "$dest_dir"
  # A skill is any directory containing a SKILL.md, discovered under skills/.
  local root="$REPO_DIR/skills"
  [ -d "$root" ] || return 0
  while IFS= read -r skill_md; do
    skill_dir="$(dirname "$skill_md")"
    name="$(basename "$skill_dir")"
    link_or_skip "$skill_dir" "$dest_dir/$name" "$name"
  done < <(find "$root" -name SKILL.md)
}

echo "=== my-superpowers install ==="
$FORCE && echo "Mode: --force (relinking all)" || echo "Mode: skip existing (run --force to relink)"
echo ""

# ── Claude Code ──────────────────────────────────────────────
echo "Claude Code:"
echo "  agents → ~/.claude/agents/"
install_agents "$REPO_DIR/agents" "$HOME/.claude/agents"
echo "  skills → ~/.claude/skills/"
install_skills "$HOME/.claude/skills"
echo ""

# ── Codex CLI ────────────────────────────────────────────────
echo "Codex CLI:"
echo "  skills → ~/.agents/skills/"
install_skills "$HOME/.agents/skills"
echo ""

echo "Done. Restart your AI tool to pick up new skills and agents."
