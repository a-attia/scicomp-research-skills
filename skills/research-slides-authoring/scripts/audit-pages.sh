#!/usr/bin/env bash
#
# audit-pages.sh -- render chosen pages of a slide deck or poster PDF for
#                   visual review, and check that expected text survived
#                   the render.
#
# Part of the research-slides-authoring skill (see ../SKILL.md, rule A1:
# "a clean build is not done"). Toolchain-agnostic: it works on the PDF,
# which Beamer, Marp, PowerPoint, Keynote and reveal.js all produce.
#
# Usage:
#   audit-pages.sh [options] DECK.pdf [PAGES...]
#
#   PAGES       page numbers or inclusive ranges, e.g. 3 7-9 12.
#               Default: every page.
#
# Options:
#   -o DIR      output directory for PNGs (default: .audit/ next to the PDF)
#   -s PX       long-edge size in pixels (default: 1100). Review at about
#               1000-1100 px; there is no benefit above ~1568 px, because
#               model image inputs are downscaled to about that anyway.
#   -e FILE     expected-text file: one string per line that must appear
#               in the extracted text of the WHOLE deck (e.g. every
#               section heading, every slide title). Lines starting with
#               '#' are ignored. Missing strings are reported and make the
#               script exit 1: an overfull slide or flowed poster column
#               can drop a block without any build warning.
#   -h          help
#
# Output: one PNG per requested page, printed as absolute paths, plus a
# one-line page-geometry summary. The script cannot judge layout; it
# makes the look-at-it step cheap. Open every PNG it prints.
#
# Needs poppler (pdftoppm, pdftotext, pdfinfo). macOS: brew install
# poppler. Debian/Ubuntu: apt-get install poppler-utils.

set -euo pipefail

usage() { sed -n '3,33p' "$0" | sed 's/^# \{0,1\}//'; }

OUT=""
SIZE=1100
EXPECT=""
while getopts ":o:s:e:h" opt; do
  case "${opt}" in
    o) OUT="${OPTARG}" ;;
    s) SIZE="${OPTARG}" ;;
    e) EXPECT="${OPTARG}" ;;
    h) usage; exit 0 ;;
    :) echo "audit-pages: -${OPTARG} needs an argument" >&2; exit 2 ;;
    *) echo "audit-pages: unknown option -${OPTARG}" >&2; usage >&2; exit 2 ;;
  esac
done
shift $((OPTIND - 1))

[[ $# -ge 1 ]] || { usage >&2; exit 2; }
PDF="$1"; shift
[[ -r "${PDF}" ]] || { echo "audit-pages: cannot read ${PDF}" >&2; exit 2; }
[[ "${SIZE}" =~ ^[0-9]+$ ]] || { echo "audit-pages: -s needs an integer" >&2; exit 2; }

for tool in pdftoppm pdftotext pdfinfo; do
  command -v "${tool}" >/dev/null 2>&1 || {
    echo "audit-pages: ${tool} not found; install poppler." >&2; exit 2; }
done

PDF_DIR="$(cd "$(dirname "${PDF}")" && pwd -P)"
PDF_ABS="${PDF_DIR}/$(basename "${PDF}")"
STEM="$(basename "${PDF}" .pdf)"
OUT="${OUT:-${PDF_DIR}/.audit}"
mkdir -p "${OUT}"
OUT="$(cd "${OUT}" && pwd -P)"

NPAGES="$(pdfinfo "${PDF_ABS}" | awk '/^Pages:/ { print $2 }')"
GEOM="$(pdfinfo "${PDF_ABS}" | awk -F': *' '/^Page size:/ { print $2 }')"
echo "${STEM}.pdf: ${NPAGES} page(s), ${GEOM}"

# Expand page arguments into a list.
PAGES=()
if [[ $# -eq 0 ]]; then
  for ((p = 1; p <= NPAGES; p++)); do PAGES+=("${p}"); done
else
  for arg in "$@"; do
    if [[ "${arg}" =~ ^([0-9]+)-([0-9]+)$ ]]; then
      for ((p = BASH_REMATCH[1]; p <= BASH_REMATCH[2]; p++)); do PAGES+=("${p}"); done
    elif [[ "${arg}" =~ ^[0-9]+$ ]]; then
      PAGES+=("${arg}")
    else
      echo "audit-pages: not a page or range: ${arg}" >&2; exit 2
    fi
  done
fi

STATUS=0
for p in "${PAGES[@]}"; do
  if (( p < 1 || p > NPAGES )); then
    echo "audit-pages: page ${p} out of range (1-${NPAGES})" >&2
    STATUS=1
    continue
  fi
  base="${OUT}/${STEM}-p$(printf '%03d' "${p}")"
  pdftoppm -png -f "${p}" -l "${p}" -scale-to "${SIZE}" -singlefile "${PDF_ABS}" "${base}"
  echo "${base}.png"
done

# Conservation check: every expected string must survive into the PDF.
if [[ -n "${EXPECT}" ]]; then
  [[ -r "${EXPECT}" ]] || { echo "audit-pages: cannot read ${EXPECT}" >&2; exit 2; }
  TEXT="$(pdftotext -layout "${PDF_ABS}" - | tr -s '[:space:]' ' ')"
  missing=0
  while IFS= read -r want || [[ -n "${want}" ]]; do
    want="${want%$'\r'}"
    [[ -z "${want//[[:space:]]/}" || "${want}" == \#* ]] && continue
    norm="$(printf '%s' "${want}" | tr -s '[:space:]' ' ')"
    if ! printf '%s' "${TEXT}" | grep -Fqi -- "${norm}"; then
      echo "MISSING from rendered text: ${want}" >&2
      missing=$((missing + 1))
    fi
  done < "${EXPECT}"
  if (( missing > 0 )); then
    echo "audit-pages: ${missing} expected string(s) missing; a block may have been dropped or clipped." >&2
    STATUS=1
  else
    echo "audit-pages: all expected strings present."
  fi
fi

echo "Now open each PNG above and check: title on one line; nothing crossing or crowding an edge or the footer; every block present."
exit "${STATUS}"
