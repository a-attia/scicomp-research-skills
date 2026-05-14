# Context-window budget

Loaded on demand from the `agent-resource-discipline` skill when a
session is loading multiple skills, multiple reference files, or
multiple PDFs simultaneously.

The agent's context window is finite. Spending it on material that
isn't actively driving the current decision is waste.

---

## The single rule

**Load only what you are about to use; unload at topic boundaries.**

Concretely:

| Item                                              | Soft limit                                          |
|:--------------------------------------------------|:----------------------------------------------------|
| Skills loaded simultaneously                      | 2 (the active task skill + at most one cross-cutting skill, e.g. `human-facing-doc-authoring` or `agent-resource-discipline`). |
| Reference files loaded per skill                  | 1 at a time (load on demand; the SKILL.md is enough until you need a specific reference). |
| PDFs / `.txt` extractions actively consulted      | 3 (read, summarise into a note, close before opening a 4th). |
| Survey notes loaded simultaneously                | 5 (when drafting a paper section that cites many; otherwise 1-2). |
| Project files loaded at session start (intake)    | 4 (AGENTS.md, PLAN.md, _collection_log.md, notes/README.md). |
| Open `Read` results held in working memory        | The minimum that lets the next decision be made.    |

These are soft limits -- if a task genuinely needs more, exceed them
and accept the cost. The point is to NOTICE when you're loading more
than this and ask "do I need all of this for the next decision?".

## Skill loading: one + one

Most sessions need exactly ONE task skill. Examples:

- Writing or revising a paper draft -> `research-paper-writing`.
- Bibliography pass -> `literature-survey`.
- Writing a README, PLAN, survey note for human review ->
  `human-facing-doc-authoring`.
- Heavy file/PDF/web work -> `agent-resource-discipline`.

Common second-skill pairings:

- `literature-survey` + `human-facing-doc-authoring` (the survey note
  is human-facing).
- `research-paper-writing` + `human-facing-doc-authoring` (when
  drafting alongside a section research note).
- Any of the above + `agent-resource-discipline` (when the work is
  heavy enough to need explicit budgeting).

**Avoid loading 3+ skills.** If a task seems to need three skills,
split it into two passes by topic boundary.

## Reference-file loading: lazy + targeted

Each skill has a SKILL.md (~200-300 lines) plus a `references/`
subfolder. The SKILL.md is loaded when the skill is loaded; the
references are loaded **on demand** by name when the SKILL.md points
at them.

Examples:

- `research-paper-writing/SKILL.md` says "for Introduction, load
  `references/introduction.md`". Load THAT ONE, not the whole
  references/ tree.
- `human-facing-doc-authoring/SKILL.md` has 5 references for 5
  different doc types. Load only the one matching the doc you're
  writing.
- `agent-resource-discipline/SKILL.md` has 5 references for 5
  disciplines. Load only the ones matching the current session's work.

**Avoid loading all references "just in case".** They are written to
be loaded individually + on demand precisely so this works.

## PDF / .txt budget

PDFs (via their `.txt` extractions) are the densest content type. A
single 30-page paper's `.txt` can be 1500 lines.

When working on a literature pass:

- Process PDFs **one at a time**: open `.txt`, write survey note,
  close `.txt`, move to next PDF.
- Do NOT bulk-load 14 PDFs at once. Even though each `.txt` is small
  enough to fit, in aggregate they swamp the context.
- The survey note (~30-50 lines) is the compressed form. Once the
  note exists, future sessions read the note (small) instead of the
  `.txt` (large).

When DRAFTING a paper section that cites many papers:

- Load the survey notes (5-10 small files) NOT the `.txt` extractions.
- If a fact in a survey note isn't enough, target-grep the specific
  `.txt` for the missing detail; do not load the whole `.txt`.

## Topic-boundary unloading

When you finish one logical sub-task and start another, ask: do I
still need everything I've loaded?

Examples of topic boundaries:

- Switching from "verifying bibliography" to "drafting a section":
  the `.txt` extractions are no longer needed; the survey notes are.
- Switching from "Section 3 drafting" to "Section 4 drafting": the
  Section 3 survey notes may not all be relevant to Section 4.
- Switching from "implementing component A" to "implementing component
  B": the `notes/impl_A.md` is done; load `notes/impl_B.md`.

The agent cannot literally "unload" content from its context window
mid-session, but it CAN avoid re-citing or re-referencing material
from earlier loads, which keeps later actions cheap.

## When the budget is breached

Symptoms that you're over budget:

- The agent's responses get terser as the session progresses
  (context-pressure symptom).
- The agent starts forgetting details from earlier in the session.
- The agent re-reads files it already read.
- The agent loses track of what step of a multi-step task it's on.

Recovery:

1. **Summarise the session's progress** into a short status update
   (3-5 bullets) and commit it to a note file
   (`notes/session_<date>.md` or similar).
2. **End the session** with the explicit save-point + last-action
   protocol updates.
3. **Start a fresh session** that loads only the indices + the
   skill+references needed for the NEXT step.

A clean save-point + clean restart is cheaper than thrashing in an
overfull context.

## Anti-patterns

- **"Let me just load everything in case I need it."** No -- that's
  the exact failure mode this skill exists to prevent.
- **"I'll load this 5000-line file briefly and then it's out of my
  way."** It isn't. The bytes stay in the context window.
- **"I'll re-read this file because I might have missed something."**
  Read your own previous summary first; only re-read if the summary
  is suspect.
- **"I'll load both `research-paper-writing/references/introduction.md`
  and `references/method.md` because I'm writing both today."** Load
  one, finish the introduction, then load the other for the method.

---

*Created 2026-05-13 by A. Attia.*
