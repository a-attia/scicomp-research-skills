# Collection-log template + worked example

This file is loaded on demand from the `literature-survey` skill when an
agent needs the precise structure of `references/_collection_log.md` for
a paper. The collection log is the audit trail for your reference
corpus -- when a reviewer asks "how do you know this citation is right?"
or when you discover a mis-attribution months later, the log is what you
check.

---

## Template

```markdown
# Bibliography Collection Log

**Last updated**: YYYY-MM-DD (descriptor of latest pass).
**Maintainer**: <Your name>.

## Scope of this collection

A short paragraph describing which sections of the paper's plan-of-record
this log covers, and what is intentionally out of scope (deferred to
later passes).

## Deliverables produced

A bulleted list of artefacts produced by this collection effort:

- `references/bibliography.bib` -- N BibTeX entries (verified by user).
- `references/pdf/<citekey>.pdf` -- N main PDFs + M supplementary PDFs.
- `references/pdf/.txt/<citekey>.txt` -- text-extracted versions
  (gitignored cache for AI tooling) produced via `pdftotext -layout`.
- `notes/survey_<citekey>.md` -- N expanded per-paper survey notes.
- This log (`references/_collection_log.md`).

## Per-entry status

One table per section of the paper. For each citekey:

| Citekey                 | Status                  | Notes                                                                   |
|:------------------------|:------------------------|:------------------------------------------------------------------------|
| `<citekey>`             | <verified / arXiv-only / placeholder> | <one-line description; flag any corrections> |

## Corrections to apply (deferred -- batch them)

A list of corrections discovered during this pass that have not yet been
applied to the paper's plan-of-record (PLAN.md or equivalent). Batch
these into a single revision when the user is ready.

1. Section X.Y: <correction>.
2. Section A.B: <correction>.

## Things newly understood (from PDF deep-dive)

Insights NOT in earlier abstract-only survey notes, now captured in the
expanded notes. Useful as a "what would I have missed?" record.

1. <Finding 1>.
2. <Finding 2>.

## Items not found / left for user

Things this pass could not resolve and are left for the user to provide
or for a follow-up pass:

1. <Item 1 with context>.

## Suggested user additions

References that were expected but not provided, with rationale for why
each might be worth adding.

## Collection methodology note

A short paragraph describing how this collection was done (e.g. "All
14 main PDFs converted to layout-preserving text via pdftotext -layout
into references/pdf/.txt/. Text files read in full to expand each survey
note from ~10-15 lines to ~30-100 lines covering: claim, full method
with key equations in MathJax, test cases + parameters, headline numerical
results, citation context, critical observations, and action items.").

## Recommended next steps

A short ordered list of what the user should do next:

1. <Action 1>.
2. <Action 2>.
```

## Worked example excerpt

Below is an excerpt of a real collection log following this template.
Many sub-sections abbreviated for the example.

```markdown
# Bibliography Collection Log

**Last updated**: 2026-05-11 (post-PDF deep-dive pass).
**Maintainer**: A. Attia.

## Scope of this collection

Sections 1.2 + 1.3 + 1.4 of `PLAN.md` -- the RL-flavoured references.
Out of scope: Section 1.1 (OED foundations), 1.5 (PDE-OED), 1.6
(SciRL/PyOED prior art).

## Deliverables produced

- `references/bibliography.bib` -- 14 BibTeX entries (verified by user).
- `references/pdf/<citekey>.pdf` -- 14 main PDFs + 3 supplementary PDFs.
- ...

## Per-entry status

### Section 1.2 -- Sequential / amortized OED with NN + RL

| Citekey                    | Status                  | Notes                                                                                              |
|:---------------------------|:------------------------|:---------------------------------------------------------------------------------------------------|
| `foster2021dad`            | VERIFIED + read in full | ICML 2021. Headline DAD paper. sPCE bound formula extracted.                                       |
| `shen2023sOED`             | VERIFIED + read in full | CMAME 2023. Closest existing work. Same AD source-inversion problem.                               |
| ...                        |                         |                                                                                                    |

## Corrections to apply (deferred)

When PLAN.md Section 1 is next revised, apply these corrections:

1. Section 1.3 `duan2021dsac`: authors are Duan et al. (NOT Ma et al.);
   6 authors including Qi Sun; published IEEE TNNLS 2022.
2. Section 1.4 `tamar2015cvarsampling`: arXiv ID is 1404.3862 (NOT
   1502.05790).

## Things newly understood (from PDF deep-dive)

1. Blau22's history-likelihood vector C_t (Eq. 13-14) enables Markovian
   state without storing full history. Should adopt in our environment.
2. Closed-form CVaR over Gaussian critic: mu - sigma * phi(Phi^-1(alpha))
   / alpha. CVaR variants downgrade from `NEW(S)` to `config-only`.

## Recommended next steps

1. Update PLAN.md Section 1 with the corrections above (single commit).
2. Review the 14 expanded notes -- primary deliverable of this round.
3. Decide whether to add Section 1.5 (PDE-OED) references in the next
   round.
```

---

## Notes on style

- Update the log every time you do a verification pass. Don't batch many
  passes worth of changes into one log update -- the audit trail
  granularity is the point.
- Date-stamp every entry's verification date so future you knows how
  stale the verification is.
- Be explicit about corrections: "WAS X, NOW Y, source: Z (DOI 10.1234/...)".
- The "Corrections to apply" section is intentionally deferred -- it
  feeds the next plan-of-record revision rather than triggering an
  immediate edit. This batches plan-of-record revisions into a small
  number of well-scoped commits.

---

*Created 2026-05-13 by A. Attia.*
