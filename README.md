# From Radar to Risk: Building a High-Resolution Hail Database for Austria And Estimating Risk Through the Integration of Distributional Neural Networks into the Metastatistical Framework

[![DOI](https://zenodo.org/badge/???ID???.svg)](https://zenodo.org/badge/latestdoi/???ID???)

This is the source code belonging to the paper of the same name [[1]](#1).


## Authors of this Source Code
- [Gregor Ehrensperger](https://github.com/noxthot) [![ORCID iD](https://orcid.org/sites/default/files/images/orcid_16x16.png)](https://orcid.org/0000-0003-4816-0233)

- [Marc-André Falkensteiner](https://github.com/Falke96) [![ORCID iD](https://orcid.org/sites/default/files/images/orcid_16x16.png)](https://orcid.org/0000-0002-6887-405X)


## Setup
### Julia
#### Instantiating the project
Open julia (we currently use the latest patch of `1.11`) inside this folder, then

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

## Documentation
### Overview
This repository contains the source code for the paper [[1]](#1) which is used to calculate the hail risk in Austria and to generate the figures of the paper.
The code is organized like this:
- `./ccc/`: Contains globally used constants.
- `./era5_retrieval/`: Contains code to retrieve cape from ERA5.
- `./etl_pipelines/`: Reads ALDIS, INCA, radar and ERA5 data, processes it by bringing it to the same 1km x 1km grid scale and stores the transformed data in `./data/processed_data`.
- `./models/mev_nn/`: Contains the code to fit the distributional neural networks (DNNs) and calculate the return levels using the spatio-temporal metastatistical framework.
- `./models/mev_pointwise/`: Contains the code to compute the return levels by applying the metastatistical model separately on each grid point.
- `./notebooks/`: Contains the Jupyter notebooks used to generate the figures of the paper.
- `./utils/`: Contains utility functions used in the code.


### How to
#### Prepare data and data preprocessing
- Provide the raw data (ALDIS, ERA5, INCA, radar) in the `./data/raw_data/` folder.
- Run `etl.py` (Python) to process the data and store it in `./data/processed_data/`.

#### Calculate return levels
##### Pointwise metastatistical model
- Run `./models/mev_pointwise/mev_pointwise.py` (Python) to fit the pointwise metastatistical model, calculate the return levels and plot the results.

##### Spatio-temporal metastatistical model
- Run `./models/mev_nn/mev_nn_fit_model.jl` (Julia) to fit the distributional neural network.
- Run `./models/mev_nn/mev_nn_calculate_return_levels.jl` (Julia) to calculate the return levels using the fitted distributional neural network.

##### Ensemble of spatio-temporal metastatistical models
- Run `./models/mev_nn/mev_nn_fit_model_ensemble.jl` (Julia) to fit an ensemble of distributional neural networks.
- Run `./models/mev_nn/mev_nn_calculate_return_levels_ensemble.jl` (Julia) to calculate the return levels using the ensemble of fitted distributional neural networks.

** Note: this is what is used within the paper **

#### Generate paper figures
Prerequisites: Preprocessed data and computed return levels are available (see steps above).
- Figure 4 (maximum observed hail stone): tba
- Figure 5 (hailstone size frequency): Run Notebook `./notebooks/empirical_mehs_return_levels.ipynb` (Python) using Jupyter.
- Figure 6 (return levels of hailstone sizes as estimated by the TMEV approach using bootstrapping on the ensemble): tba
- Figure 7 (return periods of hailstone sizes as estimated by the TMEV approach using bootstrapping on the ensemble): tba
- Figure 8 (empirical hailstone size return levels): tba
- Appendix Figure 1 (qq plot): tba
- Appendix Figure 2 (diagnostic plots using Weibull on raw data): tba
- Appendix Figure 3 (diagnostic plots using Weibull on dithered data): tba 
- Appendix Figure 5 (number of observed hail days): Run Notebook `./notebooks/haildays.ipynb` (Python) using Jupyter.


## References
<a id="1">[1]</a> Ehrensperger, G., Meyer, V., Falkensteiner, M. & Hell, T. (2025). From Radar to Risk: Building a High-Resolution Hail Database for Austria And Estimating Risk Through the Integration of Distributional Neural Networks into the Metastatistical Framework. tba