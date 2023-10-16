""" 
This module contains functions that helps analyze the raw data which can be used by the plotting functions in the plot module. 
"""

import h5py
import numpy as np
import pandas as pd
import os
from dateutil.parser import parse
from scipy.signal import savgol_filter
from typing import List, Union, Optional, Any



def get_data(fln: str, dataset_path: str) -> Any:
    """
    Extract data from a specified hdf5 file and dataset path.

    Parameters:
    fln (str): The file path for the hdf5 file.
    dataset_path (str): The specific dataset path within the hdf5 file.

    Returns:
    Any: The data found at the specified dataset path within the file.
    """
    with h5py.File(fln, 'r') as f:
        data = f[dataset_path][()]
    return data

def find_peak_height(X: Union[List[float], np.ndarray], 
                     Y: Union[List[float], np.ndarray], 
                     x_min: float, 
                     x_max: float) -> Optional[float]:
    """
    Find the peak height in a given XRD diffractogram within a specified x range.

    Parameters:
    X (list or numpy array): The array of x values (2 theta or similar)
    Y (list or numpy array): The array of y values (intensity)
    x_min (float): The minimum x value of the range to consider
    x_max (float): The maximum x value of the range to consider

    Returns:
    float: The peak height in the given range, or None if the range is invalid
    """
    # Converting X and Y to numpy arrays if they are not already
    X = np.array(X)
    Y = np.array(Y)

    # Finding the indices of X values within the range [x_min, x_max]
    valid_indices = np.where((X >= x_min) & (X <= x_max))
    
    if len(valid_indices[0]) == 0:
        return None

    # Finding the peak height within the specified range
    peak_height = np.max(Y[valid_indices])
    
    return peak_height

def get_peak_height_time(dataset: 'LoadData',
                        x_min: float,
                        x_max: float,
                        position: int,
                        smoothing_window: Union[None, int] = None,
                        n_pol: int =2) -> pd.DataFrame:
    """
    This function returns a maximum peak height in the speciifc area at the given position as a function of time stamp. 
    """
    df_hight_time = pd.DataFrame(columns=['time', 'peak height'])
    raw_data = dataset.fln_raw
    frame = dataset.height_group_frame
    integrated_data = dataset.fln_integrated
    for n in frame:
        time = get_scan_time(raw_data, scan_num=n)
        intensity_data = get_data(fln=integrated_data, dataset_path=f'{n}.1/p3_integrate/integrated/intensity')[position]
        
        # If smoothing is desired, apply the Savitzky-Golay filter
        if smoothing_window:
            # Ensure the window size is odd
            if smoothing_window % 2 == 0:
                smoothing_window += 1
            intensity_data = savgol_filter(intensity_data, smoothing_window, n_pol) 
        
        peak_height = find_peak_height(X=get_data(fln=integrated_data, dataset_path=f'{n}.1/p3_integrate/integrated/q'),
                                       Y=intensity_data,
                                       x_min=x_min,
                                       x_max=x_max)
        df_hight_time.loc[len(df_hight_time)] = [time, peak_height]
        
    return df_hight_time

def get_scan_time(fln: str, scan_num: int) -> float:
    """    
    Get the time stamp of the scan in utx.
    """ 
    exp_timestamp = get_data(fln=fln, dataset_path=f'{scan_num}.1/start_time').decode('utf-8')
    exp_timestamp_epoc = float(parse(exp_timestamp).timestamp())
    return (exp_timestamp_epoc)

def get_fe(fln_num: int) -> pd.DataFrame:
    """ 
    This function take the experiment number (fln_num) and return an array of a dataframe containing utx time stamp and the Faradaic efficiency of different gas product. 
    """ 
    # Locate the Excel file based on fln_num
    dir_excel_gc = os.path.join('Analyzed_output', 'GC_Excel')
    for file in os.listdir(dir_excel_gc):
        if int(file.split('-')[1]) == fln_num:
            fln_excel = os.path.join(dir_excel_gc, file)
            break
    input_df = pd.read_excel(fln_excel)
    
    # Helper function get_col
    def get_col(input_df: pd.DataFrame, start_row: int = 2) -> List:
        """
        Extracts a column from input_df starting from start_row.
        
        :param input_df: The dataframe to process.
        :param start_row: The row index to start the extraction from.
        :return: A list representing the extracted column.
        """
        trans_col = []
        for idx in range(start_row, len(input_df)):
            trans_col.append(input_df[idx])
        return trans_col


    for idx_col, col_name in enumerate(input_df.columns):
        if col_name == 'fe':
            idx_fe = idx_col
    for idx_col_findFeEnding in range(idx_fe+1, len(input_df.columns)):
        col_name = input_df.columns[idx_col_findFeEnding]
        if col_name.split(':')[0] != 'Unnamed':
            fe_endRange = idx_col_findFeEnding
            break
    df_feGC = pd.DataFrame()   
    for idx_col_findChemicalName in range(idx_fe, fe_endRange):
         col_name = input_df.iloc[0, idx_col_findChemicalName]
         col_data = get_col(input_df.iloc[:, idx_col_findChemicalName])
         df_feGC.insert(len(df_feGC.columns), col_name, col_data)
    df_feGC.insert(len(df_feGC.columns), 'Overall', df_feGC.sum(axis=1))
    df_feGC.insert(0, 'time', get_col(input_df['Unnamed: 0']))
    
    return df_feGC

def export_spectrum(data: 'LoadData',
                    scan_num: int,
                    position: int, 
                    export_dir: str) -> None:
    """ 
    This function print the q and count value of the spectrum of a specific scan number and position
    """
    from . import dataset
    q = get_data(fln=data.fln_integrated, dataset_path=f'{scan_num}.1/p3_integrate/integrated/q')
    count = get_data(fln=data.fln_integrated, dataset_path=f'{scan_num}.1/p3_integrate/integrated/intensity')[position]
    df_export = pd.DataFrame({'q': q, 'count': count})
    df_export.to_excel(export_dir, index=False)
