# Slide composition (phase 4)

Loaded from `research-slides-authoring/SKILL.md` while drafting or
revising slide content. Covers rules C1 to C11.

---

## C1. Assertion-evidence

The title is a **full-sentence finding**; the body is mostly a visual
that supports it.

| Topic title (avoid) | Assertion title (use) |
|:---|:---|
| Results | Convex relaxation recovers the source with half the sensors |
| Sensor placement | Greedy placement stalls after the third sensor |
| Architecture | One script turns a five-step login into one prompt |

A relational claim (A causes B, A is faster than B, A flows into B)
gets a diagram or a plot, not a bullet.

## C2. One point per slide

If a slide needs "and" in its title, it is two slides.

## C3. Enumerate, never narrate

Three or more discrete items (steps, options, stages) become a list, a
numbered flow diagram or a table.

- Avoid: "Behind that one line: install the tool if missing, write its
  config, copy the script to the remote host, run it there, and start
  the monitor."
- Use: a five-step flow diagram, or a numbered list of five short items.

## C4. Slide vs speaker

The slide carries the bones: the claim, the evidence, the labels. The
speaker carries the sentences. A bullet of 20 or more words is speaker
text and belongs in the notes. Short sentences on the slide, detail
below the line or in the notes.

## C5. Code

Only the single line the audience will type or remember: the install
command, the one invocation. Multi-line sessions and configuration
blocks go in a handout or the README. If several lines are unavoidable,
the slide title states the takeaway, not "Example configuration".

## C6. Math

- One display equation per claim, at the density D3 sets.
- **Every symbol is defined** on that slide or earlier in the deck.
- **One symbol, one meaning** for the whole deck. If notation returns
  after a gap of several slides, remind the reader what it means.
- **Compile every equation.** Some renderers fail silently on bad math
  (see `toolchain-marp.md`).

## C7. Vocabulary

- Spell out every abbreviation where it first appears, even ones the
  speaker uses every day.
- Identifiers (function names, file names, config keys) support claims;
  they never replace them.
- No slide sends the reader to a file in the repository. The audience
  cannot open it.

## C8. Numbers

Every number points at its source (a footnote with the run, the
figure script, or the citation) or is labelled as a target or estimate.
Caveats go in the body where they change the meaning; provenance goes
in a footnote.

## C9. URLs and QR codes

Classify each URL in the deck:

| Class | Treatment |
|:---|:---|
| Public and vital (the audience should visit it) | QR code, the text URL, and a one-line caption |
| Public and decorative | Text URL only, or remove |
| Private (internal tracker, unreleased repository) | Remove before any sharing |

If the PDF will be distributed, make every URL clickable from the
first draft (`\href` in Beamer; ordinary links in Marp). Check in the
render that link colours did not leak into other elements.

## C10. Whole-deck consistency and fact currency

- **New material reconciles against the whole deck.** A change to one
  slide's claim, number or term can contradict three others. After a
  change, search the deck for every slide that mentions the same thing.
- **Re-verify cited facts at every build**, especially counts, versions
  and status quoted from other documents.
- **Check whether your own work made a cited fact stale.** The most
  common case: the deck quotes a status ("0 issues filed") that the
  same session's work changed. This is `human-facing-doc-authoring`
  rule K applied to slides.

## C11. A figure must not contradict itself

Check that the figure, its caption, and the slide title say the same
thing. Geometry carries meaning too: a cycle drawn as a straight row,
or a hierarchy drawn flat, contradicts a caption that says "loop" or
"layers".

---

*Created 2026-10-14 by A. Attia. Maintained by A. Attia.*
