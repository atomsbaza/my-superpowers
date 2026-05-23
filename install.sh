#!/bin/bash
# install.sh — sets up skills and agents for Claude Code and Kiro
#
# Structure:
#   claude/agents/<category>/*.md  → ~/.claude/agents/
#   kiro/agents/<category>/*.md    → ~/.kiro/agents/
#   skills/<category>/<name>/      → ~/.claude/skills/ and ~/.kiro/skills/ (flat)
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
  local src_root="$1"   # e.g. REPO_DIR/claude/agents
  local dest_dir="$2"   # e.g. ~/.claude/agents
  mkdir -p "$dest_dir"
  for category_dir in "$src_root"/*/; do
    for agent_file in "$category_dir"*.md; do
      [ -f "$agent_file" ] || continue
      name=$(basename "$agent_file")
      link_or_skip "$agent_file" "$dest_dir/$name" "$name"
    done
  done
}

install_skills() {
  local dest_dir="$1"   # e.g. ~/.claude/skills
  mkdir -p "$dest_dir"
  for category_dir in "$REPO_DIR/skills"/*/; do
    for skill_dir in "$category_dir"*/; do
      [ -d "$skill_dir" ] || continue
      name=$(basename "$skill_dir")
      link_or_skip "$skill_dir" "$dest_dir/$name" "$name"
    done
  done
}

echo "=== my-superpowers install ==="
$FORCE && echo "Mode: --force (relinking all)" || echo "Mode: skip existing (run --force to relink)"
echo ""

# ── Claude Code ──────────────────────────────────────────────
echo "Claude Code:"
echo "  agents → ~/.claude/agents/"
install_agents "$REPO_DIR/claude/agents" "$HOME/.claude/agents"
echo "  skills → ~/.claude/skills/"
install_skills "$HOME/.claude/skills"
echo ""

# ── Kiro ─────────────────────────────────────────────────────
if command -v kiro &>/dev/null || [ -d "$HOME/.kiro" ]; then
  echo "Kiro:"
  echo "  agents → ~/.kiro/agents/"
  install_agents "$REPO_DIR/kiro/agents" "$HOME/.kiro/agents"
  echo "  skills → ~/.kiro/skills/"
  install_skills "$HOME/.kiro/skills"
  echo ""
else
  echo "Kiro: not detected (skipped)"
  echo "  To install for Kiro later: mkdir ~/.kiro && ./install.sh"
  echo ""
fi

# ── Codex CLI ────────────────────────────────────────────────
echo "Codex CLI:"
echo "  skills → ~/.agents/skills/"
install_skills "$HOME/.agents/skills"
echo ""

echo "Done. Restart your AI tool to pick up new skills and agents."
