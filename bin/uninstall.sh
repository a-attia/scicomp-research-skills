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
# Terminal output is colorized for readability; the log file always
# receives plain ASCII. Colors auto-disable when stdout is not a TTY
# or when the NO_COLOR environment variable is set.
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
# Presentation layer (colors + glyphs).
#
# Colors are enabled ONLY when stdout is an interactive terminal and
# NO_COLOR is unset. The log file always receives plain ASCII (the
# log_action helper is never colorized), so audit logs stay clean.
# ----------------------------------------------------------------------

if [[ -t 1 && -z "${NO_COLOR:-}" ]]; then
  C_RESET=$'\033[0m'
  C_BOLD=$'\033[1m'
  C_DIM=$'\033[2m'
  C_RED=$'\033[31m'
  C_GREEN=$'\033[32m'
  C_YELLOW=$'\033[33m'
  C_BLUE=$'\033[34m'
  C_CYAN=$'\033[36m'
else
  C_RESET="" C_BOLD="" C_DIM="" C_RED="" C_GREEN="" C_YELLOW="" C_BLUE="" C_CYAN=""
fi

# Status glyphs (ASCII so they render everywhere; colored only on a TTY).
GLYPH_REMOVE="x"   # would-remove / removed
GLYPH_SKIP="-"     # skipped / nothing to do
GLYPH_WARN="!"     # warning
GLYPH_OK="."       # no-op (does not exist)

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
  # Echo to stdout AND append to log (plain text, no color).
  echo "$1"
  log_action "$1"
}

# Width of the framed output (banner + rules + summary box).
BOX_WIDTH=66

# Print a horizontal rule of BOX_WIDTH dashes. Logs a plain copy.
hr() {
  local line
  line="$(printf '%*s' "${BOX_WIDTH}" '' | tr ' ' '-')"
  printf '%s%s%s\n' "${C_DIM}" "${line}" "${C_RESET}"
  log_action "${line}"
}

# Print a boxed banner with a centered title. Logs a plain copy.
banner() {
  local title="$1"
  local inner=$((BOX_WIDTH - 2))
  local pad_total=$((inner - ${#title}))
  local pad_left=$((pad_total / 2))
  local pad_right=$((pad_total - pad_left))
  local top bottom mid
  top="+$(printf '%*s' "${inner}" '' | tr ' ' '-')+"
  bottom="${top}"
  mid="|$(printf '%*s' "${pad_left}" '')${title}$(printf '%*s' "${pad_right}" '')|"
  printf '%s%s\n%s%s%s%s\n%s%s\n' \
    "${C_CYAN}${C_BOLD}" "${top}" \
    "${C_CYAN}${C_BOLD}" "${mid}" "" "${C_RESET}" \
    "${C_CYAN}${C_BOLD}${bottom}${C_RESET}" ""
  log_action "${top}"
  log_action "${mid}"
  log_action "${bottom}"
}

# Print a section header. Args: $1 = "1/3", $2 = title.
section() {
  local idx="$1" title="$2"
  printf '%s%s[%s]%s %s%s%s\n' \
    "${C_BLUE}${C_BOLD}" "" "${idx}" "${C_RESET}" \
    "${C_BOLD}" "${title}" "${C_RESET}"
  log_action "[${idx}] ${title}"
}

# Print an indented status line with a colored glyph.
# Args: $1 = kind (remove|skip|warn|ok), $2 = message.
status() {
  local kind="$1" msg="$2"
  local glyph color
  case "${kind}" in
    remove) glyph="${GLYPH_REMOVE}"; color="${C_GREEN}" ;;
    skip)   glyph="${GLYPH_SKIP}";   color="${C_DIM}"   ;;
    warn)   glyph="${GLYPH_WARN}";   color="${C_YELLOW}";;
    ok)     glyph="${GLYPH_OK}";     color="${C_DIM}"   ;;
    *)      glyph="?";               color="${C_RESET}" ;;
  esac
  printf '  %s%s%s %s\n' "${color}" "${glyph}" "${C_RESET}" "${msg}"
  log_action "  ${glyph} ${msg}"
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
        status remove "would remove symlink  ${target_dir}"
      else
        rm "${target_dir}"
        status remove "removed symlink       ${target_dir}"
      fi
      COUNT_REMOVED=$((COUNT_REMOVED + 1))
    else
      status skip "skip (points elsewhere) ${target_dir} -> ${resolved}"
      COUNT_SKIPPED=$((COUNT_SKIPPED + 1))
    fi
  elif [[ -d "${target_dir}" ]]; then
    status skip "skip (real directory)   ${target_dir}"
    COUNT_SKIPPED=$((COUNT_SKIPPED + 1))
  elif [[ -e "${target_dir}" ]]; then
    status warn "warn (not symlink/dir)  ${target_dir}"
    COUNT_WARNED=$((COUNT_WARNED + 1))
  else
    status ok "absent (nothing to do)  ${target_dir}"
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
        status remove "would remove symlink  ${name} -> AGENTS.md"
      else
        rm "${path}"
        status remove "removed symlink       ${name}"
      fi
      COUNT_REMOVED=$((COUNT_REMOVED + 1))
    else
      status skip "skip (points elsewhere) ${name} -> ${resolved}"
      COUNT_SKIPPED=$((COUNT_SKIPPED + 1))
    fi
  elif [[ -e "${path}" ]]; then
    status warn "warn (not a symlink)    ${name}"
    COUNT_WARNED=$((COUNT_WARNED + 1))
  else
    status ok "absent (nothing to do)  ${name}"
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

