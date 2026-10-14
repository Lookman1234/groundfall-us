#!/usr/bin/env python3
"""Step 4b: find likely ground failures that MSHA filed under OTHER categories.

Plain-language note: MSHA tags each accident with one cause category. Some real
highwall and bank failures at surface metal/nonmetal mines were tagged as
"powered haulage" or "machinery" instead of a fall category, so the main selection
misses them. This script runs your failure-mode rules over every other surface
metal/nonmetal accident description and lists the ones that look like a ground
failure. Nothing here enters the dataset until you review it: mark each row
accept / reject in the `author_decision` column.

Output: validation/supplement_candidates.csv
"""

import re

import pandas as pd
import yaml

from common import CONFIG, ROOT, load_config, read_msha_zip, zpad

# Must mention a ground element, so plant and equipment rocks are not listed.
GROUND = re.compile(r"\b(high ?walls?|hw|pit walls?|walls?|banks?|slopes?|benche?s?|faces?|"
                    r"hillside|overburden|over burden|berm|ledge)\b", re.I)
# Person falls and plant contexts are not ground failures.
NOT_GROUND = re.compile(r"\b(slipped and fell|lost (his|her|their)? ?footing|tripped|fell from (the )?"
                        r"(ladder|steps|truck|loader|equipment)|work bench|crusher|screen|conveyor|"
                        r"hopper|chute|bin)\b", re.I)


def main():
    cfg = load_config()
    rules = yaml.safe_load((CONFIG / "coding_rules.yaml").read_text())
    pats = [re.compile(p, re.I) for m in rules["modes"].values() for p in m["patterns"]]
    a = read_msha_zip("Accidents.zip")
    a["SUBUNIT_CD"] = zpad(a["SUBUNIT_CD"], 2)
    a["CAL_YR"] = pd.to_numeric(a["CAL_YR"], errors="coerce")
    sc = cfg["coding_scope"]
    y = cfg["years"]
    s = a[(a["COAL_METAL_IND"] == sc["coal_metal_ind"]) & a["SUBUNIT_CD"].isin(sc["subunit_codes"])
          & a["CAL_YR"].between(y["first"], y["last"])
          & ~a["CLASSIFICATION"].fillna("").str.upper().str.startswith("FALL OF")].copy()
    n = s["NARRATIVE"].fillna("")

    def hit(t):
        for p in pats:
            m = p.search(t)
            if m:
                return m.group(0)
        return ""

    s["rule_evidence"] = n.map(hit)
    keep = (s["rule_evidence"] != "") & n.str.contains(GROUND) & ~n.str.contains(NOT_GROUND)
    c = s[keep][["DOCUMENT_NO", "MINE_ID", "CAL_YR", "ACCIDENT_DT", "CLASSIFICATION",
                 "DEGREE_INJURY", "rule_evidence", "NARRATIVE"]].copy()
    c.columns = [x.lower() for x in c.columns]
    c["author_decision"] = ""
    out = ROOT / "validation"
    out.mkdir(exist_ok=True)
    c.sort_values(["cal_yr", "document_no"]).to_csv(out / "supplement_candidates.csv", index=False)
    print(f"Screened {len(s):,} surface M/NM accidents in other categories; {len(c)} candidates")
    print(c["classification"].value_counts().head(8).to_string())


if __name__ == "__main__":
    main()
