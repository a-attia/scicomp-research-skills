---
name: Numerical-correctness regression
about: A test that previously passed now fails, OR new evidence that an existing
       result is numerically wrong.
title: "[numerical-bug] <component>: <one-line description>"
labels: bug, numerical-correctness
---

## What is wrong

<One-paragraph description. Be specific. Examples:>

- A previously-passing MMS test now fails.
- A convergence-rate test now shows degraded order of accuracy.
- A conservation-invariant test now reports drift larger than the
  tolerance.
- A reproducibility check (running on the same commit + lockfile +
  seed) produces different results.
- A downstream user reports numerical results that contradict the
  library's documented behaviour.

## Component affected

- `src/<library>/<path>` (function / class / module).

## Reproduction

The minimum bar is **a runnable script + the expected output**. The
expected output should cite its source (analytical / MMS / reference
implementation / published benchmark / conservation invariant /
asymptotic relation) -- per the "no paper tests" rule of
`research-software-engineering/references/01-numerical-correctness.md`.

```python
# Minimal reproduction:
import <library_name> as <ln>
result = <ln>.<function>(...)
print(result)
# Expected:    <value> (source: MMS construction in tests/<file>.py;
#                       analytical formula derived in docs/<file>.md;
#                       reference implementation X at commit Y; ...)
# Actual:      <value>
```

## When the regression appeared

If known:

- **Last good commit**: `<hash>` (`<one-line commit message>`).
- **First bad commit**: `<hash>` (`<one-line commit message>`).
- **Bisect command**: `git bisect start <bad> <good>; git bisect run
  pytest tests/integration/test_<X>.py::test_<Y>`.

If not known: which library version / commit was the regression
observed against?

## Hypothesis (optional)

What the issue might be. Be honest about uncertainty. Examples:

- "Likely a sign error in the boundary-condition assembly added in
  commit X."
- "Possibly a floating-point regression from upgrading SciPy from
  1.10 to 1.13 (we test against `oldest` and `latest` in CI; only
  `latest` failing)."
- "Unknown; bisect needed."

## Severity

- [ ] **Critical**: a published result is wrong; needs erratum + tag
      + DOI for the corrected version.
- [ ] **High**: documented public-API behaviour is wrong; release
      blocked.
- [ ] **Medium**: internal-only consequence; fix before next release
      but not urgent.
- [ ] **Low**: edge case; fix when convenient.

## Originating context

If this regression surfaced from `notes/agent_feedback.md` or from
a paper-rebuttal session, paste the relevant entry here (sanitised
of unpublished-result details if applicable).
