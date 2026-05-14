# figures/

This directory holds **final figures** consumed by the paper draft +
supplementary material. Every figure here is expected to be
reproducible from a checked-in script + checked-in inputs (or from an
`experiments/<run-id>/` workspace). Figures whose generation cannot
be reproduced are not allowed -- a reviewer or future-you will need
to regenerate at some point (camera-ready edits, rebuttal-round
re-renders, follow-up paper extensions).

This directory is the paper-side analog of
`~/.scicomp-research-skills/templates/software-skeleton/figures/README.md`;
the conventions are identical.

## Layout

```text
figures/
├── README.md                   you are here
├── <paper-section>/
│   ├── <figure-name>.pdf       publication-quality vector PDF
│   ├── <figure-name>.png       optional rasterised version for slides
│   ├── <figure-name>.py        the script that generated the figure
│   └── README.md               one-paragraph "what does this figure
│                               show? what data feeds it?"
├── <another-section>/
│   └── ...
│
├── _drafts/                    (gitignored) WIP figures, not for
│                               citation in the paper
└── _preview/                   (gitignored) preview / thumbnail caches
```

Group figures by **paper section** (e.g. `section-4-method/`,
`section-5-test-case/`, `section-6-experiments/`); avoid a flat
directory once you have more than ~5 figures.

For paper figures specifically: ALSO maintain a one-line caption
draft in each figure subdirectory's `README.md` so future-you can
trace caption-vs-figure churn.

## Provenance discipline

Every figure subdirectory has a `README.md` containing:

- **What the figure shows** (one or two sentences; the eventual
  paper caption can grow from this).
- **Where the data comes from** -- which `experiments/<run-id>/`
  produces the inputs; OR which inline computation in the figure
  script produces them.
- **The generating script + how to run it** (`python <script>.py`
  or similar).
- **Last regenerated**: `YYYY-MM-DD`.
- **Cited in**: which paper section / figure number references this
  (e.g. "Section 5.2, Figure 7a").
- **Linked experiments**: list of `experiments/<run-id>/` whose
  output feeds this figure, so a reviewer asking "where does this
  number come from?" gets a direct trail.

## Generation script discipline

The `<figure-name>.py` script (or `.jl` / `.m` / equivalent) must:

1. **Be runnable from the project root** (handles its own paths,
   e.g. via `pathlib.Path(__file__).parent`).
2. **Read inputs from explicit paths** -- ideally from
   `experiments/<run-id>/output/`; never from absolute paths.
3. **Set the RNG seed** if any randomness is used (rarely needed for
   figure scripts; common for jittered-scatter plots).
4. **Write outputs to the same directory as the script** (so the
   script's working directory IS the figure directory).
5. **Produce both vector + rasterised versions** -- PDF for the
   paper; PNG (200dpi+) for the slide deck / talk.
6. **Use a documented colour palette + font** consistent across the
   project's figures (define once in `figures/<your-style>.mplstyle`
   or equivalent).
7. **Be idempotent** -- running it twice produces bit-identical
   outputs (modulo PDF metadata timestamps).

Minimal Python skeleton:

```python
"""Figure: <one-line description>.

Cited in: <paper section + figure number>.
Sources:
  - experiments/<run-id-1>/output/result.npy
  - experiments/<run-id-2>/output/result.npy
"""
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
OUT_BASE = HERE / "<figure-name>"

def load_inputs():
    """Load the data this figure needs."""
    repo_root = HERE.parent.parent
    runs = ["<run-id-1>", "<run-id-2>"]
    data_per_run = {}
    for run in runs:
        run_dir = repo_root / "experiments" / run
        meta = json.loads((run_dir / "metadata.json").read_text())
        data = np.load(run_dir / "output" / "result.npy")
        data_per_run[run] = (meta, data)
    return data_per_run

def make_figure(data_per_run):
    fig, ax = plt.subplots(figsize=(5, 3))
    for run, (meta, data) in data_per_run.items():
        ax.plot(data[:, 0], data[:, 1], label=meta["tags"][0])
    ax.set_xlabel("<x label>")
    ax.set_ylabel("<y label>")
    ax.set_title("<title>")
    ax.legend()
    fig.tight_layout()
    return fig

def main():
    data_per_run = load_inputs()
    fig = make_figure(data_per_run)
    fig.savefig(OUT_BASE.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(OUT_BASE.with_suffix(".png"), dpi=200, bbox_inches="tight")
    print(f"wrote {OUT_BASE}.pdf and {OUT_BASE}.png")

if __name__ == "__main__":
    main()
```

## Figure-update workflow

When a figure needs updating (new run, new style, rebuttal-round
addition, camera-ready edit):

1. Re-run the experiment if the underlying numbers changed (in the
   experiment's own dir; record fresh `metadata.json`).
2. Edit the figure script.
3. Run the script; verify output looks correct.
4. Commit script + PDF + PNG together (same commit). Commit message
   names the run-id whose data changed.
5. Update the figure subdirectory's `README.md` "Last regenerated"
   stamp.
6. If the paper draft references this figure, also update the draft
   if the change affects the caption or the surrounding text.

## Anti-patterns to refuse

- **Figure files committed with no generating script.** The figure
  becomes uncitable + uneditable; a rebuttal-round re-render is
  impossible.
- **Figure scripts that read from `~/Downloads/` or other
  user-specific paths.** Move inputs into `experiments/<run-id>/output/`
  + reference relatively.
- **PDFs with embedded raster images of plots.** Use matplotlib's PDF
  backend (or equivalent), not "screenshot the matplotlib window".
- **Figures that don't reproduce on a different machine.** Pin
  matplotlib version; pin font (e.g. `mpl.rcParams['font.family'] =
  'serif'`); don't rely on system defaults.
- **Captions in `<figure>.py` that disagree with the LaTeX caption
  in the paper draft.** The figure-script README's "Cited in" field
  is the bridge; keep both in sync.

## Cross-references

- For numbers in the paper that come from this figure, the audit
  trail is: paper text -> `figures/<section>/<name>/README.md` ->
  `experiments/<run-id>/metadata.json` -> commit hash + lockfile +
  seed -> reproducible.
- The `notes/section_<N>.md` working notes for each paper section
  can list all the figures contributing to that section, mirroring
  this directory's per-section grouping.

---

*Created YYYY-MM-DD by <your name> from
[`scicomp-research-skills/templates/paper-skeleton/figures/README.md`](https://github.com/a-attia/scicomp-research-skills/tree/main/templates/paper-skeleton/figures/README.md).*
