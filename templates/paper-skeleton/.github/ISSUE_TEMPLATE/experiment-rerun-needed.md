---
name: Experiment re-run needed
about: An experiment must be re-run -- bug fixed in the supporting library,
       new seed, new parameter, hardware change, or rebuttal-round expansion.
title: "[experiment] re-run <run-id>: <reason>"
labels: experiment
---

## Run ID

- **Original run-id**: `<original-date>_<algo>_<variant>` in
  `experiments/<original-date>_<algo>_<variant>/`.
- **New run-id (proposed)**: `<new-date>_<algo>_<variant>`.

## Reason for re-run

<One paragraph. Common reasons:>

- [ ] **Bug in supporting library** -- a bug was discovered in the
      upstream library code; the original run is invalid; need to
      re-run with the fixed library version.
- [ ] **Reviewer asked for a parameter sweep** -- specify which
      parameter + which range.
- [ ] **Reviewer asked for a different seed** -- specify which seed
      or "N additional seeds".
- [ ] **Hardware drift** -- the original ran on hardware no longer
      available; re-run on current hardware to confirm reproducibility.
- [ ] **Library version drift** -- a dependency upgrade changed
      behaviour; re-run to confirm the published number is robust.
- [ ] **Rebuttal-round expansion** -- adding additional baselines /
      ablations.

## What changes vs the original run

Be specific. The new run's `metadata.json` should differ from the
original's in clearly-enumerated ways:

| Field                   | Original                          | New                              |
|:------------------------|:----------------------------------|:---------------------------------|
| `code.library_commit`   | `<old hash>`                      | `<new hash>`                     |
| `rng_seed`              | `<old seed>`                      | `<new seed(s)>`                  |
| `params.yaml: <param>`  | `<old value>`                     | `<new value>`                    |
| `hardware.gpu`          | `<old GPU>`                       | `<new GPU>`                      |

## Acceptance criterion

What result would conclusively answer the question this re-run is
trying to address? Examples:

- "If the new run's headline metric is within 2% of the original's,
  the result is robust to <variation>; we confirm the published
  number."
- "If the new run's metric differs by >10%, the original publication
  needs an erratum."
- "If the new run produces results consistent with the original on
  3 additional seeds, we have higher confidence in the headline
  number."

## Linked rebuttal item (if applicable)

- Reviewer: R<N>.<M>.
- Or: internal-team request from <date> / commit hash.

## Estimated cost

- Wall clock per seed: <estimate>.
- Total seeds: <count>.
- Hardware: <CPU / GPU / cluster + node count>.

## Status

- [ ] Designed (metadata.json schema filled in).
- [ ] Kicked off (run.sh executed; logs streaming).
- [ ] Completed (output present; metadata finalised).
- [ ] Analysed (analysis scripts run; figure updated if applicable).
- [ ] Tagged + Zenodo-archived (if this is a submission-cited
      version).
