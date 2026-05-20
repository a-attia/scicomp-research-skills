# notes/

This directory holds working notes for the library:

- **`impl_<component>.md`** -- one per significant new component.
  Created BEFORE the component's code lands. Captures: purpose,
  public API surface, dependencies, design sketch, trade-offs
  considered, testing plan, risks, action items. Survives the
  component's lifetime as the design audit trail. See
  `~/.scicomp-research-skills/skills/human-facing-doc-authoring/references/notes-structures.md`
  section C for the canonical template.
- **`section_<topic>.md`** -- working notes for a specific area of
  the library (e.g. `section_solvers.md`, `section_io.md`). Less
  formal than impl notes; useful for cross-cutting concerns that
  don't map to a single component. See
  `~/.scicomp-research-skills/skills/human-facing-doc-authoring/references/notes-structures.md`
  section B.
- **`agent_feedback.md`** -- per-project feedback channel into the
  upstream
  [`scicomp-research-skills`](https://github.com/a-attia/scicomp-research-skills)
  repository. The agent appends entries when a skill rule was
  insufficient, a workaround was needed, or a useful pattern was
  discovered. Roll-up procedure (sanitise + file an upstream issue
  or PR) is in `~/.scicomp-research-skills/CONTRIBUTING.md`. Entries
  that have been actioned upstream are collapsed to a stub linking
  to their full text in [`_resolved/`](_resolved/INDEX.md); see the
  "Archive + resolution log" section below.

## Index of impl notes

(Update as new impl notes are added. One row per component.)

| Component       | File                                          | Status                  | Code path        |
|:----------------|:----------------------------------------------|:------------------------|:-----------------|
| `<component-1>` | [`impl_<component-1>.md`](impl_<component-1>.md) | <designing / building / shipped> | `src/<lib>/<path>` |
| `<component-2>` | [`impl_<component-2>.md`](impl_<component-2>.md) | <...>                   | `src/<lib>/<path>` |

## Index of section notes

(Update as new section notes are added.)

| Topic           | File                                  | Status                  |
|:----------------|:--------------------------------------|:------------------------|
| `<topic-1>`     | [`section_<topic-1>.md`](section_<topic-1>.md) | <active / archived>     |

## Archive + resolution log

Two parallel sub-directories hold entries / artefacts that have moved
out of the project's active working set but are preserved for
traceability (convention added 2026-05-20 from real-project evidence
on argo-anywhere + AmigAI):

- **[`_resolved/INDEX.md`](_resolved/INDEX.md)** -- `agent_feedback.md`
  entries that have been actioned upstream (codified into a
  `scicomp-research-skills` skill / reference / template). Each
  resolved entry's original text is preserved in
  `_resolved/<date>_<slug>.md`; the entry's date+title stub
  remains in `agent_feedback.md` pointing here. The index also
  tracks "partial resolutions" -- entries whose body proposed
  multiple things, only some of which shipped upstream.
- **[`_archive/INDEX.md`](_archive/INDEX.md)** -- superseded /
  filed-elsewhere artefacts (e.g. upstream-proposal drafts that
  became GitHub issues; working-document versions that were
  fully replaced; impl notes for components later removed).

The two are kept separate because "resolved upstream" and
"superseded / filed elsewhere" are different kinds of "done" and
conflating them loses information. Note: a removed-component impl
note belongs in `_archive/` (the component is gone); a still-active
impl note whose status went `building -> shipped` stays in the main
index above with status `shipped`.

When adding a new entry to either: append a row to the
corresponding INDEX.md AND (for `_resolved/`) create the
date-slugged file with the full original content; update the
stub in `agent_feedback.md` to point at the new file.

## Maintenance

- When a new note is added, append a row to the relevant index above.
- When a note's status changes (designing -> building -> shipped, or
  active -> archived), update the Status column.
- When a note becomes obsolete (component removed, area redesigned),
  do NOT delete the note -- mark its status `archived` and keep it
  for the historical record. For components removed entirely, move
  the impl note into `_archive/` per the archive convention above.
- The `agent_feedback.md` file is self-indexing (chronological at
  the bottom); it does NOT appear in the index tables above. For
  `agent_feedback.md` entries actioned upstream, follow the
  archive+resolved procedure above.

---

*Created YYYY-MM-DD by <your name> from
[`scicomp-research-skills/templates/software-skeleton/notes/README.md`](https://github.com/a-attia/scicomp-research-skills/tree/main/templates/software-skeleton/notes/README.md).*
