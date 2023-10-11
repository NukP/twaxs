import os
import h5py
from typing import Dict, Tuple, Any
from . import auxiliary as aux
"""   
This module contains functions that load and handles parsing of the raw data
"""  
class Dataset:
   
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
        self.height_group: int = height_group
        self._fln_raw: str
        self._fln_integrated: str
        self._fln_start_macro: int
        self._height_group_frame: Dict[int, Any] = {}  # Initialize the variable, will be populated later
        self._fln_raw, self._fln_integrated, self._fln_start_macro = self.get_fln_detail()

    def get_fln_detail(self) -> Tuple[str, str, int]:
        fln_base = self.dict_fln[self.fln] + '_0001'
        fln_raw = os.path.join('Data', fln_base + '_raw.h5')
        fln_integrated = os.path.join('Data', fln_base + '_integrated.h5')
        fln_start_macro = self.dict_macro_start[self.fln]
        return fln_raw, fln_integrated, fln_start_macro

    @property
    def fln_raw(self) -> str:
        return self._fln_raw

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
    
def group_heights(h_array: Dict[int,int]) -> Dict[int,int]: 
    '''
    This function sort the peak the number of peak position at to 4 groups (3 experimental height and 1 controlled height)
    '''
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