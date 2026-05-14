# Numerical correctness

Loaded on demand from the `research-software-engineering` skill when
the session involves writing, modifying, or reviewing code that
produces numerical results -- discretisations, solvers, Monte Carlo
estimators, autodiff gradients, optimisation routines, anything where
a wrong answer could pass casual inspection.

This is the highest-priority concern in scientific-computing software.
A program that crashes is annoying; a program that returns plausible
but wrong numbers is dangerous, because nobody notices until a
reviewer (or worse, a downstream user) does.

---

## The "paper tests" anti-pattern (Bridgeford 2025 R6)

Named in Bridgeford et al. 2025 "Ten Simple Rules for AI-Assisted
Coding in Science" (R6, CC-BY 4.0): **AI tools may insert fabricated
input values or dummy functions that appear to meet acceptance
criteria but do not reflect true functionality. These "paper tests"
can be dangerously misleading.**

Concrete examples in numerical code:

- A "convergence test" that asserts `error == 0.0` -- always passes
  regardless of whether convergence actually happens.
- A "solver test" that compares to a hard-coded `expected = 1.234`
  with no comment on where 1.234 came from -- becomes self-fulfilling
  the moment someone updates the code and the test.
- A "regression test" that calls `np.testing.assert_allclose(out,
  reference, atol=1e10)` -- the tolerance is so loose any change
  passes.
- A "gradient test" that compares two implementations of the same
  function to each other -- both can be wrong in the same way.

### The defence

**Every test that asserts numerical equality MUST cite the source
of the expected value, in a comment immediately above the
assertion.** Acceptable sources:

1. **Analytical solution** -- closed-form result derived by hand,
   with the derivation in a comment or a linked appendix.
2. **Method of manufactured solutions (MMS)** -- the expected
   value is constructed BEFORE the solver is run, by picking the
   solution and computing the matching forcing term (see
   "Method of manufactured solutions" below).
3. **Independent reference implementation** -- a different
   implementation, ideally in a different language or library, with
   the citation (paper, repository URL + commit hash) recorded.
4. **Published benchmark** -- a standard test problem with known
   results in the literature; cite the paper / Table / Figure.
5. **Conservation invariant** -- mass / energy / momentum / detailed
   balance / probability normalisation. The expected value is
   conserved (= initial value), not arbitrary.
6. **Asymptotic relation** -- the expected RATIO of two values
   (e.g. convergence rate $\propto h^p$), not an absolute value.

Example of the rule applied:

```python
def test_advection_diffusion_steady_state_mms():
    # MMS construction: u(x, y) = sin(pi*x) * cos(pi*y).
    # Forcing computed in test_helpers.mms_forcing, derived in
    # docs/mms_derivation.md (commit 4f3a2c1).
    u_exact = lambda x, y: np.sin(np.pi*x) * np.cos(np.pi*y)
    f = mms_forcing(u_exact, diffusivity=0.1, velocity=(1.0, 0.0))
    u_num = solve_advection_diffusion(forcing=f, ...)
    # L2 error should be O(h^2) for the linear-FE discretisation;
    # tolerance set to 5e-3 for h=1/32 based on convergence study
    # in tests/test_convergence.py::test_ad_l2_rate.
    assert l2_error(u_num, u_exact) < 5e-3
```

Versus the anti-pattern:

```python
def test_advection_diffusion_steady_state():
    u_num = solve_advection_diffusion(forcing=zeros, ...)
    # WHERE DID THIS COME FROM?
    expected = np.array([0.123, 0.456, 0.789])
    assert np.allclose(u_num, expected)
```

The first test fails when the discretisation is wrong; the second
test fails when the developer who wrote `expected` had a bug.

## Method of manufactured solutions (MMS)

The single most powerful technique for verifying discretisations.
Standard reference: Roache (2002) "Code Verification by the Method
of Manufactured Solutions" (J. Fluids Eng.).

### The procedure

