# Project status -- read this before relying on the framework

**As of 2026-05-17, this framework is still provisional but has
begun accumulating real-project evidence.** It was built in 4 days
of intensive agent-assisted development (2026-05-13..2026-05-14)
with extensive prior-art audits, then exercised on two real
projects (argo-anywhere + AmigAI) during 2026-05-15..2026-05-17.
Session A on 2026-05-17 rolled the feedback from both projects
back into 7 commits of skill-content tightening (see
[`CHANGELOG.md`](CHANGELOG.md) 2026-05-17 section). This file
exists so anyone discovering the repo for the first time has
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
  + drafts. As of Session A (2026-05-17) the AGENTS.md template now
  includes the `Audience composition` field surfaced by AmigAI's
  feedback (F-18).

- **`templates/software-skeleton/`** has now been exercised on one
  real codebase (argo-anywhere); the AGENTS.md skeleton + paper-
  coupling layer survived contact with reality. The package-layer
  delegation to `scientific-python/cookie` worked. As of Session A
  (2026-05-17) the AGENTS.md template includes the same `Audience
  composition` field (F-18). The Julia / C++ / Rust / Fortran /
  MATLAB / Mathematica branches remain informed-prediction (see
  below).

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

- **`skills/research-software-engineering/`** -- 4 of the 11
  designed references have shipped as of 2026-05-17 (01 numerical-
  correctness, 02 testing-for-numerical-code, 11 ai-assisted-coding-
  rules, 12 shell-and-cross-language-interop; the last added by
  Session A consolidating 6 rules from argo-anywhere feedback). The
  other 7 are spec'd but not written, and the spec may be wrong.
  (For current count, see [`skills/research-software-engineering/SKILL.md`](skills/research-software-engineering/SKILL.md)
  workflow table.)

- **`skills/project-onboarding/`** -- the skill ran on two real
  projects (argo-anywhere, AmigAI) during 2026-05-15..2026-05-16
  and both surfaced actionable gaps (F-12 auto-load trigger for
  bare-of-AGENTS.md directories; F-02 content-check discipline for
  rewriting existing substantial docs). Session A applied both
  fixes. The remaining 5 scenario branches (1.B mature, 1.C non-
  standard, 2.B multi-format, 2.D conflicting-conventions) are
  still speculation.

- **`templates/software-skeleton/MULTI-LANGUAGE.md`** -- the Python
  default branch has been exercised on argo-anywhere; the Julia /
  C++ / Rust / Fortran / MATLAB / Mathematica branches remain
  informed by the audit but not by experience.

- **The 16 ready-to-paste prompts** (in
  `skills/project-onboarding/references/migration-prompts.md`,
  `skills/project-onboarding/SKILL.md`, `README.md`, `AGENTS.md`) --
  the bare-directory-discovery prompt was exercised on AmigAI
  (which triggered F-12); the remaining 15 prompts have not yet
  been pasted by a real user.

- **The upstream-feedback channel** (`CONTRIBUTING.md` +
  `.github/ISSUE_TEMPLATE/` + per-project `notes/agent_feedback.md`)
  -- has produced 2 substantive per-project journals (argo-anywhere:
  611 lines, 6 findings; AmigAI: ~1600 lines, multiple workflow
  gaps + 2 upstream-proposal drafts) and 3 GitHub issues (#1
  research-monograph-writing, #2 framework-privacy-enforcement, #3
  research-slides-authoring) as of 2026-05-17. The roll-up
  procedure has run once (Session A); the channel works.

### Honest evidence count

(As of 2026-05-17; see `CHANGELOG.md` for current counts if this
section has drifted.)

| Signal                                  | Count |
|:----------------------------------------|------:|
| Real research projects bootstrapped     |     2 |
| `notes/agent_feedback.md` entries logged | 2 files, ~2200 lines total |
| New-skill proposals filed (open)         |     3 |
| Skill-improvement issues filed           |    10 (F-02..F-19, applied in Session A) |
| PRs from external contributors           |     0 |
| Onboarding sessions executed             |     2 |
| Roll-up sessions executed                |     1 (Session A, 2026-05-17) |

