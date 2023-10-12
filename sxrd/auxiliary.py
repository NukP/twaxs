import h5py
import numpy as np
from typing import List, Union, Optional, Any
""" 
This module contains functions that helps analyze the raw data which can be used by the plotting functions in the plot module. 
"""

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