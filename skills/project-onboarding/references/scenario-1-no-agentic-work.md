# Scenario 1: existing project, no prior agentic work

Loaded on demand from the `project-onboarding` skill when the audit
(see `references/existing-project-audit.md`) has confirmed that the
existing project has no `AGENTS.md` / `CLAUDE.md` / `.cursorrules`
/ etc. at the repo root.

This is the more common (and easier) of the two scenarios. The sub-
cases differ in how much existing structure must be reconciled with
the framework's expected layout.

---

## Decision: which sub-case applies?

After the audit, classify based on Audit Step 2 (existing layout vs
framework's expected layout):

- **1.A: Empty-ish repo** -- few files; little existing layout. Almost
  identical to "new project". Use the from-scratch instructions in
  root `AGENTS.md` Section 11.
- **1.B: Mature repo with substantial existing structure** -- existing
  `src/`, `experiments/`, `figures/`, `notes/`, `references/` etc.
  Migration must reconcile.
- **1.C: Repo with non-standard layout** -- e.g. all source at repo
  root; or `code/` instead of `src/`; or domain-specific layouts
  (LaTeX-document-as-repo; data-and-notebooks-only).

---

## Sub-case 1.A: empty-ish repo

If the audit shows fewer than ~10 files, no significant directory
structure, and the work hasn't really started yet: **don't migrate;
bootstrap.** Use root `AGENTS.md` Section 11 (Section 11.A for
papers, Section 11.B for software).

Worked example -- starting state:

```text
my-paper/
├── README.md           (3 lines: "this is my paper")
├── notes.txt           (10 lines of scratch ideas)
└── refs.bib            (2 entries, unverified)
```

Migration plan:

1. Treat this as "Starting a new project" per root `AGENTS.md`
   Section 11.A.
2. `cp -R ~/.scicomp-research-skills/templates/paper-skeleton/. .`
3. Copier will not overwrite `README.md` -- the agent prompts the
   user: "the existing README is 3 lines; does it have content
   worth preserving?". If yes: merge the 3 lines into the template's
   README; if no: overwrite.
4. Move `notes.txt` -> `notes/_scratch.md` and add a TODO
   to triage its content into `notes/section_*.md` later.
5. Move `refs.bib` -> `references/bibliography.bib`; add an entry
   to `references/_collection_log.md` flagging "2 entries from
   pre-onboarding state, unverified; needs `literature-survey`
   skill pass".
6. Customise the four placeholder files (AGENTS.md / PLAN.md /
   README.md / notes/README.md) per the template's guidance.
7. First commit:
   ```bash
   git add .
   git commit -m "chore: bootstrap from scicomp-research-skills/templates/paper-skeleton (migrating sparse pre-existing files)"
   ```

Total time: ~15 minutes once the user has decided what to fill in
the placeholders.

---

## Sub-case 1.B: mature repo with substantial existing structure

The harder case. The user has been working on this for weeks or
months; significant content + structure exist.

### Worked example 1: paper repo with existing structure

Starting state (from real-world example):

```text
my-paper/
├── README.md                    (full paragraph; useful)
├── paper/
│   ├── main.tex
│   ├── refs.bib                 (40 entries, mostly verified)
│   ├── sections/
│   │   ├── 01-intro.tex
│   │   ├── 02-method.tex
│   │   └── ...
│   └── figures/
│       ├── fig01-pipeline.pdf
│       └── ...
├── code/
│   ├── run_experiment.py
│   ├── analyze_results.py
│   └── plot_figure.py
├── results/
│   └── 2026-04-15_run/         (date-named runs already exist)
│       ├── output.csv
│       └── log.txt
└── pdfs/                        (downloaded reference PDFs)
    └── *.pdf
```

Audit Step 2 reconciliation:

| Framework path                | Existing path        | Decision                                               |
|:------------------------------|:---------------------|:-------------------------------------------------------|
| `drafts/main.tex`             | `paper/main.tex`     | Move `paper/` -> `drafts/`; preserve subdirs as-is.    |
| `references/bibliography.bib` | `paper/refs.bib`     | Move + de-duplicate (the `paper/` -> `drafts/` move handles this) |
| `references/pdf/<key>.pdf`    | `pdfs/*.pdf`         | Rename + move to match citekey convention; flag any unrecognized PDFs for the user to label. |
| `figures/`                    | `paper/figures/`     | Move; reorganise per `figures/<paper-section>/` if many figures. |
| `experiments/<run-id>/`       | `results/<date>_*/`  | Already date-based; rename to match `<date>_<algo>_<variant>/` convention; add `metadata.json` schema where missing. |
| `code/`                       | `code/`              | Either move to `experiments/<run-id>/run.sh` if scripts are run-specific, or extract a real Python package under `src/` if the code is reusable. The user decides. |
| `notes/`                      | (does not exist)     | Create from template. |
| `AGENTS.md`                   | (does not exist)     | Create from template. |
| `PLAN.md`                     | (does not exist)     | Create from template; seed from existing README + paper outline. |

Migration plan (each numbered item is one commit):

1. **Add the agent-facing scaffolding.** Copy AGENTS.md + PLAN.md +
   notes/README.md + notes/agent_feedback.md +
   references/_collection_log.md + .gitignore from
   `templates/paper-skeleton/`. Do NOT yet move anything else.
   ```
   git add AGENTS.md PLAN.md notes/ references/_collection_log.md .gitignore
   git commit -m "chore: add scicomp-research-skills paper-skeleton scaffolding (no content moves yet)"
   ```

2. **Customise the placeholder content** in AGENTS.md + PLAN.md +
   notes/README.md, seeding from the existing README + paper
   outline + run history.
   ```
   git add AGENTS.md PLAN.md notes/README.md
   git commit -m "docs: fill in scicomp-research-skills placeholders from existing project state"
   ```

3. **Move the bibliography.** `git mv paper/refs.bib references/bibliography.bib`;
   add a `references/_collection_log.md` entry noting the migration +
   the pre-onboarding verification status of each entry (likely
   "verified by previous workflow but not via the literature-survey
   skill's discipline; needs a re-pass").
   ```
   git mv paper/refs.bib references/bibliography.bib
   git add references/_collection_log.md
   git commit -m "chore: migrate refs.bib to references/bibliography.bib + log pre-onboarding state"
   ```

4. **Move + organise PDFs.** `mkdir -p references/pdf/`;
   `git mv pdfs/*.pdf references/pdf/`. For each PDF, rename to
   `<citekey>.pdf` matching the bib entry; flag any PDFs that don't
   correspond to a bib entry for the user.
   ```
   git mv pdfs/* references/pdf/
   # rename script, then:
   rmdir pdfs
   git add references/pdf/ -A
   git commit -m "chore: migrate downloaded PDFs to references/pdf/<citekey>.pdf layout"
   ```

5. **Move the LaTeX draft.** `git mv paper drafts`.
   ```
   git mv paper drafts
   git commit -m "chore: rename paper/ -> drafts/ to match scicomp-research-skills layout"
   ```

6. **Move + reformat experiments.** For each `results/<date>_*/`:
   rename to `experiments/<date>_<algo>_<variant>/`; add a stub
   `metadata.json` per the framework's schema (fill in what's known,
   leave the rest as `null`); preserve outputs as-is.
   ```
   mkdir -p experiments
   git mv results/* experiments/
   rmdir results
   # add metadata.json for each run, run script, etc.
   git add experiments/
   git commit -m "chore: migrate results/ to experiments/<run-id>/ with metadata.json stubs"
   ```

7. **Decide what to do with `code/`.** Two paths:
   - **Run-specific scripts** -- move each script into the
     corresponding `experiments/<run-id>/run.py`. Easier.
   - **Reusable code** -- extract a real package under `src/<name>/`,
     update import paths in scripts. Harder; do as a separate
     commit (or as the start of a follow-up software-skeleton
     migration if the code deserves it).
   ```
   # path 1:
   for run in experiments/*/; do
     cp code/run_experiment.py "${run}/run.py"
   done
   git rm -r code
   git add experiments/
   git commit -m "chore: copy code/ scripts into per-run experiments/<run-id>/run.py"
   # path 2:
   # ... see software-skeleton bootstrap workflow ...
   ```

8. **Move + reorganise figures.** `git mv drafts/figures figures` and
   organise by paper section.
   ```
   git mv drafts/figures figures
   # reorganise by section if useful
   git commit -m "chore: hoist figures/ to repo root"
   ```

9. **Verify.** Run the framework's first-action protocol on the
   migrated project: read AGENTS.md, PLAN.md, notes/README.md,
   references/_collection_log.md; check no broken cross-references;
   no personal-path leaks.

10. **Document the migration** in `notes/agent_feedback.md`. Include:
    what worked smoothly (template files dropped in cleanly), what
    required workarounds (the unrecognised PDFs in step 4), what
    gaps in the framework the migration revealed (anything that
    should improve the skill or the template).

11. (Optional) Remove `notes/_migration_<date>.md` (the working plan
    file from the audit step) once the migration is committed and
    verified.

The whole process for a moderate-complexity paper repo: ~1-2 hours of
focused work. Each commit is small, reviewable, and revertable.

### Worked example 2: software repo with existing structure

Same shape as Worked example 1, but using the software-skeleton
template + the software-skeleton's bootstrap.sh delegation step.

Starting state:

```text
my-library/
├── setup.py                    (legacy; needs migration to pyproject)
├── my_library/
│   ├── __init__.py
│   ├── core.py
│   └── utils.py
├── tests/
│   └── test_core.py            (3 tests; minimal)
├── examples/
│   └── demo.ipynb
└── README.md                   (1 paragraph)
```

Reconciliation:

| Framework path        | Existing path     | Decision                                                     |
|:----------------------|:------------------|:-------------------------------------------------------------|
| `pyproject.toml`      | `setup.py`        | bootstrap.sh's chosen upstream template will create pyproject; the user migrates setup.py content into it manually after. |
| `src/<name>/`         | `<name>/`         | Move package into `src/` (the `src` layout is the modern default; bootstrap.sh's upstream template assumes it). |
| `tests/`              | `tests/`          | Match. Add `tests/{unit,integration,e2e}/` subdivision per `research-software-engineering/references/02-testing-for-numerical-code.md`. |
| `examples/`           | `examples/`       | Match. |
| `experiments/`        | (does not exist)  | Create from template. |
| `figures/`            | (does not exist)  | Create from template. |
| `notes/`              | (does not exist)  | Create from template. |
| `AGENTS.md`           | (does not exist)  | Create from template. |
| `PLAN.md`             | (does not exist)  | Create from template; seed from setup.py / README. |
| `CITATION.cff`        | (does not exist)  | Create from template; instructions in the file. |

Migration plan additionally has:

- A step running `bootstrap.sh cookie` (or `nlesc` / `uv-cu`) AFTER
  the paper-coupling files (AGENTS.md, PLAN.md, etc.) are added so
  copier doesn't propose to overwrite them.
- A step migrating `setup.py` -> `pyproject.toml` content
  (dependencies, version, name, description) into whatever
  pyproject the upstream template generated.
- A step adding the `tests/{unit,integration,e2e}/` subdivision +
  classifying the existing 3 tests into the right tier.
- A step adding the first MMS test if the library has a numerical
  method that lacks one (per
  `research-software-engineering/references/01-numerical-correctness.md`'s
  "no paper tests" rule).

Otherwise the structure of the plan is the same.

---

## Sub-case 1.C: repo with non-standard layout

When the existing layout doesn't fit the framework's expectations
cleanly:

### Common non-standard layouts + what to do

**Layout A: sources at repo root.** Common in older Python projects
or single-script utilities.

```text
my-library/
├── library_name.py           (the whole library; one file)
├── test_library_name.py
└── README.md
```

Decision: this is barely a library. Either:

- Keep it as a script (don't migrate; the framework is overkill).
- Convert to a package: create `src/<name>/__init__.py`; move
  content into modules; add `tests/`; THEN apply the software-
  skeleton migration.

**Layout B: `code/` instead of `src/`.** Many academic projects use
this convention.

```text
my-paper/
├── code/
│   └── ...
├── data/
└── paper/
```

Decision: `code/` is fine; the framework doesn't strictly require
`src/`. Document the convention in `AGENTS.md` "Project-specific
overrides" section: "We use `code/` instead of `src/`; the agent
should not reorganise this." Then migrate everything else as in
1.B.

**Layout C: LaTeX-document-as-repo.** The repo IS the paper draft;
no code, no experiments, no figures generation.

```text
my-paper/
├── main.tex
├── refs.bib
├── *.sty
├── figures/                  (committed PDFs only; no source)
└── README.md
```

Decision: paper-skeleton applies but several directories
(`experiments/`, `figures/<...>/`, `notes/impl_*.md`) won't have
content. Use the template anyway; document in PLAN.md that the
project doesn't include code or experiments; the empty directories
serve as future-proofing.

**Layout D: notebooks-and-data only.** Common in early-stage data-
analysis projects.

```text
my-analysis/
├── notebooks/
│   ├── 01-explore.ipynb
│   ├── 02-model.ipynb
│   └── 03-figures.ipynb
├── data/
│   ├── raw/
│   └── processed/
└── README.md
```

Decision: this is the realm of `cookiecutter-data-science` more than
`paper-skeleton` or `software-skeleton`. Recommend:

- If headed for a paper: paper-skeleton; treat each notebook as a
  candidate `experiments/<run-id>/analysis.ipynb`; extract reusable
  code into a small package under `src/<name>/` over time.
- If headed for a library: software-skeleton; same notebook handling.
- If staying as analysis-only: out of this framework's scope; the
  `human-facing-doc-authoring` skill still applies for README.md
  + PLAN.md, but the directory layout doesn't fit either template.
  Document the deliberate non-adoption in PLAN.md.

### General rule for non-standard layouts

When in doubt: **keep what works; document the deviation.** The
per-project AGENTS.md "Project-specific overrides" section is the
formal home for "we don't follow the framework's convention X
because <reason>". The agent should not silently restructure to
match the template.

---

## Anti-patterns to refuse

- **"Let me just `cp -R templates/<x>-skeleton/. .` and overwrite
  everything."** No. Use the audit-and-plan procedure.
- **"Existing `code/` is wrong; let me rename to `src/` automatically."**
  No. The user might have reasons; ask first.
- **"This README is short; let me replace with the template's."** No.
  Even a 3-line README has content the user wrote; preserve + merge.
- **"The existing notes are messy; let me consolidate."** No. The
  user may need them as-is for ongoing work; move + flag, don't
  consolidate without explicit approval.

## Cross-references

- `references/existing-project-audit.md` -- the inventory step that
  precedes anything in this file.
- `references/scenario-2-existing-agentic-files.md` -- the other
  scenario; use this if Audit Step 3 found existing AGENTS.md /
  CLAUDE.md / etc.
- `references/conflict-resolution.md` -- when the user's existing
  conventions disagree with framework conventions.
- `references/migration-prompts.md` -- ready-to-paste prompts the
  user can give the agent to start a Scenario 1 migration.
- Root `AGENTS.md` Section 11 -- the "Starting a new project"
  workflow that 1.A's migration delegates to.

---

*Created 2026-05-13 by A. Attia.*
