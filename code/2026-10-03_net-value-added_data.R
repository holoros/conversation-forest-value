# Net value added (SNA sense): BEA gross value added less current-cost depreciation (consumption of fixed capital)
# of private nonresidential fixed assets, by industry. Subsidies are already netted out of BEA value added
# (taxes on production and imports less subsidies). Inputs:
#   out/bea_va_farms_forest_1997_2025.csv (from 2026-10-03_gdp-farms-forest_data.R)
#   detailnonres_dep1.xlsx  https://apps.bea.gov/national/FA2004/Details/xls/detailnonres_dep1.xlsx (updated September 30, 2026)
#   MESA_VA.xlsx            BEA Marine Economy Satellite Account, value added by activity
#   VA.xlsx                 BEA GDP by Industry TVA105-A (for seafood proxy ratios)
suppressMessages({library(readxl); library(data.table)})
dep_file <- "detailnonres_dep1.xlsx"
get_dep <- function(code) {
  x <- as.data.table(suppressMessages(read_excel(dep_file, sheet = code, col_names = FALSE)))
  hr <- which(x[[2]] == "NIPA Asset Types")[1]
  yrs <- as.integer(unlist(x[hr, -(1:2)]))
  tot <- x[grepl("^TOTAL (EQUIPMENT|STRUCTURES|INTELLECTUAL)", toupper(trimws(x[[2]])))]
  stopifnot(nrow(tot) == 3)
  data.table(code = code, year = yrs, dep = colSums(sapply(tot[, -(1:2)], as.numeric)))
}
dep <- dcast(rbindlist(lapply(c("110C", "113F", "3210", "3220", "3110", "3120"), get_dep)), year ~ code, value.var = "dep")
fwrite(dep, "out/bea_depreciation_by_industry_1925_2025.csv")
wide <- fread("out/bea_va_farms_forest_1997_2025.csv")[!is.na(year)]
raw <- as.data.table(suppressMessages(read_excel("VA.xlsx", sheet = "TVA105-A", col_names = FALSE)))
hr <- which(raw[[1]] == "Line")[1]; yrs <- as.character(unlist(raw[hr, ])); d <- raw[(hr + 1):.N]
setnames(d, c("line", "desc", yrs[-(1:2)])); d[, desc := trimws(desc)]
food <- melt(d[desc == "Food and beverage and tobacco products"][1, !"line"], id.vars = "desc", variable.name = "year", value.name = "food_va")
food[, `:=`(year = as.integer(as.character(year)), food_va = as.numeric(food_va), desc = NULL)]
x <- merge(merge(wide, dep, by = "year"), food, by = "year")
# depreciation ratios used as proxies for seafood (BEA publishes no marine economy depreciation)
x[, `:=`(r_fish = `113F` / fff, r_food = (`3110` + `3120`) / food_va)]
forest <- x[, .(year, sector = "Forest products", gva = forest, dep = `3210` + `3220`, method = "BEA depreciation, wood (3210) plus paper (3220)")]
farms  <- x[, .(year, sector = "Farms", gva = farms, dep = `110C`, method = "BEA depreciation, farms (110C)")]
m <- as.data.table(suppressMessages(read_excel("MESA_VA.xlsx", sheet = "VA", col_names = FALSE)))
my <- as.integer(unlist(m[3, -(1:2)]))
row <- function(lbl) as.numeric(unlist(m[trimws(m[[2]]) == lbl][1, -(1:2)]))
sea <- data.table(year = my, harvest = row("Commercial harvest and seafood markets"), proc = row("Seafood processing"))
sea <- merge(sea, x[, .(year, r_fish, r_food)], by = "year")
seafood <- sea[, .(year, sector = "Seafood", gva = harvest + proc, dep = harvest * r_fish + proc * r_food,
                   method = "Proxy: harvest and markets at the forestry, fishing and related (113F) depreciation ratio, processing at the food and beverage manufacturing ratio")]
out <- rbind(forest, farms, seafood)[, nva := gva - dep][, dep_share := dep / gva]
fwrite(out, "out/bea_net_value_added_farms_forest_seafood.csv")
print(out[year %in% c(2014, 2022, 2023, 2025), .(year, sector, gva = round(gva / 1e3, 1), dep = round(dep / 1e3, 1), nva = round(nva / 1e3, 1), dep_share = round(dep_share, 3))][order(sector, year)])
