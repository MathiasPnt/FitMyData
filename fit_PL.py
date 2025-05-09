# -*- coding: utf-8 -*-
"""
@Authors: Mathias Pont
@Contributors:

This script gets the central frequency and  width of a line (works for laser line too).

Input: .txt file downloaded from your computer using the app.

Output: Displays a graph and gives the central frequency of the most prominent peak and its FWHM.

Comments:
This is not very well commented. It is exactly the same as fit_reflectivity.py but for peaks instead of dips.

"""

import numpy as np
from lmfit.models import LorentzianModel, QuadraticModel
import heapq
from scipy.signal import find_peaks
import streamlit as st
import plotly.graph_objects as go
from plotly.graph_objs import *
import scipy.constants


# UTILS

# Conversion from px to eV
def px_to_eV(spectro, px, calib):
    return 1239.8 / (spectro - (670 - px) * 1 / calib)


# Conversion from px to nm
def px_to_nm(spectro, px, calib):
    return spectro - (670 - px) * 1 / calib


# Conversion from px to nm
def eV_to_nm(eV):
    return 1239.8 / eV


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


# Data must be in a .txt file with 2 columns:
# column 1 = x abscisse in px
# column 2 = intensity


def main():
    file = st.file_uploader('Load data', type={"txt"})

    if file is not None:
        data = np.loadtxt(file)[:, 1]

        # !!!! Calibration !!!!

        # Nb of pixel on the camera (horizontal axis)
        Nb_px = st.sidebar.number_input('Nb of pixel on the camera (horizontal axis)', value=1340)

        # Center WL of the spectro meter (corresponds to the WL of px 670)
        Spectro = st.sidebar.number_input('WL of central pixel [nm]', value=924.4782)

        # Conversion between px and nm (... px = 1 nm)
        Calib = st.sidebar.number_input('Calibration [px/nm]', value=45.34942)

        # create E axis
        E = get_Eaxis(Spectro, Nb_px, Calib)

        # Fit
        xdat = get_Eaxis(Spectro, Nb_px, Calib)
        ydat = data

        model = QuadraticModel(prefix="bkg_")
        params = model.make_params(a=0, b=0, c=0)

        peaks, properties = find_peaks(ydat, prominence=300, width=3)

        peaks_size = properties["prominences"]
        max_peak = np.argmax(peaks_size)

        # Find the number_of_elements largest peaks in peaks.
        # This is usefull is you see many modes that are too close to each other. If you only see one use 1
        number_of_elements = st.sidebar.number_input('Number of peaks', value=1)
        largest_peaks = heapq.nlargest(number_of_elements, enumerate(peaks_size), key=lambda x: x[1])

        CenterPx = peaks[max_peak]
        # This might need to be adapted depending on the width of the cavity
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

        FWHM = 2 * sigma

        # Get pulse duration from width (transform-limited)
        # We define TBP_gauss = ∆nu*∆tau
        c0 = scipy.constants.c
        delta_nu = c0 * FWHM / xc ** 2
        TBP_gauss = 2 * np.log(2) / np.pi
        delta_tau = TBP_gauss / delta_nu

        title_fig = "xc = " + str(round(xc, 5)) + "eV | κ = " + str(round(FWHM * 1e6, 2)) + " µeV"
        layout = Layout(
            plot_bgcolor='whitesmoke'
        )
        fig = go.Figure(layout=layout)
        fig.add_trace(go.Scatter(
            x=xdat,
            y=ydat,
            name="Data",
            mode='lines+markers',
            marker=dict(color='darkcyan', size=6),
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


if __name__ == "__main__":
    main()
