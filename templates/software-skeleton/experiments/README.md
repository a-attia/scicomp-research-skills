# experiments/

This directory holds **per-experiment workspaces**, one subdirectory
per logically distinct experimental run. The discipline here is the
single most important investment in reproducibility for this library:
a future-you (or a reviewer, or a downstream user) needs to be able
to take any published number from a paper or a notebook + walk
straight back to the code, parameters, environment, and seed that
produced it.

## Naming convention

```text
experiments/<date>_<algo>_<variant>/
```

- `<date>` -- `YYYYMMDD` of the run (when it was kicked off, not when
  it finished).
- `<algo>` -- the algorithm or method used (short identifier).
- `<variant>` -- the parameter variant, dataset variant, mesh size,
  or whatever distinguishes this run from sibling runs.

Examples:

```text
experiments/20260513_finite-element_linear-quad-mesh32/
experiments/20260513_finite-element_quadratic-quad-mesh32/
experiments/20260514_finite-volume_higher-order-mesh64/
```

The naming MUST be deterministic enough that a script can find a run
by searching for a substring (e.g. all linear-FE runs from May 2026:
`ls experiments/202605*_finite-element_linear*`).

## Per-run layout

Every run-dir contains the following files. Track all of them in
git EXCEPT large outputs (see `.gitignore`):

```text
experiments/<run-id>/
├── README.md          one-paragraph "what was this run for? what was
│                      the question? what was the result?"
├── metadata.json      machine-readable provenance (see schema below)
├── params.yaml        the parameters used (or params.toml / params.json)
├── run.sh             the script that produces the run, runnable as-is
│                      (or run.py if Python, run.jl if Julia, ...)
│
├── output/            numerical outputs of the run
│   └── ...            (gitignored if large; tracked if small + diff-able)
│
├── analysis/          post-hoc analysis scripts + figures
│   ├── plot_<X>.py
│   └── ...
│
└── notes.md           freeform notes, observations, gotchas
```

## metadata.json schema

This is the canonical machine-readable provenance record. Fill in
EVERY field; placeholders for "unknown" should be explicit (`null`
or `"unknown"`), not omitted.

> **Cross-stamp**: this schema is intentionally near-identical to the
> one in
> [`templates/paper-skeleton/experiments/README.md`](https://github.com/a-attia/scicomp-research-skills/tree/main/templates/paper-skeleton/experiments/README.md);
> the paper-skeleton variant adds two paper-specific fields
> (`code.library_repo`, `linked_paper_figure`). If you change one
> schema, change both to keep them in sync; reviewers + downstream
> tools may consume either.

```json
{
  "run_id": "20260513_finite-element_linear-quad-mesh32",
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
    "library_commit": "<git rev-parse HEAD of this library at run time>",
    "library_dirty": false,
    "library_version": "0.1.0+g<short-hash>"
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
  "tags": ["mms", "convergence-study", "section-5.2"],
  "linked_paper_section": "Section 5.2 of <paper-citekey> (if applicable)",
  "result_summary": "<one sentence: e.g. 'L2 error 4.3e-3 at h=1/32, observed rate 1.97'>"
}
```

The `code.library_commit` + `environment.lockfile_hash` + `rng_seed`
triple is the **minimum reproducibility set**: given those three,
the run can in principle be regenerated bit-for-bit.

## Run discipline

When kicking off a run:

1. **Commit before running.** A run on a dirty working tree records
   `library_dirty: true` in metadata; reviewers and future-you should
   treat dirty-tree runs as preliminary, not citable.
2. **Set the RNG seed explicitly.** Even if the algorithm appears
   deterministic, set the seed in `params.yaml` and have the script
   echo it to stdout for log capture.
3. **Capture wall-clock + peak memory** even if you don't think you'll
   need them. They become important the moment a reviewer asks "how
   long does this take?".
4. **Tag the run** in `metadata.json` with the paper section it
   supports (if applicable). This is the audit trail back to the
   paper.

When archiving a run:

1. **Verify metadata.json validates** against the schema above.
2. **If the run produces a published number**, additionally:
   - Tag the corresponding library commit
     (`v0.x-paper-submission-<run-id>`).
   - Push the tag (Zenodo will mint a per-version DOI).
   - Record the per-version DOI in `metadata.json` under a new
     `archival.zenodo_doi` field.

## What to commit vs gitignore

- **Track**: `README.md`, `metadata.json`, `params.yaml`, `run.sh`,
  `analysis/*.py`, `notes.md`, small numerical outputs (a few KB each,
  diff-able).
- **Gitignore**: `output/` (if large), `checkpoints/`, `raw/` (input
  data), large binary outputs.

The bare per-run dir + metadata + script is enough to regenerate
everything else. Large outputs that can be regenerated should be
treated as derived artifacts, not source.

For non-trivial output sizes (>100MB total or >10s of files), consider
DVC (https://dvc.org) or an equivalent data-version-control tool, but
**only after the simple approach has shown to be insufficient**. Per
the `research-software-engineering` skill: use the lightest tool that
does the job.

## Cross-references

- The `experiments/<run-id>/metadata.json` schema is the analog of
  the literature-survey skill's `references/_collection_log.md`
  per-entry table -- both are audit trails. See
  `~/.scicomp-research-skills/skills/human-facing-doc-authoring/references/audit-log-structures.md`
  for the universal audit-log conventions.
- For runs that support a published paper, link the run-id from the
  paper repo's `experiments/` (mirror layout) so the paper-side and
  code-side audit trails reconcile. This is the **code-paper
  coupling** discipline (planned reference 08 of
  `research-software-engineering`).

---

*Created YYYY-MM-DD by <your name> from
[`scicomp-research-skills/templates/software-skeleton/experiments/README.md`](https://github.com/a-attia/scicomp-research-skills/tree/main/templates/software-skeleton/experiments/README.md).*
