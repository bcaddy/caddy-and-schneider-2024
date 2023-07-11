#!/usr/bin/env python3
"""
================================================================================
 Written by Robert Caddy.

 Generates the advecting field loop plots
================================================================================
"""

from timeit import default_timer
import matplotlib.pyplot as plt
import numpy as np
import argparse
import pathlib

import shared_tools

plt.close('all')

# Values to loop over
resolutions   = [32, 64, 128]
reconstructor = 'ppmc'
tout          = 2.0
outstep       = 0.2  # should be some even division of tout=2.0
num_outputs   = int(np.ceil(tout/outstep) + 1)
B_0           = 1E-3
radius        = 0.3

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
        OutPath = pathlib.Path(__file__).resolve().parent.parent / 'assets' / '3-mhd-tests'

    if args.run_cholla:
        runCholla()

    if args.figure:
        plotAFL(OutPath)
        # shared_tools.update_plot_entry("afl", 'python/advecting-field-loop.py')

# ==============================================================================

# ==============================================================================
def runCholla():
    for res in resolutions:
        run_start = default_timer()

        cli_args = f'nx={res} ny={res} nz={2*res} tout={tout} outstep={outstep} A={B_0} radius={radius}'
        shared_tools.cholla_runner(reconstructor=reconstructor,
                                   param_file_name=f'advecting_field_loop.txt',
                                   cholla_cli_args=cli_args,
                                   move_initial=True,
                                   move_final=True,
                                   initial_filename=f'afl_n{res}_0',
                                   final_filename=f'afl_n{res}_1')
        # Copy the rest of the data
        files = (shared_tools.repo_root/'python').glob('*.h5.*')
        for target in files:
            target.rename(shared_tools.data_files_path / f'afl_n{res}_{target.stem}')

        print(f'Finished with N={res} run. Time {round(default_timer()-run_start,2)}s')
# ==============================================================================

# ==============================================================================
def load_data():
    b_squared_avg = {}
    bz_abs_avg    = {}
    times         = {}
    for res in resolutions:
        key = f'{res}'

        b_squared_avg[key] = np.zeros(num_outputs)
        bz_abs_avg[key]    = np.zeros(num_outputs)
        times[key]         = np.zeros(num_outputs)

        for i in range(num_outputs):
            file_name = f'afl_n{res}_{i}'

            temp_data = shared_tools.load_conserved_data(file_name, load_time=True)
            temp_data = shared_tools.center_magnetic_fields(temp_data)

            b_squared_avg[key][i] = np.mean(temp_data['magnetic_x_centered']**2
                                    + temp_data['magnetic_y_centered']**2
                                    + temp_data['magnetic_z_centered']**2)

            bz_abs_avg[key][i] = np.mean(np.abs(temp_data['magnetic_z_centered']))
            bz_abs_avg[key][i] /= B_0

            times[key][i] = temp_data['time']

        b_squared_avg[key] /= b_squared_avg[key][0]

    return {'b_squared_avg':b_squared_avg, 'bz_abs_avg':bz_abs_avg, 'times':times}
# ==============================================================================

# ==============================================================================
def plotAFL(outPath):
    # Plotting info
    suptitle_font_size = 15
    subtitle_font_size = 10
    axslabel_font_size = 10
    line_width         = 1
    marker_size        = 5
    tick_font_size     = 7.5
    colors             = {'32':'blue',    '64':'red',    '128':'green'}
    line_style         = {'32':'dashdot', '64':'dashed', '128':'solid'}
    markers            = {'32':'o',       '64':'v',      '128':'s'}

    # Setup figure
    fig, subPlot = plt.subplots(1, 2)

    # Load data
    data = load_data()

    # Info for each sublot
    fields = ['b_squared_avg', 'bz_abs_avg']
    subplot_indices = {'b_squared_avg':0, 'bz_abs_avg':1}

    for field in fields:
        # Get info for this field
        subplot_idx = subplot_indices[field]

        # Plot the data
        for res in resolutions:
            key    = f'{res}'
            time   = data['times'][key]
            y_data = data[field][key]
            subPlot[subplot_idx].plot(time,
                                      y_data,
                                      color=colors[key],
                                      linestyle=line_style[key],
                                      linewidth=line_width,
                                      marker=markers[key],
                                      markersize=marker_size,
                                      label=f'N={res}')

        # Set ticks and grid
        subPlot[subplot_idx].tick_params(axis='both',
                                         direction='in',
                                         which='both',
                                         labelsize=tick_font_size,
                                         bottom=True, top=True, left=True, right=True)
        if field == 'b_squared_avg':
            subPlot[subplot_idx].set_ylim(top=1.0)
        if field == 'bz_abs_avg':
            pass
            # subPlot[subplot_idx].set_ylim(bottom=0.0)
            # subPlot[subplot_idx].set_yscale('log')

        # Set titles
        subPlot[subplot_idx].set_title(f'{shared_tools.pretty_names[field]}')
        subPlot[subplot_idx].set_xlabel('Time', fontsize=axslabel_font_size)

        # Legend
        subPlot[subplot_idx].legend()

    # Save the figure and close it
    fig.tight_layout()
    plt.savefig(outPath / f'afl.pdf', transparent = True)
    plt.close()
# ==============================================================================

if __name__ == '__main__':
    start = default_timer()
    main()
    print(f'Time to execute: {round(default_timer()-start,2)} seconds')