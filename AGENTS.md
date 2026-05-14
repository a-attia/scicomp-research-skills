# scicomp-research-skills / AGENTS.md

**You are reading the root `AGENTS.md` of a shared agent-skills
repository.** Read this file first before doing anything else here or in
any project that references it.

This file follows the [agents.md](https://agents.md/) open standard.
Agent clients that look for other filenames (e.g. `CLAUDE.md`) read this
same content via symlinks created by `bin/install.sh`.

> **PROVISIONAL FRAMEWORK** (as of 2026-05-14): some skill content
> here is well-grounded (research-paper-writing, literature-survey,
> paper-skeleton template); other skill content is informed prediction
> from prior-art audits but **has not yet been validated by any real
> research-project session**. When a rule feels speculative or
> doesn't quite fit the situation, **surface that to the user
> explicitly** + append an entry to the project's
> `notes/agent_feedback.md` (per
> `agent-resource-discipline/references/persistent-memory.md`). See
> [`STATUS.md`](STATUS.md) at the repo root for the honest map of
> what is tested vs speculative.

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

Set up the canonical checkout on a fresh machine via (try SSH first;
fall back to HTTPS if SSH keys are not configured for GitHub):

```bash
git clone git@github.com:a-attia/scicomp-research-skills.git ~/.scicomp-research-skills \
  || git clone https://github.com/a-attia/scicomp-research-skills.git ~/.scicomp-research-skills
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

| Skill                              | Purpose                                                                                                  | Origin                  |
|:-----------------------------------|:---------------------------------------------------------------------------------------------------------|:------------------------|
| `skills/research-paper-writing/`   | Section-by-section paper drafting, paragraph-clarity check, claim-evidence alignment, adversarial review. | upstream (Master-cai)  |
| `skills/literature-survey/`        | bibtex + PDF + pdftotext + per-paper survey-note + collection-log workflow for heavy-literature papers.   | added here              |
| `skills/human-facing-doc-authoring/` | Author or revise any human-facing project doc (README.md, PLAN.md, survey notes, collection logs, rebuttal drafts) -- audience split, two-tier structure, cross-references. | added here |
| `skills/agent-resource-discipline/` | Reduce token / quota / context-window consumption + improve cross-session memory (tool selection, parallelism, targeted reads, PDF lifecycle, persistent-memory protocol, context-window budget, web-fetch caching). | added here |
| `skills/research-software-engineering/` | Methodology for AI-assisted scientific-computing software development -- numerical correctness (MMS / convergence-rate tests / "paper tests" guard), testing strategies for numerical code, API design for researchers, reproducibility infra, code-paper coupling, plus the Bridgeford et al. 2025 ten rules condensed agent-actionably. | added here |
| `skills/project-onboarding/` | Adopt the framework on an EXISTING project (rather than starting from scratch). Covers two scenarios -- (1) no prior agentic work; (2) existing AGENTS.md / CLAUDE.md / .cursorrules / etc. -- with worked examples, an inventory-before-acting audit procedure, and a conflict-resolution mechanism for when project conventions disagree with framework universal conventions. | added here |

When new skills are added, append a row to this table.

### Templates index

Templates in `templates/` are starter scaffolds for new projects -- copy
into a fresh project directory and customise.

| Template                       | Purpose                                                                  |
|:-------------------------------|:-------------------------------------------------------------------------|
| `templates/paper-skeleton/`    | Starter files for a new scientific-computing paper repo: AGENTS.md (per-project entry; loads paper-writing + literature-survey + human-facing-doc-authoring + agent-resource-discipline + project-onboarding-on-demand), PLAN.md (paper plan-of-record skeleton with reading-list + test-case + experiment-protocol + paper-outline sections), README.md (human-facing project description), CITATION.cff (for the supporting code/data repo, distinct from the paper's own DOI; Zenodo handshake instructions baked in), .gitignore, references/{bibliography.bib, _collection_log.md} stubs, notes/{README.md, agent_feedback.md}, experiments/README.md (per-run snapshot discipline including metadata.json schema), figures/README.md (figure-generation provenance + per-figure README convention), .github/ISSUE_TEMPLATE/{reviewer-comment-followup, experiment-rerun-needed, figure-update-needed}.md (paper-flavoured issue templates), .gitkeep stubs for experiments/ + figures/ + drafts/. |
| `templates/software-skeleton/` | Starter files for a new scientific-computing software project. Paper-coupling layer (AGENTS.md, PLAN.md, README.md, CITATION.cff with Zenodo handshake, .gitignore, experiments/README.md per-run snapshot discipline, figures/README.md provenance, notes/README.md, references/_collection_log.md, .github/ISSUE_TEMPLATE/{numerical-correctness-regression, api-ergonomics, performance-regression}) is **language-agnostic**. Package layer (build manifest, src/, tests/, docs/, CI configs) is delegated by bootstrap.sh to one of: scientific-python/cookie (BSD-3, Python, default) / NLeSC/python-template (Apache-2.0, Python, FAIR-aware) / CU-DBMI/template-uv-python-research-software (BSD-3, Python, uv-first) / JuliaBesties/BestieTemplate.jl (MPL-2.0, Julia). For C++ / Rust / Fortran / MATLAB / Mathematica: no upstream is bundled; see `templates/software-skeleton/MULTI-LANGUAGE.md` for the per-language placeholder-translation table -- the paper-coupling layer applies regardless of language. |

## 6. Universal conventions

These conventions apply unless a per-project `AGENTS.md` explicitly
overrides them. Grouped by topic for scanability; the rules within
each group are independent.

### 6.1 Code style + content encoding

- **Encoding**: ASCII only in code, code comments, and code-style
  docstrings. Markdown documentation MAY use non-ASCII for readability
  (em-dashes, math symbols rendered via MathJax). Code remains ASCII.
- **Math notation**: prefer LaTeX inside markdown via MathJax (`$...$`
  for inline, `$$...$$` for display). Avoid ASCII-art math in production
  documentation.
- **No emojis**: in code, code comments, code docstrings, and production
  documentation, unless the user explicitly requests them.
- **Code references**: when citing a specific function or block in code,
  use `path/to/file:line_number` format so the user can navigate
  directly.

### 6.2 Document hygiene

- **Date-stamping**: every plan-of-record-style document (PLAN.md,
  AGENTS.md, any skill file) ends with a `*Created YYYY-MM-DD. Revised
  YYYY-MM-DD (note about the revision). Maintained by <name>.*` footer.
  Exception: upstream-vendored content keeps its own provenance + does
  not get fake revision footers (see e.g. the note in
  `skills/research-paper-writing/SKILL.md` "Note on this skill's
  references/ files").
- **Human-facing vs agent-facing docs**: every project keeps two
  parallel families of documents with explicitly different audiences.
  **Agent-facing** (`AGENTS.md`, per-skill `SKILL.md` files) are
  telegraphic, structured, machine-parseable. **Human-facing**
  (`README.md`, `PLAN.md`, `notes/survey_*.md`,
  `references/_collection_log.md`, `notes/section_*.md`,
  `notes/impl_*.md`, rebuttal drafts, ...) are narrative, indexed,
  date-stamped where appropriate, and designed to be scanned. Do NOT
  treat human-facing docs as downstream renderings of `AGENTS.md`;
  they have different jobs. **Whenever the agent will produce or
  substantially revise a document a human is expected to read for
  review or reference, load the `human-facing-doc-authoring`
  skill** -- it codifies the universal conventions and points at
  per-doc-type structural skeletons.

### 6.3 Git + commit discipline

- **Commit messages**: no `Co-Authored-By` trailers. Conventional commit
  style preferred (`feat: ...`, `fix: ...`, `docs: ...`) but not
  enforced.
- **No unilateral commits**: agents do not create git commits unless the
  user explicitly requests it.

### 6.4 Agent tool discipline

- **Tool selection**: prefer dedicated tools over Bash equivalents.
  Use `Read` (not `cat`/`head`/`tail`), `Grep` (not `bash grep`/`rg`),
  `Glob` (not `find`/`ls -R`), `Edit` (not `sed`/`awk`), `Write` (not
  `cat <<EOF`/`echo >`). Reserve Bash for actual shell operations
  (git, package managers, build systems). Communicate with the user
  via response text, never via `echo`/`printf`.
- **Parallelism**: when several tool calls are independent (e.g.
  reading three files; greping for three patterns), batch them into a
  single message. Serialise only when one call's output feeds another.
- **Read targeted, not bulk**: for files >300 lines, use `Read` with
  explicit `offset`+`limit`, or `Grep` first to locate the relevant
  section, before `Read`-ing the whole file. The default 2000-line
  limit is for skimming, not for routine consumption.

### 6.5 Memory + persistence (across turns + across sessions)

- **Re-use prior work before generating new work**: before reading a
  source PDF or paper for the second time (this session OR a future
  session), check whether `notes/survey_<citekey>.md` already
  summarises it. Read the survey note first; only fall back to the
  PDF / `.txt` extraction when the note doesn't answer the question.
  Generalises: before re-deriving any fact, check whether an audit
  log / notes file / PLAN.md section already records it.
- **Persistent memory across sessions**: the project's indices
  (`PLAN.md` status, `references/_collection_log.md`,
  `notes/README.md`) ARE the persistent memory between agent sessions.
  Read them at the start of any non-trivial session; update them at
  the end of any session that produced new work. **When heavy
  reading, searching, PDF handling, or web fetching is anticipated,
  load the `agent-resource-discipline` skill** for the full
  resource-budget protocol (PDF lifecycle, web-fetch caching,
  context-window budget, ...).

### 6.6 Upstream feedback channel

- **Upstream feedback channel**: every project bootstrapped from
  `templates/paper-skeleton/` OR `templates/software-skeleton/` ships
  with a `notes/agent_feedback.md` file. Append an entry there
  whenever a skill rule was insufficient, a workaround was needed, or
  a useful pattern was discovered (full trigger list + entry format
  in `agent-resource-discipline/references/persistent-memory.md`).
  Mention every entry you append in your response to the user. The
  file is the per-project channel that feeds the upstream
  `scicomp-research-skills` repo's improvement loop (roll-up
  procedure in CONTRIBUTING.md).

## 7. Per-project AGENTS.md boilerplate

Per-project `AGENTS.md` files should be short (target ~50-150 lines;
software projects with multi-skill loadouts + citation policy may
reach the upper end) and follow one of the canonical templates kept
in this repository:

- `templates/paper-skeleton/AGENTS.md` -- canonical for **paper**
  projects (~80 lines; loads paper-writing + literature-survey +
  human-facing-doc-authoring + agent-resource-discipline +
  project-onboarding-on-demand).
- `templates/software-skeleton/AGENTS.md` -- canonical for
  **software** projects (~140 lines; loads research-software-
  engineering + agent-resource-discipline + human-facing-doc-
  authoring + literature-survey + research-paper-writing-on-demand
  + project-onboarding-on-demand; includes a "Citation + archival
  policy" section + Python defaults flagged with cross-reference
  to MULTI-LANGUAGE.md).

Both templates share the same overall structure: Sections 1-3
boilerplate (verify canonical checkout / read root AGENTS.md / load
skills); skills-to-load list (with `### Available but not loaded by
default` subsection for project-onboarding); Project facts;
Project-specific overrides; Project-specific facts the agent should
not have to derive; date-stamp footer.

When the user asks "how do I start a new project that uses this
repository", point them at Section 11 of this file ("Starting a new
project") and copy the matching template (`templates/paper-skeleton/`
for papers, `templates/software-skeleton/` for software).

These two templates are the single source of truth for the
boilerplate. If you need to update the boilerplate (e.g. add a new
skill to load, change a section heading), edit BOTH templates +
keep them in sync; do NOT copy-paste the boilerplate into ad-hoc
locations.

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

The canonical workflow for a research-software library / code. Templates
and skills are software-ready as of 2026-05-13.

1. **Create the project directory** (anywhere convenient; typically a
   sibling of any paper repos that will depend on this code):
   ```bash
   mkdir -p <code-parent-dir>/<library-short-name>
   cd <code-parent-dir>/<library-short-name>
   git init
   ```
2. **Copy the software-skeleton template** from the canonical checkout:
   ```bash
   cp -R ~/.scicomp-research-skills/templates/software-skeleton/. .
   ```
   This brings in `AGENTS.md`, `PLAN.md`, `README.md`, `CITATION.cff`,
   `.gitignore`, `experiments/README.md` + `.gitkeep`,
   `figures/README.md` + `.gitkeep`, `notes/README.md` +
   `notes/agent_feedback.md`, `references/_collection_log.md`, and
   `.github/ISSUE_TEMPLATE/` with three issue templates
   (numerical-correctness-regression, api-ergonomics,
   performance-regression). Plus the `bootstrap.sh` script that runs
   the package-scaffolding step (next).
3. **Run `bootstrap.sh`** to add the package layer (build manifest,
   src/, tests/, docs/, CI configs, pre-commit / equivalent linters).
   The script delegates to one of four bundled upstream community
   templates -- pick the one matching your language + style:
   ```bash
   # Python (default; best-supported):
   ./bootstrap.sh cookie    # scientific-python/cookie (BSD-3)
   ./bootstrap.sh nlesc     # NLeSC/python-template (Apache-2.0; FAIR-aware)
   ./bootstrap.sh uv-cu     # CU-DBMI/template-uv-python-research-software (BSD-3; uv-first)

   # Julia:
   ./bootstrap.sh julia     # JuliaBesties/BestieTemplate.jl (MPL-2.0)

   # C++ / Rust / Fortran / MATLAB / Mathematica:
   # No upstream is bundled. Use your community's standard scaffolding
   # (cmake init / cargo new / fpm new / etc.). The paper-coupling
   # layer in this template (AGENTS.md / PLAN.md / experiments/ /
   # figures/ / notes/ / references/ / CITATION.cff) applies regardless
   # of language. See templates/software-skeleton/MULTI-LANGUAGE.md
   # for the per-language placeholder-translation table.
   ```
   Bootstrap requires `copier` (`pipx install copier` or
   `uv tool install copier`). The upstream template will run
   interactively, asking for project name, author, license choice, etc.
   When it asks about overwriting any of the files we already provided
   (AGENTS.md, PLAN.md, README.md, CITATION.cff, experiments/, figures/,
   notes/, references/, .github/ISSUE_TEMPLATE/), **always keep our
   versions**; the upstream template should only add the package layer.
4. **Customise the four files containing `<...>` placeholders**:
   - `AGENTS.md` -- fill in library name, language + framework choices,
     mathematical conventions, status, code dependencies, paper coupling
     (if applicable).
   - `PLAN.md` -- fill in headline goal, scope + non-scope, public API
     surface, architecture, milestones, numerical-correctness plan,
     reproducibility infrastructure, design-decisions log, lifecycle
     stage.
   - `README.md` -- fill in install + quick example + how-experiments-
     are-organised + coupled-paper (if applicable) + pinned-dependencies
     + citation + authors.
   - `CITATION.cff` -- fill in title, abstract, author list, version,
     repository URL, license. Run the Zenodo handshake (instructions
     baked into the file as comments).
5. **Verify the canonical checkout is fresh** (one-time per machine):
   ```bash
   ~/.scicomp-research-skills/bin/refresh.sh
   ```
6. **Verify Scientific Python repo-review** passes (catches missing
   pyproject fields, missing pre-commit, etc.):
   ```bash
   uvx sp-repo-review[cli] .
   ```
7. **First commit**:
   ```bash
   git add .
   git commit -m "chore: bootstrap from scicomp-research-skills/templates/software-skeleton/ + <chosen-upstream> upstream"
   ```

Now open the project in your agent client. The agent will:

1. Read the project's `AGENTS.md`.
2. Follow it to `~/.scicomp-research-skills/AGENTS.md` for shared
   conventions.
3. Load `skills/research-software-engineering/` (the primary skill for
   software work) on demand. For numerical-correctness work, load
   `references/01-numerical-correctness.md`. For test design, load
   `references/02-testing-for-numerical-code.md`. For AI-assisted-
   coding rules, load `references/11-ai-assisted-coding-rules.md`.
4. Load `skills/agent-resource-discipline/` always (any non-trivial
   software session benefits from the first-action / last-action
   protocols).
5. Load `skills/human-facing-doc-authoring/` whenever touching
   README.md / PLAN.md / notes/ / experiments/README.md /
   figures/README.md.
6. Load `skills/literature-survey/` when adding a new algorithmic
   reference cited in code.
7. Load `skills/research-paper-writing/` only if this code is supporting
   a paper draft AND the draft is also being touched in the session.

A typical first session asks the agent to:

- run the M1 bootstrap (verify the package scaffold, get the test suite
  green, get pre-commit green);
- design the first numerical method in `notes/impl_<component>.md`
  (per the `human-facing-doc-authoring` notes-structures skeleton +
  the `research-software-engineering` API-design principles);
- implement the method TDD-style with MMS + convergence-rate tests
  (per `research-software-engineering/references/02-testing-for-numerical-code.md`).

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

- `rebuttal-skeleton/` -- reviewer-response workspace (response.md,
  diff-tracking, line-by-line response template).
- `experiment-skeleton/` -- standalone experiment / ablation workspace
  (separate from a paper repo, e.g. for exploratory work that may or
  may not become a paper).

When you ship one of these, append it to the templates index in
Section 5 and add a corresponding sub-section to Section 11 above.

## 12. Adopting on an existing project

Section 11 covers the from-scratch case ("I'm starting a new
paper / software / rebuttal"). The realistic case more often is
"I already have a project; help me adopt the framework on it."
That's what this section + the
`skills/project-onboarding/` skill cover.

When a user asks any of:

- "I have an existing project; help me start using these skills on
  it."
- "Migrate this repo to use the scicomp-research-skills framework."
- "I already have a `CLAUDE.md` (or `.cursorrules` or `AGENTS.md`);
  how do I integrate it with this framework?"
- "Adopt these skills on top of my existing work."

... the agent should load the
`skills/project-onboarding/SKILL.md` skill and walk the user through
the audit-then-plan-then-execute workflow it codifies.

### Two scenarios + sub-cases

The skill's decision tree distinguishes:

- **Scenario 1**: existing project, NO prior agentic instructions
  (no `AGENTS.md` / `CLAUDE.md` / `.cursorrules` at the repo root).
  Sub-cases: 1.A empty-ish repo; 1.B mature repo with substantial
  existing structure; 1.C non-standard layout.
- **Scenario 2**: existing project, WITH prior agentic instructions
  (one or more `AGENTS.md` / `CLAUDE.md` / `.cursorrules` /
  `GEMINI.md` / `CONVENTIONS.md` / `AGENT.md` files at the repo
  root). Sub-cases: 2.A one agent-file format; 2.B multiple
  agent-file formats; 2.C agent-file with substantive project
  content; 2.D conflicting conventions between the existing
  agent-file and the framework's universal conventions
  (root `AGENTS.md` Section 6).

### Universal migration workflow

Regardless of scenario, the migration follows five steps:

1. **Audit** -- inventory the existing project. Read-only step;
   nothing gets written. Output: a migration plan document
   (typically a temporary `notes/_migration_<date>.md`).
2. **Plan** -- the agent proposes specific file moves, content
   merges, new files to add, conflicts to resolve. The user
   reviews + approves before any writes.
3. **Execute** -- one commit per logical migration step.
4. **Verify** -- run the framework's first-action protocol on the
   migrated project; check that AGENTS.md / PLAN.md / cross-refs /
   no leaks all hold.
5. **Document** -- append an entry to `notes/agent_feedback.md`
   summarising the onboarding session.

### Core principle (from the skill)

**Existing project content is the user's work. The agent's job is
to preserve it, surface any conflicts to the user explicitly, and
migrate content into the canonical layout -- not to replace
existing files with template defaults.**

Concretely: audit before acting; move rather than overwrite;
surface conflicts explicitly; never auto-delete; one commit per
logical step.

### Ready-to-paste prompts

The skill's `references/migration-prompts.md` file contains
ready-to-paste prompts for each scenario + sub-case, plus a
"discovery prompt" for users unsure which scenario applies.

Every prompt begins with the same **prerequisite-check block** so
the agent can install the framework if it is not yet installed
(rather than failing opaquely on the "load skill" step). Discovery
prompt:

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

I have an existing project at <path> that I want to adopt the
scicomp-research-skills framework on. I'm not sure whether I have
prior agentic instructions or not. Load the project-onboarding
skill from
~/.scicomp-research-skills/skills/project-onboarding/SKILL.md
and its references/existing-project-audit.md. Inspect the project
state, classify which scenario applies, and propose a migration
plan. Do NOT make any changes yet.
```

### Conflict resolution mechanism

When the existing project's conventions disagree with the
framework's universal conventions (Section 6 above), the resolution
mechanism is the per-project AGENTS.md "Project-specific
overrides" section. That section is the formal home for approved
deviations -- the framework's universal rules are defaults, not
commandments, and per-project AGENTS.md MAY override them per
Section 3 of this file. The full procedure is in the skill's
`references/conflict-resolution.md`.

---

*Created 2026-05-13 by clone-and-diverge from
Master-cai/Research-Paper-Writing-Skills @ 9ee5edd.*

*Revised 2026-05-13 (post-audit cleanup: removed orphan upstream agent
config, dual-licensed LICENSE, single-sourced per-project boilerplate
via templates/paper-skeleton/AGENTS.md, added Section 11 "Starting a
new project").*

*Revised 2026-05-13 (added project-readme-authoring skill + Section 6
README-vs-AGENTS.md audience split convention).*

*Revised 2026-05-13 (renamed project-readme-authoring ->
human-facing-doc-authoring; generalised scope to all human-facing docs
incl. PLAN.md, notes/survey_*.md, references/_collection_log.md, etc.;
expanded universal convention; added per-doc-type structure files for
plan / notes / audit-log).*

*Revised 2026-05-13 (added agent-resource-discipline skill + Section 6
universal one-liners for tool selection / parallelism / targeted reads
/ re-use-prior-work / persistent-memory; codifies PDF lifecycle,
web-fetch caching, context-window budget, first-action/last-action
protocols).*

*Revised 2026-05-13 (added upstream-feedback channel: CONTRIBUTING.md +
.github/ISSUE_TEMPLATE/ + per-project notes/agent_feedback.md template
+ Section 6 universal one-liner pointing at it; the per-project
feedback channel + the agent-resource-discipline skill's recording
rules close the loop between project sessions and upstream skill
improvements).*

*Revised 2026-05-13 (added research-software-engineering skill -- first
cut: SKILL.md + references/01-numerical-correctness.md +
references/02-testing-for-numerical-code.md +
references/11-ai-assisted-coding-rules.md, per the prior-art audit's
PR1 sequencing; remaining 7 references + companion
templates/software-skeleton/ planned for PR2-PR4).*

*Revised 2026-05-13 (shipped templates/software-skeleton/ as PR3 ahead
of audit's original PR2; AGENTS.md / PLAN.md / README.md / CITATION.cff
with Zenodo handshake / .gitignore / experiments/README.md /
figures/README.md / notes/README.md + agent_feedback.md /
references/_collection_log.md / .github/ISSUE_TEMPLATE/{numerical-correctness-regression,
api-ergonomics, performance-regression}.md / bootstrap.sh delegating to
scientific-python/cookie | NLeSC/python-template |
CU-DBMI/template-uv-python-research-software; AGENTS.md Section 5
templates table updated; AGENTS.md Section 11.B replaced "not yet
shipped" stub with full 7-step walkthrough at parity with
paper-skeleton's 11.A; templates roadmap pruned to remove the
now-shipped software-skeleton entry).*

*Revised 2026-05-13 (added project-onboarding skill: SKILL.md +
references/{existing-project-audit, scenario-1-no-agentic-work,
scenario-2-existing-agentic-files, conflict-resolution,
migration-prompts}.md, addressing the realistic case of adopting the
framework on an existing project; AGENTS.md Section 5 updated; new
Section 12 'Adopting on an existing project' added; ready-to-paste
prompts for both scenarios + sub-cases provided; per-project AGENTS.md
template in templates/{paper,software}-skeleton/ updated with
project-onboarding in skills-to-load list; README.md gains an
'Adopting on an existing project' section).*

*Revised 2026-05-13 (templates/software-skeleton/ multi-language:
paper-coupling layer is language-agnostic; bootstrap.sh adds `julia`
option delegating to JuliaBesties/BestieTemplate.jl; new
MULTI-LANGUAGE.md inside the template explains which placeholders are
Python defaults vs language-agnostic + provides per-language quick
references for Julia / C++ / Rust / Fortran / MATLAB / Mathematica +
mixed-language projects + the placeholder-translation table;
template's AGENTS.md / PLAN.md / README.md flag Python defaults
explicitly with cross-references to MULTI-LANGUAGE.md; AGENTS.md
Section 5 templates row + Section 11.B bootstrap step updated).*

*Revised 2026-05-14 (post-fresh-audit cleanup: HIGH = compressed 3
over-long skill descriptions to <=1024 chars per OpenCode skill-spec
limit codified in Section 8; MEDIUM = trimmed
research-software-engineering workflow table to 3 ship-ready
references + 'Planned references' subsection for the 8 unshipped;
Section 7 acknowledges both paper-skeleton + software-skeleton
AGENTS.md as canonical with raised 50-150 line target; ATTRIBUTION.md
de-staled "templates/software-skeleton/ planned" framing; Section 6
sub-grouped into 6.1-6.6 for scanability + reformatted this footer
into a multi-paragraph italic block; LOW = paper-skeleton brought to
parity with software-skeleton via CITATION.cff + experiments/README.md
+ figures/README.md + .github/ISSUE_TEMPLATE/{reviewer-comment-followup,
experiment-rerun-needed, figure-update-needed}.md; missing template
README footers added; documented the deliberate date-stamp-footer
exception for upstream-vendored research-paper-writing references in
that skill's SKILL.md).*

*Maintained by A. Attia.*
