---
name: agent-resource-discipline
description: Use this skill at the start of any non-trivial session in this ecosystem -- it is the single biggest lever for reducing token / quota / context-window consumption and for keeping the agent productive across sessions. Make sure to load this whenever the work will involve more than a few file reads, any PDF handling, multi-file editing, web fetching, or continuation of work from a prior session, EVEN IF THE USER DOES NOT MENTION IT. The skill codifies five disciplines -- tool selection (Read/Grep/Glob/Edit/Write over Bash equivalents), PDF lifecycle (one-shot pdftotext + survey-note-first lookup), persistent memory across sessions via the project's indices (PLAN.md / collection log / notes index), context-window budgeting, and web-fetch caching -- as a research-paper / research-software-flavoured operationalisation of the file-as-memory + just-in-time retrieval patterns from Anthropic's context-engineering guidance and the Manus / planning-with-files / claude-mem prior art (see "Adjacent prior art + lineage" inside the skill for citations).
license: MIT
metadata:
  audience: any agent operating in this ecosystem
  domain: agent-tooling
  origin: A. Attia (added 2026-05-13)
---

# Agent Resource Discipline

## How this skill is organised (progressive disclosure)

This skill follows the **three-level progressive disclosure** pattern
codified by Anthropic's `skill-creator` (see "Adjacent prior art +
lineage" below):

- **Level 1 (always in context once the skill is loaded)**: this
  `SKILL.md`, ~250 lines. Contains the universal rules + the
  decision-procedure for which references to consult.
- **Level 2 (loaded on demand by name)**: the `references/*.md` files
  -- one per discipline. Loaded only when a session actually exercises
  that discipline.
- **Level 3 (planned future work)**: enforcement hooks (SessionStart /
  PreToolUse / Stop) that mechanise the protocols here so they fire
  reliably without depending on agent discipline alone. Specification
  in section "Planned future work: enforcement hooks" below.

This is the same pattern the skill itself preaches: load only what you
are about to use; defer the rest.

## When to load this skill

Load this skill at the start of any session that will involve any of:

- reading or grepping more than ~5 files;
- handling PDFs (literature survey, related work, supplementary
  material);
- editing or creating files in multiple project sub-directories;
- web fetching (publisher pages, arXiv, GitHub, doc sites);
- working across multiple agent sessions on the same project (where
  cross-session memory matters).

In practice that's most non-trivial sessions in this ecosystem. The
universal one-liners in `~/.scicomp-research-skills/AGENTS.md`
Section 6 cover the basics so cheap-and-fast rules fire even without
this skill loaded; this skill expands them with the full how-to.

## Why this matters

Agent tokens / quota / context-window are the scarcest resources in any
non-trivial session. Beyond raw cost, the **attention budget** -- the
agent's ability to pick the right detail out of its context -- degrades
faster than the nominal context window suggests. Empirical work
(Chroma's "context rot" study, cited by Anthropic in their Sep 2025
*Effective Context Engineering for AI Agents* post) shows that recall
quality drops well before the window fills. Heavily-loaded contexts
also introduce *recency bias* and *goal drift*. This skill therefore
optimises for both raw token cost AND for keeping the working set
small enough that the agent's attention stays sharp.

Default agent behaviour wastes resources in predictable ways:

- **Tool mis-selection** (`bash grep` instead of the dedicated `Grep`
  tool, `bash cat` instead of `Read`, ...) costs tokens AND loses
  features (paging, structured results).
- **Bulk reads** (`Read` with no offset/limit on a 2000-line file when
  50 lines would do) burn context window for no gain AND accelerate
  context rot.
- **Re-derivation** (re-reading a PDF that was already summarised in a
  survey note last session) wastes tokens AND risks contradicting the
  prior summary.
- **Forgetting** (not reading PLAN.md / collection log / notes index
  at session start) causes the agent to either re-do work or to make
  decisions inconsistent with prior sessions.
- **Re-fetching** (calling WebFetch on the same URL twice in one
  session) burns external quota and adds latency.
- **Goal drift in long sessions** -- the original PLAN.md fades from
  recent attention as conversation length grows. Manus calls this the
  "lost-in-the-middle" failure mode and addresses it via *recitation*
  (re-reading the plan into recent context).

