# -*- coding: utf-8 -*-
"""
@Authors: Mathias Pont
@Contributors:

This script gets the g2(0) of an histogram.
Input: .txt (Swabian) or .dat (HydraHarp) file downloaded from your computer using the app

Output: Displays a graph and gives g2(0) ± statistical error.

"""

import numpy as np
import streamlit as st
from HOM_Toolbox import get_g2_1input
import plotly.graph_objects as go
from plotly.graph_objs import *
from scipy.signal import find_peaks, peak_widths

@st.cache(suppress_st_warning=True)
def find_sidepeaks(data):

    # Peak finder
    # peaks is a list of the index of all peaks with a certain prominence and width
    peaks, properties = find_peaks(data, prominence=np.max(data) / 2, width=4, distance=50)

    # histogram with only the side peaks
    data_pk = data[peaks]

    to_delete = np.where(data_pk < max(data_pk) / 2)
    data_pk = np.delete(data_pk, to_delete)
    peaks = np.delete(peaks, to_delete)

    # Gets the width of the peaks. With 1 we take the full peak. 0.99 allows to get rid of the unwanted noise.
    results_full = peak_widths(data, peaks, rel_height=0.99)

    # get all peak separation
    p_sep = []
    for i in range(len(peaks) - 1):
        to_add = peaks[i + 1] - peaks[i]
        p_sep = p_sep + [to_add]

    # delete the separation that corresponds to the central peak
    # to_delete is then also the index of the first "side peak" in peaks.
    to_delete = np.where(p_sep > np.mean(p_sep) + np.std(p_sep) / 2)
    p_sep = np.delete(p_sep, to_delete)

    # Use the mean value and int
    pk_width = int(np.mean(results_full[0]))  # widths
    pk_sep = int(np.mean(p_sep))
    # WE ONLY USE THE FIST OCCURENCE OF A 2 PEAK SEPARATION TO GET THE CENTER PX
    ct_peak = int(peaks[to_delete][0] + pk_sep)

    return peaks, data_pk, ct_peak, pk_sep, pk_width

@st.cache(allow_output_mutation=True)
def get_g2(data, peak_width, peak_sep, central_peak, num_peaks):
    return get_g2_1input(data, peak_width, peak_sep, central_peak, num_peaks)


# Uploading data (in .txt or .dat format only). You can also drag and drop.
file = st.file_uploader('Load data', type={"txt", "dat"}, help = 'Upload your data here')

col1, col2, col3, col4 = st.columns(4)