1. **Pick a solution** $u_{\text{exact}}(x, t)$ that is sufficiently
   smooth, satisfies the boundary conditions you care about, and is
   non-trivial (not constant; not a polynomial of degree below the
   discretisation's exact-reproduction order).
2. **Compute the corresponding forcing** by substituting
   $u_{\text{exact}}$ into the differential operator. For
   $L u = f$, set $f = L u_{\text{exact}}$. This is symbolic
   differentiation; tools like SymPy automate it.
3. **Run the solver** with that $f$ as input.
4. **Compare** the numerical solution to $u_{\text{exact}}$ in the
   appropriate norm (L2, L-infinity, H1).

The test verifies that the discretisation actually solves the
equation: any bug -- in the assembly, in the boundary conditions,
in the time-stepping, in the linear solver -- shows up as a wrong
error.

### Why MMS beats hand-picked test problems

Hand-picked problems (e.g. "Burgers' equation with a known shock
solution") test only the regimes the picker thought of. MMS tests
**any** regime, including pathological ones the picker would not
have constructed. Picking a $u_{\text{exact}}$ with steep gradients,
high-frequency oscillations, or near-singular behaviour stresses
the solver in ways that real-application problems may not.

### Patterns

- **Polynomial $u_{\text{exact}}$**: catches base-case bugs but
  may pass trivially if the discretisation is exact for polynomials
  of that degree (Galerkin FE on polynomials of degree $\le k$).
- **Trigonometric $u_{\text{exact}}$**: standard choice;
  $\sin(k_x x) \cos(k_y y) e^{-\omega t}$ stresses spatial AND
  temporal discretisation. Vary $k_x, k_y, \omega$ to probe
  different regimes.
- **Combined $u_{\text{exact}}$**: e.g. polynomial + trigonometric,
  to test both regions where polynomials are exact and where they're
  not.

## Convergence-rate tests

The companion tool to MMS. Even more powerful for catching
discretisation bugs.

### The procedure

1. Pick the MMS problem (above).
2. Run on a sequence of meshes with refinement ratios 2 (or
   uniform $h, h/2, h/4, h/8$).
3. Compute the error $e_h = \|u_h - u_{\text{exact}}\|$ in each.
4. Compute the observed rate $p_{\text{obs}} = \log_2(e_h / e_{h/2})$.
5. Assert that $p_{\text{obs}}$ is close to the theoretical rate
   $p_{\text{theory}}$ (e.g. 2 for linear finite elements in L2).

A passing rate-test is much stronger evidence than a passing
absolute-error test: any bug in the assembly, BCs, or quadrature
typically degrades the rate from $p_{\text{theory}}$ to 1 or 0
(the rate is dimensionless and very sensitive).

### Tolerance setting

- Rate test typically asserts $|p_{\text{obs}} -
  p_{\text{theory}}| < 0.2$ on the second-finest level
  (asymptotic regime).
- DO NOT use $|p_{\text{obs}} - p_{\text{theory}}| < 1.0$ -- that
  would let a first-order bug pass for a second-order method.

### Example

```python
def test_poisson_convergence_rate_linear_fe():
    # MMS u_exact = sin(pi x) sin(pi y) on unit square,
    # forcing f = 2 pi^2 sin(pi x) sin(pi y), dirichlet BCs.
    h_seq = [1/8, 1/16, 1/32, 1/64]
    err = [l2_err(solve_poisson(h=h), u_exact) for h in h_seq]
    rates = [np.log2(err[i] / err[i+1]) for i in range(len(err)-1)]
    # Theoretical rate for linear FE in L2 is 2.
    # Last (asymptotic) rate must be within 0.2 of 2.
    assert abs(rates[-1] - 2.0) < 0.2, f"rates={rates}"
```

## Conservation-invariant tests

For codes where a quantity is mathematically conserved (mass, energy,
momentum, total probability, particle number), test that it is
**numerically** conserved to the expected precision over the run.

```python
def test_advection_mass_conservation():
    # No-source, periodic-BC advection conserves total mass.
    initial = setup_test_state()
    final = run_advection(initial, n_steps=1000)
    mass_drift = abs(total_mass(final) - total_mass(initial))
    # Relative drift should be at machine precision for the
    # second-order conservative scheme; allow 1e-12 for accumulation.
    assert mass_drift / total_mass(initial) < 1e-12
```

Conservation tests are cheap to add and catch a large class of bugs
(boundary conditions wrong, scheme not actually conservative,
floating-point cancellation issues).

## Symmetry / equivariance tests

For codes that should respect a symmetry (translation invariance,
rotational equivariance, reciprocity), test it explicitly.

```python
def test_helmholtz_reciprocity():
    # Reciprocity: Green's function G(x, y) = G(y, x) for the
    # adjoint-self-adjoint Helmholtz operator.
    G_xy = helmholtz_greens(source=x, observer=y, ...)
    G_yx = helmholtz_greens(source=y, observer=x, ...)
    assert np.isclose(G_xy, G_yx, rtol=1e-10)
```

## Determinism and seed discipline

### Default rule: deterministic

Test runs MUST be deterministic by default. Use fixed seeds for any
randomised algorithm. The test framework should fail loudly if
randomness leaks in.

```python
def test_monte_carlo_convergence():
    rng = np.random.default_rng(seed=12345)  # fixed seed
    estimate = mc_integrate(integrand, n_samples=10000, rng=rng)
    # Reference computed by trapezoidal rule with high N.
    assert abs(estimate - 0.7853981633974) < 1e-2
```

### Research runs: seed recorded, never the same seed twice

Production research runs (e.g. RL training, MCMC, ensemble methods)
use different seeds across replicates, but EVERY seed is recorded in
`experiments/<run-id>/metadata.json`. Reproducibility = "given the
recorded seed + recorded code commit + recorded environment, the
result is bit-for-bit reproducible". Not "rerun with the same
hyperparameters and you'll get the same number".

### Sources of non-determinism to audit

When debugging "why does this give different answers on different
runs?":

1. **Default RNG state**: NumPy / PyTorch / JAX have global RNG
   state; explicit seeding everywhere.
2. **Threading / parallelism**: BLAS thread count
   (`OMP_NUM_THREADS`), MPI message ordering, OpenMP reductions.
   Set thread count = 1 for tests; record thread count for runs.
3. **GPU non-determinism**: CUDA atomics, cuDNN benchmark mode,
   non-deterministic algorithm selection. Use
   `torch.use_deterministic_algorithms(True)` and document the
   performance cost.
4. **Floating-point order**: sums computed in different orders give
   different results to bit precision. Reductions, sparse-matrix
   products, multi-threaded accumulators.
5. **Library-version drift**: SciPy 1.10 and 1.11 may use different
   default solver choices. Pin versions in lockfile (see
   `references/05-reproducibility-infrastructure.md`).

## Floating-point gotchas every numerical-code agent should know

A small but high-leverage list:

1. **`==` on floats is almost always wrong.** Use `np.isclose` /
   `math.isclose` with explicit `rtol`/`atol`.
2. **`a + b - b != a` in general** for finite-precision floats.
   Catastrophic cancellation in subtraction of nearly-equal
   numbers; rearrange algebraically when possible.
3. **`sum([1e-9] * 10**9)` is not $10^9 \times 10^{-9} = 1$.**
   It's about $0.99999...$ depending on summation order. Use
   `np.fsum` or pairwise summation for long sums.
4. **`np.log(1 + x)` for small `x` is wrong.** Use `np.log1p(x)`.
   Same for `np.expm1`, `np.sqrt(1 + x) - 1`, etc. -- the standard
   library has special functions for the small-argument case.
5. **Subnormals are slow.** A reduction that produces denormalised
   floats (~$10^{-308}$) can be 100x slower than expected. Watch
   for this in expressions like
   `np.exp(-large_number) * np.exp(large_number)`.
6. **`int + float = float`.** Mixed-type arithmetic in NumPy
   silently promotes; for code that's supposed to be integer, this
   can cause surprising behaviour.
7. **NaN propagation.** `nan + 1 = nan`, `nan == nan = False`,
   `nan < x = False` for any `x`. A single NaN in the input can
   silently zero out an entire batch of results in
   `np.where`/`np.maximum`/`reduce` calls. Use `np.nan_to_num` /
   explicit handling.
8. **`np.float32` accumulators overflow earlier than expected.**
   `(1e20 * 1e20).astype(np.float32)` is `inf`. Mixed-precision ML
   especially. Use `dtype=np.float64` for accumulators in any
   reduction that crosses ~$10^7$ floats.

When the agent writes numerical code, mention which of these are
relevant + how the code handles them. Don't assume the user knows.

## Condition-number awareness

For any linear-algebra-dominant operation, the condition number of
the system bounds the achievable accuracy. The agent should:

1. **Estimate the condition number** when assembling a system, at
   least once during testing. SciPy: `np.linalg.cond(A)`. PETSc:
   `KSP` returns it via `ksp.getOperators()` + `mat.getCondNum()`.
2. **Warn (or fail) loudly when condition > 1e8 in single precision
   or > 1e16 in double precision.** Beyond these thresholds the
   solution is dominated by floating-point error and the system is
   effectively singular.
3. **For ill-conditioned problems**, apply standard remedies:
   regularisation (Tikhonov, truncated SVD), preconditioning,
   iterative refinement.
4. **Document the conditioning regime** of the test problems used.
   "MMS test passes with $\kappa(A) = 10^4$" is much more useful
   than "MMS test passes".

## Anti-patterns the agent should refuse

Modes the agent should refuse to enter:

- **Writing a test by running the code first and using the output
  as `expected`.** This is the "self-fulfilling test" anti-pattern;
  it locks in any bug present at the time of writing.
- **Loosening tolerances to make a failing test pass.** If a test
  starts failing, the agent should investigate WHY -- a bug, a
  legitimate algorithmic improvement, or a numerical-precision
  regression -- and document the resolution. Loosening without
  diagnosis is forbidden.
- **Adding `# noqa` or skipping a test that's flagging real
  numerical issues.** Same logic; surface to the user.
- **Using `np.allclose` with default `rtol=1e-5` for high-precision
  numerical work.** Default tolerances are convenient for ML, but
  for V&V of a discretisation, set tolerances based on a
  convergence study, not on the library default.
- **Testing autodiff against itself.** Comparing
  `forward_and_backward(x)[1]` to a numeric-gradient check should
  use finite-difference reference, not another autodiff
  implementation that may share bugs.

## See also

- `references/02-testing-for-numerical-code.md` -- the test-design
  patterns (3-tier suite, markers, finite-difference gradient
  checks, property-based for invariants) that codify the rules
  above.
- `references/11-ai-assisted-coding-rules.md` -- the Bridgeford
  rule R6 in full, plus the other nine rules.
- BSSw.io articles on "Definition and Categorization of Tests for
  CSE Software" -- the canonical V&V taxonomy
  (https://bssw.io/items/definition-and-categorization-of-tests-for-cse-software).
- Roache (2002) "Code Verification by the Method of Manufactured
  Solutions" -- the canonical MMS reference.
- Oberkampf & Roy (2010) *Verification and Validation in Scientific
  Computing* (Cambridge UP) -- book-length treatment of the V&V
  framework that grounds the rules above.

---

*Created 2026-05-13 by A. Attia. Borrows the "paper tests" framing
from Bridgeford et al. 2025 (CC-BY 4.0); the MMS / convergence-rate /
conservation-invariant patterns are standard in the
verification-and-validation literature (Roache 2002; Oberkampf & Roy
2010); the floating-point gotcha list distils common knowledge from
the NumPy / SciPy / IEEE-754 ecosystem.*
