suppressMessages({library(data.table); library(ggplot2); library(patchwork); library(readxl)})
update_geom_defaults("text", list(family = "Source Sans 3")); wl <- list(poi = "#134a31", context = "#8a948e", sea = "#0072b2", ink = "#14201a", muted = "#4a5750", faint = "#5f6b65", rule = "#d3dcd6")
cols <- c(Seafood_ = wl$sea, Farms = wl$context, Agriculture = wl$context, `Forest products` = wl$poi, Seafood = wl$sea, `Marine living resources` = wl$sea)
wide <- fread("out/bea_va_farms_forest_1997_2025.csv")[!is.na(year)]
nva <- fread("out/bea_net_value_added_farms_forest_seafood.csv")   # from 2026-10-03_net-value-added_data.R
m <- as.data.table(suppressMessages(read_excel("MESA_VA.xlsx", sheet = "VA", col_names = FALSE)))
yrs <- as.integer(unlist(m[3, -(1:2)])); lr <- as.numeric(unlist(m[trimws(m[[2]]) == "Living resources, marine"][1, -(1:2)]))
mar <- data.table(year = yrs, bn = lr / 1e3, sector = "Marine living resources")
fwrite(mar, "out/bea_mesa_living_resources_2014_2023.csv")
va <- nva[, .(year, sector, bn = nva / 1e3)]
last <- va[, .SD[year == max(year)], by = sector]
f23 <- va[sector == "Forest products" & year == 2023, bn]; m23 <- va[sector == "Seafood" & year == 2023, bn]; xs <- round(f23 / m23)
yl <- max(va[sector == "Farms", year]); ratio <- round(100 * va[sector == "Forest products" & year == yl, bn] / va[sector == "Farms" & year == yl, bn])
th <- theme_minimal(base_size = 14, base_family = "Source Sans 3") + theme(panel.grid.minor = element_blank(), panel.grid.major.x = element_blank(),
  panel.grid.major.y = element_line(colour = wl$rule, linewidth = 0.3), plot.title = element_text(face = "bold", size = 15.5, colour = wl$ink),
  plot.subtitle = element_text(colour = wl$muted, size = 11.5), axis.text = element_text(colour = wl$muted, size = 11.5), plot.title.position = "plot")
lab <- function(s) as.character(s)
mul <- fread("out/acfb2023_state_va_multipliers.csv")
mul <- unique(mul, by = "area"); ms <- mul[area != "United States"]$va_multiplier
m_us <- mul[area == "United States"]$va_multiplier[1]
q <- quantile(ms, c(0.05, 0.25, 0.75))
band <- va[sector == "Forest products", .(year, lo95 = bn * q[1], hi95 = bn * m_us, lo50 = bn * q[2], hi50 = bn * q[3])]
fwrite(data.table(stat = c("p05_state", "p25_state", "p75_state", "national"), multiplier = c(q, m_us)), "out/forest_va_multiplier_range.csv")
p1 <- ggplot(va, aes(year, bn, colour = sector)) +
  geom_ribbon(data = band, aes(x = year, ymin = lo95, ymax = hi95), inherit.aes = FALSE, fill = wl$poi, alpha = 0.12) +
  geom_ribbon(data = band, aes(x = year, ymin = lo50, ymax = hi50), inherit.aes = FALSE, fill = wl$poi, alpha = 0.22) +
  annotate("text", x = 1998, y = band[year == 1998, hi95] + 12, hjust = 0, size = 3.6, colour = wl$poi, fontface = "bold", label = "With multiplier effects") +
  geom_line(linewidth = 1.4) + geom_point(data = last, size = 2.8) +
  geom_text(data = last, aes(label = paste0(lab(sector), "\n$", round(bn), "B")), hjust = 0, nudge_x = 0.7, size = 4.3, fontface = "bold", lineheight = 0.9) +
  scale_colour_manual(values = cols, guide = "none") +
  scale_x_continuous(breaks = seq(2000, 2025, 5), expand = expansion(add = c(0.5, 11))) +
  scale_y_continuous(labels = function(x) paste0("$", x, "B"), limits = c(0, 400), breaks = seq(0, 400, 100), expand = expansion(mult = c(0, 0.02))) +
  labs(title = "Net value added to US GDP", subtitle = "Current dollars, after depreciation", x = NULL, y = NULL) + th
tr <- fread("out/us_trade_ratio_2014_2024.csv")[!is.na(ratio)]
tlast <- tr[, .SD[year == max(year)], by = sector]
p2 <- ggplot(tr, aes(year, ratio, colour = sector)) + geom_hline(yintercept = 1, colour = wl$ink, linewidth = 0.5) +
  annotate("text", x = min(tr$year), y = 1.09, label = "Exports equal imports", hjust = 0, size = 3.6, colour = wl$muted) +
  geom_line(linewidth = 1.4) + geom_point(data = tlast, size = 2.8) +
  geom_text(data = tlast, aes(label = paste0(sector, "\n", sprintf("%.2f", ratio))), hjust = 0, nudge_x = 0.4, size = 4.3, fontface = "bold", lineheight = 0.9) +
  scale_colour_manual(values = cols, guide = "none") +
  scale_x_continuous(breaks = c(2017, 2021, 2025), expand = expansion(add = c(0.3, 4.2))) +
  scale_y_continuous(limits = c(0, 1.15), breaks = seq(0, 1, 0.25), expand = expansion(mult = c(0, 0.02))) +
  labs(title = "Exports per dollar of imports", subtitle = "US goods trade, 2017 to 2025", x = NULL, y = NULL) + th
