# Multi-language guidance

This template is **NOT Python-only** -- but the bundled defaults ARE
Python-centric (per the prior-art audit's recommendation). This file
explains how to reason about which parts of the template apply to
your language + how to adapt the placeholders.

## What's language-agnostic vs Python-centric

The template has two layers:

### Language-agnostic: the paper-coupling layer

These files apply to any scientific-computing project, regardless of
implementation language. Use them as-is:

| File / directory                              | Why it's language-agnostic                                                            |
|:----------------------------------------------|:--------------------------------------------------------------------------------------|
| `AGENTS.md`                                   | Agent entry point; the conventions are about workflow, not language.                  |
| `PLAN.md`                                     | Plan-of-record; sections (headline goal, scope, milestones, decisions log, lifecycle) apply universally. |
| `README.md`                                   | Human-facing; the structure (status / install / quick example / experiments / coupled-paper / citation / authors) applies regardless of language. |
| `CITATION.cff`                                | The CFF format is language-agnostic; supported by GitHub + Zenodo for any repo.       |
| `experiments/` + `experiments/README.md`     | The `<run-id>/metadata.json` schema (commit hash, lockfile hash, RNG seed, hardware, wall-clock) applies to any code that produces numerical results. |
| `figures/` + `figures/README.md`             | Figure-generation provenance discipline applies regardless of which language generated the figure (matplotlib / Plots.jl / gnuplot / ROOT). |
| `notes/` + `notes/{README.md, agent_feedback.md}` | Working-notes layout + feedback channel apply to any project. |
| `references/_collection_log.md`              | Algorithmic-source citations (papers cited in code comments) apply to any language.   |
| `.github/ISSUE_TEMPLATE/`                    | Numerical-correctness regression / API ergonomics / performance regression -- all three apply to any numerical code. |

### Python-centric: the defaults you may need to adapt

These files have **Python-specific defaults** that you can either
keep (if you ARE writing Python) or adapt + record the deviation in
per-project AGENTS.md "Project-specific overrides":

| File                         | Python-centric content                                                                                  | What to adapt for other languages                                                                                                                            |
|:-----------------------------|:--------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `bootstrap.sh`               | Defaults bundle Python upstream templates (cookie / NLeSC / CU-DBMI). Julia is supported via `julia` option (BestieTemplate.jl). Other languages: don't run bootstrap.sh; scaffold the package layer with your community's tool. | For Julia: run `./bootstrap.sh julia`. For C++/Rust/Fortran/etc.: skip bootstrap.sh; use `cmake init` / `cargo new` / `fpm new` / etc.                       |
| `README.md` "Install" section | Shows `pip install` example.                                                                            | Replace with your language's install command (e.g. `Pkg.add("LibraryName")` for Julia; `cargo add library-name` for Rust; per-platform `cmake --install` for C++; etc.). |
| `README.md` "Quick example"   | Shows Python code block.                                                                                | Replace with an equivalent example in your language.                                                                                                         |
| `README.md` "How this repo is organised" | Annotated tree shows Python conventions (`src/<library_name>/`, `__init__.py`, `_diagnostics.py`).                           | Update tree to your language's conventions (e.g. `src/LibraryName/` + `LibraryName.jl` for Julia; `include/<library>/` + `src/` for C++; `src/lib.rs` for Rust). |
| `README.md` "Numerical correctness + testing" | Shows `pytest` invocations.                                                                                                          | Replace with your language's test runner invocation (`Pkg.test()` for Julia; `ctest` for C++; `cargo test` for Rust).                                          |
| `README.md` "Pinned dependencies" | Mentions `uv.lock` / `pixi.lock` / `conda-lock.yml`.                                                                                | Mention your language's lockfile (`Manifest.toml` for Julia; `Cargo.lock` for Rust; vcpkg manifest for C++; pinned commit hashes for Fortran/MATLAB).            |
| `README.md` "Development" section | Mentions Scientific Python repo-review.                                                                                              | Replace with your community's lint / format / repo-quality tool (Aqua.jl + JET.jl for Julia; clang-tidy for C++; clippy for Rust).                              |
| `PLAN.md` "Architecture"     | ASCII tree shows Python `src/` layout.                                                                                                                | Update to match your language's conventions (per the table above).                                                                                            |
| `PLAN.md` "Reproducibility infrastructure" | Lockfile examples are Python-flavoured.                                                                                              | Use your language's lockfile + environment-manager terminology.                                                                                                |
| `AGENTS.md` "Project-specific facts" | Default placeholders mention `Python 3.11+ / Julia 1.10+ / C++17 / mixed`, `hatchling / setuptools / scikit-build-core / poetry / uv-managed` (Python build backends), `pytest / unittest / pytest+hypothesis` (Python test frameworks). | Fill in your language's specifics (e.g. for Julia: `Build / packaging: Project.toml + Pkg.jl`; `Test framework: Test.jl + TestItemRunner.jl + Aqua.jl`).         |
| `.gitignore`                 | Includes Python-specific patterns (`__pycache__`, `*.py[cod]`, `.pytest_cache/`, `.ruff_cache/`, `.tox/`, `.nox/`, `.venv/`).         | The patterns are harmless for non-Python projects (no false matches), but feel free to remove them if cleanliness matters; ADD your language's equivalents (`Manifest.toml.bak` for Julia; `target/` for Rust; `build/` for C++; etc.). |
| `CITATION.cff` validation hint | Suggests `cffconvert` (Python tool).                                                                                                  | `cffconvert` works for any project's CITATION.cff; no change needed. (CITATION.cff itself is language-agnostic.)                                                |
| `references/_collection_log.md` | Per-component subsections example uses `src/<library>/core/` (Python).                                                              | Update to your language's source layout.                                                                                                                       |

## Per-language quick reference

### Python (default)

The template's defaults assume Python. Run `./bootstrap.sh cookie`
(or `nlesc` / `uv-cu`) and proceed with Python conventions as-is.

### Julia

1. Run `./bootstrap.sh julia` -- delegates to
   [`JuliaBesties/BestieTemplate.jl`](https://github.com/JuliaBesties/BestieTemplate.jl)
   (MPL-2.0; explicitly modeled on NLeSC/python-template; uses
   copier under the hood via PythonCall; ships with CLAUDE.md,
   GitHub Actions for tests + docs, Documenter, Codecov,
   CITATION.cff).
2. After bootstrap, edit `AGENTS.md`, `PLAN.md`, `README.md`,
   `CITATION.cff` to use Julia conventions per the table above.
3. The `experiments/<run-id>/metadata.json` schema needs no change;
   `code.library_commit` works for any git-versioned code regardless
   of language.
4. The `notes/`, `figures/`, `references/`, and
   `.github/ISSUE_TEMPLATE/` content all transfers as-is.
5. **Heads up**: BestieTemplate.jl ships its own `CLAUDE.md`. Per
   the framework's "AGENTS.md as canonical" convention (see
   `~/.scicomp-research-skills/skills/project-onboarding/references/scenario-2-existing-agentic-files.md`),
   convert that `CLAUDE.md` to a symlink to your project's
   `AGENTS.md` after bootstrap. Apply Scenario 2.A from the
   project-onboarding skill.

### C++

1. **Don't run bootstrap.sh.** Use your community's standard
   scaffolding (`cmake init`, `meson init`, vcpkg manifest, Conan
   recipe, etc.) for the package layer.
2. Useful C++ scientific-computing scaffolds to consider:
   - `cpp-best-practices/cmake_template` (MIT; modern CMake +
     pre-commit + clang-tidy + clang-format).
   - `vector-of-bool/pitchfork` -- a layout convention popular in
     scientific C++ (`src/`, `include/`, `tests/`, `examples/`,
     `external/`).
   - For HPC: PETSc-style + Trilinos-style conventions.
3. Adapt the placeholders per the table above. In particular:
   - `README.md` "Install" -> `cmake --install` or
     `vcpkg install <pkg>` or distro-specific package.
   - `PLAN.md` "Architecture" -> use `include/<lib>/` + `src/` +
     `tests/` layout.
   - `README.md` "Numerical correctness + testing" -> use Catch2 /
     GoogleTest / Boost.Test invocation.
4. The paper-coupling layer (experiments/, figures/, notes/,
   references/) transfers as-is.

### Rust

1. **Don't run bootstrap.sh.** Use `cargo new --lib <name>` for the
   package layer.
2. Useful Rust scientific-computing context:
   - The Rust scientific-computing ecosystem is younger than
     Python's; check what's stable for your domain (ndarray,
     nalgebra, faer, candle, etc.) before building.
3. Adapt placeholders per the table above:
   - `README.md` "Install" -> `cargo add <library-name>`.
   - `PLAN.md` "Architecture" -> `src/lib.rs` + `src/<modules>/` +
     `tests/` + `benches/` + `examples/`.
   - `README.md` "Numerical correctness + testing" -> `cargo test`.
4. The paper-coupling layer transfers as-is.

### Fortran

1. **Don't run bootstrap.sh.** Use `fpm new <name>` (Fortran
   Package Manager) or set up a CMake build by hand.
