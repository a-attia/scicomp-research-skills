#!/usr/bin/env bash
#
# privacy-scan.sh -- check text bound for a public surface (this repo,
#                    its commit messages, GitHub issues / PRs / comments)
#                    for private identifiers before it is published.
#
# Two kinds of check:
#   1. Generic patterns, always on: absolute home paths, email addresses
#      outside a small allowlist, IPv4 addresses, *.local hostnames.
#   2. Personal terms, from a file that lives OUTSIDE every repository:
#        ${XDG_CONFIG_HOME:-$HOME/.config}/scicomp-research-skills/private-terms.txt
#      This repository ships only the mechanism, never the terms. See
#      bin/private-terms.example.txt for the format.
#
# Modes (exactly one):
#   --staged        added lines in the staged diff (pre-commit hook)
#   --msg FILE      a commit message file, '#' comment lines ignored
#                   (commit-msg hook)
#   --file FILE     any file, or '-' for stdin (issue / PR / comment
#                   bodies before `gh ... --body-file FILE`)
#   --all           every tracked file (audit; CI uses --all --generic)
#
# Options:
#   --generic       skip the personal-terms file (CI has none)
#   -h, --help      show this help
#
# Exit status: 0 clean, 1 findings, 2 usage error.
#
# Findings are printed to stderr only, as "location  category  match",
# with the suggested replacement when the terms file gives one. Nothing
# is written anywhere else, so the scan cannot itself leak a term.
#
# ASCII-only; portable across BSD (macOS) and GNU userlands.

set -euo pipefail

CONFIG_DIR="${XDG_CONFIG_HOME:-${HOME}/.config}/scicomp-research-skills"
TERMS_FILE="${SCICOMP_PRIVATE_TERMS:-${CONFIG_DIR}/private-terms.txt}"
ALLOW_FILE="${SCICOMP_ALLOWED_TERMS:-${CONFIG_DIR}/allowed-terms.txt}"

# Email addresses that are fine anywhere (ERE, matched case-insensitively
# against the whole address).
EMAIL_ALLOW='^(noreply@anthropic\.com|git@github\.com|[^@]+@users\.noreply\.github\.com|[^@]+@example\.(com|org|net))$'

# Files exempt from the generic checks, because identity in them is
# intentional (commit-author mapping) or because they hold the patterns
# themselves.
GENERIC_EXEMPT='^(\.mailmap|bin/privacy-scan\.sh|bin/private-terms\.example\.txt)$'
# Files exempt from the personal-terms check. .mailmap maps commit
# identities, which are already public in every commit's metadata.
TERMS_EXEMPT='^\.mailmap$'

usage() { sed -n '3,33p' "$0" | sed 's/^# \{0,1\}//'; }

MODE=""
ARG=""
GENERIC_ONLY=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --staged|--all) MODE="${1#--}"; shift ;;
    --msg|--file)
      [[ $# -ge 2 ]] || { echo "privacy-scan: $1 needs an argument" >&2; exit 2; }
      MODE="${1#--}"; ARG="$2"; shift 2 ;;
    --generic) GENERIC_ONLY=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "privacy-scan: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ -n "${MODE}" ]] || { usage >&2; exit 2; }

WORK="$(mktemp -d "${TMPDIR:-/tmp}/privacy-scan.XXXXXX")"
trap 'rm -rf "${WORK}"' EXIT

# ----------------------------------------------------------------------
# Build the input as "location<TAB>text" lines in ${WORK}/input.
# ----------------------------------------------------------------------

INPUT="${WORK}/input"
: > "${INPUT}"

emit_file() {
  # $1 = display name, $2 = path; append numbered lines.
  awk -v f="$1" '{ printf "%s:%d\t%s\n", f, NR, $0 }' "$2" >> "${INPUT}"
}

case "${MODE}" in
  staged)
    # Added lines only, so pre-existing text never blocks an unrelated
    # commit. Track the target file and line number from the hunk headers.
    git diff --cached -U0 --no-color --no-ext-diff --diff-filter=ACMR \
      | awk '
          /^\+\+\+ / { f = substr($0, 7); next }
          /^@@ /     { split($3, a, ","); n = substr(a[1], 2) + 0; next }
          /^\+/      { printf "%s:%d\t%s\n", f, n, substr($0, 2); n++ }
        ' >> "${INPUT}"
    ;;
  msg)
    [[ -r "${ARG}" ]] || { echo "privacy-scan: cannot read ${ARG}" >&2; exit 2; }
    grep -v '^#' "${ARG}" > "${WORK}/msg" || true
    emit_file "commit-message" "${WORK}/msg"
    ;;
  file)
    if [[ "${ARG}" == "-" ]]; then
      cat > "${WORK}/stdin"
      emit_file "stdin" "${WORK}/stdin"
    else
      [[ -r "${ARG}" ]] || { echo "privacy-scan: cannot read ${ARG}" >&2; exit 2; }
      emit_file "${ARG}" "${ARG}"
    fi
    ;;
  all)
    while IFS= read -r -d '' f; do
      [[ -f "${f}" ]] || continue
      # Skip binary files.
      if LC_ALL=C grep -Iq . "${f}" 2>/dev/null; then emit_file "${f}" "${f}"; fi
    done < <(git ls-files -z)
    ;;
esac

# ----------------------------------------------------------------------
# Checks. Each appends "location<TAB>category<TAB>match<TAB>suggest".
# ----------------------------------------------------------------------

HITS="${WORK}/hits"
: > "${HITS}"

