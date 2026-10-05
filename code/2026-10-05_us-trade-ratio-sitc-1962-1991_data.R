# SITC Rev.1 series for 1962 to 1991, to carry the export to import ratios back before HS (1988). Same API as the HS script.
# Agriculture = SITC 0 + 1 + 22 + 4 less 03 (fish). Forest products = 24 + 25 + 63 + 64. Seafood = 03.
suppressMessages({library(jsonlite); library(data.table)})
codes <- c("0", "1", "22", "4", "03", "24", "25", "63", "64")
get_year <- function(y) {
  u <- sprintf("https://comtradeapi.un.org/public/v1/preview/C/A/S1?reporterCode=842&period=%d&partnerCode=0&partner2Code=0&customsCode=C00&motCode=0&cmdCode=%s&flowCode=X,M", y, paste(codes, collapse = ","))
  for (k in 1:6) { r <- try(fromJSON(u), silent = TRUE); if (!inherits(r, "try-error") && length(r$data)) break; Sys.sleep(15) }
  if (inherits(r, "try-error") || !length(r$data)) return(NULL)
  d <- as.data.table(r$data)[, .(year = refYear, flow = flowCode, cmd = cmdCode, fob = fobvalue, primary = primaryValue)]
  Sys.sleep(8); d
}
tr <- rbindlist(lapply(1962:1991, function(y) tryCatch(get_year(y), error = function(e) NULL)))
fwrite(tr, "out/comtrade_us_raw_sitc1_1962_1991.csv")
tr[, val := fifelse(flow == "X", primary, fifelse(!is.na(fob) & fob > 0, fob, primary))]
ag <- tr[cmd %in% c("0", "1", "22", "4"), .(val = sum(val)), by = .(year, flow)]
fish <- tr[cmd == "03", .(s = sum(val)), by = .(year, flow)]
ag <- merge(ag, fish, by = c("year", "flow"))[, .(year, flow, val = val - s, sector = "Agriculture")]
fo <- tr[cmd %in% c("24", "25", "63", "64"), .(val = sum(val), sector = "Forest products"), by = .(year, flow)]
se <- tr[cmd == "03", .(val = sum(val), sector = "Seafood"), by = .(year, flow)]
w <- dcast(rbind(ag, fo, se, use.names = TRUE), year + sector ~ flow, value.var = "val")[, ratio := X / M]
fwrite(w, "out/us_trade_ratio_sitc1_1962_1991.csv")
print(w[year %in% c(1965, 1975, 1985, 1991)][, .(year, sector, X_bn = round(X/1e9,1), M_bn = round(M/1e9,1), ratio = round(ratio,2))])
