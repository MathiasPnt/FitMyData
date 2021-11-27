# -*- coding: utf-8 -*-
"""
@Authors: Mathias Pont
@Contributors:

This script gets the lifetime (and FSS) for a Trion or an Exciton from the Time evolution of the emission

Input: .dat (HydraHarp) file downloaded from your computer using the app. Resolution must be 4 ps.

Output: Displays a graph and gives the lifetime (in ps) and FSS (in eV).

"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy
import streamlit as st
from lmfit import Model
import plotly.graph_objects as go
from plotly.graph_objs import *
from scipy.signal import find_peaks

# Some constants used to get the FSS in eV
hbar = scipy.constants.hbar
eV = scipy.constants.e

def cosine_decay(x, c1, c2, phi, w, tau):
    return ( c1 * np.sin(w*x+phi)**2) * ( c2 * np.exp(-x/tau))

def exp_decay(x, y0, N0, t0, tau):
    return y0+N0*np.exp(-(x-t0)/tau)

@st.cache(show_spinner=True)
def fit_lifetime_X(data_fit):
    mod = Model(cosine_decay)
    # Initial parameter for the fit
    pars = mod.make_params(c1 = 1, c2 = c_, phi = 0, w = w_, tau = tau_)
    result = mod.fit(data_fit, pars, x = X_fit)
    return result

@st.cache(show_spinner=True)
def fit_lifetime_T(data_fit):
    mod = Model(exp_decay)
    # Initial parameter
    pars = mod.make_params(y0 = 1, N0 = c_, t0 = 0, tau = tau_)
    result = mod.fit(data_fit, pars, x = X_fit)
    return result

# Upload a file from your computer. Has to be a .dat (ASCII export from HydraHarp).
file = st.file_uploader('Load data', type={"dat"})

if file is not None:

    # This creates columns for widgets.
    col1, col2 = st.columns(2)

    # This is how you add womething to one column.
    with col1:
        use_column = st.number_input('Use channel:', value = 0)

    # For file extracted in ASCII from Picoquant software there are 10 lines of information that we skip.
    data = np.loadtxt(file,skiprows=10)[:, use_column]

    # Peak finder
    # peaks is a list of the index of all peaks with a certain prominence and width
    peaks, properties = find_peaks(data, prominence=np.max(data) / 2, width=4, distance=50)

    # histogram with only the peaks
    data_pk = data[peaks]

    to_delete = np.where(data_pk < max(data_pk) / 100)
    data_pk = np.delete(data_pk, to_delete)
    peaks = np.delete(peaks, to_delete)

    first_peak = peaks[0]

    ## Sidebar widgets

    # Start and stop in [ns]
    # We will fit between start and stop only. These parameters influence the fit a lot.
    # Start at the first peak, stop 0.5 ns later.
    start = st.sidebar.number_input('Start [ns]', 0.0, len(data)*0.004, first_peak*0.004)
    stop = st.sidebar.number_input('Stop [ns]', 0.0, len(data)*0.004, first_peak*0.004+1)

    # We go back to time bin for the fit.
    data_fit = data[int(start/0.004):int(stop/0.004)]

    with col2:
        # Select if you want to fit a Trion or an Exciton
        excitonic_particle = st.selectbox(
            'What is it?',
            ('Exciton', 'Trion'))

    # Zoom in from start - 1 ns to stop + 1 ns
    zoom_in= st.sidebar.checkbox('Zoom')
    # Display graph in log scale
    log_scale = st.sidebar.checkbox('Log scale')

    # Use different parameters for the fit. If unchecked you use defualt values.
    fit_details = st.sidebar.checkbox('Change fit parameters')
    if fit_details:
        c_ = st.sidebar.slider('height', 0, int(np.max(data_fit)), int(np.max(data_fit)))
        tau_ = st.sidebar.slider('lifetime [ns]', 0.0, 0.250, 0.145)
    else:
        c_ = 2380
        tau_ = 0.145
        w_ = 4

    if fit_details and excitonic_particle == 'Exciton':
        w_ = st.sidebar.slider('FSS', 0, 10, 4)


    # Fit
    # !!! Resolution is 4 ps. X axis is in ns !!!
    X_fit = 0.004*np.arange(0,len(data_fit))
    X = 0.004*np.arange(0,len(data))


    # Create an interactive plotly plot. No more comments needed here.
    layout = Layout(plot_bgcolor='whitesmoke'
                    )
    fig = go.Figure(layout=layout)

    if excitonic_particle == 'Exciton':

        fit_X = fit_lifetime_X(data_fit)

        # gets the y value of the fit
        Y_fit = fit_X.best_fit
        # Lifetime
        tau =  fit_X.params['tau'].value
        # pulsation of the oscillations
        w =  fit_X.params['w'].value

        fig.add_trace(go.Scatter(
            x=X,
            y=data,
            name="Data",
            mode='lines+markers',
            marker=dict(color='darkcyan', size=6),
            line=dict(color='darkcyan', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=peaks*0.004,
            y=data_pk,
            name="Peaks",
            mode='markers',
            marker=dict(color='yellow', size=10),
        ))
        fig.add_trace(go.Scatter(
            x=X_fit+start,
            y=Y_fit,
            name="Fit",
            line=dict(color='gold', width=2)
        ))

        title_fig = 'Lifetime = ' + str(round(tau * 1000, 2)) + ' ps, FSS = ' + str(round(1e9 * w * 2 * hbar / eV, 9)) + ' eV'

    else:
        fit_T = fit_lifetime_T(data_fit)

        # Show fit report
        show_report = st.sidebar.checkbox('Show fit parameters')
        if show_report:
            st.write(fit_T .fit_report())

        # gets the y value of the fit
        Y_fit = fit_T.best_fit
        # Lifetime
        tau = fit_T.params['tau'].value

        fig.add_trace(go.Scatter(
            x=X,
            y=data,
            name="Data",
            mode='lines+markers',
            marker=dict(color='darkcyan', size=6),
            line=dict(color='darkcyan', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=peaks*0.004,
            y=data_pk,
            name="Peaks",
            mode='markers',
            marker=dict(color='yellow', size=10),
        ))
        fig.add_trace(go.Scatter(
            x=X_fit + start,
            y=Y_fit,
            name="Fit",
            line=dict(color='gold', width=2)
        ))

        title_fig = 'Lifetime = ' + str(round(tau * 1000, 2)) + ' ps'

    if zoom_in:
        fig.update_layout(xaxis_range=[start-1, stop+1])

    if log_scale:
        fig.update_yaxes(type="log")

    fig.add_vline(x=start, line_width=2, line_dash="dash", line_color="seagreen")
    fig.add_vline(x=stop, line_width=2, line_dash="dash", line_color="firebrick")

    fig.update_layout(title=title_fig,
                    title_font_size=20,
                    width=800, height=500,
                    margin=dict(l=40, r=40, b=40, t=40),
                    xaxis_title="Time [ns]",
                    yaxis_title="Counts",
                    legend_title="Legend",
                    xaxis=dict(tickformat="000"),
                    yaxis=dict(tickformat="000")
                       )

    if log_scale:
        fig.update_yaxes(type="log")
        fig.update_layout(yaxis=dict(tickformat=".1r"))

    st.plotly_chart(fig)

    # Show fit report
    show_report = st.sidebar.checkbox('Show fit report')
    if show_report:
        st.write(fit_X.fit_report())

