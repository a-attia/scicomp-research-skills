# Migration prompts (ready-to-paste for users)

Loaded on demand from the `project-onboarding` skill when the user
needs an exact prompt to give their agent client to start a
migration.

This file is also useful **without** the skill being loaded yet --
the user can copy a prompt from here as their first message to a
new agent session. The prompt loads the skill + classifies the
scenario + starts the audit in one shot.

---

## How to use

1. Pick the prompt that matches your situation (Scenario 1 or
   Scenario 2; for Scenario 2, also identify which sub-cases apply).
2. Customise the `<...>` placeholders for your project (project type,
   path, anything specific).
3. Paste into your agent client (OpenCode, Claude Code, Cursor,
   ...) as the first message of a fresh session.
4. The agent will load the skill, run the audit, and present a
   migration plan for your review BEFORE making any changes.

If you're not sure which scenario applies, use the **discovery
prompt** at the bottom of this file -- it asks the agent to inspect
the repo and tell you which scenario it sees.

---

## Universal preamble

All prompts below assume the user has already installed the
canonical scicomp-research-skills checkout
(`~/.scicomp-research-skills/`) per the root `README.md` "Quick
start". If the user hasn't, the prompt will fail at the "load skill"
step; they should run:

```bash
git clone git@github.com:a-attia/scicomp-research-skills.git ~/.scicomp-research-skills
~/.scicomp-research-skills/bin/install.sh
```

then retry.

---

## Discovery prompt (when unsure of scenario)

Use this when you don't know whether your project is in Scenario 1
or Scenario 2 -- the agent figures it out:

```text
I have an existing project at <path-to-project> that I want to
adopt the scicomp-research-skills framework on. I'm not sure
whether I have prior agentic instructions or not.

Load the project-onboarding skill from
~/.scicomp-research-skills/skills/project-onboarding/SKILL.md
and its references/existing-project-audit.md. Inspect the project
state, classify which scenario applies (Scenario 1 = no prior
agentic work; Scenario 2 = existing agentic instructions), and
report:

1. Which scenario applies + which sub-case(s).
2. A summary of the existing project state.
3. A proposed migration plan.

Do NOT make any changes yet. After your report, I will tell you
whether to proceed with the plan as-is or adjust it.
```

---

## Scenario 1: no prior agentic work

### Prompt 1.A: empty-ish repo

```text
I have an existing project at <path> that has only a few files and
no significant directory structure. I want to start fresh using the
scicomp-research-skills framework.

This is a <paper / software-library / mixed> project.

Load the project-onboarding skill from
~/.scicomp-research-skills/skills/project-onboarding/SKILL.md
and its references/scenario-1-no-agentic-work.md (sub-case 1.A).

Run the existing-project-audit, then walk me through the migration
plan step by step. Treat this essentially as a "Starting a new
project" workflow per root AGENTS.md Section 11, preserving any
existing content (especially the existing README.md).

Do NOT make any changes until I confirm the plan.
```

### Prompt 1.B: mature repo with existing structure

```text
I have an existing project at <path> with substantial structure
already in place (existing src/ or code/, experiments/ or results/,
figures/, notes/, references/, etc.). I have NOT used any agentic
tooling on it yet -- no AGENTS.md, no CLAUDE.md, no .cursorrules.

This is a <paper / software-library> project.

Load the project-onboarding skill from
~/.scicomp-research-skills/skills/project-onboarding/SKILL.md
and its references/scenario-1-no-agentic-work.md (sub-case 1.B).
Also load references/existing-project-audit.md.

Run the audit, then produce a migration plan that reconciles my
existing layout with the scicomp-research-skills layout (see
~/.scicomp-research-skills/templates/<paper-skeleton OR
software-skeleton>/ for the target layout).

The migration plan should:

1. Inventory my existing directory structure.
2. For each top-level dir, decide whether to keep, rename, or merge.
3. Propose a sequence of small commits (one logical step per
   commit) that performs the migration.
4. Surface any conflicts or ambiguous cases for me to decide.

Walk me through the plan. Do NOT make any file changes until I
explicitly approve.
```

### Prompt 1.C: non-standard layout

