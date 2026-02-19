#%%
library("fitdistrplus")


#%%
data_path <- file.path("data", "gof_data")
data_full <- read.csv(file.path(data_path, "data_full.csv"))

output_folder <- file.path(data_path, "gof_results")
dir.create(output_folder, recursive=TRUE, showWarnings=FALSE)


#%%
selections <- c("orig", "dith_naive")

sel_data_vec <- list(
  "orig"=data_full$target,
  "dith_naive"=data_full$target_dithered
)


#%% Plot CDF of sel_data
for (selection in selections) {
  sel_data <- getElement(sel_data_vec, selection)
  
  pdf(file.path(output_folder, paste0("cdf_", selection, ".pdf")))
  plot(ecdf(sel_data), main=paste("CDF of", selection), xlab="Value", ylab="ECDF")
  dev.off()
}


#%%
for (selection in selections) {
  sel_data <- getElement(sel_data_vec, selection)

  expfit <- fitdist(sel_data, "exp")
  gammafit <- fitdist(sel_data, "gamma")
  weibullfit <- fitdist(sel_data, "weibull")
  
  pdf(file.path(output_folder, paste0("qqplot_", selection, ".pdf")))
  qqcomp(list(expfit, gammafit, weibullfit), legendtext=c("exp", "gamma", "weibull"), xlab="Theoretical Quantiles [mm]", ylab="Empirical Quantiles [mm]", main=paste("QQ Plot", selection), xlim=c(0, 100), ylim=c(0, 100))
  dev.off()
  
  sink(file.path(output_folder, paste0("gofstats_", selection, ".txt")))
  cat("Goodness-of-fit statistics for Exponential distribution:\n")
  print(gofstat(expfit))
  cat("\n---")
  print(expfit)
  cat("\n\n")
  
  cat("Goodness-of-fit statistics for Gamma distribution:\n")
  print(gofstat(gammafit))
  cat("\n---")
  print(gammafit)
  cat("\n\n")
  
  cat("Goodness-of-fit statistics for Weibull distribution:\n")
  print(gofstat(weibullfit))
  cat("\n---")
  print(weibullfit)
  cat("\n\n")
  sink()
  
  pdf(file.path(output_folder, paste0("gof_expfit_", selection, ".pdf")))
  plot(expfit)
  dev.off()
  
  pdf(file.path(output_folder, paste0("gof_gammafit_", selection, ".pdf")))
  plot(gammafit)
  dev.off()
  
  pdf(file.path(output_folder, paste0("gof_weibullfit_", selection, ".pdf")))
  plot(weibullfit)
  dev.off()
}

#%% Plot histogram of orig data
selection <- selections[1]
sel_data <- getElement(sel_data_vec, selection)
pdf(file.path(output_folder, paste0("histogram_", selection, ".pdf")))
hist(sel_data, main=paste("Histogram of", selection), xlab="Value", ylab="Frequency", breaks=30)
dev.off()

# Bin the data into width of 10 and output counts
bin_width <- 10
breaks <- seq(0, ceiling(max(sel_data) / bin_width) * bin_width, by=bin_width)
binned <- cut(sel_data, breaks=breaks, right=FALSE)
counts <- table(binned)
print(counts)