2. Useful context:
   - `fortran-lang/fpm` is the modern Fortran package manager;
     comparable to `cargo`.
   - For HPC Fortran (most legacy scientific codes): keep an
     informative Makefile + clear documentation of compiler flag
     choices (`-fopenmp`, `-fdefault-real-8`, etc.).
3. Adapt placeholders per the table above.
4. The paper-coupling layer transfers as-is.

### MATLAB / Octave

1. **Don't run bootstrap.sh.** MATLAB doesn't have a copier-style
   community template ecosystem; structure is conventional rather
   than enforced.
2. Suggested MATLAB layout (mirrors Python's `src/tests/docs/`):
   - `src/+<package>/` (use a MATLAB package directory).
   - `tests/` (use MATLAB unit-test framework).
   - `docs/` (use `publish` or external docs).
3. Adapt placeholders per the table above.
4. The paper-coupling layer transfers as-is.
5. **Reproducibility note**: MATLAB version-pinning is harder than
   Python's lockfiles. Record the MATLAB version + toolbox versions
   used in `experiments/<run-id>/metadata.json` under
   `environment.matlab_version` / `environment.toolboxes`.

### Mathematica / Wolfram

1. **Don't run bootstrap.sh.** No copier-style template community.
2. Use Wolfram's package layout: `<Package>/Kernel/` +
   `<Package>/PacletInfo.m` + `<Package>/Tests/`.
3. Adapt placeholders.
4. **Reproducibility note**: same as MATLAB -- record Mathematica
   version + license type (Player vs Home vs full) in
   `experiments/<run-id>/metadata.json`.

### Mixed-language projects (e.g. Python + C++ extension via pybind11)

If your library is primarily one language with extension modules in
another:

- **Python + C/C++ extension**: use `./bootstrap.sh cookie` and pick
  the `pybind11` / `scikit-build-core` / `meson-python` build
  backend during the copier interactive prompt. The extension code
  goes alongside the Python source per the upstream's conventions.
- **Julia + C extension via `ccall`**: use `./bootstrap.sh julia`
  and add the C source under `deps/` per BestieTemplate.jl /
  Pkg.jl conventions.
- **Other combinations**: scaffold the primary-language layer first;
  add the secondary-language code per its standard conventions
  (e.g. `src/<library>/_native/` for a C extension; document the
  build process explicitly).

For mixed-language projects, the `notes/impl_<component>.md`
discipline is especially valuable for documenting which language
each component is in + why.

## What to record in per-project AGENTS.md

When using a non-Python language, your per-project `AGENTS.md`
"Project-specific overrides" section should record any deviation
from the Python defaults. Example for a Julia project:

```markdown
## Project-specific overrides

(Anything that differs from the universal conventions in
`~/.scicomp-research-skills/AGENTS.md` Section 6, OR from the
Python-centric defaults of `templates/software-skeleton/`.)

### Override: language is Julia, not Python (decided 2026-05-13)

**Template default**:
The `templates/software-skeleton/` README + PLAN + AGENTS show
Python conventions (pyproject.toml, src/<library_name>/, pytest,
SPEC 0 supported-versions).

**Project**:
This project is Julia 1.10+. Build / packaging via Project.toml
+ Pkg.jl (BestieTemplate.jl-generated). Test framework: Test.jl
+ TestItemRunner.jl + Aqua.jl. Source layout per Julia convention:
`src/LibraryName/` containing `LibraryName.jl` (the main module
file) plus submodules.

**Rationale**:
The library wraps an existing Julia ecosystem (DifferentialEquations.jl /
ApproxFun.jl / similar) and must be Julia-native; rewriting in
Python would lose the ecosystem benefit.

**Scope**: entire project.
```

This makes the deviation visible to a future agent reading the
project, prevents the agent from accidentally applying Python
conventions, and provides the rationale for future-you.

## When to file an upstream improvement

If you are using this template for a non-Python language and find
that:

- The Python-centricity is unclear or misleading;
- The `MULTI-LANGUAGE.md` placeholder-translation table is
  incomplete for your language;
- A pattern in your community's standard scaffolding is genuinely
  better than what the template assumes;

... then please **file feedback** via the upstream feedback channel
(see `~/.scicomp-research-skills/CONTRIBUTING.md`). We may add a
dedicated `templates/julia-software-skeleton/` /
`templates/cpp-software-skeleton/` / etc. once we have enough
real-project evidence to know what shape they should take. The
default position is **NOT** to ship per-language templates
speculatively.

## Cross-references

- `bootstrap.sh` -- the script this file documents.
- `AGENTS.md` (root) Section 6 "Universal conventions" -- the
  framework conventions that are language-agnostic.
- `~/.scicomp-research-skills/skills/project-onboarding/references/conflict-resolution.md`
  -- the per-project "Project-specific overrides" mechanism for
  recording deviations.
- `~/.scicomp-research-skills/skills/research-software-engineering/SKILL.md`
  -- the methodology skill; explicitly language-agnostic in its
  numerical-correctness, testing, API-design, and code-paper-
  coupling principles. Examples are Python-flavoured but the
  principles transfer.

---

*Created YYYY-MM-DD by <your name> from
[`scicomp-research-skills/templates/software-skeleton/MULTI-LANGUAGE.md`](https://github.com/a-attia/scicomp-research-skills/tree/main/templates/software-skeleton/MULTI-LANGUAGE.md).
Update this file's date-stamp on copy.*
