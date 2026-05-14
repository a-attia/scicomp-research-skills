---
name: API ergonomics
about: A public-API choice is awkward, surprising, inconsistent, or under-documented.
title: "[api] <component>: <one-line description>"
labels: enhancement, api
---

## API surface affected

- `<library>.<function>` / `<library>.<Class>` / `<library>.<module>`.

Cite the location:

- Source: `src/<library>/<path>:NN`.
- Documentation: `docs/<path>` (if applicable).
- Tests covering this API: `tests/<path>` (if applicable).

## What is awkward

<One paragraph. Examples:>

- The function takes positional arguments where keyword-only would
  be safer.
- Two functions in the library use opposite sign conventions for the
  same quantity.
- The default value for parameter X is appropriate for use case A but
  surprises users in use case B (the more common one).
- The function returns multiple values without naming them; users
  consistently get the order wrong.
- The error message when the input is invalid does not name the
  invalid value or the constraint it violated.
- The function is documented but the example in the docstring no
  longer works.
- The behaviour is inconsistent with the analogous function in
  NumPy / SciPy / scikit-learn / dolfinx / petsc4py.

## Concrete example of the awkwardness

```python
# Code that runs but feels wrong:
result = <library>.<function>(<args showing the awkwardness>)
```

What does a user typically WANT to write but can't?

```python
# Code the user would prefer:
result = <library>.<function>(<args showing the desired API>)
```

## Proposed change (optional)

Be specific. Examples:

- Make `param` keyword-only by moving it after `*` in the signature.
- Rename `<old>` to `<new>` for consistency with NumPy convention.
- Change the default of `<param>` from `<X>` to `<Y>`; old callers
  override explicitly.
- Wrap the multi-return in a `dataclass` so users access by name.

If you have a draft of the new signature + docstring, include it.

## Backwards-compatibility plan

For any API change, name the deprecation path:

- [ ] **Pure addition**: new API added; old API unchanged. No
      deprecation needed.
- [ ] **Soft deprecation**: old API still works; emits
      `DeprecationWarning`; documented removal date / version.
- [ ] **Hard removal at next major version**: old API removed in
      `vN.0`; CHANGELOG entry naming the removal.
- [ ] **Breaking change at minor version**: justified only if the
      library is pre-1.0 OR the old behaviour was numerically wrong
      (in which case file a numerical-correctness-regression issue
      instead).

## Cross-references

- Style guide consulted: `research-software-engineering/SKILL.md`
  "Universal principles" + (when shipped) `references/03-api-design-for-researchers.md`.
- Idiom comparison: which other library does this well + how?

## Originating context

If this surfaced from `notes/agent_feedback.md` or from real user
feedback, paste the relevant entry here.
