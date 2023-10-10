import os
from typing import Dict, Tuple
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

    def __init__(self, fln: int):
        self.fln: str = str(fln)
        self._fln_raw: str
        self._fln_integrated: str
        self._fln_start_macro: int
        self._fln_raw, self._fln_integrated, self._fln_start_macro = self.get_fln_detail()

    def get_fln_detail(self) -> Tuple[str, str, int]:
        fln_base = self.dict_fln[self.fln] + '_0001'
        fln_raw = os.path.join('Data', fln_base + '_raw.h5')
        fln_integrated = os.path.join('Data', fln_base + '_integrated.h5')
        fln_start_macro = self.dict_macro_start[self.fln]
        return fln_raw, fln_integrated, fln_start_macro

    @property
    def file_name(self) -> str:
        return self._fln_raw

    @property
    def fln_integrated(self) -> str:
        return self._fln_integrated

    @property
    def start_macro(self) -> int:
        return self._fln_start_macro