# Plan-of-Record: <Working Title>

**Working title**: *<Full descriptive title>*

**Authors**: <author list with affiliations>.
**Target venue class**: <e.g. JMLR / JCP / SIAM J. Sci. Comput.>.
**Target submission**: <month year> (<N> month horizon).
**Software**: <upstream library URLs, if applicable>.
**Workspace**: `<paper-repo>/` (sibling of any code repos this paper
depends on; not committed to those code repos).

> **Doc status**: Living plan-of-record. Date-stamp every revision.
> Items marked `[VERIFY]` need user confirmation or independent lookup
> before use.

---

## Headline Contribution

**Claim.** <One-paragraph statement of what this paper contributes that
prior work has not done.>

**Positioning relative to prior work.** <List the closest competitors
with one-line summaries. Be specific about what we add vs each.>

**Why this should help.** <Mechanism of action. One paragraph.>

**Test case.** <Describe the headline experimental / theoretical test
case that this paper's claims will be evaluated on.>

**Hypothesis.** <The empirical hypothesis we will test.>

---

## 1. Survey Reading List

Citation keys below match `references/bibliography.bib`. Per-paper survey
notes (~30-50 lines each: claim, method with key equations, test cases,
headline results, action items for our paper) live in
`notes/survey_<citekey>.md`. PDFs of the published manuscripts (and any
supplementary material) live in `references/pdf/<citekey>.pdf`.

**Status**: <X>/<Y> entries verified. Outstanding sections marked
`[VERIFY]` or `[INSERT]`.

### 1.1 <Section topic>

- `<citekey>`: <full citation>.

### 1.2 <Section topic>

- `<citekey>`: <full citation>.

(... add more subsections as needed ...)

**Action.** For each section, verify all `[VERIFY]` / `[INSERT]` entries
and produce survey notes via the `literature-survey` skill before any
draft references them.

---

## 2. Test Case Specification

### 2.1 <Forward problem / setup>

<Mathematical formulation of the test case. Use MathJax. Include any
domain-specific notation conventions.>

### 2.2 <Observation / measurement model>

<...>

### 2.3 <Belief / posterior / inference target>

<...>

### 2.4 <Reward / loss / objective signals>

<...>

### 2.5 <Episode horizon / experiment budget>

<...>

### 2.6 Reference baselines

<List the non-RL / non-headline-method baselines.>

---

## 3. Algorithms / Methods Comparison Matrix

| Family       | Method                  | Critic / return type           | Action / decision space | Status     |
|:-------------|:------------------------|:-------------------------------|:------------------------|:-----------|
| <family 1>   | <method 1>              | <type>                         | <space>                 | <ready / NEW (S/M/L) / config-only> |
| <family 2>   | <method 2>              | <type>                         | <space>                 | <...>     |

---

## 4. Experiment Protocol

### 4.1 Seeds / replicates

- $N_{\text{seeds}} = $ <number> per (algorithm, reward variant, action-space variant) cell.
- Aggregate via mean +/- std and report median + IQR for robustness.
- Multi-seed mandatory.

### 4.2 Metrics

Primary:

- ...

Secondary:

- ...

Diagnostic:

- ...

### 4.3 Hyperparameters

<Tuning protocol; freezing convention; reporting convention.>

### 4.4 Statistical tests

<Pairwise tests; multiple-comparisons correction; effect-size reporting.>

### 4.5 Compute budget

<Bottleneck identification; per-seed wall-clock estimate; total cell
count; total wall-clock estimate.>

---

## 5. Implementation Components: Existing vs New

### 5.1 Existing in upstream library

(Components we inherit and use as-is.)

### 5.2 New components needed

(Components we will need to build / contribute.)

---

## 6. Implementation Priority Order

1. <Component 1> -- prerequisite for everything else.
2. <Component 2> -- non-headline baselines.
3. <Component 3> -- ...

---

## 7. Paper Outline

```
1. Introduction
2. Background
3. <Method / formulation>
4. Methodology / algorithms
5. Test case
6. Experiments
7. Discussion
8. Conclusion + future work

Appendices: closed-form derivations / hyperparameters / implementation
notes / additional figures / reproducibility.
```

---

## 8. Figure List (target ~12-15)

- Fig 1. <Method illustration>.
- Fig 2. <Test case schematic>.
- ... (15-20 figure list)

---

## 9. Timeline

| Month | Milestone |
|:------|:----------|
| M1    | Survey complete; bibliography frozen; intro + background drafted. |
| M2    | Non-headline baselines shipped; Section 5 draft. |
| M3    | Headline experiments; first results figures; methodology section draft. |
| M4    | Ablations + sensitivity analyses. |
| M5    | Comparison-baselines reimplemented (if any). |
| M6    | Discussion section draft. |
| M7    | Full draft circulated to internal readers. Address feedback. |
| M8    | Polish, figures-final, appendix-final. |
| M9    | Submission. |

**Risk + buffer.** <Identify the dominant unknowns. Document fallback if
key milestones slip.>

---

## 10. Tracking and Cadence

- **This doc** (`PLAN.md`) is the contract; revise via PR-style edits
  and date-stamp changes.
- **Per-component sub-docs**: `notes/impl_<component>.md` for each new
  code component.
- **Per-paper-chunk sub-docs**: `notes/section_<N>.md` for each
  draft section's research notes.
- **Experiment results**: `experiments/$date_$algo_$variant/` with
  seed-by-seed JSON + plot scripts.
- **Figures**: `figures/` (build via matplotlib scripts checked into
  `experiments/`).
- **Drafts**: `drafts/main.tex` (or `drafts/main.md`); LaTeX project
  initialised when sections 1+2 are ready.
- **References**: `references/bibliography.bib` + `references/pdf/` +
  `notes/survey_*.md`. See `literature-survey` skill for the full
  workflow.

---

## 11. Open Questions

(Things deferred for later resolution; tracked here so they don't get
lost.)

1. <Question 1>
2. <Question 2>

---

*Created YYYY-MM-DD. Maintained by <name>.*
