#!/usr/bin/env python3
"""Step 3: quality checks. Writes data/processed/qa_report.txt.

Plain-language note: this script counts rows at every stage, checks that joins
worked, flags impossible values, and picks five accidents you can look up by hand
on MSHA's website. Read qa_report.txt before trusting any number.
"""

import json

import pandas as pd

from common import PROC, write_stats


def pct(a, b):
    return f"{(100 * a / b):.1f}%" if b else "n/a"


def main():
    c = json.loads((PROC / "build_counts.json").read_text())
    inc = pd.read_csv(PROC / "groundfall_incidents.csv", dtype={"mine_id": str, "subunit_cd": str,
                                                               "degree_injury_cd": str})
    rates = pd.read_csv(PROC / "groundfall_rates.csv")
    L, flags = [], []
    w = L.append

    w("GroundFall-US QA report")
    w("=" * 60)
    w("\n1. Row counts by stage")
    for k in ["raw_accidents", "accidents_in_years", "duplicate_document_no_dropped",
              "ground_failure_records", "raw_mines", "raw_prod_rows", "prod_rows_in_years",
              "rate_cells", "rate_cells_with_hours"]:
        w(f"   {k:38s} {c[k]:>12,}")

    w("\n2. Join match rates (ground-failure records)")
    n = c["ground_failure_records"]
    w(f"   matched to Mines file        {c['ground_failure_matched_to_mines']:>8,}  {pct(c['ground_failure_matched_to_mines'], n)}")
    w(f"   mine x subunit x year hours  {c['ground_failure_with_hours']:>8,}  {pct(c['ground_failure_with_hours'], n)}")
    w(f"   contractor records           {c['ground_failure_contractor']:>8,}  {pct(c['ground_failure_contractor'], n)}")
    w(f"   GF records (non-contractor) falling in a cell with zero hours: {c['gf_rate_records_without_hours_cell']:,}")
    if c["ground_failure_matched_to_mines"] < 0.98 * n:
        flags.append("Mine match rate below 98%")
    if c["ground_failure_unmatched_mine_ids"]:
        w(f"   unmatched mine IDs (first 20): {', '.join(c['ground_failure_unmatched_mine_ids'][:20])}")

    w("\n3. Selection rule check: every MSHA CLASSIFICATION label, 2000-2026 (* = selected)")
    w(f"   labels selected as ground failure: {c['ground_failure_labels_matched']}")
    for lab, k in sorted(c["classification_labels"].items(), key=lambda x: -x[1]):
        mark = "*" if lab in c["ground_failure_labels_matched"] else " "
        w(f"  {mark} {k:>8,}  {lab}")

    w("\n4. Range and sanity checks")
    bad_dates = pd.to_datetime(inc["accident_date"], format="%m/%d/%Y", errors="coerce").isna().sum()
    w(f"   unparseable accident dates: {bad_dates}")
    if bad_dates:
        flags.append(f"{bad_dates} unparseable dates")
    neg = (rates[["hours", "gf_records"]] < 0).sum().sum()
    w(f"   negative hours or counts: {neg}")
    hi = rates[(rates["hours"] >= 200000) & (rates["gf_injury_rate"] > 5)]
    w(f"   cells with >= 200,000 hours and GF rate > 5 per 200k h (injury rate): {len(hi)}")
    w(f"   records missing narrative: {inc['narrative'].isna().sum()}")
    w(f"   records missing state: {inc['state'].isna().sum()}")

    w("\n5. Ground-failure records by year and sector")
    t = inc.pivot_table(index="year", columns="sector", values="document_no", aggfunc="count", fill_value=0)
    w(t.to_string())

    w("\n5b. Severity by sector and mine type (no_injury_accident = reportable fall, nobody hurt)")
    w(pd.crosstab(inc["severity"], inc["sector"] + "/" + inc["mine_type"]).to_string())

    w("\n6. National rates per 200,000 hours, non-contractor, by sector and mine type (2000-2025 pooled)")
    full = rates[~rates["partial_year"]]
    g = full.groupby(["sector", "mine_type"])[["gf_injury", "gf_fatal", "gf_no_injury", "hours"]].sum()
    g["injury_rate_per_200k_h"] = g["gf_injury"] / g["hours"] * 200000
    g["fatal_rate_per_200k_h"] = g["gf_fatal"] / g["hours"] * 200000
    w(g[g["hours"] > 0].round(4).to_string())

    w("\n7. Spot checks: look these up by hand (see docs/VERIFY_CHECKLIST.md)")
    picks = []
    s = inc.sort_values(["year", "accident_date"])
    picks.append(("earliest record", s.iloc[0]))
    picks.append(("most recent record", s.iloc[-1]))
    f = inc[(inc["is_fatal"]) & (inc["sector"] == "metal_nonmetal") & (inc["mine_type"] == "surface")]
    if len(f):
        picks.append(("a surface M/NM fatality", f.sample(1, random_state=11).iloc[0]))
    u = inc[(inc["sector"] == "coal") & (inc["mine_type"] == "underground")]
    if len(u):
        picks.append(("an underground coal roof fall", u.sample(1, random_state=7).iloc[0]))
    k = inc[inc["is_contractor"]]
    if len(k):
        picks.append(("a contractor record", k.sample(1, random_state=3).iloc[0]))
    spot = []
    for why, r in picks:
        w(f"   [{why}] doc {r['document_no']} | mine {r['mine_id']} {r['mine_name']} ({r['state']}) | "
          f"{r['accident_date']} | {r['msha_classification']} | {r['degree_injury']}")
        w(f"      narrative: {str(r['narrative'])[:160]}")
        spot.append({"why": why, "document_no": r["document_no"], "mine_id": r["mine_id"],
                     "date": r["accident_date"], "state": r["state"]})

    w("\n8. Flags")
    w("   " + ("\n   ".join(flags) if flags else "none"))

    (PROC / "qa_report.txt").write_text("\n".join(L) + "\n")
    write_stats({"qa_mine_match_pct": round(100 * c["ground_failure_matched_to_mines"] / n, 2),
                 "qa_hours_match_pct": round(100 * c["ground_failure_with_hours"] / n, 2),
                 "qa_spot_checks": spot, "qa_flags": flags})
    print("\n".join(L[:30]))
    print("... full report in data/processed/qa_report.txt")


if __name__ == "__main__":
    main()
