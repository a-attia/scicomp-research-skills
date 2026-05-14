# Plan-of-Record: <Library name>

**Library name**: `<name>`. **Scope**: <one paragraph stating what
this library makes possible that wasn't possible before>.
**Audience**: <who uses this -- other researchers writing scripts /
downstream library authors / paper-companion only>.
**Status**: <pre-alpha / alpha / beta / 1.x>.
**Repo**: <URL>.
**License**: <MIT / BSD-3 / Apache-2.0 / GPLv3 / ...>.

> **Doc status**: Living plan-of-record. Date-stamp every revision.
> Items marked `[VERIFY]` need user confirmation or independent
> lookup before use.

---

## Headline goal

**Claim.** <One paragraph: what does this library make possible that
wasn't possible before. Be specific about the audience + the
"before".>

**Positioning relative to alternatives.** <Two or three closest
alternatives with one-line summaries. What we add vs each. Why a new
library is justified rather than a contribution to one of them.>

**Why this should help.** <Mechanism of action: which user pain
this addresses, how the library's design choices follow from that
pain.>

**Demonstration.** <Describe the smallest convincing demonstration of
the headline goal -- usually a 10-20 line script that solves a
representative problem with the library and produces a recognisable
result.>

---

## 1. Scope and non-scope

### In scope

- <Bullet 1>: <one-line rationale>.
- <Bullet 2>: <one-line rationale>.

### Out of scope

- <Bullet 1>: <rationale -- "use library X for this", "deliberately
  defer", "not our problem to solve">.
- <Bullet 2>: <...>.

The boundary matters as much as the in-scope list. A library that
tries to do everything ends up doing nothing well.

---

## 2. Public API surface (target)

The functions / classes / CLI commands the library will expose at
1.0. Use a table when the surface has 5+ entries; use prose otherwise.

| Name              | Kind         | Signature (sketch)                                   | Status                |
|:------------------|:-------------|:-----------------------------------------------------|:----------------------|
| `solve_<problem>` | function     | `solve_<problem>(forcing, *, tol=1e-8, ...) -> ...`  | <ready / NEW / planned> |
| `<class-name>`    | class        | `<class-name>(mesh, *, params)`                      | <...>                 |
| `<cli-cmd>`       | CLI          | `<library-name> <cli-cmd> --input X --output Y`      | <...>                 |

Design principles in use (from
`research-software-engineering/SKILL.md` "Universal principles" +
`references/03-api-design-for-researchers.md`, planned):

- I/O separated from scientific logic.
- Duck typing where helpful; functions accept the broadest input
  types they can handle.
- Keyword-only optional arguments (use `*` separator).
- Two-layer "friendly + cranky" architecture if applicable.
- Static typing throughout.

---

## 3. Architecture

<High-level description of the components and how they interact.
Either prose with an annotated ASCII tree, or a markdown image of a
block diagram. Aim to fit on one screen.>

The tree below shows the **Python** layout (the template's documented
default). For Julia, C++, Rust, Fortran, etc., adapt to your
language's conventions; see
[`MULTI-LANGUAGE.md`](MULTI-LANGUAGE.md) for the per-language
layout reference.

```text
src/<library_name>/
├── __init__.py             public API exports
├── core/                   numerical methods
├── solvers/                linear / nonlinear / time-stepping solvers
├── io/                     I/O routines (separate from numerics)
└── _diagnostics.py         python -m <library_name>._diagnostics
                            (stdlib unittest; runs on installed package)
```

Each component's responsibility in 1-2 sentences:

- **`core/`** -- <responsibility>.
- **`solvers/`** -- <responsibility>.
- **`io/`** -- <responsibility>.
- **`_diagnostics.py`** -- self-test of the installed package; per
  `research-software-engineering/references/02-testing-for-numerical-code.md`
  "Diagnostic tests" pattern. (Equivalent in Julia: a `@testset
  "diagnostics"` block runnable on the installed package; in C++:
  a `ctest` target.)

---

## 4. Milestones

| Milestone | Status | Goal                                                                            |
|:----------|:-------|:--------------------------------------------------------------------------------|
| **M1**    | <done / in-progress / pending> | Bootstrap + CI: build manifest (pyproject.toml / Project.toml / Cargo.toml / CMakeLists.txt / ...), tests/ skeleton, GitHub Actions for unit tests, pre-commit / equivalent linters. |
| **M2**    | <...>  | Core numerical method: implementation + MMS test + convergence-rate test.       |
| **M3**    | <...>  | Public API: top-level functions stable; type hints complete; first user docs.   |
| **M4**    | <...>  | First downstream user: <internal collaborator OR paper experiment OR external library>. |
| **M5**    | <...>  | Paper handoff (if applicable): commit-pin in paper repo; tag `v0.x-paper-submission`; Zenodo DOI. |
| **M6**    | <...>  | Maintenance posture: who fixes what; what gets backported; abandonment criteria. |

Milestones are **shippable**, not commit-sized. Each milestone should
correspond to a tag or a release.

---

## 5. Numerical correctness plan

Per `research-software-engineering/references/01-numerical-correctness.md`,
this section names the verification strategy for the library's core
numerical claims. Update as the library matures.

