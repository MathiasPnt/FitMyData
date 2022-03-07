# -*- coding: utf-8 -*-
"""
@Authors: Mathias Pont and Nicolas Maring
@Contributors:

This script gives the N-Photon coincidence rate as a function of the transmission of the setup. We also give
the value with the best values we found in experimental papers in the literature.

"""

import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.graph_objs import *
import streamlit_authenticator as stauth

def main():

    # Value in R&D lab @Quandela
    RepetitionRate = 160  # in MHz
    Brightness_device = 0.15
    T_DMX = 0.65
    T_chip = 0.45
    T_detec = 0.7
    t_switch = 60  # [ns]
    max_delay_photons = 540  # [ns]
    Factor_postseclect = 8

    #Password so that the values are not everywhere on the internet
    names = ['Quandela', 'C2N']
    usernames = ['Quandela', 'C2N']
    passwords = ['Quand3la', 'insitulab']

    hashed_passwords = stauth.hasher(passwords).generate()
    authenticator = stauth.authenticate(names,
                                        usernames,
                                        hashed_passwords,
                                        'cookie_name',
                                        'signature_key',
                                        cookie_expiry_days=30)

    name, authentication_status = authenticator.login('Login', 'sidebar')
    if authentication_status:
        st.write('Welcome *%s*' % (name))
        with st.sidebar:
            # Choose between values in R&D lab or best values from the literature
            parameters = st.radio("Select parameters", ('R&D', 'Best in the literature'), index=0)

            if parameters == 'R&D':
                RepetitionRate = st.number_input('Repetition rate of the laser [MHz]',
                                                 value=RepetitionRate,
                                                 )
                Brightness_device = st.number_input('End-to-end brightness of the device', value=Brightness_device)
                T_DMX = st.number_input('Transmission of the DMX', value=T_DMX)
                T_chip = st.number_input('Transmission of the Chip', value=T_chip)
                T_detec = st.number_input('Detectors Efficiency', value=T_detec)
                Factor_postseclect = st.number_input('Post selection factor [1/N]', value=Factor_postseclect)
                max_delay_photons = st.number_input('Maximal delay between photons [ns]', value=max_delay_photons)

            if parameters == 'Best in the literature':
                RepetitionRate = st.number_input('Repetition rate of the laser [MHz]',
                                                 value=320,
                                                 help="Demonstrated in Antón, C., et al., Optica 6.12 (2019): 1471-1477.")
                Brightness_device = st.number_input('Fibered brightness of the device [%]',
                                                    value=0.57,
                                                    help="Demonstrated in Tomm, Natasha, et al., Nature Nanotechnology 16.4 (2021): 399-403.")
                T_DMX = st.number_input('Transmission of the DMX [%]',
                                        value=0.7,
                                        help="See specification of DMX6 on quandela.com")
                T_chip = st.number_input('Transmission of the Chip',
                                         value=0.6,
                                         help="Demonstrated in Della Valle, G., et. al., Journal of Optics A: Pure and Applied Optics 11.1 (2008): 013001.")
                T_detec = st.number_input('Detectors Efficiency',
                                          value=0.9,
                                          help="See specification Single Quantum")
                Factor_postseclect = st.number_input('Post selection factor [1/N]',
                                                     value=8,
                                                     help='Depends on the scheme implemented')
                max_delay_photons = st.number_input('Maximal delay between photons [ns]',
                                                    value=1000,
                                                    help="Demonstrated in Tomm, Natasha, et al., Nature Nanotechnology 16.4 (2021): 399-403.")

        def C_rate(N):
            # ff takes into account the non-zero switching time of the DMX.
            tau_channel = max_delay_photons / (N - 1)  # t_plateau+t_twitch. Time in each channel
            ff_DMX = (N * (tau_channel - t_switch)) / (N * tau_channel)  # T_ON / T_tot

            return RepetitionRate * 1e6 / N * (
                    Brightness_device * T_DMX * ff_DMX * T_chip * T_detec) ** N / Factor_postseclect

        N = np.arange(2, 12 + 1)

        layout = Layout(
            plot_bgcolor='whitesmoke'
        )
        fig = go.Figure(layout=layout)
        fig.add_trace(go.Scatter(
            x=N,
            y=C_rate(N),
            line=dict(color='seagreen', width=3),
            marker=dict(size=10, color='seagreen', symbol='square')
        ))
        fig.update_layout(title='N photon coincidence rate',
                          title_font_size=28,
                          width=900, height=600,
                          margin=dict(l=40, r=40, b=40, t=40),
                          xaxis_title="N-photon",
                          yaxis_title="N-photon coincidence rate [Hz]",
                          font=dict(
                              family="Courier New, monospace",
                              size=18,
                              color="White"
                          )
                          )
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='dimgrey')
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='dimgrey')
        fig.update_yaxes(type="log")
        st.plotly_chart(fig)


    elif authentication_status == False:
        st.error('Username / password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')


if __name__ == '__main__':
    main()
