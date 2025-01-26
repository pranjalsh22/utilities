import re
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from io import StringIO, BytesIO

# Function to extract line intensities and other relevant results
def extract_cloudy_data(file_content):
    wavelengths = []
    intensities = []
    results = []
    all_lines = file_content.splitlines()

    # Parse the file line by line
    for line in all_lines:
        # Match emission line data (e.g., "O  3 5006.84A 40.150")
        match = re.search(r"[\w\s]+\s+([\d.]+)A\s+([\d.]+)", line)
        if match:
            wavelength = float(match.group(1))  # Wavelength in Å
            intensity = float(match.group(2))  # Intensity in log(erg/s)
            wavelengths.append(wavelength)
            intensities.append(intensity)
        else:
            # Identify other relevant results (e.g., warnings, notes, luminosity)
            if any(keyword in line.lower() for keyword in ["warning", "note", "luminosity", "pressure", "density"]):
                results.append(line.strip())

    return wavelengths, intensities, results, all_lines

# Streamlit app layout
st.title("Cloudy Output File Processor")
st.write("Upload a Cloudy output file to extract and visualize line intensities, and explore other results.")

# File upload widget
uploaded_file = st.file_uploader("Upload Cloudy Output File", type=["txt"])

if uploaded_file:
    # Read and process the file content
    file_content = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
    wavelengths, intensities, results, all_lines = extract_cloudy_data(file_content)

    # Display full file content
    st.subheader("Full File Content")
    st.text_area("Cloudy File Content", file_content, height=400)

    # Display extracted results
    if results:
        st.subheader("Relevant Results from the File")
        st.write("\n".join(results))

    # Display emission line data
    if wavelengths and intensities:
        # Create a DataFrame for the line data
        line_data = pd.DataFrame({
            "Wavelength (Å)": wavelengths,
            "Log(Intensity) [erg/s]": intensities
        })

        st.subheader("Emission Line Data")
        with st.expander("Show Emission Line Data Table"):
            st.dataframe(line_data)

        # Download option for line data
        csv_data = line_data.to_csv(index=False)
        st.download_button(
            label="Download Emission Line Data as CSV",
            data=csv_data,
            file_name="emission_line_data.csv",
            mime="text/csv"
        )

        # Plot the emission line data
        st.subheader("Emission Line Intensities")
        st.write("Below is the bar plot of the extracted emission lines (wavelength vs intensity).")

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(wavelengths, intensities, width=1.0, color="blue", alpha=0.7)
        ax.set_title("Emission Line Intensities", fontsize=16)
        ax.set_xlabel("Wavelength (Å)", fontsize=14)
        ax.set_ylabel("Log(Intensity) [erg/s]", fontsize=14)
        ax.grid(axis="y", linestyle="--", alpha=0.6)
        st.pyplot(fig)

        # Save the plot to an in-memory buffer
        plot_buffer = BytesIO()
        fig.savefig(plot_buffer, format="png")
        plot_buffer.seek(0)

        # Download option for the plot
        st.download_button(
            label="Download Emission Line Plot as PNG",
            data=plot_buffer,
            file_name="emission_line_plot.png",
            mime="image/png"
        )
    else:
        st.warning("No emission line data found in the uploaded file.")
