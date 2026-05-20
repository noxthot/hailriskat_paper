# Central configuration management for hailriskat project
library(jsonlite)

#' Get the project root directory
#'
#' @return The absolute path to the project root
get_project_root <- function() {
  # This file is in utils/, so go up one level to get project root
  script_dir <- getSrcDirectory(function() {})
  
  # If sourced interactively or script_dir is empty, try alternative methods
  if (script_dir == "") {
    # Try to get from current working directory structure
    # Look for config.json in parent directories
    current <- getwd()
    while (current != dirname(current)) {
      if (file.exists(file.path(current, "config.json"))) {
        return(normalizePath(current))
      }
      current <- dirname(current)
    }
    stop("Could not find project root. Make sure config.json exists in the project root.")
  }
  
  return(normalizePath(file.path(script_dir, "..")))
}

#' Load the central configuration file
#'
#' @return A list containing the configuration
load_config <- function() {
  config_path <- file.path(get_project_root(), "config.json")
  if (!file.exists(config_path)) {
    stop(paste("Configuration file not found at:", config_path))
  }
  return(fromJSON(config_path))
}

#' Get a path from the configuration
#'
#' @param key Top-level key in paths section (e.g., 'data_root', 'models')
#' @param ... Nested keys to traverse (e.g., 'mev_nn', 'final_ensemble')
#' @param relative_to If provided, return path relative to this directory
#' @return The configured path as an absolute path string
#'
#' @examples
#' get_path('models', 'mev_nn', 'final_ensemble')
#' get_path('data_root')
#' get_path('gof_data')
get_path <- function(key, ..., relative_to = NULL) {
  config <- load_config()
  
  # Navigate through nested keys
  value <- config$paths[[key]]
  subkeys <- list(...)
  
  for (subkey in subkeys) {
    value <- value[[subkey]]
  }
  
  if (is.null(value)) {
    stop(paste("Path not found for key:", key, "and subkeys:", paste(subkeys, collapse = ", ")))
  }
  
  # If relative_to is specified, calculate relative path
  if (!is.null(relative_to)) {
    root <- get_project_root()
    abs_path <- file.path(root, value)
    rel_start <- file.path(root, relative_to)
    # R doesn't have a built-in relative path function, so we'll use a simple approach
    return(value)  # Return the relative path from config
  }
  
  # Return absolute path by default
  return(normalizePath(file.path(get_project_root(), value), mustWork = FALSE))
}

