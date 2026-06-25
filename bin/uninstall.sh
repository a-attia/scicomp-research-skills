#!/usr/bin/env bash
#
# uninstall.sh -- reverse the actions of install.sh (and optionally,
#                 with --deep, fully remove the canonical checkout).
#
# Idempotent: safe to run multiple times.
#
# Default behaviour: DRY RUN. Prints what WOULD be removed without
# actually removing anything. Pass -y or --confirm to actually perform
# the removal.
#
# What this does:
#   1. Removes user-home skill-discovery symlinks created by install.sh
#      (~/.config/opencode/skills, ~/.claude/skills, ~/.agents/skills,
#      ~/.cursor/skills, ~/.copilot/skills, ~/.gemini/skills,
#      ~/.codex/skills) -- BUT ONLY if they currently
#      point at THIS canonical checkout. Symlinks pointing elsewhere or
#      real directories are left untouched.
#   2. Removes in-repo agent-filename symlinks (CLAUDE.md, GEMINI.md,
#      .cursorrules, CONVENTIONS.md, AGENT.md) created by install.sh.
#      Same safety: only symlinks are removed; real files are left
#      untouched.
#   3. With --deep AND interactive confirmation: also unsets the local
#      git config core.hooksPath and DELETES the entire canonical
#      checkout (~/.scicomp-research-skills/). Dev checkouts of this
#      repo at any other path are NEVER touched.
#
# Every action (preview or actual) is appended to a log file at
# ~/.scicomp-research-skills.uninstall.log so you can audit later.
#
# This script is intended to be run inside the canonical checkout
# location, but works in any clone of this repo.

set -euo pipefail

# ----------------------------------------------------------------------
# Setup: paths, defaults, log file.
# ----------------------------------------------------------------------

REPO_ROOT="$(git -C "$(dirname "$0")/.." rev-parse --show-toplevel)"
REPO_ROOT_ABS="$(cd "${REPO_ROOT}" && pwd -P)"
SKILLS_TARGET="${REPO_ROOT_ABS}/skills"
CANONICAL="${HOME}/.scicomp-research-skills"
LOG_FILE="${HOME}/.scicomp-research-skills.uninstall.log"

# Honour $CODEX_HOME override (same as install.sh).
CODEX_HOME_DIR="${CODEX_HOME:-${HOME}/.codex}"

# CLI flags.
DRY_RUN=1     # default: dry run
DEEP=0
ASSUME_YES=0
SHOW_HELP=0

# Counters for the final summary.
COUNT_REMOVED=0
COUNT_SKIPPED=0
COUNT_WARNED=0

# ----------------------------------------------------------------------
# Helpers.
# ----------------------------------------------------------------------

usage() {
  cat <<'EOF'
uninstall.sh -- reverse install.sh, optionally fully remove the canonical checkout.

USAGE:
  uninstall.sh [OPTIONS]

OPTIONS:
  -h, --help        Show this help and exit.
  -n, --dry-run     Show what WOULD be removed without removing anything.
                    This is the DEFAULT.
  -y, --confirm     Actually perform the removal (overrides --dry-run).
                    Aliases: --yes
      --deep        Also unset git config core.hooksPath AND delete the
                    entire canonical checkout (~/.scicomp-research-skills/).
                    Requires interactive confirmation unless -y is passed.
                    Dev checkouts of this repo at any other path are NEVER touched.

EXAMPLES:
  # Preview what would be removed (default behaviour, no removal):
  uninstall.sh

  # Actually remove install.sh's symlinks (in-repo + user-home):
  uninstall.sh --confirm

  # Full removal: symlinks + git config reset + delete canonical checkout:
  uninstall.sh --deep --confirm

LOG FILE:
  All actions (preview or actual) are logged to:
  ~/.scicomp-research-skills.uninstall.log

EOF
}

log_action() {
  # Append a timestamped entry to the log file.
  local stamp
  stamp="$(date '+%Y-%m-%d %H:%M:%S')"
  printf '%s  %s\n' "${stamp}" "$1" >> "${LOG_FILE}"
}

note() {
  # Echo to stdout AND append to log.
  echo "$1"
  log_action "$1"
}

