# -*- coding: utf-8 -*-
"""
@Authors: Mathias Pont
@Contributors:

This script gets the lifetime (and FSS) for a Trion or an Exciton from the Time evolution of the emission

Input: .dat (HydraHarp) file downloaded from your computer using the app. Resolution must be 4 ps.

Output: Displays a graph and gives the lifetime (in ps) and FSS (in eV).

"""

import numpy as np
import scipy
import streamlit as st
from lmfit import Model, Parameters
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import os

# UTILS
# Some constants used to get the FSS in eV
hbar = scipy.constants.hbar
eV = scipy.constants.e

def cosine_decay(x, c1, c2, phi, w, tau):
    return ( c1 * np.sin(w*x+phi)**2) * ( c2 * np.exp(-x/tau))

def exp_decay(x, y0, N0, t0, tau):
    return y0+N0*np.exp(-(x-t0)/tau)


def fit_lifetime_X(data_fit, x_axis, c, w, tau):
    mod = Model(cosine_decay)

    # Initial parameter for the fit
    pars = Parameters()
    pars.add('c1', value=1)
    pars.add('c2', value=c)
    pars.add('phi', value=0)
    pars.add('w', value=w, min=0)
    pars.add('tau', value=tau)

    result = mod.fit(data_fit, pars, x=x_axis)
    return result


def fit_lifetime_T(data_fit, x_axis, c, tau):
    mod = Model(exp_decay)
    # Initial parameter
    pars = Parameters()
    pars.add('y0', value=1)
    pars.add('N0', value=c)
    pars.add('t0', value=0, min=0)
    pars.add('tau', value=tau)

    result = mod.fit(data_fit, pars, x=x_axis)
    return result


def main():

    demo_mode=st.checkbox('Use demo mode', help="if you don't have your own datasets to test the software")

    if demo_mode:
        file = "demo"
        data = np.loadtxt(os.getcwd()+"/demo_data/demo_lifetime.dat", skiprows=10)[:, 3]
    else:
        # Upload a file from your computer. Has to be a .dat (ASCII export from HydraHarp).
        file = st.file_uploader('Load data', type={"dat"})

    if file is not None:
        # This creates columns for widgets.
        col1, col2 = st.columns(2)
        if file !="demo":
            # This is how you add womething to one column.
            with col1:
                use_column = st.number_input('Use channel:', value = 0)

            # For file extracted in ASCII from Picoquant software there are 10 lines of information that we skip.
            data = np.loadtxt(file, skiprows=10)[:, use_column]

        # Peak finder
        # peaks is a list of the index of all peaks with a certain prominence and width
        peaks, properties = find_peaks(data, prominence=np.max(data) / 2)

        # histogram with only the peaks
        data_pk = data[peaks]

        to_delete = np.where(data_pk < max(data_pk) / 100)
        data_pk = np.delete(data_pk, to_delete)
        peaks = np.delete(peaks, to_delete)

        first_peak = peaks[0]

        ## Sidebar widgets

        # Start and stop in [ns]
        # We will fit between start and stop only. These parameters influence the fit a lot.
        # Start at the first peak + 10 ps, stop 1 ns later.
        start = st.sidebar.number_input('Start [ns]', 0.0, len(data)*0.004, first_peak*0.004+0.010)
        stop = st.sidebar.number_input('Stop [ns]', 0.0, len(data)*0.004, first_peak*0.004+1)

        # We switch back to time bin for the fit.
        data_fit = data[int(start/0.004):int(stop/0.004)]

        with col2:
            # Select if you want to fit a Trion or an Exciton
            excitonic_particle = st.selectbox(
                'What is it?',
                ('Exciton', 'Trion'))

        # Zoom in from start - 1 ns to stop + 1 ns
        zoom_in= st.sidebar.checkbox('Zoom', value=True)
        # Display graph in log scale
        log_scale = st.sidebar.checkbox('Log scale')

        # Use different parameters for the fit. If unchecked you use defualt values.
        change_fit_pars = st.sidebar.checkbox('Change fit parameters')
        if change_fit_pars:
            c_ = st.sidebar.slider('Height', 0, int(np.max(data_fit)), int(np.max(data_fit)))
            tau_ = st.sidebar.slider('Lifetime [ns]', 0.000, 0.800, 0.145)
        else:
            c_ = 2380.00
            tau_ = 0.145
            w_ = 4.00

        if change_fit_pars and excitonic_particle == 'Exciton':
            w_ = st.sidebar.slider('FSS [µeV]', 0.00, 10.00, 4.00)


        # Fit
        # !!! Resolution is 4 ps. X axis is in ns !!!
        X_fit = 0.004*np.arange(0, len(data_fit))
        X = 0.004*np.arange(0, len(data))

        fig, ax = plt.subplots()
        ax.tick_params(direction='in', bottom=True, top=True, left=True, right=True, labelsize=12)
        ax.set_xlabel("Time [ns]", fontsize=14)
        ax.set_ylabel("Counts", fontsize=14)


        # Create an interactive plotly plot. No more comments needed here.

        if excitonic_particle == 'Exciton':

            fit_X = fit_lifetime_X(data_fit, X_fit, c_, w_, tau_)

            # gets the y value of the fit
            Y_fit = fit_X.best_fit
            # Lifetime
            tau =  fit_X.params['tau'].value
            # pulsation of the oscillations
            w =  fit_X.params['w'].value

            ax.plot(X, data, '-o', markersize = 3, label="Data")

            ax.plot(peaks*0.004, data_pk, 'o', label="Peaks")

            ax.plot(X_fit+start, Y_fit, label="Fit")

            title_fig = 'Lifetime = ' + str(round(tau * 1000, 2)) + ' ps, FSS = ' + str(round(1e9 * w * 2 * hbar / eV, 9)) + ' eV'
            ax.set_title(title_fig)
        else:
            fit_T = fit_lifetime_T(data_fit, X_fit, c_, tau_)

            # gets the y value of the fit
            Y_fit = fit_T.best_fit
            # Lifetime
            tau = fit_T.params['tau'].value

            ax.plot(X, data, '-o', markersize = 3, label="Data")

            ax.plot(peaks * 0.004, data_pk, 'o', label="Peaks")

            ax.plot(X_fit + start, Y_fit, label="Fit")

            title_fig = 'Lifetime = ' + str(round(tau * 1000, 2)) + ' ps'
            ax.set_title(title_fig)


        if zoom_in:
           ax.set_xlim(start-1, stop+1)

        if log_scale:
            ax.set_yscale('log')

        ax.axvline(start, linestyle="--", color="seagreen")
        ax.axvline(stop, linestyle="--", color="firebrick")


        st.pyplot(fig)

        # Show fit report
        show_report = st.sidebar.checkbox('Show fit report')
        if show_report and excitonic_particle == 'Trion':
            st.write(fit_T.fit_report())
        if show_report and excitonic_particle == 'Exciton':
            st.write(fit_X .fit_report())

        if file != "demo":
            # To download the plot
            directory = os.getcwd()
            local_path = directory + os.sep + "temp_picture.pdf"
            fig.savefig(local_path, bbox_inches='tight')
            with open("temp_picture.pdf", "rb") as picture:
                btn = st.download_button(
                    label="Save plot",
                    data=picture,
                    file_name=file.name[:-4] + ".pdf",
                    mime="image/pdf"
                )
            if btn:
                os.remove(local_path)


if __name__ == "__main__":
    main()
