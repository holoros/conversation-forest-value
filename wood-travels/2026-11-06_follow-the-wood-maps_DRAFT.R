# Follow the wood: two maps for the Conversation sequel
# Data are locations and figures cited in the article; routes are schematic, not shipping paths.
suppressMessages({library(ggplot2); library(maps); library(mapdata); library(ggrepel)})
grn <- "#1F4D36"; org <- "#D9692E"; blu <- "#5B8DB8"; land <- "#E8E6E1"; ink <- "#2B2B2B"; gry <- "#8A8A8A"
th <- theme_void(base_family = "sans") +
  theme(plot.title = element_text(family = "serif", face = "bold", size = 22, colour = grn, margin = margin(b = 6)),
        plot.subtitle = element_text(size = 12.5, colour = ink, lineheight = 1.15, margin = margin(b = 10)),
        plot.caption = element_text(size = 8.5, colour = "#555555", hjust = 0, lineheight = 1.2, margin = margin(t = 10)),
        plot.background = element_rect(fill = "white", colour = NA),
        panel.background = element_rect(fill = "#F4F8FB", colour = NA),
        plot.margin = margin(18, 22, 14, 22), plot.title.position = "plot", plot.caption.position = "plot")
world <- map_data("worldHires", xlim = c(-110, -25), ylim = c(-40, 62))
states <- map_data("state")
## ---- Map A: the long trips ----
pts <- data.frame(
  name = c("Saint John, N.B.", "Macon, Ga.", "Maine", "Quebec sawmills", "Brazilian eucalyptus\npulp regions"),
  lon = c(-66.06, -83.63, -69.2, -70.7, -51.7), lat = c(45.27, 32.84, 45.3, 46.6, -20.8))
routes <- data.frame(
  x = c(-66.06, -51.7, -69.8), y = c(45.27, -20.8, 45.6),
  xend = c(-83.4, -75.5, -70.6), yend = c(33.1, 36.0, 46.45),
  col = c("pulp", "pulp", "logs"))
a <- ggplot() +
  geom_polygon(data = world, aes(long, lat, group = group), fill = land, colour = "white", linewidth = 0.2) +
  geom_polygon(data = states, aes(long, lat, group = group), fill = NA, colour = "white", linewidth = 0.25) +
  geom_polygon(data = subset(states, region == "maine"), aes(long, lat, group = group), fill = grn) +
  geom_curve(data = routes[1, ], aes(x, y, xend = xend, yend = yend), colour = org, linewidth = 1.3, curvature = 0.25,
             arrow = arrow(length = unit(0.18, "in"), type = "closed")) +
  geom_curve(data = routes[2, ], aes(x, y, xend = xend, yend = yend), colour = org, linewidth = 1.3, curvature = -0.3,
             arrow = arrow(length = unit(0.18, "in"), type = "closed")) +
    geom_point(data = pts[c(1, 2, 5), ], aes(lon, lat), size = 3.2, colour = ink) +
  annotate("label", x = -86, y = 29.6, hjust = 0.5, size = 3.7, linewidth = 0.3, lineheight = 1.05,
           label = "Macon, Ga.\nPulp from New Brunswick wood\nbecomes tissue, 1,000+ miles away") +
  annotate("label", x = -64.5, y = 48.6, hjust = 0, size = 3.7, linewidth = 0.3, lineheight = 1.05,
           label = "Saint John, N.B.\nPulp mill") +
  annotate("label", x = -47, y = 33.5, hjust = 0.5, size = 3.7, linewidth = 0.3, lineheight = 1.05,
           label = "Maine logs cross the border to Quebec\nsawmills. In 2023, about 2 million tons of\nMaine's harvest left the state unprocessed,\nwhile 2.7 million tons came in from\nneighboring states and provinces") +
  annotate("segment", x = -55, y = 36.8, xend = -68.6, yend = 44.6, colour = gry, linewidth = 0.4) +
  annotate("label", x = -47, y = -4, hjust = 0.5, size = 3.7, linewidth = 0.3, lineheight = 1.05,
           label = "Brazil supplies about 82% of\nthe hardwood pulp the U.S. buys,\nmostly from eucalyptus plantations") +
  annotate("text", x = -69.2, y = 43.2, label = "MAINE", colour = grn, fontface = "bold", size = 4, hjust = 0) +
  coord_quickmap(xlim = c(-98, -32), ylim = c(-26, 52), expand = FALSE) +
  labs(title = "Follow the wood",
       subtitle = "When a mill closes, Americans keep buying paper. The fiber comes from farther away,\nand some of Maine's own wood leaves the state before anyone turns it into a product.",
       caption = paste0("Routes are schematic and show origin and destination, not shipping paths.\nSources: J.D. Irving (Saint John to Macon); Rabobank (Brazil's share of U.S. hardwood pulp imports);\nMaine Forest Service 2023 Wood Processor Report via maineforestdashboard.com (wood leaving and entering Maine);\nMaine TREE Foundation (logs to Quebec).\n",
                        "Graphic: Center for Research on Sustainable Forests, University of Maine.")) + th