These are all preventable with explicit rules. This skill codifies
them as a research-flavoured operationalisation of the broader
file-as-memory + just-in-time retrieval patterns now standard in the
agent-engineering literature.

## The five disciplines

This skill loads a small SKILL.md (you are reading it) and provides
five per-topic reference files, each loaded on demand. Each codifies
one resource-management discipline:

| Discipline               | Reference file                          | When to load                                      |
|:-------------------------|:----------------------------------------|:--------------------------------------------------|
| Tool selection           | `references/tool-selection.md`          | First time in this session you need a non-trivial file/search/edit operation. |
| Targeted reads           | (covered in tool-selection.md)          | (same)                                            |
| PDF lifecycle            | `references/pdf-lifecycle.md`           | Whenever a session involves PDF intake or re-reading. |
| Persistent memory        | `references/persistent-memory.md`       | Start of any session on a project with PLAN.md / collection log / notes index. |
| Context-window budget    | `references/context-window-budget.md`   | When loading multiple skills, multiple reference files, or multiple PDFs simultaneously. |
| Web-fetch discipline     | `references/web-fetch-discipline.md`    | Whenever WebFetch is called in this session.      |

Load only the references relevant to the current session. Do NOT load
all five at once -- that defeats the purpose.

## Critical rules (apply unconditionally; do not require loading a reference file)

These are also in `~/.scicomp-research-skills/AGENTS.md` Section 6, so
they fire even if this skill is not loaded. Restated here for
in-skill reference:

1. **Use dedicated tools, not Bash equivalents.**
   - File search: `Glob` (not `find` / `ls -R`).
   - Content search: `Grep` (not `bash grep` / `bash rg`).
   - File read: `Read` (not `cat` / `head` / `tail`).
   - File edit: `Edit` (not `sed` / `awk`).
   - File create: `Write` (not `cat <<EOF` / `echo >`).
   - User communication: response text (never `echo` / `printf`).
2. **Batch independent tool calls into a single message.** A message
   with three independent `Read`s costs less and finishes faster than
   three sequential messages.
3. **Read targeted, not bulk.** For files >300 lines, use `Grep` first
   to locate the relevant section OR `Read` with explicit
   `offset`+`limit`. The default 2000-line `Read` is for skimming, not
   routine consumption.
4. **Re-use prior work before generating new work.** Before re-reading
   a PDF, check `notes/survey_<citekey>.md`. Before re-deriving a
   fact, check the audit log / notes / PLAN.md.
5. **Indices are the persistent memory.** Read `PLAN.md` status +
   `_collection_log.md` + `notes/README.md` at session start; update
   them at session end if work was done.
6. **Recitation in long sessions.** For sessions exceeding ~50 tool
   calls, re-read `PLAN.md` (or the relevant section thereof) every
   ~30-50 calls to combat goal drift. The Manus team identified this
   as the simplest defence against the "lost-in-the-middle" failure
   mode in long agent runs. Recitation is cheap; goal drift is
   expensive.
7. **Do not edit `AGENTS.md` or system-prompt-equivalent files
   mid-session.** If the agent client uses prompt caching (Claude Code
   does, OpenCode does for Claude models), editing the cached prefix
   invalidates the cache and silently 10x's the per-token cost of all
   subsequent calls in the session. Restart the session if you
   genuinely need to change agent-facing rules.
8. **Keep errors in the conversation; do not silently retry.** When a
   tool call fails (dead URL, rate limit, file not found), let the
   error sit in the conversation so the model adapts. Silent retry
   loops both burn quota and hide useful failure signal. For
   structural failures (a citation's PDF really is unobtainable, an
   arXiv ID is wrong), log to the appropriate audit entry
   (`_collection_log.md` "Items not found / left for user", `PLAN.md`
   "Open Questions") so the failure becomes part of the persistent
   record.

### Note on prompt caching

