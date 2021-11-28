# -*- coding: utf-8 -*-
"""
@Authors: Mathias Pont
@Contributors:

This script the pulse duration from the FWHM

Input: Spectral width FWHM and center frequency xc

Output: Pulse duration in ps.

"""

import numpy as np
import streamlit as st
import scipy.constants

# speed of light in vacuum
c0 = scipy.constants.c


def convert_to_m(value, unit):
    if unit == "nm":
        return value*1e-9
    if unit == "pm":
        return value*1e-12
    if unit == "px":
        return (value / calib)*1e-9

def convert_to_s(value, unit):
    if unit == "ps":
        return value*1e-12

# Add a white space
st.markdown('#')


def get_calib():
    spectrometer = st.sidebar.radio("Select spectrometer",
                            ('White left', 'White right', 'Blue'),
                            key='dislpay unit')
    # !!!! Calibration !!!!
    # Conversion between px and nm (... px = 1 nm)
    if spectrometer == "White left":
        calib = st.sidebar.number_input('Calibration spectrometer [px/nm]', value=45.34942, key='display unit')
    if spectrometer == "White right":
        calib = st.sidebar.number_input('Calibration spectrometer [px/nm]', value=45.34942, key='display unit')
    if spectrometer == "Blue":
        calib = st.sidebar.number_input('Calibration spectrometer [px/nm]', value=77.7191, key='display unit')

    return calib

# Get pulse duration from width (transform-limited)
col1, col2 = st.columns([2, 1])
FWHM = col1.number_input('Spectral width (FWHM)', value=1.000)
unit_FWHM = col2.selectbox('Unit', ("nm", "pm", "px"), key = 'unit FWHM')
if unit_FWHM == "px":
    calib = get_calib()

col2, col3 = st.columns([2, 1])
xc = col2.number_input('Center wavelength', value=925.0, key = 'xc FWHM to tau')
unit_xc = col3.selectbox('Unit', ("nm", ), key = 'unit xc')

# We define TBP_gauss = ∆nu*∆tau
delta_nu = c0 * convert_to_m(FWHM, unit_FWHM) / convert_to_m(xc, unit_xc) ** 2
TBP_gauss = 2 * np.log(2) / np.pi
delta_tau_output = TBP_gauss / delta_nu

text = 'Pulse duration (Gaussian): '+str(round(delta_tau_output*1e12,2)) +" ps"
display = '<p style="font-family:sans-serif; color:seagreen; font-size: 32px;">'+text+'</p>'
delta_tau = st.markdown(display, unsafe_allow_html=True)

# Add a white space
st.markdown('#')


# Get pulse duration from width (transform-limited)
col5, col6 = st.columns([2, 1])
delta_tau_input = col5.number_input('Pulse duration (FWHM)', value=10.000)
unit_delta_tau = col6.selectbox('Unit', ("ps", ), key = 'unit FWHM bis')

col7, col8 = st.columns([2, 1])
xc = col7.number_input('Center wavelength', value=925.0, key = 'xc tau to FWHM')
unit_xc = col8.selectbox('Unit', ("nm", ), key = 'unit xc bis')

# We define TBP_gauss = ∆nu*∆tau
TBP_gauss = 2 * np.log(2) / np.pi
delta_nu = TBP_gauss / convert_to_s(delta_tau_input, unit_delta_tau)
delta_lambda = delta_nu * convert_to_m(xc, unit_xc) ** 2 / c0

col9, col10 = st.columns([3, 1])
in_px = col10.checkbox('in pixel?')
if in_px:
    if unit_FWHM == "px":
        pass
    else:
        calib = get_calib()
    text = 'Pulse width: ' + str(round(calib * delta_lambda*1e9,1)) + " px"
else:
    text = 'Pulse width: '+str(round(delta_lambda*1e9,2)) +" nm"
display = '<p style="font-family:sans-serif; color:seagreen; font-size: 32px;">'+text+'</p>'
delta_lambda = col9.markdown(display, unsafe_allow_html=True)