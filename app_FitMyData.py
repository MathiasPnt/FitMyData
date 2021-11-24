#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Mathias Pont
"""

# to run the code, go to your terminal and >>> streamlit run app_FitMyData.py


import streamlit as st
from PIL import Image

Choose = st.selectbox('What are we fitting today?', ('Select an option', 'Lifetime', 'HOM', 'g2', 'Reflectivity', "Photoluminescence"))

if Choose =='Select an option':
    image = Image.open('HOM_group.png')
    st.image(image, caption='Mathias Pont | mathias.pont@c2n.upsaclay.fr', width = 702)
if Choose =='Lifetime':
    exec(open('fit_lifetime.py').read())
if Choose =='HOM':
    exec(open('fit_HOM.py').read())
if Choose =='g2':
    exec(open('fit_g2.py').read())
if Choose == 'Reflectivity':
    exec(open('fit_reflectivity.py').read())
if Choose == 'Photoluminescence':
    exec(open('fit_PL.py').read())