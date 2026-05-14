# Testing for numerical code

Loaded on demand from the `research-software-engineering` skill when
the session involves designing, writing, or reviewing tests for
numerical code.

This is the operational companion to
`references/01-numerical-correctness.md`. The previous reference
defines the principles (paper-tests guard, MMS, convergence rates,
invariants); this one defines the test-suite *structure* that hosts
those principles -- where tests live, how they're named, how they're
selected and run, what shape they take in pytest / unittest.

The test-suite design here borrows heavily from the Scientific Python
Development Guide
(`https://learn.scientific-python.org/development/principles/tests/`,
BSD-3-Clause) and the pyOpenSci package guide
(`https://www.pyopensci.org/python-package-guide/tests/`).

---

## The 3-tier test suite

Adopted from the Scientific Python Development Guide. Every numerical
codebase should organise tests into three layers, each with different
purposes, audiences, and selection criteria.

```text
tests/
├── unit/             fast, isolated, "London-school" tests of
│                     individual functions and classes
├── integration/      multi-component tests; component-component
│                     and component-dependency interactions
└── e2e/              end-to-end tests on representative workflows
                     ("public interface" tests)
```

| Tier         | Purpose                                                               | Speed       | Selection                              |
|:-------------|:----------------------------------------------------------------------|:------------|:---------------------------------------|
| Unit         | Verify individual functions / classes in isolation. Heavy mocking.    | Fast (ms)   | Run on every push, every PR, every save. |
| Integration  | Verify component interactions + dependency-pinned behaviour.          | Medium (s)  | Run on every PR + at least nightly.    |
| End-to-end   | Verify representative workflows that real users actually run.         | Slow (min)  | Run on every PR; some on nightly only. |

### What each tier should and should not include

**Unit tests** cover the happy path of supported, documented behaviour
of one function. The Scientific Python Guide is explicit:

> "Avoid the temptation to test edge cases [in unit tests]! Focus on
> the happy-path. The Unit test should describe the expected and
> officially supported usage of the code under test."

Edge cases that the unit test discovers are signal -- they belong in
integration tests OR in the function itself as input validation. They
do NOT belong as a forest of `test_<function>_with_zero_input`,
`test_<function>_with_negative_input`, ... in unit-test files, which
ossify implementation details and slow refactoring.

**Integration tests** verify that components compose correctly + that
external dependencies (NumPy, SciPy, dolfinx, PETSc) behave as
expected when pinned at the lockfile version. Most of the
numerical-correctness tests from `01-numerical-correctness.md` (MMS,
convergence rates, conservation invariants) live here.

**End-to-end tests** run the workflows users actually run -- "load a
mesh, set BCs, solve, write output, verify output against a reference"
-- on small representative problems. These are slower (minutes) and
should be selectable separately from the fast unit suite.

### Marker discipline

Use pytest markers to allow per-tier selection:

```python
# tests/conftest.py
def pytest_collection_modifyitems(config, items):
    rootdir = pathlib.Path(config.rootdir)
    for item in items:
        path = pathlib.Path(item.fspath).relative_to(rootdir)
        if path.parts[1] == "unit":
            item.add_marker(pytest.mark.unit)
        elif path.parts[1] == "integration":
            item.add_marker(pytest.mark.integration)
        elif path.parts[1] == "e2e":
            item.add_marker(pytest.mark.e2e)
```

Plus per-test markers for cross-cutting concerns:

```python
@pytest.mark.slow         # >10s; skipped by default in `pytest -m "not slow"`
@pytest.mark.gpu          # requires CUDA; skipped on CPU-only CI
@pytest.mark.mpi          # requires mpirun + N>=2 ranks
@pytest.mark.online       # requires internet (rare in scientific code; flag)
```

Recommended pyproject.toml:

```toml
[tool.pytest.ini_options]
markers = [
    "unit: fast unit tests",
    "integration: cross-component integration tests",
    "e2e: end-to-end workflow tests",
    "slow: takes more than 10s",
    "gpu: requires GPU",
    "mpi: requires MPI",
]
addopts = ["-ra", "--strict-markers", "--strict-config"]
```

`--strict-markers` is critical: it forces every marker to be declared,
preventing typos like `@pytest.mark.flaky` from silently doing
nothing.

## Diagnostic tests (the fourth, special tier)

Adopted from the Scientific Python Guide. **Diagnostic tests** run on
the *installed* package in production / on a user's machine, with no
extra dependencies beyond the standard library.

Use case: a user installs your package via `pip install`, hits a
problem, and you want them to run `python -m yourpackage.diagnostics`
to verify whether the install is correct.

For scientific code, especially:

