"""  
This module contain functions that used to visualized the analyzed data.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from typing import List, Dict, Any, Union
from . import auxiliary as aux
from .dataset import LoadData

def heatmap(dataset:LoadData, min_range: float, max_range: float, export_data: str = None, display_rxn_time: bool = False) -> None:
    """
    Plots a heatmap based on the intensity of peaks as a function of the q range and scan number. The script will 
    extract the entire intensity in all of the space of q and scan number in the particular experiment.

    :param datasey: dataset object of the associated experiment.
    :param min_range: Minimum range of q values.
    :param max_range: Maximum range of q values.
    :param export_data: Whether or not to export data in excel format.
    :param display_rxn_time: If True, display reaction time. If False, display scan number.
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
    if display_rxn_time:
        array_timestamp = [aux.get_scan_time(fln=dataset.fln_raw,scan_num=f) for f in height_group_frame]
        array_rxn_time = [(t-array_timestamp[0])/60 for t in array_timestamp]
        y = np.array(array_rxn_time)
    else:
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
    if display_rxn_time:
        x_label = 'Time (min)'
    else:
        x_label = 'Scan number'
    plt.xlabel(x_label)
    plt.ylabel('Position')
    plt.title(f'Exp: {fln_num}, height group: {height_group}, q range = [{min_range},{max_range}]')
    ax = plt.gca()
    ax.minorticks_on()
    y_ticks = np.linspace(0, max_positions-1, 11)  
    ax.set_yticks(y_ticks)
    ax.yaxis.set_major_locator(ticker.FixedLocator(y_ticks))
    plt.show()
    if export_data:
        data = {
            x_label: y.flatten(),
            'Position': x.flatten(),
            'Maximum peak height': z.flatten()
        }
        df = pd.DataFrame(data)
        df.to_excel(export_data, index=False)

def compare_peak_fe(dataset:LoadData,
                    x_min: float, 
                    x_max: float,
                    position_range: Union[int, List[int]],
                    smoothing_window: Union [None, int] = None,
                    n_pol: int =3,
                    axis_y_log: bool = False,
                    axis_y_min: Union[bool, int] = False,
                    axis_y_max: Union[bool, int] = False,
                    axis_x_min: Union[bool, int] = False,
                    axis_x_max: Union[bool, int] = False, 
                    export_table: Union[bool, str] = False) -> None:
    """  
    Function to plot the X-ray intensity and the Faradaic efficiency for H2 and C2H4 (for Cu) or CO (For Ag).
    This function also includes a built-in smoothing function for the X-ray data and the ability to export the X-ray data and the FE into an excel file.
    """
    fln_num = int(dataset.fln_num)
    height_group = dataset.height_group
    # Convert single position to a list
    if isinstance(position_range, int):
        position_range = [position_range]

    # Collect data for all positions
    dfs_xray = []
    for pos in range(position_range[0], position_range[-1]+1):
        dfs_xray.append(aux.get_peak_height_time(dataset, x_min, x_max, pos, smoothing_window, n_pol))

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

