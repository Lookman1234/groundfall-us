# Start Here: GroundFall-US

*Read this first. It explains your project in plain language. Words in bold are explained in [GLOSSARY.md](GLOSSARY.md).*

## What you are building

A free, citable table of every reported ground-failure accident at U.S. mines from 2000 to 2026, with each accident labeled by how the ground failed and what set it off.

## Why it matters

Falls of rock, highwalls, and pit slopes kill and injure miners every year. Federal law (30 CFR 56.3130) requires surface mines to keep walls, banks, and slopes stable. Today the accident records sit in a large government file that is hard to use. Nobody has published one clean version that says where these failures happen, at which kinds of mines, and how the rock actually failed.

GroundFall-US fixes that. Regulators (MSHA), researchers (NIOSH), and mine operators can open one file and see, for example, how many highwall failures happened at Arizona copper pits, per hour worked, and whether blasting or water came first. That is the starting point for any early-warning system.

Think of it like a national crash database for roads, but for rock falls at mines.

## Where the information comes from

All sources are free and public from the Mine Safety and Health Administration (MSHA). Nothing here needs special permission.

| Source | In plain terms | What one row looks like | Link |
|---|---|---|---|
| Accidents | Every injury or reportable accident mines must report to MSHA, since 2000 | One accident: mine ID, date, what happened, how badly someone was hurt, and a short written description | https://arlweb.msha.gov/OpenGovernmentData/DataSets/Accidents.zip |
| Mines | The list of every U.S. mine MSHA has on file | One mine: ID, name, state, coal or metal/nonmetal, surface or underground, main commodity | https://arlweb.msha.gov/OpenGovernmentData/DataSets/Mines.zip |
| Employment and production (yearly) | How many people each mine employed and how many hours they worked each year | One mine in one year: employees, hours worked | https://arlweb.msha.gov/OpenGovernmentData/DataSets/MinesProdYearly.zip |

## What you will have at the end

- [ ] **A public project page** on GitHub with all the code, so anyone can rebuild the dataset: https://github.com/Lookman1234/groundfall-us
- [ ] **A permanent citation number (DOI)** from Zenodo for GroundFall-US v1.0: minted when the v1.0 GitHub release is archived by Zenodo
- [ ] **The dataset itself**: one table of ground-failure accidents, one table of rates by mine type, commodity, and state, and the failure-mode labels for surface metal and nonmetal accidents
- [ ] **A codebook and coding manual** that explain every column and every labeling rule, authored by you

## How it connects to your work

This puts your geotechnical judgment into a national public record. The failure-mode rules (rockfall, raveling, planar, wedge, toppling, rotational slide, and the blasting, water, and scaling triggers) are yours; the dataset is the evidence base for slope monitoring and early warning.

## What you need to do

| Your task | When | Time |
|---|---|---|
| Create accounts (ORCID, GitHub, Zenodo) | Before publishing | 15 min |
| Download three files from MSHA and attach them here | Now | 10 min |
| Answer five setup questions | Now | 10 min |
| Review and correct the failure-mode labeling rules | After the first data run | 2 to 3 hours |
| Hand-label a random sample of accidents to check the rules | After the rules | 3 to 5 hours |
| Check the results using the checklist | When the draft is ready | 1 to 2 hours |
| Approve publishing | After checking | 5 min |

Everything else is built for you.

## The steps ahead

1. **Data collected.** The three MSHA files are saved with a record of exactly where and when each came from.
2. **Data cleaned and combined.** Accidents are joined to mines and to hours worked, and ground failures are picked out.
3. **Quality checks.** Counts, match rates, and five accidents you can look up by hand.
4. **Rates and first figures.** Ground-failure rates by mine type, commodity, and state.
5. **Failure-mode labels.** Your rules applied to surface metal and nonmetal narratives, then checked against your hand labels.
6. **Ready for your check.** You verify, then we publish v1.0 to GitHub and Zenodo.

*You are here: v1.0 approved by the authors on 2026-10-13 and released on GitHub; Zenodo DOI next.*
