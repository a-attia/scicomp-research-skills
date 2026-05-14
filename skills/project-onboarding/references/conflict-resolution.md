# Conflict resolution

Loaded on demand from the `project-onboarding` skill alongside
`references/scenario-2-existing-agentic-files.md` whenever the audit
finds existing project conventions that disagree with the framework's
universal conventions.

This is the reference for **how to surface and resolve conflicts**
without losing the user's existing intent. The mechanism is the
per-project `AGENTS.md` "Project-specific overrides" section, which
is the formal home for approved deviations from the framework's
universal rules.

---

## Core principle: per-project overrides are normal

The framework's universal conventions (root `AGENTS.md` Section 6)
are **defaults**, not commandments. Per-project AGENTS.md files MAY
deviate from them, and the formal mechanism for doing so is the
"Project-specific overrides" section.

Concretely, root `AGENTS.md` Section 3 already states:

> **Universal rule**: when in doubt, the project's `AGENTS.md` and
> `PLAN.md` override any conflicting guidance from this repository.
> This repository provides defaults; projects own their specifics.

So a project with a "Project-specific overrides" section saying "we
use 4-space indent, not the framework's default" is **not a broken
project** -- it's a project exercising the override mechanism
correctly.

The agent's job during conflict resolution is therefore not to
"enforce" the framework rule. It is to:

1. Surface the conflict to the user with both rules cited.
2. Help the user articulate the intentional deviation.
3. Record the deviation in "Project-specific overrides" with a
   one-line rationale.
4. Proceed with the user's choice.

---

## How to surface a conflict

When the audit finds a project convention (in an existing
agent-file, in a CONTRIBUTING.md, in code style settings, in
verbal conversation with the user) that disagrees with a framework
convention, the agent should produce a structured surfacing in the
response message:

```text
CONFLICT DETECTED
-----------------
Framework rule (root AGENTS.md Section 6):
  "<exact text of framework rule>"

Project rule (<source>):
  "<exact text of project rule>"

These rules give different answers for: <specific situation>.

Recommended resolutions (pick one or propose your own):
  (a) Adopt the framework rule. (Drop the project rule;
      the framework convention applies.)
  (b) Adopt the project rule. (Add to "Project-specific
      overrides" with rationale; the project rule applies.)
  (c) Compromise. (Articulate a third position that handles
      both concerns; document in "Project-specific overrides".)

Which would you like to do?
```

The agent waits for the user's answer before proceeding. The agent
never silently picks one side.

## How to record an override

When the user picks (b) or (c), the deviation goes in per-project
AGENTS.md "Project-specific overrides" section in the following
format:

```markdown
## Project-specific overrides

(Anything that differs from the universal conventions in
`~/.scicomp-research-skills/AGENTS.md` Section 6. If nothing differs,
write "None".)

### Override: <one-line title> (decided YYYY-MM-DD)

**Framework rule** (`~/.scicomp-research-skills/AGENTS.md`
Section 6, "<rule heading>"):

> "<exact text of framework rule>"

**Project rule**:

> "<exact text of project rule>"

**Rationale**:

<One paragraph: why this project deviates. Examples: legacy code
already uses the deviating convention; collaborator prefers the
deviating convention; the framework rule was wrong for this domain;
the deviation was decided before the framework was adopted.>

**Scope**:

<Which parts of the project this override applies to. Sometimes the
deviation only applies to one subsystem.>
```

This format makes the override:

- **Visible** -- a future agent reads "Project-specific overrides"
  and immediately sees what deviates.
- **Justified** -- the rationale is preserved.
- **Auditable** -- the date is recorded; the framework rule is
  quoted; future-you can re-evaluate later if the framework's rule
  changes.

## Common conflicts + standard resolutions

The audit will most often find these conflicts. Use these as
templates for new ones.

### Conflict A: encoding rules

**Framework**: "ASCII only in code, code comments, and code-style
docstrings."

**Common deviations**:
- Project allows Unicode in code comments for non-English
  collaborator names.
- Project uses Unicode mathematical symbols in scientific code
  (e.g. Greek letters as variable names).

**Standard resolution**: usually (b) -- add the override; specific
scope (e.g. "Unicode allowed in docstrings; ASCII only in code
identifiers").

### Conflict B: emoji rules

**Framework**: "No emojis in code, code comments, code docstrings,
and production documentation, unless the user explicitly requests
them."

**Common deviations**:
- Internal team uses emojis in PLAN.md status indicators.
- Status badges in README use emojis (CI status, code quality, etc.).

**Standard resolution**: usually (b) -- emojis allowed in non-
production docs; ASCII or markdown badges in production-facing docs.

### Conflict C: commit message style

**Framework**: "Conventional commit style preferred (`feat: ...`,
`fix: ...`, `docs: ...`) but not enforced."

**Common deviations**:
- Project has its own prefix taxonomy (`R&D:`, `BUG:`, `DOC:`,
  `MAINT:`).
