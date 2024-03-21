from setuptools import setup, find_packages

setup(
    name="twaxs",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
    'h5py',
    'matplotlib',
    'ipywidgets',
    'IPython',
    'plotly',
    'numpy',
    'pandas',
    'scipy',
    'python-dateutil',
    'openpyxl',
    'ipykernel',
    'pathlib'
    ],
)
