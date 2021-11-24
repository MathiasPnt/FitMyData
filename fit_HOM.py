# -*- coding: utf-8 -*-
"""
@author: Mathias Pont

"""
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import os
from HOM_Toolbox import get_HOM_1input
import webbrowser

folder1 = '/Users/mathias/Desktop'

with st.expander("Load data"):

    folder = st.text_input("Folder", folder1)
    def file_selector(folder_path=folder):
        filenames = os.listdir(folder_path)
        selected_filename = st.selectbox('Select a file', filenames)
        return os.path.join(folder_path, selected_filename)
    filename = file_selector(folder)
    st.write('You selected `%s`' % filename)

    if st.button('Show me what the data looks like'):
        webbrowser.get("open -a /Applications/Firefox.app %s").open_new('file://'+ filename)

data = np.loadtxt(filename)[1]

central_peak = st.sidebar.slider('Central peak', 12400, 12600, 12500)
peak_width = st.sidebar.slider('Peak width', 0, 50, 25)
peak_sep = st.sidebar.slider('Peak sep', 180, 200, 190)
num_peaks = st.sidebar.slider('Number of peaks', 0, 20, 6)

time = (np.arange(0, 25000))
fig, ax = plt.subplots(constrained_layout = True)
ax.plot(time, data)
ax.plot(time[int(central_peak - peak_sep - peak_width / 2):int(central_peak - peak_sep + peak_width / 2)], data[int(central_peak - peak_sep - peak_width / 2):int(central_peak - peak_sep + peak_width / 2)])
ax.plot(time[int(central_peak - peak_width / 2):int(central_peak + peak_width / 2)], data[int(central_peak - peak_width / 2):int(central_peak + peak_width / 2)])
ax.set_xlabel('Time, [ns]', fontsize = 20)
ax.set_ylabel('Counts', fontsize = 20)
ax.set_xlim(central_peak-3*peak_sep, central_peak+3*peak_sep)
ax.set_title('$V_{HOM}$ =' + str(round(get_HOM_1input(data, peak_width, peak_sep, central_peak, num_peaks, baseline = True)[0] * 100, 2)) + '%')
ax.tick_params(direction='in', bottom=True, top=True, left=True, right=True, labelsize = 20)
st.pyplot(fig)