# Build spec: GroundFall-US v1.0

*Plain-language note: this is the one-page plan the whole build follows. You do not need to edit it; the plain version of each line was sent to you in chat. If the project changes, this file changes first.*

```
PROJECT:        GroundFall-US. Archetype: open dataset (1), with a rule-based
                text-coding layer. Optional second archetype: data descriptor paper.
QUESTION:       Where, at which kinds of U.S. mines, and how do ground failures
                that injure miners happen, 2000 to 2026?
SOURCES:        MSHA Open Government Data, public domain (U.S. government work),
                refreshed weekly; vintage = download date recorded in PROVENANCE.txt.
                - Accidents.zip  + Accidents_Definition_File.txt
                - Mines.zip      + Mines_Definition_File.txt
                - MinesProdYearly.zip + MineSProdYearly_Definition_File.txt
                Index: https://arlweb.msha.gov/OpenGovernmentData/OGIMSHA.asp
UNIT:           Incident table: one row per MSHA accident record (DOCUMENT_NO).
                Rate table: one row per group (mine type x commodity x state x year).
                Coding table: one row per surface metal/nonmetal ground-failure record.
SELECTION:      Ground failure = CLASSIFICATION in {fall of roof or back; fall of
                face, rib, pillar, side, highwall} [VERIFY exact labels against data],
                CAL_YR 2000 to 2026 (2026 partial, flagged).
MEASURES:       Incidents, fatalities (DEGREE_INJURY_CD 01), lost-time cases (03, 04),
                hours worked (mine-operator employees, MinesProdYearly), rate per
                200,000 hours = incidents / hours x 200,000. Rates use operator-employee
                incidents only, so numerator and denominator match.
CODING LAYER:   Surface MNM only (COAL_METAL_IND = M, surface subunits). Failure mode:
                rockfall, raveling, planar, wedge, toppling, rotational slide,
                unspecified. Trigger: blasting, water, scaling, none stated (multi-label).
                Keyword and phrase rules in config/coding_rules.yaml, authored by
                Lukman. Validation: author hand-codes a stratified random sample;
                report agreement (percent and Cohen's kappa) per category.
OUTPUTS:        data/processed/groundfall_incidents.csv
                data/processed/groundfall_rates.csv
                data/processed/groundfall_failure_modes.csv
                data/processed/qa_report.txt, paper/stats.json, paper/figures/*.png
                docs/CODEBOOK.md, docs/CODING_MANUAL.md, docs/LIMITATIONS.md
VENUES:         1) GitHub release v1.0  2) Zenodo dataset DOI (Nov 2026)
                3) data descriptor paper deferred to after v1.0
VERIFY POINTS:  ground-failure selection rule; rate denominator; contractor handling;
                every coding rule; hand-coded validation sample; five spot-check
                records; README summary in author's own words.
LICENSE:        Code MIT; derived data and docs CC BY 4.0, crediting MSHA.
DECISIONS:      2026-10-11 author accepted all five defaults: both MSHA fall
                classifications; rates per 200,000 operator hours, contractors
                excluded from rates; Claude drafts rules, author rewrites and
                hand-labels ~300; code MIT, data CC BY 4.0; Zenodo dataset only
                for v1.0 (data paper deferred, can follow).
```
