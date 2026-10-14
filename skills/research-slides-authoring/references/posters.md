# Posters (provisional)

Loaded from `research-slides-authoring/SKILL.md` for a conference or
project poster. **Provisional:** the evidence behind this file is one
poster in one project. Treat it as a starting point and log what it
misses in `notes/agent_feedback.md`.

---

## What changes from a deck

| Concern | Deck | Poster |
|:---|:---|:---|
| Reading | Sequential, paced by the speaker | Non-linear, paced by the reader, often without the author present |
| Distance | Projected; read from the room | Read from 1 to 2 m; title from 5 m |
| Claim | One per slide | One headline for the poster, one per section |
| Failure mode | Overflow off one slide | **A flowed layout pushes a whole section into a column off the page** |

## Rules

- **The title states the finding** (C1), readable from about 5 m.
- **Three to five sections**, each with an assertion heading, read in a
  clear order (columns or numbered blocks).
- **Count the sections in the render** (A4). List every section heading
  in an expected-text file and run `audit-pages.sh -e`. A section that
  overflowed its column is often absent from the page rather than
  visibly clipped.
- **Render the whole poster at review size, then crop each section**
  and magnify. One full-page render shrinks body text below legibility.
- **A QR code** to the paper, code or preprint, with the text URL and
  a caption (C9).
- **Text extraction order is not visual order** on posters. Never use
  extracted text to decide what the title or first section is; render
  and look (`agent-resource-discipline/references/pdf-lifecycle.md`).

---

*Created 2026-10-14 by A. Attia. Maintained by A. Attia.*
