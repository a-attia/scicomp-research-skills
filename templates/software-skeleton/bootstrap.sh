#!/usr/bin/env bash
#
# bootstrap.sh -- delegate package scaffolding to an upstream community
#                 template, on top of the paper-coupling layers already
#                 supplied by scicomp-research-skills/templates/software-skeleton/.
#
# This script is intended to be run ONCE, immediately after copying the
# scicomp-research-skills software-skeleton into a fresh project directory.
# It runs `copier copy` against your chosen upstream template, which will
# add the package files (build manifest, source layout, tests scaffold,
# docs scaffold, pre-commit + CI configs, etc.) without overwriting the
# paper-coupling files we already provided (AGENTS.md, PLAN.md, README.md,
# CITATION.cff, experiments/, figures/, notes/, references/,
# .github/ISSUE_TEMPLATE/).
#
# RATIONALE: scientific-python/cookie + NLeSC/python-template +
# CU-DBMI/template-uv-python-research-software (Python) and
# JuliaBesties/BestieTemplate.jl (Julia) are mature, well-maintained
# community templates. We do not duplicate their work; we add a thin
# paper-coupling layer on top.
#
# LANGUAGE COVERAGE: this script bundles defaults for Python (most
# documented; the audit's primary recommendation) and Julia (the
# secondary supported language; uses BestieTemplate.jl which itself is
# explicitly modeled on NLeSC/python-template). For C++, Rust, Fortran,
# MATLAB, Mathematica, and other languages: no upstream is bundled --
# use your community's standard scaffolding (cmake init, cargo new, an
# fpm package, etc.); the paper-coupling layer in this template applies
# regardless. See MULTI-LANGUAGE.md for the per-language guidance.
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

  Python (default; best-supported):

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

  Julia (secondary):

    julia     JuliaBesties/BestieTemplate.jl (MPL-2.0; modeled on
                                           NLeSC/python-template; copier-
                                           based via PythonCall; ships
                                           with a CLAUDE.md, GitHub
                                           Actions, Documenter, Codecov,
                                           CITATION.cff). Recommended
                                           default for Julia research
                                           software.

  Other languages (C++, Rust, Fortran, MATLAB, Mathematica, ...):

    No upstream is bundled in this script. Use your community's
    standard scaffolding (e.g. `cmake init`, `cargo new`, an `fpm`
    package, etc.); the paper-coupling layer (AGENTS.md / PLAN.md /
    README.md / experiments/ / figures/ / notes/ / references/ /
    CITATION.cff) applies regardless of language. See
    MULTI-LANGUAGE.md for per-language guidance.

EXAMPLES:
  ./bootstrap.sh cookie       # Python; scientific-python/cookie
  ./bootstrap.sh nlesc        # Python; NLeSC/python-template
  ./bootstrap.sh uv-cu        # Python; CU-DBMI uv-first template
  ./bootstrap.sh julia        # Julia; JuliaBesties/BestieTemplate.jl

NOTES:
  - The upstream template will run interactively, asking you for project
    name, author, license choice, etc.
  - copier will detect the files we already provide (AGENTS.md, PLAN.md,
    README.md, CITATION.cff, experiments/, figures/, notes/, references/,
    .github/ISSUE_TEMPLATE/) and ask before overwriting. ALWAYS keep our
    versions of those files; the upstream template should only add the
    package layer.
  - After the upstream template finishes, review the generated build
    manifest (pyproject.toml for Python; Project.toml for Julia) and
    adjust dependency lists, supported-version range (per SPEC 0 for
    Python: last 3 minor versions; per Julia LTS+current convention
    for Julia), and project metadata to match PLAN.md.
  - This script does NOT install dependencies. After it finishes, run
    your environment manager's sync command (uv sync, pixi install,
    pip install -e ".[dev]", `julia --project=. -e 'using Pkg;
    Pkg.instantiate()'`, etc.).

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

LANGUAGE=""

