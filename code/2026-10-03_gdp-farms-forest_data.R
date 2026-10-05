suppressMessages({library(readxl); library(data.table); library(ggplot2); library(patchwork); library(scales)})
in_xlsx <- "VA.xlsx"; out_dir <- "out"; dir.create(out_dir, showWarnings = FALSE)
wl <- list(poi = "#134a31", context = "#8a948e", ink = "#14201a", muted = "#4a5750", faint = "#5f6b65", rule = "#d3dcd6")
raw <- as.data.table(suppressMessages(read_excel(in_xlsx, sheet = "TVA105-A", col_names = FALSE)))
hdr_row <- which(raw[[1]] == "Line")[1]
yrs <- as.character(unlist(raw[hdr_row, ]))
dat <- raw[(hdr_row + 1):.N]
setnames(dat, c("line", "desc", yrs[-(1:2)]))
dat[, desc := trimws(desc)]
keep <- c("Gross domestic product", "Farms", "Wood products", "Paper products", "Forestry, fishing, and related activities")
dat <- dat[desc %in% keep][!duplicated(desc)]
long <- melt(dat[, !"line"], id.vars = "desc", variable.name = "year", value.name = "va")
long[, `:=`(year = as.integer(as.character(year)), va = as.numeric(va))]
wide <- dcast(long, year ~ desc, value.var = "va")
setnames(wide, c("Farms", "Forestry, fishing, and related activities", "Gross domestic product", "Paper products", "Wood products"), c("farms", "fff", "gdp", "paper", "wood"))
wide[, forest := wood + paper]
wide <- wide[!is.na(year)]
fwrite(wide, file.path(out_dir, "bea_va_farms_forest_1997_2025.csv"))
print(wide[year %in% c(1997, 2010, 2025)])
