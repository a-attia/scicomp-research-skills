# Project status: read this before relying on the framework

**As of 2026-10-14, this framework is still provisional, but most of
its content now rests on real use rather than prediction.** It was
built in four days of agent-assisted development (2026-05-13 to
2026-05-14) on the back of prior-art audits. Since then it has been
used on 14 real projects by its maintainer, and those projects have
logged roughly 150 feedback entries (as of 2026-10-14). What it still
lacks is any evidence from someone other than its author. This file
gives anyone discovering the repository an honest account of which
parts to trust and which to treat as informed guesses.

> **On project names.** Evidence below is counted, not attributed.
> The maintainer does not publish which projects use the framework,
> so this file and the rest of the repository refer to them by kind
> ("a software project", "a talk deck") rather than by name.

## Contents

- [What is well-grounded](#what-is-well-grounded)
- [What is informed prediction](#what-is-informed-prediction)
- [Evidence count](#evidence-count)
- [Roadmap to "no longer provisional"](#roadmap-to-no-longer-provisional)
- [What to expect](#what-to-expect)
- [What real use has shown](#what-real-use-has-shown)
- [How the framework grew this fast](#how-the-framework-grew-this-fast)
- [Other framing files](#other-framing-files)

---

## What is well-grounded

These parts have either an outside user base or repeated real use
behind them. Trust them at face value.

- **[`research-paper-writing`](skills/research-paper-writing/SKILL.md)**
  is vendored from
  [Master-cai/Research-Paper-Writing-Skills](https://github.com/Master-cai/Research-Paper-Writing-Skills),
  which has its own user base.
- **[`literature-survey`](skills/literature-survey/SKILL.md)**, steps 1
  to 5, was distilled from the literature survey of a real paper and
  has been reused since. *Exception:* Step 0 (finding candidate papers,
  [`references/literature-search.md`](skills/literature-survey/references/literature-search.md),
  added 2026-10-14) has not been used on a real project yet.
- **[`templates/paper-skeleton/`](templates/paper-skeleton/)** came from
  building one paper workspace and keeping what was useful. It works for
  scientific-computing papers with code, experiments, figures and
  drafts.
- **[`templates/software-skeleton/`](templates/software-skeleton/)**,
  Python branch. The `AGENTS.md` skeleton, the paper-coupling layer and
  the delegation to `scientific-python/cookie` have survived real
  codebases. The other language branches have not (see below).
- **The `notes/agent_feedback.md` journal habit.** Every project that
  adopted the framework kept one, which makes it the best-tested
  convention here.
- **Install tooling.** The `bin/install.sh` symlink wiring works on
  macOS with OpenCode, and `bin/uninstall.sh` has been exercised in a
  throwaway home directory. Skill frontmatter has been checked in CI
  since 2026-10-14 by the
  [validator workflow](.github/workflows/validate-skills.yml).

## What is informed prediction

These parts are reasoned from prior art and partly confirmed, but have
not been tested enough to trust without thought.

- **[`agent-resource-discipline`](skills/agent-resource-discipline/SKILL.md).**
  Individual rules have been sharpened by real failures, such as the
  PDF rule that extraction order is not visual order. The enforcement
  protocols (first action, last action, recitation) have not been
  measured in long sessions.
- **[`human-facing-doc-authoring`](skills/human-facing-doc-authoring/SKILL.md).**
  The universal conventions now carry rules written from real failures:
  no machine-local claims, the prose habits that read as
  machine-written, self-invalidating facts, and the cross-document
  audit. The per-document structure files (`readme-structures.md` and
  its siblings) remain guesses about what writers will reach for.
- **[`research-software-engineering`](skills/research-software-engineering/SKILL.md).**
  Four of twelve designed references have shipped, and none since
  2026-05-17. The other eight are specified but unwritten, and the
  specification may be wrong. See the skill's workflow table for the
  current list.
- **[`project-onboarding`](skills/project-onboarding/SKILL.md).** The
  bare-directory and single-agent-file paths have run on real projects.
  The mature-repository, non-standard-layout, multi-format and
  conflicting-conventions branches have not.
- **[`templates/software-skeleton/MULTI-LANGUAGE.md`](templates/software-skeleton/MULTI-LANGUAGE.md).**
  The Julia, C++, Rust, Fortran, MATLAB and Mathematica branches are
  informed by the audit, not by use.
- **The ready-to-paste onboarding prompts** in
  [`project-onboarding/references/migration-prompts.md`](skills/project-onboarding/references/migration-prompts.md).
  Only the discovery prompt is known to have been pasted by a real
  session.
- **The roll-up half of the feedback channel.** Journals fill up
  reliably. Turning them into upstream changes has happened once
  systematically (Session A, 2026-05-17) and otherwise piecemeal. See
  [What real use has shown](#what-real-use-has-shown).
- **The privacy scan** (`bin/privacy-scan.sh` and its hooks, added
  2026-10-14). It caught every planted case in testing and finds nothing
  in the current files, but it has not yet run on a real contribution.
  It only knows the names listed in each user's personal terms file.
- **[`research-slides-authoring`](skills/research-slides-authoring/SKILL.md)**
  (added 2026-10-14). Its rules come from about 30 real sessions across
  four projects in two toolchain lineages, so the content is grounded.
  The packaging is new: the phase gates, the consolidated rule set and
  `scripts/audit-pages.sh` have not yet been used on a real deck. The
  poster reference rests on a single poster.

## Evidence count

All counts are as of 2026-10-14. Recount from the sources named in the
last column before quoting them elsewhere.

| Signal | Count | Source |
|:---|---:|:---|
| Real projects using the framework | 14 | Per-project journals (names withheld) |
| Per-project feedback journals | 15 journals, about 8,800 lines, about 150 entries | Same |
| Findings applied upstream from project evidence | about 17 | [`CHANGELOG.md`](CHANGELOG.md) and `git log` |
| Systematic roll-up sessions | 1 | Session A, 2026-05-17 |
| Open GitHub issues | 2 | Of 7 filed: #2 closed by the privacy convention, #3 to #5 by the slides skill (2026-10-14) |
| Issues or pull requests from anyone but the maintainer | 0 | GitHub |
| Known external users who bootstrapped a project | 0 | (1 public fork exists) |

Still open: monograph writing (#1), deferred, and a peer-review pair
(a standing compliance checklist, #6, and an authorship-forensics
reference, #7). Implemented on 2026-10-14: the privacy convention (#2)
and slide authoring (#3, with evidence appends #4 and #5).

## Roadmap to "no longer provisional"

This file is retired, and replaced by a short status section in the
README, when all four conditions hold.

| # | Condition | Progress (as of 2026-10-14) |
|:--|:---|:---|
| 1 | At least 3 real research projects have used the framework end to end | **Met.** 14 projects use it, several end to end. |
| 2 | The roll-up procedure has produced at least 5 issues or PRs that pruned or refined the framework from real evidence | **Met in number, not in kind.** About 17 findings applied, all by the maintainer from his own projects. Independent feedback is still needed. |
| 3 | At least one external user has bootstrapped from a skeleton template | **Not met.** |
| 4 | The eight unshipped `research-software-engineering` references have each shipped or been formally dropped | **Not met.** Eight remain. None has been needed badly enough to write since 2026-05-17, which is itself evidence for dropping some. |

## What to expect

### If you start a new project against this framework today

Expect to:

- **Disagree with some rules.** Use the per-project `AGENTS.md`
  "Project-specific overrides" section freely. The rules are defaults.
- **Hit gaps.** Where a `research-software-engineering` reference is
  missing, fall back on the upstream sources it cites (the Scientific
  Python Development Guide, JOSS, Wilson et al. 2017, Bridgeford et al.
  2025).
- **Skip rules that do not fit yet.** Some content is too detailed for
  early work. Come back to it later.
- **Log what you notice** in `notes/agent_feedback.md`. That journal
  is what the improvement loop in [`CONTRIBUTING.md`](CONTRIBUTING.md)
  runs on, and an entry from someone other than the maintainer is the
  most valuable contribution this framework can receive.

### If you maintain a fork or vendor the skills

- **Expect breaking changes** as evidence prunes speculative content.
  `MULTI-LANGUAGE.md`, `project-onboarding` and the unshipped
  `research-software-engineering` references are the most likely to
  change shape.
- **Record the commit you copied from.** Pin it in your `AGENTS.md`, or
  stamp it into each vendored `SKILL.md`, so a later diff is possible.

### If you are an agent reading this for the first time

The skill content is still the canonical guidance, so follow it. When a
rule feels speculative or does not fit, **say so to the user** and
append an entry to the project's `notes/agent_feedback.md`, as
described in
`agent-resource-discipline/references/persistent-memory.md`.

---

## What real use has shown

Five months of use (2026-05-14 to 2026-10-14) produced these lessons
about the framework's shape. The first five came from the Session A
roll-up in May. The rest came later.

### From Session A (2026-05-17)

- **Onboarding has to trigger itself.** Without an auto-load trigger
  for directories lacking an `AGENTS.md`, an agent skipped onboarding
  and started drafting content. Skill descriptions now say when to load
  "even if the user does not ask".
- **Shell and cross-language boundaries produce the densest feedback.**
  One software project's six findings all sat at the boundary between
  bash, Python and YAML, which became
  `research-software-engineering` reference 12.
- **Rewriting a substantial document needs a content check.** A README
  rewrite lost nothing visible, but nothing could prove it. The
  content-check table in `human-facing-doc-authoring` now does.
- **Cited facts drift, and this repository's own status documents
  drift worst.** Keeping this file, the changelog and the README in
  step is what motivated the self-invalidation rule (K) and, later, the
  cross-document audit (L).
- **Audience facts belong in the per-project `AGENTS.md`**, so an agent
  does not spend a turn asking who the audience is.

### Since then (2026-05-20 to 2026-10-14)

- **Projects vendor the skills and stop refreshing.** At least two
  projects copied the skills into their own repository so that
  collaborators get them by cloning, then declared those copies locally
  maintained. Improvements made there reach this repository only when
  copied back by hand, and fixes made here do not reach them. The
  two-checkout model in [`AGENTS.md`](AGENTS.md) Section 2 does not
  describe this way of consuming the framework.
- **Projects write their own skills.** Two projects wrote five local
  skills between them, covering claim verification, slide and figure
  authoring, visual assets, and handling external code. Those are
  candidates for upstreaming, and they show where the shipped skills
  stop.
- **Feedback outpaces roll-up.** Journals grew to about 150 entries.
  Only one systematic roll-up has run, so most entries written after
  May have never been triaged against the framework.
- **Strict loaders fail silently.** Three `SKILL.md` descriptions did
  not parse as YAML for months, and one exceeded the length limit,
  because the regex-based loaders in daily use never noticed. A CI
  validator now catches both.
- **Slides and privacy keep coming back.** Slide-deck work recurs in
  the journals of several projects, and leaks of project-private detail
  into upstream-bound text recur in several more. These were the two
  open proposals with the most evidence (#3 and #2). Both shipped on
  2026-10-14: `AGENTS.md` Section 6.7 with the scanner, and the
  `research-slides-authoring` skill.

## How the framework grew this fast

The pattern that produced the current scope was:

1. The user asked "should we have X?"
2. The agent ran a prior-art audit and surfaced options.
3. The agent recommended the most thorough option, marked
   "(Recommended)".
4. The user picked it.
5. The agent shipped about 1,500 lines.
6. Repeat.

Each decision was defensible. Together they produced a framework that
encoded untested patterns, enforced conventions on hypothetical
projects, and was heavy to adopt. Real use has since confirmed some of
that content and left the rest untouched. The biggest risk is no longer
size alone. It is **the confidence that size projects onto the parts
that real use has not reached**, and this file exists to mark those
parts.

## Other framing files

- [`README.md`](README.md): human-facing entry point.
- [`AGENTS.md`](AGENTS.md): agent-facing entry point.
- [`CHANGELOG.md`](CHANGELOG.md): what changed, when and why.
- [`CONTRIBUTING.md`](CONTRIBUTING.md): the feedback channel.
- [`ATTRIBUTION.md`](ATTRIBUTION.md): lineage and cited sources.

---

*Created 2026-05-14 by A. Attia. Revised 2026-05-17 (Session A
roll-up). Revised 2026-10-14: recounted the evidence from all project
journals, marked retirement condition 1 as met, and added the lessons
learned since May. Project names were removed at the maintainer's
request, and the file gained a contents list and a roadmap table.
Maintained by A. Attia.*
