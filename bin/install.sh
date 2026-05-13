#!/usr/bin/env bash
#
# install.sh -- one-time setup of the canonical checkout
#               at ~/.scicomp-research-skills/
#
# Idempotent: safe to run multiple times.
#
# What this does:
#   1. Configures the local git repo's core.hooksPath to point at .githooks/
#      so the pre-commit hook (which refuses commits in the canonical
#      checkout) is active.
#   2. Makes hook scripts + bin scripts executable.
#   3. Creates agent-specific filename symlinks (CLAUDE.md, etc.) so
#      agents that look for those filenames find the canonical AGENTS.md.
#
# This script is intended to be run inside the canonical checkout location
# (typically ~/.scicomp-research-skills/), but works in any clone of this
# repo.

set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")/.." rev-parse --show-toplevel)"
cd "${REPO_ROOT}"

echo "Installing into ${REPO_ROOT}"

# 1. Configure git to use the .githooks/ directory.
git config core.hooksPath .githooks
echo "  configured core.hooksPath = .githooks"

# 2. Make all hook scripts + bin scripts executable.
chmod +x .githooks/* 2>/dev/null || true
chmod +x bin/*.sh
echo "  made hook scripts + bin scripts executable"

# 3. Create agent-specific filename symlinks pointing at AGENTS.md.
#    Each entry is a filename other agents may look for; we symlink it to
#    the canonical AGENTS.md so any agent finds the same content.
AGENT_NAMES=(
  "CLAUDE.md"          # Claude Code
  ".cursorrules"       # Cursor (older versions)
  "CONVENTIONS.md"     # Aider
  "GEMINI.md"          # Gemini Code Assist (if applicable)
)

for name in "${AGENT_NAMES[@]}"; do
  if [[ -e "${name}" && ! -L "${name}" ]]; then
    echo "  WARNING: ${name} exists and is NOT a symlink; skipping. Move it aside if you want this script to manage it."
    continue
  fi
  ln -sf AGENTS.md "${name}"
  echo "  symlinked ${name} -> AGENTS.md"
done

echo
echo "Install complete. Verify:"
echo "  ls -l ${REPO_ROOT}"
echo "  git -C ${REPO_ROOT} config core.hooksPath"
echo
echo "Optional next step: enable OpenCode / Claude Code skill auto-discovery:"
echo "  ln -s ${REPO_ROOT}/skills ~/.config/opencode/skills"
echo "  ln -s ${REPO_ROOT}/skills ~/.claude/skills"
