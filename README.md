# FitMyData

To cite this work, see CITATION.cff

Efficient and versatile toolbox for analysis of time-tagged measurements (g2 and HOM), micro-cavities (reflectivity spectrum) and emission (PL). 

The objective is to have a tool to quickly analyse data in the lab. It is not meant to cover all ppossibilities, but we would like this software to be as general as possible. 

What has been implemented so far:
1) Lifetime for exciton (cosine with exp decay) and trion (exp decay)
2) HOM normalised by area of the side peaks
3) HOM normalised by uncorelated central peak (ortho/para)
4) g2
5) Reflectivity spectrum
6) photoluminescence spectrum
7) Pulse calculator

Rerquirmements:
See requirments.txt. We can install all of them using: 'pip install -r requirements.txt' in your favorite shell. You will need some compiler for it to work (if you want to use ReadPTU). If you don't have a compiler you can use the /cloud branch. 


This code comes with a build in software using streamlit. To run the code:
cd "~.FitMyData/"
streamlit run app.py
in your terminal. 

To help improve this toolbox + software:
!!!DO NOT PUSH OR COMMIT TO MAIN!!!
1) Please create a branch with your _FirstnameLastname for any modifications. 
2) All push should be adding a reasonably small feature to only one of the files. 


