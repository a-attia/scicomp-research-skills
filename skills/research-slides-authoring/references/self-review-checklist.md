# Self-review checklist

Run before reporting a deck as finished. One check per rule in
`research-slides-authoring/SKILL.md`; each line says how to detect a
failure. Report which checks you ran.

---

## Gates

- [ ] Brief approved by the user (`notes/talk_brief.md`).
- [ ] Plan approved by the user (`notes/talk_plan.md`).
- [ ] Every changed page rendered and viewed since the last edit (A1).

## Structure

- [ ] **S2** Titles alone, read in order, tell the argument.
      *Extract them and read them.*
- [ ] **S4** Title slide has date and version. Contents and dividers if
      8 or more slides. Acknowledgements. Specific call to action.
      Backup at the end.
- [ ] **S7** Slide count fits the slot (about one per minute).
- [ ] **D4** Every slide supports the abstract or claim.

## Content

- [ ] **C1** Every title is a full sentence stating a finding.
      *Flag titles with no verb.*
- [ ] **C2** No title needs "and".
- [ ] **C3** No comma chain of three or more steps.
- [ ] **C4** No bullet of 20 or more words.
- [ ] **C5** At most one code line per slide.
- [ ] **C6** Every symbol defined at or before first use; one meaning
      per symbol; every equation compiled.
- [ ] **C7** Every abbreviation spelled out at first use; no slide
      points at a repository file.
- [ ] **C8** Every number has a source or is labelled a target.
- [ ] **C9** Every URL classified; vital ones have QR, text and caption;
      private ones removed; clickable if distributed.
- [ ] **C10** Cited facts re-verified this build, including any your own
      session changed. *Grep the deck for counts, versions and dates.*
- [ ] **C11** No figure contradicts its caption or title.
- [ ] Prose habits per `human-facing-doc-authoring` section I.

## Visual

- [ ] **V1** Comparable figures share one treatment; element styles are
      defined once.
- [ ] **V2** One colour per role; legend where colour encodes state.
- [ ] **V5** Every title on one line, in the render.
- [ ] **V6** Diagram-failure checklist run, including the separate
      arrows-against-text pass.
- [ ] **V7** Contrast and colour-blind-safe palette.
- [ ] **V8** No figure bytes embedded in the source.

## Render

- [ ] **A2** Reviewed at about 1000 to 1100 px; edges cropped and
      magnified.
- [ ] **A3** Boundary check passed on every page.
- [ ] **A4** `audit-pages.sh -e expected.txt` reports all strings
      present.
- [ ] **A5** One sweep per rule across the whole deck.

## Distribution

- [ ] **X1** PDF delivered and its location reported, with the command
      that opens it.
- [ ] **X2** Nothing overwritten without being asked.
- [ ] **X4** Privacy pass if shared publicly (root `AGENTS.md` 6.7).

---

*Created 2026-10-14 by A. Attia. Maintained by A. Attia.*
