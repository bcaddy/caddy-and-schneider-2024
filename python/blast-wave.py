#!/usr/bin/env python3
"""
================================================================================
 Written by Robert Caddy.

 Generates the MHD blast wave plots
================================================================================
"""

from timeit import default_timer

import collections
import functools

import matplotlib
import matplotlib.animation as animation
import matplotlib.pyplot as plt

import numpy as np
import h5py

import os
import sys
import argparse
import pathlib

import shared_tools

plt.close('all')

# Global settings
reconstructor = 'ppmc'

# ==============================================================================
def main():
    # Check for CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--in_path', help='The path to the directory that the source files are located in. Defaults to "~/Code/cholla/bin"')
    parser.add_argument('-o', '--out_path', help='The path of the directory to write the plots out to. Defaults to writing in the same directory as the input files')
    parser.add_argument('-r', '--run_cholla', action="store_true", help='Runs cholla to generate all the scaling data')
    parser.add_argument('-f', '--figure', action="store_true", help='Plot the L2 Norms')

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
        runCholla(rootPath)

    if args.figure:
        plotBlastWave(rootPath, OutPath)
        shared_tools.update_plot_entry("mhd-blast", 'python/blast-wave.py')

# ==============================================================================

# ==============================================================================
def runCholla(rootPath):
    # Paths
    exe_path = rootPath / 'cholla' / 'bin'
    data_from_path = rootPath / 'python'
    data_to_path = rootPath / 'data'
    # Check that the output directory exists
    data_to_path.mkdir(parents=True, exist_ok=True)

    # Generate Cholla run command
    chollaPath = exe_path / f'cholla.mhd.c3po.{reconstructor}'
    paramFilePath = data_from_path / 'cholla-config-files' / f'mhd_blast.txt'
    logFile = rootPath / 'cholla.log'
    command = f'{chollaPath} {paramFilePath} >> {logFile} 2>&1'

    # Run Cholla
    os.system(command)

    # Move data file
    finalFile = data_from_path / '1.h5.0'
    finalFile.rename(data_to_path / f'mhd-blast-final.h5')
    initialFile = data_from_path / '0.h5.0'
    initialFile.rename(data_to_path / f'mhd-blast-initial.h5')

    # Remove unused files
    (data_from_path / 'run_output.log').unlink()
    (data_from_path / 'run_timing.log').unlink()
# ==============================================================================

# ==============================================================================
# def loadData(rootPath, shock_tube):
#     # Open the file and prep for loading
#     file = h5py.File(rootPath / 'data' / (shock_tube + '.h5'), 'r')
#     y_slice_loc = resolution['ny']//2
#     z_slice_loc = resolution['nz']//2

#     # Load all the raw data
#     gamma = file.attrs['gamma'][0]
#     density    = file['density'][:, y_slice_loc, z_slice_loc]
#     velocity_x = file['momentum_x'][:, y_slice_loc, z_slice_loc] / density
#     velocity_y = file['momentum_y'][:, y_slice_loc, z_slice_loc] / density
#     velocity_z = file['momentum_z'][:, y_slice_loc, z_slice_loc] / density
#     magnetic_x = file['magnetic_x'][:, y_slice_loc, z_slice_loc]
#     magnetic_y = 0.5 * (file['magnetic_y'][:, y_slice_loc, z_slice_loc] + file['magnetic_y'][:, y_slice_loc-1, z_slice_loc])
#     magnetic_z = 0.5 * (file['magnetic_z'][:, y_slice_loc, z_slice_loc] + file['magnetic_z'][:, y_slice_loc, z_slice_loc-1])
#     energy     = file['Energy'][:, y_slice_loc, z_slice_loc]

#     # Compute the Pressure
#     magnetic_x_centered = 0.5 * (magnetic_x[1:] + magnetic_x[:-1])
#     velocity_squared = velocity_x**2 + velocity_y**2 + velocity_z**2
#     magnetic_squared = magnetic_x_centered**2 + magnetic_y**2 + magnetic_z**2
#     pressure = (gamma - 1) * (energy - 0.5 * density * (velocity_squared) - 0.5 * (magnetic_squared))

#     return {'density':density, 'pressure':pressure, 'energy':energy,
#             'velocity_x':velocity_x, 'velocity_y':velocity_y, 'velocity_z':velocity_z,
#             'magnetic_x':magnetic_x, 'magnetic_y':magnetic_y, 'magnetic_z':magnetic_z}
# ==============================================================================

