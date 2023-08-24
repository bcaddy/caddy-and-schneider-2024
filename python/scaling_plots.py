#!/usr/bin/env python3
"""
================================================================================
 Written by Robert Caddy.

 Generates the scaling test plots. This script it largely identical
 to the same script in the `scaling-tests` repo, just optimized for this paper
================================================================================
"""

from timeit import default_timer
import numpy as np
import pandas as pd
import pathlib
import matplotlib.pyplot as plt
import shared_tools

plt.close('all')

# Settings
data_path = shared_tools.repo_root / 'scaling-tests' / 'data' / '2023-08-11'

# ==============================================================================
def main():
    scaling_data = load_data(data_path)

    Scaling_Plot(scaling_data=scaling_data,
                 y_title=r'Milliseconds / 256$^3$ Cells / GPU',
                 filename='ms_per_gpu',
                 plot_func=ms_per_256_per_gpu,
                 xlims=[0.7, 1E5],
                 ylims=[7E-3, 1E3])

    Scaling_Plot(scaling_data=scaling_data,
                 y_title=r'Cells / Second / GPU',
                 filename='cells_per_second',
                 plot_func=cells_per_second_per_gpu,
                 xlims=[0.7, 1E5],
                 ylims=[1E7, 1E9],
                 skip_mpi=True)

    shared_tools.update_plot_entry('scaling_plot', 'python/scaling_plots.py')
# ==============================================================================

# ==============================================================================
def load_data(data_path):
    # Get paths
    data_dirs = sorted(pathlib.Path(data_path).glob('ranks*'))

    # Setup dataframe
    file_name = data_dirs[0] / 'run_timing.log'
    with open(file_name, 'r') as file:
        lines        = file.readlines()
        header       = lines[3][1:].split()
        scaling_data = pd.DataFrame(index=header)

    # Loop through the directories and load the data
    for path in data_dirs:
        file_name = path / 'run_timing.log'
        if file_name.is_file():
            with open(file_name, 'r') as file:
                lines  = file.readlines()
                data   = lines[4].split()
                scaling_data[int(data[0])] = pd.to_numeric(data)
        else:
            print(f'File: {file_name} not found.')

    scaling_data = scaling_data.reindex(sorted(scaling_data.columns), axis=1)
    return scaling_data
# ==============================================================================

# ==============================================================================
def Scaling_Plot(scaling_data, y_title, filename, plot_func, xlims, ylims, skip_mpi=False):
    # Instantiate Plot
    fig = plt.figure(0)
    fig.clf()
    ax = plt.gca()

    # Set plot settings
    color_mhd       = 'blue'
    color_mpi       = 'red'
    color_total     = 'purple'
    marker_size     = 4
    font_size       = 10

    # Plot the data
    ax = plot_func(scaling_data, 'Total', color_total, 'Total', ax, marker_size)
    # Note that the timer for the integrator is named "Hydro" not "MHD"
    ax = plot_func(scaling_data, 'Hydro_Integrator', color_mhd, 'MHD', ax, marker_size)
    if (not skip_mpi):
        ax = plot_func(scaling_data, 'Boundaries', color_mpi, 'MPI Comm', ax, marker_size)

    # Setup the rest of the plot
    ax.tick_params(axis='both', which='major', direction='in' )
    ax.tick_params(axis='both', which='minor', direction='in' )

    ax.set_xlim(xlims[0], xlims[1])
    # ax.set_ylim(ylims[0], ylims[1])

    ax.set_yscale('log')
    ax.set_xscale('log')

    fig.suptitle('MHD Weak Scaling on Frontier', fontsize=1.5*font_size)
    ax.set_ylabel(y_title, fontsize=font_size)
    ax.set_xlabel(r'Number of GPUs', fontsize=font_size)

    legend = ax.legend()
    fig.tight_layout()
    5
    output_path = shared_tools.repo_root / 'assets' / '3-mhd-tests' / f'scaling_tests_{filename}.pdf'
    fig.savefig(output_path)
# ==============================================================================

# ==============================================================================
def ms_per_256_per_gpu(scaling_data, name, color, label, ax, marker_size):
    x = scaling_data.loc['n_proc'].to_numpy()
    y = scaling_data.loc[name].to_numpy() / (scaling_data.loc['n_steps'].to_numpy() - 1)

    ax.plot(x, y, '--', c=color, marker='o', markersize=marker_size, label=label)

    return ax
# ==============================================================================

# ==============================================================================
def cells_per_second_per_gpu(scaling_data, name, color, label, ax, marker_size):
    x = (scaling_data.loc['n_proc'].to_numpy())

    cells_per_gpu = ( scaling_data.loc['nx'].to_numpy()
                    * scaling_data.loc['ny'].to_numpy()
                    * scaling_data.loc['nz'].to_numpy()) / x

    avg_time_step = scaling_data.loc[name].to_numpy() / (scaling_data.loc['n_steps'].to_numpy() - 1)
    avg_time_step /= 1000 # convert to seconds from ms

    y = cells_per_gpu / avg_time_step

    ax.plot(x, y, '--', c=color, marker='o', markersize=marker_size, label=label)

    return ax
# ==============================================================================

if __name__ == '__main__':
    start = default_timer()
    main()
    print(f'Time to execute: {round(default_timer()-start,2)} seconds')
