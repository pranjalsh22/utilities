import streamlit as st

purpose=st.multiselect("select",("process continuum ","find line strength"))
if "process continuum " in purpose:
  import fluxtolum 
if purpose=="find line strength":
  import cloudy_o3line
