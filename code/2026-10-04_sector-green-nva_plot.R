# Figure 1 (v12): apple to apple sector accounts, gross, net and green net value added, United States 2022.
# Run in ~/jobs/gdp_fig on firebreather after 2026-10-03_gdp-farms-forest_data.R and 2026-10-03_net-value-added_data.R.
# Inputs: out/bea_net_value_added_farms_forest_seafood.csv (forest, farms, seafood), VA.xlsx (food manufacturing),
#         detailnonres_dep1.xlsx (3110, 3120 depreciation), MESA_VA.xlsx (marine living resources total).
suppressMessages({library(data.table); library(ggplot2); library(readxl)})
set.seed(20261004)
update_geom_defaults("text", list(family = "Source Sans 3"))
wl <- list(poi = "#134a31", context = "#8a948e", sea = "#0072b2", ink = "#14201a", muted = "#4a5750", faint = "#5f6b65", rule = "#d3dcd6")
scc <- c(lo = 51, mid = 120, hi = 190)                      # $ per t CO2e, 2020 dollars
usd <- function(x) paste0("$", round(x), "B")

nva <- fread("out/bea_net_value_added_farms_forest_seafood.csv")[year == 2022]
raw <- as.data.table(suppressMessages(read_excel("VA.xlsx", sheet = "TVA105-A", col_names = FALSE)))
hr <- which(raw[[1]] == "Line")[1]; yrs <- as.character(unlist(raw[hr, ])); d <- raw[(hr + 1):.N]
setnames(d, c("line", "desc", yrs[-(1:2)])); d[, desc := trimws(desc)]
food_va <- as.numeric(d[desc == "Food and beverage and tobacco products", get("2022")][1]) / 1e3
dep <- fread("out/bea_depreciation_by_industry_1925_2025.csv")[year == 2022]
food_dep <- (dep$`3110` + dep$`3120`) / 1e3
m <- as.data.table(suppressMessages(read_excel("MESA_VA.xlsx", sheet = "VA", col_names = FALSE)))
my <- as.integer(unlist(m[3, -(1:2)])); row <- function(l) as.numeric(unlist(m[trimws(m[[2]]) == l][1, -(1:2)]))
mar_gva <- row("Living resources, marine")[my == 2022] / 1e3
harv <- row("Commercial harvest and seafood markets")[my == 2022] / 1e3
other <- mar_gva - harv
r_fish <- dep$`113F` / as.numeric(d[desc == "Forestry, fishing, and related activities", get("2022")][1])
r_food <- food_dep / food_va
ag_ghg <- -0.094 * 6343                                      # MMT, direct agriculture emissions 2022 (EPA agriculture sector page)
for_ghg <- 771.7                                             # MMT, forest land remaining forest land net removal (EPA GHGI 2024)

sec <- data.table(
  sector = c("Agriculture", "Forest", "Marine"),
  gva = c(nva[sector == "Farms", gva] / 1e3 + food_va, nva[sector == "Forest products", gva] / 1e3, mar_gva),
  dep = c(nva[sector == "Farms", dep] / 1e3 + food_dep, nva[sector == "Forest products", dep] / 1e3, harv * r_fish + other * r_food),
  ghg = c(ag_ghg, for_ghg, 0))
sec[, nva := gva - dep]
for (k in names(scc)) sec[, paste0("green_", k) := nva + ghg * scc[[k]] / 1e3]
# Full step (October 5, 2026). Agriculture: FAO SOFA 2023 US environmental hidden costs of agrifood systems, 2020, million 2020 PPP dollars,
# land 114,931 + nitrogen 62,215 + blue water 6,018 (climate 53,142 omitted, already charged in the carbon step), uncertainty -57% / +100%.
# Forest: air quality regulation by US trees, 37% of $114B (85 to 137, 2010 USD), Cavender-Bares et al. 2022 PLOS Sustain. Transform. 1(4): e0000010.
# Forest water and habitat remain unpriced (floor). Marine: no national non-market total found.
sec[, full_adj_mid := fcase(sector == "Agriculture", -(114.931 + 62.215 + 6.018), sector == "Forest", 0.37 * 114, default = 0)]
sec[, full_adj_lo := fcase(sector == "Agriculture", full_adj_mid * 2.00, sector == "Forest", 0.37 * 85, default = 0)]
sec[, full_adj_hi := fcase(sector == "Agriculture", full_adj_mid * 0.43, sector == "Forest", 0.37 * 137, default = 0)]
sec[, `:=`(full_mid = green_mid + full_adj_mid, full_lo = pmin(green_lo, green_hi) + full_adj_lo, full_hi = pmax(green_lo, green_hi) + full_adj_hi)]
stopifnot(all(sec$gva > 0), sec[sector == "Agriculture", gva] < 700, sec[sector == "Forest", gva] < 200)   # F5 magnitude bounds
fwrite(sec, "out/sector_green_nva_2022.csv")
long <- melt(sec[, .(sector, `Gross value added\n(what GDP counts)` = gva, `Net value added\n(after depreciation)` = nva,
                     `Green net value added\n(after own carbon flux)` = green_mid)], id.vars = "sector", variable.name = "step", value.name = "bn")
