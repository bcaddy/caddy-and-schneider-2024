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
import matplotlib
import matplotlib.ticker
import matplotlib.pyplot as plt
import argparse
import shared_tools

matplotlib.use("Agg")
plt.style.use('seaborn-v0_8-colorblind')

# axes_color = '0.1'
# plt.rcParams['axes.facecolor']    = axes_color
# plt.rcParams['figure.facecolor']  = background_color
# plt.rcParams['patch.facecolor']   = background_color
# plt.rcParams['savefig.facecolor'] = background_color

matplotlib.rcParams['font.sans-serif'] = "Helvetica"
matplotlib.rcParams['font.family'] = "sans-serif"
matplotlib.rcParams['mathtext.fontset'] = 'cm'
matplotlib.rcParams['mathtext.rm'] = 'serif'

plt.close('all')

# ==============================================================================
def main():
    data_path = shared_tools.repo_root / 'scaling-tests' / 'data' / '2024-03-13-fused-pcm'
    data_path_strong = shared_tools.repo_root / 'scaling-tests' / 'data' / '2024-03-23-strong-scaling'

    # Check for CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--weak',   action="store_true", help='Generate the weak scaling plots')
    parser.add_argument('-s', '--strong', action="store_true", help='Generate the strong scaling plot')
    args = parser.parse_args()

    if args.weak:
        scaling_data = load_data(data_path)

        cells_per_second_plot(scaling_data)
        weak_scaling_efficiency(scaling_data)
        ms_per_timestep(scaling_data)

        shared_tools.update_plot_entry('scaling', 'python/scaling_plots.py')

    if args.strong:
        strong_scaling(data_path_strong)
        shared_tools.update_plot_entry('strong-scaling', 'python/scaling_plots.py')
# ==============================================================================

# ==============================================================================
def load_data(data_path):
    # Get paths
    data_dirs = sorted(pathlib.Path(data_path).glob('ranks*'))

    # Setup dataframe
    file_name = data_dirs[0] / 'run_timing.log'
    with open(file_name, 'r') as file:
        lines        = file.readlines()
        header       = lines[5][1:].split()
        scaling_data = pd.DataFrame(index=header)

    # Loop through the directories and load the data
    for path in data_dirs:
        file_name = path / 'run_timing.log'
        if file_name.is_file():
            with open(file_name, 'r') as file:
                lines  = file.readlines()
                data   = lines[6].split()
                scaling_data[int(data[0])] = pd.to_numeric(data)
        else:
            print(f'File: {file_name} not found.')

    scaling_data = scaling_data.reindex(sorted(scaling_data.columns), axis=1)

    return scaling_data
# ==============================================================================

