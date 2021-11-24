#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 09:18:30 2021
@author: Mathias Pont
"""

import numpy as np
import matplotlib.pyplot as plt
import os
from lmfit.models import LorentzianModel, QuadraticModel
import heapq
from scipy.signal import find_peaks
import streamlit as st
import webbrowser
import plotly.graph_objects as go

# Data must be in a .txt file with 2 columns:
# column 1 = x abscisse in px
# column 2 = intensity

with st.expander("Load data"):

    folder1 = '/Users/mathias/Google Drive/CNRS/A-Projets/Internship Helio 2021/KAAE011/All_data_txt'
    folder = st.text_input("Select a folder", folder1)

    def file_selector(folder_path=folder):
        filenames = os.listdir(folder_path)
        selected_filename = st.selectbox('Select a file', filenames)
        return os.path.join(folder_path, selected_filename)

    filename = file_selector()
    st.write('You selected `%s`' % filename)
    if st.button('Show me what the data looks like'):
        webbrowser.get("open -a /Applications/Firefox.app %s").open_new('file://' + filename)

data = [np.loadtxt(filename), filename]


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

# get intensity specrum
def get_Spectrum(data):
    return data[0][:, 1]

# Name of the file. Should contain pillar name and experimental details.
def get_Title(data):
    return data[1]


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


def get_Q(file):

    xdat = get_Eaxis(Spectro, Nb_px, Calib)
    ydat = get_Spectrum(file)
    name = get_Title(file)

    model = QuadraticModel(prefix="bkg_")
    params = model.make_params(a=0, b=0, c=0)

    peaks, properties = find_peaks(ydat, prominence=300, width=3)

    peaks_size = properties["prominences"]
    max_peak = np.argmax(peaks_size)

    # Find the number_of_elements largest peaks in peaks.
    # This is usefull is you see many modes that are too close to each other. If you only see one use 1
    number_of_elements = st.sidebar.number_input('Number of peaks', value = 1)
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

    w = 2*sigma

    Q = round(xc / w, 2)
    w = round(w * 1e6, 2)
    xc = round(xc, 6)

    fig, ax = plt.subplots()
    ax.plot(xdat, ydat, "-o", label="data")
    ax.plot(xdat_fit, result.best_fit, label="best fit")
    ax.axvline(x=xc, linestyle="--")
    ax.set_title("$x_c$ = " + str(round(xc,5))+"eV | FWHM = " + str(w) + " µeV", size=14)
    st.pyplot(fig)

    #title_fig = "xc = " + str(round(xc,5))+"eV | κ = " + str(w) + " µeV" + " | Q = " + str(Q)
    #fig2 = go.Figure(data=[go.scatter(x=xdat, y=ydat),go.Scatter(x=xdat_fit, y=result.best_fit) ])
    #fig2.update_layout(title=title_fig, title_font_size=18, autosize=False,
    #                  width=800, height=500, margin=dict(l=40, r=40, b=40, t=40), template='plotly_white')
    #st.plotly_chart(fig2)


get_Q(data)






