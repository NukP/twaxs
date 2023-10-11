import h5py
from typing import Any
''''    
This module contains functions that helps analyze the raw data which can be used by the plotting functions in the plot module. 
'''

def get_data(fln: str, dataset_path: str) -> Any:
    '''
    Extract data from a specified hdf5 file and dataset path.

    Parameters:
    fln (str): The file path for the hdf5 file.
    dataset_path (str): The specific dataset path within the hdf5 file.

    Returns:
    Any: The data found at the specified dataset path within the file.
    '''
    with h5py.File(fln, 'r') as f:
        data = f[dataset_path][()]
    return data