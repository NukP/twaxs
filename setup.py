from setuptools import setup, find_packages

setup(
    name="sxrd",
    version="1.1.2",
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
    'python-dateutil'
    ],
)
