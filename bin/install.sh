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
#   3. Creates agent-specific FILENAME symlinks INSIDE the repo so agents
#      that look for filenames other than AGENTS.md (CLAUDE.md, GEMINI.md,
#      .cursorrules, CONVENTIONS.md, AGENT.md) find the canonical AGENTS.md
#      content.
#   4. Creates agent-specific user-home SKILLS-DIRECTORY symlinks pointing
#      at this repo's skills/ folder, so any agent that auto-discovers
#      skills from a user-level directory (~/.config/opencode/skills/,
#      ~/.claude/skills/, ~/.codex/skills/, ~/.agents/skills/, ~/.gemini/skills/)
#      sees this repo's skills automatically.
#
# With --update, additionally:
#   5. Reports orphaned in-repo symlinks pointing at our AGENTS.md whose
#      filename is NOT in the current install list (Phase 3). These were
#      created by an older install.sh but no longer match the current
#      list. We do NOT auto-remove them; suggest running uninstall.sh.
#
# This script is intended to be run inside the canonical checkout location
# (typically ~/.scicomp-research-skills/), but works in any clone of this
# repo.

set -euo pipefail

# ----------------------------------------------------------------------
# CLI flags.
# ----------------------------------------------------------------------

UPDATE_MODE=0
SHOW_HELP=0

usage() {
  cat <<'EOF'
install.sh -- set up the canonical checkout (idempotent).

USAGE:
  install.sh [OPTIONS]

OPTIONS:
  -h, --help     Show this help and exit.
  -u, --update   Run in update mode: same as default install (which is
                 already idempotent), PLUS report orphaned in-repo
                 symlinks pointing at our AGENTS.md whose filename is
                 not in the current install list. Use this after a
                 git pull (e.g. via bin/refresh.sh) to pick up new
                 in-repo or user-home symlinks added by a newer
                 version of install.sh.

EXAMPLES:
  # Initial setup on a new machine:
  install.sh

  # After bin/refresh.sh (git pull) brings in new install.sh content:
  install.sh --update

NOTES:
  - This script is always idempotent: re-running it without --update
    has the same effect as --update minus the orphan-report phase.
  - Orphan detection covers IN-REPO symlinks only. Detecting orphaned
    user-home symlinks (e.g. a path we used to install but no longer
    do) requires version-tracking we don't currently maintain.
  - Use bin/uninstall.sh to actively remove anything install.sh created.

EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)    SHOW_HELP=1; shift ;;
    -u|--update)  UPDATE_MODE=1; shift ;;
    *)            echo "ERROR: unknown flag: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if (( SHOW_HELP )); then
  usage
  exit 0
fi

# ----------------------------------------------------------------------
# Setup: paths.
# ----------------------------------------------------------------------

REPO_ROOT="$(git -C "$(dirname "$0")/.." rev-parse --show-toplevel)"
REPO_ROOT_ABS="$(cd "${REPO_ROOT}" && pwd -P)"
cd "${REPO_ROOT}"

if (( UPDATE_MODE )); then
  echo "Updating install state at ${REPO_ROOT_ABS}"
else
  echo "Installing into ${REPO_ROOT_ABS}"
fi
echo

# ----------------------------------------------------------------------
# 1. Configure git hooks.
# ----------------------------------------------------------------------
git config core.hooksPath .githooks
echo "[1/4] git: configured core.hooksPath = .githooks"

