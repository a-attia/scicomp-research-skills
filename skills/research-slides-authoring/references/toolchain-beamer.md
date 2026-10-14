# Toolchain notes: Beamer

Loaded from `research-slides-authoring/SKILL.md` when the deck is
LaTeX Beamer. The core rules are toolchain-agnostic; this file holds
the Beamer-specific traps and idioms.

---

## Build and render

```bash
latexmk -pdf slides.tex
scripts/audit-pages.sh slides.pdf <changed pages>
```

A successful `latexmk` run is a build, not an audit (rule A1).

## Traps

| Trap | Symptom | Fix |
|:---|:---|:---|
| **Overflow inside blocks is not reported** | Content silently runs past the bottom of the frame; no `Overfull \vbox` warning | Render and look; use `audit-pages.sh -e` to catch dropped text |
| **`hyperref` link colour leaks** into the frame counter and footer | The page number in the footer turns the link colour | Set `linkcolor` to the footer text colour, or reset the footer colour in the template |
| **`\AtBeginSection` contents dims** the current entry to near-invisible | Section divider shows an unreadable contents list | Raise the shaded-entry opacity, or style the current section explicitly |
| **Venue templates reserve a footer band** | Content collides with the institution footer | Measure the band once; keep 10 mm or so clear above it |
| **Title-bar width is template-specific** | Two-line titles that push content down | Measure the one-line limit once and record it in the project `AGENTS.md` |
| **Aspect ratio** | Figures sized for 16:9 overflow 4:3, or the reverse | Fix `aspectratio` in the class options before drafting figures |

## TikZ idioms

- **Edge labels on lines** are unreadable. Place them with `above`,
  `below` or `sloped`, anchor them to a node side, or, when geometry
  cannot clear the overlap, give the label an opaque pill:

  ```latex
  \node[fill=white, rounded corners=2pt, inner sep=1.5pt] {label};
  ```

- **Bounding boxes.** Multi-line node text and rotated text keep larger
  boxes than they appear to; leave room.
- **Spine figure (S6).** One `\newcommand` that draws the figure and
  takes the node to highlight, so every copy stays in step.
- **Caption macro.** Define one `\slidecaption{...}` so every caption
  has the same style and position (V1).

## Distribution

- `\href{url}{text}` for every URL from the first draft if the PDF
  will be shared (C9).
- Put the draft version and date on the title slide (S4), for example
  through `\date{\today\ -- draft v3}`.

---

*Created 2026-10-14 by A. Attia. Maintained by A. Attia.*
