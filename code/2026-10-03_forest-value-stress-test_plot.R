suppressMessages({library(data.table); library(ggplot2)})
update_geom_defaults("text", list(family = "Source Sans 3")); wl <- list(poi = "#134a31", context = "#8a948e", sea = "#0072b2", ink = "#14201a", muted = "#4a5750", faint = "#5f6b65", rule = "#d3dcd6", band = "#79bde9")
wide <- fread("out/bea_va_farms_forest_1997_2025.csv")[!is.na(year)]
mr <- fread("out/forest_va_multiplier_range.csv")
med <- median(unique(fread("out/acfb2023_state_va_multipliers.csv"), by = "area")[area != "United States"]$va_multiplier)
nva <- fread("out/bea_net_value_added_farms_forest_seafood.csv")
f22 <- nva[sector == "Forest products" & year == 2022, nva] / 1e3; farm22 <- nva[sector == "Farms" & year == 2022, nva] / 1e3
sea22 <- nva[sector == "Seafood" & year == 2022, nva] / 1e3
co2 <- 771.7; scc <- c(lo = 51, mid = 120, hi = 190)          # MMT CO2e (EPA GHGI 2024, 2022 flux); $ per t (IWG 2021 3%; EPA 2023 at 2.5% and 2%)
orsa <- 696.7; rec <- c(lo = 16.5 + 7.6, mid = 0.10 * orsa, hi = 0.25 * orsa)   # hunting + snow (BEA 2024) floor; 10% and 25% shares are assumptions
mult <- c(lo = mr[stat == "p05_state", multiplier], mid = med, hi = mr[stat == "national", multiplier])
agco2 <- 0.094 * 6343   # MMT CO2e, direct agriculture emissions 2022: 9.4% of 6,343 (EPA agriculture sector emissions page)
farm_green <- farm22 - agco2 * scc / 1e3
steps <- data.table(step = c("Wood and paper net value added (BEA)", "+ multiplier effects", "+ carbon sink at social cost of carbon", "+ outdoor recreation in forests"),
  lo = c(f22, f22 * mult["lo"], f22 * mult["lo"] + co2 * scc["lo"] / 1e3, f22 * mult["lo"] + co2 * scc["lo"] / 1e3 + rec["lo"]),
  mid = c(f22, f22 * mult["mid"], f22 * mult["mid"] + co2 * scc["mid"] / 1e3, f22 * mult["mid"] + co2 * scc["mid"] / 1e3 + rec["mid"]),
  hi = c(f22, f22 * mult["hi"], f22 * mult["hi"] + co2 * scc["hi"] / 1e3, f22 * mult["hi"] + co2 * scc["hi"] / 1e3 + rec["hi"]))
