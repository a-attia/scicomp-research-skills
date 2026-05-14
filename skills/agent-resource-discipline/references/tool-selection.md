# Tool selection + targeted reads + parallelism

Loaded on demand from the `agent-resource-discipline` skill the first
time a session needs a non-trivial file / search / edit operation.

This is the most common source of token waste. Every rule below has
been observed to fire dozens of times in real sessions before being
codified.

---

## Dedicated tools vs Bash equivalents

The dedicated tools (Read, Grep, Glob, Edit, Write) are
context-window-cheaper and produce structured results that the agent
can act on directly. Bash equivalents are token-cheap to TYPE but
expensive to consume the OUTPUT of -- the agent then needs another
round of parsing.

**Always prefer:**

| Want to ...                | Use                          | Not                                          |
|:---------------------------|:-----------------------------|:---------------------------------------------|
| Find files by name pattern | `Glob`                       | `bash find` / `bash ls -R`                   |
| Search file contents       | `Grep`                       | `bash grep` / `bash rg`                      |
| Read a file                | `Read`                       | `bash cat` / `bash head` / `bash tail`       |
| Edit a file                | `Edit`                       | `bash sed` / `bash awk` / `bash perl -i`     |
| Create a new file          | `Write`                      | `bash cat <<EOF >file` / `bash echo > file`  |
| Communicate with the user  | response text                | `bash echo` / `bash printf`                  |

**Reserve `Bash` for actual shell operations**: `git`, `npm`/`uv`/`pip`
package managers, build systems (`make`, `cmake`, `cargo`), CLI tools
(`pdftotext`, `pandoc`), running compiled binaries.

### Why "communicate with response text"

Some agents reflexively use `echo "Done!"` or `printf "Result: %s\n"`
to talk to the user. Don't. The user reads the response message,
not stdout. Every `echo` for communication is a wasted Bash call.

## Targeted reads vs bulk reads

The default `Read` returns up to 2000 lines. That is for **skimming**
unfamiliar files, not for routine consumption.

**Decision tree** when about to `Read` a file:

1. Is it <300 lines? -> `Read` whole file is fine.
2. Is it 300-1000 lines? -> `Read` whole file IF you genuinely need
   the whole thing; otherwise `Grep` first to locate the section,
   then `Read` with `offset`+`limit` for that section.
3. Is it >1000 lines? -> `Grep` first; `Read` with `offset`+`limit`
   for the section. Do NOT `Read` the whole file unless the task
   really requires it (rare).

**Exceptions** where bulk read IS appropriate:

- the file is a configuration / manifest the agent will fully ingest
  (e.g. PLAN.md, AGENTS.md, a SKILL.md file you're loading);
- the file is intentionally short (under 300 lines) by design;
- the user has explicitly asked the agent to read the whole file
  ("show me everything in X").

## Parallelism: batch independent calls

When several tool calls are **independent** (one's output does NOT
feed the next's input), batch them into a SINGLE message. Otherwise
each call costs a round-trip.

**Examples that should be parallelised:**

- Reading three different files for context.
- Greping for three different patterns to compare frequencies.
- `git status` + `git log` + `git diff` (all read-only, independent).
- Running multiple independent tests.

**Examples that must be sequentialised:**

- `mkdir` then `cp` into that dir (the cp depends on the mkdir).
- `Read` a config file then `Edit` it (the edit's `oldString` depends
  on the read).
- `git add` then `git commit` (the commit depends on the add).
- `Write` a file then `git add` it (the add depends on the write).

**When in doubt**: if the second call's parameters can be specified
WITHOUT looking at the first call's output, parallelise. If they can't,
serialise.

## Editing tactics

When making multiple edits to the same file:

- Multiple non-overlapping `Edit` calls in one message: fine,
  parallelisable.
- Multiple overlapping `Edit` calls: serialise; later edits need to
  see the earlier edit's effect on the file.
- Replacing a string that occurs many times: use `replaceAll: true`
  in a single `Edit` call rather than N separate calls.
- Whole-file rewrite where most lines change: `Write` (after `Read`)
  is cheaper than 20 `Edit` calls.

## Search tactics

When searching for "where is X used?":

1. First call: `Grep` for the canonical name (e.g. function name).
2. Examine the file paths + line numbers returned.
3. `Read` only the files where context matters.

**Anti-pattern**: `Read`-ing every file in a directory looking for X.
Always `Grep` first.

When searching for "is X mentioned anywhere?":

- `Grep` with the appropriate `include` filter (e.g. `*.md` for docs,
  `*.py` for source).
- Do NOT `Read` index files (README, AGENTS.md, ...) hoping to find a
  mention; `Grep` is faster + complete.

## Common waste-mode catalogue

Modes observed in real sessions; if you find yourself in one, stop:

1. **The "let me just cat the file" trap.** Replace `bash cat path/to/file`
   with `Read filePath: path/to/file`.
2. **The "find then read" trap.** `bash find . -name '*.md'` followed by
   reading the output. Replace with `Glob pattern: **/*.md`.
3. **The "grep through bash" trap.** `bash grep -rn 'pattern' .`
   followed by parsing the output. Replace with
   `Grep pattern: 'pattern'`.
4. **The "I already read this" trap.** Reading the same file twice in
   one session. The first read is in your context; refer back to it
   rather than re-reading.
5. **The "let me read the whole 5000-line file" trap.** `Read` with no
   limit on a large file. Replace with `Grep` + targeted `Read` with
   `offset`+`limit`.
6. **The "echo for communication" trap.** `bash echo "I will now do X"`
   instead of writing "I will now do X" in the response message.
7. **The "sequential reads" trap.** Three messages each with one
   `Read`, when they could be one message with three `Read`s.

---

*Created 2026-05-13 by A. Attia.*
