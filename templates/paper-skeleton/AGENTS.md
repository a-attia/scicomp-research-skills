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

---

## Project facts

- **Name**: <full paper title>
- **Nature**: journal paper
- **Status**: <e.g. drafting Section 5; M3 milestone>
- **Plan-of-record**: PLAN.md (read this after AGENTS.md)
- **Target venue**: <venue class>
- **Target submission**: <date>
- **Code dependencies**: <upstream libraries this paper depends on>

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
