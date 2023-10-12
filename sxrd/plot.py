import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from typing import List, Dict, Any
from . import auxiliary as aux

"""  
This module contain functions that used to visualized the analyzed data.
"""

def heatmap(dataset, min_range: float, max_range: float) -> None:
    """
    Plots a heatmap based on the intensity of peaks as a function of the q range and scan number. The script will 
    extract the entire intensity in all of the space of q and scan number in the particular experiment.

    :param min_range: Minimum range of q values.
    :param max_range: Maximum range of q values.
    :param height_group_frame: List of scan numbers for the height group.
    :param integrated_data: File path or identifier for integrated data.
    :param fln_num: File identifier number.
    """
    max_positions = 0
    height_group_frame = dataset.height_group_frame
    fln_num = dataset.fln_num
    height_group = dataset.height_group
    integrated_data = dataset.fln_integrated
    for x_val in height_group_frame:
        Y = aux.get_data(fln=integrated_data, dataset_path=f'{x_val}.1/p3_integrate/integrated/intensity')
        max_positions = max(max_positions, len(Y))

    x = np.linspace(0, max_positions-1, max_positions)
    y = np.array(height_group_frame)  # ensure this is numpy array for operations later on
    x, y = np.meshgrid(x, y)

    z = np.empty_like(x)

    for i, y_val in enumerate(height_group_frame):
        X = aux.get_data(fln=integrated_data, dataset_path=f'{y_val}.1/p3_integrate/integrated/q')
        Y = aux.get_data(fln=integrated_data, dataset_path=f'{y_val}.1/p3_integrate/integrated/intensity')
        
        for j, x_val in enumerate(x[i]):
            if 0 <= x_val < len(Y):
                z[i, j] = aux.find_peak_height(X=X, Y=Y[int(x_val)], x_min=min_range, x_max=max_range)
            else:
                z[i, j] = np.nan  

    plt.imshow(z.T, extent=[y.min(), y.max(), 0, max_positions], origin='lower', aspect='auto', cmap='RdYlBu', interpolation='nearest')
    plt.colorbar(label='Maximum peak height')
    plt.xlabel('Scan number')
    plt.ylabel('Position')
    plt.title(f'Exp: {fln_num}, height group: {height_group}, q range = [{min_range},{max_range}]')
    ax = plt.gca()
    ax.minorticks_on()
    y_ticks = np.linspace(0, max_positions-1, 11)  
    ax.set_yticks(y_ticks)
    ax.yaxis.set_major_locator(ticker.FixedLocator(y_ticks))
    plt.show()

def compare_peak_fe(dataset,
                    x_min, 
                    x_max,
                    position_range,
                    height_list,
                    smoothing_window=None,
                    n_pol=3,
                    axis_y_log=False,
                    axis_y_min=False,
                    axis_y_max=False,
                    axis_x_min=False,
                    axis_x_max=False, 
                    export_table=False):
    """  
    Function to plot the X-ray intensity and the Faradaic efficiency for H2 and C2H4 (for Cu) or CO (For Ag).
    This function also includes a built-in smoothing function for the X-ray data and the ability to export the X-ray data and the FE into an excel file.
    """
    fln_num = dataset.fln_num
    height_group = dataset.height_group
    # Convert single position to a list
    if isinstance(position_range, int):
        position_range = [position_range]

    # Collect data for all positions
    dfs_xray = []
    for pos in range(position_range[0], position_range[-1]+1):
        dfs_xray.append(aux.get_peak_height_time(x_min, x_max, pos, fln_num, height_list, smoothing_window, n_pol))

    # Average the data
    avg_df_xray = dfs_xray[0].copy()
    for df in dfs_xray[1:]:
        avg_df_xray['peak height'] += df['peak height']
    avg_df_xray['peak height'] /= len(dfs_xray)

    df_fe = aux.get_fe(fln_num)
    x_0 = df_fe['time'][0]
    
    fig, ax1 = plt.subplots()

    # Plot the X-ray intensity
    y1_axis_color = 'royalblue'
    ax1.minorticks_on()
    ax1.tick_params(axis='y', which='both', colors=y1_axis_color)
    ax1.set_xlabel('Time (min)')
    ax1.set_ylabel('Intensity', color=y1_axis_color)
    ax1.tick_params(axis='y', colors=y1_axis_color)
    ax1.spines['left'].set_color(y1_axis_color)
    ax1.plot((avg_df_xray['time']-x_0)/60, avg_df_xray['peak height'], color=y1_axis_color, label='Average X-ray peak height')
    if axis_y_min is not False and axis_y_max is not False:
        ax1.set_ylim(axis_y_min, axis_y_max)
    if axis_x_min is not False and axis_x_max is not False:
        ax1.set_xlim(axis_x_min, axis_x_max)
    ax1.legend(loc=2)
    if axis_y_log:
        ax1.set_yscale('log')

    # Plot the FE
    time_adjusted = (df_fe['time']-x_0)/60
    ax2 = ax1.twinx()
    ax2.minorticks_on()
    ax2.plot(time_adjusted, df_fe['H2']*100, color='orangered', label='H$_2$')
    if fln_num in [6, 11, 12, 13, 14, 18]:
        ax2.plot(time_adjusted, df_fe['C2H4']*100, color='forestgreen', label='C$_2$H$_4$')
    elif fln_num in [15, 16, 17, 19]:
        ax2.plot(time_adjusted, df_fe['CO']*100, color='forestgreen', label='CO')
    else:
        print('Invalid file number')
    ax2.set_ylabel('Faradaic efficiency (%)')
    ax2.spines['left'].set_color(y1_axis_color)
    ax2.legend(loc=1)
    plt.title(f'Exp: {fln_num}, height group: {height_group},peak range=[{x_min},{x_max}], pos. = {position_range}')

    # Export the table for further plotting
    if export_table is not False:
        len_xray = len(avg_df_xray)
        len_fe = len(df_fe)

        max_len = max(len_xray, len_fe)

        if len_xray < max_len:
            avg_df_xray = avg_df_xray.reindex(range(max_len))
        if len_fe < max_len:
            df_fe = df_fe.reindex(range(max_len))

        df_export = pd.DataFrame({
            'X-ray time/min': (avg_df_xray['time']-x_0)/60,
            'Average X-ray peak intensity': avg_df_xray['peak height'],
            'FE_time/min': time_adjusted,
            'FE_H2 / %': df_fe['H2']*100 
        })

        if fln_num in [6, 11, 12, 13, 14, 18]:
            df_export['FE_C2H4 / %'] = df_fe['C2H4']*100
        elif fln_num in [15, 16, 17, 19]:
            df_export['FE_CO / %'] = df_fe['CO']*100

        df_export.to_excel(export_table, index=False)