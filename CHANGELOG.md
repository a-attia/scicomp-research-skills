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

## 2026-05-20 (continued)

- **README.md drift audit + F-20 downstream-doc-audit rule.** User
  surfaced that README.md still claimed `STATUS (2026-05-14):
  provisional` + `ZERO real research projects` despite Session A +
  A.5 + 2 real-project cleanups landing in the meantime. Two
  deliverables in one commit:
  - **README.md updated for 2026-05-20 reality**: (a) status
    callout date bumped + ZERO-projects claim replaced with 2
    real-projects evidence acknowledgement + retirement-roadmap
    pointer; (b) "What you get" section rewritten as 6-skill +
    2-template tables with self-invalidation markers per F-17 +
    pointer to AGENTS.md Section 5 as canonical source; (c)
    repo-layout tree updated to show all 6 skills + 2 templates
    + missing top-level docs (STATUS.md, CHANGELOG.md,
    CONTRIBUTING.md, .github/ISSUE_TEMPLATE/); (d) "Software
    projects ... don't have dedicated templates yet" contradiction
    fixed (template exists); (e) "Feedback from real projects"
    section mentions software-skeleton + new `_resolved/` +
    `_archive/` convention + 4 issue templates (was 3).
  - **F-20: new subsection L "Downstream-doc audit before commit"
    in `skills/human-facing-doc-authoring/SKILL.md`** (~110 lines,
    after subsection K). Codifies the meta-discipline: before
    committing any non-trivial change, the agent enumerates a
    standard list of drift-prone downstream docs (README,
    STATUS, CHANGELOG, AGENTS Section 5, per-skill SKILL.md
    footers, per-template README, issue templates, per-project
    notes/README) + audits each + reports the audit checklist
    visibly to the user. Composes with K: K marks WHERE drift is
    likely; L is the cron-job that prevents drift in the first
    place. Distinguishes trivial vs non-trivial changes (only
    non-trivial trigger the audit). Includes separate audit
    lists for changes to scicomp-research-skills itself vs
    changes to per-project repos using the framework.
    Motivated by the 2026-05-20 README.md gap as existence proof
    (STATUS.md got updated, CHANGELOG.md got updated, README.md
    was missed -- F-20 prevents that miss).

## 2026-05-20

- **Session A.5: archive + resolved-feedback convention back-propagated
  to skeleton templates.** Driven by the post-Session-A cleanup of
  argo-anywhere + AmigAI projects, where the question "what do we do
  with agent_feedback.md entries that have been actioned upstream + with
  upstream-proposal drafts that became GitHub issues?" surfaced.
  Convention: two parallel sub-directories under each project's
  `notes/`:
  - `notes/_resolved/<date>_<slug>.md` -- one file per actioned-
    upstream agent_feedback entry, with a resolution-metadata
    header (date logged, date resolved, F-ID, upstream commit,
    original location); plus `notes/_resolved/INDEX.md` indexing
    all of them. The entry in `agent_feedback.md` is replaced by a
    3-line stub (date + title + RESOLVED-upstream pointer)
    preserving chronological discoverability.
  - `notes/_archive/<date>_<slug>.md` -- one file per superseded /
    filed-elsewhere artefact (e.g. upstream-proposal drafts that
    became GitHub issues; impl notes for removed components;
    preprint versions superseded by published versions); plus
    `notes/_archive/INDEX.md`.
  The two are kept separate because "resolved upstream" and
  "superseded / filed elsewhere" are different kinds of "done"
  and conflating them loses information.
  Files touched:
  - `templates/paper-skeleton/notes/README.md`: new "Archive +
    resolution log" section before "Maintenance"; agent_feedback.md
    description updated to mention the resolved-stub convention;
    "Maintenance" section gains a follow-the-procedure reminder.
  - `templates/software-skeleton/notes/README.md`: same edits as
    paper-skeleton; "Maintenance" section additionally clarifies
    that removed-component impl notes go to `_archive/` (not
    just status=`archived`).
  - `templates/{paper,software}-skeleton/notes/_resolved/INDEX.md`:
    new file (~65 lines, identical content in both templates);
    skeleton table with "Entries" + "Partial resolutions" sections
    + "When to add" rules.
  - `templates/{paper,software}-skeleton/notes/_archive/INDEX.md`:
    new file (~50 lines, identical content in both templates);
    skeleton table + "When to add" rules.
  Real-project evidence: argo-anywhere applied the convention to 5
  agent_feedback entries (F-03..F-08 actioned by Session A reference
  12) on 2026-05-20 in commit `9769e70`; AmigAI applied it to 1
  fully-resolved entry (F-12) + 1 partially-resolved entry (F-18) +
  2 archived upstream-proposal drafts (filed as GitHub issues #2 +
  #3) on 2026-05-20 (AmigAI is not a git repo so no commit hash).
  Both cleanups exercised the convention end-to-end before it was
  back-propagated here.

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
  - **F-19**: new `.github/ISSUE_TEMPLATE/append-evidence-to-skill-proposal.md`
    (~50 lines, frontmatter `name: Append evidence to existing
    skill proposal`, label `evidence`). Standardises the format
    for adding new session/project data points to an open
    `new-skill` proposal issue WITHOUT re-opening the proposal
    each time. Includes a sanitised-excerpt block (for evidence
    not linkable from a public notes/agent_feedback.md), an
    "Updated evidence count" section (sessions / projects /
    threshold-reached?), and a reminder to cross-link from the
    target proposal issue so the discussion thread stays
    synchronised. Motivated by Session A's three new-skill
    proposals (#1 monograph, #2 privacy, #3 slides) all sitting
    below the 3-sessions+2-projects threshold; future sessions
    will accumulate evidence via this template rather than
    editing the proposal in place.
  - **STATUS.md honest update reflecting Session A's deliveries.**
    Header bumped from 2026-05-14 to 2026-05-17; acknowledges
    that argo-anywhere + AmigAI projects ran during 2026-05-15..
    2026-05-17 and Session A rolled their feedback into 7
    commits. "What is well-grounded": `templates/software-
    skeleton/` AGENTS.md skeleton + paper-coupling layer moved
    up (one real codebase exercised; Audience composition field
    added). "What is informed prediction":
    `research-software-engineering` updated 3->4 references
    shipped, 8->7 planned (reference 12 added this session);
    `project-onboarding` acknowledged 2 real onboarding sessions
    with 5 scenario branches still speculation;
    `MULTI-LANGUAGE.md` Python branch acknowledged as exercised;
    1 of 16 prompts exercised; upstream-feedback channel
    acknowledged as having produced 2 journals + 3 issues + 1
    roll-up. Honest evidence count table updated: 2 projects, 2
    feedback files (~2200 lines), 3 new-skill proposals open, 10
    skill-improvement issues applied in Session A, 2 onboarding
    sessions, 1 roll-up session; external-user evidence still 0.
    Roadmap-to-no-longer-provisional: condition 1 at 2/3,
    condition 2 at 10/5 (with caveat: same author rolling up own
    feedback), condition 3 still 0, condition 4 at 1/8. New
    "What Session A learned" section (~40 lines) captures six
    framework-shape signals from the roll-up. Footer date-stamp
    updated. The STATUS.md update itself follows the F-17 self-
    invalidation discipline (parenthetical date-stamps + source
    pointers for drifting facts).

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