if file is not None:
    ext = file.name[-3:]
    # Select which TimeTagger is used
    with col1:
        if ext == 'txt':
            timetagger = st.radio("Select correlator", ('Swabian', 'HydraHarp', 'Custom dataset'), index=0, key='sw')
        if ext == 'dat':
            timetagger = st.radio("Select correlator", ('Swabian', 'HydraHarp', 'Custom dataset'), index=1, key='hyd')

    # Get the histogram from the data file depending on which correlator was used.
    if timetagger=='Swabian':
        # The data has been saved using:
        # np.savetxt(file.txt, [index, hist])
        # we only use the hist
        data = np.loadtxt(file)[1]
    if timetagger == 'HydraHarp':
        with col2:
            # Channel used with the HydraHarp (starts at 0).
            use_channel = st.number_input('Use channel:', value=0)
        # For file extracted in ASCII from Picoquant software there are 10 lines of information that we skip.
        data = np.loadtxt(file, skiprows=10)[:, use_channel]
    if timetagger == 'Custom dataset':
        with col2:
            structure_data = st.radio("Data is stored in:", ('List','Lines', 'Columns'))
        if structure_data == 'List':
            data = np.loadtxt(file)
        if structure_data == 'Lines':
            with col3:
                use_line = st.number_input('Use line:', value=0)
            data = np.loadtxt(file)[use_line]
        if structure_data == 'Columns':
            with col3:
                use_col = st.number_input('Use column:', value=0)
            with col4:
                skip = st.number_input('Skip rows:', value=0)
            data = np.loadtxt(file, skiprows=skip)[:, use_col]

    # Create time axis to plot
    time = (np.arange(0, len(data)))

    peaks, data_pk, ct_peak, pk_sep, pk_width = find_sidepeaks(data)

    # Creating widget for the app. Here we put them in a sidebar.
    # Position of the time stamp of the central peak (zero delay) of the histogram
    # Number of side peaks used to normalise the central peak and get the g2
    num_peaks = st.sidebar.slider('Number of peaks used for integration', 0, 20, 6)
    central_peak = st.sidebar.number_input('Central peak', 0, len(data), ct_peak)
    peak_width = st.sidebar.number_input('Peak width', 0, pk_sep, pk_width)
    peak_sep = st.sidebar.number_input('Peak separation', 0, len(data), pk_sep)

    g2, errg2 = get_g2(data, peak_width, peak_sep, central_peak, num_peaks)

    # Zoom out to see more peaks in the plot
    zoom = st.sidebar.slider('Zoom out [number of peaks displayed]', 1, 20, num_peaks + 1)


    # Create an interactive plotly plot. No more comments needed here.
    title_fig = 'g2 =' + str(round(g2, 4))+ '±' + str(round(errg2, 4))
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
        x=peaks,
        y=data_pk,
        name="Peaks",
        mode='markers',
        marker=dict(color='yellow', size=10),
    ))
    # Side peaks left
    for k in range(1, num_peaks+1):
        fig2.add_trace(go.Scatter(
            x=time[int(central_peak - k * peak_sep - peak_width / 2):
                   int(central_peak - k * peak_sep + peak_width / 2)],
            y=data[int(central_peak - k * peak_sep - peak_width / 2):
                   int(central_peak - k * peak_sep + peak_width / 2)],
            showlegend=False,
            line=dict(color='gold', width=1)
        ))
    # Side right
    for k in range(1, num_peaks+1):
        fig2.add_trace(go.Scatter(
            x=time[int(central_peak + k * peak_sep - peak_width / 2):
                   int(central_peak + k * peak_sep + peak_width / 2)],
            y=data[int(central_peak + k * peak_sep - peak_width / 2):
                   int(central_peak + k * peak_sep + peak_width / 2)],
            showlegend=False,
            line=dict(color='gold', width=1)
        ))
    # Baseline right
    for k in range(1, num_peaks+1):
        fig2.add_trace(go.Scatter(
            x=time[int(central_peak + k * peak_sep + 2 * peak_width):int(central_peak + (k + 1) * peak_sep - 2 * peak_width)],
            y=data[int(central_peak + k * peak_sep + 2 * peak_width):int(central_peak + (k + 1) * peak_sep - 2 * peak_width)],
            showlegend = False,
            line=dict(color='red', width=1)
        ))
    # Baseline left
    for k in range(1, num_peaks+1):
        fig2.add_trace(go.Scatter(
            x=time[int(central_peak-(k+1)*peak_sep+2*peak_width):int(central_peak-(k)*peak_sep-2*peak_width)],
            y=data[int(central_peak-(k+1)*peak_sep+2*peak_width):int(central_peak-(k)*peak_sep - 2*peak_width)],
            showlegend = False,
            line=dict(color='red', width=1)
        ))

    fig2.add_trace(go.Scatter(
        x=time[int(central_peak - peak_width / 2):int(central_peak + peak_width / 2)],
        y=data[int(central_peak - peak_width / 2):int(central_peak + peak_width / 2)],
        name="Central peaks",
        line=dict(color='gold', width=1)
    ))
    fig2.update_layout(title=title_fig,
                    title_font_size=20,
                    width=800, height=500,
                    margin=dict(l=40, r=40, b=40, t=40),
                    xaxis_title="Time [time bin]",
                    yaxis_title="Counts",
                    legend_title="Legend",
                    xaxis_range = [-zoom*peak_sep+central_peak,zoom*peak_sep+central_peak],
                    xaxis=dict(tickformat="000"),
                    yaxis=dict(tickformat="000")
                       )
    fig2.add_vline(x=central_peak, line_width=1, line_dash="dash", line_color="seagreen")

    st.plotly_chart(fig2)
