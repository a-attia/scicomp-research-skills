# Paper Workspace: <Paper Title>

This is the working directory for the journal paper

> *<Full paper title>*

(authors: <author list>; target submission <month year>; venue class:
<journal candidates>).

This workspace is intentionally separated from any code dependencies
(SciRL, PyOED, or other libraries) so paper revisions don't pollute the
codebase history. Code dependencies are referenced by their git commit
hashes in experiment metadata (see `experiments/`).

## Contents

```
<paper-repo>/
  AGENTS.md          -- entry point for AI agents (read this first)
  PLAN.md            -- plan-of-record (the contract; read this second)
  README.md          -- you are here
  ATTRIBUTION.md     -- (optional) acknowledgements / lineage
  LICENSE            -- MIT or as appropriate

  .gitignore         -- excludes PDFs, .txt extractions, experiment artifacts, LaTeX build files

  references/
    bibliography.bib    -- BibTeX (tracked); every entry verified
    _collection_log.md  -- per-paper verification status + corrections + notes
    pdf/                -- published-manuscript PDFs (gitignored)
      <citekey>.pdf
      <citekey>-supp.pdf
      .txt/             -- pdftotext -layout extractions (gitignored cache for AI)

  notes/
    README.md           -- index of survey notes (by section, by affinity)
    survey_<citekey>.md -- per-paper survey notes (~30-50 lines each)
    impl_<component>.md -- per-component implementation plans (one per new code component)
    section_<N>.md      -- per-paper-section research notes (one per draft section)

  experiments/         -- run scripts + per-run results (seed-by-seed JSON + plots)
                          Layout: experiments/$date_$algo_$variant/
  figures/             -- final figures consumed by drafts/
  drafts/              -- LaTeX / Markdown draft sources (build artifacts gitignored)
```

## How to use

1. **Read AGENTS.md first** if you are an AI agent (it points at the
   shared scicomp-research-skills conventions + this paper's specifics).
2. **Read PLAN.md end-to-end** if you are a human collaborator. It is
   the project contract.
3. **Survey notes** in `notes/survey_*.md` are the per-paper summaries;
   read the relevant ones before drafting any paper section that cites
   them.
4. **Reference workflow** for adding a new citation: see the
   `literature-survey` skill in the shared scicomp-research-skills
   repository (`~/.scicomp-research-skills/skills/literature-survey/SKILL.md`).
5. **Experiment results** follow `experiments/$date_$algo_$variant/`
   with seed-by-seed JSON + plot scripts. Each run records the upstream
   library git commit hashes for reproducibility.

## Pinned upstream versions (for reproducibility)

If this paper depends on specific external libraries:

- **<library 1>**: <repo URL>, pinned to commit `<hash>` (release tag
  `<tag>` if applicable).
- **<library 2>**: <repo URL>, pinned to commit `<hash>`.

For experiment reproducibility, record `git rev-parse HEAD` of each
upstream library into the run's metadata JSON.

## Status

- **Plan-of-record**: stable / drafting / revising; revisions tracked in
  PLAN.md trailing date-stamp footer.
- **Bibliography**: <N>/<target> entries verified.
- **Experiments**: <none / N runs / completed>.
- **Drafts**: <not started / Section X / full draft>.

---

*This skeleton was generated from
[scicomp-research-skills/templates/paper-skeleton/](https://github.com/a-attia/scicomp-research-skills/tree/main/templates/paper-skeleton).*
