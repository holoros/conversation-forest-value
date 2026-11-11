# Follow the wood with a leakage layer: routes from the article over carbon leakage rates
# Shading is cropped from Daigneault et al. 2025, Environ. Res. Lett. 20:114022, figure 2a (CC BY 4.0).
suppressMessages({library(ggplot2); library(maps); library(mapdata); library(png)})
grn <- "#1F4D36"; nav <- "#12355B"; land <- "#E8E6E1"; ink <- "#2B2B2B"; gry <- "#6E6E6E"
th <- theme_void(base_family = "sans") +
  theme(plot.title = element_text(family = "serif", face = "bold", size = 22, colour = grn, margin = margin(b = 6)),
        plot.subtitle = element_text(size = 12, colour = ink, lineheight = 1.15, margin = margin(b = 10)),
        plot.caption = element_text(size = 8.5, colour = "#555555", hjust = 0, lineheight = 1.2, margin = margin(t = 10)),
        plot.background = element_rect(fill = "white", colour = NA),
        panel.background = element_rect(fill = "#F4F8FB", colour = NA),
        plot.margin = margin(18, 22, 14, 22), plot.title.position = "plot", plot.caption.position = "plot")
world <- map_data("worldHires", xlim = c(-110, -25), ylim = c(-40, 62))
states <- map_data("state")
leak <- readPNG("leak.png"); legbar <- readPNG("legbar.png")
# georeference of the published figure (plate carree), fitted to coastline extremes
x0 <- -177.5; sc <- 3.745; xmx <- x0 + dim(leak)[2] / sc; ymx <- 314.7 / sc; ymn <- ymx - dim(leak)[1] / sc
pts <- data.frame(lon = c(-66.06, -83.63, -51.7), lat = c(45.27, 32.84, -20.8))
routes <- data.frame(x = c(-66.06, -51.7), y = c(45.27, -20.8), xend = c(-83.4, -77.3), yend = c(33.1, 37.6))
lab <- function(x, y, txt, hj = 0.5) annotate("label", x = x, y = y, hjust = hj, size = 3.7, linewidth = 0.3, lineheight = 1.05, fill = "white", label = txt)
a <- ggplot() +
  geom_polygon(data = world, aes(long, lat, group = group), fill = land, colour = NA) +
  annotation_raster(leak, xmin = x0, xmax = xmx, ymin = ymn, ymax = ymx, interpolate = TRUE) +
  geom_polygon(data = world, aes(long, lat, group = group), fill = NA, colour = "white", linewidth = 0.25) +
  geom_polygon(data = states, aes(long, lat, group = group), fill = NA, colour = "white", linewidth = 0.2) +
  geom_polygon(data = subset(states, region == "maine"), aes(long, lat, group = group), fill = NA, colour = grn, linewidth = 0.9) +
  geom_curve(data = routes[1, ], aes(x, y, xend = xend, yend = yend), colour = nav, linewidth = 1.3, curvature = 0.25,
             arrow = arrow(length = unit(0.18, "in"), type = "closed")) +
  geom_curve(data = routes[2, ], aes(x, y, xend = xend, yend = yend), colour = nav, linewidth = 1.3, curvature = -0.3,
             arrow = arrow(length = unit(0.18, "in"), type = "closed")) +
  geom_point(data = pts, aes(lon, lat), size = 3.2, colour = ink) +
  lab(-89, 29.4, "Macon, Ga.\nSaint John pulp becomes\ntissue, 1,000+ miles away") +
  lab(-64.5, 48.6, "Saint John, N.B.\nPulp mill", 0) +
  annotate("segment", x = -54, y = 38.1, xend = -68.6, yend = 44.6, colour = gry, linewidth = 0.4) +
  lab(-48, 33.5, "Maine logs cross the border to Quebec\nsawmills. In 2023, about 2 million tons of\nMaine's harvest left the state unprocessed,\nwhile 2.7 million tons came in from\nneighboring states and provinces") +
  lab(-47, -30, "Brazil supplies about 82% of\nthe hardwood pulp the U.S. buys,\nmostly from eucalyptus plantations") +
  annotate("text", x = -69.2, y = 48.4, label = "MAINE", colour = grn, fontface = "bold", size = 4, hjust = 0.5) +
  annotation_raster(legbar, xmin = -95, xmax = -93, ymin = -22, ymax = -4) +
  annotate("text", x = -92.3, y = c(-4.6, -13, -21.4), label = c("50% lost", "0%", "-50% (a net gain)"), hjust = 0, size = 3.3, colour = ink) +
  annotate("text", x = -95, y = -1.2, label = "Carbon gain lost\nto leakage", hjust = 0, vjust = 0, size = 3.5, fontface = "bold", colour = ink, lineheight = 1) +
  coord_quickmap(xlim = c(-98, -32), ylim = c(-36, 52), expand = FALSE) +
  labs(title = "Follow the wood, and the leakage",
       subtitle = "When a mill closes, Americans keep buying paper and the fiber comes from farther away. Shading shows\nhow much of the carbon gained by delaying harvests in a region is lost as cutting shifts somewhere else.",
       caption = paste0("Routes are schematic and show origin and destination, not shipping paths. Shading: mean carbon leakage for extended rotations at a 10% implementation\nrate, adapted from Daigneault et al. 2025, Environ. Res. Lett. 20:114022, figure 2a (CC BY 4.0). Gray land had no modeled timber forest. Set-aside projects\nin the same study showed much lower and often negative leakage.\nOther sources: J.D. Irving (Saint John to Macon); Rabobank (Brazil's share of U.S. hardwood pulp imports); Maine Forest Service 2023 Wood Processor\nReport via maineforestdashboard.com (wood leaving and entering Maine); Maine TREE Foundation (logs to Quebec).\n",
                        "Graphic: Center for Research on Sustainable Forests, University of Maine.")) + th
ggsave("2026-11-10_follow-the-wood-leakage-map_DRAFT.png", a, width = 10, height = 10.5, dpi = 300, bg = "white")
cat("done\n")
