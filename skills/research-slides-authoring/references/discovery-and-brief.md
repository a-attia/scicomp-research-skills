# Discovery and brief (phases 1 and 2)

Loaded from `research-slides-authoring/SKILL.md` at the start of a new
deck, or when an existing deck has no brief. Covers rules D1 to D4 and
the brief format.

---

## D1. Read before asking

Before asking the user anything, read:

- the per-project `AGENTS.md`, especially the **Audience composition**
  field (audience types, expertise, session shape, time budget,
  co-presenters, recording and sharing constraints);
- `PLAN.md` and any existing `notes/talk_brief.md` or
  `notes/talk_plan.md`;
- the material the talk presents: the paper draft, the README of the
  software, the experiment results;
- the venue template, if one is already in the repository.

**Never ask what you can read or measure.** A question the agent
could have answered locally costs the user a turn and signals that the
agent did not look.

## D2. One batch of questions

Ask everything that reading did not answer, in **one** message:

| # | Question | Why it matters |
|:--|:---|:---|
| 1 | Toolchain and template (Beamer with a venue template, Marp, PowerPoint, ...) | Determines the audit details and what can be styled |
| 2 | Audience mix and expertise | Sets math, code and jargon density (D3) |
| 3 | Venue, slot length, Q&A time | Slide budget (about one per minute) |
| 4 | Working title, or permission to propose two or three | Title and subtitle shape the arc |
| 5 | Abstract, if one exists | The contract (D4) |
| 6 | URLs or repositories to show, and which are public | QR codes and the privacy pass |
| 7 | Will the PDF be distributed? | Clickable links from the first draft |
| 8 | Recording or publication of the slides | What must be removed before sharing |
| 9 | Co-presenters and who presents what | Parallel tracks, hand-offs |

Skip any question the Audience composition field already answers, and
say that you skipped it.

## D3. Audience sets density

| Audience | Math | Code | Jargon |
|:---|:---|:---|:---|
| Mathematical (applied-math conference, math institute) | Displayed and derived; notation defined once | Rare | Field-standard terms fine |
| Engineering or domain practitioners | Key equation only, with each symbol labelled | The one line they will type | Domain terms fine, method terms defined |
| Mixed (practitioners and method people) | One equation per claim, each symbol labelled | One line at most | **Both directions are jargon**: define the domain terms for method people and the method terms for domain people |
| Non-technical leadership or funders | None | None | None; outcomes, cost and risk |

## D4. The abstract is the contract

If an abstract exists, every planned slide either supports a sentence
in it or is cut. If the deck has drifted from the abstract, reconcile
one with the other and tell the user which way.

If no abstract exists, propose one (about 150 words, ending on the
takeaway) and put it on a backup slide. For abstract structure, use
`research-paper-writing/references/abstract.md` rather than inventing
guidance here.

## The brief (phase 2)

Write `notes/talk_brief.md`, one screen, and get approval before
planning:

```markdown
# Talk brief: <working title>

- **Claim (one sentence):** <what the audience should believe afterwards>
- **Audience:** <mix, expertise>; density per D3: <math / code / jargon>
- **Slot:** <N> min + <M> min Q&A -> about <N> slides
- **Toolchain:** <toolchain + template>
- **Distribution:** <PDF shared? recorded? public?>
- **Arc:** setup -> conflict -> resolution -> what to do next
- **Must include:** <results, figures, URLs>
- **Must not include:** <unreleased results, private links, ...>
- **Open questions for the user:** <...>
```

---

*Created 2026-10-14 by A. Attia. Maintained by A. Attia.*
