import streamlit as st
from PIL import Image

import streamlit as st

st.markdown(
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">',
    unsafe_allow_html=True,
)
query_params = st.experimental_get_query_params()
tabs = ["Home", "Lifetime", "HOM sidepeaks", 'HOM ortho/para', 'g2', 'Reflectivity', 'Photoluminescence', 'Pulse calculator']
if "tab" in query_params:
    active_tab = query_params["tab"][0]
else:
    active_tab = "Home"

if active_tab not in tabs:
    st.experimental_set_query_params(tab="Home")
    active_tab = "Home"

li_items = "".join(
    f"""
    <li class="nav-item">
        <a class="nav-link{' active' if t==active_tab else ''}" href="/?tab={t}">{t}</a>
    </li>
    """
    for t in tabs
)
tabs_html = f"""
    <ul class="nav nav-tabs">
    {li_items}
    </ul>
"""

st.markdown(tabs_html, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)



if active_tab == "Home":
    import time
    with st.spinner('Wait for it...'):
        time.sleep(5)
    st.success('Done!')
    image = Image.open('HOM_group.png')
    st.image(image, caption='Mathias Pont | mathias.pont@c2n.upsaclay.fr', width=702)
elif active_tab == "Lifetime":
    exec(open('fit_lifetime.py').read())
elif active_tab == "HOM sidepeaks":
    exec(open('fit_HOM.py').read())
elif active_tab ==  'HOM ortho/para':
    exec(open('fit_2HOM.py').read())
elif active_tab == 'g2':
    exec(open('fit_g2.py').read())
elif active_tab ==  'Reflectivity':
    exec(open('fit_reflectivity.py').read())
elif active_tab ==  'Photoluminescence':
    exec(open('fit_PL.py').read())
elif active_tab ==  'Pulse calculator':
    exec(open('pulse_calculator.py').read())
else:
    st.error("Something has gone terribly wrong.")


