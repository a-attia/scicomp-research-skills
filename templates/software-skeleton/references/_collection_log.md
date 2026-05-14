# Algorithmic-source Collection Log

**Last updated**: YYYY-MM-DD (initial setup; no entries yet).
**Maintainer**: <name>.

---

## Scope of this log

This log tracks **algorithmic-source citations** -- papers or
references cited in code comments as the source of an algorithm,
formula, hyperparameter choice, or implementation pattern in this
library. The discipline is the same as the
[`literature-survey`](https://github.com/a-attia/scicomp-research-skills/blob/main/skills/literature-survey/SKILL.md)
skill's collection-log discipline (which targets papers cited in a
manuscript's bibliography), adapted for software:

- For a **paper** project: `references/_collection_log.md` lists the
  papers cited in the manuscript's bibliography.
- For a **software** project (this one): the same kind of log lists
  the papers cited in code comments as algorithm sources.

The two disciplines are interchangeable; the difference is just where
the citation appears (manuscript text vs code comment).

## Why this matters

When future-you (or a collaborator, or a reviewer) reads a code
comment that says "this implements Algorithm 3.1 from Smith et al.
2023", they need to be able to **find that paper**, **verify that
the implementation matches**, and **see what alternatives were
considered**. The `_collection_log.md` is the audit trail; the
`references/bibliography.bib` (if used) holds the canonical bib
entries; the `notes/survey_<citekey>.md` files (if used) hold the
per-paper deep-read summaries.

## Deliverables produced

(List artefacts as they are added to support the cited algorithms.)

- `references/bibliography.bib` -- BibTeX entries for cited papers
  (track in git; verify each via the `literature-survey` skill).
- `references/pdf/<citekey>.pdf` -- PDFs of cited papers (gitignored
  per `.gitignore`; copyright varies; PDFs live locally only).
- `references/pdf/.txt/<citekey>.txt` -- text extractions for AI
  consumption (gitignored regenerable cache; produced via
  `pdftotext -layout`).
- `notes/survey_<citekey>.md` -- per-paper survey notes (created via
  the `literature-survey` skill).
- This log (`references/_collection_log.md`).

## Per-entry status

One row per cited paper. Update on every verification pass.

### Algorithms in `src/<library>/core/`

| Citekey                 | Status                          | Code path                      | Notes                                                                              |
|:------------------------|:--------------------------------|:-------------------------------|:-----------------------------------------------------------------------------------|
| `<smith2023algorithm>`  | <verified / arXiv-only / placeholder> | `src/<lib>/core/<file>.py:NN` | Algorithm 3.1; we adopt it with <modification X> for <reason>.                     |
| `<jones2024solver>`     | <...>                           | `src/<lib>/core/<file>.py:NN`  | Eq. 17 used as default solver.                                                     |

### Algorithms in `src/<library>/solvers/`

| Citekey                 | Status                          | Code path                      | Notes                                                                              |
|:------------------------|:--------------------------------|:-------------------------------|:-----------------------------------------------------------------------------------|
| <add as needed>         |                                 |                                |                                                                                    |

(Add per-component subsections as the library grows.)

## Corrections to apply (deferred)

A list of corrections discovered during deep-reads or implementation
work that have not yet been applied to the library. Batch into a
single revision when the user is ready.

1. <e.g. "Section 3.1 of `smith2023algorithm` actually uses sign
   convention X, not Y as we assumed; the code in
   `src/<lib>/core/<file>.py:NN` may need a sign flip; verify
   against MMS test in tests/integration/test_<X>.py">.
2. <...>

## Things newly understood (from deep-dive)

Insights NOT in earlier abstract-only summaries, now captured in the
survey notes. Useful as a "what would I have missed?" record.

1. <...>

## Items not found / left for user

Things this pass could not resolve.

1. <e.g. "Reference paper for the preconditioner used in
   src/<lib>/solvers/<file>.py is not yet identified; ask <author>
   if their thesis covers it">.

## Suggested user additions

References that were expected but not provided, with rationale.

1. <e.g. "Smith & Jones 2024 (cond-mat) covers the same
   discretisation we use; cite for the convergence proof">.

## Collection methodology note

(Short paragraph: how the collection was done. E.g. "All 5 algorithm-
source PDFs converted to layout-preserving text via `pdftotext
-layout` into `references/pdf/.txt/`. Each survey note expanded from
~10 lines (abstract-only) to ~30-50 lines covering: the algorithm
in full detail with key equations in MathJax, the test cases the
paper ran on, headline numerical results, our implementation choices
that follow from the paper, and any deviations from the paper's
recipe.")

## Recommended next steps

(Ordered list of what to do next; keep small + actionable.)

1. <Action 1>.
2. <Action 2>.

---

*Created YYYY-MM-DD by <your name> from
[`scicomp-research-skills/templates/software-skeleton/references/_collection_log.md`](https://github.com/a-attia/scicomp-research-skills/tree/main/templates/software-skeleton/references/_collection_log.md).*