ggsave("2026-11-06_follow-the-wood-map_DRAFT.png", a, width = 10, height = 10.5, dpi = 300, bg = "white")
## ---- Map B: Maine's mill towns, then and next ----
me <- data.frame(
  town = c("Jay", "Madison", "Lincoln", "Saco", "Orono"),
  lon = c(-70.22, -69.88, -68.50, -70.44, -68.67), lat = c(44.50, 44.80, 45.36, 43.50, 44.88),
  kind = c("closed", "reborn", "reborn", "new", "research"),
  lab = c("Jay\nAndroscoggin Mill closed in 2023,\nabout 230 jobs lost",
          "Madison\nPaper mill closed in 2016; TimberHP now\nmakes insulation from chips and thinnings",
          "Lincoln\nBiorefinery planned at a former\npaper mill to turn wood waste into fuel",
          "Saco\nTanbark makes food containers\nfrom wood fiber",
          "Orono\nUniversity of Maine pilot plant makes\ncellulose nanofibrils; leads the\nForest Bioproducts Tech Hub"))
cols <- c(closed = "#5A5A5A", reborn = org, new = org, research = grn)
shp <- c(closed = 4, reborn = 16, new = 16, research = 17)
can <- map_data("worldHires", xlim = c(-75, -64), ylim = c(42, 49))
b <- ggplot() +
  geom_polygon(data = can, aes(long, lat, group = group), fill = land, colour = "white", linewidth = 0.3) +
  geom_polygon(data = states, aes(long, lat, group = group), fill = land, colour = "white", linewidth = 0.4) +
  geom_polygon(data = subset(states, region == "maine"), aes(long, lat, group = group), fill = "#DCE8DF", colour = grn, linewidth = 0.5) +
  geom_point(data = me, aes(lon, lat, colour = kind, shape = kind), size = 4.5, stroke = 1.6) +
  geom_label_repel(data = me, aes(lon, lat, label = lab), size = 3.5, lineheight = 1.05, linewidth = 0.3,
                   box.padding = 0.6, point.padding = 0.5, min.segment.length = 0, seed = 7,
                   nudge_x = c(-1.6, -1.9, 1.4, -1.2, 1.6), nudge_y = c(0.35, 1.15, 0.9, -0.35, -0.6), segment.colour = gry) +
  scale_colour_manual(values = cols, guide = "none") + scale_shape_manual(values = shp, guide = "none") +
  coord_quickmap(xlim = c(-73.6, -65.2), ylim = c(42.9, 47.6), expand = FALSE) +
  labs(title = "Maine's mill towns, then and next",
       subtitle = "Gray X marks a closed mill. Orange marks new uses for wood, two of them in former paper mill towns.\nGreen marks university research behind the state's Forest Bioproducts Tech Hub.",
       caption = paste0("Sources: Boston Globe (Jay); Mainebiz (Madison, TimberHP); UMaine News (Tech Hub); Town of Lincoln (biorefinery status, Jan. 2026);\nMaine Public (Tanbark); UMaine Process Development Center (pilot plant).\n",
                        "Graphic: Center for Research on Sustainable Forests, University of Maine.")) + th
ggsave("2026-11-06_maine-mill-towns-map_DRAFT.png", b, width = 10, height = 8.5, dpi = 300, bg = "white")
cat("done\n")
