#!/bin/bash
# install.sh — sets up skills and agents for supported AI coding tools
# Skills are organized in categories (skills/<category>/<skill-name>/)
# but installed flat into each tool's skills directory.

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

link_or_skip() {
  local src="$1"
  local dest="$2"
  local name="$3"
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    echo "  [skip] $name already exists"
  else
    ln -s "$src" "$dest"
    echo "  [link] $name"
  fi
}

install_skills() {
  local skills_dir="$1"
  mkdir -p "$skills_dir"
  # Walk two levels deep: skills/<category>/<skill-name>/
  for category_dir in "$REPO_DIR/skills"/*/; do
    for skill_dir in "$category_dir"*/; do
      [ -d "$skill_dir" ] || continue
      skill_name=$(basename "$skill_dir")
      link_or_skip "$skill_dir" "$skills_dir/$skill_name" "$skill_name"
    done
  done
}

install_agents() {
  local agents_dir="$1"
  mkdir -p "$agents_dir"
  # Walk two levels deep: agents/<category>/<agent>.md
  for category_dir in "$REPO_DIR/agents"/*/; do
    for agent_file in "$category_dir"*.md; do
      [ -f "$agent_file" ] || continue
      agent_name=$(basename "$agent_file")
      link_or_skip "$agent_file" "$agents_dir/$agent_name" "$agent_name"
    done
  done
}

echo "=== my-superpowers install ==="
echo ""

# Claude Code
echo "Claude Code (~/.claude/skills, ~/.claude/agents):"
install_skills "$HOME/.claude/skills"
install_agents "$HOME/.claude/agents"
echo ""

# Codex CLI
echo "Codex CLI (~/.agents/skills):"
install_skills "$HOME/.agents/skills"
echo ""

# Kiro — install if detected
if command -v kiro &>/dev/null || [ -d "$HOME/.kiro" ]; then
  echo "Kiro (~/.kiro/skills):"
  install_skills "$HOME/.kiro/skills"
  echo ""
fi

echo "Done. Restart your AI tool to pick up new skills."
