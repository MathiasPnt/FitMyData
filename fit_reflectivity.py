# -*- coding: utf-8 -*-
"""
@Authors: Mathias Pont
@Contributors:

This script gets the central frequency, width and quality factor of a microcavity.

Input: .txt file downloaded from your computer using the app. Reflectivity spectrum
measured with a broadband LED and a spectrometer. x axis is WL in px. y axis is intensity.

Output: Displays a graph and gives the central frequency of the fondamental mode, the FWHM and the quality factor
of the microcavity.

Do not forget to calibrate your spectrometer !!

Comments:
Here is how to export ASCII from Winspec to get the good format for your .txt file:
File Extension: txt
Delimiter = Tab            Output order = Pixel, Intensity
X-Axis unit = pixel        New Line Characters = Carriage return: yes, Line Feed: yes.
Output File Options = One File For All Frames and Single Column
Pixel Format = Convert CCD X/Y Dimension into 1 Dimension

"""

import numpy as np
from lmfit.models import LorentzianModel, QuadraticModel
import heapq
from scipy.signal import find_peaks
import streamlit as st
import plotly.graph_objects as go
from plotly.graph_objs import *
import os

# Data must be in a .txt file with 2 columns:
# column 1 = x abscisse in px
# column 2 = intensity

demo_mode = st.checkbox('Use demo mode', help="if you don't have your own datasets to test the software")

if demo_mode:
    file = "demo"
    data = np.loadtxt(os.getcwd()+"/demo_data/demo_reflectivity.txt")[:,1]
else:
    # Upload a file from your computer.
    file = st.file_uploader('Load data', type={"txt"})

if file is not None:
    if file != "demo":
        # We only use the y axis stored in the second column of the .txt file here.
        data = np.loadtxt(file)[:, 1]


    # Conversion from px to eV
    def px_to_eV(spectro, px, calib):
        return 1239.8 / (spectro - (670 - px) * 1 / calib)

    # Conversion from px to nm
    def px_to_nm(spectro, px, calib):
        return spectro - (670 - px) * 1 / calib

    # Conversion from px to nm
    def eV_to_nm(eV):
        return 1239.8/eV

    # Create the X axis of the camera in px depending on the horizontal size
    def get_Xaxis(nb_px):
        return np.arange(1, nb_px + 1, 1)

    # get energy (in eV) axis
    def get_Eaxis(spectro, nb_px, calib):
        return px_to_eV(spectro, get_Xaxis(nb_px), calib)

    # get WL (in nm) axis
    def get_WLaxis(spectro, nb_px, calib):
        return px_to_nm(spectro, get_Xaxis(nb_px), calib)


    # Toolbox for fit.
    def add_peak(prefix, center, amplitude=-1000, sigma=100e-6):
        peak = LorentzianModel(prefix=prefix)
        pars = peak.make_params()
        pars[prefix + "center"].set(center)
        pars[prefix + "amplitude"].set(amplitude)
        pars[prefix + "sigma"].set(sigma)
        return peak, pars

    # !!!! Calibration !!!!

    # Nb of pixel on the camera (horizontal axis)
    Nb_px = st.sidebar.number_input('Nb of pixel on the camera (horizontal axis)', value = 1340)

    # Center WL of the spectro meter (corresponds to the WL of px 670)
    Spectro = st.sidebar.number_input('WL of central pixel [nm]', value = 924.4782)

    # Conversion between px and nm (... px = 1 nm)
    Calib = st.sidebar.number_input('Calibration [px/nm]', value = 45.34942)

    # create E axis
    E = get_Eaxis(Spectro, Nb_px, Calib)

    xdat = get_Eaxis(Spectro, Nb_px, Calib)
    ydat = data

    model = QuadraticModel(prefix="bkg_")
    params = model.make_params(a=0, b=0, c=0)

    peaks, properties = find_peaks(-ydat, prominence=300, width=3)

    peaks_size = properties["prominences"]
    max_peak = np.argmax(peaks_size)

    # Find the number_of_elements largest peaks in peaks.
    # This is usefull is you see many modes that are too close to each other. If you only see one use 1
    number_of_elements = st.sidebar.number_input('Number of modes', value = 1)
    largest_peaks = heapq.nlargest(number_of_elements, enumerate(peaks_size), key=lambda x: x[1])

    CenterPx = peaks[max_peak]
    # This might need to be adapted depending on the width of the cabvity
    # Try more or less, but around 100 is good for Q = 10 000
    zoom_fit = st.sidebar.number_input('Zoom fit', value=75)
    start = CenterPx - zoom_fit
    stop = CenterPx + zoom_fit

    ydat_fit = ydat[start:stop]
    xdat_fit = xdat[start:stop]

    rough_peak_positions = ()
    for i in [peaks[x] for x in [idx[0] for idx in largest_peaks]]:
        rough_peak_positions += (px_to_eV(Spectro, i, Calib),)

    for i, cen in enumerate(rough_peak_positions):
        peak, pars = add_peak("lz%d_" % (i + 1), cen)
        model = model + peak
        params.update(pars)

    init = model.eval(params, x=xdat_fit)
    result = model.fit(ydat_fit, params, x=xdat_fit)
    xc = result.params["lz1_center"].value
    sigma = result.params["lz1_sigma"].value

    FWHM = 2*sigma

    Q = round(xc / FWHM, 2)
    FWHM = round(FWHM * 1e6, 2)
    xc = round(xc, 6)

    title_fig = "xc = " + str(round(xc,5))+"eV | κ = " + str(FWHM) + " µeV" + " | Q = " + str(Q)
    layout = Layout(
        plot_bgcolor='whitesmoke'
    )
    fig = go.Figure(layout=layout)
    fig.add_trace(go.Scatter(
        x=xdat,
        y=ydat,
        name="Data",
        mode='lines+markers',
        marker = dict(color='darkcyan', size=6),
        line=dict(color='teal', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=xdat_fit,
        y=result.best_fit,
        name="Fit",
        line=dict(color='gold', width=2, dash='dash')
    ))
    fig.update_layout(title=title_fig,
                        title_font_size=18,
                        width=800, height=500,
                        margin=dict(l=40, r=40, b=40, t=40),
                        xaxis_title="Energy [eV]",
                        yaxis_title="Counts",
                        legend_title="Legend",
                      xaxis=dict(tickformat="000"),
                      yaxis=dict(tickformat="000")
    )
    st.plotly_chart(fig)







