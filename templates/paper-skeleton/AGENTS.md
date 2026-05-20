# <Paper short name> / AGENTS.md

This project loads shared workflow conventions from the
[scicomp-research-skills](https://github.com/a-attia/scicomp-research-skills) repository.
Before doing anything else, the consuming agent should:

1. Verify `~/.scicomp-research-skills/AGENTS.md` exists and is no more
   than 30 days stale (per its modification time). If stale, print a
   reminder suggesting `~/.scicomp-research-skills/bin/refresh.sh` and
   proceed anyway.
2. Read `~/.scicomp-research-skills/AGENTS.md`.
3. Read any skill files referenced below from
   `~/.scicomp-research-skills/skills/<name>/SKILL.md`.
4. Then read the rest of THIS file.

## Skills to load for this project

Load on demand, not all at once:

- `~/.scicomp-research-skills/skills/research-paper-writing/SKILL.md`
  -- section-by-section drafting + paragraph-clarity check + claim-evidence
  alignment + adversarial review.
- `~/.scicomp-research-skills/skills/literature-survey/SKILL.md`
  -- bibtex + PDF + pdftotext + survey-note workflow for the bibliography.
- `~/.scicomp-research-skills/skills/human-facing-doc-authoring/SKILL.md`
  -- load whenever authoring or substantially revising any
  human-facing project doc (README.md, PLAN.md, `notes/survey_*.md`,
  `references/_collection_log.md`, rebuttal drafts, ...). The
  human/agent audience split is universal; this skill codifies the
  conventions and per-doc-type skeletons.
- `~/.scicomp-research-skills/skills/agent-resource-discipline/SKILL.md`
  -- load at the start of any session that will involve heavy
  reading / searching / PDF handling / multi-file editing / web
  fetching, AND for the first-action / last-action protocols that
  give the agent persistent memory across sessions via the project's
  indices (PLAN.md status, `_collection_log.md`, `notes/README.md`).

### Available but not loaded by default

The following skills are available and load on demand for specific
non-routine tasks; do NOT load them at session start unless the user
asks for the matching task.

- `~/.scicomp-research-skills/skills/project-onboarding/SKILL.md`
  -- only load if the user wants to migrate this project to a
  different framework structure, or asks about adopting additional
  framework features. Not relevant for routine drafting / experiment
  / reviewer-response work.

---

## Project facts

- **Name**: <full paper title>
- **Nature**: journal paper
- **Status**: <e.g. drafting Section 5; M3 milestone>
- **Plan-of-record**: PLAN.md (read this after AGENTS.md)
- **Target venue**: <venue class>
- **Target submission**: <date>
- **Code dependencies**: <upstream libraries this paper depends on>
- **Audience composition** (added 2026-05-17 per F-18; useful for
  derivative artefacts like talk decks / posters / rebuttals where the
  agent would otherwise have to interview the user about audience for
  every session): <mix of audience types -- e.g. "domain
  practitioners + AI-curious researchers; mostly intermediate
  expertise; 30-min talk + ~10 min Q&A; single-author presentation">.
  Sub-fields the agent may consult independently:
  - **Audience types**: <AI-curious / domain practitioners / theoreticians / engineers / hybrid; one or more>
  - **Expertise level**: <novice / intermediate / expert / mixed>
  - **Session shape**: <conference talk / seminar / lab meeting / poster / one-off rebuttal / collaborator handoff / journal paper / monograph chapter>
  - **Time budget**: <e.g. "30 min talk + 10 min Q&A">
  - **Co-presenters / co-authors**: <names + roles if relevant; else "single-author">
  - **Recording / sharing constraints**: <e.g. "talk recorded; slides published post-event" / "no recording; closed audience">.

## Project-specific overrides

(Anything that differs from the universal conventions in
`~/.scicomp-research-skills/AGENTS.md` Section 6. If nothing differs,
write "None".)

## Project-specific facts the agent should not have to derive

(One-off facts: target venue formatting requirements, citation style,
key collaborators, specific external dependencies, current draft phase,
known gotchas. The agent benefits from knowing these without reading
PLAN.md cover-to-cover.)

- Citation style: <e.g. natbib + numeric>
- Key collaborators: <names + roles>
- Specific dependencies: <specific git tags / versions>
- Current phase: <M1 -- bibliography pass / M3 -- experiments / M6 -- drafting>

---

*Created YYYY-MM-DD by <your name>.*
