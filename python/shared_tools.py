#!/usr/bin/env python3
"""
================================================================================
 Written by Robert Caddy.

 This contains the various shared tools that the python scripts will use
================================================================================
"""

import pathlib
import pickle
import subprocess

# ==============================================================================
# Variables that are commonly used across many scripts
# ==============================================================================

# The path to the pickled dictionary
pickle_filepath = pathlib.Path(__file__).resolve().parent / 'links.pkl'

# The root GitHub URL
github_url_root = 'https://github.com/bcaddy/caddy-et-al-2023/blob'

# The titles of plots with their pretty formatting
pretty_names = {'density':'Density',
                'pressure':'Pressure',
                'energy':'Energy',
                'velocity_x':'$V_x$',
                'velocity_y':'$V_y$',
                'velocity_z':'$V_z$',
                'magnetic_x':'$B_x$',
                'magnetic_y':'$B_y$',
                'magnetic_z':'$B_z$',
                'magnetic_energy':'Magnetic Energy',
                'spec_kinetic':'Specific Kinetic Energy',
                'fast_magnetosonic':'Fast Magnetosonic Wave',
                'slow_magnetosonic':'Slow Magnetosonic Wave',
                'alfven_wave':r'Alfvén Wave',
                'mhd_contact_wave':'Entropy Wave',
                'b&w':'Brio & Wu',
                'd&w':'Dai & Woodward',
                'einfeldt':'Einfeldt Strong Rarefaction',
                'rj1a':'Ryu & Jones 1a',
                'rj4d':'Ryu & Jones 4d'}
# ==============================================================================
# This next section is all the functions for pickling and unpickling the
# dictionary that is used in the LaTeX for links
# ==============================================================================
def pickle_dictionary(dictionary: dict, path: pathlib.Path = pickle_filepath) -> None:
    """Save a dictionary to a Pickle file

    Args:
        dictionary (dict): The dictionary to save
        path (pathlib.Path, optional): The path to the pickle file. Defaults to pickle_filepath.
    """
    with open(path, 'wb') as file:
        pickle.dump(dictionary, file)
# ==============================================================================

# ==============================================================================
def unpickle_dictionary(path: pathlib.Path = pickle_filepath) -> dict:
    """Unpickle a pickled dictionary

    Args:
        path (pathlib.Path, optional): The path to the dictionary to unpickle. Defaults to pickle_filepath.

    Returns:
        dict: The dictionary that was unpickled
    """
    if path.exists():
        with open(path, 'rb') as file:
            return pickle.load(file)
    else:
        return {}
# ==============================================================================

# ==============================================================================
def update_plot_entry(key: str, script_name: str) -> None:
    """Update the pickled dictionary used by LaTeX to show links.

    Args:
        key (str): The key of the new or updated entry
        script_name (str): The value of the new or updated entry. Should be the name of the python script
    """
    data = unpickle_dictionary()

    commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
    link = f'{github_url_root}/{commit_hash}/{script_name}'

    data[key] = link

    pickle_dictionary(data)
# ==============================================================================