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
git clone <your-fork-url> ~/.scicomp-research-skills
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

The dev checkout lives at
`~/AHMED_HOME/Research/Projects/Software/scicomp-research-skills/`
(or wherever you cloned it for editing). Edit there, commit + push from
there.

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

The dev checkout under Software/ is NEVER touched by uninstall.sh.

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
