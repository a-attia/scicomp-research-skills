---
name: project-onboarding
description: Use this skill whenever a user wants to adopt the scicomp-research-skills framework on an EXISTING project (paper, software library, analysis repo) rather than starting from scratch -- OR when the agent has been asked to produce substantive project content (drafting, refactoring, planning) in a directory that has no AGENTS.md while the framework's canonical checkout (~/.scicomp-research-skills/) does exist on the machine. Make sure to load this when the user says "I have an existing project; help me start using these skills" OR when you find yourself about to do substantive work in a bare-of-AGENTS.md directory whose contents look like a research project (LaTeX sources, Python package layout, references/ + experiments/ + figures/ subdirectories, bibliography, notes). EVEN IF THE USER DOES NOT MENTION IT EXPLICITLY -- the bare-directory case is the silent failure mode that the AmigAI project surfaced. Covers two scenarios: (1) existing project with NO prior agentic instructions; (2) existing project WITH prior agentic instructions (CLAUDE.md / .cursorrules / etc.). Each scenario has sub-cases (empty / mature / non-standard for #1; one-file / many-files / substantive-content / conflicting-conventions for #2). Provides an inventory-first migration workflow that preserves user content, surfaces conflicts via the per-project AGENTS.md "Project-specific overrides" mechanism, and never silently overwrites. Companion to root AGENTS.md Section 11 (from-scratch starts). Composes with `human-facing-doc-authoring` and `agent-resource-discipline`.
license: MIT
metadata:
  audience: agents performing migration; users planning a migration
  domain: framework-adoption
  origin: A. Attia (added 2026-05-13)
---

# Project Onboarding (Adopting on an Existing Project)

## How this skill is organised (progressive disclosure)

This skill follows the same three-level progressive-disclosure pattern
as the other skills in this repository:

- **Level 1 (always in context once loaded)**: this `SKILL.md`,
  ~250 lines. Decision tree + universal rules + which references to
  load for which scenario.
- **Level 2 (loaded on demand by name)**: per-scenario reference files
  in `references/`, with worked examples.
- **Level 3 (planned future work)**: an interactive `bin/onboard.sh`
  helper that automates the inventory step. Specification deferred;
  ad-hoc execution via the skill's reference files is sufficient
  while we accumulate experience.

## When to load this skill

Load this skill when the user says any of:

- "I have an existing project; help me start using scicomp-research-skills on it."
- "Migrate this repo to use the scicomp-research-skills framework."
- "I already have a `CLAUDE.md` / `.cursorrules` / `AGENTS.md`;
  how do I integrate it with this framework?"
- "Adopt these skills on my existing paper / library / analysis repo."
- "Bootstrap on top of what I already have."

**Auto-load trigger (added 2026-05-17 from real-project feedback)**: also
load this skill on the FIRST tool call into a directory when ALL of:

1. The current working directory contains no `AGENTS.md` at the repo
   root.
2. The canonical framework checkout (`~/.scicomp-research-skills/`)
   exists on this machine.
3. The directory's contents look like a research project: presence of
   any one of `*.tex`, `*.bib`, `references/`, `experiments/`,
   `figures/`, `notes/`, `pyproject.toml`, `setup.py`, `Project.toml`,
   `CMakeLists.txt`, `slides/`, `paper/`, `drafts/`, OR a `*.pdf` in
   the repo root that looks like a manuscript.
4. The agent is about to do substantive work (drafting, editing, or
   creating content -- not just reading).

The AmigAI session (May 2026) showed that without this auto-load
trigger, the agent goes straight to drafting content (`slides.tex`)
without recognising the directory as a Scenario 1.A onboarding
opportunity. The skill therefore fires too late or not at all.

Do NOT load this skill if:

- The user is starting a NEW project from scratch -- use root
  `AGENTS.md` Section 11 + the appropriate template
  (`paper-skeleton/` or `software-skeleton/`) instead.
