# AI-assisted coding rules for science

Loaded on demand from the `research-software-engineering` skill at the
start of any agentic coding session on a scientific-computing project.

This reference is an **agent-actionable condensation** of the ten
rules in:

> Bridgeford EW, Sochat V, Markiewicz CJ, Zhang J, Ghosh S,
> Halchenko Y, Esteban O, Hanke M, Poldrack RA. *Ten Simple Rules
> for AI-Assisted Coding in Science*. arXiv:2510.22254 (2025).
> Companion Jupyter Book: https://poldracklab.org/10sr_ai_assisted_coding
> Zenodo: 10.5281/zenodo.17398109. **License: CC-BY 4.0.**

The Bridgeford et al. paper is the only peer-style reference written
**for the AI-assisted era specifically targeting scientists**, which
is why this skill leans heavily on it. We cite it explicitly per
CC-BY-4.0; quotations below are paraphrased + condensed for
agent-actionability, not verbatim.

This reference is structured as the ten rules, each with: (a) a
one-line statement, (b) the agent-action procedure, (c) the
sci-computing-specific elaboration (where applicable), (d) the
anti-pattern to refuse.

---

## Theme A: Preparation and understanding

### R1. Gather domain knowledge before implementation

**Statement.** Before writing or asking an AI to write code that
implements a scientific method, the agent must first establish what
the method IS (mathematics, conventions, units, sign conventions) and
how the literature uses it.

**Agent procedure.**

1. Locate the reference paper(s) for the method via the project's
   `references/bibliography.bib` and `notes/survey_<citekey>.md`. If
   the method is novel to this session, run the `literature-survey`
   skill first to produce the bib + survey note.
2. Identify the **conventions in use** (sign on the diffusion term;
   row-major vs column-major; index from 0 or 1; SI units or non-
   dimensional). Disagreements between the paper and the existing
   codebase are the source of half of all numerical bugs.
3. Identify the **expected behaviour at limits** (zero diffusivity,
   infinite domain, isotropic medium) -- these become the cheap
   sanity tests in `references/02-testing-for-numerical-code.md`.

**Sci-computing elaboration.** Many domains have multiple equivalent
formulations of the same method (e.g. the heat equation has flux-form
and conservation-form variants; the Laplacian has positive and
negative sign conventions). The agent must commit to one formulation
EXPLICITLY in the impl note + code docstring; mixing them silently
within a codebase is a frequent bug source.

**Anti-pattern.** "Let me just start implementing -- I'll figure out
the conventions as I go." The conventions decide the sign and shape
of every term; getting them wrong forces a full rewrite.

### R2. Distinguish problem framing from coding

**Statement.** "Problem framing" -- deciding what to compute, what
the inputs and outputs look like, what constitutes correctness -- is
a distinct activity from coding the implementation. Mixing them is
where AI-assisted code most often goes wrong.

**Agent procedure.**

1. Before writing any code, write a short **problem-framing block**
   in the response message OR in a `notes/impl_<component>.md`
   draft, covering: inputs (types, shapes, units, constraints);
   outputs (types, shapes, units); preconditions; postconditions;
   what success looks like (a specific test that would pass).
