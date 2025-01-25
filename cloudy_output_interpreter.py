import re
import matplotlib.pyplot as plt
import streamlit as st
from io import StringIO

def extract_emission_lines(file_content):
    wavelengths = []
    intensities = []
    all_lines = file_content.splitlines()

    # Extract emission lines and organize the data
    for line in all_lines:
        match = re.search(r"[\w\s]+\s+([\d.]+)A\s+([\d.]+)", line)
        if match:
            wavelength = float(match.group(1))  # Wavelength in Å
            intensity = float(match.group(2))  # Intensity in log(erg/s)
            wavelengths.append(wavelength)
            intensities.append(intensity)
    return wavelengths, intensities, all_lines

# Streamlit interface
st.title("Cloudy Output File Processor")
st.write("Upload a Cloudy output file to visualize emission line intensities and view the file's content.")

# File upload widget
uploaded_file = st.file_uploader("Upload Cloudy Output File", type=["txt"])

if uploaded_file:
    # Read the file content
    file_content = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
    
    # Extract emission lines and all file information
    wavelengths, intensities, all_lines = extract_emission_lines(file_content)
    
    # Display the entire file content
    st.subheader("Full File Content")
    st.text_area("Cloudy File Content", file_content, height=400)
    
    if wavelengths and intensities:
        # Plot the emission line intensities
        st.subheader("Emission Line Intensities")
        st.write("Below is the bar plot of the extracted emission lines (wavelength vs intensity).")
        
        # Use Matplotlib for plotting
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(wavelengths, intensities, width=1.0, color="blue", alpha=0.7)
        ax.set_title("Emission Line Intensities", fontsize=16)
        ax.set_xlabel("Wavelength (Å)", fontsize=14)
        ax.set_ylabel("Log(Intensity) [erg/s]", fontsize=14)
        ax.grid(axis="y", linestyle="--", alpha=0.6)
        st.pyplot(fig)
    else:
        st.warning("No emission line data found in the uploaded file.")
