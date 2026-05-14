---
name: research-software-engineering
description: Use this skill whenever the work involves writing, extending, refactoring, testing, packaging, releasing, or auditing scientific-computing software -- numerical methods, PDE solvers, inverse problems, optimisation, optimal experimental design, uncertainty quantification, scientific machine learning, or any code that produces numbers (not user-facing apps). Make sure to load this whenever a session will touch a Python / Julia / C++ scientific-computing codebase, EVEN IF THE USER DOES NOT MENTION IT explicitly. The skill codifies eleven disciplines as a methodology for AI-assisted scientific software development -- numerical correctness (MMS / convergence-rate tests / conservation invariants / "paper tests" guard), testing strategies for numerical code, API design for researchers (NumPy / JAX / scikit-learn / dolfinx / petsc4py idioms), performance and scaling, reproducibility infrastructure (lockfiles / containers / Zenodo handshake), CI/CD for research code, project lifecycle (script -> library -> publication -> maintenance), code-paper coupling (commit-pinning / submission tags / SWHID), launch and debug protocols adapted from fcakyon/phd-skills, and the Bridgeford et al. 2025 ten rules for AI-assisted coding in science. Borrows from and cites: Scientific Python Development Guide (BSD-3) + sp-repo-review, pyOpenSci package guide, Wilson et al. 2017 "Good Enough Practices for Scientific Computing", JOSS review criteria (with 2025 AI-disclosure requirement), BSSw.io HPC guidance, The Turing Way Research Compendia chapter, and Bridgeford et al. 2025 (CC-BY 4.0). Companion skill to `literature-survey` (papers cited as algorithm sources) and `research-paper-writing` (when the code supports a paper).
license: MIT
metadata:
  audience: scientific-computing software authors and contributors
  domain: scientific-computing-software
  origin: A. Attia (added 2026-05-13; informed by a prior-art audit covering ~30 sources across agent-skills, project templates, and best-practice guides)
---

# Research Software Engineering

## How this skill is organised (progressive disclosure)

This skill follows the **three-level progressive disclosure** pattern
also used by `agent-resource-discipline` and codified by Anthropic's
`skill-creator`:

- **Level 1 (always in context once loaded)**: this `SKILL.md`,
  ~200 lines. Contains the universal principles + a workflow table
  showing which reference to load for which task.
- **Level 2 (loaded on demand by name)**: the `references/*.md`
  files -- one per discipline. Loaded only when a session actually
  exercises that discipline.
- **Level 3 (planned future work)**: numerical-correctness
  enforcement hooks (golden-output-diff guard, lockfile-drift guard,
  experiment-id guard, commit-pin guard) -- specification deferred,
  same rationale as `agent-resource-discipline`'s planned hooks.

Always load this SKILL.md when the trigger fires. Load specific
references only when the current sub-task requires them.

## When to load this skill

Load this skill at the start of any session that will involve any of:

- writing or extending a scientific-computing library or research code
  (numerical methods, PDE solvers, inverse problems, OED, UQ,
  scientific ML);
- adding tests to numerical code;
- packaging / releasing research code (pyproject.toml,
  GitHub Actions, Zenodo);
- preparing code for a paper submission (commit-pinning, archiving);
- auditing existing scientific software for correctness, reproducibility,
  or maintainability concerns;
- API design decisions for a Pythonic / JAX / dolfinx / petsc4py
  scientific library;
- performance tuning, GPU offload, MPI parallelisation;
- extracting a reusable library out of experiment scripts.

If the session is a paper-writing session that does NOT touch code,
load `research-paper-writing` instead. If the session is mixed (paper +
code), load both.

## Core principle: numerical correctness is not optional

A scientific-computing program that returns a plausible-looking wrong
number is much worse than one that crashes. The agent MUST treat
numerical correctness as the highest-priority concern, ahead of
performance, ahead of API ergonomics, ahead of style. Specifically:

1. **Every numerical claim made by the code must be backed by a test**
   that compares to a known-correct value (analytical, manufactured,
   or independently-verified) -- not to a dummy expected value, not
   to "whatever the code currently produces".
2. **Tests that compare to "expected" values must cite the source of
   the expected value** -- in a comment immediately above the
   assertion, naming the analytical solution / MMS construction /
   reference paper / golden-output run that justifies it. This is
   the explicit guard against the "paper tests" anti-pattern
   (Bridgeford et al. 2025 R6).
3. **Convergence-rate tests** are the single most powerful tool for
   catching numerical bugs in discretisation code -- they fail when
   the order of accuracy is wrong, even if the absolute error is
   "small enough to look right". See `references/02-testing-for-numerical-code.md`.
4. **Random seeds must be deterministic** across runs by default.
   If a test depends on randomness, the seed must be fixed; if a
   research result depends on randomness, the seed must be recorded
   in `experiments/<run-id>/metadata.json`.

