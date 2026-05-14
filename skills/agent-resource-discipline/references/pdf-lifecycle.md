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

For (1), consider re-running `pdftotext` with different flags
(`-raw`, `-layout`, no flag) to compare; one of them often works
where the others don't. Cache the better extraction in the same
`.txt/<citekey>.txt` location (overwriting the worse one).

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

---

*Created 2026-05-13 by A. Attia. Revised 2026-05-13 (post-prior-art
audit): added "How this differs from PaperQA-style RAG" comparison
table; restructured "When to re-extract or re-read" into a 5-rung
fallback ladder (target-grep -> wider .txt read -> PDF binary -> PDF
replaced -> distrust existing note) with explicit update-the-note
side-effects so the cache stays fresh.*
