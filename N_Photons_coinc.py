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
from deepdiff import DeepDiff
import copy


# Deadtime of the DMX
def ff_DMX(N, t_switch, max_delay_photons):
    # ff takes into account the non-zero switching time of the DMX.
    tau_channel = max_delay_photons / (N - 1)  # t_plateau+t_twitch. Time in each channel
    ff_DMX = (N * (tau_channel - t_switch)) / (N * tau_channel)  # T_ON / T_tot

    return ff_DMX

# N-photon coincidence rate
def C_rate(N, t_switch, max_delay_photons, RepetitionRate, Brightness_device, T_DMX, T_chip, T_detec,
           Factor_postseclect):

    # Total transmission of the setup
    T_tot = Brightness_device * T_DMX * T_chip * T_detec

    return RepetitionRate * ff_DMX(N, t_switch, max_delay_photons) * 1e6 / N * T_tot ** N / Factor_postseclect

def main():

    with st.sidebar:

        # Best experimental values in the literature
        RepetitionRate = 320  # in MHz
        Brightness_device = 0.57
        T_DMX = 0.80
        T_chip = 0.70
        T_detec = 0.9
        t_switch = 60  # [ns]
        max_delay_photons = 1000  # [ns]
        Factor_postseclect = 8

        RepetitionRate = st.number_input('Repetition rate of the laser [MHz]',
                                         value=RepetitionRate,
                                         min_value=0,
                                         step=80,
                                         help="Best demonstrated in Antón, C., et al., Optica 6.12 (2019): 1471-1477.")
        Brightness_device = st.number_input('Fibered brightness of the device [%]',
                                            value=Brightness_device,
                                            min_value=0.0,
                                            max_value=1.0,
                                            step=0.05,
                                            help="Best demonstrated in Tomm, Natasha, et al., Nature Nanotechnology 16.4 (2021): 399-403.")

        T_DMX = st.number_input('Transmission of the DMX [%]',
                                value=T_DMX,
                                min_value=0.0,
                                max_value=1.0,
                                step=0.05,
                                help="See specification of DMX6 on quandela.com")
        cola, colb = st.columns([5, 1])

        # This parameter is special, we add a '?' to explain it better
        max_delay_photons = cola.number_input('Maximal delay between photons [ns]',
                                              value=max_delay_photons,
                                              help="Best demonstrated in Tomm, Natasha, et al., Nature Nanotechnology 16.4 (2021): 399-403.")
        # Plot the transmission of the DMX as a function of the maximum delay between photons
        # This takes into account the dead time of the DMX
        plot_DMX = False
        if colb.button('?'):
            plot_DMX = True

            # Def x-axis, y-axis and the meshgrid
            N = np.arange(2, 12 + 1)
            list_delay_photons = np.linspace(250, 10000, 200)
            X, Y = np.meshgrid(N, list_delay_photons)

            layout = Layout(
                plot_bgcolor='whitesmoke'
            )
            fig1 = go.Figure(go.Surface(z=ff_DMX(X, t_switch, Y) * T_DMX,
                                        x=N,
                                        y=list_delay_photons,
                                        cmin=0,
                                        cmax=1))
            fig1.update_traces(showscale=True)
            fig1.update_layout(title='Effective transmission of the demultiplexer.',
                               title_font_size=20,
                               width=900, height=600,
                               margin=dict(l=40, r=40, b=40, t=40),
                               xaxis_title="N-photon",
                               yaxis_title="Effective transmission of the DMX",
                               scene=dict(
                                   xaxis_title='N-Photon',
                                   yaxis_title='Max delay between photons',
                                   zaxis_title='Transmission',
                                   xaxis=dict(nticks=4, range=[1, 12], ),
                                   yaxis=dict(nticks=4, range=[250, 10000], ),
                                   zaxis=dict(nticks=3, range=[0, 1], )
                               ),
                               font=dict(
                                   family="Courier New, monospace",
                                   size=18,
                                   color="White"
                               )
                               )

            fig1.update_yaxes(showgrid=True, gridwidth=1, gridcolor='dimgrey')
            fig1.update_xaxes(showgrid=True, gridwidth=1, gridcolor='dimgrey')

        T_chip = st.number_input('Transmission of the Chip',
                                 value=T_chip,
                                 min_value=0.0,
                                 max_value=1.0,
                                 step=0.05,
                                 help="Best demonstrated in Della Valle, G., et. al., Journal of Optics A: Pure and Applied Optics 11.1 (2008): 013001.")
        T_detec = st.number_input('Detectors Efficiency',
                                  value=T_detec,
                                  min_value=0.0,
                                  max_value=1.0,
                                  step=0.05,
                                  help="See specification Single Quantum")
        Factor_postseclect = st.number_input('Post selection factor [1/N]',
                                             value=Factor_postseclect,
                                             min_value=0,
                                             step=1,
                                             help='Depends on the scheme implemented')

    N = np.arange(2, 12 + 1)

    if plot_DMX:
        st.write('Press R to quit this mode.')
        st.plotly_chart(fig1)

    current_values = {'RepetitionRate': RepetitionRate,
                      'Brightness_device': Brightness_device,
                      'T_DMX': T_DMX,
                      't_chip': T_chip,
                      'T_detec': T_detec,
                      'Factor_postseclect': Factor_postseclect
                      }

    if 'saved_data' not in st.session_state:
        st.session_state.saved_data = []

    with st.expander("Hold on to this set of parameters"):
        col1, col2, col3 = st.columns(3)
        if col1.button('Hold on'):
            st.session_state.saved_data.append({'countrate': C_rate(N, t_switch, max_delay_photons, RepetitionRate,
                                                                    Brightness_device, T_DMX, T_chip, T_detec,
                                                                    Factor_postseclect),
                                                'RepetitionRate': RepetitionRate,
                                                'Brightness_device': Brightness_device,
                                                'T_DMX': T_DMX,
                                                't_chip': T_chip,
                                                'T_detec': T_detec,
                                                'Factor_postseclect': Factor_postseclect
                                                })
        if col2.button('Remove last'):
            st.session_state.saved_data.pop()
        if col3.button('Clear all'):
            st.session_state.saved_data = []

    layout = Layout(
        plot_bgcolor='whitesmoke'
    )
    fig = go.Figure(layout=layout)
    fig.add_trace(go.Scatter(
        x=N,
        y=C_rate(N, t_switch, max_delay_photons, RepetitionRate, Brightness_device, T_DMX, T_chip, T_detec,
                 Factor_postseclect),
        line=dict(color='seagreen', width=3),
        marker=dict(size=10, color='seagreen', symbol='square'),
        name="Current values"
    ))
    for idx, dat in enumerate(st.session_state.saved_data):
        fig.add_trace(go.Scatter(
            x=N,
            y=dat['countrate'],
            line=dict(width=3),
            marker=dict(size=10, symbol='circle'),
            name=f"Saved values {idx}"
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

    with st.expander("Detailed report on previous plot"):
        for id, dat in enumerate(st.session_state.saved_data):
            temporary_dat = copy.deepcopy(dat)
            del temporary_dat['countrate']
            st.write(f"Saved values {id}")
            st.write(DeepDiff(current_values, temporary_dat))


if __name__ == '__main__':
    main()