# ----------------------------------------------------------------------
# 2. Make scripts executable.
# ----------------------------------------------------------------------
chmod +x .githooks/* 2>/dev/null || true
chmod +x bin/*.sh
echo "[2/4] chmod: made hook scripts + bin scripts executable"

# ----------------------------------------------------------------------
# 3. Per-agent filename symlinks INSIDE the repo (point at AGENTS.md).
# ----------------------------------------------------------------------
echo "[3/4] in-repo filename symlinks:"

AGENT_FILENAME_SYMLINKS=(
  "CLAUDE.md"          # Claude Code (also OpenCode fallback)
  ".cursorrules"       # Cursor (older versions)
  "CONVENTIONS.md"     # Aider
  "GEMINI.md"          # Gemini Code Assist
  "AGENT.md"           # Zed (singular form fallback)
)

for name in "${AGENT_FILENAME_SYMLINKS[@]}"; do
  if [[ -e "${name}" && ! -L "${name}" ]]; then
    echo "  WARN: ${name} exists and is NOT a symlink; skipping. Move it aside to let this script manage it."
    continue
  fi
  ln -sf AGENTS.md "${name}"
  echo "  symlinked ${name} -> AGENTS.md"
done

# ----------------------------------------------------------------------
# 4. User-home skills-directory symlinks pointing at THIS repo's skills/.
#    Agents that auto-discover skills from a user-home location will pick
#    these up automatically.
# ----------------------------------------------------------------------
echo "[4/4] user-home skills-directory symlinks:"

SKILLS_TARGET="${REPO_ROOT_ABS}/skills"

# Each entry is a user-home path that one or more agents discover skills from.
# Codex respects $CODEX_HOME if set; we honour that and fall back to ~/.codex.
CODEX_HOME_DIR="${CODEX_HOME:-${HOME}/.codex}"

USER_HOME_SKILLS_DIRS=(
  "${HOME}/.config/opencode/skills"  # OpenCode (native)
  "${HOME}/.claude/skills"           # Claude Code (also OpenCode fallback)
  "${CODEX_HOME_DIR}/skills"         # Codex (respects $CODEX_HOME if set)
  "${HOME}/.agents/skills"           # agent-agnostic (also OpenCode fallback)
  "${HOME}/.gemini/skills"           # Gemini CLI (per Master-cai's install convention)
)

for target_dir in "${USER_HOME_SKILLS_DIRS[@]}"; do
  parent="$(dirname "${target_dir}")"
  mkdir -p "${parent}"

  if [[ -L "${target_dir}" ]]; then
    # Already a symlink. If it points at us, skip (idempotent). If it points
    # somewhere else, leave it alone -- don't clobber the user's existing setup.
    current_target="$(readlink "${target_dir}")"
    # Resolve to absolute for fair comparison
    current_target_abs="$(cd "${parent}" && cd "$(dirname "${current_target}")" 2>/dev/null && echo "$(pwd -P)/$(basename "${current_target}")" || echo "${current_target}")"
    if [[ "${current_target_abs}" == "${SKILLS_TARGET}" ]]; then
      echo "  ok:    ${target_dir} -> already points here"
    else
      echo "  WARN:  ${target_dir} is a symlink to ${current_target}; NOT overwriting. Remove it manually if you want our skills here."
    fi
  elif [[ -d "${target_dir}" ]]; then
    # Real directory exists. Don't overwrite -- there may be other skills there.
    echo "  WARN:  ${target_dir} exists as a real directory (not a symlink). NOT overwriting."
    echo "         To use our skills, either move existing skills out then re-run install,"
    echo "         or copy individual SKILL.md folders from ${SKILLS_TARGET} into it."
  elif [[ -e "${target_dir}" ]]; then
    # Some other thing (file?) at that path.
    echo "  WARN:  ${target_dir} exists and is not a directory or symlink; skipping."
  else
    # Path is clear; create the symlink.
    ln -s "${SKILLS_TARGET}" "${target_dir}"
    echo "  ln:    ${target_dir} -> ${SKILLS_TARGET}"
  fi
done

# ----------------------------------------------------------------------
# 5. Orphan detection (only when --update was passed).
# ----------------------------------------------------------------------

if (( UPDATE_MODE )); then
  echo
  echo "[5/5] orphan check (--update mode):"

  # Helper: return 0 if $1 is in the expected list (AGENT_FILENAME_SYMLINKS
  # or "AGENTS.md" itself), 1 otherwise. Bash 3.2-compatible (macOS default
  # bash lacks associative arrays).
  is_expected_name() {
    local needle="$1"
    if [[ "${needle}" == "AGENTS.md" ]]; then
      return 0
    fi
    local n
    for n in "${AGENT_FILENAME_SYMLINKS[@]}"; do
      if [[ "${n}" == "${needle}" ]]; then
        return 0
      fi
    done
    return 1
  }

  # Find all symlinks at the top of the repo that point at AGENTS.md.
  # These are candidates for being install.sh-created agent-filename
  # symlinks. If their basename is not in the expected list, they're orphans.
  ORPHAN_COUNT=0
  while IFS= read -r -d '' link; do
    base="$(basename "${link}")"
    target="$(readlink "${link}")"
    # Only consider symlinks pointing at AGENTS.md (relative or absolute).
    if [[ "${target}" != "AGENTS.md" && "${target}" != "${REPO_ROOT_ABS}/AGENTS.md" ]]; then
      continue
    fi
    # Skip if the file IS in the expected list.
    if is_expected_name "${base}"; then
      continue
    fi
    # Otherwise, it's an orphan.
    if (( ORPHAN_COUNT == 0 )); then
      echo "  ORPHANS (in-repo symlinks pointing at AGENTS.md but no longer in install list):"
    fi
    echo "    ${base} -> ${target}"
    ORPHAN_COUNT=$((ORPHAN_COUNT + 1))
  done < <(find "${REPO_ROOT_ABS}" -maxdepth 1 -type l -print0)

  if (( ORPHAN_COUNT == 0 )); then
    echo "  ok: no in-repo orphan symlinks found"
  else
    echo
    echo "  HINT: orphan symlinks were created by an older install.sh"
    echo "        but are not in the current install list. They are not"
    echo "        actively harmful (they still point at AGENTS.md), but"
    echo "        you can remove them via:"
    echo "          ${REPO_ROOT_ABS}/bin/uninstall.sh --confirm"
    echo "        (uninstall.sh removes ALL symlinks created by install.sh,"
    echo "         then you can re-run install.sh to recreate the current ones.)"
  fi

  echo
  echo "  NOTE: orphan detection covers IN-REPO symlinks only."
  echo "        If a previous install.sh installed a user-home skill"
  echo "        symlink (e.g. ~/.<old-agent>/skills) that this version no"
  echo "        longer creates, it will not be flagged here. Inspect manually:"
  echo "          ls -la ~/.config/opencode/skills ~/.claude/skills ~/.codex/skills ~/.agents/skills ~/.gemini/skills 2>/dev/null"
fi

# ----------------------------------------------------------------------
# Final summary + verify hint.
# ----------------------------------------------------------------------

echo
if (( UPDATE_MODE )); then
  echo "Update complete."
else
  echo "Install complete."
fi
echo
echo "Verify:"
echo "  ls -l ${REPO_ROOT_ABS}"
echo "  git -C ${REPO_ROOT_ABS} config core.hooksPath"
echo "  ls -l ~/.config/opencode/skills ~/.claude/skills ~/.codex/skills ~/.agents/skills ~/.gemini/skills 2>/dev/null"
