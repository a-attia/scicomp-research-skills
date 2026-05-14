# scicomp-research-skills

Agent skills and workflow templates for research in scientific computing
-- both research **papers** (drafts, literature surveys, reviewer
responses) and research **software** (libraries, codes, reproducibility
infrastructure).

The repository follows the [agents.md](https://agents.md/) standard and
the [OpenCode skills](https://opencode.ai/docs/skills/) /
[Anthropic skills](https://docs.anthropic.com/en/docs/build-with-claude/agent-skills)
conventions, so any markdown-aware coding agent can consume it
(OpenCode, Claude Code, Codex, Cursor, Aider, Gemini CLI, ...).

> **For AI agents reading this repository**: jump straight to
> [`AGENTS.md`](AGENTS.md). That is the canonical entry point. This
> README is for humans.

---

## Contents

- [What you get](#what-you-get)
- [Quick start](#quick-start)
  - [1. Install once per machine](#1-install-once-per-machine)
  - [2. Start a new project](#2-start-a-new-project)
  - [3. Day-to-day use](#3-day-to-day-use)
- [How it fits together](#how-it-fits-together)
  - [Two checkouts per machine](#two-checkouts-per-machine)
  - [Repository layout](#repository-layout)
  - [What `install.sh` actually does](#what-installsh-actually-does)
- [Starting a new project (in detail)](#starting-a-new-project-in-detail)
  - [A. Research paper (canonical workflow)](#a-research-paper-canonical-workflow)
  - [B. Research software project](#b-research-software-project)
  - [C. Reviewer response / rebuttal](#c-reviewer-response--rebuttal)
- [Maintenance](#maintenance)
  - [Refreshing the canonical checkout](#refreshing-the-canonical-checkout)
  - [Reconciling after `install.sh` changes](#reconciling-after-installsh-changes)
  - [Removing what `install.sh` created](#removing-what-installsh-created)
- [Extending this repository](#extending-this-repository)
- [Pulling updates from upstream](#pulling-updates-from-upstream)
- [Provenance and licence](#provenance-and-licence)

---

## What you get

Two reusable building blocks, both loaded on demand by your agent:

1. **Skills** -- focused workflow guides the agent loads when it
   recognises a matching task. Currently:
   - [`skills/literature-survey/`](skills/literature-survey/SKILL.md)
     -- BibTeX + PDF + `pdftotext` + per-paper survey notes +
     verification log workflow for building a trustworthy bibliography.
   - [`skills/research-paper-writing/`](skills/research-paper-writing/SKILL.md)
     -- section-by-section drafting, paragraph-clarity check,
     claim-evidence alignment, adversarial self-review.

2. **Templates** -- starter scaffolds you copy into a new project, then
   customise. Currently:
   - [`templates/paper-skeleton/`](templates/paper-skeleton/) -- a
     ready-to-fill paper workspace with `AGENTS.md`, `PLAN.md`,
     `README.md`, `.gitignore`, and pre-created `references/`,
     `notes/`, `experiments/`, `figures/`, `drafts/` subdirectories.

Plus the install / refresh / uninstall tooling under [`bin/`](bin/) and
the per-project `AGENTS.md` boilerplate that wires everything together.

---

## Quick start

### 1. Install once per machine

Clone the repository to its **canonical** location and run the
installer:

```bash
git clone git@github.com:a-attia/scicomp-research-skills.git ~/.scicomp-research-skills
~/.scicomp-research-skills/bin/install.sh
```

The installer is idempotent: re-running it later (e.g. after a
`refresh.sh`) is safe. See
[What `install.sh` actually does](#what-installsh-actually-does) for
the details.

### 2. Start a new project

For a research paper (canonical workflow):

```bash
mkdir -p <papers-parent-dir>/<paper-short-name>
cd       <papers-parent-dir>/<paper-short-name>
git init
cp -R ~/.scicomp-research-skills/templates/paper-skeleton/. .
# ... then customise the four files containing `<...>` placeholders
git add .
git commit -m "chore: bootstrap from scicomp-research-skills/templates/paper-skeleton"
```

Software projects and reviewer responses don't have dedicated templates
yet; see
[Starting a new project (in detail)](#starting-a-new-project-in-detail)
below for the interim recipes.

### 3. Day-to-day use

Open the new project in your agent client (OpenCode, Claude Code,
Codex, Cursor, ...). The agent reads `AGENTS.md`, follows it to the
shared `~/.scicomp-research-skills/AGENTS.md`, and loads skills on
demand as your work matches them.

A typical first session might be:

> *"Use the `literature-survey` skill on these 8 PDFs. Then once the
> survey notes are in place, use `research-paper-writing` to draft the
> introduction."*

---

## How it fits together

### Two checkouts per machine

The repository lives in **two places** on each machine, with different
roles:

- `~/.scicomp-research-skills/` -- the **canonical checkout**.
  Read-only from your perspective; refreshed via
  `~/.scicomp-research-skills/bin/refresh.sh`. This is the location
  every agent on the machine reads from. A pre-commit hook refuses
  commits here, so accidental edits cannot be committed back.

- *Anywhere else of your choosing* -- the **dev checkout**.
  This is where you edit + commit + push. A common convention is to
  keep it under your usual code-projects directory. Other research
  projects on the machine ignore this checkout completely.

After you push from the dev checkout, refresh the canonical checkout to
pick up the change (see
[Refreshing the canonical checkout](#refreshing-the-canonical-checkout)).

### Repository layout

```
scicomp-research-skills/
├── AGENTS.md             entry point for AI agents (read this first)
├── README.md             you are here
├── ATTRIBUTION.md        upstream lineage and divergence notes
├── LICENSE               MIT (dual copyright, see ATTRIBUTION.md)
│
├── bin/
│   ├── install.sh        one-time setup on a new machine
│   ├── refresh.sh        update the canonical checkout
│   └── uninstall.sh      reverse install.sh (dry-run by default)
│
├── skills/               on-demand skills (one folder per skill)
│   ├── literature-survey/
│   └── research-paper-writing/
│
├── templates/            starter scaffolds for new projects
│   └── paper-skeleton/
│
└── .githooks/
    └── pre-commit        refuses commits in the canonical checkout
```

### What `install.sh` actually does

Four idempotent steps:

1. **Wires the pre-commit hook**: sets `core.hooksPath = .githooks` so
   the hook that refuses commits in the canonical checkout becomes
   active.
2. **Marks scripts executable**: `chmod +x` on `bin/*.sh` and
   `.githooks/*`.
3. **Creates in-repo filename symlinks** so agents that look for
   non-`AGENTS.md` filenames find the same content:
   - `CLAUDE.md` -> `AGENTS.md` (Claude Code)
   - `.cursorrules` -> `AGENTS.md` (Cursor)
   - `CONVENTIONS.md` -> `AGENTS.md` (Aider)
   - `GEMINI.md` -> `AGENTS.md` (Gemini Code Assist)
   - `AGENT.md` -> `AGENTS.md` (Zed singular fallback)
4. **Creates user-home skill-discovery symlinks** so agents that
   auto-discover skills find ours:
   - `~/.config/opencode/skills/` -> `<canonical>/skills/`
   - `~/.claude/skills/` -> `<canonical>/skills/`
   - `~/.codex/skills/` (or `${CODEX_HOME}/skills/`) ->
     `<canonical>/skills/`
   - `~/.agents/skills/` -> `<canonical>/skills/`
   - `~/.gemini/skills/` -> `<canonical>/skills/`

The script is **safe by default**: if any target path already exists as
a real directory or as a symlink pointing somewhere else, it warns and
skips rather than overwrites. Re-running after manually removing a
problematic target is the way to recover.

To remove anything `install.sh` created, see
[Removing what `install.sh` created](#removing-what-installsh-created).

---

## Starting a new project (in detail)

The Quick Start above shows the minimal happy path. This section adds
context, troubleshooting, and the recipes for project types that don't
yet have a template.

### A. Research paper (canonical workflow)

Five steps, expanded from the Quick Start:

1. **Create the project directory.** Anywhere convenient -- typically a
   sibling of any code repos this paper depends on, so paper revisions
   don't pollute code history.

   ```bash
   mkdir -p <papers-parent-dir>/<paper-short-name>
   cd       <papers-parent-dir>/<paper-short-name>
   git init
   ```

2. **Copy the paper-skeleton template** verbatim:

   ```bash
   cp -R ~/.scicomp-research-skills/templates/paper-skeleton/. .
   ```

   You now have:

   - `AGENTS.md` -- per-project agent entry point.
   - `PLAN.md` -- plan-of-record (the contract).
   - `README.md` -- human-facing project description.
   - `.gitignore` -- excludes PDFs, `.txt` extractions, experiment
     artefacts, LaTeX build files.
   - `references/` -- with stub `bibliography.bib` and
     `_collection_log.md`.
   - `notes/` -- with stub `README.md` (an index over future survey
     notes).
   - `experiments/`, `figures/`, `drafts/` -- empty, with `.gitkeep`s.

3. **Customise the four files with `<...>` placeholders.** Each file
   tells you what to fill in:

   | File              | Fill in                                                                       |
   |:------------------|:------------------------------------------------------------------------------|
   | `AGENTS.md`       | project name, target venue, code dependencies, citation style, collaborators  |
   | `PLAN.md`         | working title, headline contribution, test case, hypothesis, reading list     |
   | `README.md`       | title, authors, target submission, pinned upstream library versions, status   |
   | `notes/README.md` | section topics matching your `PLAN.md` sections                               |

4. **Verify the canonical checkout is fresh** (one-time per machine, or
   whenever you suspect it's stale):

   ```bash
   ~/.scicomp-research-skills/bin/refresh.sh
   ```

5. **First commit**:

   ```bash
   git add .
   git commit -m "chore: bootstrap from scicomp-research-skills/templates/paper-skeleton"
   ```

Now open the project in your agent client. The agent will:

1. Read the project's `AGENTS.md`.
2. Follow it to `~/.scicomp-research-skills/AGENTS.md` for the shared
   conventions.
3. Load `skills/literature-survey/` and `skills/research-paper-writing/`
   on demand as the work proceeds.

A typical first session asks the agent to run the `literature-survey`
skill on your first batch of references, then to use
`research-paper-writing` to draft the introduction once the closest
competitors' survey notes are in place.

### B. Research software project

A dedicated `templates/software-skeleton/` is **not yet shipped**. In
the meantime:

1. Use your normal language- or framework-specific scaffolding
   (`cookiecutter`, `cargo new`, `uv init`, ...) to create the project.
2. Hand-write a short `AGENTS.md` modelled on
   [`templates/paper-skeleton/AGENTS.md`](templates/paper-skeleton/AGENTS.md).
   Keep the same Section 1-3 boilerplate; the skills-to-load list will
   likely be empty for now.
3. Hand-write a `PLAN.md` reorganised around code milestones (M1 =
   bootstrap + CI, M2 = core API, M3 = first user, ...) instead of paper
   milestones.

Track this gap (or contribute the template!) -- see
[Extending this repository](#extending-this-repository).

### C. Reviewer response / rebuttal

Also not yet templated. Recommended interim:

1. Add a sub-directory inside the existing paper repo:
   `<paper-repo>/rebuttal_<round>/`.
2. Hand-write a short `AGENTS.md` that loads the parent paper's
   `AGENTS.md` plus the `research-paper-writing` skill (specifically
   the `paper-review.md` reference, which covers reviewer-facing
   concerns).

For the full agent-facing walkthrough including the roadmap of
upcoming templates, see [`AGENTS.md`](AGENTS.md) Section 11.

---

## Maintenance

### Refreshing the canonical checkout

```bash
~/.scicomp-research-skills/bin/refresh.sh
# equivalent to: git -C ~/.scicomp-research-skills pull --ff-only
```

This is a `--ff-only` pull, so it will refuse to merge if anything has
diverged. (Nothing should ever diverge in the canonical checkout; the
pre-commit hook prevents commits there. If a divergent state appears,
that's a bug worth investigating.)

### Reconciling after `install.sh` changes

If a refresh brought in a newer `install.sh` (e.g. with new agent
symlinks or new user-home skill paths), reconcile by re-running it in
update mode:

```bash
~/.scicomp-research-skills/bin/install.sh --update
```

`--update` does the same idempotent install + additionally reports any
in-repo orphan symlinks (created by an older `install.sh` but no longer
in the current install list).

### Removing what `install.sh` created

`uninstall.sh` is **dry-run by default**. Without `--confirm`, it just
prints what it would do.

```bash
# Preview only (no changes):
~/.scicomp-research-skills/bin/uninstall.sh

# Actually remove install.sh's symlinks:
~/.scicomp-research-skills/bin/uninstall.sh --confirm

# Full removal: symlinks + git config + delete the canonical checkout:
~/.scicomp-research-skills/bin/uninstall.sh --deep --confirm
```

Dev checkouts of this repo at any other path are NEVER touched by
`uninstall.sh`. The `--deep` mode additionally guards against deleting
anything other than exactly `~/.scicomp-research-skills/`, and (without
`-y`) requires you to type `DELETE` to confirm.

Every action (preview or actual) is appended to
`~/.scicomp-research-skills.uninstall.log` for later audit.

---

## Extending this repository

To add a new skill, template, or convention, edit in the dev checkout
and push from there:

- **New skill**: see [`AGENTS.md`](AGENTS.md) Section 8.
- **New template**: see [`AGENTS.md`](AGENTS.md) Section 9.
- **New universal convention**: edit Section 6 of
  [`AGENTS.md`](AGENTS.md) directly.

After pushing, run `~/.scicomp-research-skills/bin/refresh.sh` on each
machine that should pick up the change.

---

## Pulling updates from upstream

The original [Master-cai/Research-Paper-Writing-Skills](https://github.com/Master-cai/Research-Paper-Writing-Skills)
repository is configured as the `upstream` remote:

```bash
git fetch upstream
git log upstream/main --oneline ^main
```

Our directory layout differs (`skills/research-paper-writing/` instead
of upstream's top-level `research-paper-writing/`), so a blind merge
will conflict on every file. **Prefer `git cherry-pick` for individual
upstream changes.**

---

## Provenance and licence

This repository began as a clone of
[Master-cai/Research-Paper-Writing-Skills](https://github.com/Master-cai/Research-Paper-Writing-Skills)
on 2026-05-13 and intentionally diverges to broaden the scope to
scientific computing. See [`ATTRIBUTION.md`](ATTRIBUTION.md) for the
full lineage and acknowledgements.

Licensed under the MIT licence. See [`LICENSE`](LICENSE) for the
combined upstream copyright (Master-cai 2026) and additions in this
fork (A. Attia 2026).