# ==============================================================================
def cells_per_second_plot(scaling_data):
    # Instantiate Plot
    fig = plt.figure(0, figsize=(15, 10))
    fig.clf()
    ax = plt.gca()

    # Set plot settings
    # Defaults colors #0072B2, #009E73, #D55E00, #CC79A7, #F0E442, #56B4E9
    color_mhd          = '#0072B2'
    color_mpi          = '#009E73'
    color_total        = '#D55E00'
    marker_style_mhd   = 'o'
    marker_style_mpi   = '1'
    marker_style_total = '^'
    marker_size     = 10

    # Plot the data
    ax, x, y = cells_per_second_per_gpu(scaling_data, 'Total', color_total, 'Total', ax, marker_size, marker_style=marker_style_total)
    # Note that the timer for the integrator is named "Hydro" not "MHD"
    ax = cells_per_second_per_gpu(scaling_data, 'Hydro_Integrator', color_mhd, 'MHD Integrator', ax, marker_size, marker_style=marker_style_mhd)[0]

    # Print the performance results
    for i in range(len(x)):
        print(f'Ranks: {int(x[i]):5d} updating at {round(y[i]/1.E8,4):3.4f}E8 cell updates per second per gpu')

    # Setup the rest of the plot
    ax.set_xlim(xmin = 0.7, xmax = 1E5)
    ax.set_ylim(ymin = 1E8, ymax = 1E9)

    ax.set_yscale('log')
    ax.set_xscale('log')

    locmaj = matplotlib.ticker.LogLocator(base=10.0,
                                          subs=(1.0, ),
                                          numticks=100)
    ax.yaxis.set_major_locator(locmaj)

    locmin = matplotlib.ticker.LogLocator(base=10.0,
                                          subs=np.arange(2, 10) * .1,
                                          numticks=100)
    ax.yaxis.set_minor_locator(locmin)
    ax.tick_params(which='both', direction='in', labelsize=20, bottom=True, top=True, left=True, right=True)

    plt.grid(axis='x', color='0.5', which='major')
    plt.grid(axis='y', color='0.5', which='major')
    # plt.grid(axis='y', color='0.25', which='minor')


    title_size      = 40
    axis_label_size = 25
    fig.suptitle('MHD Weak Scaling on Frontier (PLMC)', fontsize=title_size)
    ax.set_ylabel(r'Cell Updates / Second / GPU', fontsize=axis_label_size)
    ax.set_xlabel(r'Number of GPUs', fontsize=axis_label_size)


    legend = ax.legend(fontsize=15)
    fig.tight_layout()

    output_path = shared_tools.repo_root / 'latex-src' / f'scaling_tests_cells_per_second.pdf'
    fig.savefig(output_path, dpi=400)
# ==============================================================================

# ==============================================================================
def weak_scaling_efficiency(scaling_data):
    # Instantiate Plot
    fig = plt.figure(1, figsize=(shared_tools.fig_height, shared_tools.fig_height))
    ax = plt.gca()

    # Set plot settings
    # Defaults colors #0072B2, #009E73, #D55E00, #CC79A7, #F0E442, #56B4E9
    color_mhd          = '#0072B2'
    color_mpi          = '#009E73'
    color_total        = 'black'#'#D55E00'
    marker_style_mhd   = 'o'
    marker_style_mpi   = '1'
    marker_style_total = '^'
    marker_size        = 5

    # Plot the data
    ax, x, y = weak_scaling_efficiency_plot(scaling_data, 'Total', color_total, 'Total', ax, marker_size, marker_style=marker_style_total)
    # Note that the timer for the integrator is named "Hydro" not "MHD"
    # ax = weak_scaling_efficiency_plot(scaling_data, 'Hydro_Integrator', color_mhd, 'MHD Integrator', ax, marker_size, marker_style=marker_style_mhd)

    # Print the performance results
    print()
    for i in range(len(x)):
        print(f'Ranks: {int(x[i]):5d}, weak scaling efficiency: {round(y[i],2):5.2f}')

    # Setup the rest of the plot
    ax.set_xlim(xmin = 0.7, xmax = 1E5)
    ax.set_ylim(ymin = 0, ymax = 102)

    ax.set_xscale('log')

    # locmaj = matplotlib.ticker.LogLocator(base=10.0,
    #                                       subs=(1.0, ),
    #                                       numticks=100)
    # ax.yaxis.set_major_locator(locmaj)

    # locmin = matplotlib.ticker.LogLocator(base=10.0,
    #                                       subs=np.arange(2, 10) * .1,
    #                                       numticks=100)
    # ax.yaxis.set_minor_locator(locmin)
    ax.tick_params(which='both', direction='in', labelsize=shared_tools.font_size_normal, bottom=True, top=True, left=True, right=True)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter())

    plt.grid(axis='x', color='0.5', which='major')
    plt.grid(axis='y', color='0.5', which='major')
    # plt.grid(axis='y', color='0.25', which='minor')

    ax.set_ylabel(r'Weak Scaling Efficiency', fontsize=shared_tools.font_size_normal)
    ax.set_xlabel(r'Number of GPUs', fontsize=shared_tools.font_size_normal)
    ax.set_box_aspect(1)

    # legend = ax.legend(fontsize=15)
    fig.tight_layout()

    output_path = shared_tools.repo_root / 'latex-src' / f'scaling_tests_weak_efficiency.pdf'
    fig.savefig(output_path, dpi=400)
