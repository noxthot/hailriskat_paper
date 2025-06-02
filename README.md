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


<a id="1">[1]</a> Ehrensperger, G., Meyer, V., Falkensteiner, M. & Hell, T. (2025). From Radar to Risk: Building a High-Resolution Hail Database for Austria And Estimating Risk Through the Integration of Distributional Neural Networks into the Metastatistical Framework. tba