# Combine the HS pulls (1991 to 2013 and 2014 to 2025) into one export to import ratio series. Imports use fob where reported, else primary (CIF).
suppressMessages(library(data.table))
rd <- function(f) { d <- fread(f, colClasses = list(character = "cmd")); d[, cmd := ifelse(nchar(cmd) == 1, paste0("0", cmd), cmd)]; d }
tr <- rbind(rd("out/comtrade_us_raw_1988_2013.csv"), rd("out/comtrade_us_raw_2014_2024.csv"))
tr[, val := fifelse(flow == "X", as.numeric(primary), fifelse(!is.na(fob) & fob > 0, as.numeric(fob), as.numeric(primary)))]
ag <- tr[cmd %in% sprintf("%02d", 1:24) & cmd != "03", .(val = sum(val)), by = .(year, flow)]
s16 <- tr[cmd %in% c("1604", "1605"), .(s = sum(val)), by = .(year, flow)]
ag <- merge(ag, s16, by = c("year", "flow"))[, .(year, flow, val = val - s, sector = "Agriculture")]
fo <- tr[cmd %in% c("44", "47", "48"), .(val = sum(val), sector = "Forest products"), by = .(year, flow)]
se <- tr[cmd %in% c("03", "1604", "1605"), .(val = sum(val), sector = "Seafood"), by = .(year, flow)]
w <- dcast(rbind(ag, fo, se, use.names = TRUE), year + sector ~ flow, value.var = "val")[, ratio := X / M][order(sector, year)]
fwrite(w, "out/us_trade_ratio_hs_1991_2025.csv")
print(w[, .(year, sector, X_bn = round(X/1e9,1), M_bn = round(M/1e9,1), ratio = round(ratio,2))][year %in% c(1991, 1995, 2000, 2005, 2010, 2013, 2015, 2019, 2024, 2025)])
print(w[, .(first_deficit_year = min(year[ratio < 1]), years_surplus = sum(ratio >= 1), n = .N), by = sector])
# Splice SITC Rev.1 (1981 to 1990; the public API returned nothing for 1962 to 1980) ahead of HS (1991 on). 1991 overlap: ag 1.64 vs 1.59, forest 1.01 vs 1.00.
s1 <- fread("out/us_trade_ratio_sitc1_1962_1991.csv")[year < 1991][, class := "SITC1"]
full <- rbind(s1, w[, class := "HS"], use.names = TRUE)[order(sector, year)]
fwrite(full, "out/us_trade_ratio_1981_2025.csv")
print(full[, .(first_year = min(year), surplus_years = sum(ratio >= 1), balance_or_better = paste(year[ratio >= 0.995], collapse = ", ")), by = sector])
