# Example PLAN.md structures

Loaded on demand from the `human-facing-doc-authoring` skill when an
agent needs a starting-point skeleton for a project's `PLAN.md`. Each
skeleton is a TOC + a short note on what each section should contain.
Adapt freely.

`PLAN.md` is the **plan-of-record** -- the project's living contract.
It is read by both the human maintainer (the contract) and by the
agent (the source of truth for what the project IS). It must be
optimised for human readability while remaining authoritative.

---

## Universal PLAN.md conventions

These apply regardless of project type:

1. The **Headline Contribution** (or equivalent one-paragraph project
   summary) appears in the FIRST top-level section, before any
   detailed sections. A reader scanning only the first section should
   understand what the project is for.
2. **Every revision is date-stamped**. The footer carries
   `*Created YYYY-MM-DD. Revised YYYY-MM-DD (note about the revision).
   Maintained by <name>.*`.
3. **Status callouts** appear at the top: doc status (living /
   stable / archived), date last revised, who is responsible.
4. `[VERIFY]` / `[INSERT]` placeholders mark items that need
   confirmation before use. The agent should never silently remove
   these; only the user does, after verification.
5. Per-section trailing notes ("Action.") tell the reader what to do
   with the section's content (verify, draft, run experiment, ...).

The doc is **structurally agent-parseable** (clear section numbers +
tables) AND **narratively human-readable** (each section opens with
one sentence stating what it is about; tables are explained, not
dropped raw).

---

## A. Research-paper PLAN.md

For a paper workspace. Authoritative on: headline contribution, test
case, reading list, methods comparison matrix, experiment protocol,
implementation priorities, paper outline, timeline.

(See `~/.scicomp-research-skills/templates/paper-skeleton/PLAN.md` for
the canonical 11-section template; the skeleton below is a slightly
denser TOC view.)

```markdown
# Plan-of-Record: <Working Title>

**Working title**: *<full descriptive title>*

**Authors**: <list>. **Target venue class**: <e.g. JCP / SIAM J. Sci.
Comput.>. **Target submission**: <month year>. **Software**:
<upstream library URLs>. **Workspace**: `<paper-repo>/`.

> **Doc status**: Living plan-of-record. Date-stamp every revision.
> Items marked `[VERIFY]` need user confirmation.

---

## Headline Contribution
<One-paragraph claim. Positioning vs prior work. Mechanism of action.
Test case + hypothesis.>

## 1. Survey Reading List
<Subsections by topic; each lists citekeys with full citations.
Action: verify and produce survey notes via literature-survey skill.>

## 2. Test Case Specification
<Forward problem, observation model, belief, reward, horizon,
reference baselines.>

## 3. Algorithms / Methods Comparison Matrix
<Table: family | method | critic/return | action/decision space |
status (ready / NEW S/M/L / config-only).>

## 4. Experiment Protocol
<Seeds, metrics (primary/secondary/diagnostic), hyperparameters,
statistical tests, compute budget.>

## 5. Implementation Components: Existing vs New
<5.1 inherited; 5.2 new components needed.>

## 6. Implementation Priority Order
<Numbered list of components in build order, with rationale.>

## 7. Paper Outline
<Section list including appendices.>

## 8. Figure List
<Numbered list of target figures with one-line descriptions.>

## 9. Timeline
<Table: month | milestone. Includes risk + buffer paragraph.>

## 10. Tracking and Cadence
<Where each artefact lives: this PLAN, per-component impl notes,
per-section notes, experiments dir, figures dir, drafts dir,
references dir.>

## 11. Open Questions
<Numbered list of deferred questions, tracked so they don't get lost.>

---

*Created YYYY-MM-DD. Maintained by <name>.*
```

Notes:

- The Headline Contribution is the **only** part that should be
  duplicated (in summary form) into `README.md`. Everything else lives
  here authoritatively.
- Sections 4-7 may grow large; consider hoisting Section 4 into its
  own `experiments/PROTOCOL.md` if it exceeds ~3 pages.
