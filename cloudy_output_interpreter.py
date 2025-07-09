import fluxtolum as flx
import cloudy_o3line as o3

purpose=st.selectbox(["process continuum ","find line strength"])
if purpose=="process continuum ":
    flx()
