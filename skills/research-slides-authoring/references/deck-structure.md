# Deck structure (phase 3)

Loaded from `research-slides-authoring/SKILL.md` when planning a deck
or restructuring one. Covers rules S1 to S7 and the plan format.

---

## S1. Plan before drafting

Write `notes/talk_plan.md` and get the user's approval before
drafting any slide. Structure cannot be recovered by editing slides:
a deck drafted in work-plan order stays in work-plan order however
much its slides are polished.

```markdown
# Talk plan: <title>

Claim: <one sentence, from the brief>

| # | Section | Title (a full-sentence finding) | Visual idiom | Depends on |
|--:|:---|:---|:---|:---|
| 1 | -- | <title slide> | -- | -- |
| 2 | Setup | "Sensor placement decides what an inversion can recover" | Spine figure, all dimmed | -- |
| 3 | Setup | "Greedy placement is the standard, and it is myopic" | Two-panel comparison | 2 |
| ... | | | | |
| N | -- | "Try it on your own problem next week" | QR + one command | -- |
```

Visual idioms: spine figure, before/after, flow diagram, plot, table,
single equation, single code line, quote, QR code. A row without one
is a candidate for merging into its neighbour.

Walk the plan with the user before drafting.

## S2. The titles alone make the argument

Read only the titles, in order. They should tell the story (setup,
conflict, resolution, next step). If they are noun phrases with no
verbs ("Background", "Method", "Results"), the deck is filed, not
argued.

**Detection:** extract the titles and read them aloud. For Beamer,
`grep -o '\\begin{frame}{[^}]*}'`; for Marp, the `#` lines.

## S3. Hand-offs

Each slide opens on something the previous one established, and ends
on something the next one needs. A slide that could be moved anywhere
in the deck is not connected to its neighbours.

## S4. Required slots

| Slot | Content |
|:---|:---|
| Title slide | Title, speaker, venue, **date and draft version** |
| Contents and section dividers | When the deck has 8 or more slides. Each divider links back to the contents in a distributed PDF |
| Acknowledgements | Funding, collaborators, and AI assistance where it was substantive |
| Summary (optional) | 3 to 7 takeaways, after the synthesis and before the call to action. Never the last slide |
| Call to action | Specific: a command, a URL, a question for the room |
| Backup | Abstract, extra results, references, after the call to action |

## S5. Parallel tracks

When a talk presents several artefacts (two tools, two studies), give
each its own track, joined only at the opening and the synthesis.
Braiding them slide by slide makes each one harder to follow. The
exception is when one really depends on the other; then the dependency
is the story.

## S6. The spine figure

One overview figure, reused at the opening, at each section opener
(with that section highlighted) and at the synthesis. Keep **one
source** with a highlight parameter, so a fix to the figure reaches
every copy. In Beamer, a macro taking the highlighted node; in Marp, a
generated figure per variant from one script.

## S7. Time budget

About one slide per minute of speaking, fewer for dense results.
Count the plan's rows against the slot before drafting.

---

*Created 2026-10-14 by A. Attia. Maintained by A. Attia.*