- The reading list (Section 1) names citekeys that match
  `references/bibliography.bib`; the per-paper survey notes live at
  `notes/survey_<citekey>.md` and are NOT duplicated here.

---

## B. Research-software PLAN.md

For a research-software library. Authoritative on: scope + non-scope,
public API surface, milestones, roadmap, design decisions log.

```markdown
# Plan-of-Record: <library name>

**Library name**: `<name>`. **Scope**: <one paragraph>.
**Audience**: <who uses this>.
**Status**: <pre-alpha / alpha / beta / 1.x>. **Repo**: <URL>.

> **Doc status**: Living plan-of-record. Date-stamp every revision.

---

## Headline goal
<What this library makes possible that wasn't possible before. One
paragraph.>

## Scope and non-scope
<Bullet list of "in scope" and "out of scope" with rationale for the
boundary.>

## 1. Public API surface (target)
<Top-level functions + classes the library will expose at 1.0. Table
or annotated list.>

## 2. Architecture
<High-level component diagram (ASCII tree or block diagram in
markdown image). Description of each component's responsibility.>

## 3. Milestones
| Milestone | Status | Goal |
|:----------|:-------|:-----|
| M1 -- bootstrap + CI | <done / in-progress / pending> | <description> |
| M2 -- core API       | <...>                          | <description> |
| M3 -- first user     | <...>                          | <description> |
| ...                  |                                |               |

## 4. Design decisions log
<Numbered list of significant design decisions, each with: context,
decision, alternatives considered, consequences. Append-only.>

## 5. Open questions
<Numbered list of deferred design questions.>

## 6. Tracking and cadence
<Where each artefact lives: this PLAN, ADRs (if separate), CHANGELOG,
issue tracker, ...>

---

*Created YYYY-MM-DD. Maintained by <name>.*
```

Notes:

- Section 4 (Design decisions log) is the software equivalent of a
  paper's "Action items" / "Corrections to apply" buffers. Append
  entries; never delete. If a decision is later reversed, ADD a new
  entry that supersedes the old (don't edit the old in place).
- Milestones (Section 3) are coarser than commits. Each milestone is
  shippable.

---

## C. Standalone-experiment PLAN.md

For an exploratory experiment workspace that may or may not become a
paper. Authoritative on: hypothesis, success criterion, experimental
design, results.

```markdown
# Plan-of-Record: <experiment name>

**Hypothesis**: <one sentence>. **Success criterion**: <one sentence
that says what result would settle the question>.
**Status**: <designing / running / analysing / done>. **Owner**:
<name>.

---

## Background
<2-3 paragraphs: what motivates this experiment, what we already know
from prior work / preliminary runs, what's missing.>

## Experimental design
<What will be varied, what will be fixed, what will be measured. Be
specific about ranges + replicates.>

## Pre-registered predictions
<For each comparison, what outcome would CONFIRM and what outcome
would FALSIFY the hypothesis. Date-stamped before running.>

## Results
<Filled in as runs complete. Each result section: (a) what was run,
(b) what was found, (c) does this confirm or falsify the prediction?>

## Decisions
<What we will do as a consequence of the results (write up, abandon,
follow-up experiment, ...). Date-stamped.>

---

*Created YYYY-MM-DD. Maintained by <name>.*
```

Notes:

- The pre-registered predictions section is critical and should be
  date-stamped BEFORE running, to prevent post-hoc rationalisation.
- A "negative-result" experiment is a complete experiment; the
  Decisions section says "abandon, document the negative result, do
  not pursue". This is valuable.

---

## Common adaptations

- **Multi-author projects** add a "Roles" subsection naming who owns
  which sections.
- **Long-running projects** (multi-year) split the timeline into
  per-year sub-tables.
- **Projects with strong external dependencies** add a "Pinned
  upstream versions" section at the top with rationale per pin.
- **Projects with submission deadlines** add a "Critical path" callout
  near the top listing the dependency chain that must complete on
  time.

---

*Created 2026-05-13 by A. Attia.*
