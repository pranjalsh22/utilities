import streamlit as st
from pages import page1, page2, page3

st.set_page_config(page_title="My App", layout="wide")

# Custom logos for navigation
PAGES = {
    "Home": {"func": None, "logo": "🏠"},
    "Page 1": {"func": page1.show, "logo": "📊"},
    "Page 2": {"func": page2.show, "logo": "📈"},
    "Page 3": {"func": page3.show, "logo": "📚"}
}

# Display navigation buttons on homepage
if "page" not in st.session_state:
    st.session_state.page = "Home"

cols = st.columns(len(PAGES))
for i, (name, details) in enumerate(PAGES.items()):
    if cols[i].button(f"{details['logo']} {name}"):
        st.session_state.page = name

st.markdown("---")

# Display selected page
if st.session_state.page == "Home":
    st.title("Welcome to My Streamlit App")
    st.write("Click the icons above to navigate.")
else:
    PAGES[st.session_state.page]["func"]()
