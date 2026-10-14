#!/usr/bin/env python3
"""Step 9: numbers, tables, and figures for the preprint.

Plain-language note: every number in the preprint comes from this script. It writes
paper/numbers.tex (one LaTeX command per number), paper/tables/*.tex, and
paper/figures/paper_*.pdf. The manuscript only refers to these, so text and data
cannot disagree. Re-run after any data change, then rebuild the PDF.
"""

import json
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from common import CONFIG, PAPER, PROC, ROOT, load_config, read_msha_zip, zpad

INJ = {"01", "02", "03", "04", "05", "06"}
TEX = PAPER / "tables"
FIG = PAPER / "figures"
INK, INK2, GRID, SURF = "#111111", "#4a4a4a", "#dddddd", "#ffffff"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
N = {}  # macro name -> formatted value


DIGITS = dict(zip("0123456789", ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven",
                                  "Eight", "Nine"]))


def put(name, value, fmt=None):
    """Store a number for the paper. LaTeX command names cannot contain digits."""
    name = "".join(DIGITS.get(ch, ch) for ch in name)
    if fmt == "int":
        value = f"{int(value):,}"
    elif fmt:
        value = format(value, fmt)
    N[name] = str(value)


def esc(s):
    s = str(s).replace("\\", "\x00")
    for a, b in [("&", r"\&"), ("%", r"\%"), ("$", r"\$"),
                 ("#", r"\#"), ("_", r"\_"), ("{", r"\{"), ("}", r"\}"), ("~", r"\~{}"),
                 ("^", r"\^{}"), ('""', '"')]:
        s = s.replace(a, b)
    s = re.sub(r'"([^"]*)"', r"``\1''", s)
    return s.replace("\ufffd", "'").replace("\x00", r"\textbackslash{}")


def brk(s):
    """Allow line breaks inside long regular expressions in tables."""
    return s.replace("|", "|\\allowbreak{}").replace(")", ")\\allowbreak{}")


