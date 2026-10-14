# Build log

*Plain-language note: a dated record of what was run, what was found, and what changed. You can skim it; items marked (resolved) were author decisions, settled for v1.0.*

## 2026-10-13: re-check with real MSHA files

**Source files on hand**
- Mines.zip (2026-10-09 MSHA refresh): 92,060 mines, no duplicate IDs. Logged in data/raw/PROVENANCE.txt.
- MinesProdYearly.zip (2026-10-09 refresh): 658,922 mine-subunit-year rows, 2000 to 2026. Logged.
- Accidents.zip: **not yet received.** The workspace cannot reach msha.gov; the 52 MB file timed out over the computer link four times. The only accident data on hand is an interrupted extraction (11,271 of several hundred thousand rows, cut mid-record). It was used for testing only and is not part of the dataset.

**Real-data test (first 11,271 accident records, sorted by mine ID, mostly AL and AK)**
- Mine join: 100.0% of ground-failure records matched the Mines file.
- Hours join: 99.5% matched an hours record for the same mine, subunit, and year.
- MSHA's actual labels are `FALL OF FACE/RIB/PILLAR/SIDE/HIGHWALL` and `FALL OF ROOF OR BACK`; the selection rule matches both.
- `FALLING/SLIDING/ROLLING MATERIALS` was read in full: it covers rocks off screens, tools, and equipment, not ground. Correctly excluded.
- 792 of 1,194 test ground-failure records were degree 00 "accident only": a reportable fall where nobody was hurt, almost all underground.
- Rates printed in this test are not meaningful (partial accident file against full hours file).

**Changes made**
1. New `severity` column (fatal, lost_time, other_reportable_injury, no_injury_accident, other_or_unknown) and `gf_no_injury` / `gf_lost_time_rate` in the rate table. The headline rate is now the **injury rate** (degrees 01 to 06 per 200,000 hours); no-injury falls are reported separately so they cannot inflate rates. (resolved: confirmed by the authors)
2. Bug fix: MSHA's "?" (no value) code was being padded to "0?". Codes now stay as published.
3. MSHA's served hours file uses different column names from its definition sheet (CALENDAR_YR, ANNUAL_HRS, C_M_IND, ...); the reader maps them.
4. Coding rules: one real narrative ("an upper section of the 50 feet pit wall fell") was labeled unspecified. (resolved: left as unspecified in v1.0)

**Pipeline status:** all six scripts run cleanly on both the synthetic test set and the real partial records.

## 2026-10-13 (later): full build on real data

- All three MSHA files re-downloaded fresh on the author's linked computer (Last-Modified 2026-10-09). Accidents.zip passed a zip integrity test; Mines and hours files byte-identical to the copies from 2026-10-11. Fingerprints in data/raw/PROVENANCE.txt.
- 275,220 accident records 2000 to 2026; 29,851 ground failures; 100.0% matched to mines, 99.65% to hours. QA flags: none. Four high-rate cells are small underground metal mines (200k to 700k hours); plausible.
- Coding rules revised to v0.2-draft after reading real narratives: broader rockfall phrasing; "wall/bank collapsed" no longer labelled rotational slide; new class `collapse_mechanism_unstated` (resolved: kept in v1.0). Unspecified fell from 39 to 16 of 92.
- New finding: MSHA's classification misses some surface ground failures (filed as powered haulage, machinery, etc.). New script 04b_candidates.py lists 226 candidates for author review. Not added to counts.
- Figures 1 and 2 drawn (review stamp). docs/SUMMARY.md generated from stats.json. README, CODEBOOK, LIMITATIONS, VERIFY_CHECKLIST, CITATION.cff written.

## 2026-10-13: v1.0 release

- The authors reported the data reviewed and approved, and asked for the final version to be published.
- Coding rules set to version 1.0 (identical patterns to 0.2). Selection, injury-rate headline, contractor handling, and the `collapse_mechanism_unstated` class confirmed.
- Not in v1.0, stated in LIMITATIONS: a formal agreement statistic against blind hand labels, and review of the 226 supplement candidates. Both are planned for a later version.
- Figures and SUMMARY regenerated with --final. MSHA source files (2026-10-09 edition) added to data/raw/ so v1.0 can be rebuilt exactly.
