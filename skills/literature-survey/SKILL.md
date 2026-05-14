---
name: literature-survey
description: Build and maintain a verified literature-survey corpus for a research paper -- BibTeX entries, published-manuscript PDFs, text extractions for AI consumption, per-paper survey notes (~30-50 lines each), and a collection log tracking verification status and corrections. Use when starting a new paper that needs a substantial literature review, when adding new references to an existing paper, or when migrating an unverified bib file to a verified one.
license: MIT
metadata:
  audience: research-paper authors
  domain: scientific-computing
  origin: A. Attia (added 2026-05-13)
---

# Literature Survey

## When to load this skill

Load this skill when the user is:

- starting a new research paper that needs a literature review
- adding new references to an existing paper
- migrating an unverified BibTeX file to a verified one
- doing a deep-read pass on a set of references and producing per-paper
  notes
- needing a reproducible record of which references have been verified
  vs which are still placeholders

## Overview

A research paper's bibliography drives credibility. Stale, mis-attributed,
or unverified entries embarrass the author at submission time. This skill
defines a **5-step workflow** for building a verified literature corpus
and a deliverables structure that future-you (or a collaborator) can
audit and extend.

The five steps:

1. Add a verified BibTeX entry to `references/bibliography.bib`.
2. Drop the published-manuscript PDF into `references/pdf/<citekey>.pdf`.
3. Generate a text extraction for AI consumption.
4. Write a survey note `notes/survey_<citekey>.md`.
5. Append a row to `references/_collection_log.md`.

Each step is described in detail below, plus the directory layout, the
survey-note template, and the collection-log template.

## Directory layout

```
<paper-repo>/
  references/
    bibliography.bib          -- BibTeX (tracked); every entry verified
    _collection_log.md        -- per-paper verification status + corrections + notes
    pdf/                      -- published-manuscript PDFs (gitignored)
      <citekey>.pdf
      <citekey>-supp.pdf      -- supplementary material where applicable
      .txt/                   -- pdftotext -layout extractions (gitignored)
        <citekey>.txt
  notes/
    survey_<citekey>.md       -- per-paper survey note (~30-50 lines)
    README.md                 -- index of survey notes (by section, by affinity)
```

The `references/pdf/` directory and its `.txt/` cache should be gitignored;
the bibtex + collection log + survey notes are tracked.

## Step 1: Verified BibTeX entry

Add the entry to `references/bibliography.bib`. **Required fields**: must
include venue + page numbers + DOI or arXiv ID. Reject placeholder
entries (e.g. "Author, A. (year). *Title*. Some Venue. `[VERIFY]`"); these
go in a separate "pending" section of the bib file or are tagged with
`note = {pending verification}`.

Verification criteria for an entry to be considered "verified":

- author list matches the published manuscript (not arXiv preprint if the
  two differ)
- year is the published year (not arXiv submission year), unless the
  entry is genuinely arXiv-only
- venue + volume + issue + pages all match the published version
- DOI or arXiv ID is correct (verify by webfetch of the publisher page or
  the arXiv abstract page)
- citekey follows project convention (typically `lastname + year +
  short-tag`, e.g. `foster2021dad`)

When a verified entry corrects an earlier unverified entry, document the
correction in the collection log (Step 5). Do NOT silently overwrite.

## Step 2: PDF acquisition

Drop the published-manuscript PDF into `references/pdf/<citekey>.pdf`,
where `<citekey>` matches the BibTeX citekey **exactly**. Supplementary
material goes as `<citekey>-supp.pdf`.

The PDFs are gitignored (they're typically large; copyright varies; not
appropriate for tracked content). The `references/pdf/` directory itself
should also be gitignored (or the directory tracked but the `*.pdf` glob
ignored, depending on your project's convention -- see the `.gitignore`
template in `templates/paper-skeleton/`).

If the published PDF is paywalled and only an arXiv preprint is
available, use the preprint and explicitly document this in the
collection log so a future reader knows to upgrade when access becomes
available.

## Step 3: Text extraction

Most AI agents cannot consume PDF binaries directly. Generate a
layout-preserving text extraction once, then read it whenever a deep dive
is needed:

```bash
mkdir -p references/pdf/.txt
pdftotext -layout references/pdf/<citekey>.pdf references/pdf/.txt/<citekey>.txt
```

`pdftotext` ships with `poppler-utils` (Linux: `apt install poppler-utils`;
macOS: `brew install poppler`). The `-layout` flag preserves the
two-column structure of typical academic papers, which makes the output
much more readable than the default flow-mode extraction.

For supplementary material, repeat with `<citekey>-supp.pdf` ->
`.txt/<citekey>-supp.txt`.

The `.txt/` directory is gitignored; it is a regenerable cache.

Batch conversion of all PDFs in one go:

