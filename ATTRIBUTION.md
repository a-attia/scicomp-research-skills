# Attribution

This repository started as a clone of
[Master-cai/Research-Paper-Writing-Skills](https://github.com/Master-cai/Research-Paper-Writing-Skills)
on 2026-05-13, taken at upstream commit `9ee5edd` (which itself curates and
adapts open notes by Prof. Peng Sida (彭思达); see
[learning_research](https://github.com/pengsida/learning_research)).

We have intentionally **diverged** rather than maintained a strict fork
relationship, because the scope of this repository differs materially from
upstream:

- **Upstream scope**: paper-writing skill for ML/CV/NLP research papers
  (Codex / Claude Code / Gemini).
- **This repository's scope**: agent skills + workflow templates for
  research in **scientific computing** (covering both research **papers**
  and research **software** -- inverse problems, optimal experimental
  design, optimisation, uncertainty quantification, scientific machine
  learning, computational PDEs, etc.). Multi-agent compatible (OpenCode,
  Claude Code, Codex, Cursor, Aider, ...).

The `skills/research-paper-writing/` directory in this repository preserves
upstream's content (relocated under `skills/` to match the
[agents.md](https://agents.md/) /
[OpenCode skills](https://opencode.ai/docs/skills/) standard layout) and
will continue to receive selective merges from upstream when they apply to
our broader scope.

The MIT licence terms inherited from upstream (see `LICENSE`) apply to all
content. Additions made in this repository are also MIT-licensed, with
copyright `(c) 2026 A. Attia` for the new content.

## Upstream remote

The upstream repository is configured as a git remote named `upstream`:

```bash
git remote -v
# upstream  https://github.com/Master-cai/Research-Paper-Writing-Skills.git (fetch)
# upstream  https://github.com/Master-cai/Research-Paper-Writing-Skills.git (push)
```

To pull selective updates from upstream into this fork:

```bash
git fetch upstream
# Inspect changes
git log upstream/main --oneline ^main
# Cherry-pick or merge as appropriate; do NOT blind-merge since our
# directory layout has been restructured (skills/research-paper-writing/
# instead of upstream's research-paper-writing/ at the top level).
```

## Acknowledgements

Sincere thanks to:

- **Prof. Peng Sida (彭思达)** for openly sharing the paper-writing notes
  that form the backbone of `skills/research-paper-writing/`.
- **Master-cai** for the curation and skill packaging that made those
  notes machine-consumable.

## Other prior art consulted (not vendored)

The following repositories were studied during the design of this
repository but are not vendored here. We may import individual skills from
them in the future (with appropriate attribution updates):

- [fcakyon/phd-skills](https://github.com/fcakyon/phd-skills) -- PhD
  research skills for Claude Code; particularly strong on ML training
  guardrails (paper reproduction, debug, compare, launch, ablation
  design). Out of scope here because it is Claude Code-plugin-specific
  and ML-training-focused.
- [koaeraser/ARMS](https://github.com/koaeraser/ARMS) -- Autonomous
  research manuscript pipeline (11 coordinated skills). Out of scope here
  because it targets fully autonomous paper generation rather than
  human-in-the-loop drafting.

---

*Created 2026-05-13. Maintained by A. Attia.*
