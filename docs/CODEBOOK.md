# Codebook

*Plain-language note: every column in every output file, what it means, and where it comes from. Open this when a column name is unclear.*

Sources: A = MSHA Accidents, M = MSHA Mines, P = MSHA Employment/Production yearly, D = derived by GroundFall-US.

## groundfall_incidents.csv (one row per ground-failure accident record)

| Column | Source | Definition |
|---|---|---|
| document_no | A DOCUMENT_NO | MSHA accident form number; unique key |
| mine_id | A MINE_ID | 7-digit MSHA mine ID |
| mine_name, state, county, latitude, longitude | M | Current mine name and location from the Mines file (current values, not values at accident time) |
| accident_date | A ACCIDENT_DT | mm/dd/yyyy |
| year | A CAL_YR | Calendar year |
| sector | D from A COAL_METAL_IND | coal or metal_nonmetal |
| subunit_cd, subunit | A | Where in the mine: 01 underground, 02 surface at underground mine, 03 strip/quarry/open pit, 06 dredge, 12 other surface, 30 mill/plant, ... |
| mine_type | D from subunit_cd | underground (01); surface (02, 03, 04, 05, 06, 12); mill_plant (30); shop_yard (17); office (99). See config/selection.yaml |
| commodity | D from M PRIMARY_CANVASS_CD | coal (1, 2), sand_gravel (5), stone (6), nonmetal (7), metal (8) |
| primary_sic | M | Primary commodity description |
| msha_classification | A CLASSIFICATION | MSHA's circumstance category. Selection: "FALL OF ROOF OR BACK" or "FALL OF FACE/RIB/PILLAR/SIDE/HIGHWALL" |
| msha_accident_type, msha_immediate_notify | A | MSHA's accident type and immediate-notification category |
| degree_injury_cd, degree_injury | A | Severity code and label |
| severity | D | fatal (01); lost_time (02 to 04); other_reportable_injury (05, 06); no_injury_accident (00); other_or_unknown (07 to 10, ?) |
| is_fatal, is_injury, is_lost_time | D | True/False flags; is_injury = degree 01 to 06 |
| is_contractor, contractor_id | A CONTRACTOR_ID | True when a contractor was involved |
| occupation, activity, mining_equipment, ug_location | A | As reported |
| has_hours_same_year | D | True when P has hours > 0 for the same mine, subunit, and year |
| partial_year | D | True for 2026 (incomplete year) |
| narrative | A NARRATIVE | Operator's description, at most 384 characters, as published |

## groundfall_rates.csv (one row per year x sector x mine_type x commodity x state)

| Column | Definition |
|---|---|
| year, sector, mine_type, commodity, state | Grouping keys (state from M, else P) |
| hours | Sum of P ANNUAL_HOURS (mine-operator employees) |
| avg_employees | Sum of P AVG_EMPLOYEE_CNT |
| gf_records, gf_injury, gf_lost_time, gf_fatal, gf_no_injury | Ground-failure records in the cell, non-contractor only |
| all_records | All accident records in the cell (any classification), non-contractor |
| gf_injury_rate, gf_lost_time_rate, gf_fatal_rate, gf_records_rate | Count / hours x 200,000. Blank when hours = 0. **gf_injury_rate is the headline measure** |
| partial_year | True for 2026 |

## groundfall_failure_modes.csv (one row per surface metal/nonmetal ground-failure record)

Scope: sector metal_nonmetal and subunit 02, 03, 06, or 12.

| Column | Definition |
|---|---|
| document_no ... narrative | Copied from the incident table |
| failure_mode | First matching mode in rule precedence: wedge, planar, toppling, rotational_slide, raveling, rockfall, collapse_mechanism_unstated; else unspecified |
| failure_mode_evidence | The exact phrase that fired the label |
| trigger_blasting, trigger_water, trigger_scaling | True when the narrative (or MSHA activity, for scaling) mentions it; more than one can be true |
| trigger_*_evidence | Phrase that fired each trigger |
| any_trigger | True when any trigger is true |
| rules_version | Version of config/coding_rules.yaml used |
