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
        pass
        # plotAFL()
        # shared_tools.update_plot_entry("afl", 'python/advecting-field-loop.py')

# ==============================================================================

# ==============================================================================
def runCholla():
    num_outputs = int(np.ceil(tout/outstep) + 1)

    for res in resolutions:
        run_start = default_timer()

        cli_args = f'nx={res} ny={res} nz={2*res} tout={tout} outstep={outstep}'
        shared_tools.cholla_runner(reconstructor=reconstructor,
                                   param_file_name=f'advecting_field_loop.txt',
                                   cholla_cli_args=cli_args,
                                   move_initial=True,
                                   move_final=True,
                                   initial_filename=f'afl_n{res}_0',
                                   final_filename=f'afl_n{res}_{num_outputs-1}')
        # Copy the rest of the data
        files = (shared_tools.repo_root/'python').glob('*.h5.*')
        for target in files:
            target.rename(shared_tools.data_files_path / f'afl_n{res}_{target.stem}')

        print(f'Finished with N={res} run. Time {round(default_timer()-run_start,2)}s')
# ==============================================================================

# ==============================================================================
# def plotAFL(rootPath, outPath):
#     # Plotting info
#     line_width         = 0.1
#     suptitle_font_size = 15
#     subtitle_font_size = 10
#     num_contours       = 30

#     # Setup figure
#     fig, subPlot = plt.subplots(1, 2)

#     # Whole plot settings
#     fig.tight_layout()

#     # Load data

#     data = shared_tools.load_conserved_data('', load_gamma=True, load_resolution=True)
#     data = shared_tools.center_magnetic_fields(data)

#     for field in fields:
#         # Get info for this field
#         subplot_idx = field_indices[field]
#         field_data  = np.fliplr(np.rot90(data[field]))

#         # Compute where the contours are
#         contours = np.linspace(np.min(field_data), np.max(field_data), num_contours)

#         # Plot the data
#         subPlot[subplot_idx].contour(field_data, levels=num_contours, colors='black', linewidths=line_width)

#         # Set ticks and grid
#         subPlot[subplot_idx].tick_params(labelleft=False, labelbottom=False,
#                                          bottom=False, left=False)

#         # Ensure equal axis
#         subPlot[subplot_idx].set_aspect('equal')

#         # Set titles
#         subPlot[subplot_idx].set_title(f'{shared_tools.pretty_names[field]}')

#     # Save the figure and close it
#     plt.savefig(outPath / f'afl.pdf', transparent = True)
#     plt.close()
# ==============================================================================

if __name__ == '__main__':
    start = default_timer()
    main()
    print(f'Time to execute: {round(default_timer()-start,2)} seconds')