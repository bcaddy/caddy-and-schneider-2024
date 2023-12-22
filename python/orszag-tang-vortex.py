#!/usr/bin/env python3
"""
================================================================================
 Written by Robert Caddy.

 Generates the Orszag-Tang Vortex plots
================================================================================
"""

from timeit import default_timer
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import argparse
import pathlib

import shared_tools

plt.close('all')

matplotlib.rcParams['font.sans-serif'] = "Helvetica"
matplotlib.rcParams['font.family'] = "sans-serif"
matplotlib.rcParams['mathtext.fontset'] = 'cm'
matplotlib.rcParams['mathtext.rm'] = 'serif'

# ==============================================================================
def main():
    # Check for CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--in_path', help='The path to the directory that the source files are located in. Defaults to "~/Code/cholla/bin"')
    parser.add_argument('-o', '--out_path', help='The path of the directory to write the plots out to. Defaults to writing in the same directory as the input files')
    parser.add_argument('-r', '--run_cholla', action="store_true", help='Runs cholla to generate all the data')
    parser.add_argument('-f', '--figure', action="store_true", help='Generate the plots')

    args = parser.parse_args()

    if args.in_path:
        rootPath = pathlib.Path(str(args.in_path))
    else:
        rootPath = pathlib.Path(__file__).resolve().parent.parent

    if args.out_path:
        OutPath = pathlib.Path(str(args.out_path))
    else:
        OutPath = pathlib.Path(__file__).resolve().parent.parent / 'latex-src'

    if args.run_cholla:
        shared_tools.cholla_runner(param_file_name=f'orszag_tang_vortex.txt',
                                   move_final=True,
                                   final_filename=f'orszag_tang_vortex')

    if args.figure:
        plotOTV(rootPath, OutPath)
        shared_tools.update_plot_entry('otv', 'python/orszag-tang-vortex.py')
# ==============================================================================

# ==============================================================================
def plotOTV(rootPath, outPath):
    # Plotting info
    line_width         = 0.4
    num_contours       = 30

    # Field info
    fields = ['density', 'magnetic_energy', 'gas_pressure', 'spec_kinetic']
    field_indices = {'density':(0,0), 'magnetic_energy':(0,1), 'gas_pressure':(1,0), 'spec_kinetic':(1,1)}

    # Setup figure
    figSize = 10.0
    fig, subPlot = plt.subplots(2, 2, layout='constrained', figsize = (2*shared_tools.fig_width, 2*shared_tools.fig_height))

    # Whole plot settings
    # fig.suptitle(f'', fontsize=suptitle_font_size)

    # Load data
    data = shared_tools.load_conserved_data('orszag_tang_vortex', load_gamma=True, load_resolution=True)
    data = shared_tools.center_magnetic_fields(data)
    data = shared_tools.slice_data(data, z_slice_loc=data['resolution'][2]//2)
    data = shared_tools.compute_velocities(data)
    data = shared_tools.compute_derived_quantities(data, data['gamma'])

    for field in fields:
        # Get info for this field
        subplot_idx = field_indices[field]
        field_data  = np.rot90(data[field])

        # Compute where the contours are
        contours = np.linspace(np.min(field_data), np.max(field_data), num_contours)

        # Plot the data
        subPlot[subplot_idx].contour(field_data, levels=num_contours, cmap=shared_tools.color_maps[field], linewidths=line_width)

        # Set ticks and grid
        subPlot[subplot_idx].tick_params(labelleft=False, labelbottom=False,
                                         bottom=False, left=False)

        # Ensure equal axis
        subPlot[subplot_idx].set_box_aspect(1)

        # Set titles
        subPlot[subplot_idx].set_title(f'{shared_tools.pretty_names[field]}', fontsize=shared_tools.font_size_normal)

    # Save the figure and close it
    plt.savefig(outPath / f'orszag-tang-vortex.pdf', transparent = True)
    plt.close()
# ==============================================================================

if __name__ == '__main__':
    start = default_timer()
    main()
    print(f'Time to execute: {round(default_timer()-start,2)} seconds')