case "${TEMPLATE}" in
  cookie)
    UPSTREAM="gh:scientific-python/cookie"
    LANGUAGE="python"
    echo "[bootstrap] Using ${UPSTREAM} (BSD-3-Clause; Python)."
    ;;
  nlesc)
    UPSTREAM="gh:NLeSC/python-template"
    LANGUAGE="python"
    echo "[bootstrap] Using ${UPSTREAM} (Apache-2.0; Python)."
    ;;
  uv-cu)
    UPSTREAM="gh:CU-DBMI/template-uv-python-research-software"
    LANGUAGE="python"
    echo "[bootstrap] Using ${UPSTREAM} (BSD-3-Clause; Python; uv-first)."
    ;;
  julia)
    UPSTREAM="gh:JuliaBesties/BestieTemplate.jl"
    LANGUAGE="julia"
    echo "[bootstrap] Using ${UPSTREAM} (MPL-2.0; Julia)."
    ;;
  -h|--help)
    usage
    exit 0
    ;;
  *)
    echo "ERROR: unknown template '${TEMPLATE}'." >&2
    echo "" >&2
    echo "For C++ / Rust / Fortran / MATLAB / Mathematica and other" >&2
    echo "languages, no upstream is bundled; see MULTI-LANGUAGE.md for" >&2
    echo "per-language guidance. Use your community's standard" >&2
    echo "scaffolding for the package layer; the paper-coupling layer" >&2
    echo "in this template applies regardless." >&2
    echo "" >&2
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

# ---------------------------------------------------------------------------
# Language-specific next-step guidance.
# ---------------------------------------------------------------------------

if [ "${LANGUAGE}" = "python" ]; then
  cat <<EOF
Next steps (Python):
  1. Review generated pyproject.toml; adjust dependencies + Python
     version range (per SPEC 0: last 3 minor versions).
  2. Install dev dependencies (e.g. 'uv sync --all-extras --dev'
     or 'pip install -e ".[dev]"').
  3. Verify the test suite runs ('pytest').
  4. Verify the repo passes Scientific Python repo-review:
     uvx sp-repo-review[cli] .
  5. Fill in the placeholders in AGENTS.md, PLAN.md, README.md,
     and CITATION.cff. Update PLAN.md "Project facts" to record:
       - Language: Python <X.Y>+
       - Build backend: <whatever the upstream chose>
       - Environment manager: <uv / pixi / conda / pip-tools>
       - Test framework: <pytest / unittest / pytest+hypothesis>
  6. Make the first commit:
     git add . && git commit -m 'chore: bootstrap from
     scicomp-research-skills/templates/software-skeleton/ +
     ${TEMPLATE} upstream'
EOF
elif [ "${LANGUAGE}" = "julia" ]; then
  cat <<EOF
Next steps (Julia):
  1. Review generated Project.toml; adjust [deps] and [compat]
     entries + supported-Julia-version range (per Julia LTS +
     current-stable convention).
  2. Instantiate the environment:
     julia --project=. -e 'using Pkg; Pkg.instantiate()'
  3. Verify the test suite runs:
     julia --project=. -e 'using Pkg; Pkg.test()'
  4. Fill in the placeholders in AGENTS.md, PLAN.md, README.md,
     and CITATION.cff. Update PLAN.md "Project facts" to record:
       - Language: Julia <X.Y>+
       - Build / packaging: BestieTemplate.jl-generated Project.toml
       - Test framework: Test.jl (or TestItemRunner.jl, etc.)
     Update sections of AGENTS.md / PLAN.md / README.md whose
     placeholders show Python defaults (e.g. 'pip install',
     'pyproject.toml', 'src/<library_name>/__init__.py') to
     reflect Julia conventions instead. See MULTI-LANGUAGE.md
     for the placeholder-translation table.
  5. Make the first commit:
     git add . && git commit -m 'chore: bootstrap from
     scicomp-research-skills/templates/software-skeleton/ +
     ${TEMPLATE} upstream'
EOF
fi
