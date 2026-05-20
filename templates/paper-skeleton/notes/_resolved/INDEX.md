# Resolved feedback index

This directory holds `notes/agent_feedback.md` entries that have been
actioned upstream in `scicomp-research-skills` (or in another upstream
target). Each entry is one file. The original entry in
`agent_feedback.md` has been replaced by a stub linking back to its
file here.

**Convention**: an entry lives here when the proposal it contained has
been codified upstream + the upstream artefact is in production. If
the proposal was filed-but-not-yet-actioned (e.g. as a GitHub issue),
the entry stays in `agent_feedback.md` with a "filed as #N" marker
until the issue closes.

For superseded / filed-as-issue artefacts that aren't agent_feedback
entries, see [`../_archive/INDEX.md`](../_archive/INDEX.md).

---

## Entries (newest first)

| Date logged | Date resolved | F-ID(s) | Title | Resolution | Upstream commit | File |
|:------------|:--------------|:--------|:------|:-----------|:----------------|:-----|

(No resolved entries yet. Add a row + the corresponding
`<date>_<slug>.md` file when an entry from `../agent_feedback.md` has
been actioned upstream.)

---

## Partial resolutions (still open)

Some entries surface multiple proposals; only SOME of those may get
actioned upstream. Such entries remain in `../agent_feedback.md` with
a top-of-entry marker noting which parts were resolved + which remain
open.

| Date logged | Original entry | Partially resolved (F-ID) | Still open |
|:------------|:---------------|:--------------------------|:-----------|

(None yet.)

---

## When to add a new entry here

Append a row to the "Entries" table + create the corresponding file
when:

1. An entry in `../agent_feedback.md` has been actioned upstream
   AND the upstream artefact is shipped + visible in production.
2. The action is more than cosmetic (a fix, a new rule, a new
   reference). Trivial typo fixes don't warrant archival.

For PARTIAL resolutions: add a row to the "Partial resolutions"
table; the entry stays in `../agent_feedback.md` with a top-of-entry
marker.

The stub left in `agent_feedback.md` for fully-resolved entries
should preserve the original date + title so chronological scanning
still finds it, with a "RESOLVED upstream in commit X" body
pointing here.

---

*Convention documented in
`~/.scicomp-research-skills/templates/<paper|software>-skeleton/notes/README.md`
"Archive + resolution log" section. Originated 2026-05-20 from real-
project evidence on argo-anywhere + AmigAI.*
