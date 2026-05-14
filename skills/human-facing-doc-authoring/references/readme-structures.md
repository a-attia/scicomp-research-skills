# Example README structures

Loaded on demand from the `human-facing-doc-authoring` skill when an
agent needs a starting-point skeleton for a specific kind of project
`README.md`. Each skeleton is a TOC + a short note on what each section
should contain. Adapt freely; do not treat as a template to fill in
blank-by-blank.

---

## A. Research-paper repository

For a paper workspace bootstrapped from
`templates/paper-skeleton/`. Audience: collaborators on the paper +
the agent's human user when re-orienting after time away.

```markdown
# <Paper title>

<One-sentence "what is this paper about". Then 2-3 sentences of
positioning: what's new, who it's for, current status.>

> **For AI agents**: read [`AGENTS.md`](AGENTS.md) first, then
> [`PLAN.md`](PLAN.md). This README is for human collaborators.

## Contents
- [Status](#status)
- [Headline contribution](#headline-contribution)
- [How this repo is organised](#how-this-repo-is-organised)
- [How to reproduce a result](#how-to-reproduce-a-result)
- [How to add a new experiment](#how-to-add-a-new-experiment)
- [Pinned upstream versions](#pinned-upstream-versions)
- [Authors and acknowledgements](#authors-and-acknowledgements)

## Status
<One paragraph: target venue, target submission date, current draft
phase, blockers if any. Update on every PLAN.md revision.>

## Headline contribution
<2-3 sentences. Pull from PLAN.md "Headline Contribution"; do NOT
duplicate the full version. Reference PLAN.md for details.>

## How this repo is organised
<Annotated ASCII tree showing references/, notes/, experiments/,
figures/, drafts/. Cross-reference the literature-survey skill
workflow.>

## How to reproduce a result
<Pick one headline result. Show: which experiment dir, which seed,
which command. Cross-reference experiments/README.md for the full
matrix.>

## How to add a new experiment
<Cross-reference PLAN.md Section 4 "Experiment Protocol" for the
methodology. Show the directory-naming convention.>

## Pinned upstream versions
<List the upstream libraries this paper depends on, with git commit
hashes for reproducibility.>

## Authors and acknowledgements
<Authors with affiliations. Funding. People who provided code /
data / discussions.>
```

Notes:

- The paper's **headline contribution + plan-of-record** lives in
  `PLAN.md`, not the README. The README *summarises* in 2-3 sentences
  and links to `PLAN.md` for the full version.
- The README does NOT list the survey notes; that index lives in
  `notes/README.md`.
- The README does NOT list every experiment; that lives in
  `experiments/README.md` (or similar).

---

## B. Research software library

For a Python (or other) library intended for downstream consumption.
Audience: potential users (deciding whether to adopt), new
contributors, returning maintainers.

```markdown
# <library-name>

<One-sentence "what does this library do". Then 2-3 sentences of
positioning vs alternatives.>

> Built for <use case>. If you need <related but different use case>,
> see <other library>.

> **For AI agents**: read [`AGENTS.md`](AGENTS.md) first.

## Contents
- [Install](#install)
- [Quick example](#quick-example)
- [API tour](#api-tour)
- [Public API surface](#public-api-surface)
- [How it's organised](#how-its-organised)
- [Development](#development)
- [Citation](#citation)
- [Licence](#licence)

## Install
<One code block. The bare minimum (`pip install ...` or
`uv add ...`). Defer per-platform notes to docs/install.md.>

## Quick example
<10-20 line code snippet that produces a recognisable result. Should
be runnable verbatim. Output shown as a comment or follow-on code
block.>

## API tour
<3-5 short subsections, each on a major user-facing concept. Each
~10 lines of explanation + a short example. NOT exhaustive; this is
the "what's in the box" tour.>

## Public API surface
<List or table of the top-level public functions/classes with
one-line descriptions. Cross-reference the full API docs.>

## How it's organised
<Annotated ASCII tree showing src/, tests/, docs/, examples/.
Brief description of each top-level module.>

## Development
<How to set up a dev env (`uv sync` / `pip install -e .[dev]`), how
to run tests, how to run the linter, how to build docs. Cross-
reference CONTRIBUTING.md for the deeper version.>

## Citation
<BibTeX entry for citing the library in academic work, if applicable.>

## Licence
<One sentence + link to LICENSE.>
```

