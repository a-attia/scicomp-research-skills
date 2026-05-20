---
name: Append evidence to existing skill proposal
about: Add a new session/project data point to an open new-skill-proposal issue.
title: "[evidence] #<issue-number>: <project> <date>"
labels: evidence
---

## Target proposal

Issue this evidence belongs to:

- Closes-towards: #<issue-number> (the open `new-skill` proposal)

The evidence-threshold for a NEW skill is **a pattern recurring
across 3+ sessions and 2+ projects** (see `new-skill-proposal.md`).
This template is for accumulating evidence across multiple sessions
toward that threshold WITHOUT having to re-open the proposal each
time.

## Evidence entry

```text
Project: <project name or "private">
Date: YYYY-MM-DD
Task: <one-line description>
Pattern observed: <which aspect of the proposed scope showed up>
Outcome: <how it played out without the proposed skill>
Source: <link to notes/agent_feedback.md entry OR paste sanitised
         excerpt below>
```

### Sanitised excerpt (if not linkable)

```text
<paste the relevant notes/agent_feedback.md entry, with any
project-specific or personal-identifying content scrubbed>
```

## Updated evidence count

After appending this entry, the proposal's evidence stands at:

- Sessions: <N> (was <N-1>)
- Projects: <M> (was <M or M-1>)
- Threshold reached? <yes / no>

If **yes**, the proposal is ready for the "Sketched skill
structure" section to be filled out + the skill drafted. Mention
that explicitly in the comment on the target proposal issue.

If **no**, leave the proposal open; future evidence-append issues
will continue accumulating.

## Cross-reference back to proposal

Add a one-line comment on issue #<issue-number> linking to this
evidence-append issue, so the proposal's discussion thread stays
synchronised.
