# Project status -- read this before relying on the framework

**As of 2026-05-14, this framework is in a deliberately provisional
state.** It was built in 4 days of intensive agent-assisted
development, with extensive prior-art audits at each step but
**ZERO real research projects have used it end-to-end yet**. This
file exists so anyone discovering the repo for the first time has
honest context for what they are looking at.

---

## What that means in practice

### What is well-grounded

- **`skills/research-paper-writing/`** is vendored from
  [Master-cai/Research-Paper-Writing-Skills](https://github.com/Master-cai/Research-Paper-Writing-Skills),
  which has its own user base + has been refined through real use.
  Trust this skill at face value.

- **`skills/literature-survey/`** was distilled from a real
  literature-survey workflow on the rl-oed paper (per its footer).
  The 5-step workflow is concrete + has been ground-truthed.

- **`templates/paper-skeleton/`** is the result of writing one paper
  workspace and recording what was useful. The structure works for
  scientific-computing paper repos with code + experiments + figures
  + drafts.

- **The basic `bin/install.sh` skill-discovery symlink wiring** for
  whichever agent client you actually use has been verified to work
  on macOS + the OpenCode skill ecosystem.

### What is informed prediction (NOT yet validated)

- **`skills/agent-resource-discipline/`** -- the rules are good and
  the prior-art audit (Anthropic context-engineering posts, Manus
  blog, planning-with-files, claude-mem) is solid; but the
  enforcement protocols (first-action / last-action / recitation)
  have not been tested in real long-running sessions yet.

- **`skills/human-facing-doc-authoring/`** -- the
  human-vs-agent-audience split is correct in principle; the
  per-doc-type structure files (`readme-structures.md`,
  `plan-structures.md`, `notes-structures.md`,
  `audit-log-structures.md`) are speculation about what users will
  reach for.

- **`skills/research-software-engineering/`** -- only 3 of the 11
  designed references actually shipped (01 numerical-correctness,
  02 testing-for-numerical-code, 11 ai-assisted-coding-rules). The
  other 8 are spec'd but not written, and the spec may be wrong.

- **`skills/project-onboarding/`** -- the entire skill (six files,
  ~2200 lines) is speculation about what migration scenarios look
  like. Zero migrations have happened.

- **`templates/software-skeleton/`** including `MULTI-LANGUAGE.md` --
  Python defaults are reasonable; Julia / C++ / Rust / Fortran /
  MATLAB / Mathematica guidance is informed by the audit but not by
  experience.

- **The 16 ready-to-paste prompts** (in
  `skills/project-onboarding/references/migration-prompts.md`,
  `skills/project-onboarding/SKILL.md`, `README.md`, `AGENTS.md`) --
  designed but not yet pasted by a real user.

- **The upstream-feedback channel** (`CONTRIBUTING.md` +
  `.github/ISSUE_TEMPLATE/` + per-project `notes/agent_feedback.md`)
  -- infrastructure for a feedback loop that has produced 0 entries
  so far.

### Honest evidence count

| Signal                                  | Count |
|:----------------------------------------|------:|
| Real research projects bootstrapped     |     0 |
| `notes/agent_feedback.md` entries logged |    0 |
| Issues filed against this repo           |    0 |
| PRs from external contributors           |    0 |
| Onboarding sessions executed             |    0 |

**0 real-project sessions across all signals.**

---

## How the framework grew this fast

Pattern that produced the current scope:

1. User asked "should we have X?"
2. Agent dispatched a prior-art audit, found the patterns, surfaced
   options.
3. Agent recommended the most-thorough option labeled "(Recommended)".
4. User picked "(Recommended)".
5. Agent shipped ~1500 lines.
6. Repeat.

Each individual decision was defensible. The cumulative effect is a
framework that:

- encodes patterns that have not been tested,
- enforces conventions on hypothetical future projects,
- is heavy enough that adopting it is non-trivial.

The framework's biggest current sin is not its size -- it is the
**false confidence its size projects**. This file exists to correct
that.

---

## What you should expect

### If you start a new project against this framework today

Good -- but expect to:

- **Disagree with some of the rules.** Use the per-project AGENTS.md
  "Project-specific overrides" section liberally; it exists for
  this. The rules are defaults, not commandments.
- **Hit gaps.** The 8 missing `research-software-engineering/`
  references will sometimes leave you without specific guidance;
  fall back on the cited upstream sources (Scientific Python
  Development Guide, JOSS, Wilson 2017, Bridgeford 2025).
- **Find rules you ignore.** Some skill content is too detailed for
  early-stage work. Skip; come back later if it becomes relevant.
- **Notice things that should be improvements.** Append entries to
  `notes/agent_feedback.md`; per-project journals fund the upstream
  improvement loop documented in `CONTRIBUTING.md`. **This is the
  most useful thing you can do for the framework right now.**

### If you maintain a fork

- **Expect breaking changes** in this upstream as we get real-project
  evidence and prune. The `templates/software-skeleton/MULTI-LANGUAGE.md`,
  the `project-onboarding` skill, and the unshipped
  `research-software-engineering/` reference plan are most likely
  to change shape.
- **Pin a commit hash** in your fork's `AGENTS.md` if you want
  stability over staying current.

### If you are an agent reading this for the first time

The skill content is still the canonical guidance. Follow it. But
when a rule feels speculative or doesn't quite fit the situation,
**surface that to the user explicitly** and append an entry to the
project's `notes/agent_feedback.md` (per
`agent-resource-discipline/references/persistent-memory.md`). The
user may need to revise the rule.

---

## Roadmap to "no-longer-provisional"

This file goes away when:

1. At least **3 real research projects** have used the framework
   end-to-end, with `notes/agent_feedback.md` entries showing what
   worked + what didn't.
2. The `agent_feedback` -> `CONTRIBUTING.md` roll-up procedure has
   produced **at least 5 issues / PRs** that pruned or refined the
   framework based on real evidence.
3. **At least one external user** has bootstrapped from
   `templates/{paper,software}-skeleton/` (proof the docs are
   adequate for someone other than the original author).
4. The 8 unshipped `research-software-engineering/` references
   have either shipped (because real projects needed them) or been
   formally removed from the planned-references table (because they
   turned out not to be needed).

When all four conditions hold, this file gets replaced by a normal
"Status" section in the README and the framework is no longer
provisional.

---

## Other framing files worth reading

- [`README.md`](README.md) -- human-facing entry point.
- [`AGENTS.md`](AGENTS.md) -- agent-facing entry point.
- [`ATTRIBUTION.md`](ATTRIBUTION.md) -- lineage from upstream
  Master-cai + cited sources (Anthropic engineering posts, Manus,
  Bridgeford 2025, Scientific Python Development Guide, etc.).
- [`CONTRIBUTING.md`](CONTRIBUTING.md) -- the feedback channel.

---

*Created 2026-05-14 by A. Attia. This file lives until the framework
has accumulated enough real-project evidence to either justify or
prune the speculative content. If you start a real project against
the framework, please update `notes/agent_feedback.md` in your
project + roll relevant entries up here; that's how the framework
gets to "no-longer-provisional".*
