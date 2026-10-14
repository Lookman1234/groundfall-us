#!/usr/bin/env python3
"""Build a tiny SYNTHETIC copy of the three MSHA zips for testing the pipeline.

Plain-language note: these records are invented. They only exist so the code can be
tested without the real files. Nothing from here ever enters the dataset.

Usage: python tests/make_fixture.py <output_dir>
"""

import random
import sys
import zipfile
from pathlib import Path

random.seed(1)
out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)

MINES = [("0200001", "M", "Surface", "AZ", "8", "Copper Ore NEC"),
         ("4600002", "C", "Underground", "WV", "2", "Coal (Bituminous)"),
         ("1100003", "M", "Surface", "IL", "6", "Crushed, Broken Limestone NEC"),
         ("2600004", "M", "Surface", "NV", "8", "Gold Ore"),
         ("0400005", "M", "Surface", "CA", "5", "Construction Sand and Gravel")]
NARR = [
    "EE WAS SCALING THE HIGHWALL WHEN A ROCK FELL FROM THE HW AND STRUCK HIS SHOULDER.",
    "AFTER HEAVY RAIN A SECTION OF THE BANK GAVE WAY AND SLID ONTO THE HAUL ROAD, BURYING THE LOADER.",
    "A WEDGE FAILED ALONG INTERSECTING JOINTS FOLLOWING THE SHOT, STRIKING THE DRILL.",
    "SMALL ROCKS RAVELED DOWN THE FACE AND HIT EE ON THE HAND WHILE HE WAS WEARING A HARD HAT.",
    "A COLUMN OF ROCK TOPPLED FROM THE BENCH ONTO THE TRUCK.",
    "ROOF FELL BETWEEN BOLTS STRIKING EE ON THE BACK.",
    "EE'S HAND WAS WEDGED BETWEEN THE ROLLER AND FRAME.",
]

def write_zip(name, header, rows):
    txt = "|".join(header) + "\n" + "\n".join("|".join(map(str, r)) for r in rows) + "\n"
    with zipfile.ZipFile(out / f"{name}.zip", "w") as z:
        z.writestr(f"{name}.txt", txt.encode("cp1252"))

mh = ["MINE_ID", "CURRENT_MINE_NAME", "COAL_METAL_IND", "CURRENT_MINE_TYPE", "STATE",
      "FIPS_CNTY_CD", "FIPS_CNTY_NM", "PRIMARY_CANVASS_CD", "PRIMARY_SIC", "LATITUDE", "LONGITUDE"]
write_zip("Mines", mh, [(m, f"Test Mine {i}", s, t, st, "001", "Testcounty", c, sic, "33.0", "-111.0")
                        for i, (m, s, t, st, c, sic) in enumerate(MINES)])

ph = ["MINE_ID", "MINE_NAME", "STATE", "SUBUNIT_CD", "SUBUNIT", "CAL_YR", "ANNUAL_HOURS",
      "ANNUAL_COAL_PRODUCTION", "AVG_EMPLOYEE_CNT", "AVG_EMPLOYEE_HOURS", "COAL_METAL_IND"]
prows = []
for m, s, t, st, c, sic in MINES:
    sub = "01" if t == "Underground" else "03"
    for y in range(2000, 2027):
        prows.append((m, "x", st, sub, "x", y, random.randint(100000, 900000), "", 50, 2000, s))
write_zip("MinesProdYearly", ph, prows)

ah = ["MINE_ID", "CONTRACTOR_ID", "DOCUMENT_NO", "SUBUNIT_CD", "SUBUNIT", "ACCIDENT_DT", "CAL_YR",
      "DEGREE_INJURY_CD", "DEGREE_INJURY", "CLASSIFICATION", "ACCIDENT_TYPE", "IMMED_NOTIFY",
      "OCCUPATION", "ACTIVITY", "MINING_EQUIP", "UG_LOCATION", "NARRATIVE", "COAL_METAL_IND"]
arows, n = [], 0
for y in range(1999, 2027):
    for m, s, t, st, c, sic in MINES:
        for _ in range(random.randint(1, 4)):
            n += 1
            sub = "01" if t == "Underground" else random.choice(["03", "30"])
            cls = random.choice(["FALL OF FACE, RIB, PILLAR, SIDE, HIGHWALL", "FALL OF ROOF OR BACK",
                                 "HANDLING OF MATERIALS", "POWERED HAULAGE"])
            deg = random.choice(["01", "03", "05", "06", "00"])
            arows.append((m, random.choice(["", "", "", "ABC1"]), f"2{y}{n:06d}", sub, "x",
                          f"0{random.randint(1,9)}/1{random.randint(0,9)}/{y}", y, deg, "x", cls,
                          "x", "x", "x", random.choice(["Scaling (hand)", "Drilling", "Loading"]),
                          "x", "", random.choice(NARR), s))
write_zip("Accidents", ah, arows)
print(f"synthetic fixture: {len(arows)} accidents, {len(prows)} prod rows -> {out}")
