---
name: Reviewer comment follow-up
about: A reviewer raised a concern that needs a response in the rebuttal +
       (possibly) a code / experiment / figure change.
title: "[reviewer] R<N>.<M>: <one-line summary>"
labels: rebuttal
---

## Reviewer + concern

- **Reviewer**: R<N> (reviewer number from the editor's letter).
- **Concern ID**: R<N>.<M> (sequential per reviewer; matches the
  `rebuttal_<round>/_log.md` audit table per
  `~/.scicomp-research-skills/skills/human-facing-doc-authoring/references/audit-log-structures.md`
  section D).
- **Reviewer rating**: <e.g. weak accept / borderline / weak reject>.

## The concern (verbatim)

> <Quote the reviewer's exact wording. Do NOT paraphrase -- the rebuttal
> response will need the exact text to address it precisely.>

## Our interpretation

<One paragraph: what we think the reviewer is asking. If ambiguous,
list the alternative interpretations and which one we'll address.>

## Response status

- [ ] **Addressed in revision** (text + experiments + figures changed).
- [ ] **In progress** (response drafted; experiment running).
- [ ] **Deferred** (will note in rebuttal + offer to address in a
      follow-up paper).
- [ ] **Disputed** (we believe the reviewer is mistaken; rebuttal
      will make the case).

## What this triggers

Tick whichever apply:

- [ ] Text-only change to `drafts/main.tex` Section <X>.
- [ ] New experiment in `experiments/<run-id>/`. Specify run-id + what
      it should test.
- [ ] Re-run of existing experiment (different seed / parameter /
      hardware). Specify which run-id + what to vary.
- [ ] New figure or update to existing figure in `figures/<section>/`.
- [ ] Bibliography addition (cite a paper the reviewer mentioned).
      Use the `literature-survey` skill workflow.
- [ ] Discussion-section addition acknowledging a limitation.

## Response location

- `rebuttal_<round>/response.md` Section R<N>.<M>.
- (optional) Diff in the paper at <line range>.

## Originating context

If this was raised in a `notes/agent_feedback.md` entry or in a
specific session, paste the relevant context here.
