---
name: research-slides-authoring
description: "Use when creating, revising or auditing a research talk or poster: conference and seminar talks, lab meetings, defenses, invited talks, funder or status briefings, posters. Applies to any toolchain (Beamer, Marp, PowerPoint, Keynote, reveal.js). Covers content and verification, not file mechanics: discovery of audience and venue, a slide plan before drafting, assertion-evidence slides (the title states the finding, the body proves it), audience-matched math and code, whole-deck consistency and fact currency, visual design rules, and a render-and-look audit after every visual edit, with a page-render script. Load it EVEN IF THE USER ONLY SAYS 'fix this slide' or 'make the figure fit'. For .pptx file mechanics, also load a pptx skill."
license: MIT
metadata:
  audience: any agent producing a talk deck or poster in this ecosystem
  domain: research-communication
  origin: "A. Attia (added 2026-10-14, from issue #3 and per-project journals)"
---

# Research slides authoring

## When to load this skill

Load before creating, revising or reviewing anything that will be
**presented** rather than read at a desk: a talk deck, a poster, a
status or funder briefing, a defense, a lab-meeting update. Load it
for small requests too ("fix this slide", "make the figure fit",
"add a slide about X"). The failures this skill prevents happen most
often on small edits, because a small edit feels too small to check.

It is toolchain-agnostic. Every audit rule is stated against the
**rendered PDF**, which every toolchain produces. Toolchain specifics
live in `references/toolchain-beamer.md` and
`references/toolchain-marp.md`.

**This is not a file-format skill.** A pptx skill handles reading and
writing `.pptx` files. This skill decides what goes on the slides and
checks that it arrived. For a PowerPoint deck, load both.

## The governing test

> **Could someone who has not read the project, glancing up from their
> phone, restate this slide's point?**

A deck is not a project directory with page breaks. Every rule below
serves this test.

## The four principles

1. **Argue, don't file.** A deck makes a claim and builds evidence for
   it. The order of the work plan is not an argument.
2. **Write for someone who is not you.** The audience has not read the
   repository, does not share its vocabulary, and was not in the room
   when decisions were made.
3. **Form carries meaning.** Colour, size, position, grouping and
   repetition each say something. Use them on purpose, consistently.
4. **Look, don't assume.** A clean build proves the source compiled.
   It says nothing about whether the slide is right. Render it and look.

## Workflow and gates

| Phase | Output | Gate |
|:---|:---|:---|
| 1. Discovery | Answers to one batch of questions | Nothing asked that could have been read |
| 2. Brief | `notes/talk_brief.md`, one screen | **User approves** |
| 3. Plan | `notes/talk_plan.md`: claim, beats, one line per slide | **User approves** |
| 4. Draft | The deck | Build succeeds |
| 5. Audit | Rendered pages checked | **After every visual edit**, not once at the end |
| 6. Distribute | PDF delivered, location stated | Privacy pass if shared publicly |

For a one-slide edit, phases 1 to 3 shrink to reading the deck's
existing plan. Phase 5 never shrinks.

## Rules by phase

Each rule has one line here and full treatment in a reference file.
Load the reference for the phase you are in, not all of them.

### Discovery and brief: `references/discovery-and-brief.md`

- **D1 Read before asking.** Read the project, the material the talk
  presents, and any per-project `AGENTS.md` "Audience composition"
  field. Never ask what you can read or measure.
- **D2 Ask once, in one batch:** toolchain and template, audience mix,
  venue and time slot, title, abstract, URLs to show, and whether the
  PDF will be distributed.
- **D3 The audience sets the density** of math, code and jargon. With
  a mixed audience, both directions of jargon are jargon.
- **D4 The abstract or headline claim is the contract.** Every planned
  slide supports it. Reconcile the deck with the abstract, or propose
  one.

### Structure: `references/deck-structure.md`

- **S1 Plan before drafting.** A slide plan, one line per slide (claim
  plus visual idiom), approved by the user. Structure is not
  recoverable by editing slides.
- **S2 The titles, read alone in order, make the argument.** If they
  are noun phrases with no verbs, the deck is documentation.
- **S3 Each slide opens on something the previous one established.**
- **S4 Required slots:** a title slide with date and version; contents
  and section dividers when there are 8 or more slides; acknowledgements
  (including AI assistance); a specific call to action; backup material
  at the end.
- **S5 Several artefacts make parallel tracks**, joined at the start
  and the end, unless one really depends on another.
- **S6 A recurring spine figure** is one source with highlight
  variants, so one fix reaches every copy.
- **S7 Budget about one slide per minute.**

### Composition: `references/slide-composition.md`

- **C1 Assertion-evidence.** The title is a full-sentence finding. The
  body is mostly a visual that supports it.
- **C2 One point per slide.** Split a slide that makes two.
- **C3 Three or more discrete items become a list, diagram or table**,
  never a chain of commas.
- **C4 The slide carries the bones; the speaker carries the sentences.**
  A bullet of 20 or more words is speaker text.
- **C5 Code: only the one line the audience will type.**
- **C6 Math: one display equation per claim.** Every symbol is defined
  at or before first use, one symbol means one thing for the whole
  deck, and every equation is compiled.
- **C7 Spell out abbreviations where they first appear.** No slide
  sends the reader to a file.
