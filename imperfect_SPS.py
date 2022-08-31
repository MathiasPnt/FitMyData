# -*- coding: utf-8 -*-
"""
@Authors: Mathias Pont
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.collections import PolyCollection
import plotly.graph_objects as go
from plotly.graph_objs import *

import perceval as pcvl
import perceval.lib.symb as symb

import streamlit as st


class QPU:

    def __init__(self):
        # Set up Perceval
        self.simulator_backend = pcvl.BackendFactory().get_backend('Naive')

        # MZI interferometer
        self.mzi_circuit = pcvl.Circuit(m=2, name="MZI")

        self.phase_shifters = [pcvl.Parameter("phi1"), pcvl.Parameter("phi2")]

        (self.mzi_circuit
         .add(0, symb.PS(self.phase_shifters[0]))
         .add((0, 1), symb.BS())
         .add(0, symb.PS(self.phase_shifters[1]))
         .add((0, 1), symb.BS())
         )

        # Initial phase set to zero
        self.phase_shifters[0].set_value(0)
        # Internal phase set to pi/2
        self.phase_shifters[1].set_value(np.pi / 2)


# mzi_BasicState computes the output state distribution of any input Fock state.
def mzi_PhotonNumberTomography(scan_range=np.arange(0, 2 * np.pi, 0.1),
                               beta=1,
                               eta=0.05,
                               g2=0,
                               M=1,
                               multiphoton_model="distinguishable"):
    qpu = QPU()

    sps = pcvl.Source(brightness=beta,
                      overall_transmission=eta,
                      multiphoton_component=g2,
                      multiphoton_model=multiphoton_model,
                      indistinguishability=M,
                      indistinguishability_model="homv"
                      )

    outcome_theta = {}

    for theta in scan_range:
        outcome = []
        output_prob = dict()

        qpu.phase_shifters[0].set_value(0)
        qpu.phase_shifters[1].set_value(theta)
        p = pcvl.Processor({0: sps, 1: sps, }, qpu.mzi_circuit)
        all_p, sv_out = p.run(qpu.simulator_backend)

        for output_state in sv_out:

            if str(output_state) not in outcome:
                outcome.append(str(output_state))

            if output_state in output_prob:
                output_prob[str(output_state)] += sv_out[output_state]
            else:
                output_prob[str(output_state)] = sv_out[output_state]

        outcome_theta[theta] = output_prob

    return scan_range, outcome, outcome_theta


def plot_PhotonNumberTomography(projection='2D',
                                scan_range=np.arange(0, 2 * np.pi, 0.1),
                                beta=1, eta=0.05,
                                g2=0, M=1,
                                multiphoton_model="distinguishable"):
    scan_range, outcome, outcome_theta = mzi_PhotonNumberTomography(scan_range,
                                                                    beta, eta,
                                                                    g2, M,
                                                                    multiphoton_model)

    # 2D plot
    if projection == '2D':
        layout = Layout(
            plot_bgcolor='whitesmoke'
        )
        fig = go.Figure(layout=layout)
        for measured_state in outcome:
            X = list(outcome_theta.keys())
            Y = [outcome_theta[angle][measured_state] for angle in outcome_theta.keys()]
            fig.add_trace(go.Scatter(
                x=X,
                y=Y,
                line=dict(width=3),
                marker=dict(size=10),
                name=str(measured_state)
            ))

        fig.update_layout(width=900, height=600,
                          margin=dict(l=40, r=40, b=40, t=40),
                          xaxis_title="Internal phase of the MZI [rad]",
                          yaxis_title='Probability',
                          font=dict(
                              family="Courier New, monospace",
                              size=18,
                              color="White"
                          )
                          )
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='dimgrey')
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='dimgrey')

        st.plotly_chart(fig)

    # 3D plot
    if projection == '3D':
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        xs = scan_range
        verts = []
        ys = np.linspace(0, 1, len(outcome))
        facecolors = sns.color_palette()
        for measured_state in outcome:
            verts.append(list(zip(xs, [outcome_theta[angle][measured_state] for angle in outcome_theta.keys()])))
        poly = PolyCollection(verts, facecolors=facecolors)
        for i, measured_state in enumerate(outcome):
            ax.scatter(scan_range,
                       ys[i],
                       [outcome_theta[angle][measured_state] for angle in outcome_theta.keys()],
                       color=facecolors[i % 10])

        ax.set_xlim3d(0, 2 * np.pi)
        plt.xticks([0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi],
                   [r'$0$', r'$\frac{\pi}{2}$', r'$\pi$', r'$\frac{3\pi}{2}$', r'$2\pi$'],
                   fontsize=18)

        ax.set_ylim3d(-0.1, 1.1)
        plt.yticks(ys, outcome, fontsize=20, ha='left')

        ax.set_zlim3d(0, 1)

        ax.tick_params(direction='in', bottom=True, top=True, left=True, right=True, labelsize=20)

        st.pyplot(fig)


def outputstate_to_2outcome(output):
    """
    :param output: an output of the chip
    :return: a measurable outcome
    """
    state = []
    for m in output:
        if m.isdigit():
            state.append(m)

    if int(state[0]) == 0 and int(state[1]) == 0:
        return '|0,0>'
    if int(state[0]) == 0 and int(state[1]) > 0:
        return '|0,1>'
    if int(state[0]) > 0 and int(state[1]) == 0:
        return '|1,0>'
    if int(state[0]) > 0 and int(state[1]) > 0:
        return '|1,1>'


def compute(qpu, beta, eta, g2, M, multiphoton_model="distinguishable"):
    # Find out all the input states that must be considered depending on the characteristics of the source
    sps = pcvl.Source(brightness=beta,
                      overall_transmission=eta,
                      multiphoton_component=g2,
                      multiphoton_model=multiphoton_model,
                      indistinguishability=M,
                      indistinguishability_model="homv"
                      )

    outcome = {'|0,0>': 0,
               '|1,0>': 0,
               '|1,1>': 0,
               '|0,1>': 0
               }

    qpu.phase_shifters[1].set_value(np.pi)
    p = pcvl.Processor({0: sps, 1: sps, }, qpu.mzi_circuit)

    all_p, sv_out = p.run(qpu.simulator_backend)
    for output_state in sv_out:
        # print(str(output_state), str(sv_out[output_state]))
        # Each output is mapped to an outcome
        result = outputstate_to_2outcome(str(output_state))
        # The probability of an outcome is added, weighted by the probability of this input
        outcome[result] += sv_out[output_state]

    p_uncorr = outcome['|1,1>']

    outcome = {'|0,0>': 0,
               '|1,0>': 0,
               '|1,1>': 0,
               '|0,1>': 0
               }

    qpu.phase_shifters[1].set_value(np.pi / 2)
    p = pcvl.Processor({0: sps, 1: sps, }, qpu.mzi_circuit)

    all_p, sv_out = p.run(qpu.simulator_backend)
    for output_state in sv_out:
        # print(str(output_state), str(sv_out[output_state]))
        # Each output is mapped to an outcome
        result = outputstate_to_2outcome(str(output_state))
        # The probability of an outcome is added, weighted by the probability of this input
        outcome[result] += sv_out[output_state]

    p_corr = outcome['|1,1>']

    return 1 - 2 * p_corr / p_uncorr


def main():
    tab = st.radio('', ("Photon-number tomography", "2-photon interference"))

    if tab == "Photon-number tomography":
        st.subheader("Photon-number tomography at the output of a MZI")

        with st.sidebar:
            projection = st.selectbox('Projection', ('2D', '3D'))
            start_stop = st.slider('Select a range of values', 0.001, 2 * np.pi, (np.pi / 2, 3 * np.pi / 2))
            beta = st.slider("Brightness", min_value=0.0, max_value=0.99, value=1.0)
            eta = st.slider("Overall transmission", min_value=0.0, max_value=1.0, value=0.5)
            g2 = st.slider("g2", min_value=0.0, max_value=0.25, value=0.03)
            M = st.slider("Indistinguishability", min_value=0.0, max_value=1.0, value=1.0)
            multiphoton_model = st.selectbox('Multiphoton model', ("distinguishable", "indistinguishable"))

        scan_range = np.arange(start_stop[0], start_stop[1], 0.1)

        plot_PhotonNumberTomography(projection,
                                    scan_range,
                                    beta, eta,
                                    g2, M,
                                    multiphoton_model)

    if tab == "2-photon interference":
        st.subheader("2-photon interference")

        with st.sidebar:
            x_axis = st.selectbox('X-axis', ('eta', 'beta', 'g2'), key='xaxis_interference')

            if x_axis == 'g2':
                start_stop = st.slider('Select a range of values', 0.0, 0.3, (0.0, 0.3), key='range_xaxis')
            else:
                start_stop = st.slider('Select a range of values', 0.0, 1.0, (0.0, 1.0), key='range_xaxis')

            beta = st.slider("Brightness", min_value=0.0, max_value=1.0, value=1.0, key='beta_interfences')
            eta = st.slider("Overall transmission", min_value=0.0, max_value=1.0, value=0.05, key='eta_interfences')
            g2 = st.slider("g2", min_value=0.0, max_value=1.0, value=0.03, key='g2_interfences')
            M = st.slider("Indistinguishability", min_value=0.0, max_value=1.0, value=1.0, key='M_interfences')
            multiphoton_model = st.selectbox('Multiphoton model', ("distinguishable", "indistinguishable"),
                                             key='model_interfences')

        qpunit = QPU()

        X = np.linspace(start_stop[0], start_stop[1], 10)

        # V_HOM vs g2
        if x_axis == 'g2':
            V = [compute(qpunit, beta, eta, g2, M, multiphoton_model=multiphoton_model) for g2 in X]
        if x_axis == 'eta':
            V = [compute(qpunit, beta, eta, g2, M, multiphoton_model=multiphoton_model) for eta in X]
        if x_axis == 'beta':
            V = [compute(qpunit, beta, eta, g2, M, multiphoton_model=multiphoton_model) for beta in X]

        # Plot V_HOM vs g2

        layout = Layout(
            plot_bgcolor='whitesmoke'
        )
        fig = go.Figure(layout=layout)

        fig.add_trace(go.Scatter(
            x=X,
            y=V,
            line=dict(width=3),
            marker=dict(size=10),
        ))

        if x_axis == 'g2':
            fig.add_trace(go.Scatter(
                x=X,
                y=(M - X),
                line=dict(width=3),
                marker=None,
                name='M-g2'
            ))
        if x_axis == 'g2':
            fig.add_trace(go.Scatter(
                x=X,
                y=M - (1 + M) * X,
                line=dict(width=3),
                marker=None,
                name='M-(1+M)*g2'
            ))

        fig.update_layout(width=900, height=600,
                          margin=dict(l=40, r=40, b=40, t=40),
                          xaxis_title=x_axis,
                          yaxis_title='V_HOM',
                          font=dict(
                              family="Courier New, monospace",
                              size=18,
                              color="White"
                          )
                          )
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='dimgrey')
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='dimgrey')

        st.plotly_chart(fig)
