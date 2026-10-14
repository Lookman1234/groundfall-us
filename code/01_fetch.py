#!/usr/bin/env python3
"""Step 1: collect the three MSHA source files and record where they came from.

Plain-language note: this script downloads MSHA's Accidents, Mines, and yearly
hours-worked files (or copies them from a folder you downloaded them to), saves them
in data/raw/, and writes one line per file to data/raw/PROVENANCE.txt with its size,
fingerprint (SHA-256), source link, and date. You do not need to open this file.

Usage:
  python code/01_fetch.py                    # download from MSHA
  python code/01_fetch.py --from-dir ~/Downloads   # use files you downloaded yourself
"""

import argparse
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
BASE = "https://arlweb.msha.gov/OpenGovernmentData/DataSets/"
INDEX = "https://arlweb.msha.gov/OpenGovernmentData/OGIMSHA.asp"

SOURCES = {
    "Accidents.zip": "Accidents_Definition_File.txt",
    "Mines.zip": "Mines_Definition_File.txt",
    "MinesProdYearly.zip": "MineSProdYearly_Definition_File.txt",
}


def log(path, url, note):
    subprocess.run([sys.executable, str(ROOT / "code" / "provenance.py"), str(path), url,
                    "--log", str(RAW / "PROVENANCE.txt"), "--note", note], check=True)


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "GroundFall-US/1.0 (research dataset)"})
    with urllib.request.urlopen(req, timeout=300) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-dir", help="folder holding the .zip files you downloaded yourself")
    a = ap.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)

    for zname, defname in SOURCES.items():
        dest = RAW / zname
        url = BASE + zname
        if a.from_dir:
            src = Path(a.from_dir).expanduser() / zname
            if not src.exists():
                sys.exit(f"Missing {src}. Download it from {url}")
            shutil.copy2(src, dest)
            note = f"downloaded manually by author from {INDEX}, copied from local folder"
        else:
            print(f"Downloading {url}")
            download(url, dest)
            note = f"downloaded by 01_fetch.py; listed on {INDEX}"
        log(dest, url, note)

        with zipfile.ZipFile(dest) as z:
            members = [m for m in z.namelist() if not m.endswith("/")]
            z.extractall(RAW)
        print(f"  {zname}: extracted {', '.join(members)}")

        # Field definition files are small; fetch if reachable, else note it.
        try:
            download(BASE + defname, RAW / defname)
            log(RAW / defname, BASE + defname, "MSHA field definition file")
        except Exception as e:  # noqa: BLE001
            print(f"  could not fetch {defname} ({e}); definitions are summarized in docs/CODEBOOK.md")

    print("Done. See data/raw/PROVENANCE.txt")


if __name__ == "__main__":
    main()
