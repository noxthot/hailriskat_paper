# Configuration System

This project uses a centralized configuration system to manage paths across Julia, Python, and R code. All paths are defined in `config.json` at the root of the project.

## Configuration File

The main configuration file is `config.json`, which contains:
- Common data paths (data root, models, results, etc.) stored as relative paths
- Output directory names

**Note:** All path functions return **absolute paths** by default, resolved from the project root. This ensures paths work correctly regardless of where code is executed from.

## Usage

### Python

```python
# Import the config module
from utils.config import get_ensemble_path, get_output_dir, get_path

# Get commonly used paths (returns absolute paths)
ensemble_path = get_ensemble_path()  # e.g., /full/path/to/data/models/mev_nn/final_ensemble
output_path = get_output_dir("current_results")

# Or build custom paths
custom_path = get_path("models", "mev_nn", "final_ensemble")
```

For Python notebooks that are in the `notebooks/` directory:
```python
import sys
import os
sys.path.insert(0, os.path.join('..'))

from utils.config import get_ensemble_path, get_results_path

# Use the paths
ensemble_path = get_ensemble_path()
results_path = get_results_path()
```

### Julia

```julia
# Include the config module (adjust path relative to your script)
include("../../utils/config.jl")

# Get commonly used paths (returns absolute paths)
ensemble_path = get_ensemble_path()  # e.g., /full/path/to/data/models/mev_nn/final_ensemble
output_path = get_output_dir("current_results")

# Or build custom paths
custom_path = get_path("models", "mev_nn", "final_ensemble")
```

### R

R support can be added by creating a `utils/config.R` file that reads the JSON config:

```r
library(jsonlite)

get_config <- function() {
  config_path <- file.path(dirname(dirname(rstudioapi::getActiveDocumentContext()$path)), "config.json")
  return(fromJSON(config_path))
}

get_ensemble_path <- function() {
  config <- get_config()
  return(config$paths$models$mev_nn$final_ensemble)
}
```

## Benefits

1. **Single Source of Truth**: All paths are defined in one place
2. **Easy Updates**: Change paths in config.json without modifying code
3. **Cross-Language Consistency**: Same paths used across Python, Julia, and R
4. **Better Maintainability**: Reduces hardcoded paths scattered throughout the codebase

## Adding New Paths

To add a new path:
1. Edit `config.json` and add your path
2. Optionally add convenience functions in the language-specific config modules
3. Use the new path in your code

## Current Configured Paths

- **Ensemble Model Path**: `data/models/mev_nn/final_ensemble`
- **Results Directory**: `data/models/mev_nn/final_ensemble/results`
- **Output Directories**:
  - Current results: `data/models/mev_nn/final_ensemble/results_output`
  - Bootstrap null: `data/models/mev_nn/final_ensemble/results_bootstrap_null`
