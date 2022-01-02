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
streamlit run app_FitMyData.py
The app will be openned in your default browser.

To add a functionality:
1) Create a separate .py file that should be an independant stramlit app.
2) Add it's name to the "Choose" selectbox
3) Add it to the "if" using exec(open('your_file.py').read())
"""

import streamlit as st
from PIL import Image

choose_functionality = st.selectbox('What are we fiting today?',
                                    ('Select an option',
                                     'Lifetime',
                                     'HOM sidepeaks',
                                     'HOM ortho/para',
                                     'g2',
                                     'Reflectivity',
                                     "Photoluminescence",
                                     "Pulse calculator"))

if choose_functionality =='Select an option':
    image = Image.open('HOM_group.png')
    st.image(image, caption='Mathias Pont | mathias.pont@c2n.upsaclay.fr', width = 702)


    # Use local CSS to make things pretty. This is not usefull, only for aesthetic purposes.
    def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


    local_css("style/style.css")

    # Load Animation. Here you can change the symbol to match the season.
    animation_symbol = "❄"

    st.markdown(
        f"""
        <div class="snowflake">{animation_symbol}</div>
        <div class="snowflake">{animation_symbol}</div>
        <div class="snowflake">{animation_symbol}</div>
        <div class="snowflake">{animation_symbol}</div>
        <div class="snowflake">{animation_symbol}</div>
        <div class="snowflake">{animation_symbol}</div>
        <div class="snowflake">{animation_symbol}</div>
        <div class="snowflake">{animation_symbol}</div>
        <div class="snowflake">{animation_symbol}</div>
        """,
        unsafe_allow_html=True,
    )

if choose_functionality =='Lifetime':
    exec(open('fit_lifetime.py').read())
if choose_functionality =='HOM sidepeaks':
    exec(open('fit_HOM.py').read())
if choose_functionality == 'HOM ortho/para':
    exec(open('fit_2HOM.py').read())
if choose_functionality =='g2':
    exec(open('fit_g2.py').read())
if choose_functionality == 'Reflectivity':
    exec(open('fit_reflectivity.py').read())
if choose_functionality == 'Photoluminescence':
    exec(open('fit_PL.py').read())
if choose_functionality == 'Pulse calculator':
    exec(open('pulse_calculator.py').read())