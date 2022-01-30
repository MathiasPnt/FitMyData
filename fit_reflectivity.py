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
from lmfit.models import LorentzianModel, LinearModel
import heapq
from scipy.signal import find_peaks
import streamlit as st
import plotly.graph_objects as go
from plotly.graph_objs import *
import os
import pandas as pd


# Conversion from px to eV
def px_to_eV(spectro, px, calib):
    return 1239.8 / (spectro - (670 - px) * 1 / calib)


# Conversion from px to nm
def px_to_nm(spectro, px, calib):
    return spectro - (670 - px) * 1 / calib


# Conversion from px to nm
def eV_to_nm(eV):
    return np.array([1239.8 / E for E in eV])


def nm_to_eV(nm):
    return np.array([1239.8 / WL for WL in nm])


# Create the X axis of the camera in px depending on the horizontal size
def get_Xaxis(nb_px):
    return np.arange(1, nb_px + 1, 1)


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


def fit_cav(x, y, start_search, stop_search, number_of_elements, zoom_fit):

    xdat = x[start_search:stop_search]
    ydat = y[start_search:stop_search]

    model = LinearModel(prefix="bkg_")
    params = model.make_params(a=0, b=0)

    peaks, properties = find_peaks(-ydat, prominence=np.max(-ydat) / 2)

    peaks_size = properties["prominences"]
    max_peak = np.argmax(peaks_size)

    largest_peaks = heapq.nlargest(number_of_elements, enumerate(peaks_size), key=lambda x: x[1])

    CenterPx = peaks[max_peak]

    start_fit = CenterPx - zoom_fit
    stop_fit = CenterPx + zoom_fit

    ydat_fit = ydat[start_fit:stop_fit]
    xdat_fit = xdat[start_fit:stop_fit]

    rough_peak_positions = ()
    for i in [peaks[x] for x in [idx[0] for idx in largest_peaks]]:
        rough_peak_positions += (xdat[i],)

    for i, cen in enumerate(rough_peak_positions):
        peak, pars = add_peak("lz%d_" % (i + 1), cen)
        model = model + peak
        params.update(pars)

    init = model.eval(params, x=xdat_fit)
    result = model.fit(ydat_fit, params, x=xdat_fit)
    xc = result.params["lz1_center"].value
    sigma = result.params["lz1_sigma"].value

    parameters = result.params

    FWHM = 2 * sigma

    Q = round(xc / FWHM, 2)
    FWHM = round(FWHM * 1e6, 2)
    xc = round(xc, 6)

    return xdat, ydat, model, parameters, xc, FWHM, Q


def main():

    # Data must be in a .txt file with 2 columns:
    # column 1 = x abscisse in px
    # column 2 = intensity

    demo_mode = st.checkbox('Use demo mode', help="if you don't have your own datasets to test the software")

    spectro = st.radio("Select spectrometer", ('RS40k', 'Spectra Physics'), index=1)

    if spectro == 'Spectra Physics':

        file = st.file_uploader('Load data', type={"txt"})

        if demo_mode:
            file = "demo"
            data = np.loadtxt(os.getcwd()+"/demo_data/demo_reflectivity.txt")[:, 1]

        if file is not None:

            if file != "demo":
                data = np.loadtxt(file)[:, 1]
                # We only use the y axis stored in the second column of the .txt file here.


            # !!!! Calibration !!!!

            with st.sidebar.expander("Calibration"):

                # Nb of pixel on the camera (horizontal axis)
                Nb_px = st.number_input('Nb of pixel on the camera (horizontal axis)', value = 1340)

                # Center WL of the spectro meter (corresponds to the WL of px 670)
                Spectro = st.number_input('WL of central pixel [nm]', value = 924.4782)

                # Conversion between px and nm (... px = 1 nm)
                Calib = st.number_input('Calibration [px/nm]', value = 45.34942)


            # X acis must be in energy
            X = np.array([px_to_eV(Spectro, i, Calib) for i in range(1, Nb_px+1)])
            Y = np.array(data)



            stop = st.sidebar.number_input('Start [eV]',
                                           value=X[np.where(abs(X - 1.33) < 300e-6)[0][0]],
                                           step=1e-4,
                                           format="%.4f"
                                           )

            start = st.sidebar.number_input('Stop [eV]',
                                            value=X[np.where(abs(X - 1.35) < 300e-6)[0][0]],
                                            step=1e-4,
                                            format="%.4f"
                                            )

            i_start = np.where(abs(X - start) < 300e-6)[0][0]
            i_stop = np.where(abs(X - stop) < 300e-6)[0][0]

            # Find the number_of_elements largest peaks in peaks.
            # This is usefull is you see many modes that are too close to each other. If you only see one use 1
            number_of_elements = st.sidebar.number_input('Number of modes', value=1)

            # This might need to be adapted depending on the width of the cabvity
            # Try more or less, but around 100 is good for Q = 10 000
            zoom_fit = st.sidebar.number_input('Zoom fit', value=75)

            xdat, ydat, model, params, xc, FWHM, Q = fit_cav(X, Y, i_start, i_stop, number_of_elements, zoom_fit)

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
                x=xdat,
                y=model.eval(params, x=xdat),
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


    else:
        # This is for Redback spectrometer

        # Data must be in a .csv file.

        file = st.file_uploader('Load data', type={"csv"})

        if file is not None:
            header = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 12, 14]
            df = pd.read_csv(file,
                             delimiter=',',
                             skiprows=header)
            # We only use the y axis stored in the second column of the .txt file here.

            X = df['# wavelength'].to_numpy()
            Y = df[' signal'].to_numpy()

            unit = st.sidebar.selectbox("Choose unit for plot range",
                                        ("nm",
                                         "eV")
                                        )

            if unit == 'nm':
                start = st.sidebar.number_input('Start', value=X[np.where(abs(X - 924) < 0.01)[0][0]])
                stop = st.sidebar.number_input('Stop', value=X[np.where(abs(X - 926) < 0.01)[0][0]])

                # In WL
                i_start = np.where(abs(X - start) < 0.01)[0][0]
                i_stop = np.where(abs(X - stop) < 0.01)[0][0]

            if unit == 'eV':
                start = st.sidebar.number_input('Start',
                                                value=1239.8 / X[np.where(abs(X - 926) < 0.01)[0][0]],
                                                step =1e-4,
                                                format="%.4f"
                                                )

                stop = st.sidebar.number_input('Stop',
                                               value=1239.8 / X[np.where(abs(X - 924) < 0.01)[0][0]],
                                               step=1e-4,
                                               format="%.4f"
                                               )

                # In energy we switch start and stop
                i_start = np.where(abs(X - 1239.8 / stop) < 0.01)[0][0]
                i_stop = np.where(abs(X - 1239.8 / start) < 0.01)[0][0]

            # Find the number_of_elements largest peaks in peaks.
            # This is usefull is you see many modes that are too close to each other. If you only see one use 1
            number_of_elements = st.sidebar.number_input('Number of modes', value=1)

            # This might need to be adapted depending on the width of the cabvity
            # Try more or less, but around 100 is good for Q = 10 000
            zoom_fit = st.sidebar.number_input('Zoom fit', value=75)

            xdat, ydat, model, params, xc, FWHM, Q = fit_cav(nm_to_eV(X), Y, i_start, i_stop, number_of_elements, zoom_fit)

            title_fig = "xc = " + str(round(xc, 5)) + "eV | κ = " + str(FWHM) + " µeV" + " | Q = " + str(Q)
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
                x=xdat,
                y=model.eval(params, x=xdat),
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







