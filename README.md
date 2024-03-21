# T-WAXS

![twaxs_logo-02](https://github.com/NukP/twaxs/assets/127328032/4d70df27-e927-4628-975d-9175a0151571)

A Python package for visualizing and analyzing temporal wide-angle X-ray scattering (WAXS) data.

### Capabilities
- Reads diffraction pattern data directly from HDF5 files. This package was initially developed to visualize operando synchrotron data from Beamline ID31 at the European Synchrotron Radiation Facility (ESRF).
- The script can slice the data based on different motor heights and visualize the XRD pattern from the same motor height, representing the same position on the sample.

### Features
- Visualizes a diffractogram as a function of scan number (or time) and position, with the capability to overlay multiple reference standard XRD patterns and export a specific spectrum.
- Plots a heatmap of peak height (at a specific q-range) as a function of scan number (or time) and position, with the ability to export the plotted heatmap or the raw data.
- Plots peak height (from the specified q-range at a specific position) and the Faradaic efficiency of hydrogen or ethylene as a function of time (on a dual-axis graph).
- Plots the average peak height as a function of position.
- Allows specifying the motor used for scanning and height changes.

### Contributors
- [Nukorn Plainpan](https://github.com/NukP)

### Acknowledgements
This software was developed at the Materials for Energy Conversion Lab,

Swiss Federal Laboratories for Materials Science and Technology (Empa).
