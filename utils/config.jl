"""
Central configuration management for hailriskat project (Julia).
"""

using JSON


"""
    get_project_root()

Get the project root directory.
"""
function get_project_root()
    # Get the directory containing this script and go up one level
    return dirname(dirname(@__FILE__))
end


"""
    load_config()

Load the central configuration file.
"""
function load_config()
    config_path = joinpath(get_project_root(), "config.json")
    return JSON.parsefile(config_path)
end


"""
    get_path(key::String, subkeys::String...; relative_to::Union{String, Nothing}=nothing)

Get a path from the configuration.

# Arguments
- `key::String`: Top-level key in paths section (e.g., 'data_root', 'models')
- `subkeys::String...`: Nested keys to traverse (e.g., 'mev_nn', 'final_ensemble')
- `relative_to::Union{String, Nothing}`: If provided, return path relative to this directory

# Returns
- The configured path as an absolute path string (or relative if relative_to is specified)

# Examples
```julia
get_path("models", "mev_nn", "final_ensemble")
# Returns: "/full/path/to/data/models/mev_nn/final_ensemble"

get_path("data_root")
# Returns: "/full/path/to/data"
```
"""
function get_path(key::String, subkeys::String...; relative_to::Union{String, Nothing}=nothing)
    config = load_config()

    # Navigate through nested keys
    value = config["paths"][key]
    for subkey in subkeys
        value = value[subkey]
    end

    # If relative_to is specified, calculate relative path
    if !isnothing(relative_to)
        root = get_project_root()
        abs_path = joinpath(root, value)
        rel_start = joinpath(root, relative_to)
        return relpath(abs_path, rel_start)
    end

    # Return absolute path by default
    return joinpath(get_project_root(), value)
end


"""
    get_output_dir(key::String)

Get an output directory path from configuration.

# Arguments
- `key::String`: Key in output_directories section

# Returns
- The configured directory path as an absolute path string

# Example
```julia
get_output_dir("current_results")
# Returns: "/full/path/to/data/models/mev_nn/final_ensemble/results_2nd_revision"
```
"""
function get_output_dir(key::String)
    config = load_config()
    path = config["output_directories"][key]
    # Return absolute path by default
    return joinpath(get_project_root(), path)
end


# Convenience functions for commonly used paths

"""
    get_data_root()

Get the data root directory path.
"""
function get_data_root()
    return get_path("data_root")
end


"""
    get_ensemble_path()

Get the final ensemble model path.
"""
function get_ensemble_path()
    return get_path("models", "mev_nn", "final_ensemble")
end


"""
    get_results_path()

Get the results directory path.
"""
function get_results_path()
    return get_path("models", "mev_nn", "results")
end
