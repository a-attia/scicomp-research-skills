# Render and audit (phase 5)

Loaded from `research-slides-authoring/SKILL.md` before declaring any
visual edit done. Covers rules A1 to A6 and the page-render script.

---

## A1. A clean build is not done

This is the most repeated failure in the evidence behind this skill.
It recurred in at least four separate sessions across both toolchains,
each time after the rule had already been written down.

After **every** edit that can change how a slide looks, follow this loop:

1. **Build.**
2. **Render the changed pages**:
   `scripts/audit-pages.sh deck.pdf 7 9-10`.
3. **Look** at each PNG as if seeing it for the first time.
4. **Fix**, then go back to step 1.
5. **Report**, naming the pages you viewed.

Render after each figure edit, not only at the end of the slide. After
ten unrendered edits you cannot tell which one broke the layout.

The script is in this skill's `scripts/` directory. From a project,
call it with its full path, for example
`~/.scicomp-research-skills/skills/research-slides-authoring/scripts/audit-pages.sh`,
or through a one-line wrapper in the project's own `bin/`.

## A2. Size in pixels, not DPI

| Purpose | Long edge | Why |
|:---|:---|:---|
| Layout review | about 1000 to 1100 px | Enough to read every label |
| Boundary and label checks | Crop the region, then magnify | A crop costs less and shows more than a larger full page |
| Upper limit | about 1568 px | Model image inputs are downscaled to about this, so extra pixels cost render time and buy nothing |

DPI is the wrong unit because page sizes differ. 200 dpi on a 4:3
Beamer page and 80 dpi on a 16:9 Marp page are both about 1000 px. The
script's `-s` option sets pixels directly (default 1100).

**A thumbnail grid checks content, never boundaries.** At grid scale a
1 to 2 mm clip at the slide edge is less than a pixel.

**Rendering costs tokens each time an image is viewed.** View the pages
you changed, not the whole deck. Do not re-view an unchanged page in a
later turn. A full pass belongs at the end of a round of work.

## A3. Boundary check

On each rendered page:

- [ ] Title on one line.
- [ ] Nothing crosses or crowds the right, bottom or top edge. Treat
      the outer 2 to 3 mm as a danger margin.
- [ ] Clear space above the footer band.
- [ ] No code line or table running off the slide.
- [ ] No hyphenation or orphaned words in narrow boxes. Reword rather
      than widen.
- [ ] Nothing drifted off centre.
- [ ] Link colours did not leak into other elements.

## A4. Count what must survive the render

An overfull slide can **drop a block** without any build warning
(Beamer hides overflow inside blocks), and a flowed poster can push a
section into a column off the page. Neither is visible in the source.

Keep a list of strings that must appear in the PDF (every section
heading, every slide title) and check it:

```bash
scripts/audit-pages.sh -e expected.txt deck.pdf
```

The script extracts the PDF text and reports every expected string
that is missing. It exits 1 if any is.

## A5. Sweep by rule, not by slide

At the end of a round of work, take one rule (V6 arrows-through-text,
V5 title fit, V1 consistency) and apply it to every slide, then the
next rule. Patterns that recur across slides are invisible one slide
at a time. Run the arrows-against-text pass separately, after layout.

## A6. Checker discipline

- **Calibrate a new tool on a known-good input first.** A new
  rasteriser that renders your diagram blank may render every diagram
  blank. Then the tool is broken, not the diagram.
- **A clear result says something about the checks, not the deck.**
  Look anyway.
- **When a reader and a check disagree, crop and magnify** before
  retuning anything.
- **When a check is wrong, fix the check**, not the content.
- **An edit that does not move the symptom is not addressing the
  cause.** Stop and re-diagnose.
- A build step that regenerates committed files counts as an edit. Run
  `git status` after it.

## Fresh eyes

When the agent client supports subagents, give the rendered pages and
the plan to a subagent with no other context, and ask it to restate
each slide's point. Where its restatement differs from the plan, the
slide is unclear.

---

*Created 2026-10-14 by A. Attia. Maintained by A. Attia.*