- The user wants to update an existing scicomp-research-skills-aware
  project (refresh canonical, pull upstream changes) -- that's
  `bin/refresh.sh` + `bin/install.sh --update`, not a migration.
- The directory is a tiny scratch space (single throwaway script;
  a one-shot data-conversion utility) where onboarding overhead
  would exceed the project's lifetime value.

## Core principle: preserve and migrate, never silently overwrite

The single most important rule for migration:

**Existing project content is the user's work. The agent's job is to
preserve it, surface any conflicts to the user explicitly, and migrate
content into the canonical layout -- not to replace existing files
with template defaults.**

Concretely:

1. **Audit before acting.** Before writing or moving any file, the
   agent inventories what already exists (see
   `references/existing-project-audit.md`). The audit produces a
   plan; the user reviews the plan; only then does the agent execute.
2. **Move rather than overwrite.** When the framework expects a file
   at path X and the user has content at path Y serving the same role,
   propose a rename + content merge -- do not write a fresh template
   file at X that obliterates Y.
3. **Surface conflicts explicitly.** When the user's existing
   conventions disagree with the framework's universal conventions
   (root `AGENTS.md` Section 6), surface the conflict + the
   override-convention (per-project AGENTS.md "Project-specific
   overrides" section can deviate from universal rules), and let the
   user decide.
4. **Never auto-delete.** Even when the framework's expected layout
   doesn't include a path the user has, do not delete. Either move
   it under the framework's layout, or leave it in place + note in
   PLAN.md / AGENTS.md that it exists.
5. **One commit per logical migration step.** A migration touching 30
   files + restructuring directories should be many small commits,
   not one big "migrate to scicomp-research-skills" mega-commit. Each
   step is reviewable + revertable independently.

## Decision tree: which scenario applies?

Before loading any reference file, classify the user's situation:

```text
                        Is there an AGENTS.md / CLAUDE.md /
                        .cursorrules / GEMINI.md / CONVENTIONS.md /
                        AGENT.md at the project root?
                                |
                +---------------+---------------+
                |                               |
               NO                              YES
                |                               |
        SCENARIO 1: no                  SCENARIO 2: existing
        prior agentic work              agentic instructions
                |                               |
                v                               v
        load                            load
        references/                     references/
        scenario-1-no-                  scenario-2-existing-
        agentic-work.md                 agentic-files.md
        +                               +
        references/existing-            references/existing-
        project-audit.md                project-audit.md
                                        +
                                        references/conflict-
                                        resolution.md
```

Both scenarios share the **inventory-before-acting** step (covered in
`references/existing-project-audit.md`). Both produce + execute a
migration plan that the user reviews.

### Scenario 1 sub-cases

`references/scenario-1-no-agentic-work.md` covers:

- **1.A**: empty-ish repo (a few files; no significant existing
  layout). Migration is essentially "copy template + fill in
  placeholders + first commit"; fastest path.
- **1.B**: mature repo with substantial existing structure
  (existing `src/`, `experiments/`, `figures/`, etc.). Migration
  must reconcile existing layout with framework's expected layout.
- **1.C**: repo with non-standard layout (sources at repo root, or
  `code/` instead of `src/`, or domain-specific layouts). Migration
  decides what's load-bearing vs cosmetic in the framework's
  expectations.

### Scenario 2 sub-cases

`references/scenario-2-existing-agentic-files.md` covers:

- **2.A**: one agent-file format (e.g. just `CLAUDE.md`). Migration:
  AGENTS.md becomes canonical; existing file becomes a symlink
  (preserving the agent client's discovery) OR its content merges
  into AGENTS.md.
- **2.B**: multiple agent-file formats (`CLAUDE.md` + `.cursorrules`
  + `GEMINI.md`). Same as 2.A applied N times; deduplicate during
  migration.
- **2.C**: agent-file with substantive project content (not just
  generic rules but project-specific facts, conventions,
  in-progress decisions). Content is valuable and must be migrated
  to the right destination (AGENTS.md "Project facts" / PLAN.md /
  notes/) rather than discarded.
- **2.D**: conflicting conventions (existing `CLAUDE.md` says X,
  shared root `AGENTS.md` Section 6 says Y). See
  `references/conflict-resolution.md` for the per-project override
  convention.

## Universal migration workflow

Regardless of scenario, the migration follows five steps:

1. **Audit** -- inventory the existing project. Output: a plan-of-
   migration document (typically appended to a temporary
   `notes/_migration_<date>.md` that gets deleted after the migration
   is committed). See `references/existing-project-audit.md`.
2. **Plan** -- propose specific file moves, content merges, new
   files to add, conflicts to resolve. The user reviews the plan
   before any write actions.
3. **Execute** -- do the migration. One commit per logical step
   (per the "one commit per logical migration step" rule above).
4. **Verify** -- run the loaded skills' first-action protocols to
   confirm the migrated project is in a valid state (PLAN.md exists +
   readable; AGENTS.md exists + readable; cross-references resolve;
   no personal-path leaks; pre-commit / shellcheck pass if
   applicable).
5. **Document** -- append an entry to the project's
   `notes/agent_feedback.md` recording what was migrated, what
   conflicts arose, and how they were resolved. This is the
   onboarding-session deposit (per
   `agent-resource-discipline/references/persistent-memory.md`'s
   last-action protocol).

The full step-by-step procedure lives in the per-scenario reference
files; this section is the spine.

## Ready-to-paste prompts for users

The user can copy any of the following into their agent's first
message to kick off a migration. Each prompt loads this skill,
classifies the scenario, and starts the audit.

Each prompt below begins with a **prerequisite-check block** so the
agent can install the framework if it isn't already installed
(rather than failing opaquely on the "load skill" step). The block
is identical across all prompts; the user always pastes ONE thing
regardless of install state.

For Scenario 1 (no prior agentic work):

```text
PREREQUISITE CHECK (run this first):

1. Check whether ~/.scicomp-research-skills/AGENTS.md exists.
2. If it does NOT exist, install the framework now. Try SSH first;
   if that fails, fall back to HTTPS:
     git clone git@github.com:a-attia/scicomp-research-skills.git ~/.scicomp-research-skills \
       || git clone https://github.com/a-attia/scicomp-research-skills.git ~/.scicomp-research-skills
     ~/.scicomp-research-skills/bin/install.sh
   If both clone attempts fail, report the error to me and stop;
   do not proceed silently.
3. If it exists but is more than 30 days old (modification time of
   ~/.scicomp-research-skills/AGENTS.md), suggest I run
   `~/.scicomp-research-skills/bin/refresh.sh` and proceed regardless.

REQUEST:

Load the project-onboarding skill from
~/.scicomp-research-skills/skills/project-onboarding/SKILL.md.
This is an existing <paper / software-library / analysis> project
with no prior AGENTS.md / CLAUDE.md / .cursorrules. Audit the
current state, produce a migration plan, and walk me through it
step by step before executing.
```

For Scenario 2 (existing agentic instructions):

```text
PREREQUISITE CHECK (run this first):

1. Check whether ~/.scicomp-research-skills/AGENTS.md exists.
2. If it does NOT exist, install the framework now. Try SSH first;
   if that fails, fall back to HTTPS:
     git clone git@github.com:a-attia/scicomp-research-skills.git ~/.scicomp-research-skills \
       || git clone https://github.com/a-attia/scicomp-research-skills.git ~/.scicomp-research-skills
     ~/.scicomp-research-skills/bin/install.sh
   If both clone attempts fail, report the error to me and stop;
   do not proceed silently.
3. If it exists but is more than 30 days old (modification time of
   ~/.scicomp-research-skills/AGENTS.md), suggest I run
   `~/.scicomp-research-skills/bin/refresh.sh` and proceed regardless.

REQUEST:

Load the project-onboarding skill from
~/.scicomp-research-skills/skills/project-onboarding/SKILL.md.
This is an existing <paper / software-library / analysis> project
that already has <CLAUDE.md / .cursorrules / AGENTS.md / ...>.
Preserve the existing content; produce a migration plan that
integrates with the scicomp-research-skills framework without
losing any of the project-specific facts I've already captured.
Walk me through the plan step by step before executing anything.
```

The full library of prompts (per sub-case) is in
`references/migration-prompts.md`.

## Workflow rules

The full discipline is in the references; the cross-cutting rules are:

1. **Audit before acting.** No file writes before the user has reviewed
   + approved the migration plan.
2. **Preserve user content.** Never silently overwrite. Move +
   merge; don't replace.
3. **Surface conflicts.** When user conventions disagree with
   framework conventions, name the conflict + cite both rules + ask
   the user to choose. The per-project AGENTS.md
   "Project-specific overrides" section is the formal home for
   approved deviations.
4. **One commit per logical step.** Many small migration commits,
   not one mega-commit.
5. **Never auto-delete.** When in doubt, move-and-document; let the
   user delete if they choose.
6. **Update `notes/agent_feedback.md`** with onboarding-specific
   observations: what worked smoothly, what required workarounds,
   what gaps in this skill the migration revealed.

## Adjacent skills (compose freely)

This skill composes with:

- `agent-resource-discipline` -- always load. The first-action
  protocol applies (read project state before acting); the last-
  action protocol applies (update indices + agent_feedback after).
- `human-facing-doc-authoring` -- load when migrating or creating
  any human-facing doc (the new AGENTS.md / PLAN.md / README.md /
  notes/ files all follow that skill's structural conventions).
- `literature-survey` -- load when an existing project has a
  bibliography that needs migration into the
  `references/_collection_log.md` audit-trail discipline.
- `research-software-engineering` (for software projects) or
  `research-paper-writing` (for paper projects) -- load AFTER the
  migration is done; they are for normal work, not for onboarding.

## Output contract

When the user invokes this skill, the agent should:

1. Confirm the scenario (1 vs 2 + sub-case) per the decision tree.
2. Load the matching scenario reference + always load
   `references/existing-project-audit.md`.
3. Execute the audit (first action: read existing repo state).
4. Produce a migration plan + present it to the user for review.
5. WAIT for the user to approve before executing any writes.
6. Execute step-by-step with one commit per logical step.
7. Run verification (Step 4 of the universal workflow).
8. Append an entry to `notes/agent_feedback.md` summarising the
   onboarding (Step 5 of the universal workflow).

## See also

- `references/existing-project-audit.md` -- the inventory-before-
  acting procedure shared by both scenarios.
- `references/scenario-1-no-agentic-work.md` -- worked examples
  for sub-cases 1.A / 1.B / 1.C.
- `references/scenario-2-existing-agentic-files.md` -- worked
  examples for sub-cases 2.A / 2.B / 2.C / 2.D.
- `references/conflict-resolution.md` -- how to surface and resolve
  conflicts between user conventions and framework conventions
  (the per-project AGENTS.md "Project-specific overrides" mechanism).
- `references/migration-prompts.md` -- ready-to-paste user prompts
  for each scenario + sub-case.
- Root `AGENTS.md` Section 12 -- agent-facing summary of this
  skill's workflow.
- Root `README.md` "Adopting on an existing project" -- user-facing
  summary of the same workflow.

---

*Created 2026-05-13 by A. Attia. Companion to the "Starting a new
project" workflow (root AGENTS.md Section 11 + README.md "Starting a
new project that uses this repository") which assumes a from-scratch
start. This skill addresses the realistic "I already have a project;
help me adopt the framework" case, which is more common than starting
fresh. Revised 2026-05-17 (F-12 from real-project feedback -- AmigAI):
broadened the triggering condition + frontmatter description to fire
on bare-of-AGENTS.md directories with research-project-shaped contents,
not only on explicit user requests. The AmigAI session showed the
agent missing the bare-directory onboarding opportunity because the
trigger was too narrowly worded.*
