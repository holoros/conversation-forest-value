# How much are America's forests worth? Data and code

Scripts, derived data and figures behind Weiskittel, Daigneault and Woodall, an article for The Conversation US (2026) on crowded U.S. forests and the value GDP does not count, and the companion figure "U.S. forests give back roughly twice what GDP counts, and wood not grown here is cut somewhere else."

Archived version: Zenodo, concept DOI [10.5281/zenodo.23122535](https://doi.org/10.5281/zenodo.23122535). Cite the DOI.

## What is here

- `figures/2026-10-10_forest-gep-figure_DRAFT.png` (and PDF): the current public figure, four panels for a general audience, with forests, farms and seafood in every panel. Undervalued: value added in 2022 stepped from GDP to after depreciation, carbon counted ($120 per t, range $51 to $190) and nature's other costs and benefits (clean air from all U.S. trees, national forest water and recreation for forests; FAO land, nitrogen and water damage for farms; a rough fleet carbon and lost rent estimate for seafood). Misunderstood: imports minus exports, 1981 to 2025 (UN Comtrade, nominal dollars), with the Wear and Murray (2004) leakage finding. At risk: the EPA forest carbon sink 1990 to 2023 with two illustrative paths to 2070, beside direct farm emissions (EPA 2022) and an estimated fishing fleet total. Underinvested: FY2024 federal formula research funds. Built by `code/2026-10-10_forest-gep-figure_plot.py` from five CSVs in `data/`.
- `figures/2026-10-04_three-gaps_DRAFT.png` (and PDF): the October 4 figure, kept for the record. Panel 1 compares the forest, agriculture and marine sectors (primary production plus first stage manufacturing) on four bases for 2022: gross value added (BEA), net of depreciation (BEA Fixed Assets), green net (each sector's own carbon at $51, $120 and $190 per t CO2e), and full (agriculture charged FAO SOFA 2023 land, nitrogen and water hidden costs; forest credited air quality from Cavender-Bares et al. 2022; forest water and habitat unpriced, so the forest value is a floor). Panel 2 is exports per dollar of imports, 1981 to 2025 (UN Comtrade SITC and HS). Panel 3 is FY2018 federal research formula funds.
- `data/`: every derived CSV, documented in `data_dictionary.csv`. Raw BEA spreadsheets, the FAOSTAT bulk file and third party reports are downloaded by the scripts or cited, not stored here.
- `code/`: R scripts (data.table, ggplot2, readxl) and one Python parser. Run order is in `RUN.md`.

## Caveats

The forest tally mixes welfare values (social cost of carbon, air quality damages avoided) with exchange values and is not comparable with Bhutan's gross ecosystem product or with GDP. The 2070 paths in the current figure are illustrations, not forecasts. Seafood hidden costs are rough estimates (see `data/seafood_hidden_cost_estimate.csv`). Dollar bases are mixed and not inflated (BEA 2022 current dollars, carbon prices in 2020 dollars, FAO in 2020 PPP dollars, Cavender-Bares in 2010 dollars). Shaded fans are scenario ranges, not statistical confidence intervals. No Forest Inventory and Analysis plot data, coordinates or proprietary inventories are used.

## License

Code and data: CC BY 4.0, matching the Zenodo record.

Contact: Aaron Weiskittel, University of Maine, Center for Research on Sustainable Forests (ORCID 0000-0003-2534-4478); Adam Daigneault, University of Maine (ORCID 0000-0002-9094-160X); Christopher W. Woodall, University of Maine and CTrees.

## Funding

Supported by the U.S. Department of Agriculture (PERSEUS) and the National Science Foundation E-RISE program (Maine-FOREST).
