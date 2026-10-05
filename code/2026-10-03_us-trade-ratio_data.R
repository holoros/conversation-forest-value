suppressMessages({library(jsonlite); library(data.table)})
codes <- c(sprintf("%02d", 1:24), "44", "47", "48", "1604", "1605")
get_year <- function(y) {
  u <- sprintf("https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=842&period=%d&partnerCode=0&partner2Code=0&customsCode=C00&motCode=0&cmdCode=%s&flowCode=X,M", y, paste(codes, collapse = ","))
  for (k in 1:6) { r <- try(fromJSON(u), silent = TRUE); if (!inherits(r, "try-error") && length(r$data)) break; Sys.sleep(15) }
  d <- as.data.table(r$data)[, .(year = refYear, flow = flowCode, cmd = cmdCode, fob = fobvalue, primary = primaryValue)]
  Sys.sleep(8); d
}
tr <- rbindlist(lapply(2014:2025, function(y) tryCatch(get_year(y), error=function(e) NULL)))
fwrite(tr, "out/comtrade_us_raw_2014_2024.csv")
tr[, val := fifelse(flow == "X", primary, fifelse(fob > 0, fob, primary))]
tr[, sector := fcase(cmd %in% c("03", "1604", "1605"), "Seafood",
                     cmd %in% c("44", "47", "48"), "Forest products",
                     default = "Agriculture")]
# Agriculture = HS 01-24 minus seafood (03 whole; 1604/1605 sit inside 16)
ag <- tr[cmd %in% sprintf("%02d", 1:24) & cmd != "03", .(val = sum(val)), by = .(year, flow)]
s16 <- tr[cmd %in% c("1604", "1605"), .(s = sum(val)), by = .(year, flow)]
ag <- merge(ag, s16, by = c("year", "flow"))[, .(year, flow, val = val - s, sector = "Agriculture")]
oth <- tr[sector != "Agriculture", .(val = sum(val)), by = .(year, flow, sector)]
all <- rbind(ag, oth, use.names = TRUE)
w <- dcast(all, year + sector ~ flow, value.var = "val")
w[, ratio := X / M]
fwrite(w, "out/us_trade_ratio_2014_2024.csv")
print(w[year %in% c(2014, 2019, 2024)][, .(year, sector, X_bn = round(X/1e9,1), M_bn = round(M/1e9,1), ratio = round(ratio,2))])