- "Does the GPU build actually link CUDA?"
- "Does my MPI build agree with serial on a 2-rank job?"
- "Does the linked BLAS deliver expected performance?"
- "Does the optional dependency X resolve to a compatible version?"

Diagnostic tests use stdlib `unittest` (not pytest) so they work
in stripped-down environments. Place them inside the package, not
under `tests/`:

```text
src/yourpackage/
├── __init__.py
├── core.py
└── _diagnostics.py    # python -m yourpackage._diagnostics
```

```python
# src/yourpackage/_diagnostics.py
import unittest

class DiagnoseInstall(unittest.TestCase):
    def test_imports(self):
        import yourpackage
        self.assertTrue(hasattr(yourpackage, "__version__"))

    def test_gpu_available(self):
        try:
            import torch
            self.assertTrue(torch.cuda.is_available(),
                            "GPU build but CUDA not available")
        except ImportError:
            self.skipTest("torch not installed")

if __name__ == "__main__":
    unittest.main()
```

## Test discipline rules (universal)

These are the rules that should fire regardless of which tier the
test belongs to.

### 1. Confirm the test fails when it should

The Scientific Python Guide makes this explicit and we restate it
here:

> "Any test case is better than none. As long as that test is
> correct... check that your test fails when it should!"

Every new test must be paired with a one-time check that it FAILS
when the code under test is broken. The agent's workflow:

```text
1. Write the test.
2. Deliberately break the code under test (e.g. negate a sign,
   remove a term, return zero).
3. Run the test; verify it fails with a clear message.
4. Restore the code; verify the test passes.
5. Commit both the test and the restored code.
```

This is the single best defence against the "self-fulfilling test"
anti-pattern (tests written by running the code first and recording
the output).

### 2. Tests cite their expected-value source

(See `01-numerical-correctness.md` "The defence" -- repeated here
because it applies to every numerical assertion in every tier.)

Every test that asserts numerical equality MUST cite the source of
the expected value, in a comment immediately above the assertion.
Acceptable sources: analytical solution, MMS, independent reference
implementation, published benchmark, conservation invariant,
asymptotic relation. Never a hand-picked number with no provenance.

### 3. Run the tests in CI before merging

Tests that run only on the author's machine are tests that will rot.
Every PR must run at least the unit + integration tier in CI on a
multi-OS, multi-Python matrix (typical: Ubuntu / macOS / Windows ×
Python 3.11 / 3.12 / 3.13 per SPEC 0). E2E and slow tests can run
nightly. See `references/06-ci-cd-for-research-code.md` (PR4) for
the GitHub Actions recipe.

### 4. Tests should produce structured failure messages

A test failure that says `AssertionError` is useless to a future
debugger. Every test failure should report:

- The actual value.
- The expected value.
- Where the expected value came from (cite from the test header).
- The tolerance / norm / ratio used.

NumPy's testing utilities do this for free; use `np.testing.assert_*`
over plain `assert` for arrays:

```python
# Bad
assert np.allclose(out, expected)

# Good (failure message includes mismatch indices, max abs/rel diff)
np.testing.assert_allclose(
    out, expected, rtol=1e-10, atol=0.0,
    err_msg="MMS solution against analytical sin(pi x) cos(pi y)"
)
```

## Test design patterns specific to numerical code

### Method of manufactured solutions (MMS) tests

Full treatment in `01-numerical-correctness.md`. Pytest skeleton:

```python
@pytest.mark.integration
@pytest.mark.parametrize("h", [1/8, 1/16, 1/32])
def test_poisson_mms(h):
    # MMS: u = sin(pi x) sin(pi y), f = 2 pi^2 sin(pi x) sin(pi y).
    u_num = solve_poisson(forcing=mms_forcing_poisson, h=h)
    err = l2_error(u_num, u_exact_poisson)
    # Asymptotic L2 error for linear FE: C * h^2.
    # C ~= 0.05 from convergence study; tolerance is 2x for safety.
    assert err < 0.1 * h**2
```

### Convergence-rate tests

Always parameterise over a sequence of $h$ values; compute observed
rates; assert against theoretical rate.

```python
@pytest.mark.integration
def test_poisson_convergence_rate_linear_fe():
    h_seq = [1/8, 1/16, 1/32, 1/64]
    err = np.array([l2_err_poisson(h) for h in h_seq])
    rates = np.log2(err[:-1] / err[1:])
    # Theoretical rate for linear FE in L2 is 2.
    np.testing.assert_allclose(
        rates[-1], 2.0, atol=0.2,
        err_msg=f"Asymptotic rate {rates[-1]:.3f} != theory 2.0; rates={rates}"
    )
```

### Finite-difference gradient checks