- Project requires JIRA issue ID prefix.
- Project requires a body (multi-line commits) for every commit.

**Standard resolution**: usually (b) -- record the project's
convention; the framework's preference is genuinely "preferred not
enforced", so this is a soft conflict.

### Conflict D: AI co-authorship attribution

**Framework**: "no `Co-Authored-By` trailers" + "agents do not
create git commits unless the user explicitly requests it".

**Common deviations**:
- Project policy requires explicit AI-co-authorship trailer
  (e.g. for compliance with funder rules).
- Project requires AI-generated code to be marked with a comment.

**Standard resolution**: usually (b) -- the deviation is justified
(funder compliance, IRB requirements, etc.); record + apply.

### Conflict E: file-edit tool preference

**Framework** (from `agent-resource-discipline`): "Use dedicated
tools (`Read` / `Grep` / `Glob` / `Edit` / `Write`) over Bash
equivalents."

**Common deviations**:
- Project's CI / pre-commit hooks rely on Bash tools' specific
  output format.
- Team's preferred reviewer uses Bash tools and wants commit history
  to mirror that.

**Standard resolution**: usually (a) -- the framework rule is
about agent behaviour, not commit history; the deviation is usually
resolvable by updating the CI scripts to be tool-agnostic.

### Conflict F: testing / numerical-correctness rules

**Framework** (from `research-software-engineering`): "Every test
asserting numerical equality MUST cite the source of the expected
value."

**Common deviations**:
- Existing tests have no citations (legacy from before the rule
  existed).
- Tests use library-defaults tolerances (`np.allclose(...)`) without
  explicit tolerance justification.

**Standard resolution**: usually (a) -- the framework rule is
correct; the right action is to **plan a back-fill** rather than
permanently override. Add an `[onboarding-debt]` tag to existing
tests in a follow-up pass; resolve over time.

This conflict is unusual in that the right answer is "adopt the
framework rule, but we acknowledge we have legacy debt". Record
the debt in `notes/agent_feedback.md` or in a dedicated
`notes/_onboarding_debt.md` tracker.

### Conflict G: layout conventions

**Framework**: paper-skeleton expects `drafts/`, software-skeleton
expects `src/`.

**Common deviations**:
- Project uses `paper/` instead of `drafts/`.
- Project uses `code/` instead of `src/`.
- Project has all source at repo root (no `src/` layout).

**Standard resolution**: usually (b) for the first two; the
deviation is purely cosmetic. For the third (no `src/` at all),
consider whether refactoring to a `src/` layout is worth it; if not,
record the override.

---

## Anti-patterns to refuse

- **"This conflict is small; let me silently pick the framework
  rule."** No. Even small conflicts must be surfaced to the user;
  silent picks erode trust.
- **"The user obviously meant the framework rule; let me apply
  it."** No. The user might have reasons we don't know. Ask.
- **"Two project rules disagree with each other; I'll pick the
  newer one."** No. Surface BOTH conflicts (the project-vs-project
  conflict + each project-vs-framework conflict) to the user; the
  user decides.
- **"The override section is for advanced users; let me not bother
  documenting the deviation."** No. The override section is the
  formal mechanism precisely so future-you knows why the project
  deviates. Skipping documentation defeats the audit trail.
- **"This deviation is one-off; let me apply it just for this
  commit."** No. If a deviation is necessary, document it; if it's
  not, don't apply it. There's no third "stealth deviation" option.

## When conflicts indicate the framework should change

Sometimes a conflict reveals that the framework's universal rule is
wrong (or under-specified) for a particular domain. When you
encounter the same conflict pattern across multiple projects, that's
a signal to feed back upstream.

The mechanism: append an entry to the project's
`notes/agent_feedback.md` describing the conflict + the resolution.
Periodically the maintainer rolls these up + considers whether the
framework's rule should evolve. See `~/.scicomp-research-skills/CONTRIBUTING.md`
for the roll-up procedure.

This is the loop that keeps the framework's universal conventions
honest: project-specific overrides reveal which rules are too rigid,
and the framework's universal section evolves over time to reduce
the override surface.

## Cross-references

- `references/scenario-2-existing-agentic-files.md` -- the parent
  scenario (Sub-case 2.D references this file).
- `references/existing-project-audit.md` -- the inventory step that
  surfaces conflicts in the first place.
- `references/migration-prompts.md` -- includes a prompt for "the
  audit has surfaced a conflict; help me resolve it."
- Root `AGENTS.md` Section 6 -- the universal conventions whose
  rules these conflicts deviate from.
- Root `AGENTS.md` Section 3 -- the explicit statement that
  per-project AGENTS.md and PLAN.md override the shared repo's
  guidance.
- Root `CONTRIBUTING.md` -- the upstream-feedback channel for when
  the same conflict pattern recurs across projects.

---

*Created 2026-05-13 by A. Attia.*
