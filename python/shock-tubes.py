#!/usr/bin/env python3
"""
================================================================================
 Written by Robert Caddy.

 Generates the shock tube plots.
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

# Global Variables
shock_tubes = ['b&w', 'd&w', 'rj1a', 'rj4d', 'einfeldt']
reconstructor = 'ppmc'
resolution = {'nx':512, 'ny':16, 'nz':16}
physical_size = 1.0

# Setup shock tube parameters
shock_tube_params = {}
coef = 1.0 / np.sqrt(4 * np.pi)
shock_tube_params['b&w']      = f'gamma=2.0 tout=0.1 outstep=0.1 diaph=0.5 '\
                                f'rho_l=1.0 vx_l=0 vy_l=0 vz_l=0 P_l=1.0 Bx_l=0.75 By_l=1.0 Bz_l=0.0 '\
                                f'rho_r=0.128 vx_r=0 vy_r=0 vz_r=0 P_r=0.1 Bx_r=0.75 By_r=-1.0 Bz_r=0.0'
shock_tube_params['d&w']      = f'gamma={5./3.} tout=0.2 outstep=0.2 diaph=0.5 '\
                                f'rho_l=1.08 vx_l=1.2 vy_l=0.01 vz_l=0.5 P_l=0.95 Bx_l={2.*coef} By_l={3.6*coef} Bz_l={2.*coef} '\
                                f'rho_r=1.0 vx_r=0 vy_r=0 vz_r=0 P_r=1.0 Bx_r={2.*coef} By_r={4.*coef} Bz_r={2.*coef}'
shock_tube_params['einfeldt'] = f'gamma=1.4 tout=0.16 outstep=0.16 diaph=0.5 '\
                                f'rho_l=1.0 vx_l=-2.0 vy_l=0 vz_l=0 P_l=0.45 Bx_l=0.0 By_l=0.5 Bz_l=0.0 '\
                                f'rho_r=1.0 vx_r=2.0 vy_r=0 vz_r=0 P_r=0.45 Bx_r=0.0 By_r=0.5 Bz_r=0.0'
shock_tube_params['rj1a']     = f'gamma={5./3.} tout=0.08 outstep=0.08 diaph=0.5 '\
                                f'rho_l=1.0 vx_l=10.0 vy_l=0 vz_l=0 P_l=20.0 Bx_l={5.0*coef} By_l={5.0*coef} Bz_l=0.0 '\
                                f'rho_r=1.0 vx_r=-10.0 vy_r=0 vz_r=0 P_r=1.0 Bx_r={5.0*coef} By_r={5.0*coef} Bz_r=0.0'
shock_tube_params['rj4d']     = f'gamma={5./3.} tout=0.16 outstep=0.16 diaph=0.5 '\
                                f'rho_l=1.0 vx_l=0 vy_l=0 vz_l=0 P_l=1.0 Bx_l=0.7 By_l=0.0 Bz_l=0.0 '\
                                f'rho_r=0.3 vx_r=0 vy_r=0 vz_r=1.0 P_r=0.2 Bx_r=0.7 By_r=1.0 Bz_r=0.0'

# ==============================================================================
def main():
    # Check for CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--in_path', help='The path to the directory that the source files are located in. Defaults to "~/Code/cholla/bin"')
    parser.add_argument('-o', '--out_path', help='The path of the directory to write the plots out to. Defaults to writing in the same directory as the input files')
    parser.add_argument('-r', '--run_cholla', default=False, help='Runs cholla to generate all the scaling data')
    parser.add_argument('-f', '--figure', default=False, help='Plot the L2 Norms')
    parser.add_argument('-t', '--tube', default=['all'], nargs='+', help="List of tubes to run and/or plot. Options are 'b&w', 'd&w', 'rj1a', 'rj4d', 'einfeldt', and 'all'")

    args = parser.parse_args()

    if args.in_path:
        rootPath = pathlib.Path(str(args.in_path))
    else:
        rootPath = pathlib.Path(__file__).resolve().parent.parent

    if args.out_path:
        OutPath = pathlib.Path(str(args.out_path))
    else:
        OutPath = pathlib.Path(__file__).resolve().parent.parent / 'assets' / '3-mhd-tests'

    global shock_tubes
    if args.tube != ['all']:
        for test_val in args.tube:
            if test_val not in shock_tubes:
                raise ValueError(f'Unsupported value "{test_val}" given as a shock tube.')
        shock_tubes = args.tube

    if args.run_cholla == 'True':
        runCholla(rootPath)

    if args.figure == 'True':
        plotShockTubes(rootPath, OutPath)
        for tube in shock_tubes:
            shared_tools.update_plot_entry(tube, 'python/shock-tubes.py')

# ==============================================================================

# ==============================================================================
def runCholla(rootPath):
    # Paths
    exe_path = rootPath / 'cholla' / 'bin'
    data_from_path = rootPath / 'python'
    data_to_path = rootPath / 'data'
    # Check that the output directory exists
    data_to_path.mkdir(parents=True, exist_ok=True)

    # Cholla settings
    common_settings = f"nx={resolution['nx']} ny={resolution['ny']} nz={resolution['nz']} init=Riemann " \
                      f"xmin=0.0 ymin=0.0 zmin=0.0 xlen={physical_size} ylen={physical_size} zlen={physical_size} "\
                       "xl_bcnd=3 xu_bcnd=3 yl_bcnd=3 yu_bcnd=3 zl_bcnd=3 zu_bcnd=3 "\
                       "outdir=./"

    # Loop over the lists and run cholla for each combination
    for shock_tube in shock_tubes:
        # Generate Cholla run command
        chollaPath = exe_path / f'cholla.mhd.c3po.{reconstructor}'
        paramFilePath = data_from_path / 'cholla-config-files' / f'blank_settings_file.txt'
        logFile = rootPath / 'cholla.log'
        command = f'{chollaPath} {paramFilePath} {common_settings} {shock_tube_params[shock_tube]} >> {logFile} 2>&1'

        # Run Cholla
        os.system(command)

        # Move data file
        finalFile = data_from_path / '1.h5.0'
        finalFile.rename(data_to_path / f'{shock_tube}.h5')

        # Remove unused files
        (data_from_path / '0.h5.0').unlink()
        (data_from_path / 'run_output.log').unlink()
        (data_from_path / 'run_timing.log').unlink()

        # Print status
        print(f'Finished with {shock_tube}, {reconstructor}')
# ==============================================================================

# ==============================================================================
def loadDataField(rootPath, shock_tube):
    # Open the file and prep for loading
    file = h5py.File(rootPath / 'data' / (shock_tube + '.h5'), 'r')
    y_slice_loc = resolution['ny']//2
    z_slice_loc = resolution['nz']//2

    # Load all the raw data
    gamma = file.attrs['gamma'][0]
    density    = file['density'][:, y_slice_loc, z_slice_loc]
    velocity_x = file['momentum_x'][:, y_slice_loc, z_slice_loc] / density
    velocity_y = file['momentum_y'][:, y_slice_loc, z_slice_loc] / density
    velocity_z = file['momentum_z'][:, y_slice_loc, z_slice_loc] / density
    magnetic_x = file['magnetic_x'][:, y_slice_loc, z_slice_loc]
    magnetic_y = 0.5 * (file['magnetic_y'][:, y_slice_loc, z_slice_loc] + file['magnetic_y'][:, y_slice_loc-1, z_slice_loc])
    magnetic_z = 0.5 * (file['magnetic_z'][:, y_slice_loc, z_slice_loc] + file['magnetic_z'][:, y_slice_loc, z_slice_loc-1])
    energy     = file['Energy'][:, y_slice_loc, z_slice_loc]

    # Compute the Pressure
    magnetic_x_centered = 0.5 * (magnetic_x[1:] + magnetic_x[:-1])
    velocity_squared = velocity_x**2 + velocity_y**2 + velocity_z**2
    magnetic_squared = magnetic_x_centered**2 + magnetic_y**2 + magnetic_z**2
    pressure = (gamma - 1) * (energy - 0.5 * density * (velocity_squared) - 0.5 * (magnetic_squared))

    return {'density':density, 'pressure':pressure, 'energy':energy,
            'velocity_x':velocity_x, 'velocity_y':velocity_y, 'velocity_z':velocity_z,
            'magnetic_x':magnetic_x, 'magnetic_y':magnetic_y, 'magnetic_z':magnetic_z}
# ==============================================================================

# ==============================================================================
def plotShockTubes(rootPath, outPath):
    # Pretty names
    pretty_names = {'b&w':'Brio & Wu',
                    'd&w':'Dai & Woodward',
                    'einfeldt':'Einfeldt Strong Rarefaction',
                    'rj1a':'Ryu & Jones 1a',
                    'rj4d':'Ryu & Jones 4d',
                    'density':'Density',
                    'pressure':'Pressure',
                    'energy':'Energy',
                    'velocity_x':'X-Velocity',
                    'velocity_y':'Y-Velocity',
                    'velocity_z':'Z-Velocity',
                    'magnetic_x':'X-Magnetic Field',
                    'magnetic_y':'Y-Magnetic Field',
                    'magnetic_z':'Z-Magnetic Field'}

    # Plotting info
    data_linestyle     = '-'
    linewidth          = 1
    data_marker        = '.'
    data_markersize    = 10
    suptitle_font_size = 15
    subtitle_font_size = 10
    axslabel_font_size = 10
    tick_font_size     = 7.5

    # Field info
    fields = ['density', 'pressure', 'Energy', 'velocity_x', 'velocity_y', 'velocity_z',  'magnetic_x', 'magnetic_y', 'magnetic_z']
    field_indices = {'density':(0,0), 'pressure':(0,1), 'energy':(0,2),
                     'vx':(1,0), 'vy':(1,1), 'vz':(1,2),
                     'bx':(2,0), 'by':(2,1), 'bz':(2,2)}

    # Plot the shock tubes data
    for shock_tube in shock_tubes:
        # Setup figure
        fig, subPlot = plt.subplots(2, 2, sharex=True, sharey=True)

        # Load data
        data = loadDataField(rootPath, shock_tube)

        for field in fields:
            pass

        # Plot raw data
    #     subPlot[subplot_idx].plot(resolutions,
    #                               plmc_data,
    #                               color      = plmc_color,
    #                               linestyle  = data_linestyle,
    #                               linewidth  = linewidth,
    #                               marker     = plmc_marker,
    #                               markersize = data_markersize,
    #                               label      = 'PLMC')
    #     subPlot[subplot_idx].plot(resolutions,
    #                               ppmc_data,
    #                               color      = ppmc_color,
    #                               linestyle  = data_linestyle,
    #                               linewidth  = linewidth,
    #                               marker     = ppmc_marker,
    #                               markersize = 0.5*data_markersize,
    #                               label      = 'PPMC')

    #     # Plot the scaling lines
    #     scalingRes = [resolutions[0], resolutions[1], resolutions[-1]]
    #     # loop through the different scaling powers
    #     for i in [2]:
    #         label = r'$\mathcal{O}(\Delta x^' + str(i) + r')$'
    #         norm_point = plmc_data[1]
    #         scaling_data = np.array([norm_point / np.power(scalingRes[0]/scalingRes[1], i), norm_point, norm_point / np.power(scalingRes[-1]/scalingRes[1], i)])
    #         subPlot[subplot_idx].plot(scalingRes, scaling_data, color=scaling_color, alpha=alpha, linestyle=scaling_linestyle, linewidth=linewidth, label=label)

    #     # Set axis parameters
    #     subPlot[subplot_idx].set_xscale('log')
    #     subPlot[subplot_idx].set_yscale('log')
    #     subPlot[subplot_idx].set_xlim(1E1, 1E3)

    #     # Set ticks and grid
    #     subPlot[subplot_idx].tick_params(axis='both', direction='in', which='both', labelsize=tick_font_size, bottom=True, top=True, left=True, right=True)

    #     # Set axis titles
    #     if (subplot_idx[0] == 1):
    #         subPlot[subplot_idx].set_xlabel('Resolution', fontsize=axslabel_font_size)
    #     if (subplot_idx[1] == 0):
    #         subPlot[subplot_idx].set_ylabel(f'{norm_name}L2 Error', fontsize=axslabel_font_size)
    #     subPlot[subplot_idx].set_title(f'{pretty_names[wave]}', fontsize=subtitle_font_size)

    #     subPlot[subplot_idx].legend(fontsize=legend_font_size)

    # # Legend
    # # fig.legend()

    # # Whole plot settings
    # fig.suptitle(f'{norm_name}MHD Linear Wave Convergence', fontsize=suptitle_font_size)

    # plt.tight_layout()
    # plt.savefig(outPath / f'linear_convergence.pdf', transparent = True)
    # plt.close()
# ==============================================================================


if __name__ == '__main__':
    start = default_timer()
    main()
    print(f'Time to execute: {round(default_timer()-start,2)} seconds')