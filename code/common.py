"""Shared helpers for the GroundFall-US pipeline (paths, config, raw-file reader).

Plain-language note: internal plumbing used by the numbered scripts. You do not
need to open it.
"""

import csv
import io
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
PAPER = ROOT / "paper"
CONFIG = ROOT / "config"


COLUMN_ALIASES = {
    # MinesProdYearly.txt as served -> MineSProdYearly_Definition_File.txt
    "CURR_MINE_NM": "MINE_NAME", "STATE_ABBR": "STATE", "SUBUNIT_DESC": "SUBUNIT",
    "CALENDAR_YR": "CAL_YR", "ANNUAL_HRS": "ANNUAL_HOURS",
    "ANNUAL_COAL_PROD": "ANNUAL_COAL_PRODUCTION", "AVG_ANNUAL_EMPL": "AVG_EMPLOYEE_CNT",
    "C_M_IND": "COAL_METAL_IND",
}


def load_config(name="selection.yaml"):
    with open(CONFIG / name) as f:
        return yaml.safe_load(f)


def read_msha_zip(zname):
    """Read the single delimited table inside an MSHA zip as all-text columns.

    MSHA files are pipe-delimited with a header row and Windows-1252 text. Quotes
    are treated as ordinary characters because narratives contain them.
    """
    path = RAW / zname
    with zipfile.ZipFile(path) as z:
        members = [m for m in z.namelist() if m.lower().endswith((".txt", ".csv"))]
        if len(members) != 1:
            raise RuntimeError(f"{zname}: expected one table, found {members}")
        raw = z.read(members[0])
    text = raw.decode("cp1252", errors="replace")
    sep = "|" if text[:2000].count("|") > text[:2000].count(",") else ","
    df = pd.read_csv(io.StringIO(text), sep=sep, dtype=str, quoting=csv.QUOTE_NONE,
                     keep_default_na=False, na_values=[""], on_bad_lines="warn")
    df.columns = [c.strip().strip('"').upper() for c in df.columns]
    # The files MSHA actually serves use some column names that differ from its
    # definition sheets; map them to the documented names (checked 2026-10-11).
    df = df.rename(columns={k: v for k, v in COLUMN_ALIASES.items() if k in df.columns})
    for c in df.columns:
        df[c] = df[c].str.strip().str.strip('"')
    return df


def zpad(s, n):
    """Left-pad a code with zeros (MSHA IDs and codes sometimes lose leading zeros)."""
    t = s.astype("string").str.replace(r"\.0$", "", regex=True)
    num = t.str.fullmatch(r"\d+").fillna(False).astype(bool)
    out = t.where(~num, t.str.zfill(n)).astype(object)
    return out.where(s.notna(), np.nan)


def write_stats(update):
    PAPER.mkdir(parents=True, exist_ok=True)
    p = PAPER / "stats.json"
    stats = json.loads(p.read_text()) if p.exists() else {}
    stats.update(update)
    p.write_text(json.dumps(stats, indent=2, sort_keys=True, default=str))
