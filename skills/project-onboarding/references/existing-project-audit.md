# Existing-project audit

Loaded on demand from the `project-onboarding` skill at the start of
any onboarding session, regardless of whether the user is in
Scenario 1 or Scenario 2. The audit is the **inventory-before-acting**
step that produces the migration plan.

The audit is read-only. Nothing gets written, moved, or deleted until
after the user has reviewed + approved the plan.

---

## What to audit

Before writing anything, the agent should produce a structured
inventory covering five areas. Each area maps to a specific question
the migration plan must answer.

### 1. Project type + audience

**Question to answer**: which template does this project most
resemble (`paper-skeleton/` vs `software-skeleton/`)? What's the
target template?

**Inventory commands**:

```bash
# What kind of files dominate?
find . -type f -not -path './.git/*' \
  | sed 's|.*\.||' | sort | uniq -c | sort -rn | head -20

# Is this a Python package?
ls -la pyproject.toml setup.py setup.cfg requirements*.txt 2>&1 | grep -v "No such"

# Is this a paper draft?
ls -la *.tex drafts/*.tex paper/*.tex *.md 2>&1 | grep -v "No such" | head

# Is there an existing experiments / runs / outputs structure?
ls -la experiments/ runs/ outputs/ results/ 2>&1 | grep -v "No such"
```

**Output**: one-line classification: `paper` / `software-library` /
`software-script-collection` / `analysis-notebook-collection` /
`mixed`.

### 2. Existing layout vs framework's expected layout

**Question to answer**: which directories already exist that the
framework expects? Which framework-expected directories are missing?
Which existing directories conflict with framework conventions?

**Inventory** -- compare existing layout vs the relevant template's
layout:

```bash
# What top-level structure exists?
ls -la .

# What's in the obvious framework-related subdirs?
ls -la references/ notes/ experiments/ figures/ drafts/ src/ tests/ docs/ 2>&1
```