OpenCode (and Claude Code, and Cursor) on Claude models supports
**prompt caching** of stable prefixes (system prompt + tools +
typically the most recently loaded skill content). Cached tokens are
~10x cheaper than uncached. Implication: re-loading a small skill via
`Read` mid-session is **cheaper than carrying its content forward in
conversation**, because the cached version pays cached-rate on every
subsequent turn. This is part of why the progressive-disclosure model
above works: levels 2 + 3 can be loaded fresh when needed without
worrying that they'll dominate cost.

## Common rationalizations + rebuttals

The agent will, in real sessions, invent plausible-sounding reasons
to skip the disciplines above. The pattern is sufficiently consistent
that we name + rebut the common ones explicitly. When the agent
catches itself thinking one of these, it should treat that thought
as a signal to STOP and re-evaluate.

| Rationalization                                                   | Why the agent thinks it                                            | Rebuttal                                                                                                       |
|:------------------------------------------------------------------|:-------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------|
| "I already read this file last turn; I'll trust my memory."      | Avoids the cost of re-`Read`-ing.                                  | The file might have been edited (by you or the user). `Read` is cheap; recall is not always reliable.          |
| "It's just one extra `bash cat`, no big deal."                   | The override feels small in isolation.                             | This is the rationalization that turns a 200-token session into a 20k-token session. One bash-cat is fine; the habit isn't. |
| "Let me re-read the PDF to make sure the survey note is right."  | Healthy scepticism + low confidence in your own past summaries.    | If you have specific reason to doubt the note, target-grep the `.txt` for the suspect fact. If not, trust the note; that's what it's for. Re-reading the whole PDF "to be safe" is the most expensive single action in this ecosystem. |
| "I'll load all the section references now so I have them ready." | Tidy-up instinct; wants to "set up" before working.                | Loading speculatively is the failure mode the context-window-budget exists to prevent. Load when you actually use. |
| "I'll fetch the publisher page to confirm the year."             | Wants external verification; doesn't trust local data.             | The user verified the bib entry; that's what verification IS. Trust the bib unless you have specific reason to doubt it. |
| "I'll skip updating `notes/README.md`; it's just an index."      | The deposit feels like overhead at the end of a session.           | The deposit funds the next session's withdrawal. Skipping it is the most expensive bug in this ecosystem.       |
| "I'll process all 14 PDFs now while I have momentum."             | Wants to batch-finish a sub-task.                                  | Process one at a time; close each before opening the next. The context-window cost of 14 simultaneous `.txt` files is much larger than the round-trip cost of 14 separate `Read`s. |
| "Let me just retry that fetch, it might work this time."         | Hope-based rather than evidence-based.                             | Twice per session is the cap. After that, log to "Items not found" and move on.                                |
| "I'll silently fix this typo in the bib."                         | Helpful instinct; wants to clean up.                               | Silent fixes break the audit trail. Add a "Corrections to apply" entry; let the user batch-apply.              |
| "It's a small task; the protocol overhead would dominate."       | Wants to skip first-action / last-action for speed.                | A genuinely small task (one file edit, one question answered) is fine. Anything multi-file or multi-step earns the protocol's overhead back several times over. |

If you (the agent) find yourself thinking ANY of the left-column
phrases mid-session, stop and re-read this table.

## First-action protocol (every non-trivial session)

At the start of any session that touches a project with the standard
layout (paper-skeleton or similar):

1. **Load** (in parallel, single message): `AGENTS.md`, `PLAN.md`
   (status fields + open questions), `references/_collection_log.md`
   (verification status), `notes/README.md` (which surveys exist +
   their status). Total: 4 small reads.
2. **Decide** which skills the session actually needs (research-paper-
   writing? literature-survey? human-facing-doc-authoring? this skill?
   often only 1-2 are relevant -- not all of them).
3. **Decide** which references this session needs from each loaded
   skill (e.g. just `references/introduction.md` from
   research-paper-writing, not the whole references/ tree).
4. **Then** start the user's actual task.

Step 1 is cheap (4 small reads) and prevents the most common waste
mode: doing work the previous session already did, or doing work
inconsistent with what the previous session decided.

## Last-action protocol (every session that produced work)

Before declaring the session done:

1. **Update the indices** that record this session's output:
   - new survey notes -> add row to `notes/README.md`.
   - new bibliography entries / verifications -> append to
     `references/_collection_log.md`.
   - status change -> update the relevant `PLAN.md` status field.
   - new section drafted -> mark in `PLAN.md` outline + maybe add
     `notes/section_<N>.md`.
2. **Surface contradictions** explicitly. If something this session
   discovered contradicts prior notes / plan / bib entries, do not
   silently proceed; add a "Corrections to apply" entry to the
   relevant log.
3. **Report** to the user what was done + what indices were updated.

Steps 1+2 are the "deposit" that funds the next session's cheap
"withdrawal" via the first-action protocol.

## Output contract

When this skill is loaded, every action the agent takes should be
auditable against the rules above. If the agent finds itself about
to:

- run a Bash command that has a dedicated-tool equivalent -> stop and
  use the dedicated tool.
- do a bulk `Read` of a >300-line file -> stop and either `Grep` first
  or use `offset`+`limit`.
- re-read a PDF that has a survey note -> stop and read the note first.
- start work without reading `PLAN.md` / `_collection_log.md` /
  `notes/README.md` -> stop and read them (in parallel).
- finish work without updating those same indices -> stop and update.

The goal is **no avoidable waste**, not "minimise tokens at the cost
of correctness". When the rules conflict with correctness, correctness
wins -- and the conflict gets logged as a "Corrections to apply" entry
so the rule can be refined.

## Tool-availability assumptions

This skill assumes the agent has tools approximately equivalent to
OpenCode's `Read`, `Grep`, `Glob`, `Edit`, `Write`, `Bash`, and
`WebFetch`. For agents with more limited toolsets:

