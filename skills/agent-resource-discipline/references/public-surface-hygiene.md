# Public-surface hygiene

Loaded on demand from the `agent-resource-discipline` skill whenever
the agent is about to write to a **public surface**: a commit or commit
message in a public repository, a GitHub issue, pull request or
comment, a public skill or template, or any other text that will be
read by people outside the project. The universal rule is
`~/.scicomp-research-skills/AGENTS.md` Section 6.7. This file is the
procedure behind it.

---

## Why a procedure, not just a rule

The obvious place to sanitise is "at roll-up", when a journal entry is
promoted to an upstream issue. That is where this framework first put
it, and it was not enough. When the maintainer audited this repository
(2026-10-14), almost none of the leaks had come through roll-up. They
came from the framework's own authoring:

- **Skill text citing its origin.** "Motivated by the X onboarding
  session" names X, and the provenance habit is otherwise good.
- **Worked examples copied from real work.** An example `CLAUDE.md`
  reproduced an unpublished paper's venue, timeline, method choices and
  author list. An example survey note planned to email a named
  researcher.
- **Template rows**, which every new project then copies and nobody can
  recall.
- **Changelog entries and commit messages.** Commit messages cannot be
  edited without rewriting history.
- **Issue bodies** that kept the venue and date of a peer review while
  dropping the manuscript's name.

Each was written by an agent being helpful and specific, and none was
caught by self-review, because the author is the one reader who
already knows the names and does not notice them. Hence the mechanical
scan.

## Threat model

### What counts as private