For autodiff code (gradients of objective functions, forward / adjoint
sensitivities), test against finite-difference reference. Standard
form:

```python
@pytest.mark.unit
def test_objective_gradient_fd():
    rng = np.random.default_rng(0)
    x = rng.standard_normal(10)
    g_ad = autodiff_gradient(objective, x)
    eps = 1e-6
    g_fd = np.array([
        (objective(x + eps * e_i) - objective(x - eps * e_i)) / (2 * eps)
        for e_i in np.eye(len(x))
    ])
    # Centred FD has O(eps^2) truncation error; for eps=1e-6, ~1e-12.
    # Roundoff at this eps ~ machine_eps / eps = 2e-16 / 1e-6 = 2e-10.
    # Tolerance dominated by roundoff: 1e-7 is comfortable.
    np.testing.assert_allclose(g_ad, g_fd, rtol=1e-7,
                                err_msg="autodiff vs finite-diff gradient")
```

For high-dimensional $x$, sample a few directions rather than checking
all dimensions; record the seed.

### Property-based tests for invariants

For invariants (mass conservation, symmetry, equivariance,
positive-definiteness, monotonicity), use Hypothesis to generate
inputs:

```python
import hypothesis.strategies as st
from hypothesis import given

@pytest.mark.integration
@given(initial_mass=st.floats(min_value=0.01, max_value=100.0),
       n_steps=st.integers(min_value=10, max_value=1000))
def test_advection_conserves_mass_property(initial_mass, n_steps):
    state = uniform_state(total_mass=initial_mass)
    final = run_advection_no_source(state, n_steps=n_steps)
    drift = abs(total_mass(final) - initial_mass) / initial_mass
    assert drift < 1e-12
```

Hypothesis will explore the input space and shrink failures to
minimal repro cases. Especially valuable for code with
many-dimensional input spaces.

### Regression tests against golden output

For complex pipelines where MMS / closed-form is impractical
(realistic geometry, real data), record a "golden output" once,
manually verify it's correct, commit it, then test against it on
every change.

```python
@pytest.mark.integration
def test_full_pipeline_golden():
    out = run_full_pipeline(input_path="tests/fixtures/small.h5")
    expected = np.load("tests/fixtures/golden_small.npy")
    # Tolerance set by convergence study (ref commit f4a2c1e):
    # changes within 1e-8 are noise; larger changes need investigation.
    np.testing.assert_allclose(out, expected, atol=1e-8, rtol=1e-8,
                                err_msg="pipeline output vs golden")
```

Golden-output discipline:

1. **Cite the verification source.** A comment on the golden file
   names how it was verified -- typically a one-time MMS or
   cross-implementation check.
2. **Update goldens deliberately.** When a code change legitimately
   changes the golden output (algorithm improvement, dependency
   update with known impact), update + commit the golden in a
   SEPARATE commit, with the regenerate-script command in the
   commit message: `tests/regenerate_goldens.sh`.
3. **Never auto-regenerate.** A `pytest --update-goldens` flag is
   tempting and forbidden; it defeats the purpose of golden tests.

### Cross-implementation tests

When two implementations of the same algorithm exist (e.g. a fast
JAX-jit version and a slow reference NumPy version, or a serial and
MPI version), test that they agree on representative inputs.

```python
@pytest.mark.integration
def test_serial_vs_mpi_agreement():
    # Run a small problem in both; results should agree to roundoff.
    out_serial = solve_serial(small_problem())
    out_mpi = solve_mpi(small_problem(), n_ranks=4)
    # Tolerance allows for non-associative-sum order differences;
    # 1e-12 is comfortable for double-precision PDE solves.
    np.testing.assert_allclose(out_serial, out_mpi, rtol=1e-12,
                                err_msg="serial vs MPI(4) result drift")
```

This catches a large class of parallelisation bugs (incorrect halo
exchanges, accumulation order, race conditions).

## Pytest configuration patterns

### Useful fixtures

```python
# tests/conftest.py

@pytest.fixture(scope="session")
def deterministic_rng():
    """Single deterministic RNG for the whole test session."""
    return np.random.default_rng(seed=12345)

@pytest.fixture
def small_mesh(tmp_path):
    """Tiny mesh for fast tests."""
    mesh_file = tmp_path / "small.msh"
    write_unit_square_mesh(mesh_file, n=4)
    return mesh_file

@pytest.fixture(autouse=True)
def reset_blas_threads():
    """Force single-threaded BLAS for determinism."""
    os.environ["OMP_NUM_THREADS"] = "1"
    yield
    # No teardown needed; subprocess-isolated.
```

### Useful pytest plugins

