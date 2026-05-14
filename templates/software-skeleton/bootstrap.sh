#!/usr/bin/env bash
#
# bootstrap.sh -- delegate package scaffolding to an upstream community
#                 template, on top of the paper-coupling layers already
#                 supplied by scicomp-research-skills/templates/software-skeleton/.
#
# This script is intended to be run ONCE, immediately after copying the
# scicomp-research-skills software-skeleton into a fresh project directory.
# It runs `copier copy` against your chosen upstream template, which will
# add the package files (pyproject.toml, src/, tests/, docs/, .pre-commit
# config, GitHub Actions workflows, etc.) without overwriting the
# paper-coupling files we already provided (AGENTS.md, PLAN.md, README.md,
# CITATION.cff, experiments/, figures/, notes/, references/,
# .github/ISSUE_TEMPLATE/).
#
# RATIONALE: scientific-python/cookie + NLeSC/python-template +
# CU-DBMI/template-uv-python-research-software are all mature, well-
# maintained community templates for Python research software. We do not
# duplicate their work; we add a thin paper-coupling layer on top.
#
# REQUIRES: copier (https://copier.readthedocs.io). Install via:
#   pipx install copier
#   # OR
#   uv tool install copier

set -euo pipefail

# ---------------------------------------------------------------------------
# Available upstream templates.
# ---------------------------------------------------------------------------

usage() {
  cat <<'EOF'
bootstrap.sh -- run an upstream copier template for the package layer.

USAGE:
  ./bootstrap.sh <template>

TEMPLATES:
  cookie    scientific-python/cookie    (BSD-3-Clause; the de-facto
                                         scientific Python community
                                         template; supports 10 build
                                         backends including pure-Python,
                                         pybind11, scikit-build,
                                         maturin, meson-python).
                                         Recommended default for most
                                         pure-Python or
                                         compiled-extension libraries.

  nlesc     NLeSC/python-template       (Apache-2.0; explicitly research-
                                         software-flavoured;
                                         FAIR-software-aware; auto-
                                         creates GitHub issues with
                                         next-step instructions for
                                         Zenodo + ReadTheDocs setup).
                                         Choose this if you want
                                         FAIR-software badges + the
                                         issue-checklist pattern.

  uv-cu     CU-DBMI/template-uv-python-research-software (BSD-3-Clause;
                                         uv-first; assumes a uv-managed
                                         environment throughout).
                                         Choose this if your team is
                                         already standardised on uv.

EXAMPLES:
  ./bootstrap.sh cookie
  ./bootstrap.sh nlesc
  ./bootstrap.sh uv-cu

NOTES:
  - The upstream template will run interactively, asking you for project
    name, author, license choice, etc.
  - copier will detect the files we already provide (AGENTS.md, PLAN.md,
    README.md, CITATION.cff, experiments/, figures/, notes/, references/,
    .github/ISSUE_TEMPLATE/) and ask before overwriting. ALWAYS keep our
    versions of those files; the upstream template should only add the
    package layer.
  - After the upstream template finishes, review the generated
    pyproject.toml and adjust the dependency list, Python-version range
    (per SPEC 0: last 3 minor versions), and project metadata to match
    PLAN.md.
  - This script does NOT install dependencies. After it finishes, run
    your environment manager's sync command (uv sync, pixi install,
    pip install -e ".[dev]", etc.).

EOF
}

if [ $# -ne 1 ]; then
  usage
  exit 2
fi

TEMPLATE="$1"

# ---------------------------------------------------------------------------
# Pre-flight checks.
# ---------------------------------------------------------------------------

if ! command -v copier >/dev/null 2>&1; then
  echo "ERROR: copier is not installed." >&2
  echo "Install via:  pipx install copier   OR   uv tool install copier" >&2
  exit 1
fi

if [ ! -f "AGENTS.md" ] || [ ! -f "PLAN.md" ]; then
  echo "ERROR: this script must be run from the project root, AFTER" >&2
  echo "       copying scicomp-research-skills/templates/software-skeleton/" >&2
  echo "       contents into the project directory." >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Dispatch.
# ---------------------------------------------------------------------------

case "${TEMPLATE}" in
  cookie)
    UPSTREAM="gh:scientific-python/cookie"
    echo "[bootstrap] Using ${UPSTREAM} (BSD-3-Clause)."
    ;;
  nlesc)
    UPSTREAM="gh:NLeSC/python-template"
    echo "[bootstrap] Using ${UPSTREAM} (Apache-2.0)."
    ;;
  uv-cu)
    UPSTREAM="gh:CU-DBMI/template-uv-python-research-software"
    echo "[bootstrap] Using ${UPSTREAM} (BSD-3-Clause)."
    ;;
  -h|--help)
    usage
    exit 0
    ;;
  *)
    echo "ERROR: unknown template '${TEMPLATE}'." >&2
    echo >&2
    usage >&2
    exit 2
    ;;
esac

echo
echo "[bootstrap] Running: copier copy ${UPSTREAM} ."
echo "[bootstrap] copier will ask before overwriting any existing file."
echo "[bootstrap] ALWAYS KEEP our paper-coupling files (AGENTS.md, PLAN.md,"
echo "[bootstrap] README.md, CITATION.cff, experiments/, figures/, notes/,"
echo "[bootstrap] references/, .github/ISSUE_TEMPLATE/) -- the upstream"
echo "[bootstrap] template should only add the package layer."
echo

copier copy "${UPSTREAM}" .

echo
echo "[bootstrap] Done."
echo
echo "Next steps:"
echo "  1. Review generated pyproject.toml; adjust dependencies + Python"
echo "     version range (per SPEC 0: last 3 minor versions)."
echo "  2. Install dev dependencies (e.g. 'uv sync --all-extras --dev'"
echo "     or 'pip install -e \".[dev]\"')."
echo "  3. Verify the test suite runs ('pytest')."
echo "  4. Verify the repo passes Scientific Python repo-review:"
echo "     uvx sp-repo-review[cli] ."
echo "  5. Fill in the placeholders in AGENTS.md, PLAN.md, README.md,"
echo "     and CITATION.cff."
echo "  6. Make the first commit:"
echo "     git add . && git commit -m 'chore: bootstrap from"
echo "     scicomp-research-skills/templates/software-skeleton/ +"
echo "     ${TEMPLATE} upstream'"
