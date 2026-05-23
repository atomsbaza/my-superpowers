#!/bin/bash
# install.sh — sets up skills and agents for supported AI coding tools

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

install_skills_for_tool() {
  local tool_name="$1"
  local skills_dir="$2"
  local agents_dir="$3"

  if [ -n "$skills_dir" ]; then
    mkdir -p "$skills_dir"
    for skill in "$REPO_DIR/skills"/*/; do
      skill_name=$(basename "$skill")
      target="$skills_dir/$skill_name"
      if [ -e "$target" ] || [ -L "$target" ]; then
        echo "  [skip] $skill_name already exists"
      else
        ln -s "$skill" "$target"
        echo "  [link] $skill_name"
      fi
    done
  fi

  if [ -n "$agents_dir" ]; then
    mkdir -p "$agents_dir"
    for agent in "$REPO_DIR/agents"/*.md; do
      agent_name=$(basename "$agent")
      target="$agents_dir/$agent_name"
      if [ -e "$target" ] || [ -L "$target" ]; then
        echo "  [skip] $agent_name already exists"
      else
        ln -s "$agent" "$target"
        echo "  [link] $agent_name"
      fi
    done
  fi
}

echo "=== my-superpowers install ==="
echo ""

# Claude Code
echo "Claude Code (~/.claude/skills, ~/.claude/agents):"
install_skills_for_tool "claude" "$HOME/.claude/skills" "$HOME/.claude/agents"
echo ""

# Codex CLI
echo "Codex CLI (~/.agents/skills):"
install_skills_for_tool "codex" "$HOME/.agents/skills" ""
echo ""

# Kiro (Amazon Q / Kiro) — uses ~/.kiro/skills if it exists
if command -v kiro &>/dev/null || [ -d "$HOME/.kiro" ]; then
  echo "Kiro (~/.kiro/skills):"
  install_skills_for_tool "kiro" "$HOME/.kiro/skills" ""
  echo ""
fi

echo "Done. Restart your AI tool to pick up new skills."
