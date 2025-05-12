#version2
import re
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from io import StringIO

# Function to extract line intensities and other relevant results
def extract_cloudy_data(file_content):
    wavelengths = []
    intensities = []
    labels = []  # Store labels for identifying lines
    emission_lines = []  # Store lines where emission line strengths are shown
    warnings = []
    all_lines = file_content.splitlines()

    # Parse the file line by line
    for i, line in enumerate(all_lines):
        # Match emission line data (e.g., "O  3 5006.84A  40.150")
        match = re.search(r"([\w\s]+)\s+([\d.]+)(A|m)\s+([\d.]+)", line)
        if match:
            label = match.group(1).strip()  # Element/ion name
            wavelength = float(match.group(2))  # Wavelength
            intensity = float(match.group(4))  # Intensity
            labels.append(label)
            wavelengths.append(wavelength)
            intensities.append(intensity)
            # Append the line with an explanation of the values
            emission_lines.append(f"Line: {label}, Wavelength: {wavelength} Å, Log(Intensity): {intensity}")
        else:
            # Identify other relevant results (e.g., warnings, notes, luminosity)
            if any(keyword in line.lower() for keyword in ["warning", "note", "luminosity", "pressure", "density"]):
                warnings.append(line.strip())

    return wavelengths, intensities, labels, emission_lines, warnings, all_lines

# Streamlit app layout
st.title("Cloudy Output File Processor")
st.write("Upload a Cloudy output file to extract and visualize line intensities, and explore other results.")

# File upload widget
uploaded_file = st.file_uploader("Upload Cloudy Output File", type=["txt"])

if uploaded_file:
    # Read and process the file content
    file_content = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
    wavelengths, intensities, labels, emission_lines, warnings, all_lines = extract_cloudy_data(file_content)

    # Display Input Parameters at the Start
    st.subheader("Input Parameters")
    st.write("### Total Emission Lines Extracted:", len(wavelengths))
    st.write("### Relevant Results:")
    st.write("\n".join(warnings) if warnings else "No additional results found.")

    # Display instructions on how to read the emission line data
    st.write("""
    ### How to Read the Emission Line Data:
    Each emission line data includes three key pieces of information:
    1. **Label**: The ion or element (e.g., 'O 3' for [O III]).
    2. **Wavelength**: The wavelength of the emission line in Angstroms (Å).
    3. **Log(Intensity)**: The logarithmic intensity of the emission line.

    #### Example:
    - **Line**: O 3
    - **Wavelength**: 5006.84 Å
    - **Log(Intensity)**: 40.150

    This means the emission line is from the [O III] ion, the wavelength is 5006.84 Å, and the intensity is log-transformed, with a value of 40.150.
    """)

    # Display the emission lines in a scrollable box
    st.subheader("Emission Line Strengths")
    if emission_lines:
        st.text_area("Emission Line Data", "\n".join(emission_lines), height=300, max_chars=1000)
    else:
        st.write("No emission lines found in the file.")

    # Create a DataFrame for the line data
    line_data = pd.DataFrame({
        "Label": labels,
        "Wavelength": wavelengths,
        "Intensity": intensities
    })

    # Allow user to filter by wavelength and intensity
    st.subheader("Filter Emission Lines by Wavelength and Log(Intensity)")

    # Input for wavelength range
    min_wavelength = st.number_input(
        "Minimum Wavelength (Å)",
        min_value=int(min(wavelengths)),
        max_value=int(max(wavelengths)),
        value=int(min(wavelengths))
    )

    max_wavelength = st.number_input(
        "Maximum Wavelength (Å)",
        min_value=int(min(wavelengths)),
        max_value=int(max(wavelengths)),
        value=int(max(wavelengths))
    )

    # Input for log intensity range
    min_intensity = st.number_input(
        "Minimum Log(Intensity)",
        min_value=int(min(intensities)),
        max_value=int(max(intensities)),
        value=int(min(intensities))
    )

    max_intensity = st.number_input(
        "Maximum Log(Intensity)",
        min_value=int(min(intensities)),
        max_value=int(max(intensities)),
        value=int(max(intensities))
    )

    # Filter the line data based on the selected ranges
    filtered_data = line_data[
        (line_data["Wavelength"] >= min_wavelength) & 
        (line_data["Wavelength"] <= max_wavelength) & 
        (line_data["Intensity"] >= min_intensity) & 
        (line_data["Intensity"] <= max_intensity)
    ]

    # Display filtered data
    st.write(f"### Filtered Emission Lines (Wavelength: {min_wavelength} - {max_wavelength} Å, Log(Intensity): {min_intensity} - {max_intensity})")
    if not filtered_data.empty:
        st.dataframe(filtered_data, height=300)

        # Plotting Section: Plot the filtered data
        st.write("### Plot the Filtered Emission Lines")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(filtered_data["Wavelength"], filtered_data["Intensity"], width=1.0, color="blue", alpha=0.7)
        
        # Set the y-axis limits to match the user input range
        ax.set_ylim(min_intensity, max_intensity)
        
        ax.set_title("Filtered Emission Line Intensities", fontsize=16)
        ax.set_xlabel("Wavelength (Å)", fontsize=14)
        ax.set_ylabel("Log(Intensity)", fontsize=14)
        ax.grid(axis="y", linestyle="--", alpha=0.6)
        st.pyplot(fig)

        # Option to download filtered data
        st.download_button(
            label="Download Filtered Emission Line Data as CSV",
            data=filtered_data.to_csv(index=False),
            file_name="filtered_emission_line_data.csv",
            mime="text/csv"
        )
    else:
        st.write("No emission lines match the selected filters!")

    # Original Full Graph
    st.subheader("Full Emission Line Intensities")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(wavelengths, intensities, width=1.0, color="blue", alpha=0.7)
    ax.set_title("Full Emission Line Intensities", fontsize=16)
    ax.set_xlabel("Wavelength (Å)", fontsize=14)
    ax.set_ylabel("Log(Intensity) [erg/s]", fontsize=14)
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    st.pyplot(fig)