# scan_re <input-file> <category> <grep-flags> <ERE> <suggestion> [<skip ERE>]
# Input is "location<TAB>text". grep -E is used rather than awk because
# BSD awk lacks interval expressions ({n}) and mangles '\.' passed via -v.
scan_re() {
  local in="$1" cat="$2" flags="$3" re="$4" sugg="$5" skip="${6:-}"
  cut -f1 "${in}" > "${WORK}/locs"
  cut -f2- "${in}" > "${WORK}/text"
  # shellcheck disable=SC2086  # flags is a deliberate word list
  { grep -n -o ${flags} -e "${re}" "${WORK}/text" 2>/dev/null || true; } \
    | awk -v cat="${cat}" -v sugg="${sugg}" '
        NR == FNR { loc[NR] = $0; next }
        {
          n = $0; sub(/:.*/, "", n)
          m = $0; sub(/^[0-9]+:/, "", m)
          printf "%s\t%s\t%s\t%s\n", loc[n], cat, m, sugg
        }' "${WORK}/locs" - \
    | if [[ -n "${skip}" ]]; then
        awk -F'\t' -v skip="${skip}" '$3 !~ skip'
      else
        cat
      fi >> "${HITS}"
}

# Lines eligible for generic checks (drop exempt files).
awk -F'\t' -v ex="${GENERIC_EXEMPT}" '{
    loc = $1; sub(/:[0-9]+$/, "", loc)
    if (loc !~ ex) print
  }' "${INPUT}" > "${WORK}/generic_input"

GI="${WORK}/generic_input"
HOME_TAIL='[A-Za-z0-9._-]+'
scan_re "${GI}" home-path -E "(/Users|/home)/${HOME_TAIL}" '<home> or a ~ path' \
  '^/(Users|home)/(user|username|name|me|you|runner)$'
scan_re "${GI}" home-path -E "[Cc]:[\\\\]+Users[\\\\]+${HOME_TAIL}" '%USERPROFILE% or <home>'
scan_re "${GI}" ipv4 -E '[0-9]{1,3}[.][0-9]{1,3}[.][0-9]{1,3}[.][0-9]{1,3}' '<host>' \
  '^(127[.]0[.]0[.]1|0[.]0[.]0[.]0)$'
scan_re "${GI}" local-host -E '[A-Za-z0-9-]+[.]local' '<host>'

# Emails: extract, then drop allowlisted addresses.
scan_re "${GI}" email -E '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+[.][A-Za-z]{2,}' '<email> or a noreply address'
if [[ -s "${HITS}" ]]; then
  awk -F'\t' -v allow="${EMAIL_ALLOW}" '
      $2 != "email" { print; next }
      { a = tolower($3); if (a !~ allow) print }' "${HITS}" > "${WORK}/hits2"
  mv "${WORK}/hits2" "${HITS}"
fi

# Personal terms.
TERMS_USED=0
if (( ! GENERIC_ONLY )) && [[ -r "${TERMS_FILE}" ]]; then
  TERMS_USED=1
  awk -F'\t' -v ex="${TERMS_EXEMPT}" '{
      loc = $1; sub(/:[0-9]+$/, "", loc)
      if (loc !~ ex) print
    }' "${INPUT}" > "${WORK}/terms_input"
  while IFS= read -r line || [[ -n "${line}" ]]; do
    line="${line%$'\r'}"
    [[ -z "${line//[[:space:]]/}" || "${line}" == \#* ]] && continue
    pat="${line%%==>*}"
    sugg=""
    [[ "${line}" == *"==>"* ]] && sugg="${line#*==>}"
    if [[ "${pat}" == regex:* ]]; then
      scan_re "${WORK}/terms_input" private-term -Ei "${pat#regex:}" "${sugg:-<generic descriptor>}"
    else
      scan_re "${WORK}/terms_input" private-term -Fi "${pat}" "${sugg:-<generic descriptor>}"
    fi
  done < "${TERMS_FILE}"
fi

# Allowed terms: drop hits whose match is listed (case-insensitive,
# whole match).
if [[ -r "${ALLOW_FILE}" ]]; then
  grep -v '^[[:space:]]*\(#\|$\)' "${ALLOW_FILE}" > "${WORK}/allow" || true
  if [[ -s "${WORK}/allow" ]]; then
    # (Guarded: with an empty allow file, awk's NR == FNR idiom would read
    # the hits file as the allow list and silently drop every finding.)
    awk -F'\t' 'NR == FNR { a[tolower($0)] = 1; next } !(tolower($3) in a)' \
      "${WORK}/allow" "${HITS}" > "${WORK}/hits2"
    mv "${WORK}/hits2" "${HITS}"
  fi
fi

# ----------------------------------------------------------------------
# Report.
# ----------------------------------------------------------------------

if (( ! GENERIC_ONLY )) && (( ! TERMS_USED )); then
  echo "privacy-scan: no personal terms file at ${TERMS_FILE}; ran generic checks only." >&2
  echo "privacy-scan: see bin/private-terms.example.txt to create one." >&2
fi

if [[ -s "${HITS}" ]]; then
  sort -u "${HITS}" | awk -F'\t' '{ printf "  %-40s %-13s %s  ->  suggest: %s\n", $1, $2, $3, $4 }' >&2
  count="$(sort -u "${HITS}" | wc -l | tr -d ' ')"
  echo "privacy-scan: ${count} finding(s). Replace with a generic descriptor, or add an intentional exception to ${ALLOW_FILE}." >&2
  exit 1
fi
exit 0
