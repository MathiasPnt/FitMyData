# -*- coding: utf-8 -*-
"""
@Authors: Mathias Pont
@Contributors:

This script is bringing together different functionalities deployed as streamlit app into a single
app with a selectbox. This is meant to allow for a highly collaborative, efficient and versatile
toolbox to study experimentally single photon sources.

To run the code, go to your terminal, reach the folder "FitMyData" of this project using for example
cd /Users/mathias/PycharmProjects/FitMyData
and run the code
streamlit run app.py
The app will be opened in your default browser.

To add a functionality:
1) Create a separate .py file that should be an independent streamlit app.
2) Add its name to the "Choose" selectbox
3) Add it to the "if" using exec(open('your_file.py').read())
"""

import streamlit as st
from PIL import Image
import os
import fit_lifetime
import pulse_calculator
import fit_HOM
import fit_2HOM
import fit_g2
import fit_reflectivity
import fit_PL
import N_Photons_coinc

choose_functionality = st.selectbox('What are we fitting today?',
                                    ('Select an option',
                                     'Lifetime',
                                     'HOM sidepeaks',
                                     'HOM ortho/para',
                                     'g2',
                                     'Reflectivity',
                                     'Photoluminescence',
                                     'Pulse calculator',
                                     'N-photon coincidence'))

if choose_functionality =='Select an option':
    image = Image.open('HOM_group.png')
    st.image(image, caption='Mathias Pont | mathias.pont@c2n.upsaclay.fr', width = 702)


    # Use local CSS to make things pretty. This is not usefull, only for aesthetic purposes.
    def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


    local_css("style/style.css")

    # Load Animation. Here you can change the symbol to match the season.
    animation_symbol1 = "❄️"
    animation_symbol2 = "❄️"

    st.markdown(
        f"""
        <div class="snowflake">{animation_symbol1}</div>
        <div class="snowflake">{animation_symbol2}</div>
        <div class="snowflake">{animation_symbol1}</div>
        <div class="snowflake">{animation_symbol2}</div>
        <div class="snowflake">{animation_symbol1}</div>
        <div class="snowflake">{animation_symbol2}</div>
        <div class="snowflake">{animation_symbol1}</div>
        <div class="snowflake">{animation_symbol2}</div>
        <div class="snowflake">{animation_symbol1}</div>
        """,
        unsafe_allow_html=True,
    )

if choose_functionality =='Lifetime':
    fit_lifetime.main()
if choose_functionality =='HOM sidepeaks':
    fit_HOM.main()
if choose_functionality == 'HOM ortho/para':
    fit_2HOM.main()
if choose_functionality =='g2':
    fit_g2.main()
if choose_functionality == 'Reflectivity':
    fit_reflectivity.main()
if choose_functionality == 'Photoluminescence':
    fit_PL.main()
if choose_functionality == 'Pulse calculator':
    pulse_calculator.main()
if choose_functionality == 'N-photon coincidence':
    N_Photons_coinc.main()

