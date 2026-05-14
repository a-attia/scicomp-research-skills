# Web-fetch discipline

Loaded on demand from the `agent-resource-discipline` skill whenever
WebFetch (or its equivalent) is called in a session.

External fetches are slow, rate-limited, and quota-priced. They also
often duplicate information already present in local files.

---

## Cheap-checks-first protocol

Before calling WebFetch, in this order:

1. **Check the local bib entry**. If the citation is in
   `references/bibliography.bib`, the entry's `note`, `url`, `doi`,
   `journal`, `volume`, `pages`, `year` fields likely already answer
   what you need. The user verified the entry; trust it.
2. **Check the local survey note**. If `notes/survey_<citekey>.md`
   exists, the headline claim, method summary, and headline results
   are there. No need to fetch the publisher page.
3. **Check the local `.txt` extraction**. For specific facts (a
   particular equation, a specific table number), grep the `.txt`.
4. **Check `references/_cache/`** if it exists. If a prior session
   fetched the URL and cached it, read the cache.
5. Only then: WebFetch.

## Cache fetched content into the repo

When you do fetch:

- Cache the result into `references/_cache/<sanitised-url>.html` (or
  `.txt` / `.json` as appropriate) with a fetch-date stamp at the top
  of the file.
- The `_cache/` directory should be **gitignored** (regenerable; can
  be large; copyright varies).
- Subsequent fetches of the same URL within a session should use the
  cached file, not a fresh WebFetch.

Skeleton (when shell is available):

```bash
mkdir -p references/_cache
url='https://example.com/paper'
sanitised=$(echo "$url" | sed 's|[/:?]|_|g').html
out="references/_cache/${sanitised}"
if [ ! -f "$out" ]; then
  echo "<!-- fetched $(date -Iseconds) from $url -->" > "$out"
  curl -sL "$url" >> "$out"
fi
```

For agents with WebFetch but not shell-side caching: at minimum,
do not call WebFetch on the same URL twice in one session.

## Source-specific patterns

### arXiv

- For finding a paper's abstract / authors / submission date: prefer
  `https://arxiv.org/abs/<id>` over the PDF URL. Faster, smaller,
  contains everything you usually need.
- For the full paper: download the PDF locally
  (`curl -o references/pdf/<citekey>.pdf https://arxiv.org/pdf/<id>.pdf`),
  then `pdftotext`. Don't WebFetch the PDF binary -- agent tools
  generally cannot consume it.
- Always note the **arXiv version** (v1, v2, v3) in the bib entry's
  `note` field. Different versions can be substantially different.

### Publisher pages (Elsevier, Springer, Wiley, IEEE, ACM, ...)

- For finding DOI / volume / pages / year: fetch the abstract page;
  the metadata is usually there.
- For the full text: most are paywalled. Use the institution's
  authenticated path or the author's preprint server.
- Many publisher pages are JS-heavy; the WebFetch result may be a
  shell with no content. If that happens, fall back to:
  - the DOI's Crossref API page (returns clean JSON metadata);
  - the arXiv preprint if the author posted one;
  - a Google Scholar link to alternative versions.

### GitHub

- For repo metadata (description, stars, latest commit, language):
  fetch `https://api.github.com/repos/<owner>/<repo>` (returns JSON).
  Smaller and structured.
- For repo file contents: fetch
  `https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>`.
  No HTML overhead.
- For the README rendered: fetch
  `https://raw.githubusercontent.com/<owner>/<repo>/<branch>/README.md`.

### Documentation sites (Sphinx, mkdocs, JSDoc, Rust docs, ...)

- Most have a search index. Look for `searchindex.json` or `objects.inv`
  in the site's root before crawling individual pages.
- For Read the Docs sites, the "single-page" or "PDF" version is
  often available and compressing the search to one fetch.

## Rate-limit + retry discipline

When a fetch fails or rate-limits:

1. **Do NOT** immediately retry the same URL. Wait and try a different
   URL first (often the next URL in your queue is on a different host
   anyway).
2. **Do NOT** retry the same URL more than twice per session.
3. **Do NOT** circumvent rate limits with parallel fetches; that gets
   the host's IP blocked.
4. If the fetch genuinely fails: surface to the user with the URL +
   error + what you'll do instead. Don't silently substitute a
   different source.

## When NOT to fetch at all

The agent should refuse (or at least pause + ask) before fetching when:

- The user did not ask for the most-current information; they asked a
  question that local files can answer.
- The information is volatile (today's stock price, today's weather)
  and not relevant to a research-paper or research-software task.
- The URL is from a domain the agent has not seen before AND the
  user did not provide the URL. Avoid speculative fetching of guessed
  URLs.

## Anti-patterns

- **"Let me fetch the publisher page to confirm the year."** The bib
  entry says 2023. The user verified it. Trust the bib.
- **"Let me fetch the paper to find what method they used."** The
  survey note describes the method. Read the note.
- **Fetching the same URL three times in one session.** Once is the
  budget; cache the result and refer to it.
- **Fetching a PDF binary.** Agent tools cannot consume it. Download
  + `pdftotext` instead.
- **Fetching to "be thorough" when no decision depends on the fetch.**
  Every fetch should answer a specific question with a specific
  consequence.

---

*Created 2026-05-13 by A. Attia.*
