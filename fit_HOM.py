# -*- coding: utf-8 -*-
"""
@Authors: Mathias Pont
@Contributors:

This script gets the raw V_HOM (1-2*g2(0)) of an histogram.
Input: .txt (Swabian) or .dat (HydraHarp) file downloaded from your computer using the app

Output: Displays a graph and gives the raw V_HOM ± statistical error.

"""

import numpy as np
import streamlit as st
from HOM_Toolbox import get_HOM_1input, find_sidepeaks
import matplotlib.pyplot as plt
import os
from from_PTU import get_ptu_fromfile

demo_mode = st.checkbox('Use demo mode', help="if you don't have your own datasets to test the software")

if demo_mode:
    file = "demo"
    data = np.loadtxt(os.getcwd()+"/demo_data/demo_HOM.txt")[1]
else:
    # Uploading data (in .txt or .dat format only). You can also drag and drop.
    file = st.file_uploader('Load data', type={"txt", "dat", "ptu"}, help='Upload your data here')

col1, col2, col3, col4 = st.columns(4)

if file is not None:
    # if we use the mode 'demo' then data already exists
    if file != "demo":
        ext = file.name[-3:]
        if ext == "ptu":
            _, data = get_ptu_fromfile(file)
        else:
            # Select which TimeTagger is used
            with col1:
                if ext == 'txt':
                    timetagger = st.radio("Select correlator", ('Swabian', 'HydraHarp', 'Custom dataset'), index = 0, key = 'sw')
                if ext == 'dat':
                    timetagger = st.radio("Select correlator", ('Swabian', 'HydraHarp', 'Custom dataset'), index = 1, key = 'hyd')
            # Get the histogram from the data file depending on which correlator was used.
            if timetagger == 'Swabian':
                data = np.loadtxt(file)[1]
            if timetagger == 'HydraHarp':
                with col2:
                    # Channel used with the HydraHarp (starts at 0).
                    use_channel = st.number_input('Use channel:', value=0)
                # For file extracted in ASCII from Picoquant software there are 10 lines of information that we skip.
                data = np.loadtxt(file, skiprows=10)[:, use_channel]
            if timetagger == 'Custom dataset':
                with col2:
                    structure_data = st.radio("Data is stored in:", ('List', 'Lines', 'Columns'))
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
    base_line = st.sidebar.checkbox('Substract baseline', value = True)

    HOM, errHOM = get_HOM_1input(data, peak_width, peak_sep, central_peak, num_peaks, baseline=base_line)

    zoom = st.sidebar.slider('Zoom out [number of peaks displayed]', 1, 20, num_peaks+1)

    # PLot it
    fig, ax = plt.subplots()
    title_fig = '$V_{HOM} =$' + str(round(HOM, 4)) + '±' + str(round(errHOM, 4))
    ax.set_title(title_fig)
    ax.plot(time, data, '-o', markersize = 3)
    ax.plot(peaks, data_pk, 'o', markersize = 6, color = 'gold')
    # Side peaks left
    [ax.plot(time[int(central_peak - (k + 1) * peak_sep - peak_width / 2):
                  int(central_peak - (k + 1) * peak_sep + peak_width / 2)],
             data[int(central_peak - (k + 1) * peak_sep - peak_width / 2):
                  int(central_peak - (k + 1) * peak_sep + peak_width / 2)],
             color='gold') for k in range(1, num_peaks + 1)]
    # Side peaks right
    [ax.plot(time[int(central_peak + (k + 1) * peak_sep - peak_width / 2):
                  int(central_peak + (k + 1) * peak_sep + peak_width / 2)],
             data[int(central_peak + (k + 1) * peak_sep - peak_width / 2):
                  int(central_peak + (k + 1) * peak_sep + peak_width / 2)],
             color='gold') for k in range(1, num_peaks + 1)]
    # Center peak
    ax.plot(time[int(central_peak - peak_width / 2):int(central_peak + peak_width / 2)],
            data[int(central_peak - peak_width / 2):int(central_peak + peak_width / 2)],
            )
    # Baseline right
    [ax.plot(time[int(central_peak + k * peak_sep + 2 * peak_width):
                  int(central_peak + (k + 1) * peak_sep - 2 * peak_width)],
             data[int(central_peak + k * peak_sep + 2 * peak_width):
                  int(central_peak + (k + 1) * peak_sep - 2 * peak_width)],
            color='red') for k in range(1, num_peaks + 1)]

    # Baseline left
    [ax.plot(time[int(central_peak - (k + 1) * peak_sep + 2 * peak_width):
                  int(central_peak - k * peak_sep - 2 * peak_width)],
             data[int(central_peak - (k + 1) * peak_sep + 2 * peak_width):
                  int(central_peak - k * peak_sep - 2 * peak_width)],
             color='red') for k in range(1, num_peaks + 1)]

    ax.set_xlim(central_peak-(zoom+2)*peak_sep, central_peak+(zoom+2)*peak_sep)

    check_central = st.sidebar.checkbox('Check central peak')
    if check_central:
        ax.set_xlim(central_peak - 2 * peak_width, central_peak + 2 * peak_width)
        ax.set_ylim(0, 1.2*np.max(data[central_peak - 2 * peak_width:central_peak + 2 * peak_width]))

    ax.axvline(central_peak, linestyle='--')

    ax.set_xlabel("Timetag", fontsize=18)
    ax.set_ylabel("Counts", fontsize=18)
    ax.tick_params(direction='in', bottom=True, top=True, left=True, right=True, labelsize=12)

    st.pyplot(fig)

    col1, col2 = st.columns(2)
    g2 = col1.number_input('g2(0) [%] =', 0.00, 100.00)
    M = (HOM+g2/100)/(1-g2/100)
    text = "Ms = " + str(round(M,3)) + "±" + str(round(errHOM,3))
    display = '<p style="font-family:sans-serif; color:seagreen; font-size: 25px;">' + text + '</p>'
    if g2:
        M = col2.markdown(display, unsafe_allow_html=True)

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