# Survey-note template + worked example

This file is loaded on demand from the `literature-survey` skill when an
agent needs the precise structure of a per-paper survey note. The
template sections are MANDATORY; the worked example shows what each
section looks like in practice.

---

## Template

```markdown
# <Authors short> <year> -- <Short paper title or method nickname>

**Citation key**: `<citekey>`. <venue> <year>, <vol/no/pages or arXiv ID>.
**Authors**: <full author list with affiliations>.
**PDF**: `references/pdf/<citekey>.pdf`. <Optional: `<citekey>-supp.pdf`>.

## Headline claim

One sentence stating the paper's central contribution. Be specific about
what is new vs prior art. Avoid hype.

## Method (full detail)

The method, written for someone who has read the abstract but not the
paper. Include:

- The mathematical formulation, with key equations in MathJax (display
  blocks for important ones; inline for symbol references).
- The algorithm at a high level (pseudo-code if helpful).
- The architectural choices that matter (e.g. "uses attention over the
  history" / "fixed-atom categorical distribution").
- Any non-obvious tricks (e.g. "uses sample-and-freeze for variance
  reduction").

Aim for ~10-20 lines. Skip background that the reader of your paper will
already know.

## Test cases (with parameters)

What the paper actually runs on. Be specific:

- Datasets / problems used + dimensionalities.
- Hyperparameter ranges where they matter.
- Horizon / episode length / number of steps for sequential problems.
- Anything that will inform our reproduction or comparison.

## Headline numerical results

The numbers that appear in the paper's headline tables / figures. Cite
specific tables / figures so future-you can re-find them quickly. Use
markdown tables for structured comparisons.

## Relevance to our paper

Why we cite this paper. Be specific:

- Which sections of OUR paper will reference this one?
- Is this a direct competitor (we run against it), a foundational
  citation (we build on it), or a background citation (we mention it in
  passing)?
- What axes does our paper differ on?

## Critical observations

Things you noticed in the deep read that are NOT in the abstract:

- Implementation details that matter.
- Caveats / limitations not foregrounded by the authors.
- Connections to other papers in our corpus.
- Anything you'll want to reference in our paper's discussion section.

## Action items for our paper

Concrete things to do in our paper as a result of reading this one:

- Citation contexts (e.g. "cite in PLAN.md Section 3.4 as motivation
  for distributional critics").
- Implementation tasks (e.g. "verify our DSAC matches their Algorithm 1
  Eq. 17").
- Open questions for follow-up (e.g. "decide if we want their multiplicative
  noise model").

---

*Created YYYY-MM-DD by <name>. <Optional revision notes.>*
```

## Worked example

Below is a redacted excerpt of a survey note that follows this template.
Long sections are abbreviated for the example; in real notes, write full
content.

```markdown
# Shen and Huan 2023 -- PG-sOED for Nonlinear Bayesian sOED

**Citation key**: `shen2023sOED`. CMAME 416 (2023) 116304. arXiv:2110.15335.
**Authors**: Wanggang Shen, Xun Huan (University of Michigan ME).
**PDF**: `references/pdf/shen2023sOED.pdf`. **Code**: github.com/wgshen/sOED

## Headline claim

First end-to-end **policy-gradient deep RL** approach to sequential
Bayesian OED for **nonlinear PDE-governed inverse problems**, formulated
as a finite-horizon POMDP with KL-divergence terminal reward.

## Method (full detail)

- POMDP framing (Section 2.2): state $x_k = (x_{k,b}, x_{k,p})$ = belief
  + physical state. Belief represented by information vector
  $I_k = \{d_0, y_0, ..., d_{k-1}, y_{k-1}\}$ -- the trivial sufficient
  statistic. Avoids explicit posterior computation at intermediate steps.
- Reward = KL divergence (Lindley utility, Eq. 8). Two equivalent
  formulations (Theorem 1):
  - Terminal: $g_N(x_N) = D_{KL}(p(\cdot | I_N) \| p(\cdot | I_0))$
  - Incremental: $g_k = D_{KL}(p(\cdot | I_{k+1}) \| p(\cdot | I_k))$
- Policy gradient (Theorem 2, Eq. 16):
  $$\nabla_w U(w) = \sum_{k=0}^{N-1} \mathbb{E}\!\bigl[ \nabla_w \mu_{k, w_k}(x_k) \nabla_{d_k} Q^{\pi_w}_k \bigr]$$
- Actor-critic with deep NNs; sample-and-freeze MC trick (Eq. 17) for
  variance reduction.
- Exploration: Gaussian noise on deterministic policy during training only.

## Test cases (with parameters)

1. Linear-Gaussian benchmark (Section 4.1): scalar theta, 2-step horizon,
   conjugate posterior, closed-form optimal policy.
2. Advection-diffusion contaminant source inversion (Section 4.2):
   2D PDE, mobile sensor with displacement-action, source parameter
   theta = (theta_x, theta_y, theta_h, theta_s) in R^4. Solver: 2nd-order
   finite volume, dz=0.01, dt=5e-4. Cases 1-4: from N=2 to N>=10 horizons.

## Headline numerical results

- Linear-Gaussian: PG-sOED reaches 0.775 +/- 0.006 vs analytical optimum
  0.783; matches ADP-sOED but with 35x training speedup + 6000x online
  speedup (Table 1).
- AD source inversion: PG-sOED beats batch and greedy designs across all
  4 cases.

## Relevance to our paper

- **Single closest existing work in the literature.** Same problem class,
  same algorithm class (deep PG RL).
- Our paper differs by adding distributional critics (DSAC-Gaussian, C51)
  + risk-sensitive variants (CVaR-EIG) + per-step EIG dense reward as
  default + multiple action-space types.

## Critical observations

- Their belief representation = full information vector I_k, not a
  Gaussian sufficient statistic. They do particle/grid posterior at
  episode end (small theta-dim friendly). Our Laplace-Gaussian gives a
  much cheaper continuous posterior.
- Their observation noise is multiplicative (signal-magnitude-dependent).
  We should adopt this realism.
- Their MC sample-and-freeze trick (Eq. 17 + Appendix C) is elegant
  variance reduction worth adopting.

## Action items for our paper

1. Read full PDF carefully before designing our PyOEDAdvectionDiffusionEnv.
   Match their action space, noise model, and horizons for direct
   comparability.
2. Cite shen2023sOED prominently in PLAN.md Section 0 and Section 1.2.
3. Email Wanggang Shen (`wgshen` GitHub) about their reference
   implementation.

---

*Created 2026-05-11 by A. Attia.*
```

## Notes on style

- Use second-person never; first-person plural sparingly ("our paper",
  "we cite").
- Date-stamp every note (Created YYYY-MM-DD; Revised YYYY-MM-DD if
  applicable).
- Keep the action-items list concrete and verifiable; vague items
  ("think about how this affects us") are forbidden.
- Length budget: ~30-50 lines for typical notes; longer (up to ~100
  lines) is acceptable for landmark papers that drive multiple sections
  of your draft.

---

*Created 2026-05-13 by A. Attia.*
