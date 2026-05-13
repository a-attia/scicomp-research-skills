# scicomp-research-skills / AGENTS.md

**You are reading the root `AGENTS.md` of a shared agent-skills
repository.** Read this file first before doing anything else here or in
any project that references it.

This file follows the [agents.md](https://agents.md/) open standard.
Agent clients that look for other filenames (e.g. `CLAUDE.md`) read this
same content via symlinks created by `bin/install.sh`.

---

## 1. What this repository is

This repository holds **agent skills and workflow templates for research
in scientific computing** -- covering both research **papers** (drafts,
literature surveys, reviewer responses) and research **software**
(libraries, codes, reproducibility infrastructure) in domains such as
computational PDEs, inverse problems, optimal experimental design,
uncertainty quantification, optimisation, and scientific machine learning.

The repository exists so that:

- **Conventions are defined once and inherited everywhere.** A
  per-project `AGENTS.md` is short and project-specific; the generic
  conventions live here as **skills** loaded on demand.
- **The same conventions work across multiple agent clients** -- OpenCode,
  Claude Code, Codex, Cursor, Aider, Gemini CLI, etc. Any client that
  reads markdown can consume this repository.
- **The same conventions work across multiple machines.** A canonical
  checkout at `~/.scicomp-research-skills/` on each machine is refreshed
  via `git pull`; one source of truth.
- **Updates are versioned.** Every change to a convention or skill is a
  commit with a message; `git log` shows when and why.

This repository **starts from upstream
[Master-cai/Research-Paper-Writing-Skills](https://github.com/Master-cai/Research-Paper-Writing-Skills)**
(MIT-licensed) and intentionally diverges to broaden scope. See
`ATTRIBUTION.md` for the full lineage.

## 2. Local layout (per machine)

Two checkouts of this repository exist on each machine:

- **Development checkout**: anywhere EXCEPT `~/.scicomp-research-skills/`
  (a common convention is to keep it under your usual code-projects
  directory).
  - This is where edits + commits happen.
  - Other research projects + agents on the machine **ignore** this
    checkout completely.
  - Push from here to the GitHub remote when changes are ready.
- **Canonical checkout**:
  `~/.scicomp-research-skills/`
  - Read-only from the user's perspective; refreshed via
    `~/.scicomp-research-skills/bin/refresh.sh`
    (or `git -C ~/.scicomp-research-skills pull --ff-only`).
  - This is the location that agents read from.
  - A pre-commit hook (in `.githooks/pre-commit`) refuses commits in this
    checkout, so accidental edits cannot be committed back.
  - Per-project `AGENTS.md` files reference paths like
    `~/.scicomp-research-skills/skills/<name>/SKILL.md`.

Set up the canonical checkout on a fresh machine via:

```bash
git clone git@github.com:a-attia/scicomp-research-skills.git ~/.scicomp-research-skills
~/.scicomp-research-skills/bin/install.sh
```

## 3. How agents should consume this repository

When an agent is given a project that references this repository, the
agent's reading order is:

1. Read this root `AGENTS.md` (you are here).
2. Read any skill the project's `AGENTS.md` directs you to. Skills are
   loaded **on demand**, not all at once -- see Section 5.
3. Read the project's own `AGENTS.md` for project-specific overrides /
   facts.
4. Read the project's `PLAN.md` (or equivalent plan-of-record) if one
   exists; this is typically the project's content contract.
5. Then proceed with the user's request.

**Universal rule**: when in doubt, the project's `AGENTS.md` and `PLAN.md`
override any conflicting guidance from this repository. This repository
provides defaults; projects own their specifics.

### OpenCode-specific consumption

OpenCode supports referencing remote instructions natively via
`opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": [
    "https://raw.githubusercontent.com/a-attia/scicomp-research-skills/main/AGENTS.md"
  ]
}
```

Skill files are auto-discovered by OpenCode at
`~/.config/opencode/skills/<name>/SKILL.md` and the Claude-compatible
fallback `~/.claude/skills/<name>/SKILL.md`. The simplest deployment is
a symlink:

```bash
ln -s ~/.scicomp-research-skills/skills ~/.config/opencode/skills
# or, for Claude Code compatibility:
ln -s ~/.scicomp-research-skills/skills ~/.claude/skills
```

After symlinking, OpenCode's `skill` tool will list the skills here as
loadable on demand.

## 4. Versioning + refresh protocol

- **Refresh is manual.** Run `~/.scicomp-research-skills/bin/refresh.sh`
  (which does `git fetch && git pull --ff-only`) when you want to pick up
  updates.
- **Staleness check.** Per-project `AGENTS.md` files instruct the agent
  to check the modification time of `~/.scicomp-research-skills/AGENTS.md`
  and print a reminder if it has not been refreshed in more than N days
  (default: 30). The reminder is informational; the agent proceeds
  without blocking.
- **Date-stamping.** Every skill file ends with a date-stamp footer
  noting when it was last revised. Agents should mention the date-stamp
  of any skill they load when they cite that skill in their response.
- **Compatibility.** When breaking changes to a skill are made, the
  file's date-stamp footer notes the breaking change explicitly.
  Per-project `AGENTS.md` files MAY pin a specific commit of this
  repository if they cannot tolerate unannounced changes.

## 5. Skills index

Each skill below lives at `skills/<name>/SKILL.md` with YAML frontmatter
following the [OpenCode skills](https://opencode.ai/docs/skills/) and
[Anthropic skills](https://docs.anthropic.com/en/docs/build-with-claude/agent-skills)
conventions. Skills are loaded **on demand** by per-project `AGENTS.md`
files, not automatically.

| Skill                       | Purpose                                                                                                  | Origin                          |
|:----------------------------|:---------------------------------------------------------------------------------------------------------|:--------------------------------|
| `skills/research-paper-writing/`  | Section-by-section paper drafting, paragraph-clarity check, claim-evidence alignment, adversarial review. | upstream (Master-cai)         |
| `skills/literature-survey/` | bibtex + PDF + pdftotext + per-paper survey-note + collection-log workflow for heavy-literature papers.   | added here                      |

When new skills are added, append a row to this table.

### Templates index

Templates in `templates/` are starter scaffolds for new projects -- copy
into a fresh project directory and customise.

| Template                       | Purpose                                                                  |
|:-------------------------------|:-------------------------------------------------------------------------|
| `templates/paper-skeleton/`    | Starter files for a new scientific-computing paper repo: PLAN.md skeleton, README.md skeleton, .gitignore, references/ structure stub, notes/README.md skeleton. |

## 6. Universal conventions

These conventions apply unless a per-project `AGENTS.md` explicitly
overrides them.

- **Encoding**: ASCII only in code, code comments, and code-style
  docstrings. Markdown documentation MAY use non-ASCII for readability
  (em-dashes, math symbols rendered via MathJax). Code remains ASCII.
- **Math notation**: prefer LaTeX inside markdown via MathJax (`$...$`
  for inline, `$$...$$` for display). Avoid ASCII-art math in production
  documentation.
- **Date-stamping**: every plan-of-record-style document (PLAN.md,
  AGENTS.md, any skill file) ends with a `*Created YYYY-MM-DD. Revised
  YYYY-MM-DD (note about the revision). Maintained by <name>.*` footer.
- **Code references**: when citing a specific function or block in code,
  use `path/to/file:line_number` format so the user can navigate
  directly.
- **No emojis**: in code, code comments, code docstrings, and production
  documentation, unless the user explicitly requests them.
- **Commit messages**: no `Co-Authored-By` trailers. Conventional commit
  style preferred (`feat: ...`, `fix: ...`, `docs: ...`) but not
  enforced.
- **No unilateral commits**: agents do not create git commits unless the
  user explicitly requests it.

## 7. Per-project AGENTS.md boilerplate

Per-project `AGENTS.md` files should be short (target ~50-100 lines)
and follow the canonical template kept in this repository at:

- `templates/paper-skeleton/AGENTS.md` -- the canonical per-project
  AGENTS.md boilerplate (currently paper-flavoured; the structure
  generalises to software projects too).

When the user asks "how do I start a new project that uses this
repository", point them at Section 11 of this file ("Starting a new
project") and copy `templates/paper-skeleton/` to bootstrap.

The template is the single source of truth for the boilerplate. If you
need to update the boilerplate (e.g. add a new skill to load), edit the
template; do NOT copy-paste the boilerplate into multiple places.

## 8. How to add a new skill

1. Create `skills/<skill-name>/SKILL.md` in the **dev checkout**.
2. The skill file should:
   - Open with **YAML frontmatter** (required: `name`, `description`;
     optional: `license`, `compatibility`, `metadata`).
   - State when to load it (so per-project `AGENTS.md` authors know when
     to reference it).
   - Be self-contained (do not assume other skills are loaded unless
     explicitly stated).
   - Optionally include a `references/` subfolder for section-specific or
     deep-dive material loaded on demand from within the skill itself.
   - End with a date-stamped revision footer.
3. Append a row to the skills index table in this AGENTS.md (Section 5).
4. Commit + push from the dev checkout.
5. On any machine that needs the new skill, run
   `~/.scicomp-research-skills/bin/refresh.sh`.

### Skill name validation rules (from OpenCode skills spec)

- 1-64 characters
- lowercase alphanumeric with single hyphen separators
- not start or end with `-`
- no consecutive `--`
- match the directory name

Equivalent regex: `^[a-z0-9]+(-[a-z0-9]+)*$`

### Skill description rules

- 1-1024 characters
- specific enough for the agent to choose correctly when listing
  available skills

## 9. How to add a new template

1. Create `templates/<template-name>/` in the dev checkout.
2. Populate with the starter files.
3. Append a row to the templates table in Section 5.
4. Commit + push.

## 10. License

MIT. See `LICENSE` for the upstream copyright (Master-cai 2026); see
`ATTRIBUTION.md` for our additions (also MIT, A. Attia 2026).

## 11. Starting a new project

When a user asks "I'm starting a new <paper / software / reviewer
response>; how do I wire in this repository?", the agent should walk the
user through the steps below. The exact sequence depends on project type.

### 11.A New research paper

The canonical workflow. Templates and skills are paper-ready today.

1. **Create the project directory** (anywhere convenient; typically a
   sibling of any code dependencies it references):
   ```bash
   mkdir -p <papers-parent-dir>/<paper-short-name>
   cd <papers-parent-dir>/<paper-short-name>
   git init
   ```
2. **Copy the paper-skeleton template** from the canonical checkout:
   ```bash
   cp -R ~/.scicomp-research-skills/templates/paper-skeleton/. .
   ```
   This brings in `AGENTS.md`, `PLAN.md`, `README.md`, `.gitignore`,
   `references/{bibliography.bib, _collection_log.md}`, `notes/README.md`,
   and `.gitkeep`s for `experiments/`, `figures/`, `drafts/`.
3. **Customise the four `<...>` placeholders**:
   - `AGENTS.md` -- fill in project name, nature, status, target venue,
     code dependencies, citation style, collaborators.
   - `PLAN.md` -- fill in the working title, headline contribution,
     test case, hypothesis, survey reading list (start with stubs;
     refine via the `literature-survey` skill).
   - `README.md` -- fill in title, authors, target submission, pinned
     upstream library versions, status.
   - `notes/README.md` -- fill in the section topics matching your
     PLAN.md sections.
4. **Verify the agent will load the skills**. From inside the project:
   ```bash
   ls ~/.scicomp-research-skills/AGENTS.md      # should exist
   ls ~/.scicomp-research-skills/skills/        # should list both skills
   ```
   If the canonical checkout is missing or stale, run
   `~/.scicomp-research-skills/bin/refresh.sh` (or `install.sh` if it
   has never been set up on this machine).
5. **First commit**:
   ```bash
   git add .
   git commit -m "chore: bootstrap from scicomp-research-skills/templates/paper-skeleton"
   ```
6. **Open the project in your agent client**. The agent will read
   `AGENTS.md` first, follow it to `~/.scicomp-research-skills/AGENTS.md`,
   then load the skills referenced (`research-paper-writing`,
   `literature-survey`) on demand as the work proceeds.

A typical first session asks the agent to:

- run the `literature-survey` skill workflow on the first batch of
  references (Steps 1-5 of that skill produce the verified bib entries +
  per-paper survey notes);
- then use the `research-paper-writing` skill to draft Section 1
  (Introduction) once the survey notes for the closest competitors are
  in place.

### 11.B New research software project

A dedicated `templates/software-skeleton/` is **not yet shipped**. Until
it is, the recommended approach is:

1. Use your normal language-/framework-specific scaffolding (e.g.
   `cookiecutter`, `cargo new`, `uv init`, etc.) to create the project.
2. Hand-write a short `AGENTS.md` modelled on
   `~/.scicomp-research-skills/templates/paper-skeleton/AGENTS.md`:
   - Same Section 1-3 boilerplate (verify, read root AGENTS.md, read
     skills, then read this file).
   - Skills-to-load list will likely be EMPTY for now (the existing
     skills are paper-flavoured); add skills as we ship software-flavoured
     ones.
   - `## Project facts` should describe the library (language, public
     API surface, primary downstream consumers, current release).
3. Hand-write a `PLAN.md` modelled on
   `~/.scicomp-research-skills/templates/paper-skeleton/PLAN.md` but
   reorganised around code milestones (M1 = bootstrap + CI, M2 = core
   API, M3 = first user, ...) instead of paper milestones.
4. Open an issue against this repository requesting a
   `templates/software-skeleton/` (one of the planned future additions).

### 11.C Reviewer response / rebuttal

Also not yet shipped as a dedicated template. Recommended interim:

1. Create a sub-directory inside the existing paper repo:
   `<paper-repo>/rebuttal_<round>/`.
2. Hand-write a short `AGENTS.md` that loads the parent paper's
   AGENTS.md plus the `research-paper-writing` skill (specifically the
   `paper-review.md` reference, which covers reviewer-facing concerns).
3. A dedicated `templates/rebuttal-skeleton/` is on the roadmap.

### Roadmap of templates

Items expected to be added to `templates/` over time:

- `software-skeleton/` -- minimal Python research-software project
  skeleton (`pyproject.toml`, `src/`, `tests/`, `docs/`, AGENTS.md,
  PLAN.md tuned to code milestones).
- `rebuttal-skeleton/` -- reviewer-response workspace (response.md,
  diff-tracking, line-by-line response template).
- `experiment-skeleton/` -- standalone experiment / ablation workspace
  (separate from a paper repo, e.g. for exploratory work that may or
  may not become a paper).

When you ship one of these, append it to the templates index in
Section 5 and add a corresponding sub-section to Section 11 above.

---

*Created 2026-05-13 by clone-and-diverge from Master-cai/Research-Paper-Writing-Skills @ 9ee5edd. Revised 2026-05-13 (post-audit cleanup: removed orphan upstream agent config, dual-licensed LICENSE, single-sourced per-project boilerplate via templates/paper-skeleton/AGENTS.md, added Section 11 "Starting a new project"). Maintained by A. Attia.*