This principle is non-negotiable. If style / performance / API
elegance ever conflicts with it, correctness wins.

## Universal principles (apply unconditionally)

Beyond the correctness imperative, these universal principles fire
for every action the agent takes in a scientific-computing codebase.
Restated from the Scientific Python Development Guide
(`https://learn.scientific-python.org/development/principles/design/`,
BSD-3) with sci-computing-specific framing:

1. **Keep I/O separate.** I/O functions only do I/O and return
   standard types (NumPy arrays, dataclasses); the scientific logic
   operates on those standard types and never touches files / sockets /
   GUIs directly.
2. **Duck typing where helpful.** Avoid `isinstance` checks; functions
   should accept the broadest input types they can handle.
3. **Consider: can this just be a function?** Cite Perlis: "It is
   better to have 100 functions operate on one data structure than
   10 functions on 10 data structures." Most scientific code is
   functions over arrays; resist the urge to wrap everything in
   classes.
4. **Avoid changing state.** Replace mutable workflow classes with
   multiple immutable classes (or pure functions chained explicitly)
   representing each step.
5. **Static typing makes code more readable.** Add type hints by
   default; they document intent at zero runtime cost.
6. **Keyword-only optional arguments.** Use the `*` separator in
   function signatures to force long-tail options to be named at
   call sites; this prevents positional-argument bugs when defaults
   change.
7. **Two-layer "friendly + cranky" architecture.** Library code
   raises errors unless it knows how the user wants to handle them;
   a thin convenience layer above can be more permissive. Don't mix
   the two.
8. **Write useful error messages.** A scientific error message
   should name the offending value, the constraint it violated, and
   the function it occurred in -- not just "ValueError".

## Universal AI-assisted-coding rules (Bridgeford et al. 2025)

The Bridgeford et al. 2025 paper "Ten Simple Rules for AI-Assisted
Coding in Science" (arXiv 2510.22254, CC-BY 4.0, companion Jupyter
Book at `https://poldracklab.org/10sr_ai_assisted_coding`) is the
peer-reviewed reference for the AI-assisted era specifically targeting
scientists. The full rules are in
`references/11-ai-assisted-coding-rules.md`; the four rules that
apply unconditionally are:

- **R6 (paper tests warning)**: AI may insert fabricated input values
  or dummy functions that appear to meet acceptance criteria but do
  not reflect true functionality. Any test asserting numerical
  equality must cite the source of the expected value.
- **R8 (commit before major changes; revert beats debug-in-polluted-context)**:
  always commit working code before agentic changes; if an attempt
  goes off the rails, `git reset --hard` is cheaper than trying to
  steer a confused context back to correctness.
- **R9 ("AI wrote it" is never an accountability defence)**: the
  human is responsible for every line that ships. Be sceptical of
  the AI's claims of success; verify behaviourally, not by inspection.
- **R10 (refine incrementally with focused objectives)**: never
  ask AI to "improve my codebase". Ask for one specific change with
  one acceptance criterion.

## Workflow table: phase x concern x reference

When the session enters a specific phase or addresses a specific
concern, load the matching reference. Do NOT load all references at
once.

| Phase / concern                            | Reference to load                                     |
|:-------------------------------------------|:------------------------------------------------------|
| Numerical correctness, MMS, convergence    | `references/01-numerical-correctness.md`              |
| Test design for numerical code             | `references/02-testing-for-numerical-code.md`         |
| API design / refactoring decisions         | `references/03-api-design-for-researchers.md` (PR2)   |
| Performance / GPU / MPI                    | `references/04-performance-and-scaling.md` (PR4)      |
| Lockfiles / Zenodo / FAIR / CITATION.cff   | `references/05-reproducibility-infrastructure.md` (PR2) |
| pyproject / pre-commit / nox / actions     | `references/06-ci-cd-for-research-code.md` (PR4)      |
| Lifecycle / extraction / abandonment       | `references/07-project-lifecycle.md` (PR4)            |
| Code-paper coupling / submission tags      | `references/08-code-paper-coupling.md` (PR2)          |
| Launching a long numerical run             | `references/09-launch-checklist-numerical.md` (PR4)   |
| Debugging numerical failures               | `references/10-debug-protocol-numerical.md` (PR4)     |
| Working with AI on scientific code         | `references/11-ai-assisted-coding-rules.md`           |