| Class | Examples | Notes |
|:---|:---|:---|
| **Peer-review material** | Manuscript title, authors, ID, findings; the venue together with the review date | Owed to a third party, so the user cannot waive it. See [Peer review](#peer-review). |
| **Third-party unpublished work** | A collaborator's thesis, embargoed data, funder documents | Also owed to someone else. |
| **People** | Collaborator names, names from acknowledgements | |
| **Project identity** | Project, tool, paper and talk titles; codenames; organisation slugs | Reveals what the user works on, and when. |
| **Institution** | Institution name, internal venues, internal services, mailing lists | Most sensitive in combination with project identity. |
| **Environment** | `/Users/<name>/`, usernames, hostnames, IP addresses, machine-only claims | Overlaps `human-facing-doc-authoring` rule J. |
| **Exact dates** | A day-exact date attached to a described private project | Framework revision dates are fine; see [Dates](#dates). |

### Where it leaks, from worst to least bad

| Surface | Why it is bad | Can it be fixed? |
|:---|:---|:---|
| Templates | Copied into every new project | Only forward; old copies remain downstream |
| Commit messages | Public and permanent | Only by rewriting history |
| File content | Public; old versions stay in history | Fix forward; history needs a rewrite |
| Issue / PR bodies and comments | Public; notification emails already sent | Editable, but edit history is visible (see below) |
| Skill text and changelog | Read by every user of the framework | Fix forward |

## The procedure

### Before writing

1. **Describe the source generically.** "A shell-tooling project", "a
   talk deck", "a funded-project poster", "a journal peer review".
   Counts are fine ("14 projects"); names are not.
2. **Make examples fictional.** Invent the project, the method, the
   people and the venue (`<journal>`, `Author A`, `HeatEquationModel`).
   Keep published literature as it is; it is public. Strip anything
   that says what the user's own work does with it.
3. **Prefer a placeholder to a near-miss.** `mytool` is better than a
   lightly disguised real name.

### Before publishing

1. **Files and commits in this repo:** the hooks do it. `pre-commit`
   scans the lines the commit adds, and `commit-msg` scans the message.
   Both block on findings.
2. **Issues, PRs and comments:** write the body to a file, then:

   ```bash
   bin/privacy-scan.sh --file body.md && gh issue create --body-file body.md ...
   ```

   Never pass a public body inline with `--body`.
3. **Anything else public** (a slide deck shared online, a README in
   another public repo): `bin/privacy-scan.sh --file <path>`.
4. **Report every finding to the user** with the suggested replacement.
   Do not silently rewrite, and do not silently keep. An identifier
   stays only with the user's explicit approval for that surface.

### The scanner

`bin/privacy-scan.sh` runs two kinds of check:

- **Generic patterns**, always on: absolute home paths, email
  addresses outside a small allowlist, IPv4 addresses, `*.local`
  hostnames. CI runs these over every tracked file
  (`.github/workflows/privacy-lint.yml`).
- **Personal terms**, from a file that lives outside every repository
  and is never committed:

  ```bash
  mkdir -p ~/.config/scicomp-research-skills
  cp bin/private-terms.example.txt ~/.config/scicomp-research-skills/private-terms.txt
  ```

  One term per line, literal by default, `regex:` for an extended
  regular expression, and an optional `==>` suggestion. The syntax
  matches `git filter-repo --replace-text`, so the same file can drive a
  history rewrite if one is ever needed. Intentional exceptions (your
  own public name, for instance) go in `allowed-terms.txt` beside it.

Without a personal terms file the scanner prints a one-line warning
and runs the generic checks only. **Generic checks cannot know your
project names**, so set the file up on every machine you commit from.

Findings go to stderr only. The scan never writes a term anywhere
else, so it cannot itself leak one.

### Using the scanner in other repositories

A project repository that is public, or that has a public-release
boundary inside it, can use the same scanner: copy
`bin/privacy-scan.sh` into the project, and call it from the project's
own `pre-commit` and `commit-msg` hooks the way this repository's
`.githooks/` do. The personal terms file is shared, since it lives in
the user's config directory.

## Peer review

Peer-review material is the strictest class, for two reasons.

**The duty is to the authors and the editor, not to the user.** A user
cannot approve publishing anything about a manuscript under review,
because it is not theirs to publish. In public text, a review is "a
journal peer review", with no venue, no date finer than the year, and
nothing about the manuscript.

**Reading the manuscript may itself be prohibited.** Several publishers
forbid referees from uploading or pasting a manuscript under review
into generative-AI tools, in any form. Before an agent reads a
manuscript, ask the user to confirm that the venue's reviewer policy
allows it. If it does not, or the user does not know, stop. That
question is not answered by keeping the output private.

## Dates

`AGENTS.md` Section 6.2 requires `YYYY-MM-DD` revision footers, and
those stay. Framework revision dates describe this repository, not the
user's private work. What gets coarsened to the month or year is a date
**attached to a described private project or review**, since together
they say what the user was doing on that day.

## Cleaning up what is already published

**Fix forward by default.** Edit the file, the template, or the issue,
and write the commit message generically. A history rewrite is a last
resort.

| Surface | How | Caveat |
|:---|:---|:---|
| Files, skills, templates, changelog | Edit; one `docs:` commit with a generic message | History keeps the old text |
| Templates already copied downstream | Note in `CHANGELOG.md` which rows are safe to delete | Cannot be recalled |
| Issue / PR body | `gh issue edit N --body-file clean.md` | Edit history stays visible to anyone with read access. Delete old revisions in the web UI (click "edited", then delete the revision); `gh` cannot do this. |
| Issue / PR comment | `gh api -X PATCH repos/<owner>/<repo>/issues/comments/<id> -F body=@clean.md` | Same; delete revisions in the web UI |
| Commit messages, old file versions | `git filter-repo --replace-text terms.txt --replace-message terms.txt`, then force-push, then ask GitHub Support to purge cached views | Every commit hash changes. Every clone, including the canonical checkout on each machine, must be re-cloned. Hashes cited elsewhere go stale. **Existing forks keep the old history.** Reserve this for peer-review or third-party material. |

## Rationalizations

| Thought | Rebuttal |
|:---|:---|
| "It's the user's own project, so naming it is fine." | The user decides that, per surface. Ask; do not assume. |
| "The name is already in the history, so one more mention costs nothing." | Each new mention is another place to clean, and the current files are what people read. |
| "Provenance makes the rule credible." | Provenance by *kind* ("from a shell-tooling project, 2026-05") is just as credible and costs nothing. |
| "It's only an example." | Examples are the most-copied text in the repository. Make them fictional. |
| "I removed the manuscript title, so the review is anonymous." | Venue plus date plus topic can identify a review. Remove all three. |
| "The scan passed." | It passed the checks it has. Generic patterns do not know project names; a terms file that is missing or stale does not either. |

---

*Created 2026-10-14 by A. Attia, from the repository audit of the
same date and the privacy proposal in issue #2. Maintained by A.
Attia.*
