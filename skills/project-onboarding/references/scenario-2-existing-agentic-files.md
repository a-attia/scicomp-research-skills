# Scenario 2: existing project, existing agentic files

Loaded on demand from the `project-onboarding` skill when the audit
(see `references/existing-project-audit.md`) has confirmed that the
existing project has one or more `AGENTS.md` / `CLAUDE.md` /
`.cursorrules` / `GEMINI.md` / `CONVENTIONS.md` / `AGENT.md` files
at the repo root.

The user has already invested in agentic instructions; that
investment must be preserved. The framework's job is to **integrate**,
not to **replace**.

This file works in tandem with
`references/conflict-resolution.md` (load both when in Scenario 2).

---

## The migration target: AGENTS.md as canonical

The framework's convention is:

- **`AGENTS.md` is the canonical file.** It contains the full
  agent-facing content for the project.
- **Other agent-discovery filenames are SYMLINKS to `AGENTS.md`.**
  This way Claude Code finds `CLAUDE.md`, Cursor finds `.cursorrules`,
  Aider finds `CONVENTIONS.md`, etc., but they all read the same
  content and stay in sync automatically.

This is the same scheme `bin/install.sh` uses for the canonical
checkout itself (see root `README.md` "What `install.sh` actually
does", step 3).

The migration goal: **end with one `AGENTS.md` containing all the
project-facing content + all desired symlinks pointing at it.**

---

## Decision: which sub-case applies?

After Audit Step 3 (see `references/existing-project-audit.md`),
classify based on the table of agent files found:

- **2.A**: One agent-file format (e.g. just `CLAUDE.md`).
- **2.B**: Multiple agent-file formats (e.g. `CLAUDE.md` +
  `.cursorrules` + `GEMINI.md`).
- **2.C**: One or more agent-files contain substantive project
  content (project-specific facts, conventions, in-progress
  decisions) -- not just generic agent rules.
- **2.D**: Existing conventions in the agent-files conflict with
  framework's universal conventions (root `AGENTS.md` Section 6).

Sub-cases compose: a real project might be 2.B + 2.C + 2.D
simultaneously. Apply the relevant procedures in order.

---

## Sub-case 2.A: one agent-file format

The simplest Scenario 2 case. Worked example -- starting state:

```text
my-paper/
├── CLAUDE.md             (47 lines: 35 lines of generic Claude rules
│                          + 12 lines of project-specific facts)
├── README.md
├── paper/
└── ...
```

Migration plan:

1. **Read the existing `CLAUDE.md` carefully** in the audit step.
   Classify each section as:
   - **Generic agent rules** (e.g. "use 4-space indent", "always run
     tests before commit"). These are mostly redundant with the
     framework's universal conventions in
     `~/.scicomp-research-skills/AGENTS.md` Section 6; classify each
     as either:
     - **Subsumed by framework convention** -- safe to drop on
       migration; the framework rule covers it.
     - **Conflicting with framework convention** -- 2.D applies; see
       `references/conflict-resolution.md` to resolve before
       proceeding.
     - **Additional / not in framework** -- migrate to per-project
       AGENTS.md "Project-specific overrides" or "Project-specific
       facts the agent should not have to derive" sections.
   - **Project-specific content** (e.g. "this codebase uses convention
     X for the diffusion-term sign", "the M3 milestone is to ship a
     dolfinx integration"). This is the most valuable content;
     migrate to per-project AGENTS.md "Project facts" / "Project-
     specific facts" sections OR to PLAN.md if it's plan-of-record
     content.

2. **Create the per-project AGENTS.md** by copying the appropriate
   template (`paper-skeleton/AGENTS.md` or
   `software-skeleton/AGENTS.md`) and filling in:
   - The framework boilerplate (Sections 1-3: verify canonical
     checkout; read root AGENTS.md; load skills).
   - The skills-to-load list (per the chosen template).
   - "Project facts" + "Project-specific overrides" + "Project-
     specific facts the agent should not have to derive" populated
     from the existing CLAUDE.md content.

3. **Convert `CLAUDE.md` to a symlink to `AGENTS.md`**:
   ```bash
   git rm CLAUDE.md
   ln -s AGENTS.md CLAUDE.md
   git add AGENTS.md CLAUDE.md
   git commit -m "chore: migrate CLAUDE.md to AGENTS.md (canonical) + symlink"
   ```
   Now Claude Code still finds `CLAUDE.md`; the content lives in
   `AGENTS.md`; both stay in sync automatically.

4. **(Optional)** Add other agent-file symlinks if the user uses
   other clients on this project:
   ```bash
   ln -s AGENTS.md .cursorrules    # if user uses Cursor
   ln -s AGENTS.md GEMINI.md       # if user uses Gemini Code Assist
   ln -s AGENTS.md AGENT.md        # if user uses Zed (singular form)
   git add .cursorrules GEMINI.md AGENT.md
   git commit -m "chore: add agent-discovery symlinks for additional clients"
   ```

5. **Add `.gitignore` entries** if the user wants the symlinks
   uncommitted (per-checkout symlinks vs tracked symlinks; either
   convention is fine, but pick one). The repo's own
   `bin/install.sh` uses uncommitted symlinks via `.gitignore`; for
   per-project AGENTS.md it's usually fine to commit them so they
   don't have to be recreated on every clone.

Total time: ~20 minutes once the existing CLAUDE.md content has been
classified.

---

## Sub-case 2.B: multiple agent-file formats

The same as 2.A applied to multiple files. Common situation: a team
where different members use different agent clients, each having
added their own agent-file.

Worked example -- starting state:

```text
my-paper/
├── CLAUDE.md             (45 lines, mostly generic rules)
├── .cursorrules          (8 lines, generic Cursor rules)
├── GEMINI.md             (12 lines, project-specific Gemini-specific
│                          tips)
└── ...
```

The risk: content duplicated across files; possibly inconsistent
between them.

Migration plan:

1. **Read all three files in the audit step.** For each, classify
   per Sub-case 2.A's Step 1.

2. **Reconcile inconsistencies between the files.** If `CLAUDE.md`
   says "use snake_case" and `GEMINI.md` says "use camelCase", the
   migration cannot silently pick one. Surface the conflict to the
   user; ask which is intended; document the decision.

3. **Build the consolidated content** by merging:
   - Generic-and-subsumed: drop.
   - Generic-and-conflicting: resolve per
     `references/conflict-resolution.md` + put the resolution in
     "Project-specific overrides".
   - Generic-and-additional: put in "Project-specific overrides" or
     similar.
   - Project-specific facts: put in "Project facts" / "Project-
     specific facts the agent should not have to derive". If the
     same fact appears with different wording in two files, keep
     the more precise version + cite the agreement.

4. **Create the per-project AGENTS.md** as in 2.A Step 2.

5. **Replace each existing agent-file with a symlink:**
   ```bash
   for f in CLAUDE.md .cursorrules GEMINI.md; do
     git rm "$f"
     ln -s AGENTS.md "$f"
   done
   git add AGENTS.md CLAUDE.md .cursorrules GEMINI.md
   git commit -m "chore: consolidate CLAUDE.md + .cursorrules + GEMINI.md into AGENTS.md (canonical) + symlinks"
   ```

Total time: ~30-60 minutes; most of it spent on Step 2
(reconciling inconsistencies). The reconciliation work is the value
the migration adds; otherwise the team ends up with stale,
contradictory agent-files indefinitely.

---

## Sub-case 2.C: agent-file with substantive project content

The most important sub-case to handle carefully. The existing
agent-file is not just a generic rules file; it has been
hand-written by the user with project-specific knowledge that took
real effort to accumulate.

Worked example -- excerpt of an existing `CLAUDE.md`:

```markdown
# CLAUDE.md

You are working on the rl-oed paper.

## Project context

- Target venue: Computer Methods in Applied Mechanics and Engineering
  (CMAME), Q1 2027 submission.
- Closest competitor: Shen and Huan 2023 (CMAME 2023). We differ by
  adding distributional critics + risk-sensitive variants.
- Current draft phase: M5 (drafting Section 4 Method).

## Conventions

- All math in MathJax (`$...$` inline, `$$...$$` display).
- Citations via natbib + numeric.
- Author list: Attia, Attia, Smith (alphabetical-by-last-name).

## Skills loaded for this project

- Always use `pdftotext -layout` for PDF reading; do not try to read
  binary PDFs directly.

## In-progress decisions

- D-001 (2026-04-30): adopt CVaR-EIG as the primary risk-sensitive
  variant; defer entropy-regularised alternatives.
- D-002 (2026-05-05): use Laplace-Gaussian belief approximation; not
  the full information-vector representation that Shen 2023 uses
  (their representation is too expensive for our action space).

## Current open questions

- How to handle the multiplicative noise model in the
  PyOEDAdvectionDiffusionEnv? Shen 2023 uses signal-magnitude-
  dependent noise; we should adopt for realism but it complicates
  the gradient estimator.
```

Every section here is valuable + must be preserved during migration.
The user paid time to write it; the framework's job is to put it
where the framework's other components can find it, not to
discard it.

Migration plan:

1. **Read the existing agent-file in full** (it's
   small enough to fit in context; bulk read is appropriate here).

2. **Classify each section by destination**:

   | Existing section                  | Destination                                                    |
   |:----------------------------------|:---------------------------------------------------------------|
   | Project context                   | per-project `AGENTS.md` "Project facts" section                |
   | Conventions (math, citations)     | per-project `AGENTS.md` "Project-specific overrides" + "Project-specific facts" sections |
   | Author list                       | per-project `AGENTS.md` "Project facts" section + paper README's author list |
   | "Skills loaded for this project"  | per-project `AGENTS.md` "Skills to load for this project" section (deduplicate against template's default list) |
   | "In-progress decisions"           | `PLAN.md` Section 7 (Design decisions log; if a paper template, adapt -- the paper-skeleton's PLAN.md doesn't have a decisions log section by default, so create one OR move to `notes/section_<N>.md` for the relevant section) |
   | "Current open questions"          | `PLAN.md` Section 11 "Open Questions"                          |

3. **Create the per-project AGENTS.md** from the template; populate
   each section with the migrated content (per Step 2's table).

4. **Create / update PLAN.md** to absorb the decision log + open
   questions content.

5. **Convert the existing CLAUDE.md (or whatever) to a symlink** as
   in 2.A Step 3.

6. **Verify nothing was lost.** Diff: every line in the original
   agent-file should have a destination in the new structure (or
   be a generic rule subsumed by the framework's universal
   conventions). Any line without a destination needs explicit
   user decision before migration completes.

The "verify nothing was lost" step is the single most important step
in 2.C. The agent should produce a checklist:

```markdown
## Migration content check (CLAUDE.md -> AGENTS.md + PLAN.md)

| Original section               | Original line(s) | Destination                       | Status   |
|:-------------------------------|:-----------------|:----------------------------------|:---------|
| "You are working on..."        | line 3           | dropped (subsumed by AGENTS.md "Project facts: Name") | OK |
| "## Project context"           | lines 5-12       | AGENTS.md "Project facts"         | migrated |
| Bullet "Target venue: CMAME"   | line 7           | AGENTS.md "Project facts: Target venue" | migrated |
| Bullet "Closest competitor"    | lines 9-11       | PLAN.md "Headline Contribution: Positioning relative to prior work" | migrated |
| ...                            | ...              | ...                               | ...      |
| "## Current open questions"    | lines 35-42      | PLAN.md Section 11 "Open Questions" | migrated |
| "How to handle the multiplicative noise model" | lines 37-42 | PLAN.md Section 11 item 1 | migrated |

Total lines in original: 47. Total lines accounted for: 47. None missing.
```

Present this checklist to the user for review before the migration
commits. The user might insist on different destinations for some
content; honour their choice.

Total time for 2.C migration: ~1 hour for a 50-line agent file; more
for longer files. The work is mostly classification + careful
copying; the agent does well at it but the user must verify.

---

## Sub-case 2.D: conflicting conventions

Treated in detail in `references/conflict-resolution.md`; summary
here:

When the existing agent-file says one thing and the framework's
universal conventions (root `AGENTS.md` Section 6) say another:

1. The agent surfaces the conflict to the user explicitly.
2. The user picks one side (or proposes a compromise).
3. The decision goes in per-project `AGENTS.md` "Project-specific
   overrides" section, with the rationale.
4. The migration proceeds with the user's decision recorded; the
   framework's universal convention DOES NOT silently override the
   user's existing convention.

The "Project-specific overrides" section is the formal mechanism for
deviating from the universal conventions; it's not a "broken
project" indicator, it's a normal feature.

Common conflicts + standard resolutions:

| Framework rule (root AGENTS.md Section 6) | Common project-specific override                          |
|:------------------------------------------|:----------------------------------------------------------|
| "ASCII only in code"                      | "We allow Unicode in code comments for non-English collaborator names" |
| "No emojis in production docs"            | "We use emojis in our internal-team docs for status indicators" |
| "No `Co-Authored-By` trailers"            | "We document AI-co-authored commits via the `AI-Assist:` trailer" |
| "Conventional commit prefixes"            | "We use `R&D:` / `BUG:` / `DOC:` prefixes from our internal style guide" |

None of these are wrong; they're project-specific decisions. The
framework's job is to make the deviation visible (in
`AGENTS.md` "Project-specific overrides") rather than have the agent
silently apply one rule + the user expecting another.

---

## Anti-patterns to refuse

- **"Let me delete the existing CLAUDE.md and replace with the
  template's AGENTS.md."** No -- preserve all content; symlink for
  discovery.
- **"This existing CLAUDE.md is generic; I can drop it."** No --
  even "generic" content might be there for a reason. Read carefully;
  classify; ask the user before dropping anything.
- **"Two agent-files disagree; I'll go with the more recent one."**
  No -- surface the conflict to the user; the user decides.
- **"This in-progress decision is old; let me drop it."** No -- old
  decisions are part of the audit trail. Move to `PLAN.md` Section 7
  (Design decisions log) marked with the original date.

## Cross-references

- `references/existing-project-audit.md` -- the inventory step that
  precedes any of the above; in particular Step 3 (existing agentic
  instructions) feeds the decision tree at the top of this file.
- `references/scenario-1-no-agentic-work.md` -- the other scenario;
  use this if Audit Step 3 found no existing agent-files.
- `references/conflict-resolution.md` -- how to resolve 2.D-style
  convention conflicts; load alongside this reference whenever in
  Scenario 2.
- `references/migration-prompts.md` -- ready-to-paste prompts the
  user can give the agent to start a Scenario 2 migration.
- Root `AGENTS.md` Section 6 -- the universal conventions that
  govern Sub-case 2.D conflicts.

---

*Created 2026-05-13 by A. Attia.*
