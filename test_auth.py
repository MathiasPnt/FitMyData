import streamlit as st
from PIL import Image
import streamlit_authenticator as stauth

names = ['Admin','HOM', 'Quandela']
usernames = ['adm','HOM', 'Quqndela']
passwords = ['123','insitu', 'Qdl']

hashed_passwords = stauth.hasher(passwords).generate()
authenticator = stauth.authenticate(names, usernames, hashed_passwords,
                                    'some_cookie_name', 'some_signature_key', cookie_expiry_days=1)

name, authentication_status = authenticator.login('Login', 'main')

if authentication_status:
    st.write('Welcome *%s*' % (name))
    choose_functionality = st.selectbox('What are we fiting today?',
                                        ('Select an option',
                                         'Lifetime',
                                         'HOM sidepeaks',
                                         'HOM ortho/para',
                                         'g2',
                                         'Reflectivity',
                                         "Photoluminescence",
                                         "Pulse calculator"))

    if choose_functionality == 'Select an option':
        image = Image.open('HOM_group.png')
        st.image(image, caption='Mathias Pont | mathias.pont@c2n.upsaclay.fr', width=702)
    if choose_functionality == 'Lifetime':
        exec(open('fit_lifetime.py').read())
    if choose_functionality == 'HOM sidepeaks':
        exec(open('fit_HOM.py').read())
    if choose_functionality == 'HOM ortho/para':
        exec(open('fit_2HOM.py').read())
    if choose_functionality == 'g2':
        exec(open('fit_g2.py').read())
    if choose_functionality == 'Reflectivity':
        exec(open('fit_reflectivity.py').read())
    if choose_functionality == 'Photoluminescence':
        exec(open('fit_PL.py').read())
    if choose_functionality == 'Pulse calculator':
        exec(open('pulse_calculator.py').read())


elif authentication_status == False:
    st.error('Username/password is incorrect')

elif authentication_status == None:
    st.warning('Please enter your username and password')
