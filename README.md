# GroundFall-US

**Status: DRAFT v0.9, not yet verified by the authors. Do not cite yet.** Target release: v1.0 on Zenodo, November 2026.

GroundFall-US is an open dataset of ground-failure accidents at U.S. mines from 2000 to 2026. It brings together three public files from the Mine Safety and Health Administration (MSHA): accident reports, the list of mines, and hours worked each year. The result is one documented set of tables. It shows how many falls of roof, rib, face, highwall, and slope happened, at which kinds of mines and in which states, and the rate per hour worked. For surface metal and nonmetal mines, it also labels how the ground failed (rockfall, raveling, planar, wedge, toppling, rotational slide) and what set it off (blasting, water, scaling), using rules written by a geotechnical engineer. Wall, bank, and slope stability at these mines is regulated under 30 CFR 56.3130. The dataset is meant as a national reference for MSHA, NIOSH, and mine operators, and as an evidence base for early warning.

[VERIFY: author rewrites this paragraph in his own words before release]

Headline numbers: see [docs/SUMMARY.md](docs/SUMMARY.md), which is generated from the data.

## Outputs

| File | One row is | Rows |
|---|---|---|
| `data/processed/groundfall_incidents.csv` | one MSHA accident record classified as a ground failure | see SUMMARY |
| `data/processed/groundfall_rates.csv` | one year x sector x mine type x commodity x state, with counts, hours, and rates | |
| `data/processed/groundfall_failure_modes.csv` | one surface metal/nonmetal ground-failure narrative, with failure mode, triggers, and the phrase that fired each label | |
| `data/processed/qa_report.txt` | quality checks: row counts, match rates, spot checks | |

Every column is defined in [docs/CODEBOOK.md](docs/CODEBOOK.md). The labeling rules are in [config/coding_rules.yaml](config/coding_rules.yaml). Known limits are in [docs/LIMITATIONS.md](docs/LIMITATIONS.md).

## How to rebuild it

Needs Python 3.10 or later.

```
pip install -r requirements.txt
python code/01_fetch.py            # downloads the three MSHA files (or: --from-dir FOLDER)
python code/02_build.py            # selects ground failures, joins mines and hours, computes rates
python code/03_qa.py               # writes data/processed/qa_report.txt
python code/04_coding.py           # applies the failure-mode rules
python code/04b_candidates.py      # lists likely ground failures MSHA filed under other categories
python code/05_validation_sample.py
python code/07_figures.py          # add --final after verification
python code/08_summary.py
```

MSHA replaces its files every Friday. To reproduce v1.0 exactly, use the files whose SHA-256 fingerprints are in `data/raw/PROVENANCE.txt`; they are archived with the Zenodo release.

## Sources

All from MSHA Open Government Data, https://arlweb.msha.gov/OpenGovernmentData/OGIMSHA.asp, U.S. government work, public domain. Edition used: the 2026-10-09 weekly refresh.

- Accident Injuries (`Accidents.zip`), 30 CFR Part 50 reports
- Mines (`Mines.zip`)
- Employment/Production, yearly (`MinesProdYearly.zip`)

## License

Code: MIT. Data and documentation: CC BY 4.0. Please credit GroundFall-US and MSHA. See [LICENSE](LICENSE).

## Authors

Lukman Alabede (ORCID 0009-0008-7769-7455), Independent Researcher, Safford, Arizona: concept, failure-mode rules, validation.
Kayode Komolafe, Colorado School of Mines, Golden, Colorado: [VERIFY role].

Code for fetching and joining the data was written with AI assistance (Claude, Anthropic). The authors made every analytic decision and verified the outputs. See [CITATION.cff](CITATION.cff).
