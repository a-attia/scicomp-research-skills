---
name: New skill proposal
about: A pattern recurring across multiple sessions / projects deserves its own skill.
title: "[skill] <proposed-skill-name>: <one-line scope>"
labels: new-skill
---

## Proposed skill

Proposed name (must satisfy the OpenCode skill-name regex
`^[a-z0-9]+(-[a-z0-9]+)*$`):

- `<proposed-name>`

One-paragraph scope:

## Why this isn't covered by an existing skill

The four shipped skills today are:

- `research-paper-writing` -- paper drafting + adversarial review.
- `literature-survey` -- bib + PDF + survey-note workflow.
- `human-facing-doc-authoring` -- README/PLAN/notes/log conventions.
- `agent-resource-discipline` -- token / context / memory hygiene.

Explain why the proposed scope is genuinely separate from each.
Prefer extending an existing skill where possible -- new skills add
load on the agent's attention budget.

## Evidence the pattern recurs

The minimum bar for a NEW skill is **a pattern recurring across 3+
sessions and 2+ projects**. Less than that should usually be a new
rule or a new reference file under an existing skill.

For each session that motivates the proposed skill:

```text
Project: <project name or "private">
Date: YYYY-MM-DD
Task: <one-line description>
Pattern observed: <which aspect of the proposed scope showed up>
Outcome: <how it played out without the proposed skill>
```

If the evidence comes from `notes/agent_feedback.md` entries, paste
them here (sanitised).

## Sketched skill structure

What would the skill's `SKILL.md` look like? Sketch:

- **When to load it** -- triggering conditions.
- **Top-level sections** -- the spine.
- **References** -- which on-demand `references/*.md` files would
  exist (one per loadable topic).
- **Cross-references to existing skills** -- where this skill would
  be cited from / cite to.

A 50-line sketch is enough; the full draft can come later.

## Prior art (be honest)

Search publicly-available skill repos before proposing. Useful
catalogues: `anthropics/skills`, `VoltAgent/awesome-agent-skills`,
`ComposioHQ/awesome-claude-skills`, `addyosmani/agent-skills`,
`OthmanAdi/planning-with-files`, `thedotmack/claude-mem`. Cite
anything closely comparable so the proposal can position itself
honestly.

If the proposed skill duplicates publicly-available prior art with
nothing distinguishing, the answer is usually "load the upstream
skill instead of vendoring our own".

## Roll-up plan (optional)

If this becomes a skill, what existing rules from current skills
should move into it? What new rules emerge that aren't in any
current skill?
