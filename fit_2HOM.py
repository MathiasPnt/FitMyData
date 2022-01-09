# -*- coding: utf-8 -*-
"""
@Authors: Mathias Pont
@Contributors:

This script gets the HOM of two histograms in ortho and para.
Input: .txt (Swabian) or .dat (HydraHarp) file downloaded from your computer using the app for orthogonal
        and parallel polarisation

Output: Displays a graph and gives Visibility ± statistical error.

"""

import numpy as np
import streamlit as st
from antibunching_toolbox import get_HOM_2input, find_sidepeaks
import matplotlib.pyplot as plt


def main():

    col1, col2 = st.columns(2)
    # Uploading data (in .txt or .dat format only). You can also drag and drop.
    file_ortho = col1.file_uploader('Load data ortho', type={"txt", "dat"}, help = 'Upload your data here', key='ortho')
    file_para = col2.file_uploader('Load data para', type={"txt", "dat"}, help = 'Upload your data here', key='para')

    col1, col2, col3, col4 = st.columns(4)

    if file_ortho is not None:
        ext = file_ortho.name[-3:]
        # Select which TimeTagger is used
        with col1:
            if ext == 'txt':
                timetagger = st.radio("Select correlator ortho", ('Swabian', 'HydraHarp', 'Custom dataset'), index=0, key='sw')
            if ext == 'dat':
                timetagger = st.radio("Select correlator ortho", ('Swabian', 'HydraHarp', 'Custom dataset'), index=1, key='hyd')

        # Get the histogram from the data file depending on which correlator was used.
        if timetagger=='Swabian':
            # The data has been saved using:
            # np.savetxt(file.txt, [index, hist])
            # we only use the hist
            data_ortho = np.loadtxt(file_ortho)[1]
        if timetagger == 'HydraHarp':
            with col2:
                # Channel used with the HydraHarp (starts at 0).
                use_channel = st.number_input('Use channel:', value=0, key="ch_ortho")
            # For file extracted in ASCII from Picoquant software there are 10 lines of information that we skip.
            data_ortho = np.loadtxt(file_ortho, skiprows=10)[:, use_channel]
        if timetagger == 'Custom dataset':
            with col2:
                structure_data = st.radio("Data is stored in:", ('List','Lines', 'Columns'))
            if structure_data == 'List':
                data_ortho = np.loadtxt(file_ortho)
            if structure_data == 'Lines':
                with col3:
                    use_line = st.number_input('Use line:', value=0)
                data_ortho = np.loadtxt(file_ortho)[use_line]
            if structure_data == 'Columns':
                with col3:
                    use_col = st.number_input('Use column:', value=0)
                with col4:
                    skip = st.number_input('Skip rows:', value=0)
                data_ortho = np.loadtxt(file_ortho, skiprows=skip)[:, use_col]

    col5, col6, col7, col8 = st.columns(4)
    if file_para is not None:
        ext = file_ortho.name[-3:]
        # Select which TimeTagger is used
        with col5:
            if ext == 'txt':
                timetagger = st.radio("Select correlator para",
                                      ('Swabian', 'HydraHarp', 'Custom dataset'), index=0, key='sw2')
            if ext == 'dat':
                timetagger = st.radio("Select correlator para",
                                      ('Swabian', 'HydraHarp', 'Custom dataset'), index=1, key='hyd2')

        # Get the histogram from the data file depending on which correlator was used.
        if timetagger=='Swabian':
            # The data has been saved using:
            # np.savetxt(file.txt, [index, hist])
            # we only use the hist
            data_para = np.loadtxt(file_para)[1]
        if timetagger == 'HydraHarp':
            with col6:
                # Channel used with the HydraHarp (starts at 0).
                use_channel = st.number_input('Use channel:', value=0, key="ch_para")
            # For file extracted in ASCII from Picoquant software there are 10 lines of information that we skip.
            data_para = np.loadtxt(file_para, skiprows=10)[:, use_channel]
        if timetagger == 'Custom dataset':
            with col6:
                structure_data = st.radio("Data is stored in:", ('List','Lines', 'Columns'))
            if structure_data == 'List':
                data_para = np.loadtxt(file_para)
            if structure_data == 'Lines':
                with col7:
                    use_line = st.number_input('Use line:', value=0)
                data_para = np.loadtxt(file_para)[use_line]
            if structure_data == 'Columns':
                with col7:
                    use_col = st.number_input('Use column:', value=0)
                with col8:
                    skip = st.number_input('Skip rows:', value=0)
                data_para = np.loadtxt(file_para, skiprows=skip)[:, use_col]

    if file_para and file_ortho is not None:

        # Create time axis to plot
        time = (np.arange(0, len(data_para)))

        peaks, data_pk, ct_peak, pk_sep, pk_width = find_sidepeaks(data_para)


        # Creating widget for the app. Here we put them in a sidebar.
        # Position of the time stamp of the central peak (zero delay) of the histogram
        # Number of side peaks used to normalise the central peak and get the g2

        num_peaks = st.sidebar.slider('Number of peaks used for integration', 0, 20, 6)
        central_peak = st.sidebar.number_input('Central peak', 0, len(data_para), ct_peak)
        peak_width = st.sidebar.number_input('Peak width', 0, pk_sep, pk_width)
        peak_sep = st.sidebar.number_input('Peak separation', 0, len(data_para), pk_sep)

        V, errV, HOM_ortho_norm, HOM_para_norm = get_HOM_2input(data_ortho, data_para, num_peaks, manualmode=True,
                                                                ct_peak=central_peak, peak_sp=peak_sep, peak_w=peak_width)

        title_fig = 'HOM =' + str(round(V, 4)) + '±' + str(round(errV, 4))


        # PLot it
        fig, ax = plt.subplots()
        ax.set_title(title_fig)

        ax.plot(time, HOM_ortho_norm, '-o', label = 'Ortho', markersize=3)
        ax.plot(time, HOM_para_norm, '-o', label = 'Para', markersize=3)
        # Center peak
        ax.plot(time[int(central_peak - peak_width / 2):int(central_peak + peak_width / 2)],
                HOM_para_norm[int(central_peak - peak_width / 2):int(central_peak + peak_width / 2)],
                color = 'seagreen')
        ax.plot(time[int(central_peak - peak_width / 2):int(central_peak + peak_width / 2)],
                HOM_ortho_norm[int(central_peak - peak_width / 2):int(central_peak + peak_width / 2)],
                color='seagreen')

        ax.axhline(1, linestyle='--', color='dimgray')
        ax.axhline(0.75, linestyle='--', color='dimgray')
        ax.axhline(0.5, linestyle='--', color='dimgray')

        ax.set_xlim(central_peak - 5 * peak_sep, central_peak + 5 * peak_sep)
        ax.axvline(central_peak, linestyle='--')
        ax.legend(loc='upper right')

        check_central = st.sidebar.checkbox('Check central peak')
        if check_central:
            ax.set_xlim(central_peak - 2 * peak_width, central_peak + 2 * peak_width)

        ax.set_xlabel("Timetag", fontsize=18)
        ax.set_ylabel("Visibility", fontsize=18)
        ax.tick_params(direction='in', bottom=True, top=True, left=True, right=True, labelsize=12)

        st.pyplot(fig)


if __name__ == "__main__":
    main()