**2 real-project sessions; both ran by the framework author.
External-user evidence: still 0.**

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

## What Session A learned (2026-05-17)

The first roll-up session produced these signals about the
framework's shape:

- **Onboarding-skill auto-load is load-bearing.** AmigAI revealed
  that without an auto-load trigger for bare-of-AGENTS.md
  directories, the agent will skip onboarding entirely and start
  drafting content. F-12 fixed this. Implication: skill
  descriptions need explicit "when to load EVEN IF the user
  doesn't ask" triggers, not just topical descriptions.
- **Shell + cross-language interop produces the densest feedback.**
  argo-anywhere's 6 rules all clustered in the bash/Python/YAML
  boundary -- YAML quoting, setdefault security defaults, error-
  message recovery hints, test stimulus, shell-script test
  mechanics, exit-summary scope-keying. This domain is dense
  enough to deserve its own reference (12) and likely more.
- **Rewriting substantial docs needs a content-check discipline.**
  argo-anywhere rewrote a README during migration without losing
  anything visible, but with no mechanism to PROVE the negative.
  F-02 ships the content-check-table discipline; the same pattern
  likely applies to PLAN.md updates, paper-section rewrites,
  rebuttal drafts.
- **Cited facts drift, and the framework's own docs are the
  worst offender.** Maintaining STATUS.md / CHANGELOG.md /
  README.md consistency across 7 commits in one session is itself
  the existence proof for F-17 (self-invalidation of cited facts).
- **The 3 NEW-SKILL proposals from Session A all sit below the
  evidence threshold.** Monograph (1 session), privacy (cross-
  cutting concern not specific to one skill), slides (1 session).
  F-19 ships an issue template that lets future sessions accumulate
  evidence without re-opening the proposals.
- **Audience composition belongs in per-project AGENTS.md.** AmigAI
  surfaced that audience-discovery interview turns are wasted when
  the audience facts can be captured once. F-18 added the field to
  both skeleton templates.

## Roadmap to "no-longer-provisional"

This file goes away when:

1. At least **3 real research projects** have used the framework
   end-to-end (2 of 3 reached as of 2026-05-17: argo-anywhere +
   AmigAI; 1 more needed).
2. The `agent_feedback` -> `CONTRIBUTING.md` roll-up procedure has
   produced **at least 5 issues / PRs** that pruned or refined the
   framework based on real evidence (10 of 5 reached as of
   2026-05-17 via Session A's F-02..F-19 commits; but they were
   all applied by the framework author rolling up his own
   feedback. Independent feedback still needed).
3. **At least one external user** has bootstrapped from
   `templates/{paper,software}-skeleton/` (proof the docs are
   adequate for someone other than the original author). Not yet
   reached.
4. The 7 still-unshipped `research-software-engineering/`
   references have either shipped (because real projects needed
   them) or been formally removed from the planned-references
   table (because they turned out not to be needed). 1 of 8
   shipped as of 2026-05-17 (reference 12); 7 remain.

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

*Created 2026-05-14 by A. Attia. Revised 2026-05-17 (Session A
roll-up: moved templates/software-skeleton/ AGENTS.md structure
+ project-onboarding partway from "informed prediction" to "well-
grounded" based on argo-anywhere + AmigAI evidence; updated
evidence-count table; updated retirement-conditions progress;
added "What Session A learned" section). This file lives until
the framework has accumulated enough real-project evidence -- and
specifically enough EXTERNAL-USER evidence -- to either justify
or prune the speculative content. If you start a real project
against the framework, please update `notes/agent_feedback.md` in
your project + roll relevant entries up here; that's how the
framework gets to "no-longer-provisional".*
