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

`install.sh` configures the local repo's `core.hooksPath`, makes scripts
executable, and creates agent-specific filename symlinks (CLAUDE.md,
.cursorrules, etc.) inside the canonical checkout.

For OpenCode auto-discovery of skills, additionally:

```bash
ln -s ~/.scicomp-research-skills/skills ~/.config/opencode/skills
# or for Claude Code compatibility:
ln -s ~/.scicomp-research-skills/skills ~/.claude/skills
```

## On the development machine

The dev checkout lives at
`~/AHMED_HOME/Research/Projects/Software/scicomp-research-skills/`
(or wherever you cloned it for editing). Edit there, commit + push from
there.

To pick up the latest changes in the canonical checkout used by agents:

```bash
~/.scicomp-research-skills/bin/refresh.sh
# or directly: git -C ~/.scicomp-research-skills pull --ff-only
```

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
