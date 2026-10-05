# FAOSTAT Forestry (bulk normalized file, downloaded October 5, 2026 from bulks-faostat.fao.org): US export and import value of
# "Wood, pulp and paper products (export/import)" and "Primary wood and paper products (export/import)", 1961 onward, 1000 USD.
suppressMessages(library(data.table))
d <- fread("fao/Forestry_E_All_Data_(Normalized).csv", encoding = "Latin-1")
us <- d[Area == "United States of America" & Element %in% c("Export value", "Import value") &
        Item %in% c("Wood, pulp and paper products (export/import)", "Primary wood and paper products (export/import)")]
w <- dcast(us, Item + Year ~ Element, value.var = "Value")
setnames(w, c("Export value", "Import value"), c("X_kusd", "M_kusd"))
w[, ratio := X_kusd / M_kusd]
fwrite(w, "out/fao_us_forest_trade_1961_2024.csv")
print(unique(us$Unit))
for (it in unique(w$Item)) {
  x <- w[Item == it]
  cat("\n", it, "\n"); print(x[Year %in% c(1961, 1965, 1970, 1973, 1975, 1979, 1980, 1981, 1985, 1990, 1991, 2000, 2005, 2011, 2012, 2020, 2023, 2024), .(Year, X_bn = round(X_kusd / 1e6, 1), M_bn = round(M_kusd / 1e6, 1), ratio = round(ratio, 2))])
  cat("surplus years:", paste(x[ratio >= 1, Year], collapse = ", "), "\n")
}
