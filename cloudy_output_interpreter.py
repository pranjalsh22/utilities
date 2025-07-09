import streamlit as st

purpose=st.selectbox("select",("process continuum ","find line strength"))
if purpose=="process continuum ":
  import fluxtolum 
if purpose=="find line strength":
  import cloudy_o3line
