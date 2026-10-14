# How much are America's forests worth? Data and code

Scripts, derived data and figures behind Weiskittel, Daigneault and Woodall, an article for The Conversation US (2026) on crowded U.S. forests and the value GDP does not count, and the companion figure "Of farms, forests and fishing, only forests give back more than GDP counts."

Archived version: Zenodo, concept DOI [10.5281/zenodo.23122535](https://doi.org/10.5281/zenodo.23122535). Cite the concept DOI. Code and data are also at https://github.com/holoros/conversation-forest-value.

## What is here

The lead file, `figures/00_farms-forests-fishing_graphical_abstract.png`, is the current public figure (October 13, 2026), identical to `figures/2026-10-13_farms-forests-fishing-figure-case-public_FINAL.png`. It compares farms, forests and fishing in four panels: value per $1 of GDP in 2022 (GDP less depreciation, plus or minus each sector's own carbon at $120 per t CO2e with a $51 to $190 range, plus other nature costs and benefits, divided by GDP), with a diamond marking forests without the clean air credit (1.76 rather than 2.07); net carbon stored or released, 1990 to 2023; exports minus imports, 1981 to 2025, where wood shows a deficit in 43 of 45 years; and FY2024 federal formula research funds (McIntire-Stennis, Hatch, Sea Grant). `figures/2026-10-13_farms-forests-fishing-figure-hero-public_FINAL.png` is a two panel 16:9 version (value and research funds). Both are built by `code/2026-10-13_farms-forests-fishing-figure-public_plot.py` from `data/`, with icons from `code/icons/` (Material Design Icons, Apache License 2.0), and the script stops on any failed data or layout gate.

The article's own figure adds a fifth element, the share of U.S. forest by crowding with the modeled chance of damage. That panel comes from an analysis not yet peer reviewed, so its inputs, code and figure are withheld from this record and the GitHub repository until the paper is accepted.

The October 12 figure of record (`figures/2026-10-12_farms-forests-fishing-figure_FINAL.png`, built by `code/2026-10-12_farms-forests-fishing-figure_plot.py`) is kept. Its panel 2 extends each sector's 1990 to 2023 linear trend to 2040; these are not forecasts. Its panel 3 shows exports per dollar of imports, with a note on harvest leakage citing Daigneault, Sohngen, Belair and Ellis (2025, Environmental Research Letters 20:114022). The three panel variant drops the funding panel.

Earlier figures are kept for the record. `figures/2026-10-10_forest-gep-figure_DRAFT.png` (October 10) used the same four themes with illustrative 2070 sink paths and a seafood lost rent estimate, both since removed; built by `code/2026-10-10_forest-gep-figure_plot.py`. `figures/2026-10-04_three-gaps_DRAFT.png` and `figures/2026-10-04_sector-green-nva_DRAFT.png` (October 4) compared the sectors on gross, net, green net and full bases; built by `code/2026-10-04_sector-green-nva_plot.R`. `figures/00_forest-value_graphical_abstract.png` and `figures/2026-10-03_forest-value-stress-test_DRAFT.png` (October 3) summarized the forest value stress test; built by `code/graphical_abstract.R` and `code/2026-10-03_forest-value-stress-test_plot.R`.

`data/` holds every derived CSV, documented in `data_dictionary.csv`. The three raw BEA spreadsheets downloaded on September 30, 2026 (GDP by Industry value added, Fixed Assets depreciation, Marine Economy Satellite Account) are in the Zenodo record but not the GitHub repository; the FAOSTAT bulk file and third party reports are downloaded by the scripts or cited. `code/` holds R scripts (data.table, ggplot2, readxl) and Python scripts (pandas, matplotlib). Run order is in `RUN.md`.

## Caveats

The forest tally mixes welfare values (social cost of carbon, air quality damages avoided) with exchange values and is not comparable with Bhutan's gross ecosystem product or with GDP. Dashed carbon lines are linear trend extensions, not forecasts. Fishing fleet carbon is a rough estimate (see `data/seafood_hidden_cost_estimate.csv`). Dollar bases are mixed and not inflated (BEA 2022 current dollars, carbon prices in 2020 dollars, FAO in 2020 PPP dollars, Cavender-Bares in 2010 dollars). Ranges are scenario ranges, not statistical confidence intervals. Carbon is valued at social cost estimates that a 2025 executive order withdrew from federal use. No Forest Inventory and Analysis plot data, coordinates or proprietary inventories are used.

## Versions

1.0.0 (October 3, 2026): value added, trade ratio and research funding tables with the forest value stress test. 1.1.0 (October 10): the four panel public figure, the EPA sink, research fund and seafood hidden cost tables, and a third author. 1.2.0 (October 12): the farms, forests and fishing figure of record, EPA farm emissions and NOAA landings series, a recomputed `sector_green_nva_2022.csv`, and the Daigneault et al. (2025) leakage note. 1.3.0 (October 13): the public four panel figure (value per $1 of GDP with the clean air sensitivity, carbon, net wood trade, research funds) as the lead file, its two panel variant, the gated plotting script and its icons. The forest crowding panel used in the article is withheld pending peer review.

## License

Code and data: CC BY 4.0, matching the Zenodo record.

Contact: Aaron Weiskittel, University of Maine, Center for Research on Sustainable Forests (ORCID 0000-0003-2534-4478); Adam Daigneault, University of Maine (ORCID 0000-0002-9094-160X); Christopher W. Woodall, University of Maine and CTrees.

## Funding

Supported by the U.S. Department of Agriculture (PERSEUS) and the National Science Foundation E-RISE program (Maine-FOREST).
