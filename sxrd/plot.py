import numpy as np
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