steps[, step := factor(step, levels = rev(step))]
fwrite(steps, "out/stress_test_forest_contribution_2022.csv")
lab <- function(x) paste0("$", round(x), "B")
p <- ggplot(steps, aes(y = step)) +
  annotate("rect", xmin = farm_green["hi"], xmax = farm_green["lo"], ymin = -Inf, ymax = Inf, fill = wl$context, alpha = 0.15) +
  geom_vline(xintercept = farm22, colour = wl$context, linewidth = 0.8, linetype = "22") +
  annotate("text", x = farm22, y = 4.42, label = paste0("Farms, net ", lab(farm22)), hjust = -0.03, size = 4, colour = wl$muted, fontface = "bold") +
  annotate("text", x = farm_green["hi"], y = 0.62, label = paste0("Farms, net, less own emissions: ", lab(farm_green["hi"]), " to ", lab(farm_green["lo"])), hjust = -0.02, size = 3.6, colour = wl$muted, fontface = "bold") +
  geom_vline(xintercept = sea22, colour = wl$sea, linewidth = 0.8, linetype = "22") +
  annotate("text", x = sea22, y = 4.42, label = paste0("Seafood, net ", lab(sea22)), hjust = -0.05, size = 4, colour = wl$sea, fontface = "bold") +
  geom_linerange(aes(xmin = lo, xmax = hi), linewidth = 7, colour = wl$poi, alpha = 0.25) +
  geom_point(aes(x = mid), size = 4.5, colour = wl$poi) +
  geom_text(aes(x = hi, label = ifelse(lo == hi, lab(mid), paste0(lab(lo), " to ", lab(hi)))), hjust = -0.12, size = 4.6, fontface = "bold", colour = wl$ink) +
  scale_x_continuous(labels = lab, limits = c(0, 900), breaks = seq(0, 800, 200), expand = expansion(mult = c(0, 0))) +
  scale_y_discrete(expand = expansion(add = c(0.6, 0.9))) +
  labs(x = "Billion dollars per year, around 2022", y = NULL,
       title = paste0("Counting carbon and recreation lifts forests from ", lab(f22), " to between ", lab(steps[4, lo]), " and ", lab(steps[4, hi]), " a year"),
       subtitle = "Cumulative scenarios. Dots are central values, bars are low to high assumptions. These are not all GDP and should not be read as a national account.",
       caption = paste0("Base: BEA wood and paper manufacturing net value added (value added less current-cost depreciation), 2022. Multipliers are applied to the net base, an approximation.\nMultipliers: 5th percentile of state value-added multipliers (", sprintf("%.2f", mult["lo"]), "), state median (", sprintf("%.2f", mult["mid"]),
                        ") and national (", sprintf("%.2f", mult["hi"]), "), Arkansas Center for Forest Business (2023).\n",
                        "Carbon: net flux of forest land remaining forest land, 771.7 MMT CO2e in 2022 (EPA Inventory 2024), valued at $51 (Interagency Working Group 2021, 3%), $120 and $190 per tonne (EPA 2023, 2.5% and 2%), 2020 dollars.\n",
                        "No federal social cost of carbon has been in force since Executive Order 14154 (January 2025). Recreation: low is BEA hunting, shooting and trapping plus snow activities ($24B, 2024); central and high assume\n",
                        "10% and 25% of BEA outdoor recreation value added ($697B, 2024) occurs in forests, an assumption, not an estimate. Water supply and quality are excluded because no current national dollar value was verified.\n",
                        "Gray band: farm net value added less direct agricultural emissions (9.4% of 6,343 MMT CO2e, EPA, 2022) at the same carbon prices, a scenario. Farms would also carry multipliers; nutrient and water damages are not counted for either sector.\nForest products manufacturing emissions are not netted. Chart: Weiskittel and Daigneault, University of Maine.")) +
  theme_minimal(base_size = 14, base_family = "Source Sans 3") +
  theme(panel.grid.minor = element_blank(), panel.grid.major.y = element_blank(), panel.grid.major.x = element_line(colour = wl$rule, linewidth = 0.3),
        axis.text.y = element_text(face = "bold", colour = wl$ink, size = 13), axis.text.x = element_text(colour = wl$muted, size = 12),
        axis.title.x = element_text(face = "bold", colour = wl$ink, size = 12, margin = margin(t = 8)),
        plot.title = element_text(face = "bold", size = 19, colour = wl$ink), plot.subtitle = element_text(colour = wl$poi, face = "bold", size = 12.5, margin = margin(b = 10)),
        plot.caption = element_text(colour = wl$faint, size = 9, hjust = 0, lineheight = 1.15), plot.title.position = "plot", plot.caption.position = "plot",
        plot.background = element_rect(fill = "white", colour = NA), plot.margin = margin(14, 18, 10, 14))
ggsave("out/2026-10-03_forest-value-stress-test_DRAFT.png", p, width = 36, height = 18, units = "cm", dpi = 300, bg = "white")
ggsave("out/2026-10-03_forest-value-stress-test_DRAFT.pdf", p, width = 36, height = 18, units = "cm", bg = "white", device = cairo_pdf)
ggsave("out/thumb3.png", p, width = 36, height = 18, units = "cm", dpi = 60, bg = "white")
print(steps)