```bash
mkdir -p references/pdf/.txt
for pdf in references/pdf/*.pdf; do
  base=$(basename "$pdf" .pdf)
  pdftotext -layout "$pdf" "references/pdf/.txt/${base}.txt"
done
```

## Step 4: Per-paper survey note

Read the `.txt` extraction, then write `notes/survey_<citekey>.md` to
~30-50 lines covering the structure in `references/survey-note-template.md`
(loaded on demand from this skill's `references/` subfolder when needed).

The survey note is the primary artefact of this workflow: it is what
future-you reads when drafting the paper's related-work section, and it
is what a collaborator reads to get up to speed without re-reading every
PDF.

Briefly, a good survey note has these sections:

1. Header: citekey, full citation, PDF path.
2. Headline claim (one sentence).
3. Method (full detail with key equations in MathJax).
4. Test cases + parameters used in the paper.
5. Headline numerical results.
6. Relevance to our paper (why we cite this; in which sections).
7. Critical observations (insights NOT in the abstract).
8. Action items for our paper draft.

Load `references/survey-note-template.md` from this skill for the full
template + a worked example.

## Step 5: Collection log

Append a row to `references/_collection_log.md` documenting:

- citekey
- verification status (verified / arXiv-only / placeholder)
- date verified
- any corrections made vs an earlier entry
- any quirks worth noting (e.g. "supplementary material is essential",
  "v3 of the arXiv preprint is significantly different from v1")

The collection log serves as the audit trail. When a reviewer asks
"how did you decide on this citation?" or when you discover a
mis-attribution months later, the log is where you check.

Load `references/collection-log-template.md` from this skill for the
template.

## Workflow rules

1. **Never cite a paper you have not verified.** Placeholder entries are
   acceptable in `references/bibliography.bib` only if they are tagged
   explicitly (e.g. `note = {pending verification}`) and marked in the
   collection log as such.
2. **Survey-note quality matters more than count.** A short paper with 5
   well-written survey notes is more useful than a long one with 25
   superficial ones. If a note would just restate the abstract, skip it
   and link the abstract instead.
3. **Re-read the source.** When writing the paper's related-work
   section, re-open the survey note (and if needed the .txt extraction)
   rather than relying on memory or your initial summary.
4. **Track corrections.** If you discover a mis-attribution (wrong
   author list, wrong year, wrong arXiv ID), log it explicitly in
   `_collection_log.md`. Do NOT silently fix it -- the audit trail is
   what makes the corpus trustworthy.
5. **MathJax for equations.** Survey notes use MathJax (`$...$` inline,
   `$$...$$` display) for any equations transcribed from the source.
   ASCII-art math is forbidden in survey notes.
6. **Survey notes and the collection log are HUMAN-FACING documents.**
   Both are read by the user when drafting the paper, by co-authors
   when re-orienting, and (sometimes) by reviewers. They follow the
   conventions in the `human-facing-doc-authoring` skill (audience
   split, narrative prose over telegraphic fragments, tables where
   they aid scanning, date-stamps, no personal-path leaks). When
   producing or substantially revising either artefact, also load
   `~/.scicomp-research-skills/skills/human-facing-doc-authoring/SKILL.md`
   for the universal conventions and the per-doc-type self-review
   checklist.

## Output contract

When the user invokes this skill, the agent should:

1. Confirm or create the directory layout (Section "Directory layout")
   if it does not exist.
2. Walk through the 5 steps for each paper the user provides
   (interactively or in batch).
3. After processing, summarise in a single message:
   - Citekeys added.
   - Verification status of each.
   - Any corrections discovered vs prior entries.
   - PDFs missing (if any).
   - Survey notes written.
   - Suggested next step (typically: read the survey notes, then update
     the paper's plan-of-record / Section 1 reading list).

## See also

- `references/survey-note-template.md` -- the canonical survey-note
  template + worked example.
- `references/collection-log-template.md` -- the canonical
  collection-log template + worked example.
- `templates/paper-skeleton/` (in this repository, sibling of `skills/`)
  -- a starter paper-repo skeleton that pre-creates the `references/`
  and `notes/` directory structure.
- `~/.scicomp-research-skills/skills/human-facing-doc-authoring/SKILL.md`
  -- universal conventions for human-facing docs. The survey-note +
  collection-log templates above embody these conventions; load the
  human-facing-doc-authoring skill when authoring or revising either
  artefact and you want the cross-cutting checklist.

---

*Created 2026-05-13 by A. Attia. Distilled from the literature-survey
workflow developed for the rl-oed paper (14 references verified across
3 sections of the paper's plan-of-record). Revised 2026-05-13 (added
Workflow rule #6 + See-also pointer to human-facing-doc-authoring
skill, since survey notes and the collection log are human-facing
artefacts).*
