---
name: agent-resource-discipline
description: Reduce token / quota / context-window consumption and improve cross-session memory by following explicit rules for tool selection (Read/Grep/Glob/Edit/Write vs bash equivalents), parallel vs sequential tool calls, targeted reads (offset+limit) over bulk reads, PDF lifecycle (one-shot pdftotext extraction + survey-note-first lookup), persistent-memory protocol (read project indices first, update them last), context-window budgeting (max-N skills/references/PDFs simultaneously), and web-fetch caching. Use whenever a task is expected to involve heavy reading, searching, multi-file editing, PDF handling, or external fetching -- which in practice is most non-trivial sessions in this ecosystem.
license: MIT
metadata:
  audience: any agent operating in this ecosystem
  domain: agent-tooling
  origin: A. Attia (added 2026-05-13)
---

# Agent Resource Discipline

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
non-trivial session. Default agent behaviour wastes them in predictable
ways:

- **Tool mis-selection** (`bash grep` instead of the dedicated `Grep`
  tool, `bash cat` instead of `Read`, ...) costs tokens AND loses
  features (paging, structured results).
- **Bulk reads** (`Read` with no offset/limit on a 2000-line file when
  50 lines would do) burn context window for no gain.
- **Re-derivation** (re-reading a PDF that was already summarised in a
  survey note last session) wastes tokens AND risks contradicting the
  prior summary.
- **Forgetting** (not reading PLAN.md / collection log / notes index
  at session start) causes the agent to either re-do work or to make
  decisions inconsistent with prior sessions.
- **Re-fetching** (calling WebFetch on the same URL twice in one
  session) burns external quota and adds latency.

These are all preventable with explicit rules. This skill codifies
them.

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
repository's own bootstrapping.*
