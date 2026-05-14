---
name: Figure update needed
about: A figure in the paper needs to be regenerated, restyled, or replaced.
title: "[figure] <section>/<figure-name>: <reason>"
labels: figure
---

## Which figure

- **Path**: `figures/<paper-section>/<figure-name>.{pdf,png,py}`
- **Cited in paper**: Section <X>, Figure <N> (or Table <N> if
  applicable).
- **Generating script**: `figures/<paper-section>/<figure-name>.py`.

## Reason for update

<One paragraph. Common reasons:>

- [ ] **New experiment data** -- the underlying `experiments/<run-id>/`
      changed; figure needs regeneration with fresh inputs.
- [ ] **Reviewer requested style change** -- different colour scheme /
      legend / annotation / scale.
- [ ] **Reviewer requested additional data** -- more methods / more
      seeds / more parameter values shown on the same axes.
- [ ] **Reviewer requested split / merge** -- this figure should
      become two figures, or two figures should merge.
- [ ] **Camera-ready polishing** -- font / size / DPI / page-fit
      adjustment for the final published version.
- [ ] **Caption change required** in addition to the figure (text
      change in the draft).
- [ ] **Bug in figure script** -- script produces wrong axes /
      mislabeled / broken legend; output is currently misleading.

## What changes

Be specific. Examples:

- "Add a third method (CVaR-EIG) alongside the existing two; legend
  needs new entry; colour palette extends to 3 categories."
- "Switch from log-y to log-log scale for x in [0.01, 100] regime."
- "Replace 200dpi PNG with vector PDF for inclusion in the final
  paper."
- "Re-render with the new run-id `experiments/20260520_dsac_advdiff_v2/`
  replacing the old `experiments/20260513_dsac_advdiff_v1/` (the v2
  has the bug-fixed library)."

## Linked experiments

If the figure consumes data from `experiments/`, name every
`<run-id>/` involved:

- `experiments/<run-id-1>/output/...`
- `experiments/<run-id-2>/output/...`

If a re-run is also needed, file a separate
`experiment-rerun-needed` issue + cross-reference here.

## Linked paper text

If the figure update changes the paper's claim or caption, list the
text changes:

- `drafts/main.tex` Section <X> caption: <old> -> <new>.
- `drafts/main.tex` Section <X> paragraph 3: requires a sentence
  acknowledging the new data.

## Linked rebuttal item (if applicable)

- Reviewer: R<N>.<M>.
- Or: internal-team request from <date>.

## Status

- [ ] Designed (sketch / decision recorded; new script logic clear).
- [ ] Generated (script run; PDF + PNG present).
- [ ] Visually verified (looks correct).
- [ ] Caption + paper text updated (if applicable).
- [ ] Committed (script + PDF + PNG in same commit; commit message
      names the change).
- [ ] `figures/<section>/README.md` "Last regenerated" + "Cited in"
      stamp updated.
