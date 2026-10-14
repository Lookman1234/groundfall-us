#!/usr/bin/env python3
"""Step 6: compare the rules with Lukman's hand labels.

Plain-language note: after you fill in validation/validation_sheet.csv, this script
reports how often the rules agree with you, overall and for each failure mode and
trigger. "Kappa" is agreement corrected for lucky guesses (1 = perfect, 0 = no better
than chance; above 0.6 is usually called substantial). Overall numbers use only the
random part of the sample, so they describe the whole dataset fairly; per-mode
numbers use everything.

Output: validation/agreement_report.txt, and numbers added to paper/stats.json
"""

import pandas as pd

from common import ROOT, write_stats

MODES = ["rockfall", "raveling", "planar", "wedge", "toppling", "rotational_slide",
         "collapse_mechanism_unstated", "unspecified"]
YES = {"y", "yes", "1", "true", "t", "x"}


def kappa(a, b):
    a, b = pd.Series(a).reset_index(drop=True), pd.Series(b).reset_index(drop=True)
    n = len(a)
    if n == 0:
        return float("nan")
    po = (a == b).mean()
    cats = set(a) | set(b)
    pe = sum((a == c).mean() * (b == c).mean() for c in cats)
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


def main():
    v = ROOT / "validation"
    sheet = pd.read_csv(v / "validation_sheet.csv", dtype=str)
    key = pd.read_csv(v / "validation_key.csv", dtype={"document_no": str})
    d = sheet.merge(key, on="document_no", how="inner")
    d = d[d["author_failure_mode"].fillna("").str.strip() != ""].copy()
    if d.empty:
        raise SystemExit("No hand labels yet. Fill in author_failure_mode in validation_sheet.csv.")
    d["author_failure_mode"] = d["author_failure_mode"].str.strip().str.lower().str.replace(" ", "_")
    bad = sorted(set(d["author_failure_mode"]) - set(MODES))
    if bad:
        raise SystemExit(f"Unknown labels {bad}. Use one of {MODES}.")

    L = ["GroundFall-US rule validation", "=" * 60, f"Labeled narratives: {len(d)}"]
    r = d[d["sample_stratum"] == "random"]
    L.append(f"Random-sample narratives: {len(r)}")
    stats = {"validation_n": len(d), "validation_random_n": len(r)}

    pa, k = (r["failure_mode"] == r["author_failure_mode"]).mean(), kappa(r["failure_mode"], r["author_failure_mode"])
    L.append(f"\nFailure mode, random sample: agreement {pa:.1%}, Cohen's kappa {k:.2f}")
    stats.update(validation_mode_agreement_pct=round(100 * pa, 1), validation_mode_kappa=round(k, 2))

    L.append("\nPer failure mode (all labeled narratives): rules said X / you said X / both")
    L.append(f"{'mode':18s}{'rules':>7s}{'you':>7s}{'both':>7s}{'precision':>11s}{'recall':>8s}")
    for m in MODES:
        rs, ys = d["failure_mode"] == m, d["author_failure_mode"] == m
        both = (rs & ys).sum()
        prec = both / rs.sum() if rs.sum() else float("nan")
        rec = both / ys.sum() if ys.sum() else float("nan")
        L.append(f"{m:18s}{rs.sum():7d}{ys.sum():7d}{both:7d}{prec:11.2f}{rec:8.2f}")

    L.append("\nTriggers, random sample")
    for t in ["blasting", "water", "scaling"]:
        a = r[f"trigger_{t}"].astype(str).str.lower().isin({"true", "1"})
        b = r[f"author_trigger_{t}"].fillna("").str.strip().str.lower().isin(YES)
        pa, k = (a == b).mean(), kappa(a, b)
        L.append(f"   {t:10s} agreement {pa:.1%}, kappa {k:.2f} (rules yes {a.sum()}, you yes {b.sum()})")
        stats[f"validation_trigger_{t}_kappa"] = round(k, 2)

    L.append("\nDisagreements (all labeled): document_no | rules -> you")
    for _, x in d[d["failure_mode"] != d["author_failure_mode"]].iterrows():
        L.append(f"   {x['document_no']} | {x['failure_mode']} -> {x['author_failure_mode']} | {str(x['narrative'])[:120]}")

    (v / "agreement_report.txt").write_text("\n".join(L) + "\n")
    write_stats(stats)
    print("\n".join(L[:20]))


if __name__ == "__main__":
    main()