# Resolve a symlink to an absolute path, handling relative targets.
resolve_link() {
  local link="$1"
  local target
  target="$(readlink "${link}")"
  if [[ "${target}" = /* ]]; then
    # Already absolute.
    echo "${target}"
  else
    # Relative to the link's directory.
    local link_dir
    link_dir="$(dirname "${link}")"
    (cd "${link_dir}" && cd "$(dirname "${target}")" 2>/dev/null && \
     echo "$(pwd -P)/$(basename "${target}")") || echo "${target}"
  fi
}

# Process a single user-home skills-directory symlink candidate.
# Args: $1 = path (e.g. ~/.config/opencode/skills)
process_user_home_symlink() {
  local target_dir="$1"

  if [[ -L "${target_dir}" ]]; then
    local resolved
    resolved="$(resolve_link "${target_dir}")"
    if [[ "${resolved}" == "${SKILLS_TARGET}" ]]; then
      if (( DRY_RUN )); then
        note "  WOULD REMOVE symlink: ${target_dir} -> ${resolved}"
      else
        rm "${target_dir}"
        note "  removed symlink: ${target_dir}"
      fi
      COUNT_REMOVED=$((COUNT_REMOVED + 1))
    else
      note "  skip: ${target_dir} is a symlink to ${resolved} (not us)"
      COUNT_SKIPPED=$((COUNT_SKIPPED + 1))
    fi
  elif [[ -d "${target_dir}" ]]; then
    note "  skip: ${target_dir} is a real directory (not created by install.sh)"
    COUNT_SKIPPED=$((COUNT_SKIPPED + 1))
  elif [[ -e "${target_dir}" ]]; then
    note "  WARN: ${target_dir} exists but is neither a symlink nor a directory; skipping"
    COUNT_WARNED=$((COUNT_WARNED + 1))
  else
    note "  ok: ${target_dir} does not exist (nothing to remove)"
    COUNT_SKIPPED=$((COUNT_SKIPPED + 1))
  fi
}

# Process a single in-repo filename symlink candidate.
# Args: $1 = filename (e.g. CLAUDE.md), relative to REPO_ROOT.
process_in_repo_symlink() {
  local name="$1"
  local path="${REPO_ROOT}/${name}"

  if [[ -L "${path}" ]]; then
    local resolved
    resolved="$(readlink "${path}")"
    # We expect these to be relative symlinks pointing at AGENTS.md.
    if [[ "${resolved}" == "AGENTS.md" || "${resolved}" == "${REPO_ROOT}/AGENTS.md" ]]; then
      if (( DRY_RUN )); then
        note "  WOULD REMOVE symlink: ${name} -> AGENTS.md"
      else
        rm "${path}"
        note "  removed symlink: ${name}"
      fi
      COUNT_REMOVED=$((COUNT_REMOVED + 1))
    else
      note "  skip: ${name} is a symlink to ${resolved} (not our AGENTS.md)"
      COUNT_SKIPPED=$((COUNT_SKIPPED + 1))
    fi
  elif [[ -e "${path}" ]]; then
    note "  WARN: ${name} exists and is NOT a symlink; skipping (not created by install.sh)"
    COUNT_WARNED=$((COUNT_WARNED + 1))
  else
    note "  ok: ${name} does not exist (nothing to remove)"
    COUNT_SKIPPED=$((COUNT_SKIPPED + 1))
  fi
}

# ----------------------------------------------------------------------
# Parse flags.
# ----------------------------------------------------------------------

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)         SHOW_HELP=1; shift ;;
    -n|--dry-run)      DRY_RUN=1; shift ;;
    -y|--yes|--confirm) DRY_RUN=0; ASSUME_YES=1; shift ;;
    --deep)            DEEP=1; shift ;;
    *)                 echo "ERROR: unknown flag: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if (( SHOW_HELP )); then
  usage
  exit 0
fi

# ----------------------------------------------------------------------
# Banner + log header.
# ----------------------------------------------------------------------

mkdir -p "$(dirname "${LOG_FILE}")"
log_action "==== uninstall.sh invoked  REPO_ROOT=${REPO_ROOT_ABS}  DRY_RUN=${DRY_RUN}  DEEP=${DEEP}  ASSUME_YES=${ASSUME_YES} ===="

note "Uninstalling from ${REPO_ROOT_ABS}"
if (( DRY_RUN )); then
  note "Mode: DRY RUN (no changes will be made). Pass -y / --confirm to actually remove."
else
  note "Mode: CONFIRMED removal."
fi
note "Log file: ${LOG_FILE}"
note ""

# ----------------------------------------------------------------------
# Phase 1: user-home skill-discovery symlinks.
# ----------------------------------------------------------------------

note "[1/3] user-home skills-directory symlinks:"

USER_HOME_SKILLS_DIRS=(
  "${HOME}/.config/opencode/skills"
  "${HOME}/.claude/skills"
  "${HOME}/.agents/skills"
  "${HOME}/.cursor/skills"
  "${HOME}/.copilot/skills"
  "${HOME}/.gemini/skills"
  "${CODEX_HOME_DIR}/skills"
)

for d in "${USER_HOME_SKILLS_DIRS[@]}"; do
  process_user_home_symlink "${d}"
done

# ----------------------------------------------------------------------
# Phase 2: in-repo filename symlinks.
# ----------------------------------------------------------------------

note ""
note "[2/3] in-repo filename symlinks:"

AGENT_FILENAME_SYMLINKS=(
  "CLAUDE.md"
  ".cursorrules"
  "CONVENTIONS.md"
  "GEMINI.md"
  "AGENT.md"
)

for name in "${AGENT_FILENAME_SYMLINKS[@]}"; do
  process_in_repo_symlink "${name}"
done

# ----------------------------------------------------------------------
# Phase 3: deep uninstall (only if --deep was passed).
# ----------------------------------------------------------------------

note ""
if (( DEEP )); then
  note "[3/3] deep uninstall: git config + canonical checkout"

  # 3a. git config core.hooksPath unset.
  if (( DRY_RUN )); then
    note "  WOULD UNSET git config core.hooksPath in ${REPO_ROOT_ABS}"
  else
    if git -C "${REPO_ROOT_ABS}" config --get core.hooksPath >/dev/null 2>&1; then
      git -C "${REPO_ROOT_ABS}" config --unset core.hooksPath
      note "  unset git config core.hooksPath"
      COUNT_REMOVED=$((COUNT_REMOVED + 1))
    else
      note "  ok: git config core.hooksPath was not set"
      COUNT_SKIPPED=$((COUNT_SKIPPED + 1))
    fi
  fi

  # 3b. Delete the canonical checkout (only if THIS checkout IS the canonical one).
  CANONICAL_ABS="$(cd "${CANONICAL}" 2>/dev/null && pwd -P || echo "")"

  if [[ -z "${CANONICAL_ABS}" ]]; then
    note "  ok: canonical checkout ${CANONICAL} does not exist"
    COUNT_SKIPPED=$((COUNT_SKIPPED + 1))
  elif [[ "${REPO_ROOT_ABS}" != "${CANONICAL_ABS}" ]]; then
    note "  WARN: this is NOT the canonical checkout (${REPO_ROOT_ABS} vs ${CANONICAL_ABS})."
    note "        --deep can only delete the canonical checkout when run from inside it."
    note "        To delete it from elsewhere: rm -rf ${CANONICAL_ABS}"
    COUNT_WARNED=$((COUNT_WARNED + 1))
  else
    # Belt-and-braces safety: only ever delete the exact expected
    # canonical path (${HOME}/.scicomp-research-skills). The earlier
    # REPO_ROOT_ABS == CANONICAL_ABS check should already guarantee
    # this, but we re-check here so any future refactor cannot
    # accidentally rm -rf the wrong directory.
    EXPECTED_CANONICAL="${HOME}/.scicomp-research-skills"
    EXPECTED_CANONICAL_ABS="$(cd "${EXPECTED_CANONICAL}" 2>/dev/null && pwd -P || echo "${EXPECTED_CANONICAL}")"

    if [[ "${CANONICAL_ABS}" != "${EXPECTED_CANONICAL_ABS}" ]]; then
      note "  REFUSED: ${CANONICAL_ABS} is not the expected canonical path (${EXPECTED_CANONICAL_ABS}); refusing to delete."
      COUNT_WARNED=$((COUNT_WARNED + 1))
    elif (( DRY_RUN )); then
      note "  WOULD DELETE canonical checkout: ${CANONICAL_ABS}"
      note "  (tip: dev checkouts of this repo at any other path are NOT touched)"
    else
      # Interactive confirmation unless --yes was also passed.
      if (( ! ASSUME_YES )); then
        note ""
        echo "*** This will RECURSIVELY DELETE the canonical checkout: ${CANONICAL_ABS}"
        echo "*** Dev checkouts of this repo at any other path are NOT touched."
        read -r -p "Type 'DELETE' to confirm: " confirmation
        log_action "  interactive confirmation prompt: user typed: '${confirmation}'"
        if [[ "${confirmation}" != "DELETE" ]]; then
          note "  ABORTED canonical-checkout deletion (confirmation did not match 'DELETE')"
          COUNT_SKIPPED=$((COUNT_SKIPPED + 1))
        else
          # We're about to delete the directory we're sitting in. cd out first.
          cd "${HOME}"
          rm -rf "${CANONICAL_ABS}"
          note "  DELETED canonical checkout: ${CANONICAL_ABS}"
          COUNT_REMOVED=$((COUNT_REMOVED + 1))
        fi
      else
        # --yes was passed; skip the interactive prompt.
        cd "${HOME}"
        rm -rf "${CANONICAL_ABS}"
        note "  DELETED canonical checkout: ${CANONICAL_ABS} (via -y)"
        COUNT_REMOVED=$((COUNT_REMOVED + 1))
      fi
    fi
  fi
else
  note "[3/3] deep uninstall: SKIPPED (pass --deep to enable)"
fi

# ----------------------------------------------------------------------
# Summary.
# ----------------------------------------------------------------------

note ""
note "================================================================"
if (( DRY_RUN )); then
  note "Summary (DRY RUN -- no changes made):"
  note "  Would-remove items: ${COUNT_REMOVED}"
  note "  Skip items:         ${COUNT_SKIPPED}"
  note "  Warnings:           ${COUNT_WARNED}"
  note ""
  note "To actually perform this removal, re-run with -y or --confirm:"
  note "  $0 ${DEEP:+--deep }--confirm"
else
  note "Summary:"
  note "  Removed items: ${COUNT_REMOVED}"
  note "  Skipped items: ${COUNT_SKIPPED}"
  note "  Warnings:      ${COUNT_WARNED}"
fi
note "================================================================"
log_action "==== uninstall.sh complete ===="
