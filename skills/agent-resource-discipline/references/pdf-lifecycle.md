# PDF lifecycle

Loaded on demand from the `agent-resource-discipline` skill whenever a
session involves PDF intake, re-reading, or any literature work.

PDFs are the most expensive class of input in this ecosystem: a typical
academic paper PDF is 10-40 pages with mixed text + figures + equations,
and the binary format is not directly consumable by most agents. The
rules below minimise repeated work across sessions.

## How this differs from PaperQA-style RAG

A common alternative to the protocol below is **programmatic
retrieval-augmented generation** over PDFs (parse + chunk + embed +
retrieve), e.g. via [PaperQA2](https://github.com/Future-House/paper-qa).
Both approaches solve the same underlying problem (avoid re-reading
PDFs in full on every query), but optimise for different things:

| Dimension                     | This skill (survey-note cache)                    | PaperQA / RAG (embedding cache)                  |
|:------------------------------|:--------------------------------------------------|:-------------------------------------------------|
| Cache representation          | Hand-curated `notes/survey_<citekey>.md` (~30-50 lines) | Vector embeddings of chunked PDFs            |
| Per-query token cost          | Low (a survey note is small)                      | Medium (embedding lookup + chunk fetch)          |
| Ad-hoc query flexibility      | Only what the survey note covers                  | Any question over the whole paper                |
| Reproducibility / version control | Markdown in git; diffs auditable              | Vector DB; not normally checked in                |
| Citation-quality summaries    | Yes (the survey note IS a citation)               | No (RAG output is regenerated per query)         |
| Cross-session human review    | Yes (the user reads the same note the agent reads) | No (the user does not read the embeddings)      |

The skill's protocol is designed for **research-paper authoring**,
where citation-quality, version-controlled, human-reviewable summaries
matter more than ad-hoc query flexibility. For the latter use case
(e.g. reading 200 papers to answer a single broad question), PaperQA-
style RAG is the better tool. Use whichever is appropriate; the two
can also coexist (survey notes for the deeply-cited papers, RAG over
the long tail).

---

## The lifecycle in one diagram

```text
First encounter                     Subsequent encounters
---------------                     ---------------------
new PDF arrives                     question about <citekey>
       |                                    |
       v                                    v
references/pdf/<citekey>.pdf        notes/survey_<citekey>.md
       |                            exists?
       v                                    |
pdftotext -layout                  +--------+--------+
       |                           |                 |
       v                           yes              no
references/pdf/.txt/<citekey>.txt   |                 |
       |                            v                 v
       v                       Read survey   Grep .txt for section,
read for survey note            note FIRST   then Read with offset+limit
       |                            |                 |
       v                            v                 v
notes/survey_<citekey>.md      answers Q?       answers Q?
       |                          |   |             |   |
       v                         yes  no           yes  no
append to notes/README.md        |    |             |    |
       |                       done   v          done   v
       v                              fall back        re-read
references/_collection_log.md   to .txt extraction    PDF (rare;
                                                      .txt usually
                                                      enough)
```

The point: `pdftotext` runs ONCE. Survey notes are read FIRST.
Re-reading the PDF binary is a last resort.

## Step 1: One-shot pdftotext extraction (intake)

When a new PDF arrives:

```bash
mkdir -p references/pdf/.txt
pdftotext -layout references/pdf/<citekey>.pdf references/pdf/.txt/<citekey>.txt
```

The `-layout` flag preserves the two-column structure of typical
academic papers, which makes the output much more readable than
default flow-mode.

**Batch all PDFs in one go** when seeding a new project:

```bash
mkdir -p references/pdf/.txt
for pdf in references/pdf/*.pdf; do
  base=$(basename "$pdf" .pdf)
  [ -f "references/pdf/.txt/${base}.txt" ] && continue   # idempotent
  pdftotext -layout "$pdf" "references/pdf/.txt/${base}.txt"
done
```

The `-f ...txt && continue` makes this idempotent (re-runnable without
re-extracting unchanged PDFs).

For supplementary material, repeat with `<citekey>-supp.pdf` ->
`.txt/<citekey>-supp.txt`.

The `.txt/` directory is gitignored (it's a regenerable cache).

**Never re-extract** unless the PDF itself changed (e.g. you replaced
the arXiv preprint with the published version). The `.txt` is your
canonical source of truth from this point on.

## Step 2: Survey-note-first lookup (subsequent encounters)

Whenever you need information about a paper that is already in the
corpus:

1. **Check whether `notes/survey_<citekey>.md` exists.**
   - If yes: `Read` the survey note FIRST.
   - If no: see Step 3.
2. If the survey note answers your question -> done.
3. If the survey note does NOT answer your question (e.g. you need a
   specific equation that wasn't in the headline-result extraction):
   - **Grep the `.txt` extraction** for the relevant section name
     (e.g. `Grep pattern: '4.2 Advection-diffusion'`).
   - `Read` with `offset` + `limit` for that section only.
   - Consider updating the survey note with the new fact (so the next
     session doesn't have to re-derive).

**Never `Read` the full `.txt` file** unless the question really
requires reading the whole paper end-to-end (rare; usually for the
first deep-dive that produced the survey note in the first place).

## Step 3: First-time deep read (when no survey note exists yet)

When the corpus has the PDF + `.txt` but no survey note:

1. `Read` the `.txt` file. Initial pass: usually fine to read the
   whole thing for a 10-30 page paper (~500-1500 lines of text after
   `pdftotext`).
2. **Produce the survey note immediately** following the
   `literature-survey` skill's template. This is the deposit; future
   sessions will withdraw from it.
3. Update `notes/README.md` and `references/_collection_log.md` per
   the literature-survey skill's Steps 4 + 5.

If the paper is very long (50+ pages, e.g. a survey paper or a thesis
chapter): use `Grep` for section names + targeted `Read` with
`offset`+`limit`. Do not bulk-read.

## What a survey note should pre-emptively cover

The survey note's job is to make future PDF re-reads UNNECESSARY for
all but the rarest questions. The
`literature-survey/references/survey-note-template.md` template
specifies eight required sections; following it strictly is what makes
the future-cheap promise hold.

In particular, the **Method (full detail)** section should include the
key equations in MathJax, not just prose summaries. If a future
session needs the equation, it should be in the note already.

## Fallback protocol (when the survey note is insufficient)

The agent's default is **read the survey note first**. But the note is
sometimes wrong, missing, or insufficient for the current question.
The fallback ladder, in order of cost:

### Rung 1: target-grep the `.txt` extraction

When the survey note doesn't directly answer the question but the
question is well-defined (a specific equation, a specific table number,
a specific parameter value):

1. `Grep` the `.txt` extraction for keywords or section names from the
   question.
2. `Read` the matching section with `offset` + `limit`.
3. **Update the survey note** with the new fact you just retrieved
   (one or two lines under the appropriate section; add a "Revised
   YYYY-MM-DD" stamp). Future sessions will not have to re-derive.

This is the most common fallback. It costs ~50-200 tokens (one Grep,
one targeted Read) instead of ~1500 (whole-paper Read).

### Rung 2: read more of the `.txt`

When you've target-grepped and the answer requires understanding more
context than a single section provides:

1. `Read` the surrounding 2-3 sections (still offset+limit; not the
   whole paper).
2. **If you found that the survey note has a substantive error or
   omission** (not just a missing detail): add a "Corrections to
   apply" entry to `references/_collection_log.md` describing what
   the note got wrong; then revise the note with a "Revised" stamp.
3. Surface the discrepancy to the user in your response.

### Rung 3: open the PDF binary

Reserved for cases where text extraction genuinely fails:

1. **`pdftotext` lost critical content** (uncommon, but happens with
   heavily-formatted papers; equations rendered as images; columns
   parsed in wrong order on a complex layout).
2. **Need to look at a figure or table directly** (`pdftotext` does
   not extract figures; some tables come out as garbled grids).
3. **Need to see the page layout** (e.g. understand which figure
   refers to which paragraph).
4. **The question is about a string's ROLE, not its presence** — see
   the next subsection. This is the dangerous case, because extraction
   appears to succeed.

For (1), consider re-running `pdftotext` with different flags
(`-raw`, `-layout`, no flag) to compare; one of them often works
where the others don't. Cache the better extraction in the same
`.txt/<citekey>.txt` location (overwriting the worse one).

#### Extraction order is not visual order

**`pdftotext` emits text in content-stream order, which is the order
objects were written into the file — not the order a human reads them.**
On a single-column paper these usually coincide, which is what makes
the failure mode so easy to walk into: the heuristic "first extracted
line is the title" holds often enough to feel reliable, then fails
silently on any document where layout carries meaning.

It fails hardest on **posters, slides, figures, and title banners**,
where the headline typically sits in a separate graphic layer and may
be emitted anywhere in the stream — frequently *after* body text that
appears visually below it.

The generalisable rule:

> **Text extraction establishes that a string is PRESENT. It never
> establishes that a string is the title, the heading, the caption, or
> the first thing a reader sees.** Presence is a text question; role is
> a layout question. Do not answer a layout question with a text tool.

When the question is about role — *what is this poster's title?*, *which
heading does this paragraph sit under?*, *what does the reader see
first?* — render the page and look at it:

```bash
pdftoppm -png -r 40 -f 1 -l 1 file.pdf /tmp/page   # -> /tmp/page-1.png
```

Then `Read` the PNG. At 40 dpi a page is legible for structure and
costs little; raise to 100+ dpi only if you must read small print.
Multimodal agents can consume the image directly; for text-only agents,
this rung means asking the user rather than guessing.

**Symptoms that you are in this failure mode:**

- Two candidate strings both look like plausible titles.
- The extracted "title" reads more like a section heading or a thesis
  statement than a title.
- An adjacent source (a metadata record, a submitted abstract, a
  citation) disagrees with your extraction.

That last one is the important one. **When an external record disagrees
with your extraction about a title, the prior should be that the record
is right and the extraction is wrong** — records are usually entered by
a human looking at the artifact, whereas extraction is a lossy
projection of it. Render before concluding otherwise, and be especially
careful before propagating the extracted string into other documents.

Corollary for the surrounding files: **do not use a sibling file to
corroborate an extracted title.** A nearby `abstract.txt`, `STORY.md`,
or `notes.md` may record an *earlier* version, a submission draft, or a
discussion of framing rather than the delivered title. Two weak signals
pointing the same way is not confirmation; it is the same guess twice.

### Rung 4: the PDF was replaced upstream

When the upstream PDF has changed (preprint -> published; v1 -> v3 on
arXiv; corrigendum issued):

1. Replace `references/pdf/<citekey>.pdf` with the new PDF.
2. Re-run `pdftotext`.
3. Diff the new `.txt` against the cached old one (`git diff` if the
   `.txt` were tracked, or `diff` against a backup).
4. Update the survey note for any substantive changes.
5. Add a "Corrections to apply" entry noting the version change AND
   any change to bib metadata (page numbers, year).

### Rung 5: the survey note was written by someone else and you don't trust it

If you have specific reason to suspect the existing note misrepresents
the paper:

1. Read the `.txt` end-to-end (this is the rare case where bulk read
   is appropriate).
2. **Do NOT silently overwrite** the existing note. Add a new
   "Revised YYYY-MM-DD by <reviewer>" stamp + an "Earlier version
   said X; deep re-read shows Y" delta block at the end of the note.
3. Surface the discrepancy in your response so the user can decide
   whether to keep the old characterisation or adopt the new one.

## Default state

Outside the fallback ladder above, the day-to-day default is: the
`.txt` is enough; the note is enough; the PDF binary stays in the
directory but is never re-opened. **The fallback is a fallback, not a
fall-through.** If you find yourself reaching Rung 3 or 5 routinely,
the survey notes are too thin -- update the `literature-survey` skill
workflow to capture more on first read.

## Anti-patterns to refuse

Modes the agent should refuse to enter:

- **"Let me just re-read the PDF to make sure"** when a survey note
  exists. Read the note. If the note doesn't answer, target-grep the
  `.txt`. The PDF is a fallback, not a default.
- **`Read references/pdf/<citekey>.pdf`** -- agent tools generally
  cannot consume PDF binaries. Use the `.txt` extraction.
- **Re-running `pdftotext` on a PDF that already has a `.txt`.**
  Idempotent in command form, but the user-visible cost is the
  agent thinking "let me extract this" when extraction already exists.
- **Reading the full `.txt` of a 60-page survey paper to find one
  fact.** `Grep` for the fact's keywords first.
- **Answering a layout question from `pdftotext` output.** "What is the
  title of this poster/slide/figure?" is not a text question. Render the
  page (`pdftoppm -png -r 40`) and look. See Rung 3.
- **Treating the first extracted line as the title.** Extraction order
  is content-stream order, not reading order.
- **Concluding an external record is stale because your extraction
  disagrees with it.** Render the artifact first; the record is more
  often right than the extraction.

---

*Created 2026-05-13 by A. Attia. Revised 2026-05-13 (post-prior-art
audit): added "How this differs from PaperQA-style RAG" comparison
table; restructured "When to re-extract or re-read" into a 5-rung
fallback ladder (target-grep -> wider .txt read -> PDF binary -> PDF
replaced -> distrust existing note) with explicit update-the-note
side-effects so the cache stays fresh. Revised 2026-09-27: added
"Extraction order is not visual order" to Rung 3 + three anti-patterns,
after a live session in which the agent read a conference poster's
title from `pdftotext` output, took the first extracted line as the
title, and reported an accurate institutional record as stale. The
banner sat in a separate graphic layer; the extracted line was the
first content-box heading. The wrong title had already propagated into
a submitted document and a CV before the user caught it. The
generalisation — text extraction answers presence, not role — applies
to any layout-bearing PDF, not just posters.*
