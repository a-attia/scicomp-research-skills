# experiments/

This directory holds **per-experiment workspaces** that produce results
cited by the paper -- one subdirectory per logically distinct
experimental run. The discipline here is the single most important
investment in reproducibility for the paper: a future-you (or a
reviewer, or a downstream researcher) needs to be able to take any
number printed in the paper and walk straight back to the code,
parameters, environment, and seed that produced it.

This directory is a paper-side mirror of the discipline applied to
research-software repositories (see
`~/.scicomp-research-skills/templates/software-skeleton/experiments/README.md`
for the canonical version + full schema). The conventions are
identical; the audience is the paper's reviewers + readers + future
authors of follow-up papers.

## Naming convention

```text
experiments/<date>_<algo>_<variant>/
```

- `<date>` -- `YYYYMMDD` of when the run was kicked off.
- `<algo>` -- the algorithm or method used (short identifier matching
  the paper's nomenclature).
- `<variant>` -- the parameter / dataset / mesh-size variant.

Examples:

```text
experiments/20260513_dsac-gaussian_advdiff-d4_seed01/
experiments/20260513_dsac-gaussian_advdiff-d4_seed02/
experiments/20260514_c51_advdiff-d4_seed01/
```

The naming MUST be deterministic enough that `ls experiments/*<algo>*`
finds all runs of one algorithm.

## Per-run layout

```text
experiments/<run-id>/
├── README.md          one-paragraph "what was this run for? which
│                      paper section / figure does it feed?"
├── metadata.json      machine-readable provenance (see schema below)
├── params.yaml        the parameters used
├── run.sh             the script that produces the run
│
├── output/            numerical outputs (gitignored if large; tracked
│                      if small + diff-able)
├── analysis/          post-hoc analysis scripts + figures (drafts)
└── notes.md           freeform notes, observations, gotchas
```

## metadata.json schema

The canonical machine-readable provenance record. Fill in EVERY field;
explicit `null` is better than omission.

```json
{
  "run_id": "20260513_dsac-gaussian_advdiff-d4_seed01",
  "kicked_off": "2026-05-13T14:23:01-05:00",
  "completed": "2026-05-13T14:31:47-05:00",
  "wall_clock_seconds": 526.0,
  "peak_memory_mb": 412.3,
  "hardware": {
    "host": "<machine name or 'cluster <name>'>",
    "cpu": "<e.g. AMD EPYC 7763 64-Core>",
    "gpu": "<e.g. NVIDIA A100 40GB; or 'none'>",
    "n_mpi_ranks": 1,
    "n_omp_threads": 1
  },
  "code": {
    "library_commit": "<git rev-parse HEAD of the supporting library at run time>",
    "library_dirty": false,
    "library_version": "0.1.0+g<short-hash>",
    "library_repo": "<URL of the upstream library repo, if external>"
  },
  "environment": {
    "lockfile_hash": "<sha256 of uv.lock / pixi.lock at run time>",
    "python": "3.12.3",
    "key_dependencies": {
      "numpy": "2.0.1",
      "scipy": "1.13.0",
      "<library-name>": "0.1.0+g<short-hash>"
    }
  },
  "rng_seed": 12345,
  "params_path": "params.yaml",
  "params_hash": "<sha256 of params.yaml>",
  "tags": ["section-5.2", "table-3", "figure-7a"],
  "linked_paper_section": "Section 5.2",
  "linked_paper_figure": "Figure 7a",
  "result_summary": "<one sentence: e.g. 'CVaR-EIG 0.247 +/- 0.012 over 30 seeds'>"
}
```

The `code.library_commit` + `environment.lockfile_hash` + `rng_seed`
triple is the **minimum reproducibility set**. The
`linked_paper_section` + `linked_paper_figure` fields are the
paper-side audit trail: the paper should cite the run-id (or the
`experiments/<run-id>/` path) for every reported number that came from
this directory.

## Run discipline

When kicking off a run that will feed the paper:

1. **Commit the supporting library before running.** A run on a dirty
   working tree records `library_dirty: true` in metadata; reviewers
   should treat dirty-tree results as preliminary.
2. **Set the RNG seed explicitly.** Every paper-cited result must be
   reproducible from the recorded seed.
3. **Capture wall-clock + peak memory** -- reviewers and editors ask
   "how long does this take?" + "what hardware do I need?".
4. **Tag the run** in `metadata.json` with the paper section + figure
   it supports. This is the bidirectional audit trail.

When tagging the paper for submission:

1. Tag the supporting-library commit AND the supporting-data version
   (`v0.1-paper-submission`).
2. Push tag; Zenodo auto-archives.
3. Record the per-version DOI in this repo's `CITATION.cff` AND in
   `experiments/<run-id>/metadata.json` for every run that produced a
   submission-cited number.

## What to commit vs gitignore

- **Track**: `README.md`, `metadata.json`, `params.yaml`, `run.sh`,
  `analysis/*.py`, `notes.md`, small numerical outputs (a few KB,
  diff-able).
- **Gitignore**: `output/` if large; `checkpoints/`; `raw/` (input
  data). Per `templates/paper-skeleton/.gitignore`.

For non-trivial output sizes (>100MB total or >10s of files), consider
DVC (https://dvc.org); but only after the simple approach has shown
to be insufficient.

## Cross-references

- This file's discipline mirrors
  `~/.scicomp-research-skills/templates/software-skeleton/experiments/README.md`.
- The audit-trail pattern is the analog of `references/_collection_log.md`
  (which audits the BIBLIOGRAPHY); this directory audits the EXPERIMENTAL
  RESULTS that feed the paper.
- For paper sections that cite multiple runs (e.g. a comparison table),
  list all the run-ids in the corresponding `notes/section_<N>.md`.

---

*Created YYYY-MM-DD by <your name> from
[`scicomp-research-skills/templates/paper-skeleton/experiments/README.md`](https://github.com/a-attia/scicomp-research-skills/tree/main/templates/paper-skeleton/experiments/README.md).*
