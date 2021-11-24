#!/usr/bin/env python3
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
    
    Use_column = st.number_input('Column', value  = 2)

    data = np.loadtxt(file,skiprows=10)[:,Use_column]

    ## Sidebar widgets
    central = st.sidebar.slider('Cursor', 0, len(data), 0)
    zoom = st.sidebar.slider('zoom', 1, int(len(data)), 800)

    start = st.sidebar.slider('Start', 2300, 2700, 2353 )
    stop = st.sidebar.slider('Stop', 2300, 2900, 2480)

    data_fit = data[start:stop]

    log_scale = st.sidebar.checkbox('Log scale')
    excitonic_particle = st.sidebar.selectbox(
        'What are we fitting today',
        ('Exciton', 'Trion'))
    fit_details = st.sidebar.checkbox('Show fit details')

    if fit_details:
        c_ = st.sidebar.slider('c', 0, int(np.max(data_fit)), 2380)
        tau_ = st.sidebar.slider('tau', 0.0, 0.250, 0.145)
    else:
        c_ = 2380
        tau_ = 0.145

    # Fit
    # resolution is 4 ps. X axis is in ns
    X_fit = 0.004*np.arange(0,len(data_fit))
    X = 0.004*np.arange(0,len(data))


    # Plot
    fig, ax = plt.subplots()
    if excitonic_particle == 'Exciton':
        fit_X = fit_lifetime_X(data_fit)

        tau =  fit_X.params['tau'].value
        w =  fit_X.params['w'].value

        hbar = scipy.constants.hbar
        eV = scipy.constants.e

        ax.plot(X - start * 0.004, data, 'o', color=color1, markersize=3)
        ax.plot(X_fit,  fit_X.best_fit, '--', color=color2)
        ax.set_title('Lifetime = ' + str(round(tau * 1000, 2)) + ' ps, FSS = ' + str(round(1e9 * w * 2 * hbar / eV, 9)) + ' eV', )

    else:
        fit_T = fit_lifetime_T(data_fit)
        tau = fit_T.params['tau'].value

        ax.plot(X - start * 0.004, data, 'o', color=color1, markersize=3)
        ax.plot(X_fit, fit_T.best_fit, '--', color=color2)
        ax.set_title('Lifetime = ' + str(round(tau * 1000, 2)) + ' ps')

    ax.tick_params(direction='in', bottom=True, top=True, left=True, right=True, labelsize=14)
    if log_scale:
        ax.set_yscale('log')

    ax.set_xlabel('Time [ns]', fontsize = 18)
    ax.axvline(central*0.004, linestyle = '--')
    ax.axvline(start*0.004-start*0.004, color = 'green')
    ax.axvline(stop*0.004-start*0.004, color = 'red')
    ax.set_ylabel('Counts', fontsize = 18)
    ax.set_xlim(central*0.004-zoom*0.004/2, central*0.004+zoom*0.004/2)

    st.pyplot(fig)