2. Confirm with the user that the framing matches their intent
   (especially for non-obvious cases: "should the boundary include
   the endpoints?", "is the input expected to be normalised?").
3. ONLY THEN start writing the implementation.

**Sci-computing elaboration.** The framing block for numerical code
must include the **mathematical statement** -- the equation being
solved, the discretisation choice, the boundary / initial conditions,
the units. A framing block that says "compute the heat equation
solution" is not framing; one that says
$\partial_t u = \nabla \cdot (\kappa(x) \nabla u) + f$, $\kappa \in
H^1(\Omega)$, $u(\cdot, 0) = u_0$, homogeneous Dirichlet on
$\partial \Omega$, second-order centred-difference in space,
backward-Euler in time, stable for $\kappa > 0$ ... IS framing.

**Anti-pattern.** Implementation-first ("write me a function that
solves the heat equation"). The agent should refuse and ask for
framing first.

### R3. Choose appropriate AI interaction models

**Statement.** Different sub-tasks call for different agent modes:
**conversational** (user-driven, agent suggests), **IDE assistant**
(inline completions, narrow scope), **autonomous agent** (multi-step
tool use, broad scope). Each mode has different failure modes.

**Agent procedure.** For each task, pick the right mode:

| Task                                                | Mode                       | Why                                                       |
|:----------------------------------------------------|:---------------------------|:----------------------------------------------------------|
| Drafting a new function                             | conversational             | Need user feedback on framing + acceptance criteria.      |
| Fixing a typo / renaming a variable                 | IDE assistant               | Narrow scope; low risk.                                    |
| Multi-file refactor with clear acceptance criteria  | autonomous agent (sandboxed) | Repetitive; verifiable end-state.                         |
| Debugging a numerical issue                         | conversational             | High risk; needs the user's domain knowledge in the loop. |
| Adding a test for known behaviour                   | autonomous agent           | Acceptance criterion is "test passes when code is right". |
| Implementing a new numerical method                 | conversational + framing   | High risk; framing must be confirmed before code.         |

**Sci-computing elaboration.** "Sandboxed" means: in a feature
branch, with a clean working tree, after a `git commit`, with an
explicit list of paths the agent may modify. Numerical code refactors
should NEVER run autonomously across more than one component without
intermediate test runs.

**Anti-pattern.** Setting up an autonomous agent on a numerical
codebase with broad permissions and no test gate. Even if every
individual change is correct, the cumulative effect is unverifiable.

---

## Theme B: Context engineering and interaction

### R4. Start by thinking through a potential solution

**Statement.** Before prompting an AI, think through a candidate
solution yourself. Identify what's known, what's unknown, what
constraints apply. The prompt then becomes "given this framing, fill
in the gaps" rather than "do the whole thing".

**Agent procedure.** When the user delegates a task, the agent should:

1. Sketch the solution outline in the response BEFORE writing code
   (1-2 paragraphs, or a numbered list).
2. Identify the parts the agent is confident about vs the parts it
   needs the user to confirm.
3. Ask one specific clarifying question if anything material is
   ambiguous.
4. Only then implement.

**Sci-computing elaboration.** For a numerical method, the sketch
should name: the discretisation choice, the solver choice, the
expected order of accuracy, the conservation properties, the
condition-number regime, the failure modes the agent is watching
for. If any of these is uncertain, ASK before implementing.

**Anti-pattern.** "Implement first, explain after." Or worse,
"implement first, never explain". The user needs to see the framing
to catch wrong assumptions cheaply.

### R5. Manage context strategically

**Statement.** AI agents have finite working memory. Manage it
deliberately: use external memory files (`PLAN.md`, `notes/`,
problem-solving scratch files), restate critical requirements
periodically, don't rely on the agent to remember decisions made 50
messages ago.

**Agent procedure.** **This entire concern is owned by the
`agent-resource-discipline` skill in this repository.** Specifically:

- `references/persistent-memory.md` -- first-action / last-action
  protocols, withdrawal-and-deposit metaphor.
- `references/context-window-budget.md` -- soft limits; topic-boundary
  unloading; recitation against goal drift.

Load `agent-resource-discipline` whenever R5 is in scope (which is
almost always for software sessions).

**Sci-computing elaboration.** For numerical work specifically,
critical requirements that the agent should restate every ~30 tool
calls in long sessions: the conventions chosen (R1), the framing
(R2), the test goals (R6), the open numerical-correctness concerns.

**Anti-pattern.** Continuing a 200-message session without
periodically re-reading `PLAN.md`. The `agent-resource-discipline`
recitation rule (Critical Rule 6 in that skill) addresses this.

---

## Theme C: Testing and validation

### R6. Implement test-driven development with AI -- and watch for "paper tests"

**Statement.** TDD is the standard tool for verifying code; with
AI, it becomes especially important because the AI may write code
that *looks* right but doesn't compute the right thing. The key
warning Bridgeford et al. raise:

> "AI may insert fabricated input values or dummy functions that
> appear to meet acceptance criteria but do not reflect true
> functionality. These 'paper tests' can be dangerously misleading."

**Agent procedure.** For any new numerical function:

1. Write a test FIRST that captures the desired behaviour. Cite
   the source of the expected value (analytical / MMS / reference
   implementation / published benchmark / conservation invariant /
   asymptotic relation -- see
   `references/01-numerical-correctness.md`).
2. Run the test; verify it FAILS (because the function is not yet
   implemented).
3. Implement the function.
4. Run the test; verify it passes.
5. Deliberately break the function (negate a sign, return zero);
   verify the test fails.
6. Restore the function; verify the test passes again.
7. Commit both the test and the implementation in the same commit.

**Sci-computing elaboration.** This is the single most important
discipline in this skill. The "paper tests" anti-pattern is more
dangerous in scientific code than in general software because:

- A test that passes silently because the expected value was
  fabricated will continue to pass forever, signalling correctness
  that doesn't exist.
- The downstream consumer (a paper, a follow-up project, a
  collaborator) will trust the test result.
- The bug is only discovered when an external reviewer runs an
  independent verification, which is rare.

**The defence is in `references/01-numerical-correctness.md`**:
every test asserting numerical equality must cite the source of
the expected value, in a comment immediately above the assertion.

**Anti-pattern.** "Run the code first, paste the output as
expected." The test is now incapable of detecting any bug present
when the test was written.

### R7. Leverage AI for test planning and refinement

**Statement.** AI is genuinely good at suggesting parameterised
tests, fixtures, mocks, and CI configurations. Use it for these.
Just don't use it to write the *expected values* in tests.

**Agent procedure.** When the user has a numerical function to test,
the agent can helpfully:

1. Suggest a test parameterisation matrix (input dimensions,
   parameter ranges, edge regimes) -- the agent picks the matrix
   shape; the user picks which cells to verify analytically.
2. Suggest fixtures (small mesh, deterministic RNG, golden output
   path).
3. Suggest pytest markers (`slow`, `gpu`, `mpi`).
4. Suggest GitHub Actions matrix configuration (Python versions,
   OS, oldest/latest deps).

What the agent must NOT do unsupervised:

1. Write the **expected values** in tests. Those come from
   analytical derivation / MMS / reference / benchmark / invariant
   / asymptotic -- per R6. The agent can write the test
   *infrastructure*; the *expected values* need explicit human
   provenance.

**Sci-computing elaboration.** The agent should propose finite-
difference gradient checks, MMS test scaffolds, conservation tests,
cross-implementation tests as standard suggestions for any numerical
function it's helping test. The skeletons are in
`references/02-testing-for-numerical-code.md`.

**Anti-pattern.** "Generate me 50 tests for this function." Those
50 tests will likely all be paper tests. Generate test STRUCTURE
in bulk; fill expected values one at a time with cited sources.

---

## Theme D: Code quality and review

### R8. Monitor progress and know when to restart

**Statement.** AI sessions accumulate context that can become
unhelpful. When a session has been thrashing on a problem for many
turns, **revert + restart with a clean context is often cheaper
than debugging in a polluted context.**

**Agent procedure.**

1. **ALWAYS commit working code before agentic changes.** A clean
   `git status` before starting an autonomous run is the safety net.
2. If a session goes off the rails (3+ consecutive failed
   attempts at the same fix; agent contradicting earlier statements;
   loss of thread): STOP, summarise the session into a status note
   for the next session (see `agent-resource-discipline` last-action
   protocol), `git reset --hard` to the last working commit, start
   fresh.
3. The "lesson learned" goes into the new session's first prompt
   as constraints / hints, NOT as a continuation of the old
   conversation.

**Sci-computing elaboration.** For numerical code, the failure mode
"agent fixes the symptom but breaks something else" is especially
expensive because numerical bugs can be silent (R6). After any
multi-attempt fix session, REVIEW THE TESTS: did the new code break
any test that was previously passing? Did any test suspiciously
change its tolerance or expected value?

**Anti-pattern.** Continuing to push on a problem the agent has
failed at 5 times. Each new attempt is more polluted by the failed
attempts; the cost-per-attempt rises while quality falls. Revert and
restart.

### R9. Critically review generated code -- "AI wrote it" is never an accountability defence

**Statement.** **Every line of code that ships is the human's
responsibility, period.** An AI's claim that "this is correct" is
not evidence; it's a starting hypothesis to verify behaviourally.

**Agent procedure.** For any non-trivial code the agent produces:

1. The user (or a designated reviewer) reads it.
2. The user RUNS the tests on the modified code; "the agent says
   the tests pass" is not enough. Verify.
3. For numerical code: the user runs at least one independent
   sanity check (a small problem with a known answer; a
   conservation check; a unit-check) before merging.
4. The commit message names the human author who reviewed +
   accepted the change. The AI is not a co-author per repo
   conventions.

**Sci-computing elaboration.** The downstream consumers of
scientific code (paper readers, reviewers, follow-up researchers)
will not have visibility into "this part was AI-generated". They
will assume scientific accountability for every result. The author
must therefore stand behind every line, AI-generated or not.

**The JOSS 2025+ AI-Usage Disclosure** (cited in
`references/01-numerical-correctness.md` "see also" via the JOSS
review criteria) makes this explicit at submission time: the
software paper must disclose how AI was used + how AI-generated
content was verified.

**Anti-pattern.** Merging code the user didn't read because "the
agent's tests pass". The agent's tests may be paper tests (R6); the
user must verify behaviourally.

### R10. Refine code incrementally with focused objectives

**Statement.** "Improve my codebase" is not a useful prompt.
"Refactor this 80-line function into smaller pieces while
preserving behaviour, with tests confirming behaviour is preserved"
is.

**Agent procedure.** When the user requests a non-trivial change:

1. Decompose into one-objective-at-a-time changes.
2. For each: state the objective + the acceptance criterion + the
   test that verifies it.
3. Implement one objective; verify; commit.
4. Move to the next.

**Sci-computing elaboration.** Numerical code is especially
vulnerable to "refactor + silent regression" because the regressions
are silent (R6). Therefore: any refactor of numerical code must
preserve the test-suite outputs bit-for-bit (or to a tolerance the
user explicitly approves). Run the full integration + e2e tests on
each refactor commit; do not batch refactor commits.

**Anti-pattern.** A single agentic session that touches 30 files
across 5 components and produces a single commit "refactored module
X". Each affected component should be a separate commit; each
commit should leave the test suite green.

---

## Theme E: Synthesis (our additions, not in Bridgeford)

### S1. Compose with `agent-resource-discipline` always

For software sessions, `research-software-engineering` and
`agent-resource-discipline` should be loaded together. The R5
context-management concern is owned by `agent-resource-discipline`;
the `references/persistent-memory.md` first-/last-action protocols
ensure the rules above survive across sessions.

### S2. Surface contradictions to the user

Per the universal "no silent action" rule (root `AGENTS.md`
Section 6 + `agent-resource-discipline` `references/persistent-memory.md`),
any contradiction the agent discovers (paper says one sign
convention, code uses another; existing test asserts X but the
analytical solution gives Y) must be surfaced to the user
explicitly. NEVER silently pick one side.

### S3. Append to `notes/agent_feedback.md` when rules misfire

When any rule above produced a confusing situation, an unhelpful
result, or a workaround the agent had to invent, append an entry
to the project's `notes/agent_feedback.md` per the
`agent-resource-discipline` skill's recording protocol. The
upstream `scicomp-research-skills` repository improves only when
real-project experience flows back; this skill is no exception.

---

## Quick-reference checklist for AI-assisted scientific coding

Before starting a new agentic coding session:

- [ ] R1: Domain knowledge gathered (paper / conventions /
      formulations explicit)?
- [ ] R2: Problem framed (inputs / outputs / preconditions /
      postconditions / success criterion)?
- [ ] R3: Right interaction mode chosen (conversational vs IDE vs
      autonomous)?
- [ ] R4: Solution sketched before prompting?
- [ ] R5: `agent-resource-discipline` loaded; first-action protocol
      executed?

During the session:

- [ ] R6: Test written FIRST with cited expected-value source?
- [ ] R6: Test confirmed to FAIL when code is broken?
- [ ] R7: Test STRUCTURE may be AI-suggested; expected VALUES are
      human-verified?
- [ ] R8: Working code committed before any agentic change?

After the session:

- [ ] R8: If session went off the rails, was reverted to last
      good commit + restarted clean?
- [ ] R9: User read every line; ran tests; ran one independent
      sanity check?
- [ ] R10: Refactors committed one-objective-at-a-time, each
      leaving tests green?
- [ ] S2: Any contradictions discovered surfaced to the user?
- [ ] S3: Feedback entries appended to `notes/agent_feedback.md`
      where applicable?

## Adjacent prior art + lineage

This reference is the agent-actionable codification of:

- **Bridgeford et al. 2025** -- *Ten Simple Rules for AI-Assisted
  Coding in Science*. arXiv:2510.22254. License **CC-BY 4.0**.
  Citation required; verbatim quotation is permitted with
  attribution. The rule numbering above (R1-R10) follows the
  paper exactly.
- **Russ Poldrack's *Better Code, Better Science* (2024)** -- free
  online book at `https://poldrack.github.io/BetterCodeBetterScience/`
  by the senior author of Bridgeford et al. Book-length treatment
  of the same argument.
- **Wilson et al. 2017** -- *Good Enough Practices for Scientific
  Computing*. PLOS Computational Biology. CC-BY. The pre-AI-era
  baseline; the JOSS 2025 AI-Usage Disclosure is a direct
  descendant of the recommendations in this paper.
- **JOSS review criteria** (2025+, with AI-Usage Disclosure
  required) -- `https://joss.readthedocs.io/en/latest/review_criteria.html`.
- **Scientific Python Development Guide / Principles**
  (`https://learn.scientific-python.org/development/principles/`,
  BSD-3-Clause) -- the testing + design principles cited in
  `references/01-numerical-correctness.md` and
  `references/02-testing-for-numerical-code.md`.
- **fcakyon/phd-skills** (MIT) -- ML-flavoured prior-art for
  agentic-coding-in-research; the structural patterns informed but
  did not originate the ones in this reference.

The full prior-art audit that informed this skill (covering ~30
sources) is referenced in the skill's main `SKILL.md` footer. The
audit's report is preserved in the dev-checkout's session history
but is not vendored here.

---

*Created 2026-05-13 by A. Attia. Faithful condensation + agent-
actionable elaboration of Bridgeford et al. 2025 (CC-BY 4.0).
Verbatim quotations of the paper appear in single-line italicised
form with explicit attribution; everything else is paraphrased +
elaborated for the scientific-computing-software context.*
