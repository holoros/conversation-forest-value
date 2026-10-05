# Conversation GDP figures, October 3, 2026

Job folder on firebreather: ~/jobs/gdp_fig. R 4.5, data.table, ggplot2, patchwork, readxl, jsonlite. Font: Source Sans 3 (Adobe TTF in ~/.fonts, cairo devices).

Inputs (downloaded by the scripts or by hand on October 3, 2026):
- VA.xlsx: BEA GDP by Industry, Value Added (TVA105-A), https://apps.bea.gov/industry/Release/XLS/GDPxInd/ValueAdded.xlsx, published September 30, 2026
- MESA_VA.xlsx: BEA Marine Economy Satellite Account, value added by activity, https://www.bea.gov/sites/default/files/2025-06/mesa0625-VA-Activity.xlsx
- acfb2023.pdf: Arkansas Center for Forest Business, 2023 U.S. Forestry Economic Contribution by State (state value-added multipliers parsed to acfb2023_state_va_multipliers.csv)
- UN Comtrade public preview API (US reporter, world partner, HS 01 to 24, 44, 47, 48, 1604, 1605), fetched by the trade script

Run order:
1. Rscript 2026-10-03_gdp-farms-forest_data.R   -> bea_va_farms_forest_1997_2025.csv
2. Rscript 2026-10-03_us-trade-ratio_data.R     -> comtrade_us_raw_2014_2024.csv, us_trade_ratio_2014_2024.csv (rate limited; run detached)
3. Rscript 2026-10-03_gdp-trade-research_plot.R -> Figure 1 (PNG 300 dpi, PDF), forest_va_multiplier_range.csv, bea_mesa_living_resources_2014_2023.csv
4. Rscript 2026-10-03_forest-value-stress-test_plot.R -> stress test figure, stress_test_forest_contribution_2022.csv

No restricted, keyed or coordinate data. Not yet pushed to GitHub: needs Aaron's yes to copy the PAT to firebreather and a target repo.

## Update, October 5, 2026
5. Rscript out/2026-10-03_net-value-added_data.R -> bea_depreciation_by_industry_1925_2025.csv, bea_net_value_added_farms_forest_seafood.csv (needs detailnonres_dep1.xlsx from BEA Fixed Assets detail)
6. Rscript out/2026-10-04_sector-green-nva_plot.R -> sector_green_nva_2022.csv, 2026-10-04_sector-green-nva_DRAFT (single panel) and 2026-10-04_three-gaps_DRAFT (Figure 1, three panels)
Figure 1 bases: gross and net value added (BEA, 2022), green net (own carbon at $51/$120/$190 per t), full (agriculture less FAO SOFA 2023 land, nitrogen and water hidden costs, 2020 PPP; forest plus Cavender-Bares et al. 2022 air quality, 2010 USD). Forest water and habitat unpriced. The 2026-10-03 figures are superseded but kept.
7. Rscript out/2026-10-05_us-trade-ratio-1988-2013_data.R and out/2026-10-05_us-trade-ratio-sitc-1962-1991_data.R (rate limited, run detached), then out/2026-10-05_us-trade-ratio-combine.R -> us_trade_ratio_1981_2025.csv (SITC 1981 to 1990, HS 1991 to 2025). Figure 1 panel 2 and the graphical abstract use this series.
Zenodo draft 23122536 resynchronized October 5, 2026: 40 files, checksums verified, graphical abstract rebuilt on the four bases. Still unsubmitted.
8. Rscript out/2026-10-05_fao-forest-trade-1961_data.R (needs fao/Forestry_E_All_Data_(Normalized).csv from bulks-faostat.fao.org) and out/2026-10-05_costanza-crosscheck.R. Sea Grant bar set to FY2018 enacted ($76.5M).