long[, x := as.integer(step)]
cols <- c(Agriculture = wl$context, Forest = wl$poi, Marine = wl$sea)
rng <- sec[, .(sector, x = 3, lo = pmin(green_lo, green_hi), hi = pmax(green_lo, green_hi), mid = green_mid)]
ratio <- sec[sector == "Forest", .(green_lo, green_mid, green_hi)] / sec[sector == "Agriculture", .(green_lo, green_mid, green_hi)]

p <- ggplot(long, aes(x, bn, colour = sector)) +
  geom_linerange(data = rng[hi - lo > 1], aes(x = x, ymin = lo, ymax = hi, colour = sector), inherit.aes = FALSE, linewidth = 9, alpha = 0.25) +
  geom_line(linewidth = 1.6) + geom_point(size = 3.6) +
  geom_text(data = long[x < 3], aes(label = usd(bn)), vjust = -1.1, size = 4.3, fontface = "bold") +
  geom_text(data = sec[abs(ghg) > 1], aes(x = 2.5, y = (nva + green_mid) / 2 + ifelse(ghg > 0, 18, -26), colour = sector,
            label = paste0(ifelse(ghg > 0, "+", "\u2212"), usd(abs(ghg * scc["mid"] / 1e3)), ifelse(ghg > 0, " carbon removed", " own emissions"))),
            inherit.aes = FALSE, size = 3.9, fontface = "bold.italic") +
  geom_text(data = rng[sector == "Marine"], aes(x = 3.07, y = mid, label = paste0(sector, "  ", usd(mid))), hjust = 0, size = 5, fontface = "bold") +
  geom_text(data = rng[sector != "Marine"], aes(x = 3, y = ifelse(sector == "Agriculture", hi + 34, lo - 34), label = usd(mid)), size = 4.3, fontface = "bold") +
  geom_text(data = rng[hi - lo > 1], aes(x = 3.07, y = hi, label = usd(hi)), hjust = 0, size = 3.8, fontface = "bold") +
  geom_text(data = rng[hi - lo > 1], aes(x = 3.07, y = lo, label = usd(lo)), hjust = 0, size = 3.8, fontface = "bold") +
  scale_colour_manual(values = cols, guide = "none") +
  scale_x_continuous(breaks = 1:3, labels = levels(long$step), expand = expansion(add = c(0.3, 0.75))) +
  scale_y_continuous(labels = usd, limits = c(0, 600), breaks = seq(0, 600, 100), expand = expansion(mult = c(0, 0.02))) +
  labs(x = NULL, y = NULL,
       title = sprintf("On the books the forest sector is a quarter the size of agriculture.\nCount each sector's own carbon and it is about half (%d%% to %d%%)",
                       round(100 * min(ratio)), round(100 * max(ratio))),
       subtitle = "United States, 2022, $B. Each sector is primary production plus first stage manufacturing.\nDots are central values at $120 per t CO₂e, bars span $51 to $190 per t.",
       caption = paste0("Forest sector: wood and paper manufacturing (BEA 3210, 3220). Agriculture sector: farms plus food, beverage and tobacco manufacturing (BEA 110C, 3110, 3120). Marine sector: BEA marine living resources (harvest, markets,\n",
                        "processing, marine pharmaceuticals, fish based feeds). Forestry and logging and agricultural support services are excluded from both land sectors because BEA reports them in one combined line (113F). Net value added\n",
                        "subtracts BEA current-cost depreciation of private nonresidential fixed assets by detailed industry (September 30, 2026), which BEA rates below its published aggregates in quality; subsidies are already netted out of\n",
                        "value added. Marine depreciation is a proxy at the 113F and food manufacturing ratios. Carbon: forest land remaining forest land, net removal of 771.7 MMT CO₂e (EPA GHGI 2024); direct agriculture emissions 596 MMT\n",
                        "(9.4% of 6,343 MMT, EPA, 2022); priced at $51 (IWG 2021, 3%), $120 and $190 per t (EPA 2023, 2.5% and 2%), 2020 dollars; no federal value has been in force since January 2025. Not netted for any sector: mill, food plant\n",
                        "and fishing fleet emissions, nutrient and water damages, and non-market benefits other than carbon (water, recreation). Scenarios on a common basis, not a national account. Chart: Weiskittel and Daigneault, University of Maine.")) +
  theme_minimal(base_size = 14, base_family = "Source Sans 3") +
  theme(panel.grid.minor = element_blank(), panel.grid.major.x = element_blank(), panel.grid.major.y = element_line(colour = wl$rule, linewidth = 0.3),
        axis.text.x = element_text(face = "bold", colour = wl$ink, size = 13), axis.text.y = element_text(colour = wl$muted, size = 12),
        plot.title = element_text(face = "bold", size = 19, colour = wl$ink, lineheight = 1.05), plot.subtitle = element_text(colour = wl$poi, face = "bold", size = 12.5, margin = margin(b = 10)),
        plot.caption = element_text(colour = wl$faint, size = 8.6, hjust = 0, lineheight = 1.15), plot.title.position = "plot", plot.caption.position = "plot",
        plot.background = element_rect(fill = "white", colour = NA), plot.margin = margin(14, 18, 10, 14))
