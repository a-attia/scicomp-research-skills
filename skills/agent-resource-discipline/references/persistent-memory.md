# Persistent memory across sessions

Loaded on demand from the `agent-resource-discipline` skill at the
start of any session on a project that has the standard layout
(PLAN.md + collection log + notes index).

Agents do not have memory across sessions. The PROJECT files DO. The
project's indices (`PLAN.md` status fields, `_collection_log.md`,
`notes/README.md`) are the persistent memory. Read them first; update
them last.

---

## The withdrawal-and-deposit metaphor

- **Withdrawal** = first action of a session: read the indices to
  recover the prior state cheaply (4 small reads).
- **Deposit** = last action of a session: update the indices to fund
  the next session's withdrawal.

If every session deposits, every session's withdrawal is cheap. If a
session skips the deposit, the next session has to either re-derive
the missing state (expensive) or proceed in ignorance (risky).

## First-action protocol

At the start of any non-trivial session, in PARALLEL (single message,
multiple `Read` calls):

1. `Read` the project's `AGENTS.md` -- skills to load, project-specific
   facts.
2. `Read` the project's `PLAN.md` -- focusing on:
   - the status / date-stamp at the top;
   - the "Open Questions" section near the bottom;
   - the section relevant to today's task.
3. `Read` the project's `references/_collection_log.md` (if
   bibliography work is involved) -- focusing on:
   - the "Last updated" stamp;
   - any "Corrections to apply (deferred)" section;
   - any entries marked `[VERIFY]` or `placeholder`.
4. `Read` the project's `notes/README.md` (if survey work is involved)
   -- the index over survey notes; tells you which exist and at what
   quality (full / stub / pending).

Total cost: 4 reads, each typically <200 lines (PLAN.md may be larger;
target the relevant section with `offset`+`limit` if so).

Output: the agent now knows what state the project is in, what the
prior session decided, and what is pending.

## Last-action protocol

Before declaring a session done, in any session that produced new work:

1. **Update `notes/README.md`** if any survey note was added or its
   status changed (stub -> full, full -> updated):
   - Add / update the row in the per-section table.
   - Update the row in the by-affinity table if the note is now
     relevant to a paper section it wasn't before.
2. **Update `references/_collection_log.md`** if any bibliography
   work was done:
   - Append a row to the per-section status table for new citekeys.
   - Add a row to "Corrections to apply (deferred)" for any
     corrections discovered.
   - Update the "Last updated" stamp at the top.
3. **Update `PLAN.md`** if status changed:
   - Update the Status callout at the top.
   - Tick off completed items in section-specific status lists.
   - Update the "Action." trailing notes per section if the action
     changed.
   - Append to "Open Questions" if new ones emerged.
4. **Tell the user explicitly** what was updated, in the response
   message.

Skipping any of these is the most expensive bug in this whole
ecosystem -- it means the next session pays the same intake cost the
current one paid.

## Typical waste modes (and what to do instead)

| Waste mode (avoid)                                | Discipline (do)                                                         |
|:--------------------------------------------------|:------------------------------------------------------------------------|
| Re-verifying a citekey already verified           | Check `_collection_log.md` first; the entry is there with date-stamp.  |
| Re-summarising a paper that has a survey note     | Read the survey note first; only re-summarise if the note is wrong.    |
| Re-deriving a method choice that PLAN.md decided  | Check PLAN.md Section 3 / Section 5 before deciding.                   |
| Drafting a paragraph the previous session drafted | Check `notes/section_<N>.md` and `drafts/main.tex` first.              |
| Re-running an experiment whose results exist      | Check `experiments/` for the matching run dir.                         |

## Surfacing contradictions

When a session discovers a fact that contradicts existing project
state (a wrong citekey, a wrong year on an existing entry, a method
description that doesn't match the paper, an experiment result that
contradicts an earlier one):

1. **Do NOT silently fix it.** Silent fixes break the audit trail.
2. **Add a "Corrections to apply" entry** to the appropriate audit
   log:
   - Bibliography correction -> `references/_collection_log.md`.
   - Plan correction -> `PLAN.md` "Open Questions" or a new
     "Corrections to apply" subsection.
   - Method-description correction -> the relevant
     `notes/survey_<citekey>.md` (with a Revised stamp).
3. **Surface in the response message** to the user. They decide
   whether to apply the correction now or defer to a batched revision
   pass.

This protocol is what makes the indices trustworthy. Without it, the
indices drift from reality; with it, they remain the canonical
record.

## Index hierarchy

The indices form a small hierarchy:

```text
AGENTS.md                                  (project-wide rules + facts)
   |
   +-- PLAN.md                             (the contract; living)
   |     |
   |     +-- references/bibliography.bib   (verified citations)
   |     +-- references/_collection_log.md (verification audit trail)
   |     +-- notes/README.md               (survey-note index)
   |     |     |
   |     |     +-- notes/survey_*.md       (per-paper notes)
   |     |
   |     +-- notes/section_*.md            (per-section research notes)
   |     +-- notes/impl_*.md               (per-component impl plans)
   |
   +-- experiments/<run-id>/               (per-run results + metadata)
```

When reading at session start, walk the hierarchy top-down: AGENTS.md
-> PLAN.md -> the index files. Do not dive into individual survey
notes / experiment runs unless the task requires it.

## Multi-session workflows

Some tasks span sessions deliberately:

- **Bibliography sweep**: session 1 verifies 5 of 14 entries; session
  2 picks up at entry 6. The collection log + bibliography.bib's per-
  section organisation makes this cheap iff session 1 deposited
  properly.
- **Section drafting**: session 1 drafts paragraphs 1-3; session 2
  drafts 4-6. The `notes/section_<N>.md` working note + the draft file
  itself make this cheap iff session 1 stopped at a paragraph boundary
  + recorded what's done in `notes/section_<N>.md`.
- **Experiment iteration**: session 1 designs the experiment + runs
  one seed; session 2 runs the full seed sweep + analyses. The
  `experiments/<run-id>/` per-run dir + a per-experiment notes file
  make this cheap.

In each case, the session boundary is a SAVE POINT. Treat it
explicitly: leave the project in a state where "session 2" knows
exactly where to resume.

---

*Created 2026-05-13 by A. Attia.*
