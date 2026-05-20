---
name: human-facing-doc-authoring
description: Author or revise any project document whose primary audience is a HUMAN -- README.md, PLAN.md, per-paper survey notes (notes/survey_*.md), bibliography collection logs (references/_collection_log.md), reviewer-response drafts, per-section research notes (notes/section_*.md), per-component implementation plans (notes/impl_*.md). Apply the human/agent audience split (these docs are NOT downstream renderings of AGENTS.md), the two-tier readability structure (orient-quickly + look-up-later), proper sectioning + cross-references, narrative prose over telegraphic fragments, and tables/trees/code-blocks where they aid scanning. Use whenever the agent will produce text that a human collaborator (the user or a co-author or a reviewer) is expected to read for review or reference.
license: MIT
metadata:
  audience: research-project authors and contributors
  domain: scientific-computing
  origin: A. Attia (added 2026-05-13; renamed from project-readme-authoring 2026-05-13 to generalise scope)
---

# Human-Facing Doc Authoring

## When to load this skill

Load this skill whenever the agent is about to produce or substantially
revise a document whose primary audience is a **human** -- not the
agent itself, not a downstream tool. In this ecosystem that includes
(non-exhaustive list):

- `README.md` -- top-level human-facing entry point for any project.
- `PLAN.md` -- plan-of-record / contract; both humans and agents read.
- `notes/survey_<citekey>.md` -- per-paper survey notes; the user reads
  these when drafting paper sections and when re-orienting after time
  away.
- `references/_collection_log.md` -- bibliography verification audit
  trail; the user (and reviewers) read this.
- `notes/section_<N>.md` -- per-paper-section research notes; the user
  reads them while drafting the section.
- `notes/impl_<component>.md` -- per-component implementation plans;
  the user reads them before greenlighting code.
- Reviewer responses / rebuttals.
- Acknowledgement / contribution / changelog files.

**Always load this skill before** generating any of the above. Other
skills (`literature-survey`, `research-paper-writing`) cross-reference
this one for the structural + stylistic conventions they share.

Do NOT load this skill for:

- editing `AGENTS.md` files -- those have the *opposite* audience
  (agents). They should be telegraphic and structured, not narrative.