def peak_span (dataset:LoadData,
               x_min: float,
               x_max: float,
               position: int,
               n_plot: int,
               export_table: Union[bool, str] = False) -> None:
    """
    Function to plot peaks in the designated range at specific scan interval to check the peak broadening.

    :param datasey: dataset object of the associated experiment.
    :param x_min: minimum q-range of the plotting window.
    :param x_max: maximum q-range of the plotting window.
    :param position: position of the scan.
    :param n_plot: number of plot to be overlayed.
    :export_table: if given, a path to export an Excel file containing peak information. 
    """
    def select_frames(frame_list: List[int], n: int) -> List[int]:
        """
        Selects 'n' evenly spaced frames from a given list of frame numbers.
        
        The function calculates the step size and the starting index to ensure that
        the frames are as evenly distributed as possible across the list. If 'n' is
        greater than the number of frames, it returns the entire list.
        
        Parameters:
        frame_list (List[int]): The list of frame numbers to select from.
        n (int): The number of frames to select.
        
        Returns:
        List[int]: A list containing the selected frame numbers.
        
        Raises:
        ValueError: If 'n' is a non-positive integer.
        """
        if n <= 0:
            raise ValueError("The number of frames to select must be a positive integer.")
        
        total_frames = len(frame_list)
        if n >= total_frames:
            return frame_list  # If n is greater than the list size, return the whole list.
        
        step = max(total_frames // n, 1)  # Ensure step is at least 1
        selected_frames = []

        # Calculate the starting index to make the distribution as even as possible
        start_index = (total_frames - (step * (n - 1))) // 2

        for i in range(n):
            # Calculate the index of the frame to be selected
            index = start_index + i * step
            # Append the selected frame to the list
            selected_frames.append(frame_list[index])

        return selected_frames
    
    selected_frames = select_frames(dataset.height_group_frame, n_plot)
    fig, ax = plt.subplots()
    ax.minorticks_on()
    df_export = pd.DataFrame()
    for frame in selected_frames:
        df_frame = aux.export_spectrum(data=dataset, scan_num=frame, position=position)
        idx = [i for i in range(0,len(df_frame)) if df_frame['q'][i] > x_min and df_frame['q'][i] < x_max]
        plt.plot(df_frame['q'][idx], df_frame['count'][idx], label=f'Scan number: {frame}', marker='.')
        df_export.insert(len(df_export.columns),f'q - frame:{frame}', df_frame['q'][idx])
        df_export.insert(len(df_export.columns),f'count - frame:{frame}', df_frame['count'][idx])
    plt.legend()
    plt.xlabel('q')
    plt.ylabel('count')

    if export_table is not False:
        df_export.to_excel(export_table, index=False)

def vertical_compare(dataset: LoadData,
                     x_min: float, 
                     x_max: float,
                     scan_number: Union[int, List[int]],
                     export_table: Union[bool, str] = False) -> None:
    """
    Function to plot the highest peak intensity within a given q-range as a function of position for a specified scan number.
    
    :param dataset: dataset object of the associated experiment.
    :param x_min: Minimum q-value for the selection window.
    :param x_max: Maximum q-value for the selection window.
    :param scan_number: Scan number(s) to be included in the plot (can be a single value or a list).
    :param export_table: If provided, path to export an Excel file containing the plotted data.
    """
    # Convert single scan number to a list if it's not already a list
    if isinstance(scan_number, int):
        scan_number = [scan_number]

    # Initialize a dictionary to store peak heights for each position
    peak_heights_dict = {}

    # Loop through each scan number
    for scan in scan_number:
        # Retrieve the intensity data for the given scan number
        Y = aux.get_data(fln=dataset.fln_integrated, dataset_path=f'{scan}.1/p3_integrate/integrated/intensity')
        X = aux.get_data(fln=dataset.fln_integrated, dataset_path=f'{scan}.1/p3_integrate/integrated/q')
        
        # Find the peak height for each position within the q-range
        for pos in range(len(Y)):
            peak_height = aux.find_peak_height(X=X, Y=Y[pos], x_min=x_min, x_max=x_max)
            if pos in peak_heights_dict:
                peak_heights_dict[pos].append(peak_height)
            else:
                peak_heights_dict[pos] = [peak_height]

    # Calculate the average peak height for each position
    positions = list(peak_heights_dict.keys())
    avg_peak_heights = [np.mean(peak_heights_dict[pos]) for pos in positions]

    # Plot the average peak heights as a function of position
    fig, ax = plt.subplots()
    ax.minorticks_on()
    plt.plot(positions, avg_peak_heights, marker='.', linestyle='-', color='royalblue', alpha=0.9)
    plt.xlabel('Position')
    plt.ylabel('Average Maximum Peak Height')
    plt.title(f'Exp: {dataset.fln_num}, height group: {dataset.height_group},peak range=[{x_min},{x_max}], scan_num = {scan_number}')
    plt.show()

    # Export the data to an Excel file if requested
    if export_table:
        df_export = pd.DataFrame({
            'Position': positions,
            'Average Peak Height': avg_peak_heights
        })
        df_export.to_excel(export_table, index=False)
    
    
    