ggsave("out/2026-10-04_sector-green-nva_DRAFT.png", p, width = 36, height = 21, units = "cm", dpi = 300, bg = "white")
ggsave("out/2026-10-04_sector-green-nva_DRAFT.pdf", p, width = 36, height = 21, units = "cm", bg = "white", device = cairo_pdf)
ggsave("out/thumb4.png", p, width = 36, height = 21, units = "cm", dpi = 60, bg = "white")
print(sec); print(round(100 * ratio))

# ---- Three panel version (October 4, 2026): undervalued, misunderstood, underinvested ----
# Mirrors 2026-10-04_three-gaps_plot.py. Panel 2 uses the full 2017 to 2025 series from out/us_trade_ratio_2014_2024.csv.
suppressMessages(library(patchwork))
ag <- sec[sector == "Agriculture"]; fo <- sec[sector == "Forest"]; land <- sec[sector != "Marine"]
fan <- rbindlist(lapply(split(land, land$sector), function(d) data.table(sector = d$sector, x = c(3, 4, 4), y = c(d$green_mid, d$full_lo, d$full_hi))))
p1 <- p + labs(title = "1. Undervalued", subtitle = "Value added to US GDP, 2022, $B, by accounting basis", caption = NULL) +
  geom_polygon(data = fan, aes(x, y, fill = sector, group = sector), inherit.aes = FALSE, alpha = 0.18) + scale_fill_manual(values = cols, guide = "none") +
  geom_segment(data = land, aes(x = 3, xend = 4, y = green_mid, yend = full_mid, colour = sector), inherit.aes = FALSE, linewidth = 1.6) +
  geom_point(data = land, aes(x = 4, y = full_mid, colour = sector), inherit.aes = FALSE, size = 3.6) +
  geom_text(data = land, aes(x = 4.07, y = full_mid + ifelse(sector == "Forest", 12, -12), colour = sector, label = paste(sector, usd(full_mid)), vjust = ifelse(sector == "Forest", 0, 1)), inherit.aes = FALSE, hjust = 0, size = 4.5, fontface = "bold") +
  geom_text(data = land, aes(x = 4.07, y = full_hi + ifelse(sector == "Forest", 14, 0), colour = sector, label = usd(full_hi)), inherit.aes = FALSE, hjust = 0, size = 3.2, fontface = "bold") +
  geom_text(data = land, aes(x = 4.07, y = full_lo - ifelse(sector == "Forest", 0, 14), colour = sector, label = usd(full_lo)), inherit.aes = FALSE, hjust = 0, size = 3.2, fontface = "bold") +
  geom_hline(yintercept = 0, colour = wl$ink, linewidth = 0.4) +
  scale_y_continuous(labels = usd, limits = c(-60, 600), breaks = seq(0, 600, 100), expand = expansion(mult = c(0, 0.02))) +
  theme(plot.caption = element_text(hjust = 0, size = 9, colour = wl$muted)) +
  labs(caption = "Full step: agriculture charged $183B for land, nitrogen and water damages (FAO 2023); forest credited $42B for clean air (Cavender-Bares et al. 2022),\nwith water and habitat still unpriced, so the forest value is a floor.") +
  scale_x_continuous(breaks = 1:4, labels = c("Gross\n(what GDP\ncounts)", "Net\n(after\ndepreciation)", "Green net\n(after own\ncarbon)", "Full\n(land, water,\nair, habitat)"), expand = expansion(add = c(0.3, 1.1)))
