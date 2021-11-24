# -*- coding: utf-8 -*-
"""
@author: Mathias Pont
"""

import numpy as np
import streamlit as st
from HOM_Toolbox import get_g2_1input
import plotly.graph_objects as go
from plotly.graph_objs import *


def get_resolution(resolution):

    # This is the values for 128 ps. For other resolution we simply use this as a ref
    central_peak = 777  # index of central peak
    bin_width = 22  # width of each peak
    peak_sep = 96  # separation between peaks. If resolution of hydraharp is 128ps this should be 96
    num_peaks = 8  # Number of peaks either side of central peak that will be used

    return (128 / resolution) * central_peak, (128 / resolution) * bin_width, (128 / resolution) * peak_sep, (128 / resolution) * num_peaks

col1, col2, col3= st.columns(3)
with col1:
    timetagger = st.radio("Select correlator", ('Swabian', 'HydraHarp'))

file = st.file_uploader('Load data', type={"txt", "dat"})

if file is not None:

    if timetagger=='Swabian':
        data = np.loadtxt(file)[1]
        # Position of the time stamp of the central peak (zero delay) of the histogram
        central_peak = st.sidebar.number_input('Central peak', 12400, 12600, 12500)
        # Width of the peak
        peak_width = st.sidebar.slider('Peak width', 0, 50, 25)
        # Separation between the peak [time stamp]
        peak_sep = st.sidebar.number_input('Peak sep', 180, 200, 190)
        # Number of side peaks used to normalise the central peak and get the g2
        num_peaks = st.sidebar.slider('Number of peaks', 0, 20, 10)
        # Create time axis
        time = (np.arange(0, 25000))
    else:
        with col2:
            Use_channel = st.number_input('Use channel Nº', value=2)
        with col3:
            resolution = st.selectbox('Resolution [ps]?', ('128', '64', '32', '16', '4'))

        data = np.loadtxt(file, skiprows=10)[:, Use_channel]

        # Set values
        central_peak0, peak_width0, peak_sep0, num_peaks0 = get_resolution(int(resolution))

        central_peak = st.sidebar.number_input('Central peak', 0, 65536, int(central_peak0))
        peak_width = st.sidebar.slider('Peak width', 0, 100, int(peak_width0))
        peak_sep = st.sidebar.number_input('Peak sep', 0, 65536, int(peak_sep0))
        num_peaks = st.sidebar.slider('Number of peaks', 0, 20, int(num_peaks0))

        time = (np.arange(0, 65536))

    g2, errg2 = get_g2_1input(data, peak_width, peak_sep, central_peak, num_peaks, baseline=True)


    title_fig = 'g2 =' + str(round(g2, 4))+'±'+str(round(errg2, 4))
    layout = Layout(plot_bgcolor='whitesmoke'
                    )
    fig2 = go.Figure(layout=layout)
    fig2.add_trace(go.Scatter(
        x=time,
        y=data,
        name="Data",
        mode='lines+markers',
        marker = dict(color='darkcyan', size=6),
        line=dict(color='teal', width=2)
    ))
    fig2.add_trace(go.Scatter(
        x=time[int(central_peak - peak_sep - peak_width / 2):int(central_peak - peak_sep + peak_width / 2)],
        y=data[int(central_peak - peak_sep - peak_width / 2):int(central_peak - peak_sep + peak_width / 2)],
        name="Fit of side peak",
        line=dict(color='gold', width=2, dash = 'dash')
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
                    xaxis_range = [-3*peak_sep+central_peak,3*peak_sep+central_peak],
                    xaxis=dict(tickformat="000"),
                    yaxis=dict(tickformat="000")
                       )
    st.plotly_chart(fig2)