- **`pytest-xdist`** -- parallel test execution. Caveat:
  unsafe with tests that share global state (BLAS thread count,
  GPU device); use `--dist=loadfile` to keep tests within a file
  on the same worker.
- **`pytest-cov`** -- coverage reporting. Numerical code coverage
  is a noisy metric (most lines are exercised by happy-path tests);
  use as a directional indicator, not a gate.
- **`hypothesis`** -- property-based testing. See
  "Property-based tests for invariants" above.
- **`pytest-benchmark`** -- microbenchmarks with statistical
  comparison; useful for performance-regression CI gates.
- **`syrupy`** -- snapshot testing. Useful for golden-output tests
  with structured (non-array) outputs.

### Useful CI matrix dimensions for scientific code

```yaml
strategy:
  matrix:
    python: ["3.11", "3.12", "3.13"]    # SPEC 0: last 3 minor versions
    os: [ubuntu-latest, macos-latest, windows-latest]
    deps:
      - oldest    # minimum supported versions of NumPy / SciPy / etc.
      - latest    # current versions
```

The "oldest vs latest dependencies" axis is critical for scientific
code: many bugs are version-sensitive. Pin minimums in
`pyproject.toml` `dependencies =`; install with
`uv sync --resolution=lowest-direct` for the "oldest" cell.

## Anti-patterns the agent should refuse

- **`pytest.skip` without a clear `reason=`.** Every skip should
  name the condition and the path to un-skipping
  (`reason="needs CUDA; install pytorch-cu12 to enable"`).
- **`@pytest.mark.xfail` as a way to "fix" a failing test.** xfail
  is for known bugs that the team has decided to track but not fix
  yet; document the issue number. Never use xfail to ignore.
- **`try: ... except: pass` inside test bodies.** A test that
  silently absorbs exceptions is a test that always passes.
- **Flaky tests.** A test that "sometimes passes" is worse than
  no test; either fix the flakiness (usually a race condition or
  RNG issue) or remove the test.
- **Testing private functions.** Tests should exercise the public
  API. Tests of private internals (functions starting with `_`)
  ossify implementation details and discourage refactoring.
- **One huge test that asserts 50 things.** Split into multiple
  focused tests; on failure, the diagnosis is much faster.

## Self-review checklist after writing tests

Before commit:

- [ ] Each test failure produces a structured message (not just
      `AssertionError`).
- [ ] Each numerical assertion cites its expected-value source in a
      comment.
- [ ] Each test has been confirmed to FAIL when the code under test
      is broken (then restored + re-verified).
- [ ] Tests are placed in the correct tier (`unit/`, `integration/`,
      `e2e/`).
- [ ] Tests have appropriate markers (`@pytest.mark.slow`, `gpu`,
      `mpi`).
- [ ] Random seeds are fixed.
- [ ] No `pytest.skip` / `@pytest.mark.xfail` without a clear reason.
- [ ] No `try: ... except: pass` blocks.
- [ ] No test of a private function.
- [ ] CI configuration covers the relevant matrix dimensions
      (Python versions, OS, oldest/latest deps).

## See also

- `references/01-numerical-correctness.md` -- the principles
  (paper-tests guard, MMS, convergence rates, invariants) that
  every test in this reference operationalises.
- `references/11-ai-assisted-coding-rules.md` -- Bridgeford R6
  ("paper tests" warning) + R7 ("Leverage AI for test planning
  and refinement") apply throughout this reference.
- Scientific Python Development Guide / Principles / Tests
  (`https://learn.scientific-python.org/development/principles/tests/`,
  BSD-3-Clause) -- the upstream source for the 3-tier suite +
  marker discipline + "confirm the test fails" rule + diagnostic
  tests pattern.
- pyOpenSci package guide / tests
  (`https://www.pyopensci.org/python-package-guide/tests/`) --
  alternative organisation of the same material with broader
  packaging context.
- BSSw.io "Definition and Categorization of Tests for CSE Software"
  (`https://bssw.io/items/definition-and-categorization-of-tests-for-cse-software`)
  -- canonical V&V taxonomy that grounds the unit/integration/e2e
  split in scientific terminology (verification, validation,
  acceptance, regression).

---

*Created 2026-05-13 by A. Attia. The 3-tier suite + marker discipline
+ "confirm the test fails" + diagnostic-tests pattern are adapted
from the Scientific Python Development Guide (BSD-3-Clause) with
attribution. The numerical-test patterns (MMS, convergence rate,
finite-difference gradient check, property-based for invariants,
golden output, cross-implementation) are standard in V&V literature
(Roache 2002; Oberkampf & Roy 2010); the agent-actionable framing is
new to this skill.*
