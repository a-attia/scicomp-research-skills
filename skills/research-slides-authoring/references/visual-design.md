# Visual design (phase 4)

Loaded from `research-slides-authoring/SKILL.md` while drafting or
polishing figures and slide layout. Covers rules V1 to V8, including
the diagram-failure checklist.

---

## V1. Consistency

- **Polish one, polish all.** When one figure gains a treatment (group
  titles, shadows, a caption style), every comparable figure gets it.
  A deck where one figure is polished and five are plain looks
  unfinished.
- **Style each element type once.** Nodes, code blocks, tables,
  callouts and captions are each defined in one place: the theme, the
  preamble, or a macro. Never style a single slide by hand.
- **The title sits in the same place on every slide.**

## V2. Colour

- One colour per role (input, process, output, warning, conclusion),
  and no exceptions.
- When colour encodes state, add a legend.
- The conclusion or alert colour must differ from the colour of the
  boxes around it, or the alert disappears.
- Bullet and section colours match the section they belong to.

## V3. Hierarchy

- **Named subjects** (the two tools the talk is about) must look
  different from **generic groupings** (a row of four interchangeable
  models in a container).
- Stages of a flow are styled by role, not by position.
- In decision figures, distinguish what was chosen, what was delivered,
  and what is still a target.

## V4. Depth

One elevation level or none. Stacked shadows and gradients compete
with the content.

## V5. Titles fit on one line

Confirm it in the render, not the source. Every template has its own
limit; measure it once and note it in the project's `AGENTS.md`.

## V6. Diagram-failure checklist

Run this on every diagram, in the render:

- [ ] **Arrows through text.** Trace every arrow shaft against every
      label it passes: node labels, container titles, the frame title,
      the footer, captions. Run this as a **separate pass after layout**
      is settled, because layout passes miss it.
- [ ] **Labels sitting on lines.** An edge label drawn on its own line
      is unreadable. Move it, anchor it, or as a last resort give it an
      opaque background.
- [ ] **Cramped node text**, touching or nearly touching the border.
- [ ] **Stranded or disconnected boxes** that the eye cannot place.
- [ ] **Connectors too short to read** as a flow: when the arrowhead
      is more than about a third of the arrow, the gap reads as a dash.
- [ ] **Missing grouping.** Three or more nodes in one category belong
      in a labelled container.
- [ ] **Fan-in to one narrow box**, which piles arrowheads together.
- [ ] **Text dimmed to invisible** by an automatic outline or overlay.

The bounding-box traps behind most arrow-through-text misses:
multi-line labels are taller than they look; colour does not change a
bounding box; rotated text keeps its unrotated box; a neighbour's label
counts too.

## V7. Accessibility

Sufficient contrast, a colour-blind-safe palette (never red against
green as the only distinction), a sans-serif face at a readable size,
about six elements per slide at most, and no animation that carries
meaning a PDF reader will lose.

## V8. Figures by reference

Generate every figure with a committed script, and have the deck refer
to the output by name. Never embed figure bytes in the deck source
(for example, base64 data URIs in Markdown). Embedded figures make the
source unreadable to tools and agents, bloat the history on every
edit, and silently go stale when the data changes. The exported PDF
can still be self-contained.

**Open every figure at full size once, on its own**, before it goes on
a slide. Label collisions are invisible at slide scale.

---

*Created 2026-10-14 by A. Attia. Maintained by A. Attia.*