# ==============================================================================

# ==============================================================================
def ms_per_timestep(scaling_data):
    # Instantiate Plot
    fig = plt.figure(3, figsize=(shared_tools.fig_height, shared_tools.fig_height))
    ax = plt.gca()

    # Set plot settings
    # Defaults colors #0072B2, #009E73, #D55E00, #CC79A7, #F0E442, #56B4E9
    color_mhd          = '#0072B2'
    color_mpi          = '#009E73'
    color_total        = 'black'#'#D55E00'
    marker_style_mhd   = 'o'
    marker_style_mpi   = 's'
    marker_style_total = '^'
    marker_size        = 5

    # Plot the data
    scale_to = 256**3
    ax, x, y = ms_per_timestep_plot(scaling_data, 'Total', color_total, 'Total runtime (excluding initialization)', ax, marker_size, marker_style=marker_style_total, scale_to=scale_to)
    ax = ms_per_timestep_plot(scaling_data, 'Boundaries', color_mpi, 'MPI Communication', ax, marker_size, marker_style=marker_style_mpi, scale_to=scale_to)[0]
    # Note that the timer for the integrator is named "Hydro" not "MHD"
    ax = ms_per_timestep_plot(scaling_data, 'Hydro_Integrator', color_mhd, 'MHD Integrator', ax, marker_size, marker_style=marker_style_mhd, scale_to=scale_to)[0]

    # Print the performance results
    print()
    for i in range(len(x)):
        print(f'Ranks: {int(x[i]):5d},  ms/{int(np.cbrt(scale_to))}^3 cells/GPU: {round(y[i],2):5.2f}')

    # Setup the rest of the plot
    ax.set_xlim(xmin = 0.7, xmax = 1E5)
    ax.set_ylim(ymax = 120)

    ax.set_xscale('log')
    # ax.set_yscale('log')

    # locmaj = matplotlib.ticker.LogLocator(base=10.0,
    #                                       subs=(1.0, ),
    #                                       numticks=100)
    # ax.yaxis.set_major_locator(locmaj)

    # locmin = matplotlib.ticker.LogLocator(base=10.0,
    #                                       subs=np.arange(2, 10) * .1,
    #                                       numticks=100)
    # ax.yaxis.set_minor_locator(locmin)
    ax.tick_params(which='both', direction='in', labelsize=shared_tools.font_size_normal, bottom=True, top=True, left=True, right=True)
    # ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter())

    plt.grid(axis='x', color='0.5', which='major')
    plt.grid(axis='y', color='0.5', which='major')
    # plt.grid(axis='y', color='0.25', which='minor')

    ax.set_ylabel(r'Milliseconds / $256^3$ Cells / GPU', fontsize=shared_tools.font_size_normal)
    ax.set_xlabel(r'Number of GPUs', fontsize=shared_tools.font_size_normal)
    ax.set_box_aspect(1)

    legend = ax.legend(loc='upper left', fontsize=shared_tools.font_size_tiny)
    fig.tight_layout()

    output_path = shared_tools.repo_root / 'latex-src' / f'scaling_tests_ms_per_gpu.pdf'
    fig.savefig(output_path, dpi=400)
# ==============================================================================

# ==============================================================================
def weak_scaling_efficiency_plot(scaling_data, name, color, label, ax, marker_size, marker_style):
    x = scaling_data.loc['n_proc'].to_numpy()
    y = scaling_data.loc[name].to_numpy() / (scaling_data.loc['n_steps'].to_numpy() - 1)

    # Normalize to percentage
    y = (y[0] / y) * 100

    ax.plot(x, y, '--', c=color, marker=marker_style, markersize=marker_size, label=label)

    return ax, x, y
# ==============================================================================

