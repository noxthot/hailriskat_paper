# HailRiskAT

Hail Risk Maps for Austria


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