def style(ax):
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color("#bbbbbb")
    ax.tick_params(colors=INK2, labelsize=7, length=0)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def main():
    TEX.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Nimbus Roman",
                         "DejaVu Serif"], "pdf.fonttype": 42})
    cfg = load_config()
    s = json.loads((PAPER / "stats.json").read_text())

    # ---- all accidents (context: shares of injuries and deaths) --------------
    a = read_msha_zip("Accidents.zip")
    a["CAL_YR"] = pd.to_numeric(a["CAL_YR"], errors="coerce")
    a["SUBUNIT_CD"] = zpad(a["SUBUNIT_CD"], 2)
    a["DEGREE_INJURY_CD"] = zpad(a["DEGREE_INJURY_CD"], 2)
    a = a[a["CAL_YR"].between(2000, 2026)]
    a["gf"] = a["CLASSIFICATION"].fillna("").str.upper().str.startswith("FALL OF")
    fat, inj = a[a["DEGREE_INJURY_CD"] == "01"], a[a["DEGREE_INJURY_CD"].isin(INJ)]
    put("MineMatchPct", s["qa_mine_match_pct"], ".1f")
    put("HoursMatchPct", s["qa_hours_match_pct"], ".2f")
    put("NAllAccidents", len(a), "int")
    put("NAllFatal", len(fat), "int")
    put("NAllInjury", len(inj), "int")
    put("PctGFofInjury", 100 * inj["gf"].mean(), ".1f")
    put("PctGFofFatal", 100 * fat["gf"].mean(), ".1f")
    put("CFRAll", 100 * len(fat) / len(inj), ".2f")
    for sec, nm in [("C", "Coal"), ("M", "MNM")]:
        f = fat[fat["COAL_METAL_IND"] == sec]
        put(f"PctGFofFatal{nm}", 100 * f["gf"].mean(), ".1f")
        put(f"NFatal{nm}", len(f), "int")

    # ---- incident table --------------------------------------------------------
    i = pd.read_csv(PROC / "groundfall_incidents.csv", dtype=str)
    for c in ["is_fatal", "is_injury", "is_contractor"]:
        i[c] = i[c] == "True"
    i["year"] = i["year"].astype(int)
    put("NGF", len(i), "int")
    put("NGFInjury", i["is_injury"].sum(), "int")
    put("NGFFatal", i["is_fatal"].sum(), "int")
    put("NGFNoInjury", (i["severity"] == "no_injury_accident").sum(), "int")
    put("PctGFNoInjury", 100 * (i["severity"] == "no_injury_accident").mean(), ".1f")
    put("NGFContractor", i["is_contractor"].sum(), "int")
    put("CFRGF", 100 * i["is_fatal"].sum() / i["is_injury"].sum(), ".2f")
    put("CFRRatio", (i["is_fatal"].sum() / i["is_injury"].sum()) / (len(fat) / len(inj)), ".1f")
    put("NRoof", (i["msha_classification"] == "FALL OF ROOF OR BACK").sum(), "int")
    put("NFace", i["msha_classification"].str.contains("FACE").sum(), "int")
    for sec, mt, nm in [("coal", "surface", "CSurf"), ("metal_nonmetal", "surface", "MSurf")]:
        d = i[(i["sector"] == sec) & (i["mine_type"] == mt)]
        put(f"NFace{nm}", d["msha_classification"].str.contains("FACE").sum(), "int")
    put("LastDate", i.sort_values(["year", "accident_date"]).iloc[-1]["accident_date"])

    # severity / case fatality by setting
    rows = []
    keys = [("coal", "underground", "Coal, underground"), ("coal", "surface", "Coal, surface"),
            ("metal_nonmetal", "underground", "M/NM, underground"),
            ("metal_nonmetal", "surface", "M/NM, surface")]
    for sec, mt, lab in keys:
        d = i[(i["sector"] == sec) & (i["mine_type"] == mt)]
        nm = (sec[:1].upper() + ("UG" if mt == "underground" else "Surf"))
        cfr = 100 * d["is_fatal"].sum() / max(d["is_injury"].sum(), 1)
        put(f"N{nm}", len(d), "int")
        put(f"NInj{nm}", d["is_injury"].sum(), "int")
        put(f"NFat{nm}", d["is_fatal"].sum(), "int")
        put(f"NNoInj{nm}", (d["severity"] == "no_injury_accident").sum(), "int")
        put(f"CFR{nm}", cfr, ".1f")
        put(f"PctNoInj{nm}", 100 * (d["severity"] == "no_injury_accident").mean(), ".1f")
        rows.append((lab, len(d), (d["severity"] == "no_injury_accident").sum(), d["is_injury"].sum(),
                     d["is_fatal"].sum(), cfr))
    with open(TEX / "severity.tex", "w") as f:
        for lab, n, ni, nj, nf, c in rows:
            f.write(f"{lab} & {n:,} & {ni:,} & {nj:,} & {nf} & {c:.1f} \\\\\n")
    surf_inj = sum(r[3] for r in rows if "surface" in r[0])
    surf_fat = sum(r[4] for r in rows if "surface" in r[0])
    put("NSurfInj", surf_inj, "int")
    put("NSurfFat", surf_fat, "int")
    put("CFRSurf", 100 * surf_fat / surf_inj, ".1f")
    ug_inj = sum(r[3] for r in rows if "underground" in r[0])
    ug_fat = sum(r[4] for r in rows if "underground" in r[0])
    put("CFRUG", 100 * ug_fat / ug_inj, ".1f")
    put("CFRSurfVsUG", (surf_fat / surf_inj) / (ug_fat / ug_inj), ".0f")

    # ---- rates -----------------------------------------------------------------
    r = pd.read_csv(PROC / "groundfall_rates.csv")
    r = r[~r["partial_year"]]
    r["period"] = pd.cut(r["year"], [1999, 2004, 2009, 2014, 2019, 2025],
                         labels=["2000--04", "2005--09", "2010--14", "2015--19", "2020--25"])
    g = (r[r["mine_type"].isin(["surface", "underground"])]
         .groupby(["sector", "mine_type", "period"], observed=True)[["gf_injury", "gf_fatal", "hours"]].sum())
    g["rate"] = g["gf_injury"] / g["hours"] * 2e5
    g["frate"] = g["gf_fatal"] / g["hours"] * 1e8
    with open(TEX / "periods.tex", "w") as f:
        for sec, mt, lab in keys:
            sub = g.loc[(sec, mt)]
            cells = " & ".join(f"{v:.3f}" if mt == "underground" else f"{v:.4f}" for v in sub["rate"])
            f.write(f"{lab} & {cells} \\\\\n")
        f.write("\\midrule\n")
        for sec, mt, lab in keys:
            sub = g.loc[(sec, mt)]
            cells = " & ".join(f"{v:.1f}" for v in sub["frate"])
            f.write(f"{lab} & {cells} \\\\\n")
    for sec, mt, _ in keys:
        nm = (sec[:1].upper() + ("UG" if mt == "underground" else "Surf"))
        sub = g.loc[(sec, mt)]
        put(f"RateFirst{nm}", sub["rate"].iloc[0], ".3f" if mt == "underground" else ".4f")
        put(f"RateLast{nm}", sub["rate"].iloc[-1], ".3f" if mt == "underground" else ".4f")
        put(f"RateDrop{nm}", 100 * (1 - sub["rate"].iloc[-1] / sub["rate"].iloc[0]), ".0f")
        put(f"FRateFirst{nm}", sub["frate"].iloc[0], ".1f")
        put(f"FRateLast{nm}", sub["frate"].iloc[-1], ".1f")
        put(f"FRateDrop{nm}", 100 * (1 - sub["frate"].iloc[-1] / sub["frate"].iloc[0]), ".0f")
        tot = r[(r["sector"] == sec) & (r["mine_type"] == mt)][["gf_injury", "gf_fatal", "hours"]].sum()
        put(f"RateAll{nm}", tot["gf_injury"] / tot["hours"] * 2e5, ".3f" if mt == "underground" else ".4f")
        put(f"FRateAll{nm}", tot["gf_fatal"] / tot["hours"] * 1e8, ".1f")
        put(f"Hours{nm}", tot["hours"] / 1e9, ".2f")
    # exact Poisson 95% intervals for period fatality rates (small counts)
    from scipy.stats import chi2
    for sec, mt, _ in keys:
        nm = (sec[:1].upper() + ("UG" if mt == "underground" else "Surf"))
        sub = g.loc[(sec, mt)]
        for tag, row in [("First", sub.iloc[0]), ("Last", sub.iloc[-1])]:
            k, h = int(row["gf_fatal"]), row["hours"]
            lo = chi2.ppf(0.025, 2 * k) / 2 if k else 0.0
            hi = chi2.ppf(0.975, 2 * k + 2) / 2
            put(f"FCount{tag}{nm}", k, "int")
            put(f"FRateLo{tag}{nm}", lo / h * 1e8, ".1f")
            put(f"FRateHi{tag}{nm}", hi / h * 1e8, ".1f")
    put("RatioUGCoalVsSurfMNM", float(N["RateAllCUG"]) / float(N["RateAllMSurf"]), ".0f")
    put("FRatioUGCoalVsSurfMNM", float(N["FRateAllCUG"]) / float(N["FRateAllMSurf"]), ".0f")
    put("FRatioMNMUGvsSurf", float(N["FRateAllMUG"]) / float(N["FRateAllMSurf"]), ".0f")
    for k in ["rate_coal_underground_2000", "rate_coal_underground_2025",
              "rate_metal_nonmetal_underground_2000", "rate_metal_nonmetal_underground_2025"]:
        put("Y" + "".join(w.capitalize() for w in k.split("_")).replace("Metal", "M").replace("Nonmetal", "NM"),
            s[k], ".2f")

    # commodity table
    gc = (r[r["mine_type"].isin(["surface", "underground"])]
          .groupby(["sector", "mine_type", "commodity"])[["gf_injury", "gf_fatal", "hours"]].sum())
    gc = gc[gc["hours"] >= 1e6]
    lab_c = {"coal": "Coal", "metal": "Metal", "nonmetal": "Nonmetal", "stone": "Stone",
             "sand_gravel": "Sand and gravel"}
    with open(TEX / "commodity.tex", "w") as f:
        for (sec, mt, com), v in gc.iterrows():
            rate = v["gf_injury"] / v["hours"] * 2e5
            fr = v["gf_fatal"] / v["hours"] * 1e8
            mtl = "UG" if mt == "underground" else "Surface"
            f.write(f"{lab_c[com]} & {mtl} & {v['hours'] / 1e6:,.0f} & {int(v['gf_injury']):,} & "
                    f"{int(v['gf_fatal'])} & {rate:.3f} & {fr:.1f} \\\\\n")
    for com in ["metal", "stone", "nonmetal"]:
        v = gc.loc[("metal_nonmetal", "underground", com)]
        put(f"RateUG{com.capitalize()}", v["gf_injury"] / v["hours"] * 2e5, ".3f")
        put(f"FRateUG{com.capitalize()}", v["gf_fatal"] / v["hours"] * 1e8, ".1f")

    # state table: top states by injuries in each underground setting
    with open(TEX / "states.tex", "w") as f:
        for sec, mt, lab in keys:
            st = (r[(r["sector"] == sec) & (r["mine_type"] == mt)]
                  .groupby("state")[["gf_injury", "gf_fatal", "hours"]].sum())
            st = st[st["hours"] > 0]
            share3 = 100 * st["gf_injury"].nlargest(3).sum() / st["gf_injury"].sum()
            nm = (sec[:1].upper() + ("UG" if mt == "underground" else "Surf"))
            put(f"Top3Share{nm}", share3, ".0f")
            put(f"NStates{nm}", len(st), "int")
            top = st.sort_values("gf_injury", ascending=False).head(5)
            cells = "; ".join(f"{sn} {int(v['gf_injury'])} ({v['gf_injury'] / v['hours'] * 2e5:.2f})"
                              if mt == "underground" else f"{sn} {int(v['gf_injury'])}"
                              for sn, v in top.iterrows())
            f.write(f"{lab} & {len(st)} & {share3:.0f} & {cells} \\\\\n")
            if (sec, mt) == ("coal", "underground"):
                put("TopThreeCUG", ", ".join(top.index[:3]))
            if (sec, mt) == ("metal_nonmetal", "underground"):
                id_ = st.loc["ID"]
                put("RateIDMUG", id_["gf_injury"] / id_["hours"] * 2e5, ".2f")
                put("RateNVMUG", st.loc["NV", "gf_injury"] / st.loc["NV", "hours"] * 2e5, ".2f")
                put("InjIDMUG", id_["gf_injury"], "int")
                put("InjNVMUG", st.loc["NV", "gf_injury"], "int")

    # ---- external consistency check (Khademian et al. 2022, 2010-2019) ---------
    x = i[i["year"].between(2010, 2019)]
    put("KhN", len(x), "int")
    put("KhNoInj", (x["severity"] == "no_injury_accident").sum(), "int")
    put("KhFatal", x["is_fatal"].sum(), "int")
    put("KhDiffPct", 100 * (len(x) - 8303) / 8303, ".1f")
    put("KhNoInjDiffPct", 100 * ((x["severity"] == "no_injury_accident").sum() - 5175) / 5175, ".1f")

    # ---- surface M/NM coding layer --------------------------------------------
    m = pd.read_csv(PROC / "groundfall_failure_modes.csv", dtype=str)
    m["is_fatal"] = m["is_fatal"] == "True"
    put("NCoded", len(m), "int")
    put("NCodedFatal", m["is_fatal"].sum(), "int")
    rules = yaml.safe_load((CONFIG / "coding_rules.yaml").read_text())
    put("RulesVersion", rules["version"])
    put("NPatterns", sum(len(v["patterns"]) for v in rules["modes"].values())
        + sum(len(v["patterns"]) for v in rules["triggers"].values()), "int")
    order = ["rockfall", "collapse_mechanism_unstated", "raveling", "toppling", "rotational_slide",
             "wedge", "planar", "unspecified"]
    labm = {"collapse_mechanism_unstated": "Collapse, mechanism unstated",
            "rotational_slide": "Rotational slide"}
    with open(TEX / "modes.tex", "w") as f:
        for k in order:
            d = m[m["failure_mode"] == k]
            put("Mode" + "".join(w.capitalize() for w in k.split("_")), len(d), "int")
            f.write(f"{labm.get(k, k.capitalize())} & {len(d)} & {100 * len(d) / len(m):.0f} & "
                    f"{d['is_fatal'].sum()} \\\\\n")
    put("PctUnspecified", 100 * (m["failure_mode"] == "unspecified").mean(), ".0f")
    put("PctMechanismNamed", 100 * m["failure_mode"].isin(
        ["wedge", "planar", "toppling", "rotational_slide"]).mean(), ".0f")
    put("NMechanismNamed", m["failure_mode"].isin(["wedge", "planar", "toppling", "rotational_slide"]).sum(), "int")
    for t in ["blasting", "water", "scaling"]:
        put("Trig" + t.capitalize(), (m[f"trigger_{t}"] == "True").sum(), "int")
    put("TrigAny", (m["any_trigger"] == "True").sum(), "int")
    put("PctTrigAny", 100 * (m["any_trigger"] == "True").mean(), ".0f")
    for k in ["stone", "metal", "sand_gravel", "nonmetal"]:
        put("Com" + "".join(w.capitalize() for w in k.split("_")), (m["commodity"] == k).sum(), "int")
    eq = r"\bloader|\b988|\b992|excavator|backhoe|trackhoe|haul truck|\btruck\b|\bdrill|dozer|\bshovel|dredge|boat"
    put("NEquipment", m["narrative"].str.contains(eq, case=False, regex=True).sum(), "int")
    put("PctEquipment", 100 * m["narrative"].str.contains(eq, case=False, regex=True).mean(), ".0f")
    put("NExcavator", m["narrative"].str.contains("excavator|backhoe|trackhoe", case=False).sum(), "int")
    put("NLoader", m["narrative"].str.contains(r"\bloader|\b988|\b992", case=False, regex=True).sum(), "int")
    put("NCollapseFatal", m[m["failure_mode"] == "collapse_mechanism_unstated"]["is_fatal"].sum(), "int")
    put("NNoInjCoded", (m["degree_injury"] == "ACCIDENT ONLY").sum(), "int")

    # rules table (appendix): first pattern of each mode as illustration, plus counts
    with open(TEX / "rules.tex", "w") as f:
        for k in rules["mode_precedence"] + ["unspecified"]:
            if k == "unspecified":
                f.write("Unspecified & -- & no mode pattern matched \\\\\n")
                continue
            p = rules["modes"][k]["patterns"]
            ex = rules["modes"][k].get("exclude", [])
            f.write(f"{labm.get(k, k.capitalize())} & {len(p)} & \\texttt{{{brk(esc(p[0]))}}}"
                    + (f"; excludes \\texttt{{{esc(ex[0])}}}" if ex else "") + " \\\\\n")
        f.write("\\midrule\n")
        for k, v in rules["triggers"].items():
            ex = v.get("exclude", [])
            f.write(f"Trigger: {k} & {len(v['patterns'])} & \\texttt{{{brk(esc(v['patterns'][0]))}}}"
                    + (f"; excludes \\texttt{{{esc(ex[0])}}}" if ex else "") + " \\\\\n")

    # ---- supplement candidates ---------------------------------------------------
    c = pd.read_csv(ROOT / "validation" / "supplement_candidates.csv", dtype=str)
    put("NCand", len(c), "int")
    put("NCandFatal", (c["degree_injury"] == "FATALITY").sum(), "int")
    cc = c["classification"].value_counts()
    with open(TEX / "candidates.tex", "w") as f:
        for k, v in cc.head(7).items():
            nf = ((c["classification"] == k) & (c["degree_injury"] == "FATALITY")).sum()
            f.write(f"{esc(k.capitalize())} & {v} & {nf} \\\\\n")
        rest = cc.iloc[7:].sum()
        nf = ((~c["classification"].isin(cc.head(7).index)) & (c["degree_injury"] == "FATALITY")).sum()
        f.write(f"All other categories & {rest} & {nf} \\\\\n")
    put("NCandPH", cc.get("POWERED HAULAGE", 0), "int")
    put("NCandMach", cc.get("MACHINERY", 0), "int")
    put("CandRatio", len(c) / len(m), ".1f")

    # ---- quote tables (verbatim public MSHA narratives) --------------------------
    def quotes(fname, docs, frame, extra=None):
        with open(TEX / fname, "w") as f:
            for j, (doc, head) in enumerate(docs):
                row = frame[frame["document_no"] == doc]
                if row.empty:
                    raise SystemExit(f"quote {doc} not found")
                row = row.iloc[0]
                txt = esc(row["narrative"]).strip()
                ctx = extra(row) if extra else ""
                f.write(f"\\textbf{{{head}}} {ctx}\\newline \\textit{{``{txt}''}} \\\\\n")
                if j < len(docs) - 1:
                    f.write("\\midrule\n")

    deg = {"FATALITY": "fatal", "DAYS AWAY FROM WORK ONLY": "days away from work",
           "DYS AWY FRM WRK & RESTRCTD ACT": "days away and restricted work",
           "DAYS RESTRICTED ACTIVITY ONLY": "restricted work", "NO DYS AWY FRM WRK,NO RSTR ACT":
           "no days away or restriction", "ACCIDENT ONLY": "no injury",
           "INJURIES INVOLVNG NONEMPLOYEES": "non-employee injured",
           "PERM TOT OR PERM PRTL DISABLTY": "permanent disability"}
    readable = lambda x: esc(deg.get(x, str(x).lower()))
    cm = {"stone": "stone", "metal": "metal", "nonmetal": "nonmetal", "sand_gravel": "sand and gravel"}
    sev = lambda row: f"({cm[row['commodity']]}, {row['state']}, {row['year']}; {readable(row['degree_injury'])})"
    quotes("quotes_modes.tex", [
        (_doc(m, "wedge"), "Wedge."),
        (_doc(m, "toppling", 1), "Toppling."),
        (_doc(m, "rotational_slide", 1), "Rotational slide."),
        (_doc(m, "collapse_mechanism_unstated", contains="Excavator was producing"), "Collapse, mechanism unstated."),
        (_doc(m, "rockfall", contains="LARGE ROCK ROLLED FROM THE HIGHWALL"), "Rockfall."),
    ], m, sev)
    quotes("quotes_errors.tex", [
        (_doc(m, "raveling", contains="1.06 million"), "Labelled raveling; a ten-bench highwall failure."),
        (_doc(m, "raveling", contains="500,000"), "Labelled raveling, blasting; a 500,000-ton slough."),
        (_doc(m, "planar", 0), "Labelled planar; mechanism not stated."),
        (_doc(m, "unspecified", contains="cone crusher"), "In MSHA's fall category; not a ground failure."),
    ], m, sev)
    candq = lambda row: f"(MSHA category: {esc(row['classification'].lower())}; {row['cal_yr']}; {readable(row['degree_injury'])})"
    quotes("quotes_candidates.tex", [
        (_doc(c, None, contains="TOPPLED ONTL LOADER", col="narrative"), "Highwall toppling, filed as powered haulage."),
        (_doc(c, None, contains="mine slope collapsed", col="narrative"), "Fatal slope collapse, filed as falling materials."),
        (_doc(c, None, contains="BENCH SLID DOWN 20", col="narrative"), "Bench failure, filed as slip or fall of person."),
        (_doc(c, None, contains="section of the highwall sloughed", col="narrative"), "Highwall slough, filed as machinery."),
        (_doc(c, None, contains="ROCK ROLLED UNDERFOOT", col="narrative"), "Not a ground failure (screen false positive)."),
    ], c, candq)

    # ---- figures for the paper (vector) -----------------------------------------
    gy = (r[r["mine_type"].isin(["surface", "underground"])]
          .groupby(["year", "sector", "mine_type"])[["gf_injury", "hours"]].sum().reset_index())
    gy["rate"] = gy["gf_injury"] / gy["hours"] * 2e5
    fig, axes = plt.subplots(1, 4, figsize=(7.0, 1.75))
    cols = [BLUE, ORANGE, AQUA, YELLOW]
    for ax, (sec, mt, lab), col in zip(axes, keys, cols):
        d = gy[(gy["sector"] == sec) & (gy["mine_type"] == mt)].sort_values("year")
        style(ax)
        ax.plot(d["year"], d["rate"], color=col, linewidth=1.4)
        ax.scatter(d["year"].iloc[[0, -1]], d["rate"].iloc[[0, -1]], s=10, color=col, zorder=3)
        fmt = ".2f" if mt == "underground" else ".3f"
        ax.annotate(format(d["rate"].iloc[0], fmt), (d["year"].iloc[0], d["rate"].iloc[0]),
                    xytext=(-4, 0), textcoords="offset points", fontsize=6.5, color=INK, ha="right",
                    va="center")
        ax.annotate(format(d["rate"].iloc[-1], fmt), (d["year"].iloc[-1], d["rate"].iloc[-1]),
                    xytext=(4, 0), textcoords="offset points", fontsize=6.5, color=INK, ha="left",
                    va="center")
        ax.set_xlim(1993, 2033)
        ax.set_title(lab, fontsize=8, color=INK, loc="left")
        ax.set_ylim(0, d["rate"].max() * 1.3)
        ax.set_xticks([2000, 2010, 2020])
    axes[0].set_ylabel("Injuries per 200,000 h", fontsize=7, color=INK2)
    fig.tight_layout(pad=0.4, w_pad=0.8)
    fig.savefig(FIG / "paper_rates.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(3.3, 1.7))
    style(ax)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    labs = [r[0] for r in rows][::-1]
    vals = [r[5] for r in rows][::-1]
    ax.barh(labs, vals, color=[YELLOW, AQUA, ORANGE, BLUE], height=0.55)
    for k, v in enumerate(vals):
        ax.text(v + 0.3, k, f"{v:.1f}%", va="center", fontsize=7, color=INK)
    ax.axvline(float(N["CFRAll"]), color=INK2, linewidth=0.8, linestyle=(0, (2, 2)))
    ax.set_xlabel(f"Fatal share of ground-failure injuries (%)\n(dotted line: all MSHA injuries, {N['CFRAll']}%)",
                  fontsize=6.5, color=INK2)
    ax.set_xlim(0, max(vals) * 1.25)
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "paper_cfr.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(3.3, 1.9))
    style(ax)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    vc = m["failure_mode"].value_counts().reindex(order[::-1]).fillna(0)
    fc = m[m["is_fatal"]]["failure_mode"].value_counts().reindex(order[::-1]).fillna(0)
    names = [labm.get(k, k.capitalize()) for k in vc.index]
    ax.barh(names, vc.values, color=BLUE, height=0.6, label="All records")
    ax.barh(names, fc.values, color=ORANGE, height=0.6, label="Fatal")
    for k, (v, fv) in enumerate(zip(vc.values, fc.values)):
        ax.text(v + 0.5, k, f"{int(v)}" + (f" ({int(fv)} fatal)" if fv else ""), va="center", fontsize=6.5, color=INK)
    ax.set_xlim(0, vc.max() * 1.6)
    ax.legend(fontsize=6.5, frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2)
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "paper_modes.pdf")
    plt.close(fig)

    # provenance table (latest fingerprint per source file)
    prov = {}
    for line in (ROOT / "data" / "raw" / "PROVENANCE.txt").read_text().splitlines():
        parts = [x.strip() for x in line.split("|")]
        if len(parts) >= 5:
            prov[parts[1]] = (parts[0], parts[2], parts[3].replace("sha256:", ""))
    with open(TEX / "provenance.tex", "w") as f:
        for name in ["Accidents.zip", "Mines.zip", "MinesProdYearly.zip"]:
            date, size, h = prov[name]
            f.write(f"\\texttt{{{name}}} & {int(size.split()[0]):,} & \\texttt{{\\footnotesize {h[:32]}\\newline {h[32:]}}} \\\\\n")

    with open(PAPER / "numbers.tex", "w") as f:
        f.write("% Generated by code/09_paper_stats.py from the GroundFall-US outputs. Do not edit.\n")
        for k, v in sorted(N.items()):
            f.write(f"\\newcommand{{\\{k}}}{{{v}}}\n")
    (PAPER / "paper_stats.json").write_text(json.dumps(N, indent=1, sort_keys=True))
    print(f"{len(N)} numbers, tables in {TEX}, figures in {FIG}")


def _doc(frame, mode=None, idx=0, contains=None, col="narrative"):
    d = frame if mode is None else frame[frame["failure_mode"] == mode]
    if contains:
        d = d[d[col].str.contains(contains, case=False, regex=False, na=False)]
    return d.iloc[idx]["document_no"]


if __name__ == "__main__":
    main()
