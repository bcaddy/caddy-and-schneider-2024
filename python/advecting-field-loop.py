#!/usr/bin/env python3
"""
================================================================================
 Written by Robert Caddy.

 Generates the advecting field loop plots
================================================================================
"""

from timeit import default_timer
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import argparse
import pathlib
import scipy

import shared_tools

plt.close('all')

matplotlib.rcParams['font.sans-serif'] = "Helvetica"
matplotlib.rcParams['font.family'] = "sans-serif"
matplotlib.rcParams['mathtext.fontset'] = 'cm'
matplotlib.rcParams['mathtext.rm'] = 'serif'

# Values to loop over
resolutions   = [32, 64, 128, 256]
reconstructor = 'ppmc'
tout          = 2.0
outstep       = 0.1  # should be some even division of tout=2.0
num_outputs   = int(np.ceil(tout/outstep) + 1)
B_0           = 1E-3
radius        = 0.3

# Plotting data save path
save_path = shared_tools.repo_root / 'python' / 'afl.pkl'
save_path_slice  = shared_tools.repo_root / 'python' / 'afl_slice.pkl'

# ==============================================================================
def main():
    # Check for CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--in_path', help='The path to the directory that the source files are located in. Defaults to "~/Code/cholla/bin"')
    parser.add_argument('-o', '--out_path', help='The path of the directory to write the plots out to. Defaults to writing in the same directory as the input files')
    parser.add_argument('-r', '--run_cholla', action="store_true", help='Runs cholla to generate all the data')
    parser.add_argument('-f', '--figure', action="store_true", help='Generate the plots')
    parser.add_argument('-d', '--data', action="store_true", help='Load and generate the data to be plotted.')
    parser.add_argument('--slicedata', action="store_true", help='Load and generate the slice data to be plotted.')
    parser.add_argument('--slicefigure', action="store_true", help='Plot the slice figure')

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
        runCholla()

    if args.data:
        shared_tools.pickle_dictionary(load_data(), save_path)

    if args.figure:
        plotAFL(OutPath)
        shared_tools.update_plot_entry("afl", 'python/advecting-field-loop.py')

    if args.slicedata:
        shared_tools.pickle_dictionary(load_slices(), save_path_slice)

    if args.slicefigure:
        plotAFL_slice(OutPath)
        shared_tools.update_plot_entry("afl_slice", 'python/advecting-field-loop.py')

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
    divergence    = {}
    times         = {}
    for res in resolutions:
        key = f'{res}'

        b_squared_avg[key] = np.zeros(num_outputs)
        divergence[key]    = np.zeros(num_outputs)
        times[key]         = np.zeros(num_outputs)

        for i in range(num_outputs):
            file_name = f'afl_n{res}_{i}'

            temp_data = shared_tools.load_conserved_data(file_name, load_time=True, load_dx=True)
            temp_data = shared_tools.center_magnetic_fields(temp_data)

            b_squared_avg[key][i] = np.mean(temp_data['magnetic_x_centered']**2
                                    + temp_data['magnetic_y_centered']**2
                                    + temp_data['magnetic_z_centered']**2)

            div_x = (temp_data['magnetic_x'][1:, :, :]
                   - temp_data['magnetic_x'][:-1, :, :]) / temp_data['dx'][0]
            div_y = (temp_data['magnetic_y'][:, 1:, :]
                   - temp_data['magnetic_y'][:, :-1, :]) / temp_data['dx'][1]
            div_z = (temp_data['magnetic_z'][:, :, 1:]
                   - temp_data['magnetic_z'][:, :, :-1]) / temp_data['dx'][2]
            divergence[key][i] = np.max(div_x + div_y + div_z)

            times[key][i] = temp_data['time']

        b_squared_avg[key] /= b_squared_avg[key][0]

    return {'b_squared_avg':b_squared_avg, 'divergence':divergence, 'times':times}
# ==============================================================================

