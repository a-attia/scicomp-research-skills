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

## 2026-05-17

- **Session A: skill-optimisation pass driven by real-project feedback
  (argo-anywhere + AmigAI).** Applied 10 distinct findings from the
  feedback corpus; no new infrastructure, no new skills, no new
  templates. Goal: tighten existing skill content based on what real
  projects actually surfaced, before any further framework expansion.
  - **F-12**: `skills/project-onboarding/SKILL.md` frontmatter
    description + "When to load this skill" section rewritten to add
    an auto-load trigger for bare-of-AGENTS.md directories whose
    contents look like a research project. The AmigAI session went
    straight to drafting `slides.tex` without recognising the directory
    as a Scenario 1.A onboarding opportunity; the skill was loaded too
    late. Auto-load conditions enumerated explicitly (no AGENTS.md +
    canonical framework checkout exists + research-project-shaped
    contents + agent about to do substantive work). Also added a "do
    NOT load" carve-out for tiny scratch directories where the
    onboarding overhead exceeds the project's lifetime value.
  - **F-18**: both `templates/{paper,software}-skeleton/AGENTS.md`
    gain an `Audience composition` field under the existing "Project
    facts" section. The field captures audience types (AI-curious /
    domain practitioners / theoreticians / engineers / hybrid),
    expertise level, session shape, time budget, co-presenters,
    recording / sharing constraints (paper) OR primary user persona,
    expertise level, use contexts, secondary audiences, release-
    announcement channels, communication constraints (software). With
    this field populated up-front in per-project AGENTS.md, derivative
    artefacts (talk decks, posters, release announcements, rebuttals)
    skip an entire audience-discovery interview turn. Per the AmigAI
    feedback's proposal A4 "Cross-cutting framework changes" section.
  - **F-03..F-08 (this commit)**: shipped
    `skills/research-software-engineering/references/12-shell-and-cross-language-interop.md`
    (~370 lines) consolidating 6 rules from the argo-anywhere project's
    notes/agent_feedback.md: (12.1) YAML/JSON quoting on the bash/
    Python interop boundary; (12.2) setdefault for security-defaulted
    keys preserves the wrong default on upgraders; (12.3) error-
    message recovery hints must themselves be tested; (12.4) test
    stimulus must actually exercise the assertion site; (12.5)
    shell-script unit-test mechanics (pipe-eats-exit-code; awk
    function-body extraction fragility); (12.6) exit-summary "what
    to do next" hints must be scope-keyed not action-keyed. Reference
    12 moved from the SKILL.md "Planned references" table to the live
    "Workflow table"; SKILL.md footer updated. The framework's
    `research-software-engineering` skill now ships 4 references
    (01, 02, 11, 12); 7 remain planned (03, 04, 05, 06, 07, 08, 09,
    10 -- subtract 12 from the original 8-references-still-planned
    count). Each rule cites its argo-anywhere origin + concrete
    example.
  - **F-02**: `skills/human-facing-doc-authoring/SKILL.md` gains a
    "Rewriting an existing substantial doc" subsection (~80 lines)
    inserted between the "Authoring workflow" numbered list + the
    "Output contract" heading. Codifies a 5-step content-check-table
    discipline for any rewrite of a substantial existing doc (>100
    lines OR project-fact-bearing OR cross-referenced from
    elsewhere): inventory → identify destinations → produce check
    table → present to user for approval → execute + diff. The
    pattern is borrowed from `project-onboarding/references/scenario-2-existing-agentic-files.md`
    Scenario 2.C (which solves the same problem for migrating
    CLAUDE.md → AGENTS.md); generalised here for any doc-rewrite.
    Motivated by the argo-anywhere onboarding session (2026-05-14)
    where a substantial README was rewritten without a discipline
    forcing the agent to PROVE nothing was lost -- the silent
    failure mode the content-check table makes auditable. Includes
    explicit "when to apply" + "when NOT to apply" carve-outs to
    avoid bureaucratic overhead on small docs.
  - **F-17**: `skills/human-facing-doc-authoring/SKILL.md` gains a
    new subsection "K. Self-invalidation of cited facts" (~50
    lines) under the universal-conventions section (between J.
    Hygiene + the "What goes where" heading). Codifies four rules
    for inline cited facts that will drift over time (counts,
    enumerations, status labels, SHAs): (1) prefer cross-reference
    over inline citation when a single source of truth exists;
    (2) when inline citation is load-bearing, tag with a self-
    invalidation marker -- parenthetical date-stamp + source
    pointer; (3) audit cited facts before committing any doc
    edit; (4) status labels carry the date they were last
    verified, not the date they were added. Motivated by Session
    A's own STATUS.md / CHANGELOG.md maintenance burden where
    every commit shifts counts that other docs cite, with no
    mechanism to flag the drift between sessions. STATUS.md,
    CHANGELOG.md, README.md "Current status" sections, and
    per-skill SKILL.md footers identified as the most-frequent
    drift sites.

## 2026-05-14

- **AI co-authorship attribution: default flipped from OFF to ON.**
  Root AGENTS.md Section 6.3 previously said "no `Co-Authored-By`
  trailers by default; per-project AGENTS.md MAY override to add
  them" (inherited from the Master-cai upstream's stance). Flipped
  to "default = ON; per-project AGENTS.md MAY override to omit" on
  the rationale that (a) the agent IS doing substantive work in
  most sessions; (b) the JOSS 2025+ AI-Usage Disclosure norm makes
  per-commit attribution increasingly expected; (c) Bridgeford et
  al. 2025 R9 ("AI wrote it" is never an accountability defence)
  is about *responsibility*, not *attribution* -- the trailer
  records who participated, it doesn't shift accountability.
  Changes:
  - Root AGENTS.md Section 6.3 rewrote the "Commit messages" /
    "AI co-authorship attribution" rules accordingly.
  - templates/paper-skeleton/.gitmessage + templates/software-skeleton/.gitmessage
    (new) ship the Co-Authored-By: Claude trailer pre-wired; new
    projects activate via `git config --local commit.template
    .gitmessage` after bootstrap.
  - This repo's own CONTRIBUTING.md simplified -- the
    "Maintainer-policy override" section was added in the previous
    commit (when the framework default was OFF + this repo
    overrode); now removed since this repo follows the framework
    default.
  - skills/project-onboarding/references/conflict-resolution.md
    Conflict D (AI co-authorship attribution) rewritten to reflect
    the polarity flip. Now describes "default = ON" + lists the
    common reasons for an override (institutional policy
    prohibits naming AI; AI involvement is rare enough that
    per-commit attribution is noise; conference / journal
    compliance constraint).
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