(Items marked PR2 / PR4 are planned in subsequent shipments; the four
unmarked references are in this skill's first cut.)

## Workflow rules

The full discipline lives in the references; the cross-cutting rules
applied across all references are:

1. **Correctness before style.** Numerical correctness wins when in
   conflict with anything else.
2. **Tests cite their expected-value source.** Always.
3. **Commit before agentic changes.** Bridgeford R8.
4. **Lightest tool that does the job.** A small PDE-paper repo
   usually needs only Git + Zenodo + `experiments/<run-id>/` + a
   lockfile. Don't oversell DVC / wandb / mlflow until the project
   actually needs them.
5. **Defer to upstream templates.** For package scaffolding, use
   `scientific-python/cookie` (or `NLeSC/python-template`,
   `CU-DBMI/template-uv-python-research-software`). Don't reinvent
   pyproject.toml + pre-commit + GitHub Actions configs we'd just
   have to maintain forever.
6. **Audit-trail for every numerical decision.** Choices made during
   library extraction (which tolerance, which solver, which
   stopping criterion) get a one-line note in
   `notes/impl_<component>.md` with the source of the choice (paper
   citation, prior implementation, empirical sweep).
7. **Long open-development history.** Avoid the JOSS desk-rejection
   anti-pattern of "all commits in the last two weeks before
   submission". Open the repo from project start; commit early and
   often; aim for 6+ months of public history before any planned
   release.

## Adjacent skills (compose freely)

This skill composes with:

- `agent-resource-discipline` -- always load when the session is
  heavy (PDF / multi-file / web fetch / cross-session). Software
  sessions almost always qualify.
- `human-facing-doc-authoring` -- load when authoring or revising
  the project's `README.md`, `PLAN.md`, `notes/impl_*.md`, or any
  human-facing doc.
- `literature-survey` -- load when papers cited as algorithm
  sources need bib + survey-note workflow (the `_collection_log.md`
  pattern transfers cleanly to "papers we cited in code comments").
- `research-paper-writing` -- load when the code supports a paper
  and the paper draft is also being touched.

The four skills are designed to compose; loading 2-3 simultaneously
is normal for software sessions.

## Adjacent prior art + lineage

Detailed prior-art lineage lives at the bottom of
`references/11-ai-assisted-coding-rules.md`. The shortest summary:
the audit that informed this skill found a clear gap (no agent-skill
exists for sci-computing software methodology) but a rich corpus of
human-facing best-practice guides and project templates to cite +
borrow from. Templates: `scientific-python/cookie` (BSD-3) +
`NLeSC/python-template` (Apache-2.0) +
`CU-DBMI/template-uv-python-research-software` (BSD-3). Best-practice
corpus: Scientific Python Development Guide (BSD-3) + sp-repo-review,
pyOpenSci package guide, Wilson et al. 2017 (CC-BY), JOSS review
criteria, BSSw.io, The Turing Way (CC-BY 4.0 + MIT), Bridgeford et al.
2025 (CC-BY 4.0). Closest neighbour skills (different scope):
`fcakyon/phd-skills` (MIT, ML-flavored) and
`K-Dense-AI/scientific-agent-skills` (MIT, per-package wrappers).

## Output contract

When the user invokes this skill, the agent should:

1. Confirm the phase / concern (so it knows which references to load).
2. Load only the references matching the phase (per the workflow
   table above).
3. Apply the universal principles + the AI-assisted-coding rules
   throughout.
4. For any numerical assertion produced by the agent, ensure the
   "tests cite their expected-value source" rule is followed.
5. Surface contradictions explicitly (per `agent-resource-discipline`'s
   surfacing rule); never silently fix.
6. Append an entry to `notes/agent_feedback.md` if any of the
   trigger conditions in
   `agent-resource-discipline/references/persistent-memory.md` fired
   during the session.

---

*Created 2026-05-13 by A. Attia. Informed by a prior-art audit
covering ~30 sources across agent-skills (`anthropics/skills`,
`fcakyon/phd-skills`, `K-Dense-AI/scientific-agent-skills`,
`addyosmani/agent-skills`, `47Wu/cc_skills`,
`sscivier/prompt-protocols`), project templates
(`scientific-python/cookie`, `NLeSC/python-template`,
`UCL-ARC/python-tooling`, `CU-DBMI/template-uv-python-research-software`,
`pyOpenSci/python-package-guide`, cookiecutter-data-science),
best-practice corpora (Scientific Python Development Guide,
Wilson et al. 2014/2017, Bridgeford et al. 2025, JOSS review criteria,
The Turing Way, BSSw.io), and reproducibility tooling (DVC,
mlflow / wandb, Snakemake / Nextflow, Zenodo, Software Heritage,
JuliaBesties/BestieTemplate.jl). The audit identified a clear gap:
no agent-skill targeted scientific-computing software methodology;
this skill is the first cut at filling that gap. Currently ships
`SKILL.md` + four references; remaining seven references and a
companion `templates/software-skeleton/` are planned in subsequent
shipments per the audit's PR1-PR4 sequencing.*
