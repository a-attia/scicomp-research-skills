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
  or PR) is in `~/.scicomp-research-skills/CONTRIBUTING.md`.

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

## Maintenance

- When a new note is added, append a row to the relevant index above.
- When a note's status changes (designing -> building -> shipped, or
  active -> archived), update the Status column.
- When a note becomes obsolete (component removed, area redesigned),
  do NOT delete the note -- mark its status `archived` and keep it
  for the historical record.
- The `agent_feedback.md` file is self-indexing (chronological at
  the bottom); it does NOT appear in the index tables above.

---

*Created YYYY-MM-DD by <your name> from
[`scicomp-research-skills/templates/software-skeleton/notes/README.md`](https://github.com/a-attia/scicomp-research-skills/tree/main/templates/software-skeleton/notes/README.md).*