fund <- data.table(prog = factor(c("Agriculture\n(Hatch Act)", "Marine\n(Sea Grant)", "Forestry\n(McIntire-\nStennis)"), levels = c("Agriculture\n(Hatch Act)", "Marine\n(Sea Grant)", "Forestry\n(McIntire-\nStennis)")),
                   m = c(244, 80, 33), sector = c("Farms", "Seafood", "Forest products"))
p3 <- ggplot(fund, aes(prog, m, fill = sector)) + geom_col(width = 0.62) +
  geom_text(aes(label = paste0("$", m, "M")), vjust = -0.45, size = 5, fontface = "bold", colour = wl$ink) +
  scale_fill_manual(values = cols, guide = "none") + scale_y_continuous(limits = c(0, 285), expand = expansion(mult = c(0, 0))) +
  labs(title = "Research formula funds", subtitle = "Federal, FY2018 (Sea Grant FY2019)", x = NULL, y = NULL) +
  th + theme(panel.grid.major.y = element_blank(), axis.text.y = element_blank(), axis.text.x = element_text(face = "bold", colour = wl$ink, size = 11.5))
fig <- p1 + p2 + p3 + plot_layout(widths = c(1.5, 1.15, 0.85)) + plot_annotation(
  title = paste0("After depreciation, forest products add ", xs, " times as much to GDP as seafood and ", ratio, "% as much as farms,\nyet the US imports more wood than it sells and funds forestry research at a seventh of agriculture's level"),
  subtitle = "None of these totals counts outdoor recreation, which added $697B to US GDP in 2024 and includes hiking, hunting and camping in forests.",
  caption = paste0("Lines are net value added, BEA value added less current-cost depreciation of private nonresidential fixed assets by industry (BEA Fixed Assets detail, September 30, 2026). Subsidies are already\n",
                   "netted out of BEA value added. Seafood depreciation is a proxy (harvest and markets at the forestry, fishing and related ratio, processing at the food manufacturing ratio). Green bands are a scenario\n",
                   "range, not a confidence interval: forest products net value added times state value-added multipliers from the 25th to 75th percentile (dark, 1.66 to 1.98) and from the 5th percentile to the national\n",
                   "multiplier (light, 1.53 to 2.78), Arkansas Center for Forest Business (2023). Farms and seafood also have multiplier effects, not shown. Forest products are wood and paper manufacturing; forestry and\n",
                   "logging are excluded because BEA combines them with fishing and farm support services. Seafood is BEA marine commercial harvest, seafood markets and processing, 2014 to 2023 (marine pharmaceuticals\n",
                   "excluded). Trade: agriculture HS 01 to 24 less seafood; forest products HS 44, 47, 48; seafood HS 03, 1604, 1605; both flows free on board. Sources: BEA GDP by Industry (TVA105-A, September 30, 2026);\n",
                   "BEA Marine Economy and Outdoor Recreation Satellite Accounts; UN Comtrade; McIntire-Stennis (OMB) and Hatch (COSSA) via Weiskittel et al. (in review); Sea Grant base plus aquaculture, NOAA FY2020\n",
                   "budget justification (also funds extension and education). Chart: Weiskittel and Daigneault, University of Maine."),
  theme = theme(text = element_text(family = "Source Sans 3"), plot.title = element_text(face = "bold", size = 19, colour = wl$ink, lineheight = 1.05, margin = margin(b = 6)),
                plot.subtitle = element_text(colour = wl$poi, face = "bold", size = 12.5, margin = margin(b = 10)),
                plot.caption = element_text(colour = wl$faint, size = 9, hjust = 0, lineheight = 1.15),
                plot.caption.position = "plot", plot.title.position = "plot",
                plot.background = element_rect(fill = "white", colour = NA), plot.margin = margin(14, 16, 10, 14)))
ggsave("out/2026-10-03_gdp-trade-research_DRAFT.png", fig, width = 36, height = 21, units = "cm", dpi = 300, bg = "white")
ggsave("out/2026-10-03_gdp-trade-research_DRAFT.pdf", fig, width = 36, height = 21, units = "cm", bg = "white", device = cairo_pdf)
ggsave("out/thumb2.png", fig, width = 36, height = 21, units = "cm", dpi = 60, bg = "white")
cat("ok", xs, ratio, "\n"); print(tr[, .N, by = sector])