| Claim                                                | Verification                                                                                | Status |
|:-----------------------------------------------------|:--------------------------------------------------------------------------------------------|:-------|
| <e.g. "second-order convergence in L2 for linear FE"> | MMS test in `tests/integration/test_<...>_mms.py` + convergence-rate test in `tests/integration/test_<...>_rate.py` | <pending / passing> |
| <conservation invariant claim>                       | Property-based test in `tests/integration/test_<...>_invariant.py`                          | <...>  |
| <symmetry / equivariance claim>                      | Test in `tests/unit/test_<...>_symmetry.py`                                                 | <...>  |

Every claim in this table must be testable + tested before the
corresponding milestone is marked done.

**No "paper tests"**: every assertion of numerical equality MUST cite
the source of the expected value (analytical / MMS / reference impl /
benchmark / invariant / asymptotic). See the rule in
`research-software-engineering/references/01-numerical-correctness.md`
"The defence".

---

## 6. Reproducibility infrastructure

| Asset                              | Status / Location                                                |
|:-----------------------------------|:-----------------------------------------------------------------|
| **Lockfile**                       | <`uv.lock` / `pixi.lock` / `conda-lock.yml`; pinned to commit X> |
| **Container image**                | <if used; Dockerfile location; pin policy>                       |
| **CITATION.cff**                   | repo root; populated at M3                                       |
| **Zenodo integration**             | <enabled YYYY-MM-DD; concept DOI: <doi>>                         |
| **Per-experiment metadata schema** | `experiments/<run-id>/metadata.json` (see `experiments/README.md`) |
| **Test fixtures**                  | `tests/fixtures/` (small reproducible inputs)                    |
| **Golden outputs**                 | `tests/fixtures/golden_*.npy` (regenerate via `tests/regenerate_goldens.sh`) |

Per the `research-software-engineering` skill: use the lightest tool
that does the job. A small library usually needs only Git + Zenodo +
`experiments/<run-id>/` + a lockfile. Don't add DVC / wandb / mlflow
unless the project actually needs them.

---

## 7. Design decisions log

Significant architectural / design decisions, append-only. Each entry
gets a number + date + status.

### D-001 -- <one-line title> (YYYY-MM-DD)

**Status**: accepted / superseded by D-NNN.

**Context.** <What problem prompted this decision. 2-3 sentences.>

**Decision.** <What we chose. Be specific.>

**Alternatives considered.** <Numbered list: alternative + why
rejected.>

**Consequences.** <What this commits us to. What it makes harder.
What it makes easier.>

### D-002 -- ... (YYYY-MM-DD)

...

(See
`~/.scicomp-research-skills/skills/human-facing-doc-authoring/references/audit-log-structures.md`
section B for the full decision-log convention. Append-only: never
delete D-NNN; if reversed, add D-MMM marked "supersedes D-NNN" and
edit D-NNN's status to "superseded by D-MMM".)

---

## 8. Code-paper coupling (if applicable)

If this library exists to support a paper, fill in:

- **Paper repository**: <URL of sibling paper repo, OR "internal,
  not yet a sibling repo">.
- **Paper plan-of-record**: <link to paper's `PLAN.md`>.
- **Sections of the paper this code supports**:
  - Paper Section 4 (Method) -- via the `<module>` API.
  - Paper Section 5 (Test case) -- via `experiments/<run-id>/`.
  - Paper Section 6 (Experiments) -- via `experiments/<run-id>/`.
- **Submission-tag policy**: tag `v0.x-paper-submission` at submission;
  Zenodo auto-archives; cite the DOI in the paper.
- **Reviewer-response policy**: any code change triggered by reviewer
  comments goes in a clearly-named branch (`rebuttal-r1-rN`) and is
  tagged separately (`v0.x-paper-rebuttal-r1`).

If this library is standalone (no paper coupling), write "None" for
this section.

---

## 9. Lifecycle stage

What's the current and expected lifecycle stage (per
`research-software-engineering/references/07-project-lifecycle.md`,
planned)?

- **Now**: <experiment script / extracted library / pre-release / 1.x
  released / maintenance / abandoning>.
- **Next 6 months**: <expected target stage>.
- **Long term**: <maintenance posture; who fixes what; release cadence;
  abandonment criteria>.

The lifecycle stage decides how much investment is justified in
each subsequent change. A pre-release library should not invest
heavily in backwards-compatibility tests; a 1.x library MUST.

---

## 10. Tracking and cadence

- **This doc** (`PLAN.md`) is the contract; revise via PR-style edits
  and date-stamp changes.
- **Per-component design notes**: `notes/impl_<component>.md` for each
  significant new component (created BEFORE any code lands).
- **Per-experiment notes**: `experiments/<run-id>/` with metadata +
  results (see `experiments/README.md`).
- **Algorithmic-source citations**: `references/_collection_log.md`
  for papers cited in code comments (algorithm sources).
- **Agent-feedback journal**: `notes/agent_feedback.md` -- per-project
  feedback channel into the upstream
  [`scicomp-research-skills`](https://github.com/a-attia/scicomp-research-skills).

---

## 11. Open questions

(Things deferred for later resolution; tracked here so they don't
get lost.)

1. <Question 1 -- depends on <X>>.
2. <Question 2>.

---

*Created YYYY-MM-DD. Maintained by <name>.*