tr <- fread("out/us_trade_ratio_1981_2025.csv")[!is.na(ratio)]; tlast <- tr[, .SD[year == max(year)], by = sector]   # SITC 1981 to 1990 plus HS 1991 to 2025, from 2026-10-05_us-trade-ratio-combine.R
tcols <- c(Agriculture = wl$context, `Forest products` = wl$poi, Seafood = wl$sea)
p2 <- ggplot(tr, aes(year, ratio, colour = sector)) + geom_hline(yintercept = 1, colour = wl$ink, linewidth = 0.5) +
  annotate("text", x = min(tr$year), y = 1.06, label = "Exports equal imports", hjust = 0, size = 3.4, colour = wl$muted) +
  annotate("text", x = 1993, y = 2.28, label = "Farms ran a surplus in every year but\nthree from 1981 to 2019. Forest products\nhave not run a surplus since the record\nbegins in 1981 (balanced in 2011, 2012).", hjust = 0, vjust = 1, size = 3.2, colour = wl$muted, lineheight = 0.95) +
  annotate("text", x = 1993, y = 2.85, hjust = 0, vjust = 1, size = 3.4, colour = wl$poi, fontface = "bold", lineheight = 0.95,
           label = "US forests grow 58% more wood than\nis cut, yet in 2024 the country imported\n$47B of wood, pulp and paper and\nexported $34B.") +
  geom_line(linewidth = 1.4) + geom_point(data = tlast, size = 2.8) +
  geom_text(data = tlast, aes(label = paste0(sub("Forest products", "Forest", sector), "\n", sprintf("%.2f", ratio))), hjust = 0, nudge_x = 0.6, size = 3.5, fontface = "bold", lineheight = 0.9) +
  scale_colour_manual(values = tcols, guide = "none") + scale_x_continuous(breaks = c(1981, 1990, 2000, 2010, 2020), expand = expansion(add = c(0.5, 13))) +
  scale_y_continuous(limits = c(0, 2.9), breaks = seq(0, 1, 0.25), expand = expansion(mult = c(0, 0))) +
  labs(title = "2. Misunderstood", subtitle = "Exports per dollar of imports, 1981 to 2025", x = NULL, y = NULL)
fund <- data.table(prog = factor(c("Agriculture\n(Hatch)", "Marine\n(Sea Grant)", "Forestry\n(McIntire-\nStennis)"), levels = c("Agriculture\n(Hatch)", "Marine\n(Sea Grant)", "Forestry\n(McIntire-\nStennis)")),
                   m = c(244, 76.5, 33), hi = c(NA, 91.5, NA), fill = c(wl$context, wl$sea, wl$poi))
p3 <- ggplot(fund, aes(prog, m)) + geom_col(fill = fund$fill, width = 0.62) +
  annotate("rect", xmin = 2.69, xmax = 3.31, ymin = 33, ymax = 120, fill = wl$poi, alpha = 0.25) +
  annotate("segment", x = 2.65, xend = 3.35, y = 120, yend = 120, colour = wl$poi, linewidth = 0.9, linetype = "22") +
  annotate("text", x = 3, y = 128, label = "Target $120M", colour = wl$poi, fontface = "bold", size = 3.6, vjust = 0) +
  geom_errorbar(aes(ymin = m, ymax = hi), width = 0.15, linewidth = 0.6, colour = wl$ink, na.rm = TRUE) +
  geom_text(aes(y = pmax(m, hi, na.rm = TRUE) + 7, label = paste0("$", ifelse(m %% 1 == 0, m, sprintf("%.1f", m)), "M")), size = 4.4, fontface = "bold", colour = wl$ink) +
  scale_y_continuous(limits = c(0, 285), expand = expansion(mult = c(0, 0))) + labs(title = "3. Underinvested", subtitle = "Federal research formula funds, FY2018", x = NULL, y = NULL)
th3 <- theme_minimal(base_size = 13, base_family = "Source Sans 3") + theme(panel.grid.minor = element_blank(), panel.grid.major.x = element_blank(), panel.grid.major.y = element_line(colour = wl$rule, linewidth = 0.3),
  plot.title = element_text(face = "bold", size = 15, colour = wl$ink), plot.subtitle = element_text(colour = wl$muted, size = 11), axis.text = element_text(colour = wl$muted, size = 11),
  axis.text.x = element_text(face = "bold", colour = wl$ink), plot.title.position = "plot")
