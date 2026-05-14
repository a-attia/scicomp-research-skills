# Self-Review Checklist for Human-Facing Docs

Loaded on demand from the `human-facing-doc-authoring` skill once a
draft or revision exists. Every item should be answerable yes / done;
if not, the doc needs another pass.

The checklist covers any human-facing doc -- README.md, PLAN.md,
survey notes, collection logs, section notes, rebuttal drafts, etc.
Items marked `[README]`, `[PLAN]`, `[NOTES]`, `[LOG]` are doc-type
specific; the rest are universal.

## A. Audience clarity (30-second decision)

1. Does the **first paragraph** state what this document IS in one
   sentence?
2. Does the **first paragraph** state who the doc is for (or what
   question it answers)?
3. `[README]` Is there an explicit **AI-agent redirect** ("agents go
   to AGENTS.md") near the top, set off as a callout?
4. Could a stranger landing here decide in 30 seconds whether to keep
   reading? If not, what's missing?

## B. Findability (look-up use case)

1. Does any document longer than ~100 lines have a **TOC** (Markdown
   link list)?
2. Do all top-level sections appear in the TOC with anchor links that
   actually resolve?
3. Are the section headings **descriptive** (a returning reader can
   guess from the TOC where to look)?
4. Are there **cross-references** between sections that mention each
   other?

## C. Two-tier readability (orient-quickly + look-up-later)

1. `[README]` Is there a **Quick Start** section in the first ~30% of
   the document?
2. `[PLAN]` Is the **Headline Contribution** (or equivalent
   one-paragraph summary of the project) at the top, BEFORE the
   detailed sections?
3. `[NOTES survey]` Does the survey note open with a **Headline
   claim** (one sentence) before the full Method section?
4. `[LOG]` Does the collection log open with a **Last updated** stamp,
   a **Scope** paragraph, and a **Deliverables produced** list before
   the per-entry tables?
5. Do top-section pointers cross-reference the deeper sections so the
   reader can choose their depth?

## D. Audience-correct content (the human/agent split)

1. Does the doc contain any text starting with "the agent should
   ..."? -> Move to `AGENTS.md`.
2. `[README]` Does the README list specific skills to load (with paths
   like `~/.scicomp-research-skills/skills/<name>/SKILL.md`)? -> Move
   to `AGENTS.md`. The README may *mention* what skills exist.
3. `[README]` Does the README contain plan-of-record content
   (timelines, M1/M2 milestones, open research questions)? -> Move to
   `PLAN.md`. The README may state current status in ONE line.
4. `[README]` Does the README contain per-paper survey notes or
   implementation plans? -> Move to `notes/`.
5. `[PLAN]` Does the PLAN contain agent directives ("the agent should
   ...")? -> Move to `AGENTS.md`.
6. `[NOTES]` Does the note contain content that belongs in PLAN.md
   (e.g. cross-cutting protocol decisions)? -> Move it.

## E. Tone and prose

1. Does each section open with **one sentence** stating what the
   section is about?
2. Are sentences **complete** (no telegraphic fragments like "Does
   four things")?
3. Are paragraphs **readable** (not run-on lists glued together with
   commas)?
4. Are tables used where they help (3+ parallel items)? Are they
   **avoided** where they hurt (1-2 items, sequential narrative)?
5. Is **one heading style** used throughout (ATX `##`, not Setext
   underlines)?
6. Is **one capitalisation style** used in headings (sentence case OR
   title case, consistently)?
7. Is **active voice** preferred? Is filler removed ("In order to",
   "It should be noted that")?

## F. Layout / structure

1. `[README]` Is the **repository layout** shown as a tree (Unicode
   box-drawing or ASCII), not a flat bullet list?
2. `[README]` Are tree entries **annotated** with one-line
   descriptions?
3. Are code blocks **language-tagged** (` ```bash ` not just ` ``` `)?
4. Are bash code blocks **short** (long ones broken into numbered
   steps with shorter blocks)?
5. Are equations rendered via **MathJax** (`$...$` / `$$...$$`) and
   not as ASCII art?

## G. Hygiene

1. Are there any **personal paths** leaked (`/Users/<name>/`,
   author-specific directory conventions)? Replace with placeholders.
2. Are there any **`<your-fork>` / `<TODO>` / `<INSERT>` placeholders**
   that should now be filled in (vs ones deliberately left for users
   to substitute)?
3. `[README]` Is the **licence pointer** present (link to `LICENSE`)?
4. `[README]` Is the **provenance / acknowledgements** section present
   where relevant (forks, derivative works)?
5. Do all **internal links** resolve (no broken anchors, no broken
   relative paths)?
6. Are external links **described** (so they make sense even if the
   target 404s)?
7. `[PLAN]`, `[LOG]`, `[NOTES]` Is the doc **date-stamped** (Created
   YYYY-MM-DD; Revised YYYY-MM-DD if applicable)?

## H. Cross-document consistency

1. `[README]` Does the README's description of the project agree with
   the one-liner in `AGENTS.md` Section "Project facts"?
2. `[README]` Does the README's status line (if any) agree with
   `PLAN.md`'s current state?
3. `[README]` Does the README's repository-layout tree match the
   actual current layout?
4. `[PLAN]` Are citekeys in the reading list consistent with
   `references/bibliography.bib`?
5. `[NOTES survey]` Does the survey note's citekey + bib metadata
   agree with `references/bibliography.bib`?
6. `[LOG]` Are the per-entry verification statuses consistent with
   the actual current state of `references/bibliography.bib` and
   `references/pdf/`?

## I. Doc-type specifics

1. `[NOTES survey]` Is the note ~30-50 lines (or up to ~100 for
   landmark papers)? Are all required sections present (headline,
   method, test cases, results, relevance, observations, action
   items)?
2. `[LOG]` Is the per-entry table **per-section** (matching the
   PLAN.md sections), not a single flat list?
3. `[LOG]` Are corrections **explicit** ("WAS X, NOW Y, source Z")
   rather than silently overwritten?
4. `[PLAN]` Does the PLAN end-stamp note any open `[VERIFY]` /
   `[INSERT]` placeholders that the next pass should resolve?
5. `[NOTES impl]` Does the impl note state trade-offs explicitly (not
   just the final design)?

## How to use this checklist

- Go through it linearly the first time.
- On subsequent revisions, focus on the sections most likely to have
  drifted (E, G, and H are the most fragile).
- If a check fails, fix it before any other work; small style
  inconsistencies compound.

---

*Created 2026-05-13 by A. Attia. Revised 2026-05-13: generalised from
README-only to all human-facing doc types.*
