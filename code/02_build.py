#!/usr/bin/env python3
"""Step 2: clean, select ground failures, join to mines and hours, compute rates.

Plain-language note: this script turns the three raw MSHA files into the two main
GroundFall-US tables. It picks out ground-failure accidents, attaches each one to
its mine (state, commodity, mine type), and divides accident counts by hours worked
to get rates. Decisions it uses live in config/selection.yaml. You do not need to
open this file.

Outputs:
  data/processed/groundfall_incidents.csv   one row per ground-failure accident record
  data/processed/groundfall_rates.csv       counts, hours, and rates by year x sector x
                                            mine type x commodity x state
  data/processed/build_counts.json          row counts at each stage (read by 03_qa.py)
"""

import json
import re

import numpy as np
import pandas as pd

from common import PROC, load_config, read_msha_zip, write_stats, zpad

INJURY_DEGREES = {"01", "02", "03", "04", "05", "06"}
LOST_TIME_DEGREES = {"01", "02", "03", "04"}


def main():
    cfg = load_config()
    y0, y1 = cfg["years"]["first"], cfg["years"]["last"]
    counts = {}

    # --- load ---------------------------------------------------------------
    acc = read_msha_zip("Accidents.zip")
    mines = read_msha_zip("Mines.zip")
    prod = read_msha_zip("MinesProdYearly.zip")
    counts["raw_accidents"] = len(acc)
    counts["raw_mines"] = len(mines)
    counts["raw_prod_rows"] = len(prod)

    for df in (acc, mines, prod):
        df["MINE_ID"] = zpad(df["MINE_ID"], 7)
    for df in (acc, prod):
        df["SUBUNIT_CD"] = zpad(df["SUBUNIT_CD"], 2)
        df["CAL_YR"] = pd.to_numeric(df["CAL_YR"], errors="coerce").astype("Int64")
    acc["DEGREE_INJURY_CD"] = zpad(acc["DEGREE_INJURY_CD"], 2)
    mines["PRIMARY_CANVASS_CD"] = mines["PRIMARY_CANVASS_CD"].str.replace(r"\.0$", "", regex=True)

    # --- accidents: year window and de-duplication ------------------------------
    acc = acc[acc["CAL_YR"].between(y0, y1)].copy()
    counts["accidents_in_years"] = len(acc)
    dup = acc.duplicated(subset=["DOCUMENT_NO"], keep="first") & acc["DOCUMENT_NO"].notna()
    counts["duplicate_document_no_dropped"] = int(dup.sum())
    acc = acc[~dup].copy()

    # Record every CLASSIFICATION label seen, so the selection rule can be checked.
    counts["classification_labels"] = (acc["CLASSIFICATION"].fillna("<blank>")
                                       .value_counts().to_dict())

    pat = "|".join(re.escape(p) for p in cfg["ground_failure_classification_patterns"])
    acc["is_ground_failure"] = acc["CLASSIFICATION"].fillna("").str.upper().str.contains(pat)
    counts["ground_failure_labels_matched"] = sorted(
        acc.loc[acc["is_ground_failure"], "CLASSIFICATION"].unique().tolist())

    # --- derived fields on all accidents (needed for rate denominators of context) --
    sg = cfg["subunit_groups"]
    cg = cfg["canvass_groups"]
    acc["sector"] = acc["COAL_METAL_IND"].map({"C": "coal", "M": "metal_nonmetal"})
    acc["mine_type"] = acc["SUBUNIT_CD"].map(sg).fillna("other_unknown")
    acc["is_contractor"] = acc["CONTRACTOR_ID"].notna()
    acc["is_fatal"] = acc["DEGREE_INJURY_CD"].eq("01")
    acc["is_injury"] = acc["DEGREE_INJURY_CD"].isin(INJURY_DEGREES)
    acc["is_lost_time"] = acc["DEGREE_INJURY_CD"].isin(LOST_TIME_DEGREES)
    acc["is_no_injury"] = acc["DEGREE_INJURY_CD"].eq("00")
    acc["severity"] = np.select(
        [acc["is_fatal"], acc["is_lost_time"], acc["is_injury"], acc["is_no_injury"]],
        ["fatal", "lost_time", "other_reportable_injury", "no_injury_accident"], default="other_or_unknown")

    mcols = ["MINE_ID", "CURRENT_MINE_NAME", "STATE", "FIPS_CNTY_CD", "FIPS_CNTY_NM",
             "CURRENT_MINE_TYPE", "PRIMARY_CANVASS_CD", "PRIMARY_SIC", "LATITUDE", "LONGITUDE"]
    m = mines[mcols].drop_duplicates("MINE_ID")
    acc = acc.merge(m, on="MINE_ID", how="left", indicator="_mine_match")
    acc["commodity"] = acc["PRIMARY_CANVASS_CD"].map(cg).fillna("unknown")

    gf = acc[acc["is_ground_failure"]].copy()
    counts["ground_failure_records"] = len(gf)
    counts["ground_failure_matched_to_mines"] = int((gf["_mine_match"] == "both").sum())
    counts["ground_failure_unmatched_mine_ids"] = sorted(
        gf.loc[gf["_mine_match"] != "both", "MINE_ID"].dropna().unique().tolist())[:200]

    # --- hours worked -------------------------------------------------------
    prod["ANNUAL_HOURS"] = pd.to_numeric(prod["ANNUAL_HOURS"], errors="coerce")
    prod["AVG_EMPLOYEE_CNT"] = pd.to_numeric(prod["AVG_EMPLOYEE_CNT"], errors="coerce")
    prod = prod[prod["CAL_YR"].between(y0, y1)].copy()
    prod["sector"] = prod["COAL_METAL_IND"].map({"C": "coal", "M": "metal_nonmetal"})
    prod["mine_type"] = prod["SUBUNIT_CD"].map(sg).fillna("other_unknown")
    prod = prod.merge(m[["MINE_ID", "PRIMARY_CANVASS_CD"]], on="MINE_ID", how="left")
    prod["commodity"] = prod["PRIMARY_CANVASS_CD"].map(cg).fillna("unknown")
    prod = prod.rename(columns={"STATE": "STATE_PROD"})
    prod = prod.merge(m[["MINE_ID", "STATE"]], on="MINE_ID", how="left")
    prod["STATE"] = prod["STATE"].fillna(prod["STATE_PROD"])
    counts["prod_rows_in_years"] = len(prod)

    # Does each ground-failure record have hours for its mine x subunit x year?
    keys = prod.loc[prod["ANNUAL_HOURS"] > 0, ["MINE_ID", "SUBUNIT_CD", "CAL_YR"]].drop_duplicates()
    keys["_has_hours"] = True
    gf = gf.merge(keys, on=["MINE_ID", "SUBUNIT_CD", "CAL_YR"], how="left")
    gf["has_hours_same_year"] = gf["_has_hours"].fillna(False).astype(bool)
    counts["ground_failure_with_hours"] = int(gf["has_hours_same_year"].sum())
    counts["ground_failure_contractor"] = int(gf["is_contractor"].sum())

    # --- rate table ---------------------------------------------------------
    dims = ["CAL_YR", "sector", "mine_type", "commodity", "STATE"]
    rate_acc = acc[~acc["is_contractor"]] if cfg["exclude_contractors_from_rates"] else acc
    gfr = rate_acc[rate_acc["is_ground_failure"]]
    num = gfr.groupby(dims, dropna=False).agg(
        gf_records=("DOCUMENT_NO", "size"),
        gf_injury=("is_injury", "sum"),
        gf_lost_time=("is_lost_time", "sum"),
        gf_fatal=("is_fatal", "sum"),
        gf_no_injury=("is_no_injury", "sum"))
    allc = rate_acc.groupby(dims, dropna=False).agg(all_records=("DOCUMENT_NO", "size"))
    den = prod.groupby(dims, dropna=False).agg(hours=("ANNUAL_HOURS", "sum"),
                                                avg_employees=("AVG_EMPLOYEE_CNT", "sum"))
    rates = den.join(num, how="outer").join(allc, how="outer").reset_index()
    for c in ["gf_records", "gf_injury", "gf_lost_time", "gf_fatal", "gf_no_injury", "all_records"]:
        rates[c] = rates[c].fillna(0).astype(int)
    base = cfg["rate_base_hours"]
    ok = rates["hours"] > 0
    for c in ["gf_injury", "gf_lost_time", "gf_fatal", "gf_records"]:
        rates[f"{c}_rate"] = np.where(ok, rates[c] / rates["hours"] * base, np.nan)
    rates["partial_year"] = rates["CAL_YR"].eq(cfg["partial_year"])
    rates = rates.rename(columns={"CAL_YR": "year", "STATE": "state"})
    counts["rate_cells"] = len(rates)
    counts["rate_cells_with_hours"] = int(ok.sum())
    counts["gf_rate_records_without_hours_cell"] = int(rates.loc[~ok, "gf_records"].sum())

    # --- incident table -----------------------------------------------------
    gf["partial_year"] = gf["CAL_YR"].eq(cfg["partial_year"])
    out_cols = {
        "DOCUMENT_NO": "document_no", "MINE_ID": "mine_id", "CURRENT_MINE_NAME": "mine_name",
        "STATE": "state", "FIPS_CNTY_NM": "county", "LATITUDE": "latitude",
        "LONGITUDE": "longitude", "ACCIDENT_DT": "accident_date", "CAL_YR": "year",
        "sector": "sector", "SUBUNIT_CD": "subunit_cd", "SUBUNIT": "subunit",
        "mine_type": "mine_type", "commodity": "commodity", "PRIMARY_SIC": "primary_sic",
        "CLASSIFICATION": "msha_classification", "ACCIDENT_TYPE": "msha_accident_type",
        "IMMED_NOTIFY": "msha_immediate_notify", "DEGREE_INJURY_CD": "degree_injury_cd",
        "DEGREE_INJURY": "degree_injury", "severity": "severity", "is_fatal": "is_fatal", "is_injury": "is_injury",
        "is_lost_time": "is_lost_time", "is_contractor": "is_contractor",
        "CONTRACTOR_ID": "contractor_id", "OCCUPATION": "occupation", "ACTIVITY": "activity",
        "MINING_EQUIP": "mining_equipment", "UG_LOCATION": "ug_location",
        "has_hours_same_year": "has_hours_same_year", "partial_year": "partial_year",
        "NARRATIVE": "narrative",
    }
    inc = gf[list(out_cols)].rename(columns=out_cols).sort_values(["year", "accident_date", "document_no"])

    PROC.mkdir(parents=True, exist_ok=True)
    inc.to_csv(PROC / "groundfall_incidents.csv", index=False)
    rates.to_csv(PROC / "groundfall_rates.csv", index=False)
    (PROC / "build_counts.json").write_text(json.dumps(counts, indent=2, default=str))

    write_stats({"n_ground_failure_records": len(inc),
                 "n_ground_failure_injury": int(inc["is_injury"].sum()),
                 "n_ground_failure_no_injury": int((inc["severity"] == "no_injury_accident").sum()),
                 "n_ground_failure_fatal": int(inc["is_fatal"].sum()),
                 "year_first": y0, "year_last": y1})
    print(f"Ground-failure records: {len(inc):,} of {counts['accidents_in_years']:,} accidents "
          f"{y0}-{y1}; rate cells: {len(rates):,}")


if __name__ == "__main__":
    main()
