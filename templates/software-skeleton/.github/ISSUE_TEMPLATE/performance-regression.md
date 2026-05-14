---
name: Performance regression
about: An operation got slower, used more memory, or scaled worse.
title: "[perf] <component>: <one-line description>"
labels: performance
---

## What got slower / heavier / less scalable

<One paragraph. Be specific: which operation, on what input, by how
much, on what hardware.>

## Component affected

- `src/<library>/<path>` (function / class / module).

## Reproduction

The minimum bar is **a runnable benchmark + a reference number**.
Use `pytest-benchmark`, `airspeed-velocity`, or a hand-rolled timing
script -- whatever the project standardises on.

```python
# Minimal reproduction:
import time
import <library_name> as <ln>

t0 = time.perf_counter()
for _ in range(N):
    result = <ln>.<function>(<args>)
elapsed = time.perf_counter() - t0
print(f"elapsed: {elapsed:.3f}s")
# Reference:    <X.X>s on <hardware>, <library version>, commit <hash>.
# Observed now: <Y.Y>s on <same / different hardware>, current commit.
```

## When the regression appeared

If known:

- **Last fast commit**: `<hash>` (`<one-line commit message>`,
  baseline: `<X.X>s`).
- **First slow commit**: `<hash>` (`<one-line commit message>`,
  observed: `<Y.Y>s`).
- **Bisect command**: `git bisect start <bad> <good>; git bisect run
  <benchmark-script>`.

## Memory profile (if relevant)

```text
Before: peak <X> MB
After:  peak <Y> MB
```

Use `memray`, `tracemalloc`, or `/usr/bin/time -v`.

## Scaling profile (if relevant)

How does the issue depend on:

- Problem size (mesh size, number of degrees of freedom, batch size)?
- Number of MPI ranks / OpenMP threads / GPUs?
- Sparsity / density of inputs?

A small table is often easier to read than prose:

| problem size | before (s) | after (s) | ratio |
|:-------------|-----------:|----------:|------:|
| N=100        |       0.12 |      0.13 |  1.08 |
| N=1000       |       1.20 |      4.50 |  3.75 |
| N=10000      |     120.0  |   1500.0  | 12.5  |

A regression that grows with problem size is much more concerning
than a constant-factor slowdown.

## Hypothesis (optional)

What the issue might be. Examples:

- "Likely an accidental Python loop introduced in commit X where the
  vectorised version used to be."
- "Possibly a NumPy 2.0 behaviour change in the way ufuncs handle
  output buffers; we test against `oldest` and `latest`."
- "Cache-miss pattern changed when the array layout switched from C
  to Fortran order."

## Severity

- [ ] **Critical**: blocks running representative problems on the
      target hardware (OOM, runs > N hours that used to take
      minutes).
- [ ] **High**: noticeable in production use; needs fix before next
      release.
- [ ] **Medium**: noticeable in benchmarks; fix when convenient.
- [ ] **Low**: micro-optimization; track but don't block.

## Acceptable trade-offs (optional)

Sometimes a regression is the price of a correctness fix. If you
already know:

- "We accept this slowdown because the previous code was numerically
  wrong; tracked in #<numerical-correctness-issue>."
- "Acceptable for CPU; need to fix for GPU."
- "Acceptable in single-precision; not in double."

## Originating context

If this surfaced from `notes/agent_feedback.md` or from a user
benchmark report, paste the relevant entry here.
