# -*- coding: utf-8 -*-
"""
@author: Mathias Pont
"""

import numpy as np
import streamlit as st
from HOM_Toolbox import get_HOM_1input
import plotly.graph_objects as go
from plotly.graph_objs import *

file = st.file_uploader('Load data', type={"txt"})

if file is not None:

    data = np.loadtxt(file)[1]

    # Position of the time stamp of the central peak (zero delay) of the histogram
    central_peak = st.sidebar.number_input('Central peak', 12400, 12600, 12500)
    # Width of the peak
    peak_width = st.sidebar.slider('Peak width', 0, 50, 25)
    # Separation between the peak [time stamp]
    peak_sep = st.sidebar.number_input('Peak sep', 180, 200, 190)
    # Number of side peaks used to normalise the central peak and get the g2
    num_peaks = st.sidebar.slider('Number of peaks', 0, 20, 10)

    HOM, errHOM = get_HOM_1input(data, peak_width, peak_sep, central_peak, num_peaks, baseline=True)

    # Createe time axis
    time = (np.arange(0, 25000))

    title_fig = 'HOM =' + str(round(HOM, 4)) + '±' + str(round(errHOM, 4))
    layout = Layout(
        plot_bgcolor='whitesmoke'
    )
    fig2 = go.Figure(layout=layout)
    fig2.add_trace(go.Scatter(
        x=time,
        y=data,
        name="Data",
        mode='lines+markers',
        marker=dict(color='darkcyan', size=6),
        line=dict(color='teal', width=2)
    ))
    fig2.add_trace(go.Scatter(
        x=time[int(central_peak - peak_sep - peak_width / 2):int(central_peak - peak_sep + peak_width / 2)],
        y=data[int(central_peak - peak_sep - peak_width / 2):int(central_peak - peak_sep + peak_width / 2)],
        name="Fit of side peak",
        line=dict(color='gold', width=2, dash='dash')
    ))

    fig2.add_trace(go.Scatter(
        x=time[int(central_peak - peak_width / 2):int(central_peak + peak_width / 2)],
        y=data[int(central_peak - peak_width / 2):int(central_peak + peak_width / 2)],
        name="Fit of central peak",
        line=dict(color='gold', width=2)
    ))
    fig2.update_layout(title=title_fig,
                       title_font_size=18,
                       width=800, height=500,
                       margin=dict(l=40, r=40, b=40, t=40),
                       xaxis_title="Time [ns]",
                       yaxis_title="Counts",
                       legend_title="Legend",
                       xaxis_range=[-3 * peak_sep + central_peak, 3 * peak_sep + central_peak],
                       xaxis=dict(tickformat="000"),
                       yaxis=dict(tickformat="000")
                       )
    st.plotly_chart(fig2)
