# figures/

This directory holds **final figures** for documentation, papers,
talks, and posters. Every figure here is expected to be reproducible
from a checked-in script + checked-in inputs (or from an
`experiments/<run-id>/` workspace). Figures whose generation cannot
be reproduced are not allowed in this directory.

## Layout

```text
figures/
├── README.md                you are here
├── <topic-or-paper-section>/
│   ├── <figure-name>.pdf    publication-quality vector PDF
│   ├── <figure-name>.png    optional rasterised version for slides
│   ├── <figure-name>.py     the script that generated the figure
│   └── README.md            one-paragraph "what does this figure
│                            show? what data feeds it?"
├── <another-topic>/
│   └── ...
│
├── _drafts/                 (gitignored) WIP figures, not for
│                            citation
└── _preview/                (gitignored) preview / thumbnail caches
```

Group figures by **topic** (or by paper section if the figures support
a paper); avoid a flat directory once you have more than ~5 figures.

## Provenance discipline

Every figure subdirectory has a `README.md` containing:

- **What the figure shows** (one or two sentences).
- **Where the data comes from** (which `experiments/<run-id>/`, OR
  which inline computation in the figure script).
- **The generating script + how to run it** (`python <script>.py`
  or similar).
- **Last regenerated**: `YYYY-MM-DD`.
- **Linked in**: which document(s) cite this figure (paper section,
  talk slide deck, README screenshot, ...).

## Generation script discipline

The `<figure-name>.py` script (or equivalent in another language)
must:

1. **Be runnable from the project root** (handles its own paths
   robustly, e.g. via `pathlib.Path(__file__).parent`).
2. **Read inputs from explicit paths** (no hard-coded absolute
   paths; no "wherever I happened to have it").
3. **Set the RNG seed** if any randomness is used.
4. **Write outputs to the same directory as the script** (so the
   script's working directory IS the figure directory).
5. **Produce both vector + rasterised versions** when both are
   useful (PDF for paper, PNG for slides; matplotlib does this
   in one call).
6. **Use a documented colour palette + font choice** consistent
   across the project's figures (define once in
   `figures/<your-style>.mplstyle` or equivalent).
7. **Be idempotent**: running it twice produces bit-identical
   outputs (modulo PDF metadata timestamps).

Minimal Python skeleton:

```python
"""Figure: <one-line description>.

Sources:
  - <experiments/<run-id>/output/>
  - <other inputs>
"""
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
OUT_BASE = HERE / "<figure-name>"

def load_inputs():
    """Load the data this figure needs."""
    run_dir = HERE.parent.parent / "experiments" / "<run-id>"
    metadata = json.loads((run_dir / "metadata.json").read_text())
    data = np.load(run_dir / "output" / "result.npy")
    return data, metadata

def make_figure(data, metadata):
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot(data[:, 0], data[:, 1])
    ax.set_xlabel("<x label>")
    ax.set_ylabel("<y label>")
    ax.set_title(f"<title> (run {metadata['run_id']})")
    fig.tight_layout()
    return fig

def main():
    data, metadata = load_inputs()
    fig = make_figure(data, metadata)
    fig.savefig(OUT_BASE.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(OUT_BASE.with_suffix(".png"), dpi=200, bbox_inches="tight")
    print(f"wrote {OUT_BASE}.pdf and {OUT_BASE}.png")

if __name__ == "__main__":
    main()
```

## Figure-update workflow

When a figure needs to be updated (new run, new style, new annotation):

1. Rerun the experiment if the underlying numbers changed (do this in
   the experiment's own dir; record a fresh `metadata.json`).
2. Edit the figure script.
3. Run the script; verify the output looks correct.
4. Commit the figure script + the updated PDF/PNG together (same
   commit). The commit message should name the run-id whose data
   changed, if applicable.
5. Update the figure subdirectory's `README.md` "Last regenerated"
   stamp.

## Anti-patterns to refuse

- **Figure files committed with no generating script.** The figure
  becomes uncitable (you can't show how it was made) and uneditable
  (you can't change one element without redrawing from scratch).
- **Figure scripts that read from `~/Downloads/` or other user-
  specific paths.** Move the input into `experiments/<run-id>/output/`
  + reference relatively.
- **Figure scripts that print to stdout but don't save the figure.**
  Always save to disk; the on-screen view is for development only.
- **PDFs with embedded raster images of plots.** Use `matplotlib`'s
  PDF backend (or equivalent), not "screenshot the matplotlib
  window".
- **Figures that don't reproduce on a different machine.** Pin the
  matplotlib version; pin the font (e.g. `mpl.rcParams['font.family']
  = 'serif'`); don't rely on the system's default fonts.

## Cross-references

- For papers that this library supports, the figures here are likely
  identical to (or sources for) figures in the paper repo's
  `figures/` directory. Coordinate via the paper-section tag in each
  figure's `README.md`.
- The `experiments/<run-id>/analysis/` subdirectory is the place for
  exploratory / draft figures; figures graduate to `figures/` once
  they are publication-bound.

---

*Created YYYY-MM-DD by <your name> from
[`scicomp-research-skills/templates/software-skeleton/figures/README.md`](https://github.com/a-attia/scicomp-research-skills/tree/main/templates/software-skeleton/figures/README.md).*
