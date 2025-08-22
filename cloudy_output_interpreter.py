import streamlit as st
from pages import save_continuum_file, cloudy_out_file

st.set_page_config(page_title="My Streamlit App", layout="wide")

# Define your pages with logos
PAGES = {
    "Home": {"func": None, "logo": "🏠"},
    "Save Continuum File": {"func": save_continuum_file.show, "logo": "💾"},
    "Cloudy Out File": {"func": cloudy_out_file.show, "logo": "☁️"}
}

# Session state to track which page is selected
if "page" not in st.session_state:
    st.session_state.page = "Home"

# Make buttons in a row
cols = st.columns(len(PAGES))
for i, (name, details) in enumerate(PAGES.items()):
    if cols[i].button(f"{details['logo']} {name}"):
        st.session_state.page = name

st.markdown("---")

# Display content
if st.session_state.page == "Home":
    st.title("Welcome to My Streamlit App")
    st.write("Click the icons above to navigate to different pages.")
else:
    PAGES[st.session_state.page]["func"]()