fig3 <- (p1 + th3 + theme(axis.text.x = element_text(face = "bold", colour = wl$ink, size = 11), plot.caption = element_text(hjust = 0, size = 9, colour = wl$muted), plot.caption.position = "plot")) + (p2 + th3) + (p3 + th3 + theme(panel.grid.major.y = element_blank(), axis.text.y = element_blank())) +
  plot_layout(widths = c(1.9, 0.95, 0.85)) + plot_annotation(
  title = "America's forests are undervalued, misunderstood and underinvested",
  subtitle = sprintf("With carbon counted, forests are about half the size of agriculture, not a quarter. Charge farms for land, nitrogen and water damages,\ncredit forests for clean air, and the forest sector is likely the larger of the two (central %d%%, lower bound %d%%) before forest water\nand habitat are priced. The country grows far more wood than it cuts yet imports more than it sells, and funds forestry research at a\nseventh of agriculture's level.", round(100 * fo$full_mid / ag$full_mid), round(100 * fo$full_lo / ag$full_hi)),
  caption = paste0("Panel 1. Sectors are primary production plus first stage manufacturing: farms plus food, beverage and tobacco manufacturing (BEA 110C, 3110, 3120); wood and paper manufacturing (3210, 3220); marine living resources (BEA MESA). Forestry and logging\n",
                   "and farm support services are excluded from both land sectors (BEA reports them in one line, 113F). Net value added subtracts BEA current-cost depreciation by detailed industry (September 30, 2026; BEA rates the detail below its aggregates); marine\n",
                   "depreciation is a proxy. Shaded fans are scenario ranges, not statistical confidence intervals: each sector's own carbon (forest removal 771.7 MMT CO₂e, EPA GHGI 2024; direct farm emissions 596 MMT, EPA 2022) at $51, $120 and $190 per t (IWG 2021, EPA 2023).\n",
                   "BEA publishes no sampling error for value added. Fourth step, agriculture: FAO State of Food and Agriculture 2023, US environmental hidden costs of agrifood systems in 2020 (million 2020 PPP dollars): land 114,931, nitrogen 62,215, blue water 6,018\n",
                   "(climate 53,142 omitted because the carbon step already charges farm emissions), uncertainty minus 57% to plus 100%. Fourth step, forest: air quality regulation by US trees, 37% of $114B (range $85B to $137B, 2010 USD), Cavender-Bares et al. 2022,\n",
                   "PLOS Sustainability and Transformation; carbon and wood products from that study are already counted. Forest water yield (drinking water for about 180 million Americans) and habitat have no verified national dollar value, so the forest full value is a floor.\n",
                   "Mill, food plant and fleet emissions are not netted. Panel 2. UN\n",
                   "Comtrade, SITC Rev. 1 for 1981 to 1990 and HS for 1991 to 2025 (1991 overlap within 0.05); exports free on board, imports free on board where reported, otherwise CIF; agriculture HS 01 to 24 less seafood, forest\n",
                   "products HS 44, 47, 48, seafood HS 03, 1604, 1605. FAOSTAT forestry trade shows primary wood and paper products in deficit every year from 1961 to 1990. Growth to harvest ratio from Arkansas Center for Forest Business (2023).\n",
                   "Panel 3. Hatch and McIntire-Stennis FY2018 (OMB, COSSA); Sea Grant base $65.0M plus aquaculture $11.5M, FY2018 enacted (Consolidated Appropriations Act 2018 explanatory statement), whisker to FY2024 ($91.5M). The target is half of Hatch,\n",
                   "the central forest to agriculture ratio in panel 1. Chart: Weiskittel and Daigneault, University of Maine."),
  theme = theme(text = element_text(family = "Source Sans 3"), plot.title = element_text(face = "bold", size = 20, colour = wl$ink), plot.subtitle = element_text(colour = wl$poi, face = "bold", size = 12.5, margin = margin(b = 12)),
                plot.caption = element_text(colour = wl$faint, size = 8.4, hjust = 0, lineheight = 1.15), plot.caption.position = "plot", plot.title.position = "plot", plot.background = element_rect(fill = "white", colour = NA), plot.margin = margin(14, 16, 10, 14)))
ggsave("out/2026-10-04_three-gaps_DRAFT.png", fig3, width = 36, height = 21, units = "cm", dpi = 300, bg = "white")
ggsave("out/2026-10-04_three-gaps_DRAFT.pdf", fig3, width = 36, height = 21, units = "cm", bg = "white", device = cairo_pdf)
ggsave("out/thumb5.png", fig3, width = 36, height = 21, units = "cm", dpi = 60, bg = "white")