```text
I have an existing project at <path> with a non-standard layout for
my domain: <briefly describe the layout, e.g. "all source at repo
root", "code/ instead of src/", "LaTeX-document-as-repo with no
code", "notebooks-and-data only">.

I have NOT used any agentic tooling on it yet.

Load the project-onboarding skill from
~/.scicomp-research-skills/skills/project-onboarding/SKILL.md
and its references/scenario-1-no-agentic-work.md (sub-case 1.C).

Run the audit. Then propose a migration plan that respects my
non-standard layout choices -- do NOT silently rename existing
directories to match the framework's defaults. Instead:

1. Identify which framework conventions are load-bearing (must
   adopt) vs cosmetic (can deviate via "Project-specific overrides"
   in the per-project AGENTS.md).
2. Propose deviations where my existing layout disagrees with the
   framework's default; document each in "Project-specific
   overrides" with a one-line rationale.
3. Add the framework files (AGENTS.md, PLAN.md, etc.) without
   reorganising my existing tree.

Walk me through the plan. Do NOT make changes until I approve.
```

---

## Scenario 2: existing agentic instructions

### Prompt 2.A: one agent-file format

```text
I have an existing project at <path> that already has a <CLAUDE.md
/ .cursorrules / GEMINI.md / etc.> at the repo root. I want to
adopt the scicomp-research-skills framework while preserving all of
the content I've already captured.

This is a <paper / software-library> project.

Load the project-onboarding skill from
~/.scicomp-research-skills/skills/project-onboarding/SKILL.md plus:
- references/existing-project-audit.md
- references/scenario-2-existing-agentic-files.md (sub-case 2.A)
- references/conflict-resolution.md (in case of convention
  conflicts)

Run the audit, with special attention to my existing agent-file's
content. Classify each section of the existing agent-file by:

(a) generic agent rule subsumed by framework universal conventions
    (drop on migration);
(b) generic rule that conflicts with framework convention (surface
    the conflict; let me decide);
(c) generic rule additional to framework (migrate to per-project
    AGENTS.md "Project-specific overrides");
(d) project-specific facts (migrate to per-project AGENTS.md
    "Project facts" section);
(e) plan-of-record content (migrate to PLAN.md).

Produce a migration plan that:

1. Builds the per-project AGENTS.md from the appropriate template
   plus the migrated content from (c)-(e).
2. Converts the existing agent-file to a symlink to AGENTS.md so
   my agent client still finds it.
3. Includes a content-check table verifying that every line of the
   original was either migrated, dropped (with reason), or flagged
   for my decision.

Do NOT make any changes until I review the plan + the content-check
table.
```

### Prompt 2.B: multiple agent-file formats

```text
I have an existing project at <path> that already has multiple
agent-files at the repo root: <list them, e.g. "CLAUDE.md,
.cursorrules, GEMINI.md">. I want to consolidate into the
scicomp-research-skills framework while preserving all of the
content.

This is a <paper / software-library> project.

Load the project-onboarding skill from
~/.scicomp-research-skills/skills/project-onboarding/SKILL.md plus:
- references/existing-project-audit.md
- references/scenario-2-existing-agentic-files.md (sub-case 2.B)
- references/conflict-resolution.md

Read all my existing agent-files. Note any inconsistencies BETWEEN
the files (e.g. CLAUDE.md says X, GEMINI.md says Y, for the same
question) -- surface those for my decision before consolidating.

Then produce a migration plan that:

1. Reconciles inconsistencies (per my decisions).
2. Builds a single per-project AGENTS.md containing the merged
   content.
3. Converts each existing agent-file to a symlink to AGENTS.md.
4. Includes a content-check table covering every line of every
   original file.

Do NOT make any changes until I review the plan + content-check
table.
```

### Prompt 2.C: existing agent-file with substantive project content