# ==============================================================================
def ms_per_timestep_plot(scaling_data, name, color, label, ax, marker_size, marker_style, scale_to):
    x = scaling_data.loc['n_proc'].to_numpy()
    y = scaling_data.loc[name].to_numpy() / (scaling_data.loc['n_steps'].to_numpy() - 1)

    # Scale to the requested number of cells
    n_cells_per_gpu = int(scaling_data.loc['nx'][1]) * int(scaling_data.loc['ny'][1]) * int(scaling_data.loc['nz'][1])
    y *= scale_to / n_cells_per_gpu

    ax.plot(x, y, '--', c=color, marker=marker_style, markersize=marker_size, label=label)
    return ax, x, y
# ==============================================================================

# ==============================================================================
def cells_per_second_per_gpu(scaling_data, name, color, label, ax, marker_size, marker_style, delete_first=None):
    x = (scaling_data.loc['n_proc'].to_numpy())

    cells_per_gpu = ( scaling_data.loc['nx'].to_numpy()
                    * scaling_data.loc['ny'].to_numpy()
                    * scaling_data.loc['nz'].to_numpy()) / x

    avg_time_step = scaling_data.loc[name].to_numpy() / (scaling_data.loc['n_steps'].to_numpy() - 1)
    avg_time_step /= 1000 # convert to seconds from ms

    y = cells_per_gpu / avg_time_step

    ax.plot(x, y, '--', c=color, marker=marker_style, markersize=marker_size, label=label)
    return ax, x, y
# ==============================================================================

# ==============================================================================
def strong_scaling(data_path):

    # Plot settings
    file_path = data_path / 'run_timing.log'
    scaling_linestyle  = '--'
    alpha              = 0.4
    scaling_color      = 'black'


    # get header info
    with open(file_path, 'r') as file:
        lines        = file.readlines()
        header       = lines[5][1:].split()

    scaling_data = pd.read_csv(file_path, delim_whitespace=True, comment='#', skiprows=4, names=header)

    # Compute the speed up
    num_ranks = np.array(scaling_data['n_proc'])
    speedup   = np.array(np.max(scaling_data['Total'])/scaling_data['Total'])

    num_ranks = num_ranks
    speedup   =   speedup

    # Print the performance results
    for i in range(len(speedup)):
        print(f'Ranks: {int(num_ranks[i]):5d}, speedup: {round(speedup[i],2):>3.2f}, Strong Scaling Efficiency: {round(100*speedup[i] / num_ranks[i],2):3.2f}%')

    # Instantiate Plot
    fig = plt.figure(1, figsize=(shared_tools.fig_height, shared_tools.fig_height))
    ax = plt.gca()

    # Set plot settings
    color_total        = 'black'#'#D55E00'
    marker_style_total = '^'
    marker_size        = 5

    # Plot the data
    ax.plot(num_ranks, speedup, linestyle='--', c=color_total, marker=marker_style_total, markersize=marker_size, label='Total Runtime (excluding initialization)')

    # Plot the perfect scaling line
    ax.plot(num_ranks, num_ranks, color=scaling_color, alpha=alpha, linestyle=scaling_linestyle, label='Ideal Scaling')

    ax.set_xscale('log')
    ax.set_yscale('log')

    ax.tick_params(which='both', direction='in', labelsize=shared_tools.font_size_normal, bottom=True, top=True, left=True, right=True)
    # ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter())

    plt.grid(axis='x', color='0.5', which='major')
    plt.grid(axis='y', color='0.5', which='major')

    ax.set_ylabel(r'Speedup (vs. single GPU)', fontsize=shared_tools.font_size_normal)
    ax.set_xlabel(r'Number of GPUs', fontsize=shared_tools.font_size_normal)
    ax.set_box_aspect(1)

    legend = ax.legend(fontsize=9)
    fig.tight_layout()

    output_path = shared_tools.repo_root / 'latex-src' / f'scaling_test_strong.pdf'
    fig.savefig(output_path, dpi=400)
# ==============================================================================

if __name__ == '__main__':
    start = default_timer()
    main()
    print(f'Time to execute: {round(default_timer()-start,2)} seconds')
