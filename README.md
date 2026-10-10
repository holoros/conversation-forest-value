# How much are America's forests worth? Data and code

Scripts, derived data and figures behind Weiskittel, Daigneault and Woodall, an article for The Conversation US (2026) on crowded U.S. forests and the value GDP does not count, and the companion figure "U.S. forests give back roughly twice what GDP counts, and wood not grown here is cut somewhere else."

Archived version: Zenodo, concept DOI [10.5281/zenodo.23122535](https://doi.org/10.5281/zenodo.23122535). Cite the DOI.

## What is here

- `figures/2026-10-10_forest-gep-figure_DRAFT.png` (and PDF): the current companion figure, three panels in a New York Times editorial style. Panel 1 (undervalued) is a forest ecosystem account for 2022: wood and paper value added less depreciation ($115B), plus carbon taken up (772 million t at $51 to $190 per t, central $120), clean air from all U.S. trees (Cavender-Bares et al. 2022), national forest water (Sedell et al. 2000, inflated) and national forest recreation (USDA Forest Service), $271B with a range of $206B to $336B; agriculture net value added charged its own emissions and FAO SOFA 2023 land, nitrogen and water damage; and seafood (BEA MESA) with its import share. Panel 2 (misunderstood) is the EPA forest carbon sink, 1990 to 2023, with illustrative paths to 2070 built from published end points (Maine mixed management gain from Daigneault et al. 2024, the 1990 to 2023 trend, and the 2020 RPA net source scenario) and the leakage finding of Wear and Murray (2004). Panel 3 (underinvested) is FY2024 federal research capacity funds. Built by `code/2026-10-10_forest-gep-figure_plot.py` (Python, matplotlib) from `data/sector_green_nva_2022.csv`, `data/us_trade_ratio_1981_2025.csv`, `data/epa_forest_sink_1990_2023.csv` and `data/research_capacity_funds_fy2024.csv`; the build reproduces the committed PNG byte for byte.
- `figures/2026-10-04_three-gaps_DRAFT.png` (and PDF): the October 4 figure, kept for the record. Panel 1 compares the forest, agriculture and marine sectors (primary production plus first stage manufacturing) on four bases for 2022: gross value added (BEA), net of depreciation (BEA Fixed Assets), green net (each sector's own carbon at $51, $120 and $190 per t CO2e), and full (agriculture charged FAO SOFA 2023 land, nitrogen and water hidden costs; forest credited air quality from Cavender-Bares et al. 2022; forest water and habitat unpriced, so the forest value is a floor). Panel 2 is exports per dollar of imports, 1981 to 2025 (UN Comtrade SITC and HS). Panel 3 is FY2018 federal research formula funds.
- `data/`: every derived CSV, documented in `data_dictionary.csv`. Raw BEA spreadsheets, the FAOSTAT bulk file and third party reports are downloaded by the scripts or cited, not stored here.
- `code/`: R scripts (data.table, ggplot2, readxl) and one Python parser. Run order is in `RUN.md`.

## Caveats

The forest tally mixes welfare values (social cost of carbon, air quality damages avoided) with exchange values and is not comparable with Bhutan's gross ecosystem product or with GDP. The 2070 paths in the current figure are illustrations, not forecasts. Dollar bases are mixed and not inflated (BEA 2022 current dollars, carbon prices in 2020 dollars, FAO in 2020 PPP dollars, Cavender-Bares in 2010 dollars). Shaded fans are scenario ranges, not statistical confidence intervals. No Forest Inventory and Analysis plot data, coordinates or proprietary inventories are used.

## License

Code and data: CC BY 4.0, matching the Zenodo record.

Contact: Aaron Weiskittel, University of Maine, Center for Research on Sustainable Forests (ORCID 0000-0003-2534-4478); Adam Daigneault, University of Maine (ORCID 0000-0002-9094-160X); Christopher W. Woodall, University of Maine and CTrees.

## Funding

Supported by the U.S. Department of Agriculture (PERSEUS) and the National Science Foundation E-RISE program (Maine-FOREST).