```text
I have an existing project at <path> with a <CLAUDE.md / etc.>
that contains substantive project-specific content (project facts,
in-progress decisions, conventions, open questions) -- NOT just
generic agent rules. I have spent time on it; I want every piece
of that content preserved + migrated to the right destination in
the scicomp-research-skills framework.

This is a <paper / software-library> project.

Load the project-onboarding skill from
~/.scicomp-research-skills/skills/project-onboarding/SKILL.md plus:
- references/existing-project-audit.md
- references/scenario-2-existing-agentic-files.md (sub-case 2.C)
- references/conflict-resolution.md

Read my existing agent-file IN FULL. For every section / paragraph,
classify by destination:

- per-project AGENTS.md "Project facts" section -> for project-
  specific facts the agent should not have to derive.
- per-project AGENTS.md "Project-specific overrides" section -> for
  conventions deviating from the framework's universal rules.
- PLAN.md Headline Contribution / Section 1 / Section 7 / Section
  11 (Open Questions) -> for plan-of-record content.
- notes/section_<N>.md or notes/impl_<component>.md -> for working
  notes.
- DROP (with explanation) -> only for content fully subsumed by
  framework universal conventions.

Produce a migration plan that includes the destination for EVERY
line of the original. Use a content-check table:

| Original lines | Content (excerpt) | Destination | Status |
|:---|:---|:---|:---|
| 5-8 | "Closest competitor: Shen 2023..." | PLAN.md Headline Contribution: Positioning | migrated |
| ... | ... | ... | ... |

Total lines accounted for must equal the total lines in the
original. If any line lacks a destination, flag it for my decision
before proceeding.

Do NOT make any changes until I review the content-check table +
approve the plan.
```

### Prompt 2.D: conflicting conventions

Use this AFTER the audit has surfaced a conflict (Scenario 2 prompts
above will surface conflicts as part of the audit; use this prompt
to resolve them once they're surfaced):

```text
The audit has surfaced one or more conflicts between my existing
project conventions and the scicomp-research-skills framework's
universal conventions.

Load the project-onboarding skill's
references/conflict-resolution.md.

For each conflict, present:
1. The framework rule (cited verbatim from root AGENTS.md
   Section 6).
2. The project rule (cited from wherever it appeared).
3. The specific situation where they disagree.
4. The three resolution options: (a) adopt framework rule, (b)
   adopt project rule + record in "Project-specific overrides",
   (c) compromise + document.

Wait for my decision per conflict. Do NOT silently pick a side.

After I've decided on each conflict, update the per-project
AGENTS.md "Project-specific overrides" section per the
conflict-resolution.md template.
```

---

## Common follow-up prompts

After a successful migration, the user often wants to do one of the
following. These prompts are independent of the migration but flow
naturally from it.

### Verify the migration succeeded

```text
Run the project-onboarding skill's universal workflow Step 4
(verification) on this project. Confirm:

- AGENTS.md exists, is readable, and follows the per-project
  template structure.
- PLAN.md exists, is readable, and is populated (not just
  placeholders).
- All cross-references in AGENTS.md / PLAN.md / notes/README.md
  resolve.
- No personal-path leaks in any tracked file (no /Users/<...>,
  no project-author-specific paths).
- pre-commit hooks pass (if applicable).
- shellcheck passes on any shell scripts (if applicable).
- The repo passes Scientific Python repo-review (for software
  projects only).

Report what passes + what fails + any quick fixes for the failures.
```

### Document the migration in agent_feedback

```text
Append an entry to notes/agent_feedback.md summarising this
onboarding session per the agent-resource-discipline skill's
recording protocol. Include:

- What worked smoothly.
- What required workarounds (in particular, any conflicts that had
  to be surfaced + resolved).
- What gaps in the project-onboarding skill the migration
  revealed.
- Any feedback worth rolling up to the upstream
  scicomp-research-skills repository (per CONTRIBUTING.md).

Mention the entry in your response so I can review it before the
session ends.
```

### Run the first-action protocol on the migrated project

```text
Run the agent-resource-discipline skill's first-action protocol on
this project. Read AGENTS.md + PLAN.md + references/_collection_log.md
+ notes/README.md (in parallel) and report the project's current
state. This verifies that the migration produced a state the
framework's first-action protocol can actually consume.
```

---

## Cross-references

- `SKILL.md` (this skill's main file) -- the workflow these prompts
  invoke.
- `references/existing-project-audit.md` -- the audit step every
  prompt's first action invokes.
- `references/scenario-1-no-agentic-work.md` -- where Scenario 1
  prompts ultimately route the agent.
- `references/scenario-2-existing-agentic-files.md` -- where
  Scenario 2 prompts ultimately route the agent.
- `references/conflict-resolution.md` -- where Prompt 2.D
  ultimately routes the agent.
- Root `README.md` "Adopting on an existing project" -- user-
  facing summary that points at this file.

---

*Created 2026-05-13 by A. Attia.*
