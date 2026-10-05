# Graphical abstract for the Zenodo record (2 x 2 panels), built from the deposited CSVs.
# Usage: Rscript graphical_abstract.R [--doi 10.5281/zenodo.NNNNNNN]
# Run from the deposit root (data/ and the output PNG live there).
suppressMessages({library(data.table); library(ggplot2); library(patchwork)})
args <- commandArgs(trailingOnly = TRUE); doi <- if (length(i <- which(args == "--doi"))) args[i + 1] else NA
ff <- "Source Sans 3"; update_geom_defaults("text", list(family = ff))
wl <- list(poi = "#134a31", context = "#8a948e", sea = "#0072b2", ink = "#14201a", muted = "#4a5750", rule = "#d3dcd6")
cols <- c(Farms = wl$context, Agriculture = wl$context, `Forest products` = wl$poi, Forest = wl$poi, Seafood = wl$sea, Marine = wl$sea)
th <- theme_minimal(base_size = 13, base_family = ff) + theme(panel.grid.minor = element_blank(), panel.grid.major.x = element_blank(),
  panel.grid.major.y = element_line(colour = wl$rule, linewidth = 0.3), plot.title = element_text(face = "bold", size = 14, colour = wl$ink),
  plot.subtitle = element_text(colour = wl$muted, size = 10.5), axis.text = element_text(colour = wl$muted, size = 10), plot.title.position = "plot")
sec <- fread("data/sector_green_nva_2022.csv"); sec[, sector := sub(" sector", "", sector)]
lng <- melt(sec[, .(sector, `Gross` = gva, `Net` = nva, `Green net` = green_mid, `Full` = full_mid)], id.vars = "sector", variable.name = "basis", value.name = "bn")
lng[, x := as.integer(basis)]; lst <- lng[x == 4]
fan <- rbindlist(lapply(split(sec[sector != "Marine"], sec[sector != "Marine"]$sector), function(d) data.table(sector = d$sector[1], x = c(3, 4, 4), y = c(d$green_nva_mid, d$full_lo, d$full_hi))))
p1 <- ggplot(lng, aes(x, bn, colour = sector)) + geom_hline(yintercept = 0, colour = wl$ink, linewidth = 0.3) +
  geom_polygon(data = fan, aes(x, y, fill = sector, group = sector), inherit.aes = FALSE, alpha = 0.16) + scale_fill_manual(values = cols, guide = "none") +
  geom_line(linewidth = 1.2) + geom_point(size = 2.2) +
  geom_text(data = lst, aes(x = 4.1, y = bn + ifelse(sector == "Forest", 10, ifelse(sector == "Agriculture", -10, 0)), label = paste0(sector, " $", round(bn), "B")), hjust = 0, size = 3.4, fontface = "bold") +
  scale_colour_manual(values = cols, guide = "none") + scale_x_continuous(breaks = 1:4, labels = c("Gross", "Net", "Green\nnet", "Full"), expand = expansion(add = c(0.3, 0.3))) + coord_cartesian(clip = "off") +
  scale_y_continuous(labels = function(x) paste0("$", x, "B"), limits = c(-60, 600)) +
  labs(title = "a. Sector value added, 2022, four bases", subtitle = "Net of depreciation, own carbon, then FAO 2023 and\nCavender-Bares 2022 (scenario fans)", x = NULL, y = NULL) + th + theme(plot.margin = margin(5.5, 120, 5.5, 5.5), axis.text.x = element_text(face = "bold", colour = wl$ink, size = 9.5))
