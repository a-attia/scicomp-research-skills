# <Library short name> / AGENTS.md

This project loads shared workflow conventions from the
[scicomp-research-skills](https://github.com/a-attia/scicomp-research-skills)
repository. Before doing anything else, the consuming agent should:

1. Verify `~/.scicomp-research-skills/AGENTS.md` exists and is no more
   than 30 days stale (per its modification time). If stale, print a
   reminder suggesting `~/.scicomp-research-skills/bin/refresh.sh` and
   proceed anyway.
2. Read `~/.scicomp-research-skills/AGENTS.md`.
3. Read any skill files referenced below from
   `~/.scicomp-research-skills/skills/<name>/SKILL.md`.
4. Then read the rest of THIS file.

## Skills to load for this project

Load on demand, not all at once:

- `~/.scicomp-research-skills/skills/research-software-engineering/SKILL.md`
  -- the primary skill for this project. Methodology for AI-assisted
  scientific-computing software development: numerical correctness
  (MMS / convergence-rate tests / "paper tests" guard), testing
  strategies for numerical code, API design for researchers,
  reproducibility infrastructure, code-paper coupling, plus the
  Bridgeford et al. 2025 ten rules condensed agent-actionably.
- `~/.scicomp-research-skills/skills/agent-resource-discipline/SKILL.md`
  -- always load for any non-trivial software session. Token / quota /
  context-window discipline; first-action / last-action protocols that
  give the agent persistent memory across sessions via the project's
  indices (`PLAN.md` status, `notes/README.md`).
- `~/.scicomp-research-skills/skills/human-facing-doc-authoring/SKILL.md`
  -- load whenever authoring or substantially revising any human-facing
  project doc (`README.md`, `PLAN.md`, `notes/impl_*.md`,
  `notes/section_*.md`, `notes/agent_feedback.md`,
  `experiments/<run-id>/README.md`, `figures/<topic>/README.md`,
  `references/_collection_log.md`). The
  `references/plan-structures.md` reference file inside that skill has
  a section B specifically for research-software PLAN.md.
- `~/.scicomp-research-skills/skills/literature-survey/SKILL.md`
  -- load when adding a new algorithmic reference cited in code (e.g.
  "this implements Algorithm 3.1 from Smith et al. 2023"). The bib +
  PDF + survey-note workflow is the same as for paper projects; the
  collection log lives at `references/_collection_log.md`.
- `~/.scicomp-research-skills/skills/research-paper-writing/SKILL.md`
  -- load only when this project's code is supporting a paper draft
  AND the draft is also being touched in this session.

The four skills `research-software-engineering` +
`agent-resource-discipline` + `human-facing-doc-authoring` +
`literature-survey` are designed to compose freely; loading 2-3
simultaneously is normal for software sessions.

---

## Project facts

- **Name**: <full library name>
- **Nature**: research-software library (or research-software code).
- **Status**: <e.g. M1 -- bootstrap + CI; M3 -- core API stable; M5 -- paper handoff>
- **Plan-of-record**: PLAN.md (read this after AGENTS.md)
- **Public API surface**: <one-line summary of the top-level exports>
- **Primary downstream consumers**: <names of other projects that depend on this; or "internal only" / "this paper only">
- **Current release**: <git tag / pip version / "pre-release">
- **Code dependencies**: <upstream libraries this code depends on, with pin policy>
- **Paper coupling**: <"none -- standalone library" OR "supports paper <citekey> at sibling repo `<paper-short-name>`">

## Project-specific overrides

(Anything that differs from the universal conventions in
`~/.scicomp-research-skills/AGENTS.md` Section 6. If nothing differs,
write "None".)

## Project-specific facts the agent should not have to derive

(One-off facts: language + framework choices, mathematical conventions
in use, key collaborators, specific external dependencies that need
care, current development phase, known gotchas. The agent benefits
from knowing these without reading PLAN.md cover-to-cover.)

- **Language**: <Python 3.11+ / Julia 1.10+ / C++17 / mixed>
- **Build backend**: <hatchling / setuptools / scikit-build-core / poetry / uv-managed>
- **Environment manager**: <uv / pixi / conda / pip-tools>
- **Test framework**: <pytest / unittest / pytest+hypothesis>
- **Mathematical conventions**: <e.g. row-major arrays, 0-based indexing,
  positive-definite-A sign convention for the discrete Laplacian, SI units
  throughout, ...>
- **Key collaborators**: <names + roles>
- **Specific external dependencies**: <e.g. dolfinx >= 0.8 (pinned because
  of API change); PETSc-Python with complex-scalar build only; CUDA 12.x>
- **Current phase**: <e.g. M2 -- core API stable but no users yet>
- **Known gotchas**: <e.g. "MPI tests fail on macOS due to Open MPI bug
  X; use Linux for full test suite">
- **Hardware assumptions**: <e.g. CPU-only; CPU + single GPU; multi-node
  MPI required for full-scale runs>

## Citation + archival policy

- **CITATION.cff**: at repo root; populated by template at first
  release.
- **Zenodo handshake**: <enabled YYYY-MM-DD via Zenodo settings -> GitHub;
  every tagged release auto-archives>.
- **DOI**: <Zenodo concept DOI for the project>; per-version DOIs are
  recorded in `experiments/<run-id>/metadata.json` for any run that
  produces a published result.
- **Software Heritage SWHID**: <if used; for citing specific code
  blocks in paper text>.

---

*Created YYYY-MM-DD by <your name>. Bootstrapped from
[`scicomp-research-skills/templates/software-skeleton/`](https://github.com/a-attia/scicomp-research-skills/tree/main/templates/software-skeleton).*
