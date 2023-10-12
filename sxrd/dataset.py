import os
import h5py
from typing import Dict, Any, List, Tuple, Optional
import plotly.graph_objects as go
from IPython.display import display, clear_output
from ipywidgets import interactive, SelectionSlider, IntSlider, Checkbox
from . import auxiliary as aux
"""   
This module contains functions that load and handles parsing of the raw data.
Cerntain information specific to experimental files obtaining from a beamtime during 14-18 th  September 2023
was incoperated here for smooth parsing of the raw data. For other set of experiment, please adjust these 
conditions acordingly. 
"""  
class LoadData:
   
    dict_fln: Dict[str, str] = {
        '6': '06_s01',
        '11': '11_s01',
        '12': '12_s06',
        '13': '13_S11',
        '14': '14_S03',
        '15': '15_s05',
        '16': '16_s07',
        '17': '17_s13',
        '18': '18_s11',
        '19': '19_S14'
    }

    dict_macro_start: Dict[str, int] = {
        '6': 14,
        '11': 9,
        '12': 27,
        '13': 13,
        '14': 15,
        '15': 19,
        '16': 16,
        '17': 17,
        '18': 10,
        '19': 6
    }

    def __init__(self, fln: int, height_group: int):
        self.fln: str = str(fln)
        self._height_group: int = height_group
        self._fln_raw: str = None
        self._fln_integrated: str = None
        self._fln_start_macro: int = None
        self._height_group_frame: Dict[int, Any] = {}
        self._fln_raw, self._fln_integrated, self._fln_start_macro = self.get_fln_detail()

    def get_fln_detail(self) -> Tuple[str, str, int]:
        fln_base = self.dict_fln.get(self.fln)
        if fln_base is None:
            return None, None, None

        fln_base += '_0001'
        fln_raw = os.path.join('Data', fln_base + '_raw.h5')
        fln_integrated = os.path.join('Data', fln_base + '_integrated.h5')
        fln_start_macro = self.dict_macro_start.get(self.fln, None)
        return fln_raw, fln_integrated, fln_start_macro

    @property
    def fln_raw(self) -> str:
        return self._fln_raw

    @property
    def height_group(self) -> int:
        return self._height_group

    @property
    def fln_num(self) -> str:
        return self.fln

    @property
    def fln_integrated(self) -> str:
        return self._fln_integrated

    @property
    def fln_start_macro(self) -> int:
        return self._fln_start_macro

    def get_max_frame_index(self, filename: str) -> int:
        with h5py.File(filename, 'r') as f:
            keys = list(f.keys())
            frame_indices = [int(key.split('.')[0]) for key in keys if '.' in key]
            return max(frame_indices)

    def get_height_array(self, start: int, num_end: int) -> Dict[int, Any]:
        end = self.get_max_frame_index(self._fln_raw) if num_end == 0 else num_end
        dict_height = {}
        for scan_num in range(start, end+1):
            height = aux.get_data(fln=self._fln_raw, dataset_path=f'{scan_num}.1/instrument/positioners/h1tz')
            dict_height[scan_num] = height
        return dict_height

    @property
    def height_group_frame(self) -> Dict[int, Any]:
        if not self._height_group_frame:
            end_num = 148 if self.fln == '12' else 0
            height_array = self.get_height_array(self._fln_start_macro, end_num)
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
                'text': f'Exp: {self.fln_num}, Height group: {self.height_group}',
                'y':0.9,  
                'x':0.5, 
                'xanchor': 'center',  
                'yanchor': 'top'  
            },
            xaxis_title='q',
            yaxis_title='Count',
            width=1600,
            height=600,
            legend=dict(
                x=1,  
                y=1,  
                traceorder="normal",
                font=dict(
                    family="sans-serif",
                    size=15,
                    color="black"
                ),
                bgcolor="White",
                bordercolor="Black",
                borderwidth=2
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
        def plot_data(n, position, bg_substract):
            x = aux.get_data(fln=self._fln_integrated, dataset_path=f'{n}.1/p3_integrate/integrated/q')
            y_0 = aux.get_data(fln=self._fln_integrated, dataset_path=f'{self.height_group_frame[0]}.1/p3_integrate/integrated/intensity')[position]
            y_n = aux.get_data(fln=self._fln_integrated, dataset_path=f'{n}.1/p3_integrate/integrated/intensity')[position]

            y = y_n - y_0 if bg_substract else y_n

            # Update the data in the existing figure
            fig.data[0].x = x
            fig.data[0].y = y
            clear_output(wait=True)

        max_positions = 0
        for n in self.height_group_frame:
            Y = aux.get_data(fln=self._fln_integrated, dataset_path=f'{n}.1/p3_integrate/integrated/intensity')
            max_positions = max(max_positions, len(Y))

        # Create interactive sliders and checkbox
        interactive_plot = interactive(
            plot_data,
            n=SelectionSlider(options=self.height_group_frame, description='Scan number'),
            position=IntSlider(min=0, max=max_positions-1, step=1, description='Position'),
            bg_substract=Checkbox(value=False, description='Background Subtraction')
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