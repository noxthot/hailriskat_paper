# From Radar to Risk: Building a High-Resolution Hail Database for Austria And Estimating Risk Through the Integration of Distributional Neural Networks into the Metastatistical Framework

[![DOI](https://zenodo.org/badge/993841796.svg)](https://zenodo.org/badge/latestdoi/993841796)

This is the source code belonging to the paper of the same name [[1]](#1).


## Authors of this Source Code
- [Gregor Ehrensperger](https://github.com/noxthot) [![ORCID iD](https://orcid.org/sites/default/files/images/orcid_16x16.png)](https://orcid.org/0000-0003-4816-0233)

- [Marc-André Falkensteiner](https://github.com/Falke96) [![ORCID iD](https://orcid.org/sites/default/files/images/orcid_16x16.png)](https://orcid.org/0000-0002-6887-405X)


## Setup
### Julia
#### Instantiating the project
Open julia (we currently use `1.11`) inside this folder, then

```julia
pkg>activate .  # use ']' to open the Pkg REPL
pkg>instantiate
# exit with backspace or CTRL+C
```

This creates a separate environment for the packages for this project and installs the exact versions.

### Python
We currently use `Python 3.10`.

#### PDM
Use `pdm` to install/sync all required modules:
```bash
pdm sync
```

To run code / `IPython` / `jupyter lab` in this environment:
```bash
pdm run python <SCRIPT.py>

pdm run ipython

pdm run jupyter lab
```

To add a package:
```bash
pdm add <PACKAGE_NAME>
```


### R
#### rig
We use [rig](https://github.com/r-lib/rig) to manage the R version.

To install `rig` on Ubuntu:
```bash
curl -Ls https://github.com/r-lib/rig/releases/download/latest/rig-linux-latest.tar.gz |
  sudo tar xz -C /usr/local
```

We are working with `4.5.0`, so we add this version:
```bash
rig add 4.5.0
```

Launch this specific version with:
```bash
R-4.5.0
```

#### renv
Use renv to install all required R modules from `renv.lock`: 
```r
renv::restore()
```

After manually adding a package (by updating `DESCRIPTION`), update the `renv.lock` using this command:
```r
renv::init() 
```
and choosing
```
2: Discard the lockfile and re-initialize the project.
```


## Documentation
### Overview
This repository contains the source code for the paper [[1]](#1) which is used to calculate the hail risk in Austria and to generate the figures of the paper.
The code is organized like this:
- `./ccc/`: Contains globally used constants.
- `./era5_retrieval/`: Contains code to retrieve cape from ERA5.
- `./etl_pipelines/`: Reads ALDIS, INCA, radar and ERA5 data, processes it by bringing it to the same 1km x 1km grid scale and stores the transformed data in `./data/processed_data`.
- `./models/mev_nn/`: Contains the code to fit the distributional neural networks (DNNs) and calculate the return levels using the spatio-temporal metastatistical framework.
- `./notebooks/`: Contains the Jupyter notebooks used to generate most of the figures of the paper.
- `./utils/`: Contains utility functions used in the code.
- `etl.py`: The main entry point for the ETL (Extract, Transform, Load) process to prepare the data.
- `gof.R`: Contains the code related to goodness-of-fit tests and diagnostic plots.

To summarize: Python is used for data preprocessing and plotting the resulting maps.
The metastatistical framework with its distributional neural network core is implemented in Julia, and R is used for goodness-of-fit tests and diagnostic plots regarding the choice of distribution describing the ordinary events (hailstone sizes).

### How to
#### Prepare data and data preprocessing (1)
- Provide the raw data (ALDIS, ERA5, INCA, radar) in the `./data/raw_data/` folder.
- Run `etl.py` (Python; uses `./etl_pipelines/`) to process the data and store it in `./data/processed_data/`.

#### Calculate return levels (2)
- Within Julia REPL, start Pluto:
```julia
using Pluto
Pluto.run()
```
- Open and run `./models/mev_nn/1_mev_nn_fit_model_ensemble.jl` (Julia) to fit an ensemble of distributional neural networks.
- Open and run `./models/mev_nn/2a_mev_nn_calculate_return_levels_ensemble.jl` (Julia) to calculate the return levels using the metastatistical approach with an ensemble of fitted distributional neural networks in its core.
- Open and run `./models/mev_nn/2b_mev_nn_calculate_return_periods_ensemble.jl` (Julia) to calculate the return periods using the metastatistical approach with an ensemble of fitted distributional neural networks in its core.
- Open and run `./models/mev_nn/3_bootstrap.jl` (Julia) to bootstrap the resulting return levels and periods of the ensemble model.


#### Generate data set for goodness-of-fit tests (3)
This step is a bit hacky since it would make more sense to simply also use (1) directly; however, this was implemented faster.
- Open `./models/mev_nn/1_mev_nn_fit_model_ensemble.jl` (Julia) and check `export data` to generate a data set for the goodness-of-fit tests.

#### Generate figures used in the paper
Prerequisites: Preprocessed data (1) and computed return levels (2) are available (see steps above).
- Figure 4 (maximum observed hailstone size; requires (1)): Run notebook `./notebooks/hail_eda.ipynb` (Python) using Jupyter.
- Figure 5 (hailstone size frequency; requires (1)): Run notebook `./notebooks/hail_eda.ipynb` (Python) using Jupyter.
- Figure 6 (return levels of hailstone sizes as estimated by the TMEV approach using bootstrapping on the ensemble; requires (2)): Run notebook `./notebooks/mev_nn_plot_return_levels_ensemble.ipynb` (Python) using Jupyter.
- Figure 7 (return periods of hailstone sizes as estimated by the TMEV approach using bootstrapping on the ensemble; requires (2)): Run notebook `./notebooks/mev_nn_plot_return_levels_ensemble.ipynb` (Python) using Jupyter.
- Figure 8 (empirical hailstone size return levels; requires (1)): Run notebook `./notebooks/hail_eda.ipynb` (Python) using Jupyter.
- Figure A.1 (qq plot; requires (3)): Run `./gof.R` (R).
- Figure A.2 (diagnostic plots using Weibull on raw data; requires (3)): Run `./gof.R` (R).
- Figure A.3 (diagnostic plots using Weibull on dithered data; requires (3)): Run `./gof.R` (R). 
- Figure B.2 (number of observed hail days; requires (3)): Run Notebook `./notebooks/hail_eda.ipynb` (Python) using Jupyter.


## References
<a id="1">[1]</a> Ehrensperger, G., Meyer, V., Falkensteiner, M. & Hell, T. (2025). From Radar to Risk: Building a High-Resolution Hail Database for Austria And Estimating Risk Through the Integration of Distributional Neural Networks into the Metastatistical Framework. tba
