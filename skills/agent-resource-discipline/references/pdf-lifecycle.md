# PDF lifecycle

Loaded on demand from the `agent-resource-discipline` skill whenever a
session involves PDF intake, re-reading, or any literature work.

PDFs are the most expensive class of input in this ecosystem: a typical
academic paper PDF is 10-40 pages with mixed text + figures + equations,
and the binary format is not directly consumable by most agents. The
rules below minimise repeated work across sessions.

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

## When to re-extract or re-read the binary PDF

Rare cases. The honest list:

1. **The PDF was replaced** (preprint -> published version, v1 -> v3
   on arXiv). Re-run `pdftotext`; consider updating the survey note.
2. **The `.txt` extraction is corrupted or missing** (rare; usually a
   tooling bug).
3. **You need to look at a figure or table directly** (`pdftotext` does
   not extract figures). Use the binary PDF viewer.
4. **The survey note was written by someone else and you don't trust
   it**. Read the `.txt` end-to-end and produce a fresh note (do NOT
   silently overwrite the existing note; add a "Revised" stamp + note
   the disagreements).

Outside these cases: the `.txt` is enough; the note is enough; the
PDF binary stays in the directory but is never re-opened.

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

*Created 2026-05-13 by A. Attia.*
