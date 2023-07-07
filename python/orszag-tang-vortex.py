#!/usr/bin/env python3
"""
================================================================================
 Written by Robert Caddy.

 Generates the Orszag-Tang Vortex plots
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
reconstructor = 'plmc'

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
        plotOTV(rootPath, OutPath)
        # shared_tools.update_plot_entry('otv', 'python/orszag-tang-vortex.py')

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
    paramFilePath = data_from_path / 'cholla-config-files' / f'orszag_tang_vortex.txt'
    logFile = rootPath / 'cholla.log'
    command = f'{chollaPath} {paramFilePath} >> {logFile} 2>&1'

    # Run Cholla
    os.system(command)

    # Move data file
    (data_from_path / '1.h5.0').rename(data_to_path / f'orszag_tang_vortex.h5')

    # Remove unused files
    (data_from_path / '0.h5.0').unlink()
    (data_from_path / 'run_output.log').unlink()
    (data_from_path / 'run_timing.log').unlink()
# ==============================================================================

# ==============================================================================
def loadData(rootPath):
    # Open the file and prep for loading
    file = h5py.File(rootPath / 'data' / 'orszag_tang_vortex.h5', 'r')
    resolution = file.attrs['dims']
    z_slice_loc = resolution[2]//2

    # Load all the raw data
    gamma = file.attrs['gamma'][0]
    density    = file['density'][:, :, z_slice_loc]
    velocity_x = file['momentum_x'][:, :, z_slice_loc] / density
    velocity_y = file['momentum_y'][:, :, z_slice_loc] / density
    velocity_z = file['momentum_z'][:, :, z_slice_loc] / density
    magnetic_x = 0.5 * (file['magnetic_x'][1:,  :, z_slice_loc] + file['magnetic_x'][:-1, :,   z_slice_loc])
    magnetic_y = 0.5 * (file['magnetic_y'][ :, 1:, z_slice_loc] + file['magnetic_y'][:,   :-1, z_slice_loc])
    magnetic_z = 0.5 * (file['magnetic_z'][ :,  :, z_slice_loc] + file['magnetic_z'][:,   :,   z_slice_loc-1])
    energy     = file['Energy'][:, :, z_slice_loc]

    # Compute magnetic energy
    velocity_squared = velocity_x**2 + velocity_y**2 + velocity_z**2
    magnetic_squared = magnetic_x**2 + magnetic_y**2 + magnetic_z**2

    magnetic_energy = 0.5 * magnetic_squared
    spec_kinetic = 0.5 * velocity_squared

    pressure = (gamma - 1) * (energy - 0.5 * density * (velocity_squared) - magnetic_energy)

    return {'density':density, 'energy':energy, 'pressure':pressure,
            'magnetic_energy':magnetic_energy, 'spec_kinetic':spec_kinetic,
            'velocity_x':velocity_x, 'velocity_y':velocity_y, 'velocity_z':velocity_z,
            'magnetic_x':magnetic_x, 'magnetic_y':magnetic_y, 'magnetic_z':magnetic_z}
# ==============================================================================

# ==============================================================================
def plotOTV(rootPath, outPath):
    # Pretty names
    pretty_names = {'density':'Density',
                    'magnetic_energy':'Magnetic Energy',
                    'pressure':'Pressure', 'spec_kinetic':'Specific Kinetic Energy'}

    # Plotting info
    line_width         = 0.4
    suptitle_font_size = 15
    subtitle_font_size = 10
    num_contours       = 30

    # Field info
    fields = ['density', 'magnetic_energy', 'pressure', 'spec_kinetic']
    field_indices = {'density':(0,0), 'magnetic_energy':(0,1), 'pressure':(1,0), 'spec_kinetic':(1,1)}

    # Setup figure
    figSizeScale = 2.                 # Scaling factor for the figure size
    figHeight    = 4.8 * figSizeScale # height of the plot in inches, default is 4.8
    figWidth     = 7.0 * figSizeScale # width of the plot in inches, default is 6.4
    fig, subPlot = plt.subplots(2, 2)#figsize = (figWidth, figHeight))

    # Whole plot settings
    # fig.suptitle(f'', fontsize=suptitle_font_size)

    # Load data
    data = loadData(rootPath)

    for field in fields:
        # Get info for this field
        subplot_idx = field_indices[field]
        field_data  = np.rot90(data[field])

        # Compute where the contours are
        contours = np.linspace(np.min(field_data), np.max(field_data), num_contours)

        # Plot the data
        subPlot[subplot_idx].contour(field_data, levels=num_contours, colors='black', linewidths=line_width)

        # Set ticks and grid
        subPlot[subplot_idx].tick_params(labelleft=False, labelbottom=False,
                                         bottom=False, left=False)

        # Ensure equal axis
        subPlot[subplot_idx].set_aspect('equal')

        # Set titles
        subPlot[subplot_idx].set_title(f'{pretty_names[field]}')

    # Save the figure and close it
    fig.tight_layout()
    plt.savefig(outPath / f'orszag-tang-vortex.pdf', transparent = True)
    plt.close()
# ==============================================================================

if __name__ == '__main__':
    start = default_timer()
    main()
    print(f'Time to execute: {round(default_timer()-start,2)} seconds')