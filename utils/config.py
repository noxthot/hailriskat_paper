"""Central configuration management for hailriskat project."""
import json
import os
from pathlib import Path
from typing import Any, Dict


def get_project_root() -> Path:
    """Get the project root directory."""
    # This file is in utils/, so go up one level to get project root
    return Path(__file__).parent.parent


def load_config() -> Dict[str, Any]:
    """Load the central configuration file."""
    config_path = get_project_root() / "config.json"
    with open(config_path, 'r') as f:
        return json.load(f)


def get_path(key: str, *subkeys, relative_to: str | None = None) -> str:
    """
    Get a path from the configuration.
    
    Args:
        key: Top-level key in paths section (e.g., 'data_root', 'models')
        subkeys: Nested keys to traverse (e.g., 'mev_nn', 'final_ensemble')
        relative_to: If provided, return path relative to this directory
        
    Returns:
        The configured path as an absolute path string
        
    Examples:
        >>> get_path('models', 'mev_nn', 'final_ensemble')
        '/path/to/project/data/models/mev_nn/final_ensemble'
        
        >>> get_path('data_root')
        '/path/to/project/data'
    """
    config = load_config()
    
    # Navigate through nested keys
    value = config['paths'][key]
    for subkey in subkeys:
        value = value[subkey]
    
    # If relative_to is specified, calculate relative path
    if relative_to:
        root = get_project_root()
        abs_path = root / value
        rel_start = root / relative_to
        return os.path.relpath(abs_path, rel_start)
    
    # Return absolute path by default
    return str(get_project_root() / value)


def get_output_dir(key: str) -> str:
    """
    Get an output directory path from configuration.
    
    Args:
        key: Key in output_directories section
        
    Returns:
        The configured directory path as an absolute path string
        
    Example:
        >>> get_output_dir('current_results')
        '/path/to/project/data/models/mev_nn/final_ensemble/results_2nd_revision'
    """
    config = load_config()
    path = config['output_directories'][key]
    # Return absolute path by default
    return str(get_project_root() / path)


# Convenience functions for commonly used paths
def get_data_root() -> str:
    """Get the data root directory path."""
    return get_path('data_root')


def get_ensemble_path() -> str:
    """Get the final ensemble model path."""
    return get_path('models', 'mev_nn', 'final_ensemble')


def get_results_path() -> str:
    """
    Get the results directory path.
    """
    return get_path('models', 'mev_nn', 'results')