# ==============================================================================
def load_slices():

    def load_slice(filename):
        data = shared_tools.load_conserved_data(filename, load_gamma=True, load_resolution=True)
        data = shared_tools.center_magnetic_fields(data)
        data = shared_tools.compute_velocities(data)
        data = shared_tools.compute_derived_quantities(data, data['gamma'])

        B_energy = data['magnetic_energy']

        side_slice = B_energy[:,B_energy.shape[1]//2,:]

        top_slice = scipy.ndimage.rotate(B_energy, angle=45, axes=(1,2))
        top_slice = top_slice[:,15:-16,top_slice.shape[2]//2]

        return np.rot90(side_slice), np.rot90(top_slice)

    init_side, init_top   = load_slice('afl_n256_0')
    final_side, final_top = load_slice('afl_n256_10')

    max_val = np.max(np.array([init_side, final_side, init_top, final_top]))

    return {'init_side':init_side, 'init_top':init_top,
            'final_side':final_side, 'final_top':final_top, 'max':max_val}
# ==============================================================================

# ==============================================================================
def plotAFL(outPath):
    # Plotting info
    line_width         = 1
    marker_size        = 5
    colors             = {'32':'blue',    '64':'red',    '128':'green', '256':'purple'}
    line_style         = {'32':'dashdot', '64':'dashed', '128':'solid', '256':'dotted'}
    markers            = {'32':'o',       '64':'v',      '128':'s',     '256':'*'}

    # Setup figure
    fig, subPlot = plt.subplots(1, 2, figsize = (2*shared_tools.fig_width, shared_tools.fig_height))

    # Load data
    data = shared_tools.unpickle_dictionary(save_path)

    # Info for each sublot
    fields = ['b_squared_avg', 'divergence']
    subplot_indices = {'b_squared_avg':0, 'divergence':1}

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
                                         labelsize=shared_tools.tick_font_size,
                                         bottom=True, top=True, left=True, right=True)
        if field == 'b_squared_avg':
            subPlot[subplot_idx].set_ylim(top=1.0)
        if field == 'divergence':
            pass
            # subPlot[subplot_idx].set_ylim(bottom=0.0)
            subPlot[subplot_idx].set_yscale('log')

        # Set titles
        subPlot[subplot_idx].set_ylabel(f'{shared_tools.pretty_names[field]}', fontsize=shared_tools.font_size_normal)
        subPlot[subplot_idx].set_xlabel('Time', fontsize=shared_tools.font_size_normal)
        subPlot[subplot_idx].set_box_aspect(1)

        # Legend
        subPlot[subplot_idx].legend(fontsize=shared_tools.font_size_small)

    # Save the figure and close it
    fig.tight_layout()
    plt.savefig(outPath / f'afl.pdf', transparent = True)
    plt.close()
# ==============================================================================

# ==============================================================================
def plotAFL_slice(outPath):
    # Plotting info
    line_width         = 0.4
    num_contours       = 30
    font_size          = 20

     # Load data
    data = shared_tools.unpickle_dictionary(save_path_slice)

    # Setup figure
    figSize = 10.0
    fig, subPlot = plt.subplots(1,4, layout='constrained', figsize = (2*shared_tools.fig_width, shared_tools.fig_height))

    # Plot the data
    subPlot[0].imshow(data['init_top'],   vmin=0.0, vmax=data['max'], cmap='Blues')#shared_tools.color_maps["magnetic_energy"])
    subPlot[1].imshow(data['final_top'],  vmin=0.0, vmax=data['max'], cmap='Blues')#shared_tools.color_maps["magnetic_energy"])
    subPlot[2].imshow(data['init_side'],  vmin=0.0, vmax=data['max'], cmap='Blues')#shared_tools.color_maps["magnetic_energy"])
    subPlot[3].imshow(data['final_side'], vmin=0.0, vmax=data['max'], cmap='Blues')#shared_tools.color_maps["magnetic_energy"])

    # # Set ticks and grid
    for i in range(4):
        subPlot[i].tick_params(labelleft=False, labelbottom=False,bottom=False, left=False)

    # Set labels
    subPlot[0].text(.01, .99, r'$t=0.0$', ha='left', va='top', transform=subPlot[0].transAxes, fontsize=shared_tools.font_size_normal)
    subPlot[1].text(.01, .99, r'$t=1.0$', ha='left', va='top', transform=subPlot[1].transAxes, fontsize=shared_tools.font_size_normal)
    subPlot[2].text(.01, .99, r'$t=0.0$', ha='left', va='top', transform=subPlot[2].transAxes, fontsize=shared_tools.font_size_normal)
    subPlot[3].text(.01, .99, r'$t=1.0$', ha='left', va='top', transform=subPlot[3].transAxes, fontsize=shared_tools.font_size_normal)

    # Save the figure and close it
    plt.savefig(outPath / f'afl_slices.pdf', transparent = True)
    plt.close()
# ==============================================================================

if __name__ == '__main__':
    start = default_timer()
    main()
    print(f'Time to execute: {round(default_timer()-start,2)} seconds')