- **Shell-only agents** (some Claude Code tool configs): use
  `pdftotext`, `rg`, `fd`, `sed`/`awk` carefully (quote everything;
  prefer here-docs over `echo` chains; cap output with `head`/`tail`
  EXPLICITLY rather than relying on the agent's truncation).
- **Agents without WebFetch**: load `references/web-fetch-discipline.md`
  for the protocol of caching fetches into the repo via shell commands
  (`curl` -> `references/_cache/<hash>.html`).
- **Agents without parallel tool calls**: serialise; the parallelism
  rule simply does not apply, but the targeted-read and re-use-prior-work
  rules still do.

## Adjacent prior art + lineage

This skill is a research-flavoured aggregation of patterns that have
crystallised across the agent-engineering literature since mid-2025.
Citations are given so users (and future maintainers) know what we
borrowed, what we adapted, and where the genuinely novel pieces are.

**Foundational sources (cited in the rules above):**

- **Manus team blog post** -- *Context Engineering for AI Agents:
  Lessons from Building Manus*
  (`https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus`).
  Source for the file-as-memory pattern (rule 5 of their post),
  recitation against goal drift (rule 4 -> our Critical Rule 6),
  KV-cache stability (rule 1 -> our Critical Rule 7), and
  keep-errors-in-context (rule 5 -> our Critical Rule 8).
- **Anthropic engineering: *Effective Context Engineering for AI
  Agents*** (Sep 2025,
  `https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents`).
  Source for the "attention budget" framing in "Why this matters",
  the "context rot" empirical finding (Chroma research,
  `https://research.trychroma.com/context-rot`), and the hybrid
  pre-load + just-in-time retrieval pattern that underlies our
  first-action protocol.
- **Anthropic engineering: *Equipping agents for the real world with
  Agent Skills*** (Oct 2025,
  `https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills`).
  Source for the three-level progressive-disclosure pattern this
  skill follows; informs the SKILL.md length budget guidance in
  `references/context-window-budget.md`.
- **Anthropic engineering: *Writing effective tools for agents -- with
  agents*** (Sep 2025,
  `https://www.anthropic.com/engineering/writing-tools-for-agents`).
  Tool-author-side counterpart of our discipline 1; informs why
  dedicated `Read`/`Grep`/`Glob` are higher-signal than Bash
  equivalents.
- **MemGPT paper** (Packer et al. 2023, arXiv:2310.08560,
  `https://arxiv.org/abs/2310.08560`). Academic ancestor of all
  subsequent file-as-memory patterns; introduces the
  OS-memory-hierarchy framing.

**Closest comparable agent-rule skills:**

- **`OthmanAdi/planning-with-files`**
  (`https://github.com/OthmanAdi/planning-with-files`) -- 3-file
  workflow (`task_plan.md` / `findings.md` / `progress.md`) enforced
  via SessionStart / PreToolUse / Stop hooks. The hook-enforcement
  pattern is the model for our planned future work below; their
  evidence-based 96.7% pass-rate (vs 6.7% baseline) is what motivates
  shipping hooks rather than relying on agent discipline alone.
- **`thedotmack/claude-mem`**
  (`https://github.com/thedotmack/claude-mem`) -- automated
  observation capture into SQLite + Chroma vector DB with lifecycle
  hooks. We deliberately diverge: our markdown-on-disk approach is
  git-diffable, blameable, and human-readable, which matters more for
  research reproducibility than the higher recall of an embedding
  store. Both approaches are valid; pick by use case.
- **`addyosmani/agent-skills`**
  (`https://github.com/addyosmani/agent-skills`) -- 22 production-
  engineering skills with anti-rationalization tables in every skill;
  we adopted that pattern explicitly in "Common rationalizations +
  rebuttals" above.
- **`anthropics/skills/skill-creator`**
  (`https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md`)
  -- the authoritative how-to-write-a-skill skill; informs our
  three-level progressive-disclosure structure and the "pushy
  description" anti-undertriggering convention applied to this
  skill's own description.
- **`Future-House/paper-qa` (PaperQA2)**
  (`https://github.com/Future-House/paper-qa`) -- programmatic RAG
  over PDFs (parse + cache + embed + retrieve). Solves the same
  problem as our PDF lifecycle (avoid re-reading PDFs) with a
  fundamentally different mechanism (vector embeddings vs human-
  curated survey notes). Our `references/pdf-lifecycle.md` discusses
  the trade-off explicitly; both approaches are valid.

**Where we are genuinely novel** (per the prior-art audit, no
publicly-available agent-rule skill found that codifies these):

- **PDF lifecycle as a per-session protocol** for a research project,
  with `notes/survey_<citekey>.md` as the agent-readable cache.
- **Web-fetch discipline grounded in a research-paper context** (bib
  fields and survey notes consulted before WebFetch; arXiv abstract
  preferred over PDF page; cache to `references/_cache/`).
- **The aggregation itself**: no other skill we found packages all
  five disciplines together with a coherent first-action /
  last-action protocol grounded in a research-paper-skeleton's
  specific file layout.

**Adjacent ecosystems (mentioned for context, not directly borrowed):**

- **Cline memory bank**
  (`https://docs.cline.bot/prompting/cline-memory-bank`) -- one-task-
  one-goal + auto-compact + `.clineignore` patterns. We have no
  `.agentignore` analogue yet; possible future addition.
- **MemGPT / Letta** -- programmatic memory backend; conceptually
  parallel but different abstraction layer.
- **LangChain / LlamaIndex memory** -- programmatic backends; out of
  scope for an agent-operation skill.

## Planned future work: enforcement hooks

The disciplines above currently rely on agent self-discipline. The
single biggest reliability improvement available is to mechanise the
first-action / last-action protocols as hooks invoked by the agent
client, so the protocol fires regardless of whether the agent
remembered to follow it.

`OthmanAdi/planning-with-files` reports a 96.7% pass-rate on
Anthropic's skill-creator eval after introducing
`PreToolUse + PostToolUse + Stop` hooks vs 6.7% without. Our
expectation is similar gains for the first/last-action protocols,
because the same failure mode -- agent skipping the bookkeeping when
context fills up -- is what the hooks defend against.

Hooks are deferred for now (kept the repo simple at this stage). When
implemented, the design should be:

### Hook spec (for future implementation)

**Layout** (probably `bin/hooks/` shipped in this repo, with users
copying or symlinking into their per-project `.opencode/hooks/`):

```text
bin/hooks/
├── session-start.sh       reads AGENTS.md + PLAN.md (status section)
│                          + _collection_log.md (Last updated +
│                          Corrections-to-apply) + notes/README.md
│                          (status section). Echoes a compact
│                          summary into the agent's startup context.
├── pre-tool-use.sh        on tool calls that risk losing work
│                          (Edit, Write, Bash with `git commit`),
│                          checks PLAN.md mtime > AGENTS.md mtime,
│                          warns if AGENTS.md was edited mid-session
│                          (Critical Rule 7 violation).
├── post-tool-use.sh       on Write / Edit calls under notes/ or
│                          references/, prompts the agent to update
│                          notes/README.md or _collection_log.md if
│                          the modified file is a new survey note or
│                          a new bib entry.
└── stop.sh                before declaring session done, checks
                           that PLAN.md / _collection_log.md /
                           notes/README.md have been touched if
                           survey notes / bib entries / experiment
                           dirs changed during the session. If not,
                           refuses to stop and prompts for the
                           last-action update.
```

**Compatibility**: the hooks should be CLI-agnostic shell scripts
(no agent-client-specific assumptions in the hook bodies); each
agent client (OpenCode, Claude Code, Cursor) wires them via its own
hook mechanism, but the script bodies are portable.

**Implementation order when picked up**:

1. `session-start.sh` -- highest payoff, lowest implementation risk.
   Single read-only pass over 4 files; echoes a status summary.
2. `stop.sh` -- second-highest payoff. Walks `git status` for changes
   under `notes/` / `references/` / `experiments/` and verifies the
   matching index was updated. Refuses to stop if not.
3. `post-tool-use.sh` -- soft prompt; less critical.
4. `pre-tool-use.sh` -- defensive against Critical Rule 7 violation;
   only relevant for users iterating heavily on AGENTS.md.

**Open questions to resolve at implementation time**:

- Where exactly to install for OpenCode (`.opencode/hooks/` per repo?
  `~/.config/opencode/hooks/` user-global?). Per-repo is more correct
  but requires users to copy explicitly.
- How to make the prompts actionable rather than annoying (the user
  should never feel the hook is in the way of legitimate work).
- Whether to log hook fires to `~/.scicomp-research-skills.hooks.log`
  for debugging (probably yes, very small).
- Compatibility testing matrix: OpenCode + Claude Code + Cursor at
  least.

**When to revisit**: when at least 3 real research-paper sessions
have shown the agent skipping the first-action or last-action
protocol despite the rules being loaded. Until then, the cost of
maintaining hooks across multiple agent clients exceeds the benefit.

## See also

- `references/tool-selection.md` -- dedicated-tools-vs-bash + targeted
  read rules + parallelism rules.
- `references/pdf-lifecycle.md` -- one-shot pdftotext extraction;
  survey-note-first lookup; section-targeted reads of `.txt` files.
- `references/persistent-memory.md` -- first-action / last-action
  protocols for cross-session memory; the indices as memory.
- `references/context-window-budget.md` -- max-N skills / references /
  PDFs simultaneously; when to summarise + close.
- `references/web-fetch-discipline.md` -- cache-first; bib-fields
  before publisher page; arXiv abstract over PDF.
- The universal one-liners in
  `~/.scicomp-research-skills/AGENTS.md` Section 6 are a strict subset
  of the rules above; that section is what fires for agents that have
  not loaded this skill.

---

*Created 2026-05-13 by A. Attia. Distilled from observed waste modes
across multiple agent sessions on the rl-oed paper + this skills
repository's own bootstrapping. Revised 2026-05-13 (post-prior-art
audit): adopted progressive-disclosure framing + pushy description
(Anthropic skill-creator); added "Why this matters" framing around
attention-budget + context-rot (Anthropic context-engineering post +
Chroma); added Critical Rules 6-8 (recitation, no-mid-session-prompt-
edits, keep-errors-in-conversation) from Manus; added prompt-caching
note; added "Common rationalizations + rebuttals" table
(addyosmani/agent-skills pattern); added "Adjacent prior art +
lineage" section citing Manus / Anthropic / planning-with-files /
claude-mem / addyosmani / paper-qa / MemGPT; added "Planned future
work: enforcement hooks" with full spec (deferred implementation,
specification kept here so future work has the design ready).*
