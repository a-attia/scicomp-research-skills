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
  design). Structural patterns (5-step probe-then-claim debug, 5-step
  launch pre-flight, 7-step research-publishing) informed
  `skills/research-software-engineering/`'s planned references 09 and 10
  (launch + debug protocols), with adaptation from ML probes to
  numerical probes. License: MIT.
- [koaeraser/ARMS](https://github.com/koaeraser/ARMS) -- Autonomous
  research manuscript pipeline (11 coordinated skills). Out of scope here
  because it targets fully autonomous paper generation rather than
  human-in-the-loop drafting.
- [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills)
  -- 135 per-package wrappers (RDKit, BioPython, Scanpy, Pymatgen,
  Astropy, Qiskit, ...). Different scope from this repo (we cover
  *methodology*; they cover *tool wrappers*). License: MIT. Cited from
  `skills/research-software-engineering/SKILL.md` as the closest
  neighbour-but-orthogonal-axis prior art.

## Sources cited from inside skill content

The following upstream sources are cited from inside the skill files
themselves (not vendored). They are not "prior art that informed the
repository's design" in the same sense as the section above; rather,
they are the named references the skill content explicitly directs
agents and users to read.

### Cited from `skills/research-software-engineering/`

- **Bridgeford EW, Sochat V, Markiewicz CJ, Zhang J, Ghosh S, Halchenko Y,
  Esteban O, Hanke M, Poldrack RA. *Ten Simple Rules for AI-Assisted
  Coding in Science*.** arXiv:2510.22254 (2025). Companion Jupyter Book:
  https://poldracklab.org/10sr_ai_assisted_coding . Zenodo DOI
  10.5281/zenodo.17398109. **License: CC-BY 4.0.** The single most
  important upstream source for the AI-assisted-coding rules in
  `references/11-ai-assisted-coding-rules.md` (verbatim quotation
  permitted with attribution per CC-BY-4.0).
- **Poldrack RA. *Better Code, Better Science*.** Free online book at
  https://poldrack.github.io/BetterCodeBetterScience/ (2024). Book-length
  treatment of the same author's argument; cited as further reading.
- **Wilson G, Bryan J, Cranston K, Kitzes J, Nederbragt L, Teal TK.
  *Good Enough Practices in Scientific Computing*.** PLOS Computational
  Biology 13(6): e1005510 (2017).
  https://swcarpentry.github.io/good-enough-practices-in-scientific-computing/
  License: CC-BY. Pre-AI-era baseline; cited as foundational reference.
- **Wilson G, Aruliah DA, Brown CT, et al. *Best Practices for Scientific
  Computing*.** PLOS Biology 12(1): e1001745 (2014). Sibling-paper to the
  2017 "Good Enough" paper; cited where the more rigorous baseline applies.
- **Roache PJ. *Code Verification by the Method of Manufactured
  Solutions*.** J. Fluids Eng. 124(1): 4-10 (2002). Canonical MMS
  reference cited in `references/01-numerical-correctness.md`.
- **Oberkampf WL, Roy CJ. *Verification and Validation in Scientific
  Computing*.** Cambridge University Press (2010). Book-length V&V
  reference cited in `references/01-numerical-correctness.md`.
- **LeVeque RJ, Mitchell IM, Stodden V. *Reproducible Research for
  Scientific Computing: Tools and Strategies for Changing the Culture*.**
  Computing in Science & Engineering 14(4): 13-17 (2012). DOI
  10.1109/MCSE.2012.38. Cited in
  `references/05-reproducibility-infrastructure.md` (planned).
- **Scientific Python Development Guide + sp-repo-review.**
  https://learn.scientific-python.org/development/ ;
  https://github.com/scientific-python/cookie ;
  https://github.com/scientific-python/sp-repo-review .
  **License: BSD-3-Clause.** The single best-aligned best-practice corpus
  in this domain. The 3-tier test suite, marker discipline, "confirm the
  test fails" rule, diagnostic-tests pattern, and design principles in
  `references/02-testing-for-numerical-code.md` and the universal
  principles in `SKILL.md` are adapted from this guide with attribution.
- **pyOpenSci Python Package Guide.**
  https://www.pyopensci.org/python-package-guide/ . Community-developed
  guide on packaging + tests + docs for scientific Python software.
  Cited as an alternative organisation of the same material.
- **JOSS (Journal of Open Source Software) review criteria** (2025+,
  with required AI-Usage Disclosure).
  https://joss.readthedocs.io/en/latest/review_criteria.html . Cited as
  the canonical review checklist for paper-companion software.
- **BSSw.io (Better Scientific Software).** https://bssw.io . DOE/NNSA-
  funded curated resource library; particularly the V&V articles
  (https://bssw.io/items/definition-and-categorization-of-tests-for-cse-software).
- **The Turing Way.** https://book.the-turing-way.org . CC-BY 4.0 + MIT.
  The Research Compendia chapter is cited in
  `references/08-code-paper-coupling.md` (planned).
- **NLeSC fair-software 5 recommendations.** https://fair-software.eu .
  The five FAIR-software recommendations (public repo, license, registry,
  citable, checklist) cited in `references/05-reproducibility-infrastructure.md`
  (planned).

### Project templates referenced (planned for `templates/software-skeleton/`)

The future `templates/software-skeleton/` (planned per the audit's PR3
sequencing) will not reimplement package scaffolding. It will delegate
to one of:

- **scientific-python/cookie** (BSD-3-Clause).
  https://github.com/scientific-python/cookie .
- **NLeSC/python-template** (Apache-2.0).
  https://github.com/NLeSC/python-template .
- **CU-DBMI/template-uv-python-research-software** (BSD-3-Clause).
  https://github.com/CU-DBMI/template-uv-python-research-software .

The `templates/software-skeleton/` will add only the research-paper-
specific layers (`experiments/<run-id>/`, `figures/<paper-section>/`,
`notes/impl_*.md`, `references/_collection_log.md`, CITATION.cff with
Zenodo handshake instructions, `.github/ISSUE_TEMPLATE/` for
numerical-correctness regressions / API ergonomics / performance
regressions) on top of whichever upstream the user chooses. Detailed
attribution will land in the template's own `AGENTS.md` and `README.md`
when shipped.

---

*Created 2026-05-13. Revised 2026-05-13 (added cited sources for
research-software-engineering skill: Bridgeford 2025, Poldrack book,
Wilson 2014/2017, Roache 2002, Oberkampf & Roy 2010, LeVeque/Mitchell/
Stodden 2012, Scientific Python Development Guide, pyOpenSci, JOSS,
BSSw.io, The Turing Way, NLeSC fair-software, plus template upstreams
scientific-python/cookie + NLeSC/python-template + CU-DBMI/template-uv-
python-research-software). Maintained by A. Attia.*