- editing source code or code docstrings -- those have their own
  conventions (governed by the project's coding style).
- editing per-skill `SKILL.md` files -- those are agent-facing.

## Core principle: human/agent audience split

Every project in this ecosystem keeps two parallel entry-point
documents with explicitly different audiences:

| File         | Audience            | Tone                                         |
|:-------------|:--------------------|:---------------------------------------------|
| `AGENTS.md`  | AI coding agents    | Telegraphic, structured, machine-parseable.  |
| `README.md`  | Human collaborators | Narrative, indexed, designed to be SCANNED.  |

The same split generalises to every other document the agent produces:

| Document type                       | Primary audience      | Tone                                   |
|:------------------------------------|:----------------------|:---------------------------------------|
| `README.md`                         | New + returning humans | Narrative, two-tier, scannable.       |
| `PLAN.md`                           | Maintainer + co-authors | Structured prose; sectioned; living. |
| `notes/survey_<citekey>.md`         | Paper authors           | Compact prose + equations + tables.  |
| `references/_collection_log.md`     | Maintainer + reviewers  | Audit-trail tables; date-stamped.    |
| `notes/section_<N>.md`              | Paper authors           | Working notes; section-flavoured.    |
| `notes/impl_<component>.md`         | Code authors            | Design doc; trade-offs explicit.     |
| Reviewer-response / rebuttal        | Editors + reviewers     | Direct; concession-and-concession-counter style. |

**Critical**: do NOT treat any of these as downstream renderings of
`AGENTS.md`. They have different jobs. `AGENTS.md` tells an agent what
to do; the documents above let a human read what the project IS, what
the plan IS, what is known, what is decided.

A well-written human-facing doc should:

- let a new human collaborator decide in **30 seconds** whether the
  doc (or the project) is relevant to them;
- get a motivated reader the answer they came for in **3-5 minutes**;
- contain enough depth that a returning collaborator can **answer
  their own question** without paging the maintainer.

## Universal conventions (apply to ALL human-facing docs)

These rules apply regardless of doc type. Per-doc-type structure goes
in the `references/<doc-type>-structures.md` files loaded on demand.

### A. Orientation up front

- The **first paragraph** answers "what is this document?" in one
  sentence + 2-3 sentences of context.
- Documents longer than ~100 lines have a **TOC** (Markdown link list)
  with anchor-linked entries.
- Documents that primarily exist as audit trails or living records
  carry a **status / last-updated stamp** near the top.

### B. Two-tier structure where appropriate

For docs read by both impatient and thorough readers (`README.md`,
`PLAN.md`, longer survey notes), use a **Quick Start** / **Headline**
section near the top with the 30-second version, then deeper sections
for the 5-minute reader. Cross-reference between the two so the reader
can choose their depth.

For shorter docs (a single survey note, a single section note), the
two-tier rule reduces to: open with a one-sentence headline, then
expand.

### C. Heading discipline

- **ATX headings only** (`#`, `##`, `###`). No Setext-style underlines.
- **Cap depth at `###`**. If you need `####`, the section needs to be
  split.
- **One `#` per document** (the title). Top-level sections are `##`.
- Pick **one capitalisation style** (sentence case OR title case) and
  apply consistently within a doc.

### D. Cross-references

- Every claim that is supported elsewhere should **link to the
  supporting location** by anchor (within the doc) or relative path
  (to another file in the same repo).
- Every "see X" should be a clickable link.
- Use **relative links** to other files in the same repo
  (`[`PLAN.md`](PLAN.md)`), not absolute URLs.
- For external references that may rot (papers, blog posts), include
  the link AND a one-line description so the link's role is obvious
  even if it 404s.
- Cite code with `path/to/file:line_number` so the reader can navigate
  directly.

### E. Tables vs prose vs annotated lists

Prefer **tables** when:

- there are 3+ items each described by 2-3 attributes;
- the items are parallel (same shape);
- a reader wants to look up a specific item rather than read
  top-to-bottom.

Prefer **prose** when:

- the items are sequential (numbered steps, narrative flow);
- the explanation between items matters as much as the items
  themselves;
- there are fewer than 3 items.

Prefer **annotated bullet lists** (one item per line, with `--` or `:`
explaining each) when items are short labels with one-line definitions.

### F. ASCII trees for layout

For repository or directory layouts, use a Unicode-box-drawing tree
with brief inline annotations:

```text
project-name/
├── AGENTS.md             entry point for AI agents
├── README.md             you are here
└── src/                  source code
```

Avoid plain `--`-bulleted lists for layout; the tree shape conveys
nesting visually and is far easier to scan.

### G. Code blocks

- Tag every code block with a language (`bash`, `python`, `text`, ...).
- Keep bash blocks short -- if a block has more than ~5 commands, it
  probably wants surrounding numbered-step prose with shorter blocks
  inside each step.
- Use `<...>` placeholders for values the reader must substitute.
  Comment what to substitute on the line above when not obvious.

### H. Math notation

- Use **LaTeX inside Markdown via MathJax** (`$...$` inline,
  `$$...$$` display) for any equation or symbol.
- Avoid ASCII-art math (e.g. `x^2 + y^2`); it is harder to scan and
  harder to copy.

### I. Tone and prose

- Each section opens with **one sentence** stating what the section is
  about.
- Sentences are **complete** (no telegraphic fragments like "Does four
  things").
- Paragraphs are **readable** (not run-on lists glued together with
  commas).
- Prefer **active voice**; minimise "we" in single-author docs.
- Avoid filler ("In order to ..."  -> "To ...";  "It should be noted
  that ..."  -> delete).

### J. Hygiene

- **No personal paths** (`/Users/<name>/`, author-specific directory
  conventions). Use generic placeholders (`<projects-parent-dir>/...`)
  so the doc is publishable without per-author scrubbing.
- **No `<TODO>` / `<INSERT>` / `<your-fork>` placeholders** that should
  have been filled in (vs ones deliberately left for users to
  substitute).
- **Date-stamp** every plan-of-record-style doc (`*Created YYYY-MM-DD.
  Revised YYYY-MM-DD (note). Maintained by <name>.*`).

### K. Self-invalidation of cited facts

Human-facing docs accumulate **cited facts** -- file counts ("the
skill ships 4 references"), line counts ("AGENTS.md is ~680
lines"), enumerations ("the three deferred items are X, Y, Z"),
status labels ("F-03..F-08 -- shipped 2026-05-17"), commit SHAs,
test counts, citation counts. These facts WILL drift as the
underlying state changes; the doc that cites them becomes silently
wrong.

The discipline:

1. **Avoid citing facts that will drift, when a cross-reference
   suffices.** Instead of "the skill ships 4 references", prefer
   "see the workflow table in `SKILL.md`" -- the table is the
   single source of truth, and the reader who cares about the
   exact count reads the table.
2. **When a drifting fact MUST be cited inline** (because the
   number itself is load-bearing for the argument: "we covered all
   12 rules", "the budget was exceeded by 2.3x"), tag the fact with
   a **self-invalidation marker** -- a parenthetical date-stamp +
   source pointer:
   ```markdown
   ... ships 4 references (as of 2026-05-17;
   see [`SKILL.md`](SKILL.md) workflow table for current count).
   ```
   The marker tells future readers (and future agents auditing the
   doc) "this number may have drifted; check the source."
3. **When updating a doc, audit cited facts.** Before committing a
   doc edit, scan for inline numbers / counts / enumerations / SHAs
   in the doc and verify each against its current source.
   `STATUS.md`, `CHANGELOG.md`, README.md "Current status" sections,
   and per-skill SKILL.md footers are the most-frequent drift
   sites.
4. **Status labels carry their own date.** "Shipped" / "planned" /
   "deferred" / "blocked" labels must include the date the label
   was last verified, not just the date the label was added.
   "F-17 -- planned (as of 2026-05-17)" is correct; "F-17 --
   planned" alone will be silently wrong by 2026-06.

This rule was motivated by Session A's STATUS.md / CHANGELOG.md
maintenance burden: every commit shifts counts that other docs
cite, and without explicit self-invalidation markers the drift
accumulates invisibly between sessions.

## What goes where (audience-routing rules)

When authoring or auditing a human-facing doc, ask of each piece of
content: **"who needs this and when?"** Use the table to decide
placement.

| Content                                                      | Goes in                              | Rationale                                                                    |
|:-------------------------------------------------------------|:-------------------------------------|:-----------------------------------------------------------------------------|
| Project name, one-line description, scope                    | `README.md`                          | First thing a human visiting the repo sees.                                  |
| "Where do AI agents start?" pointer                          | `README.md`                          | One callout block near the top.                                              |
| Quick start / install / first-use commands                   | `README.md`                          | Humans need this; agents follow `AGENTS.md` instead.                         |
| Repository layout (annotated tree)                           | `README.md`                          | Helps humans orient.                                                         |
| Glossary / definitions / domain context                      | `README.md` (or `docs/glossary.md`)  | Humans need; agents get domain facts from per-project `AGENTS.md`.           |
| Contribution / extension instructions                        | `README.md`                          | Humans need; cross-reference `AGENTS.md` for skill-/template-author rules.   |
| Provenance, licence, acknowledgements                        | `README.md`                          | Humans + standard repo hygiene.                                              |
| List of which skills the agent should load                   | `AGENTS.md`                          | Agent-only directive.                                                        |
| Per-project facts (target venue, citation style, ...)        | `AGENTS.md`                          | Agent-only; humans read these in `PLAN.md` if needed.                        |
| Plan-of-record / roadmap / experiment protocol               | `PLAN.md`                            | The contract; both humans and agents read.                                   |
| Headline contribution + positioning                          | `PLAN.md` (full); `README.md` (2-3 sentences) | Single source of truth in PLAN.md; README summarises + links.       |
| Per-paper survey notes                                       | `notes/survey_<citekey>.md`          | One per reference; not user-facing index material.                           |
| Bibliography verification audit trail                        | `references/_collection_log.md`      | Per-pass status + corrections.                                               |
| Per-section research notes (working drafts of paper sections) | `notes/section_<N>.md`              | Working docs.                                                                |
| Per-component implementation plans                           | `notes/impl_<component>.md`          | Working docs.                                                                |

## Per-doc-type structure (loaded on demand)

The structural skeletons + worked examples for each doc type live in
`references/`:

- `references/readme-structures.md` -- README.md skeletons for paper /
  software / skills-repo / rebuttal projects.
- `references/plan-structures.md` -- PLAN.md skeletons for paper /
  software / experiment projects.
- `references/notes-structures.md` -- skeletons for `survey_*.md`,
  `section_*.md`, `impl_*.md`.
- `references/audit-log-structures.md` -- skeleton for
  `_collection_log.md` (bibliography) and other audit trails.

Load only the file relevant to the current edit target.

## Authoring workflow

When asked to author or rewrite a human-facing doc:

1. **Identify the audience(s)**. Most docs serve at least three:
   first-time visitor, motivated new collaborator, returning
   collaborator. Section structure should serve all three
   simultaneously.
2. **Identify the doc type** and load the matching
   `references/<doc-type>-structures.md` for the skeleton.
3. **Draft the TOC first**. The headings ARE the document's spine; if
   the TOC reads coherently, the document will too.
4. **Write the lead paragraph** -- one sentence stating what this doc
   IS, then 2-3 sentences of context.
5. **Write the orient-quickly section** (Quick Start, headline,
   summary -- whatever the doc type's skeleton specifies).
6. **Write the deep sections in TOC order**, each opening with one
   sentence stating what the section is about.
7. **Add cross-reference links** in a final pass.
8. **Self-review** against `references/self-review-checklist.md`.
9. **Move misplaced content** to its rightful home (`AGENTS.md`,
   `PLAN.md`, `notes/`, code docstrings) -- listing each move in the
   response so the user can confirm.

## Rewriting an existing substantial doc

The authoring workflow above assumes a new doc. **Rewriting an
existing substantial doc (a README, a PLAN.md, a long survey note,
a paper section in `drafts/`) is a distinct workflow with a higher
risk of silent content loss**. The argo-anywhere onboarding session
(2026-05-14) surfaced this -- the agent rewrote a substantial
README during migration, and although nothing was lost, there was
no discipline forcing the agent to PROVE nothing was lost. This
section codifies the missing discipline.

The pattern is adapted from the
[`project-onboarding`](../project-onboarding/references/scenario-2-existing-agentic-files.md)
skill's Scenario 2.C content-check table -- which solves the same
problem for migrating an existing `CLAUDE.md` to a per-project
`AGENTS.md`. The pattern generalises to ANY substantial doc
rewrite.

### When to apply

Apply this workflow when the rewrite target is:

- An existing doc >100 lines that the user wrote (or that previous
  agentic sessions co-authored under user direction).
- A doc with project-specific facts the user has accumulated over
  time + may not remember they captured.
- A doc that other documents cross-reference (a section in PLAN.md
  cited by experiments/<run-id>/README.md, a `notes/section_*.md`
  cited by drafts/main.tex).

Do NOT apply for: small docs (<50 lines, easy to eyeball); freshly-
templated docs that haven't been customised; auto-generated docs
(API reference, changelogs).

### The 5-step procedure

1. **Inventory the existing doc** (read-only). Output: a mental or
   written enumeration of every distinct piece of content -- not just
   sections, but every project-fact, every decision-rationale, every
   cross-reference, every example. For very long docs, write this to
   a temporary `notes/_rewrite-inventory_<doc>_<date>.md` so the
   user can review.
2. **Identify destinations**. For each inventory item, decide:
   - **Keep in this doc** (preserve in the rewrite).
   - **Move to another doc** (the item belongs elsewhere; cite where).
   - **Drop with reason** (item is obsolete / redundant / subsumed
     elsewhere; cite which / what).
3. **Produce a content-check table** before any writes. Format:

   ```markdown
   | Item | Original location | New destination | Status |
   |:---|:---|:---|:---|
   | Project codename rationale | README.md L52-56 | new README.md "Background" section | preserved |
   | Old deployment instructions | README.md L120-180 | drops (deployment moved to docs/deploy.md) | dropped, reason: relocated |
   | Personal-anecdote paragraph | README.md L201-215 | drops | dropped, reason: not appropriate for README |
   | ... | ... | ... | ... |
   ```

   Total inventory items in the original = total rows in the table.
   Every line in the original has a row OR is explicitly dropped
   with reason. **NO silent omission.**
4. **Present the content-check table to the user**. The user
   reviews + approves OR adjusts (especially the "Drop with reason"
   rows). Only then proceed to writes.
5. **Execute the rewrite**. After writing the new doc:
   - Diff the inventory against the new doc to confirm every
     "preserve" item is actually present.
   - Report any "Move to another doc" actions that you executed
     (so the user can confirm the cross-references still resolve).
   - Leave the temporary `notes/_rewrite-inventory_<doc>_<date>.md`
     in the working tree for one commit cycle (the user may want to
     consult it post-rewrite); then delete in a follow-up commit.

### Why this matters

The "rewrote a README + nothing was obviously lost" case is the
silent failure mode. Without the content-check table, neither the
agent nor the user can prove the negative ("we didn't lose
anything"). The table makes the proof explicit + reviewable +
auditable.

### Cross-references

- This pattern is borrowed from `project-onboarding/references/scenario-2-existing-agentic-files.md`
  (Scenario 2.C "agent-file with substantive project content") --
  which solves the same problem for the specific case of migrating
  an existing agent-file to AGENTS.md. The general-purpose
  doc-rewrite version is here.
- For rewrites that involve substantive structural change (not just
  reorganisation), additionally consult `references/<doc-type>-structures.md`
  for the target structure.

## Output contract

When the user asks the agent to produce a human-facing doc:

1. Confirm the doc type + audience(s) + primary use cases.
2. Load the relevant `references/<doc-type>-structures.md`.
3. Draft or revise the TOC.
4. Apply the universal conventions above + the per-doc-type structure.
5. Run the self-review checklist from
   `references/self-review-checklist.md`.
6. Report what was changed, what content was moved between files (if
   any), and what (if anything) was deliberately left alone.

## Interactions with other skills

- The `literature-survey` skill produces `notes/survey_<citekey>.md`
  and `references/_collection_log.md`. Both are human-facing; that
  skill's output should follow this skill's conventions.
  `literature-survey` cross-references this skill explicitly.
- The `research-paper-writing` skill produces draft paper sections.
  The drafts themselves are governed by paper-writing conventions
  (paragraph clarity, claim-evidence alignment); but any *meta-docs*
  it produces (a section-level research note, a paper README, a
  rebuttal draft) are human-facing and follow this skill.

## See also

- `references/readme-structures.md` -- README.md skeletons.
- `references/plan-structures.md` -- PLAN.md skeletons.
- `references/notes-structures.md` -- skeletons for `notes/*.md`
  (survey, section, impl).
- `references/audit-log-structures.md` -- skeleton for collection logs
  and other audit trails.
- `references/self-review-checklist.md` -- self-review checklist for a
  freshly-authored or revised human-facing doc.
- The `research-paper-writing` skill -- different audience (paper
  readers, not project visitors), but the paragraph-clarity check and
  claim-evidence alignment principles transfer well.

---

*Created 2026-05-13 by A. Attia (initially as `project-readme-authoring`).
Revised 2026-05-13: renamed to `human-facing-doc-authoring` and
generalised scope to cover all human-facing project documents (PLAN.md,
survey notes, collection logs, rebuttal drafts, ...) -- the
human/agent audience split is universal, not README-specific.*