For each framework-expected directory (paper-skeleton or
software-skeleton, depending on Step 1's classification), categorise
it as:

- **Already exists, same role** -- framework-expected name + content
  fits framework's expectation. No action needed.
- **Already exists, different role** -- name collision but content
  is for a different purpose. Flag for the user; propose rename
  during plan stage.
- **Already exists, partially fits** -- name matches but content is
  a subset / superset of framework's expectation. Propose merge plan.
- **Doesn't exist** -- need to create from template. Easiest case.

### 3. Existing agentic instructions

**Question to answer**: does this project already have agent-facing
files? If so, what are they + what content do they contain?

**Inventory commands**:

```bash
# Check for the canonical agent files at repo root.
ls -la AGENTS.md AGENT.md CLAUDE.md GEMINI.md .cursorrules CONVENTIONS.md 2>&1 | grep -v "No such"

# Look for OpenCode / Cursor / etc. specific config dirs.
ls -la .opencode/ .cursor/ .claude/ .github/copilot/ 2>&1 | grep -v "No such"

# Look for any *.md files that might be agent-facing
find . -maxdepth 2 -name "*.md" -not -path './.git/*' | head -10
```

**Output**: a table of agent files found, their sizes, and a
one-line characterization of each (generic-rules / project-facts /
mixed / empty-stub).

| File | Size | Characterization | Migration target |
|:---|---:|:---|:---|
| `CLAUDE.md` | 47 lines | mixed (generic Claude rules + 12 lines of project facts) | merge project facts into AGENTS.md "Project facts"; convert remainder to symlink |
| `.cursorrules` | 8 lines | generic only (no project facts) | symlink to AGENTS.md |
| `AGENTS.md` | absent | -- | create from `templates/<which>-skeleton/AGENTS.md` |

If table is empty: this is **Scenario 1** (no prior agentic work).
If table has rows: this is **Scenario 2** (existing agentic
instructions); load `scenario-2-existing-agentic-files.md` next.

### 4. Existing project-of-record / planning docs

**Question to answer**: does this project already have a PLAN.md /
ROADMAP.md / TODO.md / NOTES.md / project-spec doc? Its content is
the seed for the migrated `PLAN.md`.

**Inventory commands**:

```bash
ls -la PLAN.md ROADMAP.md TODO.md NOTES.md DESIGN.md SPEC.md 2>&1 | grep -v "No such"
ls -la docs/plan*.md docs/design*.md docs/roadmap*.md 2>&1 | grep -v "No such"

# Existing notes directory?
ls -la notes/ 2>&1
```

**Output**: list of doc files found + one-line role per file.
Map each to the framework's `PLAN.md` + `notes/<type>_<topic>.md`
conventions during plan stage.

### 5. Existing references / bibliography

**Question to answer**: does this project already have references /
PDFs / a bibliography? They become the seed for
`references/bibliography.bib` + `references/_collection_log.md` +
per-paper `notes/survey_<citekey>.md` (paper projects) OR the
`references/_collection_log.md` for algorithm-source citations
(software projects).

**Inventory commands**:

```bash
# Bibliography files?
find . -maxdepth 3 -name "*.bib" -not -path './.git/*'

# PDF stash?
find . -maxdepth 3 -name "*.pdf" -not -path './.git/*' | head -10

# Existing per-paper notes?
ls notes/survey_*.md 2>&1 | grep -v "No such" | head
```

**Output**: count + one-line summary. If references exist, plan to
migrate into the framework's references/ + notes/ structure during
the plan stage; otherwise leave for later when the user actually
adds references.

## The migration plan: what the audit produces

The audit ends with a **migration plan document** -- a temporary file
at `notes/_migration_<YYYYMMDD>.md` (the leading underscore signals
"working file; will be deleted after migration commits").

The plan has six sections, one per audit area + one for the proposed
sequence:

```markdown
# Migration plan -- adopting scicomp-research-skills (YYYY-MM-DD)

## 1. Project classification
<paper / software-library / mixed / ...; chosen target template>

## 2. Layout reconciliation
<table of existing dirs vs framework-expected dirs; per-row decision>

## 3. Agentic-instructions migration
<table of existing agent files; per-file migration target;
 conflicts to surface to user>

## 4. PLAN.md seed
<which existing docs feed the new PLAN.md; per-section mapping>

## 5. References migration
<existing bib + PDFs + survey notes; mapping to framework structure>

## 6. Proposed migration sequence
<numbered list of commits, each one logical step;
 acceptance criterion for each>
```

The plan is presented to the user. The user reviews + approves. ONLY
THEN does the agent start executing.

## Audit-stage anti-patterns to refuse

- **Touching any file before producing the plan.** The audit is
  strictly read-only; the user has not yet approved any writes.
- **Producing a plan without inventorying.** "I'll just copy the
  template and we'll see what conflicts" is the wrong order; we
  inventory first so the conflicts are surfaced before the user
  has to sort them out under time pressure.
- **Proposing destructive moves the user didn't ask for.** "Let me
  delete this old `notes/` directory and replace it with the
  framework's" -- never. Move + merge + flag.
- **Glossing over conflicting conventions.** Conflicts must be in
  the plan + must be raised explicitly in the response message; not
  deferred to "we'll figure it out later".

## Cross-references

- After the audit completes, branch by scenario:
  - Scenario 1 -> load `references/scenario-1-no-agentic-work.md`.
  - Scenario 2 -> load `references/scenario-2-existing-agentic-files.md`
    AND `references/conflict-resolution.md`.
- The plan-stage discipline (review + approve before executing) is
  the same as the universal "no silent action" rule from root
  `AGENTS.md` Section 6.
- The "one commit per logical step" execution discipline mirrors
  the human-facing-doc-authoring skill's authoring workflow (draft
  TOC first, write sections in order, cross-references in a final
  pass).

---

*Created 2026-05-13 by A. Attia.*
