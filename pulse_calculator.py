# -*- coding: utf-8 -*-
"""
@Authors: Mathias Pont
@Contributors: Antoine H.

This script the pulse duration from the FWHM

Input: Spectral width FWHM and center frequency xc

Output: Pulse duration in ps.

"""

import numpy as np
import streamlit as st
import scipy.constants

# speed of light in vacuum
c0 = scipy.constants.c


def convert_to_m(value, unit, calib):
    if unit == "nm":
        return value*1e-9
    if unit == "pm":
        return value*1e-12
    if unit == "px":
        return (value / calib)*1e-9

def convert_to_s(value, unit):
    if unit == "ps":
        return value*1e-12

def main():

    # Add a white space
    st.markdown('#')

    st.error("Computes the transform-limited, i.e. minimum possible pulse duration.")

    st.markdown('#')

    def get_calib():
        spectrometer = st.sidebar.radio("Select spectrometer",
                                ('White left', 'White right', 'Blue'),
                                key='dislpay unit')
        # !!!! Calibration !!!!
        # Conversion between px and nm (... px = 1 nm)
        if spectrometer in ["White left", "White right"]:
            value = 45.34942
        elif spectrometer == "Blue":
            value = 77.7191
        else:
            raise NotImplementedError(spectrometer)

        calib = st.sidebar.number_input('Calibration spectrometer [px/nm]', value=value, key='display unit')
        return calib

    # Get pulse duration from width (transform-limited)
    col1, col2 = st.columns([2, 1])
    # User inputs FWHM of emission spectrum
    FWHM = col1.number_input('Spectral width (FWHM)', value=1.0000)
    # User chooses unit
    unit_FWHM = col2.selectbox('Unit', ("nm", "pm", "px"), key = 'unit FWHM')
    if unit_FWHM == "px":
        calib = get_calib()
    else:
        calib = 1

    col2, col3 = st.columns([2, 1])
    xc = col2.number_input('Center wavelength', value=925.0, key = 'xc FWHM to tau')
    unit_xc = col3.selectbox('Unit', ("nm", ), key = 'unit xc')

    # Convert delta-frequency from unit to m
    delta_nu = c0 * convert_to_m(FWHM, unit_FWHM, calib) / convert_to_m(xc, unit_xc, calib) ** 2
    # We define TBP_gauss = ∆nu*∆tau
    TBP_gauss = 2 * np.log(2) / np.pi
    # Computes duration for gaussian pulse
    delta_tau_output_gauss = TBP_gauss / delta_nu

    # We define TBP_lorentz = ∆nu*∆tau
    TBP_lorentz = np.log(2) * np.sqrt(np.sqrt(2)-1) / np.pi
    # Computes duration for lorentzian pulse
    delta_tau_output_lorentz = TBP_lorentz / delta_nu

    # User choose which type of pulse he wants to use
    type_pulse1 = st.radio('Type of pulse', ("Gaussian", "Lorentzian"), key = 'type-1')

    if type_pulse1 == "Gaussian":
        delta_tau = delta_tau_output_gauss
    if type_pulse1 == "Lorentzian":
        delta_tau = delta_tau_output_lorentz
    duration = round(delta_tau * 1e12, 2)
    text = f'Pulse duration: {duration} ps'
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

    delta_nu_gauss = TBP_gauss / convert_to_s(delta_tau_input, unit_delta_tau)
    delta_nu_lorentz = TBP_lorentz / convert_to_s(delta_tau_input, unit_delta_tau)

    delta_lambda_gauss = delta_nu_gauss * convert_to_m(xc, unit_xc, calib) ** 2 / c0
    delta_lambda_lorentz = delta_nu_lorentz * convert_to_m(xc, unit_xc, calib) ** 2 / c0

    type_pulse2 = st.radio('Type of pulse', ("Gaussian", "Lorentzian"), key = 'type-2')

    col9, col10 = st.columns([3, 1])
    unit_result = col10.selectbox('Unit', ("px", "nm", "pm"), key = 'unit-result')

    if type_pulse2 == "Gaussian":
        delta_lambda = delta_lambda_gauss
    if type_pulse2 == "Lorentzian":
        delta_lambda = delta_lambda_lorentz

    if unit_result=='px':
        if unit_FWHM == "px":
            pass
        else:
            calib = get_calib()
        width = round(calib * delta_lambda*1e9, 2)

    if unit_result=='nm':
        width = round(delta_lambda*1e9, 3)

    if unit_result=='pm':
        width = round(delta_lambda*1e12, 3)

    text = f'Pulse width: {width} {unit_result}'
    display = '<p style="font-family:sans-serif; color:seagreen; font-size: 32px;">'+text+'</p>'
    delta_lambda = col9.markdown(display, unsafe_allow_html=True)



if __name__ == "__main__":
    main()