# ==============================================================================
def plotBlastWave(rootPath, outPath):
    pass
    # Pretty names
    # pretty_names = {'b&w':'Brio & Wu',
    #                 'd&w':'Dai & Woodward',
    #                 'einfeldt':'Einfeldt Strong Rarefaction',
    #                 'rj1a':'Ryu & Jones 1a',
    #                 'rj4d':'Ryu & Jones 4d',
    #                 'density':'Density',
    #                 'pressure':'Pressure',
    #                 'energy':'Energy',
    #                 'velocity_x':'$V_x$',
    #                 'velocity_y':'$V_y$',
    #                 'velocity_z':'$V_z$',
    #                 'magnetic_x':'$B_x$',
    #                 'magnetic_y':'$B_y$',
    #                 'magnetic_z':'$B_z$'}

    # # Plotting info
    # data_marker        = '.'
    # data_markersize    = 5
    # data_linestyle     = '-'
    # linewidth          = 0.1 * data_markersize
    # suptitle_font_size = 15
    # subtitle_font_size = 10
    # axslabel_font_size = 10
    # tick_font_size     = 7.5

    # colors = {'density':'blue', 'pressure':'green', 'energy':'red',
    #           'velocity_x':'purple', 'velocity_y':'purple', 'velocity_z':'purple',
    #           'magnetic_x':'orange', 'magnetic_y':'orange', 'magnetic_z':'orange'}

    # # Field info
    # fields = ['density', 'pressure', 'energy', 'velocity_x', 'velocity_y', 'velocity_z',  'magnetic_x', 'magnetic_y', 'magnetic_z']
    # field_indices = {'density':(0,0), 'pressure':(0,1), 'energy':(0,2),
    #                  'velocity_x':(1,0), 'velocity_y':(1,1), 'velocity_z':(1,2),
    #                  'magnetic_x':(2,0), 'magnetic_y':(2,1), 'magnetic_z':(2,2)}

    # # Plot the shock tubes data
    # for shock_tube in shock_tubes:
    #     # Setup figure
    #     figSizeScale = 2.                 # Scaling factor for the figure size
    #     figHeight    = 4.8 * figSizeScale # height of the plot in inches, default is 4.8
    #     figWidth     = 7.0 * figSizeScale # width of the plot in inches, default is 6.4
    #     fig, subPlot = plt.subplots(3, 3, sharex=True, figsize = (figWidth, figHeight))

    #     # Whole plot settings
    #     fig.suptitle(f'{pretty_names[shock_tube]}', fontsize=suptitle_font_size)
    #     fig.tight_layout(pad = 1.5, w_pad = 1.5)

    #     # Load data
    #     data = loadData(rootPath, shock_tube)

    #     for field in fields:
    #         # Get info for this field
    #         subplot_idx = field_indices[field]
    #         field_data  = data[field]

    #         # Compute the positional data
    #         positions = np.linspace(0, physical_size, data[field].size)

    #         # Check the range. If it's just noise then set y-limits
    #         if np.abs(field_data.max() - field_data.min()) < 1E-10:
    #             mean = field_data.mean()
    #             subPlot[subplot_idx].set_ylim(mean - 0.5, mean + 0.5)

    #         # Plot the data
    #         subPlot[subplot_idx].plot(positions,
    #                                   field_data,
    #                                   color      = colors[field],
    #                                   linestyle  = data_linestyle,
    #                                   linewidth  = linewidth,
    #                                   marker     = data_marker,
    #                                   markersize = data_markersize,
    #                                   label      = 'PLMC')

    #         # Set ticks and grid
    #         subPlot[subplot_idx].tick_params(axis='both',
    #                                          direction='in',
    #                                          which='both',
    #                                          labelsize=tick_font_size,
    #                                          bottom=True,
    #                                          top=True,
    #                                          left=True,
    #                                          right=True)

    #         # Set titles
    #         subPlot[subplot_idx].set_ylabel(f'{pretty_names[field]}', fontsize=axslabel_font_size)
    #         if (subplot_idx[0] == 2):
    #             subPlot[subplot_idx].set_xlabel('Position', fontsize=axslabel_font_size)

    #     # Save the figure and close it
    #     plt.savefig(outPath / f'{shock_tube}.pdf', transparent = True)
    #     plt.close()

    #     print(f'Finished with {pretty_names[shock_tube]} plot.')
# ==============================================================================


if __name__ == '__main__':
    start = default_timer()
    main()
    print(f'Time to execute: {round(default_timer()-start,2)} seconds')