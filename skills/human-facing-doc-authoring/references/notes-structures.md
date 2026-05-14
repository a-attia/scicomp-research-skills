# Example notes/ structures

Loaded on demand from the `human-facing-doc-authoring` skill when an
agent needs starting-point skeletons for working notes that live under
`notes/`. The three flavours covered here are:

- `notes/survey_<citekey>.md` -- per-paper survey notes (the
  literature-survey skill is the primary author).
- `notes/section_<N>.md` -- per-paper-section research notes.
- `notes/impl_<component>.md` -- per-component implementation plans.

All three are **human-facing working documents**. They are read by the
user when drafting paper sections, when re-orienting after time away,
and (sometimes) by reviewers / co-authors.

---

## A. Survey notes (`notes/survey_<citekey>.md`)

Authoritative skeleton + worked example: see
`~/.scicomp-research-skills/skills/literature-survey/references/survey-note-template.md`.

Quick summary of the required structure (8 sections):

1. **Header** -- citekey, full citation, PDF path.
2. **Headline claim** -- one sentence stating the central
   contribution.
3. **Method (full detail)** -- ~10-20 lines including key equations
   in MathJax.
4. **Test cases (with parameters)** -- datasets / dimensionalities /
   horizons.
5. **Headline numerical results** -- specific table / figure
   references; tables for structured comparisons.
6. **Relevance to our paper** -- which sections cite this paper, why,
   what we differ on.
7. **Critical observations** -- non-obvious findings from deep read,
   not in the abstract.
8. **Action items for our paper** -- concrete + verifiable.

Length: ~30-50 lines for typical notes; up to ~100 for landmark
papers.

Style rules specific to survey notes:

- **Equations in MathJax** (`$...$` inline, `$$...$$` display); never
  ASCII-art math.
- **Date-stamp** every note (`Created YYYY-MM-DD by <name>.`).
- **Action items must be concrete + verifiable**; vague items ("think
  about how this affects us") are forbidden.
- Cite specific tables / figures from the source paper so future-you
  can re-find the result quickly.

---

## B. Per-section research notes (`notes/section_<N>.md`)

Working notes for a specific paper section. Aggregates: the relevant
survey-note action items, experiment results that bear on the section,
figure references, draft outline.

```markdown
# Section <N> notes -- <section title>

**Status**: <outlining / drafting / revising / done>.
**Last updated**: YYYY-MM-DD.
**Linked PLAN.md sections**: <e.g. PLAN.md Section 2 + Section 5.2>.

## Goal of this section
<One sentence: what role does this section play in the paper's
argument? What does the reader know after reading it?>

## Outline (target)
<Bulleted outline of the section's paragraphs / subsections, with
one-line role descriptions.>

## Source material
<What this section draws on:>

- Survey notes: `survey_<citekey1>.md`, `survey_<citekey2>.md`, ...
- Experiments: `experiments/<run-id>/` ...
- Figures: `figures/<file>.pdf` ...
- PLAN.md sections: <list>

## Action items pulled from survey notes
<For each cited survey note, restate the action items (from that
note's "Action items" section) that bear on THIS paper section.>

1. From `survey_<citekey>.md`: <action item>.
2. ...

## Open questions for this section
<Things to resolve before this section can be finalised.>

1. <question> -- depends on <result / decision>.

## Draft sketch
<Optional: paragraph-level sketch of the section in prose, before
actual drafting begins. Not a substitute for `drafts/main.tex`; this
is the planning scratchpad.>

---

*Created YYYY-MM-DD by <name>.*
```

Notes:

- The section note is the **bridge** between survey notes
  (per-reference) and the actual draft (per-section). Use it to
  aggregate before drafting; use it to track loose ends after
  drafting.
- When the section is finalised in the actual draft, mark this note's
  Status as "done" but DO NOT delete it -- it remains the audit trail
  for "where did Section 4 paragraph 3's claim come from?".

---

## C. Per-component implementation plans (`notes/impl_<component>.md`)

Design doc for a planned new code component. Written **before** any
code is committed for that component.

```markdown
# Implementation plan -- <component name>

**Status**: <designing / building / shipped>.
**Owner**: <name>. **Last updated**: YYYY-MM-DD.
**Target repo**: <URL or path>.
**Linked PLAN.md sections**: <e.g. PLAN.md Section 5.2 item 3>.

## Purpose
<One sentence: what problem does this component solve?>

## Public API surface
<The functions / classes / CLI flags this component will expose.
Type signatures included.>

## Dependencies
<Which existing code this builds on (upstream library + version).>

## Design
<Sketch of the implementation. Critical algorithms in pseudo-code.
Data structures. Concurrency / IO model if non-trivial.>

## Trade-offs considered
<For each major design decision: alternatives considered, why we
chose what we chose, what we'd revisit.>

## Testing plan
<What tests will gate "shipped" status. Unit tests, integration
tests, regression tests. Performance budget if applicable.>

## Risks
<What could go wrong. What we will do if it does.>

## Action items
<Numbered list of concrete tasks with current status.>

1. <task> -- <pending / in-progress / done> -- <owner>.

---

*Created YYYY-MM-DD by <name>.*
```

Notes:

- The Trade-offs section is the most valuable part for future
  collaborators; do not skip it even when the design feels obvious in
  the moment.
- "Action items" mirrors the survey-note convention: concrete,
  verifiable, ownership-stated.
- When the component is shipped, mark Status = shipped, but keep the
  doc as the design record (link to actual code via
  `path/to/file:line_number`).

---

## Common adaptations

- **Notes that grow large** (a survey note that needs ~150 lines for a
  multi-method landmark paper, an impl note for a 10-file component):
  break the structure into clearly-marked subsections, but keep the
  top-level skeleton intact for skim-readability.
- **Notes for code reviews** (reviewer-response style): add a
  "Reviewer response" subsection to the impl note with reviewer
  comment + author response pairs, dated.
- **Notes that supersede earlier notes** (e.g. design changed): do
  NOT delete the old note. ADD a "Superseded by `impl_<component2>.md`"
  banner at the top, with one-line summary of why.

---

*Created 2026-05-13 by A. Attia.*
