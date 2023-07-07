#!/usr/bin/env python3
"""
================================================================================
 Written by Robert Caddy.

 Generates the linear wave convergence plots. This script it largely identical
 to the same script in the `analysis_scripts` repo, just optimized for this paper
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

# 1. (optionally) Run Cholla
#   a. Resolutions: 16, 32, 64, 128, 256, 512
#   b. All 4 waves
#   c. PLMC and PPMC
# 2. (optionally) Compute all the L2 Norms
# 3. (optionally) Plot the results
#   a. Plot specific scaling lines

# Lists to loop over
reconstructors = ['plmc', 'ppmc']
waves          = ['alfven_wave', 'fast_magnetosonic', 'mhd_contact_wave', 'slow_magnetosonic']
resolutions    = [16, 32, 64, 128, 256, 512]

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

    if args.run_cholla == 'True':
        runCholla(rootPath)

    if args.figure == 'True':
        L2Norms = computeL2Norm(rootPath)
        plotL2Norm(L2Norms, OutPath)
        shared_tools.update_plot_entry('linear_wave_convergence', 'python/linear-wave-convergence.py')

# ==============================================================================

# ==============================================================================
def runCholla(rootPath):
    # Basic Settings
    offAxisResolution = 'ny=16 nz=16'
    exe_path = rootPath / 'cholla' / 'bin'
    data_from_path = rootPath / 'python'
    data_to_path = rootPath / 'data'

    # Check that the output directory exists
    data_to_path.mkdir(parents=True, exist_ok=True)

    # Loop over the lists and run cholla for each combination
    for reconstructor in reconstructors:
        for wave in waves:
            for resolution in resolutions:
                # Generate Cholla run command
                chollaPath = exe_path / f'cholla.mhd.c3po.{reconstructor}'
                paramFilePath = data_from_path / 'cholla-config-files' / f'{wave}.txt'
                logFile = rootPath / 'cholla.log'
                command = f'{chollaPath} {paramFilePath} nx={resolution} {offAxisResolution} >> {logFile} 2>&1'

                # Run Cholla
                os.system(command)

                # Move data files
                initialFile = data_from_path / '0.h5.0'
                finalFile = data_from_path / '1.h5.0'
                initialFile.rename(data_to_path / f'{reconstructor}_{wave}_{resolution}_initial.h5')
                finalFile.rename(data_to_path / f'{reconstructor}_{wave}_{resolution}_final.h5')

                # Print status
                print(f'Finished with {resolution}, {wave}, {reconstructor}')
# ==============================================================================

# ==============================================================================
def computeL2Norm(rootPath):
    # Setup dictionary to hold data
    data = {}
    for reconstructor in reconstructors:
        for wave in waves:
            for resolution in resolutions:
                data[f'{reconstructor}_{wave}'] = []

    # Loop over the lists and compute the L2 norm for each combination
    for reconstructor in reconstructors:
        for wave in waves:
            for resolution in resolutions:
                # Determine file paths and load the files
                initialFilePath = rootPath / 'data' / f'{reconstructor}_{wave}_{resolution}_initial.h5'
                finalFilePath   = rootPath / 'data' / f'{reconstructor}_{wave}_{resolution}_final.h5'
                initialFile = h5py.File(initialFilePath, 'r')
                finalFile   = h5py.File(finalFilePath, 'r')

                # Get a list of all the data sets
                fields = initialFile.keys()

                # Compute the L2 Norm
                L2Norm = 0.0
                for field in fields:
                    initialData = np.array(initialFile[field])
                    finalData   = np.array(finalFile[field])

                    diff = np.abs(initialData - finalData)
                    L1Error = np.sum(diff) / initialData.size
                    L2Norm += np.power(L1Error, 2)

                L2Norm = np.sqrt(L2Norm)
                data[f'{reconstructor}_{wave}'].append(L2Norm)

    return data
# ==============================================================================

# ==============================================================================
def plotL2Norm(L2Norms, outPath, normalize = False):
    # Plotting info
    data_linestyle     = '-'
    linewidth          = 1
    plmc_marker        = '.'
    ppmc_marker        = '^'
    data_markersize    = 10
    scaling_linestyle  = '--'
    alpha              = 0.6
    scaling_color      = 'black'
    plmc_color         = 'red'
    ppmc_color         = 'blue'
    suptitle_font_size = 15
    subtitle_font_size = 10
    axslabel_font_size = 10
    legend_font_size   = 7.5
    tick_font_size     = 7.5

    # Plot the L2 Norm data
    fig, subPlot = plt.subplots(2, 2)#, sharex=True, sharey=True)

    wave_position = {'alfven_wave':(1,0), 'fast_magnetosonic':(0,1), 'mhd_contact_wave':(1,1), 'slow_magnetosonic':(0,0)}

    for wave in waves:
        subplot_idx = wave_position[wave]
        # Optionally, normalize the data
        if normalize:
            plmc_data = L2Norms[f'plmc_{wave}'] / L2Norms[f'plmc_{wave}'][0]
            ppmc_data = L2Norms[f'ppmc_{wave}'] / L2Norms[f'ppmc_{wave}'][0]
            norm_name = "Normalized "
        else:
            plmc_data = L2Norms[f'plmc_{wave}']
            ppmc_data = L2Norms[f'ppmc_{wave}']
            norm_name = ''

        # Plot raw data
        subPlot[subplot_idx].plot(resolutions,
                                  plmc_data,
                                  color      = plmc_color,
                                  linestyle  = data_linestyle,
                                  linewidth  = linewidth,
                                  marker     = plmc_marker,
                                  markersize = data_markersize,
                                  label      = 'PLMC')
        subPlot[subplot_idx].plot(resolutions,
                                  ppmc_data,
                                  color      = ppmc_color,
                                  linestyle  = data_linestyle,
                                  linewidth  = linewidth,
                                  marker     = ppmc_marker,
                                  markersize = 0.5*data_markersize,
                                  label      = 'PPMC')

        # Plot the scaling lines
        scalingRes = [resolutions[0], resolutions[1], resolutions[-1]]
        # loop through the different scaling powers
        for i in [2]:
            label = r'$\mathcal{O}(\Delta x^' + str(i) + r')$'
            norm_point = plmc_data[1]
            scaling_data = np.array([norm_point / np.power(scalingRes[0]/scalingRes[1], i), norm_point, norm_point / np.power(scalingRes[-1]/scalingRes[1], i)])
            subPlot[subplot_idx].plot(scalingRes, scaling_data, color=scaling_color, alpha=alpha, linestyle=scaling_linestyle, linewidth=linewidth, label=label)

        # Set axis parameters
        subPlot[subplot_idx].set_xscale('log')
        subPlot[subplot_idx].set_yscale('log')
        subPlot[subplot_idx].set_xlim(1E1, 1E3)

        # Set ticks and grid
        subPlot[subplot_idx].tick_params(axis='both', direction='in', which='both', labelsize=tick_font_size, bottom=True, top=True, left=True, right=True)

        # Set axis titles
        if (subplot_idx[0] == 1):
            subPlot[subplot_idx].set_xlabel('Resolution', fontsize=axslabel_font_size)
        if (subplot_idx[1] == 0):
            subPlot[subplot_idx].set_ylabel(f'{norm_name}L2 Error', fontsize=axslabel_font_size)
        subPlot[subplot_idx].set_title(f'{shared_tools.pretty_names[wave]}', fontsize=subtitle_font_size)

        subPlot[subplot_idx].legend(fontsize=legend_font_size)

    # Legend
    # fig.legend()

    # Whole plot settings
    fig.suptitle(f'{norm_name}MHD Linear Wave Convergence', fontsize=suptitle_font_size)

    plt.tight_layout()
    plt.savefig(outPath / f'linear_convergence.pdf', transparent = True)
    plt.close()
# ==============================================================================


if __name__ == '__main__':
    start = default_timer()
    main()
    print(f'Time to execute: {round(default_timer()-start,2)} seconds')