banner "scicomp-research-skills  uninstall"
note ""

# Mode line, colorized by severity.
if (( DRY_RUN )); then
  printf '  %sMode%s    %s%sDRY RUN%s  (no changes will be made; pass -y / --confirm to remove)\n' \
    "${C_BOLD}" "${C_RESET}" "${C_YELLOW}${C_BOLD}" "" "${C_RESET}"
  log_action "  Mode    DRY RUN (no changes will be made; pass -y / --confirm to remove)"
else
  printf '  %sMode%s    %s%sCONFIRMED%s  (changes WILL be made)\n' \
    "${C_BOLD}" "${C_RESET}" "${C_RED}${C_BOLD}" "" "${C_RESET}"
  log_action "  Mode    CONFIRMED (changes WILL be made)"
fi
if (( DEEP )); then
  printf '  %sScope%s   symlinks + git config + canonical checkout (%s--deep%s)\n' \
    "${C_BOLD}" "${C_RESET}" "${C_BOLD}" "${C_RESET}"
  log_action "  Scope   symlinks + git config + canonical checkout (--deep)"
else
  printf '  %sScope%s   symlinks only\n' "${C_BOLD}" "${C_RESET}"
  log_action "  Scope   symlinks only"
fi
printf '  %sFrom%s    %s\n' "${C_BOLD}" "${C_RESET}" "${REPO_ROOT_ABS}"
log_action "  From    ${REPO_ROOT_ABS}"
printf '  %sLog%s     %s\n' "${C_BOLD}" "${C_RESET}" "${LOG_FILE}"
log_action "  Log     ${LOG_FILE}"
note ""

# ----------------------------------------------------------------------
# Phase 1: user-home skill-discovery symlinks.
# ----------------------------------------------------------------------

