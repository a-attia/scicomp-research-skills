# scicomp-research-skills / AGENTS.md

**You are reading the root `AGENTS.md` of a shared agent-skills
repository.** Read this file first before doing anything else here or in
any project that references it.

This file follows the [agents.md](https://agents.md/) open standard.
Agent clients that look for other filenames (e.g. `CLAUDE.md`) read this
same content via symlinks created by `bin/install.sh`.

---

## 1. What this repository is

This repository holds **agent skills and workflow templates for research
in scientific computing** -- covering both research **papers** (drafts,
literature surveys, reviewer responses) and research **software**
(libraries, codes, reproducibility infrastructure) in domains such as
computational PDEs, inverse problems, optimal experimental design,
uncertainty quantification, optimisation, and scientific machine learning.

The repository exists so that:

- **Conventions are defined once and inherited everywhere.** A
  per-project `AGENTS.md` is short and project-specific; the generic
  conventions live here as **skills** loaded on demand.
- **The same conventions work across multiple agent clients** -- OpenCode,
  Claude Code, Codex, Cursor, Aider, Gemini CLI, etc. Any client that
  reads markdown can consume this repository.
- **The same conventions work across multiple machines.** A canonical
  checkout at `~/.scicomp-research-skills/` on each machine is refreshed
  via `git pull`; one source of truth.
- **Updates are versioned.** Every change to a convention or skill is a
  commit with a message; `git log` shows when and why.

This repository **starts from upstream
[Master-cai/Research-Paper-Writing-Skills](https://github.com/Master-cai/Research-Paper-Writing-Skills)**
(MIT-licensed) and intentionally diverges to broaden scope. See
`ATTRIBUTION.md` for the full lineage.

## 2. Local layout (per machine)

Two checkouts of this repository exist on each machine:

- **Development checkout**:
  `~/AHMED_HOME/Research/Projects/Software/scicomp-research-skills/`
  - This is where edits + commits happen.
  - Other research projects + agents on the machine **ignore** this
    checkout completely.
  - Push from here to the GitHub remote when changes are ready.
- **Canonical checkout**:
  `~/.scicomp-research-skills/`
  - Read-only from the user's perspective; refreshed via
    `~/.scicomp-research-skills/bin/refresh.sh`
    (or `git -C ~/.scicomp-research-skills pull --ff-only`).
  - This is the location that agents read from.
  - A pre-commit hook (in `.githooks/pre-commit`) refuses commits in this
    checkout, so accidental edits cannot be committed back.
  - Per-project `AGENTS.md` files reference paths like
    `~/.scicomp-research-skills/skills/<name>/SKILL.md`.

Set up the canonical checkout on a fresh machine via:

```bash
git clone <your-fork-url> ~/.scicomp-research-skills
~/.scicomp-research-skills/bin/install.sh
```

## 3. How agents should consume this repository

When an agent is given a project that references this repository, the
agent's reading order is:

1. Read this root `AGENTS.md` (you are here).
2. Read any skill the project's `AGENTS.md` directs you to. Skills are
   loaded **on demand**, not all at once -- see Section 5.
3. Read the project's own `AGENTS.md` for project-specific overrides /
   facts.
4. Read the project's `PLAN.md` (or equivalent plan-of-record) if one
   exists; this is typically the project's content contract.
5. Then proceed with the user's request.

**Universal rule**: when in doubt, the project's `AGENTS.md` and `PLAN.md`
override any conflicting guidance from this repository. This repository
provides defaults; projects own their specifics.

### OpenCode-specific consumption

OpenCode supports referencing remote instructions natively via
`opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": [
    "https://raw.githubusercontent.com/<your-fork>/main/AGENTS.md"
  ]
}
```

Skill files are auto-discovered by OpenCode at
`~/.config/opencode/skills/<name>/SKILL.md` and the Claude-compatible
fallback `~/.claude/skills/<name>/SKILL.md`. The simplest deployment is
a symlink:

```bash
ln -s ~/.scicomp-research-skills/skills ~/.config/opencode/skills
# or, for Claude Code compatibility:
ln -s ~/.scicomp-research-skills/skills ~/.claude/skills
```

After symlinking, OpenCode's `skill` tool will list the skills here as
loadable on demand.

## 4. Versioning + refresh protocol

- **Refresh is manual.** Run `~/.scicomp-research-skills/bin/refresh.sh`
  (which does `git fetch && git pull --ff-only`) when you want to pick up
  updates.
- **Staleness check.** Per-project `AGENTS.md` files instruct the agent
  to check the modification time of `~/.scicomp-research-skills/AGENTS.md`
  and print a reminder if it has not been refreshed in more than N days
  (default: 30). The reminder is informational; the agent proceeds
  without blocking.
- **Date-stamping.** Every skill file ends with a date-stamp footer
  noting when it was last revised. Agents should mention the date-stamp
  of any skill they load when they cite that skill in their response.
- **Compatibility.** When breaking changes to a skill are made, the
  file's date-stamp footer notes the breaking change explicitly.
  Per-project `AGENTS.md` files MAY pin a specific commit of this
  repository if they cannot tolerate unannounced changes.

## 5. Skills index

Each skill below lives at `skills/<name>/SKILL.md` with YAML frontmatter
following the [OpenCode skills](https://opencode.ai/docs/skills/) and
[Anthropic skills](https://docs.anthropic.com/en/docs/build-with-claude/agent-skills)
conventions. Skills are loaded **on demand** by per-project `AGENTS.md`
files, not automatically.

| Skill                       | Purpose                                                                                                  | Origin                          |
|:----------------------------|:---------------------------------------------------------------------------------------------------------|:--------------------------------|
| `skills/research-paper-writing/`  | Section-by-section paper drafting, paragraph-clarity check, claim-evidence alignment, adversarial review. | upstream (Master-cai)         |
| `skills/literature-survey/` | bibtex + PDF + pdftotext + per-paper survey-note + collection-log workflow for heavy-literature papers.   | added here                      |

When new skills are added, append a row to this table.

### Templates index

Templates in `templates/` are starter scaffolds for new projects -- copy
into a fresh project directory and customise.

| Template                       | Purpose                                                                  |
|:-------------------------------|:-------------------------------------------------------------------------|
| `templates/paper-skeleton/`    | Starter files for a new scientific-computing paper repo: PLAN.md skeleton, README.md skeleton, .gitignore, references/ structure stub, notes/README.md skeleton. |

## 6. Universal conventions

These conventions apply unless a per-project `AGENTS.md` explicitly
overrides them.

- **Encoding**: ASCII only in code, code comments, and code-style
  docstrings. Markdown documentation MAY use non-ASCII for readability
  (em-dashes, math symbols rendered via MathJax). Code remains ASCII.
- **Math notation**: prefer LaTeX inside markdown via MathJax (`$...$`
  for inline, `$$...$$` for display). Avoid ASCII-art math in production
  documentation.
- **Date-stamping**: every plan-of-record-style document (PLAN.md,
  AGENTS.md, any skill file) ends with a `*Created YYYY-MM-DD. Revised
  YYYY-MM-DD (note about the revision). Maintained by <name>.*` footer.
- **Code references**: when citing a specific function or block in code,
  use `path/to/file:line_number` format so the user can navigate
  directly.
- **No emojis**: in code, code comments, code docstrings, and production
  documentation, unless the user explicitly requests them.
- **Commit messages**: no `Co-Authored-By` trailers. Conventional commit
  style preferred (`feat: ...`, `fix: ...`, `docs: ...`) but not
  enforced.
- **No unilateral commits**: agents do not create git commits unless the
  user explicitly requests it.

## 7. Per-project AGENTS.md boilerplate

Per-project `AGENTS.md` files should follow this structure (keep them
short -- target ~50-100 lines):

```markdown
# <project name> / AGENTS.md

This project loads shared workflow conventions from a separate
repository. Before doing anything else, the consuming agent should:

1. Verify `~/.scicomp-research-skills/AGENTS.md` exists and is no more
   than 30 days stale (per its modification time). If stale, print a
   reminder suggesting `~/.scicomp-research-skills/bin/refresh.sh` and
   proceed anyway.
2. Read `~/.scicomp-research-skills/AGENTS.md`.
3. Read any skill files referenced below from
   `~/.scicomp-research-skills/skills/<name>/SKILL.md`.
4. Then read the rest of THIS file.

Skills to load for this project (load on demand, not all at once):

- `~/.scicomp-research-skills/skills/research-paper-writing/SKILL.md`
- `~/.scicomp-research-skills/skills/literature-survey/SKILL.md`

---

## Project facts

- Name: <project full name>
- Nature: <e.g. journal paper, software library>
- Status: <e.g. drafting Section 5; M3 milestone>
- Plan-of-record: PLAN.md (read this after AGENTS.md)

## Project-specific overrides

(Anything that differs from the universal conventions in
~/.scicomp-research-skills/AGENTS.md Section 6.)

## Project-specific facts the agent should not have to derive

(One-off facts: target venue, citation conventions, key collaborators,
specific external dependencies, current draft phase.)
```

## 8. How to add a new skill

1. Create `skills/<skill-name>/SKILL.md` in the **dev checkout**.
2. The skill file should:
   - Open with **YAML frontmatter** (required: `name`, `description`;
     optional: `license`, `compatibility`, `metadata`).
   - State when to load it (so per-project `AGENTS.md` authors know when
     to reference it).
   - Be self-contained (do not assume other skills are loaded unless
     explicitly stated).
   - Optionally include a `references/` subfolder for section-specific or
     deep-dive material loaded on demand from within the skill itself.
   - End with a date-stamped revision footer.
3. Append a row to the skills index table in this AGENTS.md (Section 5).
4. Commit + push from the dev checkout.
5. On any machine that needs the new skill, run
   `~/.scicomp-research-skills/bin/refresh.sh`.

### Skill name validation rules (from OpenCode skills spec)

- 1-64 characters
- lowercase alphanumeric with single hyphen separators
- not start or end with `-`
- no consecutive `--`
- match the directory name

Equivalent regex: `^[a-z0-9]+(-[a-z0-9]+)*$`

### Skill description rules

- 1-1024 characters
- specific enough for the agent to choose correctly when listing
  available skills

## 9. How to add a new template

1. Create `templates/<template-name>/` in the dev checkout.
2. Populate with the starter files.
3. Append a row to the templates table in Section 5.
4. Commit + push.

## 10. License

MIT. See `LICENSE` for the upstream copyright (Master-cai 2026); see
`ATTRIBUTION.md` for our additions (also MIT, A. Attia 2026).

---

*Created 2026-05-13 by clone-and-diverge from Master-cai/Research-Paper-Writing-Skills @ 9ee5edd. Maintained by A. Attia.*
