# Maine mill towns and Quebec border mills, for the Conversation sequel
# Quebec mills: Gouvernement du Quebec, Liste des usines de transformation primaire du bois (CC BY 4.0), file updated June 25, 2026.
suppressMessages({library(ggplot2); library(maps); library(mapdata); library(ggrepel)})
grn <- "#1F4D36"; red <- "#A23B2A"; nav <- "#2F6C9E"; lblu <- "#8DB7D8"; land <- "#E8E6E1"; ink <- "#2B2B2B"; gry <- "#6E6E6E"
th <- theme_void(base_family = "sans") +
  theme(plot.title = element_text(family = "serif", face = "bold", size = 22, colour = grn, margin = margin(b = 6)),
        plot.subtitle = element_text(size = 12.5, colour = ink, lineheight = 1.15, margin = margin(b = 10)),
        plot.background = element_rect(fill = "white", colour = NA),
        panel.background = element_rect(fill = "#F4F8FB", colour = NA),
        plot.margin = margin(18, 22, 18, 22), plot.title.position = "plot")
d <- read.csv("qc_usines.csv", fileEncoding = "UTF-8-BOM", check.names = FALSE)
m <- map("state", "maine", plot = FALSE, fill = TRUE)
kx <- 111.32 * cos(46 * pi / 180); ky <- 110.57; bx <- m$x * kx; by <- m$y * ky
n <- length(bx); a <- cbind(bx[-n], by[-n]); b <- cbind(bx[-1], by[-1]); keep <- complete.cases(a, b); a <- a[keep, ]; b <- b[keep, ]
dseg <- function(px, py) { ab <- b - a; t <- pmin(1, pmax(0, ((px - a[, 1]) * ab[, 1] + (py - a[, 2]) * ab[, 2]) / rowSums(ab^2)))
  min(sqrt((px - a[, 1] - t * ab[, 1])^2 + (py - a[, 2] - t * ab[, 2])^2)) }
d$km <- mapply(dseg, d$longitude * kx, d$latitude * ky)
q <- d[d$km <= 50, ]; q$kind <- ifelse(grepl("^2", q$catcomplet), "Sawmill", "Other wood mill")
nq <- nrow(q); ns <- sum(q$kind == "Sawmill")
write.csv(q[, c("usicomplet", "muncomplet", "catcomplet", "clascomplet", "latitude", "longitude", "km")], "2026-06-25_quebec-mills-within-50km-of-maine_DATA.csv", row.names = FALSE)
closed <- data.frame(
  lab = c("Millinocket\nclosed 2008", "East Millinocket\nclosed 2014", "Bucksport\nclosed 2014", "Lincoln\nclosed 2015",
          "Old Town\nclosed 2015, reopened,\nclosed again 2023", "Madison\nclosed 2016; TimberHP now\nmakes insulation there", "Jay\nclosed 2023"),
  lon = c(-68.710, -68.574, -68.795, -68.505, -68.645, -69.880, -70.216),
  lat = c(45.657, 45.627, 44.574, 45.362, 44.934, 44.798, 44.504),
  nx = c(-1.5, 1.5, 1.3, 1.6, 1.7, -1.6, -1.4), ny = c(0.45, 0.5, -0.45, 0.05, -0.15, 0.55, -0.35))
newu <- data.frame(lab = c("Ashland\nWholeTrees makes beams\nfrom whole tree trunks", "Saco\nTanbark makes food\ncontainers from wood fiber"),
  lon = c(-68.406, -70.443), lat = c(46.631, 43.501), nx = c(1.5, -1.3), ny = c(0.35, -0.2))
can <- map_data("worldHires", xlim = c(-76, -63), ylim = c(41, 50)); states <- map_data("state")
p <- ggplot() +
  geom_polygon(data = can, aes(long, lat, group = group), fill = land, colour = "white", linewidth = 0.3) +
  geom_polygon(data = states, aes(long, lat, group = group), fill = land, colour = "white", linewidth = 0.4) +
  geom_polygon(data = subset(states, region == "maine"), aes(long, lat, group = group), fill = "#DCE8DF", colour = grn, linewidth = 0.5) +
  geom_point(data = q, aes(longitude, latitude, fill = kind), shape = 21, size = 3.4, colour = "white", stroke = 0.5) +
  geom_point(data = closed, aes(lon, lat), shape = 4, size = 4.5, stroke = 2, colour = red) +
  geom_point(data = newu, aes(lon, lat), shape = 17, size = 5, colour = grn) +
  geom_label_repel(data = closed, aes(lon, lat, label = lab), size = 3.4, lineheight = 1.05, linewidth = 0.3, colour = ink, fill = "white",
                   box.padding = 0.5, point.padding = 0.6, min.segment.length = 0, seed = 7, nudge_x = closed$nx, nudge_y = closed$ny, segment.colour = gry) +
  geom_label_repel(data = newu, aes(lon, lat, label = lab), size = 3.4, lineheight = 1.05, linewidth = 0.3, colour = ink, fill = "white",
                   box.padding = 0.5, point.padding = 0.6, min.segment.length = 0, seed = 7, nudge_x = newu$nx, nudge_y = newu$ny, segment.colour = gry) +
  annotate("label", x = -73.3, y = 47.25, hjust = 0, size = 3.9, lineheight = 1.08, linewidth = 0, fill = "white", colour = nav, fontface = "bold",
           label = sprintf("Quebec: %d wood mills operate within\n30 miles of Maine, %d of them sawmills", nq, ns)) +
  annotate("text", x = -66.6, y = 46.6, label = "New Brunswick\nmills not mapped", size = 3.2, colour = gry, fontface = "italic", lineheight = 1) +
  scale_fill_manual(values = c("Sawmill" = nav, "Other wood mill" = lblu), name = NULL) +
  guides(fill = guide_legend(override.aes = list(size = 4))) +
  coord_quickmap(xlim = c(-73.6, -65.4), ylim = c(42.95, 47.75), expand = FALSE) +
  labs(title = "Maine lost its paper mills while Quebec's mills line the border",
       subtitle = "Red X marks a Maine town that lost a paper mill since 2008. Green triangles mark new uses for wood.\nBlue dots are Quebec wood mills within 30 miles of the Maine border.") + th +
  theme(legend.position = c(0.99, 0.02), legend.justification = c(1, 0), legend.background = element_rect(fill = "white", colour = NA),
        legend.text = element_text(size = 10), legend.margin = margin(4, 8, 4, 6))
ggsave("2026-11-10_maine-mill-towns-quebec-mills-map_DRAFT.png", p, width = 10, height = 7.6, dpi = 300, bg = "white")
cat(nq, ns, "done\n")
