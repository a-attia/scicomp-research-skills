# Example audit-log structures

Loaded on demand from the `human-facing-doc-authoring` skill when an
agent needs starting-point skeletons for audit-trail documents that
record verification status, corrections, or decision history. The
flagship example is `references/_collection_log.md` for a paper's
bibliography; the structure generalises.

Audit logs are **append-mostly**: entries are added as work proceeds,
corrections are made by ADDING new entries that supersede old ones (not
by silently overwriting). The audit value comes from the log's
trustworthiness as a historical record.

---

## Universal audit-log conventions

These apply regardless of audit-log type:

1. **Top-of-doc stamp**: `**Last updated**: YYYY-MM-DD (descriptor of
   latest pass). **Maintainer**: <name>.`
2. **Scope paragraph**: what this log covers AND what is intentionally
   out of scope.
3. **Deliverables list**: the artefacts produced as part of the work
   the log records.
4. **Per-entry tables**, one per logical group (per paper section, per
   release, per code component).
5. **Corrections section**: explicit "WAS X, NOW Y, source Z" entries
   for every correction. Never silent.
6. **Methodology note**: short paragraph describing how the work was
   done, so future-you can audit the audit.
7. **Recommended next steps**: ordered list of what to do next.

The log is **structurally machine-parseable** (tables, consistent
column headers) AND **narratively human-readable** (each section opens
with a sentence stating what it is about; tables are explained; date
context is preserved).

---

## A. Bibliography collection log (`references/_collection_log.md`)

Authoritative skeleton + worked example: see
`~/.scicomp-research-skills/skills/literature-survey/references/collection-log-template.md`.

Quick summary of the required structure:

```markdown
# Bibliography Collection Log

**Last updated**: YYYY-MM-DD (descriptor of latest pass).
**Maintainer**: <name>.

## Scope of this collection
<Paragraph: which PLAN.md sections this log covers; what is out of
scope (deferred to later passes).>

## Deliverables produced
<Bullet list: bibliography.bib entries, PDFs, .txt extractions,
survey notes, this log.>

## Per-entry status

### Section 1.X -- <topic>

| Citekey      | Status                          | Notes                           |
|:-------------|:--------------------------------|:--------------------------------|
| `<citekey>`  | verified / arXiv-only / placeholder | <one-line description; flag corrections> |

### Section 1.Y -- <topic>

| Citekey      | Status                          | Notes                           |
|:-------------|:--------------------------------|:--------------------------------|

## Corrections to apply (deferred)
<Numbered list of corrections discovered during this pass that have
not yet been applied to PLAN.md. Batch into the next plan-of-record
revision.>

## Things newly understood (from PDF deep-dive)
<Insights NOT in earlier abstract-only survey notes. The "what would
I have missed?" record.>

## Items not found / left for user
<Things this pass could not resolve.>

## Suggested user additions
<References that were expected but not provided.>

## Collection methodology note
<Short paragraph: how the collection was done, to enable future audit
of the audit.>

## Recommended next steps
<Ordered list of what to do next.>
```

Notes:

- The per-entry tables are **per-PLAN.md-section**, not a single flat
  list. This makes the log easy to read alongside the plan.
- "Corrections to apply" is intentionally **deferred** -- it feeds the
  next plan-of-record revision rather than triggering an immediate
  edit. This batches PLAN.md revisions into well-scoped commits.

---

## B. Decision log / ADR (`docs/adr/_log.md` or `notes/decisions.md`)

For software projects: a numbered, append-only log of significant
architectural / design decisions. Each entry has its own subsection.

```markdown
# Decision Log

**Last updated**: YYYY-MM-DD.
**Maintainer**: <name>.

## Scope
<What kinds of decisions are recorded here. Typically: anything that
affects the public API, the build system, the dependency graph, or
the data model. Trivial coding decisions are NOT in scope.>

## How to add an entry
<One-paragraph protocol: number sequentially, never reorder, never
delete; if a decision is reversed, ADD a new entry that supersedes.>

---

## D-001 -- <one-line title> (YYYY-MM-DD)

**Status**: accepted / superseded by D-NNN.

### Context
<What problem prompted this decision. 2-3 sentences.>

### Decision
<What we chose. Be specific.>

### Alternatives considered
<Numbered list: alternative + why it was rejected.>

### Consequences
<What this commits us to. What it makes harder. What it makes easier.>

---

## D-002 -- ... (YYYY-MM-DD)

...
```

Notes:

- Append-only: never delete D-NNN. If a decision is reversed, add
  D-MMM with `Status: supersedes D-NNN` and edit D-NNN's status to
  `superseded by D-MMM`. That single forward-pointer edit is the only
  modification ever made to a past entry.
- The Consequences section is the most important for future readers.
  Spend time on it.

---

## C. Release / change log (`CHANGELOG.md`)

For published software. Conventional format -- see
[keepachangelog.com](https://keepachangelog.com/) for the full
specification. Summary skeleton:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- <new functionality>

### Changed
- <changes in existing functionality>

### Deprecated
- <soon-to-be-removed functionality>

### Removed
- <removed functionality>

### Fixed
- <bug fixes>

### Security
- <vulnerability addresses>

## [1.2.0] -- YYYY-MM-DD

### Added
- ...

## [1.1.0] -- YYYY-MM-DD

...
```

Notes:

- Categorise every entry into one of the six standard sections.
- Date-stamp every released version; do not date-stamp [Unreleased].
- Link version headings to the GitHub diff for that release.

---

## D. Reviewer-response audit (`rebuttal_<round>/_log.md`)

Tracks per-reviewer-comment status during rebuttal preparation.

```markdown
# Rebuttal audit -- <paper>, round <N>

**Last updated**: YYYY-MM-DD.
**Maintainer**: <name>.
**Submission deadline**: YYYY-MM-DD.

## Per-reviewer status

### Reviewer 1 (rating: <score>)

| Concern ID | Concern (short) | Status | Response location |
|:-----------|:----------------|:-------|:------------------|
| R1.1       | <one-line>      | <addressed / in-progress / deferred / disputed> | response.md Section X |

### Reviewer 2 (rating: <score>)

...

## Cross-cutting concerns
<Concerns raised by multiple reviewers; respond once and reference.>

## Method changes triggered by rebuttal
<List of changes to the actual paper / experiments triggered by
reviewer comments. Each linked to commit + diff.>

## Open items
<Concerns not yet addressed; what blocks them.>

---

*Created YYYY-MM-DD by <name>.*
```

Notes:

- "Disputed" status is legitimate. Use it (sparingly) for concerns
  the authors believe are mistaken. The response in `response.md`
  should make the case; the audit log just records the disposition.
- "Cross-cutting concerns" is the rebuttal-specific equivalent of
  the bibliography log's "Things newly understood" -- it captures
  emergent themes that were not visible from any single comment.

---

## Common adaptations

- **Audit logs that span multiple passes** (bibliography that grows
  over months): add a `## Pass history` section near the top with one
  row per pass (date, scope, additions, corrections).
- **Audit logs with sub-team ownership**: add an "Owner" column to
  each per-entry table.
- **Logs that get long** (>500 lines): split per major section into
  separate files (`references/_collection_log_section1.md`,
  `_collection_log_section2.md`) and have a top-level `_collection_log.md`
  index.

---

*Created 2026-05-13 by A. Attia.*
