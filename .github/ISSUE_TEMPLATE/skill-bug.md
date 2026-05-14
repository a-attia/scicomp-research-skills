---
name: Skill bug
about: Something in a skill is wrong or contradictory.
title: "[bug] <skill name>: <one-line description>"
labels: bug
---

## Which skill

Skill name (and reference file, if applicable):

- `skills/<name>/SKILL.md` (or `skills/<name>/references/<file>.md`)

Section within the skill (heading or line range):

## What is wrong

<One-paragraph description. Be specific.>

Examples of what counts as a bug:

- A cross-reference that doesn't resolve (broken anchor or missing
  file).
- Two rules within the same skill that contradict each other.
- A rule that cites prior art incorrectly (wrong author, wrong URL,
  wrong year).
- A rule that no longer applies because tooling has changed.
- A statement that is empirically false (e.g. "this command exits
  non-zero" when it doesn't).

## Evidence

If the bug is:

- **A broken link / cross-reference**: paste the link as it appears
  in the skill + the actual error or 404 you observed.
- **A contradictory rule**: quote both rules with their locations.
- **An incorrect citation**: quote the citation + the corrected
  source.
- **An empirically false statement**: paste the minimal command +
  output that disproves it.

## Suggested fix (optional)

<If you have a specific change in mind, describe it.>

## Originating context (optional)

If this bug surfaced from a `notes/agent_feedback.md` entry in a
real project, paste the entry here (sanitised of project-specific
details).
