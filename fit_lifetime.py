# -*- coding: utf-8 -*-
"""
@author: Mathias Pont
"""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy
import streamlit as st
from lmfit import Model
import plotly.graph_objects as go
from plotly.graph_objs import *

@st.cache(show_spinner=True)
def cos_decay(x, b, c, phi, w, tau):
    return ( b * np.sin(w*x+phi)**2) * ( c * np.exp(-x/tau))
@st.cache(show_spinner=True)
def exp_decay(x, y0, N0, t0, tau):
    return y0+N0*np.exp(-(x-t0)/tau)

@st.cache(show_spinner=True)
def fit_lifetime_X(data_fit):
    mod = Model(cos_decay)
    # Initial parameter
    pars = mod.make_params(b = 1, c = c_, phi = 0, w = 4, tau = tau_)
    result = mod.fit(data_fit, pars, x = X_fit)
    return result

@st.cache(show_spinner=True)
def fit_lifetime_T(data_fit):
    mod = Model(exp_decay)
    # Initial parameter
    pars = mod.make_params(y0 = 1, N0 = c_, t0 = 0, tau = tau_)
    result = mod.fit(data_fit, pars, x = X_fit)
    return result

color1 = sns.color_palette("tab10", 8)[0]
color2 = sns.color_palette("tab10", 8)[1]

file = st.file_uploader('Load data', type={"dat"})

if file is not None:
    
    Use_column = st.number_input('Column', value = 2)

    # For file extracted in ASCII from Picoquant software there are 10 lines of information
    # that we skip.
    data = np.loadtxt(file,skiprows=10)[:,Use_column]

    ## Sidebar widgets

    # Start and stop in [ns]
    start = st.sidebar.number_input('Start [ns]', 0.0, len(data)*0.004, 9.0)
    stop = st.sidebar.number_input('Stop [ns]', 0.0, len(data)*0.004, 12.0)

    # We go back to time bin for the fit
    data_fit = data[int(start/0.004):int(stop/0.004)]


    excitonic_particle = st.sidebar.selectbox(
        'What are we fitting today',
        ('Exciton', 'Trion'))

    zoom_in= st.sidebar.checkbox('Zoom')
    log_scale = st.sidebar.checkbox('Log scale')

    fit_details = st.sidebar.checkbox('Change fit parameters')
    if fit_details:
        c_ = st.sidebar.slider('height', 0, int(np.max(data_fit)), int(np.max(data_fit)))
        tau_ = st.sidebar.slider('lifetime [ns]', 0.0, 0.250, 0.145)
    else:
        c_ = 2380
        tau_ = 0.145

    # Fit
    # resolution is 4 ps. X axis is in ns
    X_fit = 0.004*np.arange(0,len(data_fit))
    X = 0.004*np.arange(0,len(data))


    # Plot
    layout = Layout(plot_bgcolor='whitesmoke'
                    )
    fig2 = go.Figure(layout=layout)

    if excitonic_particle == 'Exciton':
        fit_X = fit_lifetime_X(data_fit)

        tau =  fit_X.params['tau'].value
        w =  fit_X.params['w'].value

        hbar = scipy.constants.hbar
        eV = scipy.constants.e

        fig2.add_trace(go.Scatter(
            x=X,
            y=data,
            name="Data",
            line=dict(color='blue', width=2)
        ))

        fig2.add_trace(go.Scatter(
            x=X_fit+start,
            y=fit_X.best_fit,
            name="Fit",
            line=dict(color='gold', width=2)
        ))

        title_fig = 'Lifetime = ' + str(round(tau * 1000, 2)) + ' ps, FSS = ' + str(round(1e9 * w * 2 * hbar / eV, 9)) + ' eV'

    else:
        fit_T = fit_lifetime_T(data_fit)
        tau = fit_T.params['tau'].value

        fig2.add_trace(go.Scatter(
            x=X,
            y=data,
            name="Data",
            mode='lines+markers',
            marker=dict(color='darkcyan', size=6),
            line=dict(color='darkcyan', width=2)
        ))

        fig2.add_trace(go.Scatter(
            x=X_fit + start,
            y=fit_T.best_fit,
            name="Fit",
            line=dict(color='gold', width=2)
        ))

        title_fig = 'Lifetime = ' + str(round(tau * 1000, 2)) + ' ps'

    if zoom_in:
        fig2.update_layout(xaxis_range=[start-1, stop+1])

    fig2.update_layout(title=title_fig,
                    title_font_size=20,
                    width=800, height=500,
                    margin=dict(l=40, r=40, b=40, t=40),
                    xaxis_title="Time [ns]",
                    yaxis_title="Counts",
                    legend_title="Legend",
                    xaxis=dict(tickformat="000"),
                    yaxis=dict(tickformat="000")
                       )
    st.plotly_chart(fig2)
