# Agent feedback journal

This file is the per-project feedback channel into the
[`scicomp-research-skills`](https://github.com/a-attia/scicomp-research-skills)
repository. Entries here capture observations about how the shared
skills + conventions worked (or didn't) on this specific project, so
they can be rolled up periodically into upstream improvements.

> The agent (per `agent-resource-discipline/references/persistent-memory.md`)
> will append entries automatically when triggers below fire. Humans
> can also add entries any time. The roll-up procedure (sanitise +
> file an issue at scicomp-research-skills) is in
> `~/.scicomp-research-skills/CONTRIBUTING.md`.

## Entry triggers

The agent should add an entry when:

- it caught itself in a rationalization not covered by the
  `agent-resource-discipline` rebuttals table;
- a skill rule didn't apply cleanly to the situation;
- it discovered a useful pattern not yet codified in any skill;
- the user said "remember this feedback" or "this is worth noting";
- a step in a documented workflow failed or felt awkward;
- it had to invent a workaround that other projects would also need.

### Software-specific triggers

In addition to the universal triggers above, software projects bring
their own situations worth recording:

- a `research-software-engineering` rule did not apply cleanly to a
  domain-specific situation (PDE / inverse / OED / UQ / SciML
  variant);
- a numerical-correctness check (MMS / convergence-rate / invariant)
  was insufficient or produced ambiguous evidence;
- the "paper tests" guard (Bridgeford R6) caught a real instance --
  worth recording so the rule's defensive value is documented;
- the upstream template (`scientific-python/cookie` /
  `NLeSC/python-template` / `CU-DBMI/...`) had a gotcha during
  bootstrap that other projects would hit;
- a domain-library idiom (dolfinx / petsc4py / JAX-research-style)
  came up that isn't yet in
  `references/03-api-design-for-researchers.md` (planned);
- a reproducibility step (lockfile / Zenodo handshake / CITATION.cff)
  hit friction.

## Entry skeleton

Each entry is short (5-15 lines):

```markdown
## YYYY-MM-DD -- <one-line title>

**Project context**: <which sub-task, which session phase>.
**Trigger**: <agent-self-caught / user-flagged / external-failure / pattern-discovered>.
**Skill(s) involved**: <e.g. agent-resource-discipline, literature-survey>.
**Observation**: <what happened, in 1-3 sentences>.
**Proposed action**: <add rule X to skill Y / clarify Z / no change needed but worth noting>.
**Evidence / minimal repro**: <a code snippet, a quoted agent message, or "happened twice this session in <context>">.

Status: open
```

`Status:` transitions: `open` -> `rolled-up to issue #N` (after
filing upstream) -> `rolled-up to PR #N` -> closed (when the upstream
change has merged + been pulled into this project's canonical
checkout).

## Privacy

This file lives in the project repo (not upstream). Sensitive content
(unpublished results, reviewer identities, internal data) can appear
here freely; it's only the **roll-up step** that copies sanitised
versions to the public upstream issue tracker.

## Roll-up cadence

Suggested: review at the end of each major project milestone, OR at
least monthly for active projects. Prioritise patterns that recurred
3+ times or affected multiple sub-tasks.

---

## Entries

(Add entries chronologically below, newest at the BOTTOM. The first
real entry replaces this placeholder.)

## YYYY-MM-DD -- (template entry; delete when first real entry is added)

**Project context**: example sub-task.
**Trigger**: example-trigger.
**Skill(s) involved**: example-skill.
**Observation**: example observation.
**Proposed action**: example proposed action.
**Evidence / minimal repro**: none (template).

Status: template

---

*Created YYYY-MM-DD by <your name> from
[`scicomp-research-skills/templates/software-skeleton/notes/agent_feedback.md`](https://github.com/a-attia/scicomp-research-skills/tree/main/templates/software-skeleton/notes/agent_feedback.md).*
