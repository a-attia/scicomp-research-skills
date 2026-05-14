# notes/ index

This directory holds working notes for the paper:

- **`survey_<citekey>.md`** -- one per literature reference (citekey
  matches `../references/bibliography.bib`). Each ~30-50 lines: claim,
  full method with key equations, test cases + parameters, headline
  numerical results, citation context, action items for our paper.
  Produced via the `literature-survey` skill in scicomp-research-skills.
- **`impl_<component>.md`** -- one per planned new code component
  (created before any code lands in the upstream repo).
- **`section_<N>.md`** -- one per draft paper section (research notes
  aggregating the relevant survey-note action items + experiment results
  + figure references).
- **`agent_feedback.md`** -- the per-project feedback channel into the
  upstream `scicomp-research-skills` repository. The agent appends
  observations here when a skill rule was insufficient, a workaround
  was needed, or a useful pattern was discovered. Roll-up procedure
  (sanitise + file an upstream issue) lives in
  `~/.scicomp-research-skills/CONTRIBUTING.md`.

This README is the index over the **survey notes** only. The other
three kinds (`impl_*.md`, `section_*.md`, `agent_feedback.md`) are
self-indexing; they get their own per-file structure described in
the upstream `human-facing-doc-authoring` skill's reference files.
Update the tables below as new survey notes are added.

## Status (YYYY-MM-DD)

- Section 1.X (<topic>): <N> notes, <status>.
- Section 1.Y (<topic>): <N> notes, <status>.

## Index by PLAN.md section

### Section 1.X -- <topic>

| Citekey      | File                          | Year | Status     |
|:-------------|:------------------------------|:-----|:-----------|
| `<citekey>`  | [survey_<citekey>.md](survey_<citekey>.md) | <year> | <full read / stub / pending> |

### Section 1.Y -- <topic>

| Citekey      | File                          | Year | Status     |
|:-------------|:------------------------------|:-----|:-----------|

## Index by paper section affinity

Maps each survey note to the PLAN.md / paper-draft sections it most
directly informs. A note can appear in multiple rows.

### PLAN.md "Headline Contribution" / paper Section 1 "Introduction"

Most-cited surveys for the positioning paragraph + novelty claim:

- `<citekey>` -- <one-line reason>

### PLAN.md Section 3 / paper Section 3 "<Section title>"

- `<citekey>` -- <one-line reason>

### PLAN.md Section 5 / paper Section 4 "Methodology"

- `<citekey>` -- <one-line reason>

### PLAN.md Section 2 / paper Section 5 "Test case"

- `<citekey>` -- <one-line reason>

### PLAN.md Section 6 / paper Section 6 "Experiments"

- `<citekey>` -- <one-line reason>

### PLAN.md Section 7 / paper Section 7 "Discussion"

- `<citekey>` -- <one-line reason>

### Background citations only

Used as foundational references in the paper's Section 2 "Background"
but not as direct competitors:

- `<citekey>` -- <one-line reason>

## Maintenance

- When a new survey note is added, append a row to all relevant
  by-section + by-affinity tables above.
- When a survey note's status changes (stub -> full read, or full read
  -> updated after re-reading), update the Status column in the
  relevant by-section table.
- This README does NOT track impl notes or section notes -- those will
  get their own indexes when the first impl/section notes are written.
