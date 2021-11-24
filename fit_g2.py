# -*- coding: utf-8 -*-
"""
@author: Mathias Pont
"""
import numpy as np
import seaborn as sns
import streamlit as st
import os
from HOM_Toolbox import get_g2_1input
import webbrowser
import plotly.graph_objects as go
from plotly.graph_objs import *

color1 = sns.color_palette("tab10", 8)[0]
color2 = sns.color_palette("tab10", 8)[1]

folder1 = '/Users/mathias/Desktop'

with st.expander("Load data"):

    folder = st.text_input("Folder", folder1)
    def file_selector(folder_path=folder):
        filenames = os.listdir(folder_path)
        selected_filename = st.selectbox('Select a file', filenames)
        return os.path.join(folder_path, selected_filename)

    filename = file_selector()

    if st.button('Show me what the data looks like'):
        webbrowser.get("open -a /Applications/Firefox.app %s").open_new('file://' + filename)

data = np.loadtxt(filename)[1]

central_peak = st.sidebar.number_input('Central peak', 12400, 12600, 12500)
peak_width = st.sidebar.slider('Peak width', 0, 50, 25)
peak_sep = st.sidebar.number_input('Peak sep', 180, 200, 190)
num_peaks = st.sidebar.slider('Number of peaks', 0, 20, 10)

g2, errg2 = get_g2_1input(data, peak_width, peak_sep, central_peak, num_peaks, baseline=True)

time = (np.arange(0, 25000)*0.064-central_peak*0.064)

title_fig = 'g2 =' + str(round(g2, 4))+'±'+str(round(errg2, 4))
layout = Layout(
    plot_bgcolor='whitesmoke'
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
                xaxis_range = [-3*peak_sep*0.064,3*peak_sep*0.064]
)
st.plotly_chart(fig2)
