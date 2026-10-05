# Per hectare cross check of the sector comparison using global unit values (benefit transfer, order of magnitude only).
# Costanza et al. 2014, Global Environmental Change 26:152-158, Figure S1 table (UCL Discovery preprint p. 17): 2011 flow value,
# 2007 USD per ha per year: temperate/boreal forest 3,013; cropland 126; marine shelf 2,222; open ocean 491.
# US areas: forest land 663.7 million acres (Arkansas Center for Forest Business 2023, from FIA); cropland 377 million acres in 2022 (USDA ERS Major Land Uses).
suppressMessages(library(data.table))
ac2ha <- 0.404686
x <- data.table(sector = c("Forest", "Agriculture (cropland)"), area_Mac = c(663.7, 377), usd_ha = c(3013, 126))
x[, `:=`(area_Mha = area_Mac * ac2ha, total_bn_2007usd = area_Mac * ac2ha * usd_ha / 1e3)]
x[, ratio_to_cropland := total_bn_2007usd / x[2, total_bn_2007usd]]
fwrite(x, "out/costanza2014_us_crosscheck.csv"); print(x)
