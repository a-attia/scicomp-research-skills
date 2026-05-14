---
name: Skill improvement (from real-project experience)
about: A skill rule was insufficient or unclear; you have evidence from a real session.
title: "[improve] <skill name>: <one-line description>"
labels: enhancement
---

## Which skill

Skill (and reference file, if applicable):

- `skills/<name>/SKILL.md` (or `skills/<name>/references/<file>.md`)

Section / rule that needs improvement:

## What was insufficient

<One-paragraph description. Examples:>

- A rule was unclear and the agent applied it incorrectly.
- A rule was correct but the situation it covers had a sub-case the
  rule didn't address.
- A rationalization the agent invented isn't in the skill's
  rebuttals table.
- The skill's threshold (e.g. "files >300 lines") was wrong for
  this situation.
- The skill needs an example or a clarifying note.

## Evidence from real sessions

The minimum bar is **one concrete session** where the current rule
was insufficient. **Two or more is much stronger**.

For each session, give:

```text
Project: <project name or "private">
Date: YYYY-MM-DD
What the agent was doing: <one-line task description>
What rule fired (or should have): <skill section + rule>
What went wrong: <1-3 sentences>
Quoted output (if relevant):
    <agent message OR command output OR file content>
```

If the evidence comes from `notes/agent_feedback.md` entries in the
project, paste them here (sanitised of project-specific details).

## Proposed change

Be specific. Vague "the agent should be smarter about X" is harder
to act on than concrete "add the following rule to
`skills/<name>/SKILL.md` Section <Y>: ..."

If you have a draft of the new rule text, include it (or open a PR
referencing this issue).

## Why this generalises

One short paragraph: would another project hit the same situation?
Is this specific to a domain we cover (papers, software libraries,
literature surveys), or specific to one project's quirks?

## Originating journal entries (optional)

Direct copy of the relevant `notes/agent_feedback.md` entries, with
project-specific details sanitised.
