# Contributing to scicomp-research-skills

Thanks for taking the time to contribute. This repository improves only
when real research projects use it and feed back what worked, what
didn't, and what was missing. The whole point of versioning the skills
in git is so that those observations become tracked, dated improvements
rather than oral tradition.

This document is for **humans**. The agent-facing entry point is
[`AGENTS.md`](AGENTS.md).

---

## Contents

- [The feedback loop in one diagram](#the-feedback-loop-in-one-diagram)
- [Per-project feedback journal](#per-project-feedback-journal)
- [Rolling project journals into proposals](#rolling-project-journals-into-proposals)
- [Filing an issue](#filing-an-issue)
- [Submitting a pull request](#submitting-a-pull-request)
- [What changes need what evidence](#what-changes-need-what-evidence)
- [Style + commit conventions](#style--commit-conventions)
- [Maintainer cadence](#maintainer-cadence)

---

## The feedback loop in one diagram

```text
real research project session
            |
            v
   notes/agent_feedback.md          <-- per-project journal (one entry per
            |                            session that produced feedback)
            v
periodic roll-up by maintainer
            |
            +--> minor fix     -> direct PR
            |
            +--> medium change -> GitHub issue using ISSUE_TEMPLATE/skill-improvement-from-experience
            |
            +--> new skill     -> GitHub issue using ISSUE_TEMPLATE/new-skill-proposal
            |
            +--> bug           -> GitHub issue using ISSUE_TEMPLATE/skill-bug
            |
            v
  PR against scicomp-research-skills
            |
            v
       merged + git pull
            |
            v
  refreshed canonical checkout on every machine
```

The loop has three layers, each catching feedback at a different level
of effort:

1. **Per-project journal** (cheap, in-session): the agent records
   observations as they happen, into `notes/agent_feedback.md` of the
   project being worked on. No friction; never leaves the project repo.
2. **GitHub issues** (medium): when a journal entry seems to deserve
   action, it's promoted to an issue here using a templated form that
   asks for the specific evidence the maintainer needs.
3. **Pull requests** (high): for changes whose shape is already clear
   (a typo fix, a new entry in a rationalizations table, a new
   reference file), open a PR directly.

Skip layers when the situation is clear (a typo doesn't need an
issue first; a brand-new skill should be discussed in an issue
before a PR).

---

## Per-project feedback journal

Every project bootstrapped from
[`templates/paper-skeleton/`](templates/paper-skeleton/) ships with a
`notes/agent_feedback.md` file pre-created. It is the lowest-friction
place to capture observations as they happen.

### When to add an entry

The agent (per `agent-resource-discipline/references/persistent-memory.md`)
will add an entry when:

- it caught itself in a rationalization the rebuttals table didn't
  cover;
- a skill rule didn't apply cleanly to the situation;
- it discovered a useful pattern not yet codified;
- the user said "remember this feedback" or "this is worth noting";
- a step in a documented workflow failed or felt awkward;
- it had to invent a workaround that other projects would also need.

Humans can add entries any time, with no specific trigger needed.

### What an entry looks like

Each entry is short -- 5-15 lines -- and structured so that a future
roll-up pass can act on it without paging the original session
context. Use this skeleton (it's also in the file's header):

```markdown
## YYYY-MM-DD -- <one-line title>

**Project context**: <which project, which sub-task, which session>.
**Trigger**: <what surfaced this; agent-self-caught / user-flagged /
external-failure>.
**Skill(s) involved**: <e.g. agent-resource-discipline,
literature-survey>.
**Observation**: <what happened, in 1-3 sentences>.
**Proposed action**: <add rule X to skill Y / clarify Z / no change
needed but worth noting>.
**Evidence / minimal repro**: <a code snippet, a quoted agent message,
or "happened twice this session in <context>">.

Status: open / rolled-up to issue #N / rolled-up to PR #N / wontfix.
```

### Privacy / scope

The journal lives **in the project repo**, not here. If the project
repo is private, the journal stays private until the user explicitly
copies an entry into a public issue or PR here. Sensitive content
(unpublished results, reviewer identities, internal data) should
NEVER appear in entries that get rolled up to this public repo --
the per-project journal is the place to write naturally; the
roll-up step is where you sanitise.

---

## Rolling project journals into proposals

Periodically (e.g. once per major project milestone, or once per
month for active projects), review `notes/agent_feedback.md` and
decide what to roll up. Useful triage questions:

- **Is this a one-off or a pattern?** A pattern that occurred 3+
  times across different sub-tasks deserves codification. A one-off
  weirdness probably doesn't.
- **Would another project have hit the same thing?** If yes -> roll
  up. If it's specific to this project's domain -> stays local.
- **Is the proposed action concrete?** Vague "the agent should be
  smarter about X" is not actionable; "add rule X to skill Y's
  rationalizations table" is.

Once you've identified an entry to act on:

1. Mark its `Status:` line in the journal as
   `rolled-up to issue #N` (after filing) or `rolled-up to PR #N`
   so future roll-up passes skip it.
2. File the appropriate issue or PR (see below).
3. Sanitise the content during the roll-up step (remove project-
   specific names, quote only the minimum reproducible context).

---

## Filing an issue

Use one of the three templates in
[`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/):

| Template                                | When to use                                                                                              |
|:----------------------------------------|:---------------------------------------------------------------------------------------------------------|
| `skill-bug.md`                          | Something in a skill is wrong (broken cross-reference, contradictory rules, mis-cited prior art).        |
| `skill-improvement-from-experience.md`  | A skill rule was insufficient or unclear; you have evidence from at least one real session.              |
| `new-skill-proposal.md`                 | A pattern recurred across multiple sessions / projects and isn't covered by any existing skill.          |

The templates prompt for the specific evidence the maintainer needs
to act -- citations from `notes/agent_feedback.md`, project context,
proposed rule text, etc. Filling the template is the single most
useful thing you can do to make a change land.

If you're not sure which template fits, use
`skill-improvement-from-experience.md` and let the maintainer
re-categorise.

---

## Submitting a pull request

For changes whose shape is already clear:

1. Fork or branch from `main`.
2. Make the change in your **dev checkout** (NOT
   `~/.scicomp-research-skills/` -- the pre-commit hook will refuse).
3. If touching a skill, update the skill's date-stamp footer with a
   `Revised YYYY-MM-DD (note about the revision)` line.
4. If touching the root `AGENTS.md`, also update its date-stamp
   footer.
5. Run `shellcheck -x bin/*.sh .githooks/pre-commit` if you touched
   shell scripts. (CI runs this on push.)
6. Commit with a conventional-commit-style message
   (`feat:` / `fix:` / `docs:` / `chore:` / `ci:`). No
   `Co-Authored-By` trailers.
7. Open a PR against `main` referencing the issue (if any) and
   citing the journal entries that motivated the change.

PRs without evidence (no journal entry, no issue, no real-world
context) are still welcome but will move slower; "this seems like a
good idea" is harder to evaluate than "this fired three times in two
projects".

---

## What changes need what evidence

| Change type                                    | Minimum evidence                                                                                                      |
|:-----------------------------------------------|:----------------------------------------------------------------------------------------------------------------------|
| Typo / formatting fix                          | None. Just open the PR.                                                                                               |
| Tightening or clarifying an existing rule      | One concrete session / journal entry where the current rule was ambiguous.                                            |
| Adding a new rule to an existing skill         | Two concrete sessions / journal entries where the rule would have helped, or one where its absence caused real cost. |
| Adding a new rationalization to the rebuttals  | One concrete session where the agent thought this exact thing.                                                        |
| Adding a new reference file under a skill      | A clear scope (load on demand for what kind of task) + at least one existing rule that overflows the parent SKILL.md. |
| Adding a new top-level skill                   | A pattern recurring across 3+ sessions / 2+ projects + a one-page proposal in a `new-skill-proposal` issue.           |
| Removing or substantially changing a rule      | Evidence the current rule causes harm OR is no longer correct (e.g. tooling has changed). Include a deprecation plan. |

The point of these requirements is **not gate-keeping** -- it is to
make sure proposals come with the context that lets the change be
evaluated honestly + lets future maintainers understand why each
rule exists.

---

## Style + commit conventions

These are the universal conventions from
[`AGENTS.md`](AGENTS.md) Section 6 that apply to docs and skills:

- **ASCII only** in code, code comments, code-style docstrings.
  Markdown documentation may use non-ASCII for readability.
- **Math notation**: LaTeX via MathJax (`$...$` inline, `$$...$$`
  display). No ASCII-art math in production docs.
- **Date-stamping**: every plan-of-record-style document
  (`AGENTS.md`, every `SKILL.md`, every plan-or-log doc) ends with a
  `*Created YYYY-MM-DD. Revised YYYY-MM-DD (note). Maintained by <name>.*`
  footer.
- **Code references**: `path/to/file:line_number` so the user can
  navigate directly.
- **No emojis** in code, code comments, code docstrings, or
  production docs (unless the user explicitly requests them).
- **Commit messages**: conventional-commit style preferred
  (`feat: ...`, `fix: ...`, `docs: ...`); no `Co-Authored-By`
  trailers; no automatic AI attribution.
- **No unilateral commits**: agents do not create commits unless the
  user explicitly requests them.

For human-facing documents specifically (any document a human is
expected to read for review or reference -- README.md, PLAN.md,
journal entries, rebuttal drafts, ...), the conventions in the
[`human-facing-doc-authoring`](skills/human-facing-doc-authoring/SKILL.md)
skill apply: clear sectioning, two-tier structure, cross-references,
narrative prose over telegraphic fragments.

---

## Maintainer cadence

The maintainer (currently A. Attia) commits to:

- **Triaging issues within ~7 days** -- accept / decline / request more
  context.
- **A periodic roll-up review** of accumulated feedback (target:
  monthly, or once per major maintainer-project milestone).
- **Date-stamping every revision** to a skill or root convention so
  the change history is traceable in git.
- **Calling out breaking changes** explicitly in the affected file's
  date-stamp footer ("Revised 2026-MM-DD: BREAKING -- ...").

Forks are free to deviate. If you maintain a fork that has tracked
substantial divergent changes, please add an entry to
[`ATTRIBUTION.md`](ATTRIBUTION.md) (in your fork, not upstream)
explaining the divergence.

---

*Created 2026-05-13 by A. Attia. Maintained by A. Attia.*
