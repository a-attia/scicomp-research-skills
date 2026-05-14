# <library-name>

<One-sentence "what does this library do". Then 2-3 sentences of
positioning -- what's the headline contribution, who is it for,
status.>

> Built for <use case>. If you need <related but different use case>,
> see <other library>.

> **For AI agents**: read [`AGENTS.md`](AGENTS.md) first, then
> [`PLAN.md`](PLAN.md). This README is for human collaborators.

---

## Contents

- [Status](#status)
- [Install](#install)
- [Quick example](#quick-example)
- [How this repo is organised](#how-this-repo-is-organised)
- [Numerical correctness + testing](#numerical-correctness--testing)
- [How experiments are organised](#how-experiments-are-organised)
- [Coupled paper](#coupled-paper)
- [Pinned dependencies](#pinned-dependencies)
- [Development](#development)
- [Citation](#citation)
- [Authors and acknowledgements](#authors-and-acknowledgements)
- [Licence](#licence)

---

## Status

<One paragraph: current development stage (pre-alpha / alpha / beta /
1.x), latest released version + Zenodo DOI if applicable, current
milestone target (M1 / M2 / ... per `PLAN.md`), blockers if any.
Update on every `PLAN.md` revision.>

## Install

<One code block. The bare minimum (e.g. `pip install <library-name>`,
`uv add <library-name>`, or `pip install git+<URL>` for pre-release).
Defer per-platform notes and CUDA/MPI variants to `docs/install.md`.>

```bash
pip install <library-name>
```

## Quick example

<10-20 line code snippet that produces a recognisable result. Should
be runnable verbatim. Output shown as a comment or follow-on code
block.>

```python
import <library_name> as <ln>

# Smallest convincing demonstration.
result = <ln>.solve_<problem>(...)
print(result)  # expected: <recognisable output>
```

## How this repo is organised

```text
<library-name>/
├── AGENTS.md             entry point for AI agents
├── PLAN.md               plan-of-record (the contract)
├── README.md             you are here
├── CITATION.cff          how to cite this library
├── LICENSE
│
├── src/<library_name>/   the library source
│   ├── core/             numerical methods
│   ├── solvers/          linear / nonlinear / time-stepping solvers
│   ├── io/               I/O routines (separate from numerics)
│   └── _diagnostics.py   python -m <library_name>._diagnostics
│
├── tests/
│   ├── unit/             fast, isolated tests
│   ├── integration/      MMS / convergence-rate / invariant tests
│   ├── e2e/              end-to-end pipeline tests
│   └── fixtures/         small reproducible inputs + golden outputs
│
├── docs/                 user-facing documentation source
├── examples/             runnable example scripts
│
├── experiments/          per-experiment workspaces; gitignored except
│                         for metadata + scripts (see experiments/README.md)
├── figures/              final figures + generation scripts (see figures/README.md)
├── notes/                impl notes / section notes / agent feedback (see notes/README.md)
├── references/           algorithmic-source citations + survey notes
│
└── .github/
    ├── workflows/        CI: tests, docs, release-on-tag
    └── ISSUE_TEMPLATE/   numerical / API / performance regression templates
```

The package layout itself (the `src/<library_name>/`, `tests/`,
`docs/` parts, plus `pyproject.toml` / `pre-commit` config / GitHub
Actions) was scaffolded by an upstream community template; see
[Development](#development).

## Numerical correctness + testing

This library follows the
[`research-software-engineering`](https://github.com/a-attia/scicomp-research-skills/blob/main/skills/research-software-engineering/SKILL.md)
methodology. The non-negotiable rules:

- **Every test asserting numerical equality cites the source of the
  expected value** (analytical / MMS / reference impl / published
  benchmark / conservation invariant / asymptotic relation). No
  "paper tests" -- a test with a hand-picked expected value and no
  citation is considered broken.
- **Method of manufactured solutions (MMS)** + **convergence-rate
  tests** are the primary verification tool for any discretisation
  routine. Located under `tests/integration/`.
- **Conservation-invariant tests** for any quantity that is
  mathematically conserved (mass / energy / momentum / total
  probability).
- **Random seeds are deterministic by default** in tests; runs that
  use randomness record their seed in
  `experiments/<run-id>/metadata.json`.

Run the full test suite:

```bash
pytest                              # unit + integration (fast)
pytest -m e2e                       # add end-to-end (slower)
pytest -m "slow or gpu or mpi"      # opt-in to slow / specialised tests
python -m <library_name>._diagnostics  # verify the installed package
```

## How experiments are organised

Each experiment lives in `experiments/<run-id>/` where `<run-id>` is
the convention `<date>_<algo>_<variant>` (e.g.
`20260513_finite-element_linear-quad`). Each run-dir contains:

- `metadata.json` -- code commit hash, environment lockfile hash,
  RNG seed, hardware, wall-clock, peak memory, lockfile DOI if
  applicable.
- `params.yaml` -- the parameters used.
- `run.sh` (or `run.py`) -- the script that produces the run.
- `output/` -- numerical outputs (gitignored if large; tracked if
  small + diff-able).
- `analysis/` -- post-hoc analysis scripts + figures.

See [`experiments/README.md`](experiments/README.md) for the full
discipline.

## Coupled paper

<If this library supports a paper, fill in:>

This library supports the paper **<Paper title>** (sibling repo
[`<paper-short-name>`](<URL>); paper `PLAN.md`: <link>).

- The paper's Section 4 (Method) corresponds to <module>.
- The paper's Section 5 (Test case) corresponds to
  `experiments/<run-id-or-pattern>`.
- The paper's Section 6 (Experiments) corresponds to
  `experiments/<run-id-pattern>`.
- The submission-tagged version is `v<X>.<Y>-paper-submission` (Zenodo
  DOI: <DOI>).

<If this library is standalone, replace this section with a single
sentence: "This library is standalone; not currently coupled to a
specific paper.">

## Pinned dependencies

For reproducibility, this library pins direct + transitive
dependencies. The lockfile is at <`uv.lock` / `pixi.lock` /
`conda-lock.yml`>.

Key direct dependencies + version policy:

- **<dep 1>**: <version constraint> (<rationale, e.g. "API change in
  X.Y.0">).
- **<dep 2>**: <version constraint>.
- **Python versions supported**: <e.g. "3.11, 3.12, 3.13" per SPEC 0>.

Update the lockfile via:

```bash
<uv lock --upgrade>      # or pixi update / conda-lock --update / ...
```

## Development

This library was bootstrapped via
[`scicomp-research-skills/templates/software-skeleton/`](https://github.com/a-attia/scicomp-research-skills/tree/main/templates/software-skeleton),
which delegates the package scaffolding (pyproject, pre-commit, ruff,
GitHub Actions matrix) to an upstream community template. The
recommended upstream is
[`scientific-python/cookie`](https://github.com/scientific-python/cookie)
(BSD-3-Clause); alternative upstreams supported by `bootstrap.sh` are
[`NLeSC/python-template`](https://github.com/NLeSC/python-template)
(Apache-2.0; FAIR-software-aware) and
[`CU-DBMI/template-uv-python-research-software`](https://github.com/CU-DBMI/template-uv-python-research-software)
(BSD-3-Clause; uv-first).

To set up a development environment:

```bash
git clone <URL>
cd <library-name>
<uv sync --all-extras --dev>     # OR: pip install -e ".[dev]"
pre-commit install
pytest
```

To verify the repo against the
[Scientific Python repo-review](https://learn.scientific-python.org/development/guides/repo-review/)
checks (codes `PY*` / `PP*` / `GH*` / `MY*` / `RF*`):

```bash
uvx sp-repo-review[cli] .
```

For the full development workflow + contribution guide, see
<`docs/development.md` / `CONTRIBUTING.md`>.

## Citation

If you use this library in academic work, please cite via the
[`CITATION.cff`](CITATION.cff) (GitHub provides a "Cite this
repository" button; software citation tools resolve `.cff` files
automatically). The Zenodo DOI for the latest released version is
<DOI>; the concept-DOI (latest version of any release) is <DOI>.

BibTeX entry (auto-generated from CITATION.cff):

```bibtex
@software{<author>_<year>_<library>,
  author       = {<author list>},
  title        = {<library-name>},
  year         = {<year>},
  publisher    = {Zenodo},
  doi          = {<DOI>},
  url          = {<repo URL>}
}
```

## Authors and acknowledgements

<Authors with affiliations.>

<Funding acknowledgements.>

<People who provided code / data / discussions but are not co-authors.>

## Licence

<One sentence + link to LICENSE.>

This project is licensed under the <licence>; see [`LICENSE`](LICENSE)
for the full text.
