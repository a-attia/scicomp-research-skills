# Toolchain notes: Marp

Loaded from `research-slides-authoring/SKILL.md` when the deck is Marp
(Markdown slides). The core rules are toolchain-agnostic; this file
holds the Marp-specific traps.

---

## Build and render

```bash
marp --pdf --allow-local-files deck.md -o build/deck.pdf
scripts/audit-pages.sh build/deck.pdf <changed pages>
```

## Traps

| Trap | Symptom | Fix |
|:---|:---|:---|
| **Markdown inside an HTML block** | Backticks, `**bold**` and `$math$` render literally inside a `<div>` | Put a blank line after the opening tag and before the closing tag |
| **Broken math fails silently** | KaTeX renders an error span or the raw LaTeX; the build succeeds | Compile every equation with the same KaTeX version, or look at every math slide |
| **`\|` inside a table cell** | Markdown splits the cell on the bar before KaTeX sees it; the equation breaks | Use `\vert`, `\mid`, or `\lVert ... \rVert` |
| **Flex containers** | The default theme makes `div`s flex containers, so percentage widths and spaces between inline elements behave unexpectedly | Set widths on the children; check spacing in the render |
| **Missing slide separator** | Two slides merge | `---` needs a blank line on both sides |
| **Hard-wrapped paragraphs** | Line breaks appear where the source wrapped | Do not hard-wrap prose in the deck source, or set `breaks: false` |
| **Embedded figures** | A 160-line deck becomes megabytes of base64 that no tool can read (V8) | Reference figures by name and substitute at build time |

## Diagrams (Mermaid)

- **Render Mermaid through Marp or a headless browser**, not
  `rsvg-convert`. Mermaid puts labels in `<foreignObject>`, which
  `rsvg-convert` drops, so the diagram looks blank. Calibrate on a
  known-good diagram before blaming yours (A6).
- **Subgraph titles collide** when several subgraphs sit side by side.
  Prefer flat graphs with labelled nodes, or stack subgraphs vertically.
- A `flowchart TB` overrides `direction LR` inside a subgraph.
- Subgraph titles inherit theme text colours; check their contrast.

## Distribution

Export PDF as the deliverable even when presenting the HTML. Keep the
PDF as a fallback (X1).

---

*Created 2026-10-14 by A. Attia. Maintained by A. Attia.*
