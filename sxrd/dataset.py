"""   
This module contains functions that load and handles parsing of the raw data.
Cerntain information specific to experimental files obtaining from a beamtime during 14-18 th  September 2023
was incoperated here for smooth parsing of the raw data. For other set of experiment, please adjust these 
conditions acordingly. 
"""  
import pandas as pd
import h5py
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import plotly.graph_objects as go
from IPython.display import display, clear_output
from ipywidgets import interactive, SelectionSlider, IntSlider, Checkbox
from . import auxiliary as aux

class LoadData:
    """
    This class takes an experiment number and height group to create an object that processes properties 
    required for other functions used for analysis and visualizing data. 
    This class also includes a show_spectrum class function, allowing users to quickly visualize the spectrum.
    """
   
    def __init__(self, fl_num: int, height_group: int, data_info: Optional[str] = None):
        self.fl_num = fl_num  
        self._height_group = height_group
        self.data_info = data_info
        self._fl_integrated, self._fl_raw, self._fl_start_macro, self._fl_end_macro, self._condition = self.get_fl_detail()

    def get_fl_detail(self,
                      input_fl_integrated: Optional[str] = None,
                      input_fl_raw: Optional[str] = None, 
                      input_fl_start_macro: Optional[int] = None, 
                      input_fl_end_macro: Optional[int] = np.nan,
                      input_condition: Optional[str] = None,
                      input_pos_scan_motor: Optional[str] = 'pp01',
                      input_h_group_motor: Optional[str] = 'h1tz'
                      ) -> Tuple[str, str, int, Optional[int], str, str, str]:
        """
        Retrieves file details based on the experimental number. If data_info is provided, it fetches details from the Excel file,
        otherwise, it uses the provided input values.
        """
        if self.data_info:
            try:
                df_exp_info = pd.read_excel(self.data_info)
            except FileNotFoundError:
                raise Exception(f"Excel file not found: {self.data_info}")

            data_row = df_exp_info[df_exp_info['Experimental number'] == self.fl_num]

            if data_row.empty:
                raise ValueError(f"Experimental number {self.fl_num} not found in the data.")


            fl_integrated_path = Path(data_row['Integrated file directory'].values[0]).resolve()
            fl_raw_path = Path(data_row['Raw file directory'].values[0]).resolve()

            fl_start_macro = data_row['Macro start number'].values[0]
            fl_end_macro = data_row['Macro end number (optional)'].values[0] if not pd.isna(data_row['Macro end number (optional)'].values[0]) else None
            condition = data_row['Condition name'].values[0]
            pos_scan_motor = data_row['Position scanning motor'].values[0]
            h_group_motor = data_row['Height group motor'].values[0]
        else:
            fl_integrated_path = Path(input_fl_integrated).resolve() if input_fl_integrated else None
            fl_raw_path = Path(input_fl_raw).resolve() if input_fl_raw else None
            fl_start_macro = input_fl_start_macro
            fl_end_macro = input_fl_end_macro
            condition = input_condition
            pos_scan_motor = input_pos_scan_motor
            h_group_motor = input_h_group_motor

            if not all([fl_integrated_path, fl_raw_path, fl_start_macro, condition, pos_scan_motor, h_group_motor]):
                raise ValueError("All file details must be provided if not using an Excel file.")

        return str(fl_integrated_path), str(fl_raw_path), fl_start_macro, fl_end_macro, condition, pos_scan_motor, h_group_motor

    @property
    def fl_raw(self) -> str:
        return self._fl_raw

    @property
    def height_group(self) -> int:
        return self._height_group

    @property
    def fl_integrated(self) -> str:
        return self._fl_integrated

    @property
    def fl_start_macro(self) -> int:
        return self._fl_start_macro
    
    @property
    def fl_end_macro(self) -> Optional[int]:
        return self._fl_end_macro

    def get_max_frame_index(self) -> int:
        with h5py.File(self.fl_raw, 'r') as f:
            keys = list(f.keys())
            frame_indices = [int(key.split('.')[0]) for key in keys if '.' in key]
            return max(frame_indices)

    def get_height_array(self, start: int, num_end: int) -> Dict[int, Any]:
        if pd.isna(num_end):
            end = self.get_max_frame_index()
        else:
            end = int(num_end)
        dict_height = {}
        for scan_num in range(start, end+1):
            height = aux.get_data(fl=self._fl_raw, dataset_path=f'{scan_num}.1/instrument/positioners/h1tz')
            dict_height[scan_num] = height
        return dict_height

    @property
    def height_group_frame(self) -> Dict[int, Any]:
        height_array = self.get_height_array(self._fl_start_macro, self._fl_end_macro)
        grouped_height_array = group_heights(height_array)
        self._height_group_frame = grouped_height_array[self.height_group]
        return self._height_group_frame
    
    def show_spectrum(self, xref_list: Optional[List] = None):
        # Function to draw vertical bars and legend labels
        def ybar_plotly(fig, x, label, thick=0.02, alpha=0.25, color='green'):
            fig.add_shape(
                type="rect",
                x0=x-thick,
                x1=x+thick,
                y0=0,
                y1=1,
                fillcolor=color,
                opacity=alpha,
                line=dict(width=0),
                xref="x",
                yref="paper"
            )
            if label:  # Add a legend entry only if a label is provided
                fig.add_trace(
                    go.Scatter(
                        x=[None],  
                        y=[None],
                        mode="markers",
                        marker=dict(color=color),
                        name=label,
                        showlegend=True,
                        legendgroup=label  
                    )
                )

        # Initialize your figure
        fig = go.FigureWidget()
        fig.update_layout(
            title={
                'text': f'Exp: {self.fl_num}, Height group: {self.height_group} <br> Condition: {self._condition}',
                'y':0.9,  
                'x':0.5, 
                'xanchor': 'center',  
                'yanchor': 'top',
            },
            title_font=dict(size=20),  
            xaxis_title='q',
            yaxis_title='Count',
            width=1600,
            height=600,
            legend=dict(
                x=1,  # Legend x position
                y=1,  # Legend y position
                traceorder="normal",
                font=dict(
                    family="sans-serif",
                    size=15,
                    color="black"
                ),
                bgcolor="White",
                bordercolor="White",
                borderwidth=0
                )
        )

        # Add a primary trace for the data
        fig.add_trace(go.Scatter(x=[], y=[], mode='lines', line=dict(color='red', width=2), name="Spectrum", opacity=0.7, showlegend=False))

        # If xref_list is provided, add bars and legends
        if xref_list is not None:
            for item in xref_list:
                xrefs, color, label = item
                added_legend = False
                for pos in xrefs:
                    ybar_plotly(fig, pos, label if not added_legend else '', thick=0.01, color=color)
                    added_legend = True

        display(fig)

        # Function to update the plot with new data
        def plot_data(n: int, position: int, bg_substract: bool, log_scale: bool) -> None:
            x = aux.get_data(fl=self._fl_integrated, dataset_path=f'{n}.1/p3_integrate/integrated/q')
            y_0 = aux.get_data(fl=self._fl_integrated, dataset_path=f'{self.height_group_frame[0]}.1/p3_integrate/integrated/intensity')[position]
            y_n = aux.get_data(fl=self._fl_integrated, dataset_path=f'{n}.1/p3_integrate/integrated/intensity')[position]

            y = y_n - y_0 if bg_substract else y_n

            # Update the data in the existing figure
            fig.data[0].x = x
            fig.data[0].y = y
            fig.update_yaxes(type='log' if log_scale else 'linear')
            clear_output(wait=True)

        max_positions = 0
        for n in self.height_group_frame:
            Y = aux.get_data(fl=self._fl_integrated, dataset_path=f'{n}.1/p3_integrate/integrated/intensity')
            max_positions = max(max_positions, len(Y))

        # Create interactive sliders and checkbox
        interactive_plot = interactive(
            plot_data,
            n=SelectionSlider(options=self.height_group_frame, description='Scan number'),
            position=IntSlider(min=0, max=max_positions-1, step=1, description='Position'),
            bg_substract=Checkbox(value=False, description='Background Subtraction'),
            log_scale=Checkbox(value=False, description='Log Scale Y')
        )
        display(interactive_plot)
        

def group_heights(h_array: Dict[int,int]) -> Dict[int,int]: 
    """
    This function sort the peak the number of peak position at to 4 groups (3 experimental height and 1 controlled height)
    """
    rounded_h_array = {k: round(v, 3) for k, v in h_array.items()}
    groups = {}
    for scan_num, height in rounded_h_array.items():
        if height not in groups:
            groups[height] = []
        groups[height].append(scan_num)
    unique_heights = sorted(groups.keys())
    h_list = [groups[height] for height in unique_heights]
    control_height = min(unique_heights, key=lambda x: len(groups[x]))
    for i, height in enumerate(unique_heights):
        height_type = "control height" if height == control_height else f"height {i}"
        #print(f"list position {i}; {height_type} at {height} mm")
    return h_list