tr <- fread("data/us_trade_ratio_1981_2025.csv")[!is.na(ratio)]; tl <- tr[, .SD[year == max(year)], by = sector]
p2 <- ggplot(tr, aes(year, ratio, colour = sector)) + geom_hline(yintercept = 1, colour = wl$ink, linewidth = 0.4) + geom_line(linewidth = 1.2) +
  geom_text(data = tl, aes(y = ratio + ifelse(sector == "Agriculture", 0.12, ifelse(sector == "Forest products", -0.12, 0)), label = paste0(sector, " ", sprintf("%.2f", ratio))), hjust = 0, nudge_x = 0.5, size = 3.4, fontface = "bold") +
  scale_colour_manual(values = cols, guide = "none") + scale_x_continuous(breaks = c(1981, 1990, 2000, 2010, 2020), expand = expansion(add = c(0.3, 0.3))) + coord_cartesian(clip = "off") +
  scale_y_continuous(limits = c(0, 2.4)) + labs(title = "b. Exports per dollar of imports", subtitle = "UN Comtrade, 1981 to 2025\n(SITC to 1990, HS from 1991)", x = NULL, y = NULL) + th + theme(plot.margin = margin(5.5, 125, 5.5, 5.5))
fund <- data.table(prog = factor(c("Agriculture", "Marine", "Forestry"), levels = c("Agriculture", "Marine", "Forestry")), m = c(244, 76.5, 33), sector = c("Farms", "Seafood", "Forest products"))
p3 <- ggplot(fund, aes(prog, m, fill = sector)) + geom_col(width = 0.6) + geom_text(aes(label = paste0("$", round(m), "M")), vjust = -0.4, size = 4, fontface = "bold", colour = wl$ink) +
  scale_fill_manual(values = cols, guide = "none") + scale_y_continuous(limits = c(0, 280)) +
  labs(title = "c. Research formula funds", subtitle = "FY2018, all three programs", x = NULL, y = NULL) +
  th + theme(axis.text.y = element_blank(), panel.grid.major.y = element_blank(), axis.text.x = element_text(face = "bold", colour = wl$ink, size = 9.5))
st <- fread("data/stress_test_forest_contribution_2022.csv"); st[, step := factor(step, levels = rev(step))]
levels(st$step) <- sub("Wood and paper value added \\(BEA\\)", "Wood and paper (BEA)", sub("\\+ carbon sink at social cost of carbon", "+ carbon sink (SCC)", sub("\\+ outdoor recreation in forests", "+ forest recreation", levels(st$step))))
p4 <- ggplot(st, aes(y = step)) + geom_linerange(aes(xmin = lo, xmax = hi), linewidth = 6, colour = wl$poi, alpha = 0.25) + geom_point(aes(x = mid), size = 3, colour = wl$poi) +
  geom_text(aes(x = mid, label = ifelse(lo == hi, paste0("$", round(mid), "B"), paste0("$", round(lo), "B to $", round(hi), "B"))), nudge_y = 0.38, size = 3.4, fontface = "bold", colour = wl$ink) +
  scale_x_continuous(labels = function(x) paste0("$", x, "B"), limits = c(0, 760), breaks = c(0, 250, 500, 750)) + coord_cartesian(clip = "off") +
  labs(title = "d. Forest value stress test, about 2022", subtitle = "Cumulative scenarios, not a national account", x = NULL, y = NULL) +
  th + theme(axis.text.y = element_text(face = "bold", colour = wl$ink, size = 10), panel.grid.major.y = element_blank())
cap <- paste0("Weiskittel and Daigneault (2026). Data: BEA, UN Comtrade, NOAA, EPA, FAO, Arkansas Center for Forest Business, Cavender-Bares et al. (2022).\nForest water and habitat are unpriced, so the forest full value is a floor.", if (!is.na(doi)) paste0(" doi:", doi) else "")
fig <- (p1 | p2) / ((p3 | p4) + plot_layout(widths = c(1, 1.3))) + plot_annotation(title = "How much are America's forests worth?",
  caption = cap, theme = theme(text = element_text(family = ff), plot.title = element_text(face = "bold", size = 17, colour = wl$ink),
  plot.caption = element_text(colour = wl$muted, size = 9, hjust = 0), plot.background = element_rect(fill = "white", colour = NA)))
ggsave("00_forest-value_graphical_abstract.png", fig, width = 22, height = 15, units = "cm", dpi = 300, bg = "white")
cat("written 00_forest-value_graphical_abstract.png", if (!is.na(doi)) paste("with", doi) else "(no DOI yet)", "\n")