Notes:

- The README is **not** the API reference. It tours the API; the
  reference lives in generated docs.
- "Quick example" and "API tour" together should be readable in 5
  minutes and convey what the library is for.
- For a library with multiple distinct usage modes (e.g. CLI + Python
  API), give each its own short subsection.

---

## C. This skills repository

For a meta-repository of agent skills + templates. Audience: humans
who want to use the skills (mostly the maintainer + contributors), and
forks who want to adapt.

(See this repository's actual `README.md` -- it follows this skeleton
and is the canonical worked example.)

```markdown
# <skills-repo-name>

<One-sentence scope. Then 2-3 sentences positioning: which
agent clients are supported, what kinds of projects it serves.>

> **For AI agents**: read [`AGENTS.md`](AGENTS.md). This README is
> for humans.

## Contents
- [What you get](#what-you-get)
- [Quick start](#quick-start)
  - [1. Install once per machine](#1-install-once-per-machine)
  - [2. Start a new project](#2-start-a-new-project)
  - [3. Day-to-day use](#3-day-to-day-use)
- [How it fits together](#how-it-fits-together)
- [Starting a new project (in detail)](#starting-a-new-project-in-detail)
- [Maintenance](#maintenance)
- [Extending this repository](#extending-this-repository)
- [Pulling updates from upstream](#pulling-updates-from-upstream)
- [Provenance and licence](#provenance-and-licence)

## What you get
<Up-front naming of the reusable building blocks: skills, templates,
tooling. One subsection or table per category.>

## Quick start
<3 numbered steps for the impatient reader. Each step copy-paste-able.
Cross-reference the deep sections for context.>

## How it fits together
<Conceptual model: two-checkout layout, refresh protocol, what
install.sh does. The "architecture" of the skills system.>

## Starting a new project (in detail)
<Per-project-type recipes: paper, software, rebuttal. Where templates
exist, point at them; where they don't, give the interim recipe.>

## Maintenance
<Refresh, update, uninstall.>

## Extending this repository
<How to add a new skill or template. Cross-reference AGENTS.md
Sections 8 and 9.>

## Pulling updates from upstream
<If forked: how to merge upstream changes.>

## Provenance and licence
<Lineage, acknowledgements, licence pointer.>
```

---

## D. Reviewer-response / rebuttal workspace

For a rebuttal sub-directory inside a paper repo (e.g.
`<paper-repo>/rebuttal_round1/`). Audience: co-authors collaborating
on the response, future-self when preparing a subsequent round.

```markdown
# Rebuttal -- <paper short name>, round <N>

<One sentence: which review cycle, key dates.>

## Contents
- [Reviewer summary](#reviewer-summary)
- [Response status](#response-status)
- [Files in this directory](#files-in-this-directory)
- [Workflow](#workflow)

## Reviewer summary
<Compact table: reviewer | rating | top concerns. One row per
reviewer.>

## Response status
<Per-reviewer + per-concern status table: addressed / in-progress /
deferred. Update as the response is drafted.>

## Files in this directory
<Annotated list: response.md, diff.tex, supplementary additions,
new figures.>

## Workflow
<How to add a new response thread, how to mark a concern as
addressed, where to put new experimental results.>
```

Notes:

- The detailed line-by-line response goes in `response.md`, not the
  README.
- The README is the *index* over the rebuttal material.

---

## Common adaptations

- **Multiple-author projects**: add a "Who maintains what" subsection
  near the bottom (after Maintenance) listing per-component owners.
- **Projects with non-obvious external dependencies**: add a
  "Prerequisites" subsection between Quick Start and How it fits
  together.
- **Projects with a strong domain context**: add a "Glossary" section
  if the project uses domain-specific terminology that a typical
  visitor won't know.
- **Projects with significant prior art**: add a "Comparison to prior
  work" subsection (paper-style positioning); cross-reference
  `PLAN.md` for the deeper analysis.

---

*Created 2026-05-13 by A. Attia.*