section "1/3" "User-home skill-discovery symlinks"

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
section "2/3" "In-repo filename symlinks"

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
  section "3/3" "Deep uninstall: git config + canonical checkout"

  # 3a. git config core.hooksPath unset.
  if (( DRY_RUN )); then
    status remove "would unset           git config core.hooksPath in ${REPO_ROOT_ABS}"
  else
    if git -C "${REPO_ROOT_ABS}" config --get core.hooksPath >/dev/null 2>&1; then
      git -C "${REPO_ROOT_ABS}" config --unset core.hooksPath
      status remove "unset                 git config core.hooksPath"
      COUNT_REMOVED=$((COUNT_REMOVED + 1))
    else
      status ok "absent (nothing to do)  git config core.hooksPath was not set"
      COUNT_SKIPPED=$((COUNT_SKIPPED + 1))
    fi
  fi

  # 3b. Delete the canonical checkout (only if THIS checkout IS the canonical one).
  CANONICAL_ABS="$(cd "${CANONICAL}" 2>/dev/null && pwd -P || echo "")"

  if [[ -z "${CANONICAL_ABS}" ]]; then
    status ok "absent (nothing to do)  canonical checkout ${CANONICAL}"
    COUNT_SKIPPED=$((COUNT_SKIPPED + 1))
  elif [[ "${REPO_ROOT_ABS}" != "${CANONICAL_ABS}" ]]; then
    status warn "warn (not canonical)    ${REPO_ROOT_ABS}"
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
      status warn "refused (unexpected path) ${CANONICAL_ABS}"
      note "        expected ${EXPECTED_CANONICAL_ABS}; refusing to delete."
      COUNT_WARNED=$((COUNT_WARNED + 1))
    elif (( DRY_RUN )); then
      status remove "would delete checkout ${CANONICAL_ABS}"
      printf '    %s(dev checkouts at any other path are NOT touched)%s\n' "${C_DIM}" "${C_RESET}"
      log_action "    (dev checkouts at any other path are NOT touched)"
    else
      # Interactive confirmation unless --yes was also passed.
      if (( ! ASSUME_YES )); then
        note ""
        printf '%s%s  !! This will RECURSIVELY DELETE the canonical checkout:%s\n' \
          "${C_RED}" "${C_BOLD}" "${C_RESET}"
        printf '%s%s     %s%s\n' "${C_RED}" "${C_BOLD}" "${CANONICAL_ABS}" "${C_RESET}"
        printf '  %sDev checkouts of this repo at any other path are NOT touched.%s\n' \
          "${C_DIM}" "${C_RESET}"
        log_action "  !! This will RECURSIVELY DELETE the canonical checkout: ${CANONICAL_ABS}"
        read -r -p "  Type 'DELETE' to confirm: " confirmation
        log_action "  interactive confirmation prompt: user typed: '${confirmation}'"
        if [[ "${confirmation}" != "DELETE" ]]; then
          status skip "aborted (no 'DELETE')  canonical-checkout deletion"
          COUNT_SKIPPED=$((COUNT_SKIPPED + 1))
        else
          # We're about to delete the directory we're sitting in. cd out first.
          cd "${HOME}"
          rm -rf "${CANONICAL_ABS}"
          status remove "deleted checkout      ${CANONICAL_ABS}"
          COUNT_REMOVED=$((COUNT_REMOVED + 1))
        fi
      else
        # --yes was passed; skip the interactive prompt.
        cd "${HOME}"
        rm -rf "${CANONICAL_ABS}"
        status remove "deleted checkout      ${CANONICAL_ABS} (via -y)"
        COUNT_REMOVED=$((COUNT_REMOVED + 1))
      fi
    fi
  fi
else
  section "3/3" "Deep uninstall"
  status skip "skipped (pass --deep)   git config + canonical checkout"
fi

# ----------------------------------------------------------------------
# Summary.
# ----------------------------------------------------------------------

note ""
hr

if (( DRY_RUN )); then
  printf '  %sSummary%s  %s(dry run -- no changes made)%s\n' \
    "${C_BOLD}" "${C_RESET}" "${C_YELLOW}" "${C_RESET}"
  log_action "  Summary (dry run -- no changes made)"
  REMOVE_LABEL="would remove"
else
  printf '  %sSummary%s\n' "${C_BOLD}" "${C_RESET}"
  log_action "  Summary"
  REMOVE_LABEL="removed"
fi

printf '    %s%s %-12s%s %s%d%s\n' \
  "${C_GREEN}" "${GLYPH_REMOVE}" "${REMOVE_LABEL}" "${C_RESET}" "${C_BOLD}" "${COUNT_REMOVED}" "${C_RESET}"
log_action "    ${GLYPH_REMOVE} ${REMOVE_LABEL}: ${COUNT_REMOVED}"
printf '    %s%s %-12s%s %s%d%s\n' \
  "${C_DIM}" "${GLYPH_SKIP}" "skipped" "${C_RESET}" "${C_BOLD}" "${COUNT_SKIPPED}" "${C_RESET}"
log_action "    ${GLYPH_SKIP} skipped: ${COUNT_SKIPPED}"
# Warnings line: highlight in yellow only when non-zero.
if (( COUNT_WARNED > 0 )); then
  printf '    %s%s %-12s %d%s\n' \
    "${C_YELLOW}${C_BOLD}" "${GLYPH_WARN}" "warnings" "${COUNT_WARNED}" "${C_RESET}"
else
  printf '    %s%s %-12s%s %s%d%s\n' \
    "${C_DIM}" "${GLYPH_WARN}" "warnings" "${C_RESET}" "${C_BOLD}" "${COUNT_WARNED}" "${C_RESET}"
fi
log_action "    ${GLYPH_WARN} warnings: ${COUNT_WARNED}"

if (( DRY_RUN )); then
  note ""
  if (( DEEP )); then
    next_cmd="$0 --deep --confirm"
  else
    next_cmd="$0 --confirm"
  fi
  printf '  %sNext%s   to apply, re-run:  %s%s%s\n' \
    "${C_BOLD}" "${C_RESET}" "${C_CYAN}" "${next_cmd}" "${C_RESET}"
  log_action "  Next   to apply, re-run: ${next_cmd}"
fi

hr
log_action "==== uninstall.sh complete ===="
