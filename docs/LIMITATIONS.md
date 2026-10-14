# Limitations

*Plain-language note: the honest list of what this dataset cannot tell you. Read it before using the numbers. [VERIFY: author reads and agrees]*

1. **It only sees what was reported.** Records come from 30 CFR Part 50 reports filed by operators. Unreported events, and ground failures that hurt nobody and did not meet a reporting trigger, are missing. No-injury falls are reported far more often underground, so no-injury counts are not comparable between surface and underground.
2. **Selection relies on MSHA's category, which misses some events.** A record is a ground failure when MSHA classified it "fall of roof or back" or "fall of face/rib/pillar/side/highwall". Screening other categories found 226 surface metal/nonmetal narratives that look like ground failures filed elsewhere (for example under powered haulage). They are listed in `validation/supplement_candidates.csv` for author review and are **not** in v1.0 counts unless the authors accept them. Counts for surface mines are therefore likely undercounts.
3. **Surface metal/nonmetal numbers are small.** 92 records over 27 years. Yearly rates for surface mines swing on one or two events and should be read as multi-year averages, not trends.
4. **Mine attributes are current, not historical.** State, commodity, and name come from today's Mines file. A mine that changed commodity is grouped by its current one.
5. **Rates cover mine-operator employees only.** Contractor accidents are in the incident table but not in rates, because contractor hours are reported separately and not by mine subunit.
6. **Narratives are short and written by operators.** At most 384 characters, with abbreviations and typos. Failure mechanism is often not stated, which is why a "collapse, mechanism unstated" class exists. Labels describe what the narrative says, not an engineering investigation.
7. **Failure-mode labels are rule-based.** Agreement with expert hand labels is reported in `validation/agreement_report.txt` [VERIFY: fill after validation]. Rare modes (planar, wedge, toppling) rest on very few records.
8. **The source changes weekly.** MSHA replaces its files every Friday and can revise past records. v1.0 is fixed to the 2026-10-09 refresh; fingerprints are in `data/raw/PROVENANCE.txt`.
9. **2026 is partial** (records to late September 2026) and is excluded from yearly rates.
