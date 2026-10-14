# Your verification checklist

*Before GroundFall-US goes public under your name, you check it. Total: about 1.5 to 2 hours, plus the rule work in Part 4. Tick each box and add the date. The publish gate script checks the mechanical items; these are yours.*

**How to check an accident record by hand:** go to MSHA's Mine Data Retrieval System, https://www.msha.gov/data-and-reporting/mine-data-retrieval-system , type the **mine ID**, open **Accidents**, and find the date. The description should match the `narrative` column.

## Part 1: Results can be rebuilt (15 to 30 min)

- [ ] Ask Claude in a new chat to re-run the pipeline from the repository and compare with these headline numbers: 29,851 ground-failure records; 9,465 injuries; 162 deaths; mine match 100.0%; hours match 99.65%. (Or run the commands in the README yourself.)
- [ ] Every number in `docs/SUMMARY.md` matches `paper/stats.json` (it is generated from it).

## Part 2: Sources (10 min)

- [ ] https://arlweb.msha.gov/OpenGovernmentData/OGIMSHA.asp still loads and lists Accidents, Mines, and Employment/Production (yearly).
- [ ] MSHA data are U.S. government work, public domain: reuse allowed.

## Part 3: Check records by hand (30 to 45 min)

File: `data/processed/groundfall_incidents.csv`. Look up each by mine ID as above.

**Arizona records you can judge first-hand:**
- [ ] doc 220152260028, mine 0201049 Pinto Valley Mine, 08/13/2015, open pit. ___
- [ ] doc 220191890023, mine 0200135 Mission/San Xavier/Eisenhower, 07/06/2019, open pit. ___
- [ ] doc 220261540020, mine 0203305 Pinyon Plain Mine, 05/15/2026, underground. ___

**Extremes (most likely to be errors):**
- [ ] earliest: doc 220000240052, mine 1507475 (KY), 01/01/2000, roof fall, accident only. ___
- [ ] most recent: doc 220262720011, mine 4608759 North Eagle Mine (WV), 09/23/2026. ___
- [ ] highest rate cell: `groundfall_rates.csv`, 2008, metal_nonmetal, underground, metal, NY: 7 injuries in 216,947 hours (6.45 per 200,000). Plausible for one small mine? ___
- [ ] surface fatality: doc 220233200007, mine 0900143 Wrens Plant (GA), 11/13/2023, highwall collapse. ___

**Random rows (seed 20261013):**
- [ ] doc 220012540136, mine 3600958 Mine 84 (PA), 08/26/2001. ___
- [ ] doc 220162310026, mine 4601816 Pinnacle Mine (WV), 07/25/2016. ___
- [ ] doc 220120310001, mine 4604236 Maple Eagle No. 1 (WV), 05/03/2011. ___

## Part 4: Your decisions and your rules (the main work)

- [ ] **Headline rate.** Injury rate (nobody-hurt falls reported separately), or all reportable falls? Recommended: injury rate. Your choice: ___
- [ ] **Contractors.** Keep them out of rates (in the incident table only)? Recommended: yes. ___
- [ ] **Missed ground failures.** Review `validation/supplement_candidates.csv` (226 rows, about 1.5 h). Mark each `accept` or `reject`. Then decide: add accepted rows to v1.0 as a flagged supplement, or list them only? Recommended: add, flagged. ___
- [ ] **Rules.** Rewrite `config/coding_rules.yaml` in your own judgment. Decide whether to keep the `collapse_mechanism_unstated` class. Answer the open question at the top of the file. ___
- [ ] **Hand labels.** Fill in `validation/validation_sheet.csv` (92 narratives, rule labels hidden): your failure mode and Y for each trigger. Then Claude runs `06_agreement.py` and the agreement numbers go into LIMITATIONS. ___
- [ ] **Kayode Komolafe.** ORCID and role added to `AUTHORS.json`. ___

## Part 5: Before it goes public (15 to 30 min)

- [ ] README summary rewritten in your own words.
- [ ] `docs/LIMITATIONS.md` read and agreed.
- [ ] Figures regenerated with `--final`; `publish_gate.py` passes.
- [ ] Release day: publication logged in the evidence log.

**When every box is ticked, tell Claude in your own words that you have checked the package and approve publishing.**
