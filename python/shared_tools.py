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
import os

# ==============================================================================
# Variables that are commonly used across many scripts
# ==============================================================================

# Repo Root Path
repo_root = pathlib.Path(__file__).resolve().parent.parent

# The path to the pickled dictionary
pickle_filepath = repo_root / 'python' / 'links.pkl'

# Path to data files
data_files_path = repo_root / 'data'

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
# Various useful functions
# ==============================================================================
# ==============================================================================
def cholla_runner(exe_path: pathlib.Path = repo_root / 'cholla' / 'bin',
                  reconstructor: str = 'ppmc',
                  param_file_name: str = 'blank_settings_file.txt',
                  cholla_cli_args: str = '' ,
                  move_initial: bool = False,
                  move_final: bool = False,
                  initial_filename: str = 'initial',
                  final_filename: str = 'final') -> None:
    """Run cholla with the given parameters and organize/clear the resulting files

    Args:
        exe_path (pathlib.Path, optional): The path to the directory that contains the Cholla executable. Defaults to repo_root/'cholla'/'bin'.
        reconstructor (str, optional): The reconstructor to use. Allows 'ppmc' or 'plmc'. Defaults to 'ppmc'.
        param_file_name (str, optional): The name of the parameter file to use. Defaults to 'blank_settings_file.txt'.
        cholla_cli_args (str, optional): The CLI arguments to pass to Cholla. Defaults to ''.
        move_initial (bool, optional): If True move the initial conditions file, if false delete it. Defaults to False.
        move_final (bool, optional): If True move the final conditions file, if false delete it.. Defaults to False.
        initial_filename (str, optional): The new name of the initial conditions file. Defaults to 'initial'.
        final_filename (str, optional): The new name of the final conditions file. Defaults to 'final'.
    """

    if not (reconstructor == 'ppmc' or reconstructor == 'plmc'):
        raise ValueError("reconstructor argument can only be 'ppmc' or 'plmc'")

    # Generate Cholla run command
    cholla_path = exe_path / f'cholla.mhd.c3po.{reconstructor}'
    param_file_path = repo_root / 'python' / 'cholla-config-files' / param_file_name
    log_file = repo_root / 'cholla.log'

    command = f'{cholla_path} {param_file_path} {cholla_cli_args} >> {log_file} 2>&1'

    # Run Cholla
    os.system(command)

    # Move or delete data files
    data_source_dir = repo_root / 'python'
    initial_data = data_source_dir / '0.h5.0'
    final_data = data_source_dir / '1.h5.0'

    if move_initial:
        initial_data.rename(data_files_path / f'{initial_filename}.h5')
    else:
        initial_data.unlink()

    if move_final:
        final_data.rename(data_files_path / f'{final_filename}.h5')
    else:
        final_data.unlink()

    (data_source_dir / 'run_output.log').unlink()
    (data_source_dir / 'run_timing.log').unlink()
# ==============================================================================

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