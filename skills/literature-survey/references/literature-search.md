# Literature search (Step 0: finding candidate papers)

Loaded on demand from `literature-survey/SKILL.md` "Step 0". The five
main steps of that skill start once you *have* a candidate paper; this
file covers how to find candidates in the first place, and how to hand
each one to Step 1 with enough identifiers to verify it.

> **Provenance.** Adapted from the `literature-search` skill in
> [AI-ModCon/genesis-skills](https://github.com/AI-ModCon/genesis-skills)
> (`skills/literature-search/`, author Ian Foster, ModCon Base CAF
> Team; upstream commit `b7e8434`), licensed Apache-2.0. The licence
> text is in `literature-search.LICENSE` beside this file. **Changes
> from upstream:** condensed the three upstream files (`databases.md`,
> `strategies.md`, `formats.md`) into one; replaced the biomedical and
> chemistry emphasis with scientific-computing sources (math.NA,
> SIAM, zbMATH, OSTI); added the programmatic endpoints in
> "Programmatic lookup" (each checked by hand on 2026-10-14); dropped
> the APA / MLA formatting guidance (this framework uses BibTeX only);
> tied the search log and hand-off to `literature-survey` Steps 1 and 5.

---

## 1. Pick the search strategy

| Strategy        | Use when                                           | How                                                                                                   |
|:----------------|:---------------------------------------------------|:------------------------------------------------------------------------------------------------------|
| **Snowball**    | You already have one or two anchor papers.         | Backward: walk the anchor's reference list. Forward: walk "cited by" (Google Scholar, Semantic Scholar, OpenAlex `cites:` filter). |
| **Systematic**  | Review article, proposal, thesis chapter, or any claim of the form "no prior work does X". | Fix terms + synonyms up front; query every source in Section 2; apply written inclusion / exclusion criteria; log every query (Section 5). |
| **Exploratory** | Entering a field you do not know.                  | Start with `"<topic>" review OR survey OR tutorial`; note recurring authors and groups; find the seminal papers; then narrow. |

A "no prior work does X" claim in a paper is only as strong as the
systematic search behind it. If the search was exploratory, say so to
the user rather than letting the claim stand.

## 2. Where to search (scientific-computing first)

| Source                     | Best for                                                                     | Access                                            |
|:---------------------------|:-----------------------------------------------------------------------------|:--------------------------------------------------|
| **arXiv**                  | Preprints in math.NA, math.OC, stat.ML, stat.CO, physics.comp-ph, cs.LG, cs.NA, cs.MS | API (Section 3); web `site:arxiv.org`           |
| **OpenAlex**               | Cross-domain metadata, citation counts, "cited by", open-access links        | Free API, no key (Section 3)                      |
| **Crossref**               | Authoritative DOI metadata for published versions                            | Free API (Section 3)                              |
| **Semantic Scholar**       | Citation graph, "influential citations", recommendations                     | API; rate-limited without a key                   |
| **zbMATH Open**            | Mathematics, numerical analysis; reviewed bibliographic records              | Web + API                                         |
| **MathSciNet**             | Mathematics; reviewed records and author disambiguation                      | Institutional subscription                        |
| **SIAM / SIAM Epubs**      | SISC, SINUM, SIOPT, SIAM/ASA JUQ, SIIMS, inverse-problems + OED literature    | Web `site:epubs.siam.org`                         |
| **OSTI.gov**               | DOE lab reports, DOE-funded journal articles, software records               | Free API (Section 3)                              |
| **Google Scholar**         | Broadest coverage, theses, books; noisiest                                   | Web only, no API                                  |
| **IEEE Xplore / ACM DL**   | HPC, computer architecture, signal processing                                | Web                                               |

arXiv category codes worth knowing in this domain: `math.NA` /
`cs.NA` (numerical analysis), `math.OC` (optimisation and control),
`stat.ML`, `stat.CO` (computation), `stat.ME` (methodology),
`physics.comp-ph`, `cs.MS` (mathematical software), `cs.DC`
(distributed and parallel computing).

## 3. Programmatic lookup

Use these instead of scraping search pages. All return structured
metadata that maps directly onto a BibTeX entry. Cache responses per
`agent-resource-discipline/references/web-fetch-discipline.md`.

```bash
# arXiv: search (Atom XML). Note https; http redirects.
curl -sSL "https://export.arxiv.org/api/query?search_query=cat:math.NA+AND+all:%22experimental+design%22&max_results=20"

# OpenAlex: search, with citation count and DOI (JSON, no key).
curl -sS "https://api.openalex.org/works?search=optimal%20experimental%20design%20inverse%20problems&per-page=20&select=display_name,doi,publication_year,cited_by_count"

# OpenAlex: forward snowball -- works citing a given work ID.
curl -sS "https://api.openalex.org/works?filter=cites:W<id>&per-page=50"

# Crossref: bibliographic match to a DOI.
curl -sS "https://api.crossref.org/works?query.bibliographic=<title+first-author>&rows=5&select=DOI,title,author,issued"

# OSTI: DOE reports and DOE-funded articles (JSON).
curl -sS -H "Accept: application/json" "https://www.osti.gov/api/v1/records?q=%22<phrase>%22&rows=20"

# Semantic Scholar: search (add -H "x-api-key: ..." if you have one;
# without a key expect HTTP 429 under load -- back off, don't hammer).
curl -sS "https://api.semanticscholar.org/graph/v1/paper/search?query=<terms>&limit=20&fields=title,year,externalIds,citationCount"
```

**DOI to BibTeX** (the hand-off to Step 1):

```bash
curl -sSL -H "Accept: application/x-bibtex" "https://doi.org/<doi>"
```

This returns the publisher-registered record. It is a *starting
point* for a verified entry, not a verified entry: the citekey will
not follow project convention, and fields such as page ranges and
author-name accents are often wrong or missing. Step 1's verification
criteria still apply.

## 4. Judge what you found

- **Published version beats preprint.** When an arXiv paper has a
  journal version (check the arXiv abstract page's "Journal ref" /
  DOI, or Crossref by title), cite and download the journal version,
  per Step 1. Note diverging versions (v1 vs v3) in the collection log.
- **Citation counts need context.** Normalise by age and field; a
  2024 SIAM paper with 15 citations may be more central than a 2012
  ML paper with 300. Counts differ between OpenAlex, Semantic Scholar
  and Google Scholar; record which source you used.
- **Red flags:** predatory venue; retraction (check Retraction Watch
  or the publisher page); no code or data for a computational claim;
  heavy self-citation; results that no later paper reproduces.

Triage each candidate into one of: **must read** (directly relevant or
seminal; full Steps 1-5), **should read** (related method or
comparison; Steps 1-5 with a shorter survey note), **cite only**
(background; Step 1 + Step 5, no survey note), **drop** (log why).

## 5. Log the search

A systematic search is only reproducible if the queries are recorded.
Keep a "Search log" section in `references/_collection_log.md` (the
same human-facing audit trail as Step 5), one entry per query:

```markdown
### Search log

| Date       | Source   | Query                                                         | Hits | Kept | Notes                          |
|:-----------|:---------|:--------------------------------------------------------------|-----:|-----:|:-------------------------------|
| 2026-10-14 | OpenAlex | `optimal experimental design inverse problems`                |  ~3M |    0 | Too broad; narrowed below.     |
| 2026-10-14 | arXiv    | `cat:math.NA AND all:"experimental design"`                   |  212 |    9 | Sorted by date; 2019 onward.   |
```

"Kept" entries proceed to Step 1. "Drop" decisions with a reason
belong in the log too: they are what lets a reviewer, or you in six
months, see that a paper was considered and excluded rather than
missed.

## 6. Hand-off checklist (to Step 1)

For every kept candidate, before starting Step 1, have:

- [ ] DOI (or arXiv ID if genuinely arXiv-only)
- [ ] the source you found it through (for the search log)
- [ ] triage class (must read / should read / cite only)
- [ ] a one-line reason it is relevant (seeds the survey note's
      "Relevance to our paper" section)

---

*Created 2026-10-14 by A. Attia, adapted from genesis-skills
`literature-search` (Apache-2.0; see Provenance above).*
