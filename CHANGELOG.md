# Changelog

Revision history of the root `AGENTS.md` of `scicomp-research-skills`,
moved here on 2026-05-14 to keep the AGENTS.md file focused on its
agent-facing content. Per-skill revision history continues to live at
the foot of each skill's `SKILL.md`. Per-template revision history
lives at the foot of each template's individual files.

This file follows the AGENTS.md universal-convention date-stamp-footer
format (`*Revised YYYY-MM-DD (note about the revision).*`) but
formatted as a chronological list rather than a prose footer.

---

## 2026-05-14

- **Post-fresh-audit cleanup**:
  - HIGH: compressed 3 over-long skill descriptions
    (`research-software-engineering`, `project-onboarding`,
    `agent-resource-discipline`) to <= 1024 chars per the OpenCode
    skill-spec limit codified in Section 8.
  - MEDIUM: trimmed the `research-software-engineering` workflow
    table to 3 ship-ready references; moved the 8 unshipped to a
    "Planned references" subsection with explicit "do NOT try to
    load these" warning.
  - MEDIUM: Section 7 acknowledges both paper-skeleton +
    software-skeleton AGENTS.md as canonical with raised 50-150 line
    target.
  - MEDIUM: ATTRIBUTION.md de-staled "templates/software-skeleton/
    planned" framing.
  - Section 6 sub-grouped into 6.1-6.6 for scanability + reformatted
    this footer into a multi-paragraph italic block.
  - LOW: paper-skeleton brought to parity with software-skeleton via
    CITATION.cff + experiments/README.md + figures/README.md +
    .github/ISSUE_TEMPLATE/{reviewer-comment-followup,
    experiment-rerun-needed, figure-update-needed}.md; missing
    template README footers added; documented the deliberate
    date-stamp-footer exception for upstream-vendored
    research-paper-writing references.
- **Path C (over-engineering audit)**: added STATUS.md provisional-
  framework callout + wired into README + AGENTS.md (top-of-file
  STATUS callout block). The framework was built in 4 days with
  extensive prior-art audits but ZERO real research projects had
  used it end-to-end yet; STATUS.md gives honest framing without
  changing any actual content.
- **Revision history extracted from AGENTS.md to this file**, which
  is the source of this CHANGELOG.

## 2026-05-13

- **Initial repository creation** by clone-and-diverge from
  Master-cai/Research-Paper-Writing-Skills @ 9ee5edd.
- **Post-clone cleanup**: removed orphan upstream agent config,
  dual-licensed LICENSE, single-sourced per-project boilerplate via
  `templates/paper-skeleton/AGENTS.md`, added Section 11 "Starting a
  new project".
- **Skill: project-readme-authoring** added + Section 6
  README-vs-AGENTS.md audience split convention.
- **Renamed**: project-readme-authoring -> human-facing-doc-authoring;
  generalised scope to all human-facing docs (PLAN.md,
  notes/survey_*.md, references/_collection_log.md, etc.); expanded
  universal convention; added per-doc-type structure files for plan
  / notes / audit-log.
- **Skill: agent-resource-discipline** added + Section 6 universal
  one-liners for tool selection / parallelism / targeted reads /
  re-use-prior-work / persistent-memory; codifies PDF lifecycle,
  web-fetch caching, context-window budget, first-action /
  last-action protocols.
- **Upstream-feedback channel** added: CONTRIBUTING.md +
  .github/ISSUE_TEMPLATE/ + per-project notes/agent_feedback.md
  template + Section 6 universal one-liner pointing at it. The
  per-project feedback channel + the agent-resource-discipline
  skill's recording rules close the loop between project sessions
  and upstream skill improvements.
- **Skill: research-software-engineering** first cut: SKILL.md +
  references/01-numerical-correctness.md +
  references/02-testing-for-numerical-code.md +
  references/11-ai-assisted-coding-rules.md, per the prior-art
  audit's PR1 sequencing; remaining 7 references + companion
  templates/software-skeleton/ planned for PR2-PR4.
- **Template: software-skeleton** shipped as PR3 ahead of audit's
  original PR2: AGENTS.md / PLAN.md / README.md / CITATION.cff with
  Zenodo handshake / .gitignore / experiments/README.md /
  figures/README.md / notes/README.md + agent_feedback.md /
  references/_collection_log.md /
  .github/ISSUE_TEMPLATE/{numerical-correctness-regression,
  api-ergonomics, performance-regression}.md / bootstrap.sh
  delegating to scientific-python/cookie | NLeSC/python-template |
  CU-DBMI/template-uv-python-research-software; AGENTS.md Section 5
  templates table updated; AGENTS.md Section 11.B replaced "not yet
  shipped" stub with full 7-step walkthrough at parity with
  paper-skeleton's 11.A; templates roadmap pruned.
- **Skill: project-onboarding** added: SKILL.md +
  references/{existing-project-audit, scenario-1-no-agentic-work,
  scenario-2-existing-agentic-files, conflict-resolution,
  migration-prompts}.md, addressing the realistic case of adopting
  the framework on an existing project; AGENTS.md Section 5
  updated; new Section 12 'Adopting on an existing project' added;
  ready-to-paste prompts for both scenarios + sub-cases provided;
  per-project AGENTS.md template in
  templates/{paper,software}-skeleton/ updated with
  project-onboarding in skills-to-load list; README.md gains an
  'Adopting on an existing project' section.
- **templates/software-skeleton/ multi-language**: paper-coupling
  layer is language-agnostic; bootstrap.sh adds `julia` option
  delegating to JuliaBesties/BestieTemplate.jl; new MULTI-LANGUAGE.md
  inside the template explains which placeholders are Python defaults
  vs language-agnostic + provides per-language quick references for
  Julia / C++ / Rust / Fortran / MATLAB / Mathematica +
  mixed-language projects + the placeholder-translation table;
  template's AGENTS.md / PLAN.md / README.md flag Python defaults
  explicitly with cross-references to MULTI-LANGUAGE.md; AGENTS.md
  Section 5 templates row + Section 11.B bootstrap step updated.

---

*Maintained by A. Attia. Format: chronological by date; most-recent
date first; each entry summarises one revision (typically one or two
commits).*
