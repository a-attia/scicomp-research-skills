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
4. **Check the agent-feedback triggers** (see "Recording feedback
   into the project's agent-feedback journal" below). If any
   trigger fired during this session and the corresponding entry
   was not yet appended, append it now to
   `notes/agent_feedback.md`. This is the **upstream** deposit:
   it funds the periodic roll-up into improvements to the
   `scicomp-research-skills` repo itself.
5. **Tell the user explicitly** what was updated + what feedback
   (if any) was recorded, in the response message.

Skipping any of these is the most expensive bug in this whole
ecosystem -- it means the next session pays the same intake cost the
current one paid, AND the upstream skills repo never learns from this
project's experience.

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

## Recording feedback into the project's agent-feedback journal

Per-project repos that bootstrap from
`~/.scicomp-research-skills/templates/paper-skeleton/` ship with a
`notes/agent_feedback.md` file. It is the per-project feedback
channel into the upstream `scicomp-research-skills` repository --
observations recorded here are periodically rolled up by the
maintainer into upstream skill improvements.

The agent should **append an entry** to `notes/agent_feedback.md`
when any of the following triggers fires during a session:

1. **Self-caught rationalization** -- the agent caught itself about
   to act on a thought that's not in the
   `agent-resource-discipline` SKILL.md "Common rationalizations +
   rebuttals" table. The new rationalization deserves to be added
   upstream.
2. **Rule-application gap** -- a skill rule didn't apply cleanly
   to the situation (the rule was ambiguous, the situation had a
   sub-case the rule didn't address, the threshold was wrong, the
   rule contradicted another rule).
3. **Pattern discovery** -- a useful sub-protocol or convention
   emerged that isn't in any current skill, AND the pattern is
   plausibly useful in other projects (not specific to this
   project's domain).
4. **Workflow friction** -- a documented step felt awkward or had a
   dead-end the docs didn't anticipate.
5. **User-flagged** -- the user said "remember this feedback",
   "this is worth noting", "we should improve this in the upstream
   skills", or equivalent.
6. **Workaround invented** -- the agent had to invent a workaround
   that other projects would also need.

### Entry format

Use the skeleton from the project's `notes/agent_feedback.md`
header. Recap:

```markdown
## YYYY-MM-DD -- <one-line title>

**Project context**: <which sub-task, which session phase>.
**Trigger**: <agent-self-caught / user-flagged / external-failure / pattern-discovered>.
**Skill(s) involved**: <e.g. agent-resource-discipline, literature-survey>.
**Observation**: <what happened, in 1-3 sentences>.
**Proposed action**: <add rule X to skill Y / clarify Z / no change needed but worth noting>.
**Evidence / minimal repro**: <a code snippet, a quoted agent message, or "happened twice this session in <context>">.

Status: open
```

### Where to insert in the file

Append to the end (newest at the bottom). Replace the placeholder
`## YYYY-MM-DD -- (template entry; ...)` block on first real entry.

### When NOT to record

- The observation is specific to this project's domain (e.g. a
  domain-specific notation choice). Those belong in the project's
  PLAN.md "Open Questions" or a section note, not in
  `agent_feedback.md`.
- The observation is about the user's preference (e.g. "the user
  prefers tabs over spaces in this project"). Those belong in the
  project's `AGENTS.md` "Project-specific overrides" section.
- The observation is purely about the project's content (e.g. "this
  citation needs verification"). That goes in
  `references/_collection_log.md`.

The journal is for upstream-skill feedback only. Other persistent
notes go to other files.

### Surfacing the entry to the user

Per the universal "no silent action" rule, every journal entry the
agent appends should also be **mentioned in the response message**:
"I appended an entry to `notes/agent_feedback.md` recording <one
line>." The user then has the option to expand, edit, or remove the
entry before the session ends.

### Privacy

The journal lives in the project repo; nothing leaves until the user
explicitly rolls an entry up to a public upstream issue or PR. Until
then it is as private as the project repo itself. Sensitive content
(unpublished results, reviewer identities) can appear freely; the
roll-up step in `~/.scicomp-research-skills/CONTRIBUTING.md` is
where sanitisation happens.

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

## Mid-session memory: recitation against goal drift

Long sessions (those exceeding ~50 tool calls) suffer from a separate
failure mode: the original PLAN.md fades from the agent's recent
attention as conversation length grows. The Manus team identifies this
as the "lost-in-the-middle" pattern and addresses it via **recitation**
(`https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus`,
their rule 4): the agent periodically re-reads the plan into recent
context, where the model attends most strongly.

Concrete recitation rule:

- Every ~30-50 tool calls in a long session, re-`Read` the relevant
  section of `PLAN.md` (just the section the work is currently in, not
  the whole document).
- Likewise, before declaring a major sub-task complete, re-`Read` the
  outline of the sub-task from the relevant `notes/section_<N>.md` or
  `notes/impl_<component>.md`.

Recitation is cheap (~50-200 tokens per re-read). Goal drift is
expensive (the agent ends up working on the wrong sub-task, or the
right sub-task with the wrong constraints).

## Failures stay in the conversation; structural failures get logged

When a tool call fails mid-session (a dead URL, a rate limit, a file
not found, a bib entry that doesn't resolve), the temptation is to
silently retry or work around it. The Manus team's rule 5 ("keep the
wrong stuff in") is the right response: **let the failure sit in the
conversation** so the model adapts and avoids re-trying the same path.

For *structural* failures -- failures that are not transient and that
future sessions will hit too -- additionally log to the appropriate
audit entry:

- A citation's PDF is genuinely unobtainable -> note in the bib
  entry's `note` field AND log to `_collection_log.md` "Items not
  found / left for user".
- An arXiv ID is wrong (resolves to a different paper) -> add a
  "Corrections to apply" entry to `_collection_log.md`.
- A URL referenced in PLAN.md is dead -> log to `PLAN.md` "Open
  Questions" with the dead URL + when it was last reachable.
- A figure-generation script in `experiments/` fails reproducibly ->
  log in the run's metadata JSON + a note in `notes/section_<N>.md`.

The principle: in-session failures stay in the conversation for the
agent's adaptive use; structural failures additionally become part of
the persistent record so future sessions don't have to rediscover
them. Silent retries are forbidden; silent fixes are forbidden;
explicit logging is the way.

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

*Created 2026-05-13 by A. Attia. Revised 2026-05-13 (post-prior-art
audit): added "Mid-session memory: recitation against goal drift"
section codifying the Manus team's rule 4 (recitation as the simplest
defence against the lost-in-the-middle failure mode); added "Failures
stay in the conversation; structural failures get logged" section
codifying Manus's rule 5 + a routing table for which audit entry
gets which kind of structural failure. Revised 2026-05-13 (added
"Recording feedback into the project's agent-feedback journal"
section codifying the per-project feedback-channel triggers and
entry format; added step 4 to the last-action protocol so the
agent-feedback deposit becomes part of the routine; cross-referenced
upstream CONTRIBUTING.md for the roll-up procedure).*
