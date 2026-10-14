#!/usr/bin/env python3
"""Step 5: draw the sample of narratives Lukman labels by hand.

Plain-language note: this picks accident descriptions at random (plus extra ones
for rare failure modes so each mode gets tested) and writes them to a spreadsheet
with empty columns for your own labels. The sheet does NOT show what the rules
decided, so your labels are independent. The same seed always gives the same
sample, so anyone can check it.

Output: validation/validation_sheet.csv     (you fill this in)
        validation/validation_key.csv       (rule labels and sampling weights; do not open while labeling)
"""

import argparse

import pandas as pd

from common import PROC, ROOT

SEED = 20261011


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--random-n", type=int, default=200)
    ap.add_argument("--extra-per-rare-mode", type=int, default=20)
    a = ap.parse_args()

    df = pd.read_csv(PROC / "groundfall_failure_modes.csv", dtype={"mine_id": str})
    rnd = df.sample(min(a.random_n, len(df)), random_state=SEED)
    rnd = rnd.assign(sample_stratum="random")
    rest = df.drop(rnd.index)
    extra = []
    for mode in ["wedge", "planar", "toppling", "rotational_slide", "raveling",
                 "collapse_mechanism_unstated"]:
        pool = rest[rest["failure_mode"] == mode]
        if len(pool):
            extra.append(pool.sample(min(a.extra_per_rare_mode, len(pool)), random_state=SEED)
                         .assign(sample_stratum=f"oversample_{mode}"))
    s = pd.concat([rnd] + extra).sample(frac=1, random_state=SEED)  # shuffle so strata are hidden

    out = ROOT / "validation"
    out.mkdir(exist_ok=True)
    sheet = s[["document_no", "year", "state", "commodity", "activity", "narrative"]].copy()
    for c in ["author_failure_mode", "author_trigger_blasting", "author_trigger_water",
              "author_trigger_scaling", "author_notes"]:
        sheet[c] = ""
    sheet.to_csv(out / "validation_sheet.csv", index=False)
    s[["document_no", "sample_stratum", "failure_mode", "trigger_blasting", "trigger_water",
       "trigger_scaling"]].to_csv(out / "validation_key.csv", index=False)
    print(f"Wrote {len(sheet)} narratives ({len(rnd)} random, {len(sheet) - len(rnd)} oversampled)")


if __name__ == "__main__":
    main()