- **C8 A number points at its source** or is labelled as a target.
- **C9 URLs:** vital ones get a QR code, the text URL and a caption;
  private ones are removed; all are clickable in a distributed PDF.
- **C10 Reconcile new material against the whole deck**, not just the
  slide that asked for it. Re-verify cited facts at every build,
  including facts your own session may have made stale.
- **C11 A figure must not contradict its caption, title or geometry.**

### Visual design: `references/visual-design.md`

- **V1 Consistency.** Polish one figure, polish all. Style each element
  type once (theme, preamble, macros), never per slide.
- **V2 One colour per role**, a legend when colour encodes state, and a
  conclusion colour distinct from context.
- **V3 Hierarchy carries meaning.** Named subjects look different from
  generic groupings.
- **V4 Restrained depth:** one elevation level, or none.
- **V5 Titles fit on one line**, confirmed in the render.
- **V6 Run the diagram-failure checklist:** arrows through text, labels
  on lines, cramped or stranded boxes, connectors too short to read.
- **V7 Accessibility:** contrast, a colour-blind-safe palette, no more
  than about six elements per slide.
- **V8 Figures are generated by committed scripts** and referenced by
  name, never embedded as bytes in the deck source.

### Render and audit: `references/render-audit.md`

- **A1 A clean build is not done.** After every visual edit: build,
  render the changed pages, look at each as if for the first time,
  fix, then report. Use `scripts/audit-pages.sh`.
- **A2 Size renders in pixels, not DPI:** about 1000 to 1100 px on the
  long edge for review. Crop and magnify for edges and labels. A
  thumbnail grid checks content, never boundaries.
- **A3 Boundary check:** edges, footer clearance, code and table
  overflow, hyphenation in narrow boxes.
- **A4 Count what must survive.** Every heading in the source must
  appear in the PDF text (`audit-pages.sh -e`). An overfull slide or a
  flowed poster column can drop a block silently.
- **A5 Sweep the deck rule by rule**, not slide by slide. Check arrows
  against text in a separate pass after layout.
- **A6 Distrust your checker before your deck.** Calibrate a new tool on
  a known-good input. When a check and a reader disagree, magnify
  before retuning.

### Distribution

- **X1 Ship the PDF and say where it is**, with the command that opens
  it. Keep a PDF fallback for any live-rendered format.
- **X2 Never overwrite without being asked.** Archive earlier versions.
- **X3 A visible version stamp** on the title slide.
- **X4 Before sharing publicly**, apply root `AGENTS.md` Section 6.7:
  no private URLs or QR codes, no machine-local paths or claims, no
  unreleased results unless the user says so.

Posters follow the same rules with different geometry and reading
distance: see `references/posters.md` (provisional).

## Common rationalizations

| Thought | Rebuttal |
|:---|:---|
| "The build is clean, so it's done." | The most repeated failure in the evidence. Render the changed pages and look. |
| "The thumbnail grid looks fine." | A grid compresses a 2 mm clip to under a pixel. Grids check content, not edges. |
| "I only changed one slide." | One partial fix once left 28 defects across a deck. Reconcile, then render the changed pages. |
| "Trim prose until it fits." | Fitting is a structure problem first. Split the slide or move detail to the speaker. |
| "The checker passed." | It passed the checks it has. Look anyway, and calibrate the checker on a known-good slide. |
| "The audience will read the bullets." | They will read or listen, not both. Move sentences to the speaker. |
| "Same numbers as last time." | Cited facts drift, including ones your own session changed. Re-verify at build time. |

## Done checklist

Before reporting a deck as finished: `references/self-review-checklist.md`
(one check per rule above). At minimum: the brief and plan were
approved; every changed page was rendered and viewed; all expected
headings survived (`audit-pages.sh -e`); the titles read as an argument;
the PDF location was reported.

## Interactions with other skills

- `human-facing-doc-authoring`: section I prose habits apply to slide
  text, rule K (self-invalidating facts) generalises C10, and rule L
  generalises whole-deck reconciliation. Cite them; do not restate.
- `research-paper-writing`: `research-paper-writing/references/abstract.md`
  for D4, and `research-paper-writing/references/paper-review.md` for an
  adversarial pass over the finished deck.
- `agent-resource-discipline`:
  `agent-resource-discipline/references/pdf-lifecycle.md` (text
  extraction order is not visual order) and
  `agent-resource-discipline/references/public-surface-hygiene.md` (X4).
- A pptx skill, for `.pptx` file mechanics.

## Prior art

- K. M. Naegle, "Ten simple rules for effective presentation slides",
  *PLoS Computational Biology* 17(12): e1009554 (2021).
- M. Alley and J. Garner, the assertion-evidence approach
  (assertion-evidence.com).
- Anthropic's `pptx` skill: rendered visual QA with fresh eyes.
- `Noi1r/beamer-skill` (MIT): a gated Beamer workflow with density
  caps and the observation that Beamer hides overflow inside blocks.

---

*Created 2026-10-14 by A. Attia. Consolidated from the slide-authoring
proposal (issue #3, with evidence appends #4 and #5) and per-project
journals: about 30 sessions across four projects in two independent
lineages (Beamer and Marp), which converged on the same core rules.
All four projects are the maintainer's own; external evidence is still
needed. Maintained by A. Attia.*
