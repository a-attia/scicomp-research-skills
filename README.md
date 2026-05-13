# scicomp-research-skills

Agent skills + workflow templates for research in scientific computing
(papers and software).

This repository follows the [agents.md](https://agents.md/) standard and
the [OpenCode skills](https://opencode.ai/docs/skills/) /
[Anthropic skills](https://docs.anthropic.com/en/docs/build-with-claude/agent-skills)
conventions, so any markdown-aware coding agent can consume it (OpenCode,
Claude Code, Codex, Cursor, Aider, Gemini CLI, etc.).

**See [`AGENTS.md`](AGENTS.md) for the entry point that AI agents
should read first.**

This repository started as a clone of
[Master-cai/Research-Paper-Writing-Skills](https://github.com/Master-cai/Research-Paper-Writing-Skills)
on 2026-05-13 and intentionally diverges to broaden scope to scientific
computing (covering both research papers AND research software). See
[`ATTRIBUTION.md`](ATTRIBUTION.md) for the lineage.

## Layout

```
scicomp-research-skills/
  AGENTS.md             -- entry point for AI agents (read this first)
  README.md             -- you are here
  ATTRIBUTION.md        -- upstream attribution + divergence notes
  LICENSE               -- MIT (inherited from upstream)

  bin/
    refresh.sh          -- refresh the canonical (~/.scicomp-research-skills/) checkout
    install.sh          -- one-time setup on a new machine

  skills/               -- on-demand skills (one folder per skill, each with SKILL.md)
    research-paper-writing/   -- (from upstream) section drafting + paragraph-clarity check
    literature-survey/        -- (added) bibtex+PDF+pdftotext+survey-note workflow

  templates/            -- starter scaffolds for new projects
    paper-skeleton/     -- starter files for a new scientific-computing paper repo

  .githooks/
    pre-commit          -- refuses commits in the canonical (~/.scicomp-research-skills/) checkout
```

## On a new machine

```bash
git clone git@github.com:a-attia/scicomp-research-skills.git ~/.scicomp-research-skills
~/.scicomp-research-skills/bin/install.sh
```

`install.sh` does four things, idempotently:

1. Configures the local repo's `core.hooksPath` to enable the
   commit-blocking pre-commit hook on the canonical checkout.
2. Makes hook scripts and `bin/` scripts executable.
3. Creates **in-repo filename symlinks** so agents that look for
   non-AGENTS.md filenames find the same content: `CLAUDE.md` (Claude
   Code), `.cursorrules` (Cursor), `CONVENTIONS.md` (Aider), `GEMINI.md`
   (Gemini), `AGENT.md` (Zed singular form fallback).
4. Creates **user-home skill-discovery symlinks** so agents that
   auto-discover skills from `~/.config/opencode/skills/`, `~/.claude/skills/`,
   `~/.codex/skills/` (or `$CODEX_HOME/skills/`), `~/.agents/skills/`,
   and `~/.gemini/skills/` all point at our `skills/` folder.

The script defends against accidentally clobbering existing user
content: if any of these target paths already exists as a real directory
or as a symlink pointing somewhere else, it warns and skips rather than
overwrites. Re-running the script after manually removing a problematic
target is safe.

## On the development machine

The dev checkout lives wherever you cloned it for editing (anywhere
EXCEPT `~/.scicomp-research-skills/`, which is the canonical checkout
that refuses commits). A common convention is to keep it under your
usual code-projects directory. Edit there, commit + push from there.

## Refreshing the canonical checkout

To pick up the latest changes:

```bash
~/.scicomp-research-skills/bin/refresh.sh
# or directly: git -C ~/.scicomp-research-skills pull --ff-only
```

If a refresh brought in changes to install.sh (new agent symlinks, new
user-home skill paths, etc.), reconcile by running:

```bash
~/.scicomp-research-skills/bin/install.sh --update
```

`--update` does the same idempotent install + additionally reports any
in-repo orphan symlinks (created by an older install.sh but no longer in
the current install list) so you know whether to run uninstall.sh.

## Removing what install.sh created

```bash
# Preview what would be removed (default: dry-run, no changes):
~/.scicomp-research-skills/bin/uninstall.sh

# Actually remove install.sh's symlinks:
~/.scicomp-research-skills/bin/uninstall.sh --confirm

# Full removal (symlinks + git config + delete the canonical checkout):
~/.scicomp-research-skills/bin/uninstall.sh --deep --confirm
```

Dev checkouts of this repo at any other path are NEVER touched by uninstall.sh.

## Starting a new project that uses this repository

Once `~/.scicomp-research-skills/` is installed (see "On a new machine"
above), starting a new project that loads these skills + conventions is
a 5-step copy-and-customise.

### A. New research paper (canonical workflow)

```bash
# 1. Create the project directory anywhere you keep papers.
#    Substitute your own path for <papers-parent-dir>.
mkdir -p <papers-parent-dir>/<paper-short-name>
cd <papers-parent-dir>/<paper-short-name>
git init

# 2. Copy the paper-skeleton template (AGENTS.md + PLAN.md + README.md +
#    .gitignore + references/ + notes/ + experiments/ + figures/ + drafts/).
cp -R ~/.scicomp-research-skills/templates/paper-skeleton/. .

# 3. Customise the four files containing <...> placeholders:
#    - AGENTS.md   -> project name, target venue, code dependencies
#    - PLAN.md     -> working title, headline contribution, reading list
#    - README.md   -> title, authors, target submission, pinned versions
#    - notes/README.md -> section topics matching PLAN.md sections

# 4. (One-time per machine) verify the canonical checkout is fresh:
~/.scicomp-research-skills/bin/refresh.sh

# 5. First commit.
git add .
git commit -m "chore: bootstrap from scicomp-research-skills/templates/paper-skeleton"
```

Now open the project in your agent client (OpenCode, Claude Code, Codex,
Cursor, ...). The agent will:

1. Read the project's `AGENTS.md`.
2. Follow it to `~/.scicomp-research-skills/AGENTS.md` for shared
   conventions.
3. Load `skills/literature-survey/` and `skills/research-paper-writing/`
   on demand as the work proceeds.

A typical first session: ask the agent to run the `literature-survey`
skill on your first batch of references, then use
`research-paper-writing` to draft the introduction once the closest
competitors' survey notes are in place.

### B. New research software project

Templates for software-flavoured projects are planned but not yet
shipped. For now, see `AGENTS.md` Section 11.B for the recommended
interim approach (scaffold with your usual tool, then hand-write a
short `AGENTS.md` modelled on the paper-skeleton's).

### C. Reviewer response / rebuttal

Also not yet templated. See `AGENTS.md` Section 11.C for the interim
approach (add a `rebuttal_<round>/` sub-directory inside the existing
paper repo).

### Full reference

For the detailed walkthrough including troubleshooting and the roadmap
of upcoming templates (software-skeleton, rebuttal-skeleton,
experiment-skeleton), see `AGENTS.md` Section 11.

## Adding a new skill, template, or convention

See `AGENTS.md` Sections 8 and 9.

## Pulling updates from upstream (Master-cai)

The upstream repository is configured as the `upstream` remote:

```bash
git fetch upstream
git log upstream/main --oneline ^main
# Cherry-pick or merge as appropriate.
# Note: our directory layout differs (skills/research-paper-writing/
# instead of upstream's research-paper-writing/), so blind-merge will
# conflict on every file. Prefer cherry-pick for individual changes.
```

## License

MIT. See `LICENSE` (inherited from upstream, A. Attia additions also
MIT). See `ATTRIBUTION.md` for the divergence record.
