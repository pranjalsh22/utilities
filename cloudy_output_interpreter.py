import re
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from io import StringIO, BytesIO

# Function to extract line intensities and other relevant results
def extract_cloudy_data(file_content):
    wavelengths = []
    intensities = []
    labels = []  # Store labels for identifying lines
    results = []
    all_lines = file_content.splitlines()

    # Parse the file line by line
    for line in all_lines:
        # Match emission line data (e.g., "O  3 5006.84A 40.150")
        match = re.search(r"([\w\s]+)\s+([\d.]+)A\s+([\d.]+)", line)
        if match:
            label = match.group(1).strip()  # Element/ion name
            wavelength = float(match.group(2))  # Wavelength in Å
            intensity = float(match.group(3))  # Intensity in log(erg/s)
            labels.append(label)
            wavelengths.append(wavelength)
            intensities.append(intensity)
        else:
            # Identify other relevant results (e.g., warnings, notes, luminosity)
            if any(keyword in line.lower() for keyword in ["warning", "note", "luminosity", "pressure", "density"]):
                results.append(line.strip())

    return wavelengths, intensities, labels, results, all_lines

# Streamlit app layout
st.title("Cloudy Output File Processor")
st.write("Upload a Cloudy output file to extract and visualize line intensities, and explore other results.")

# File upload widget
uploaded_file = st.file_uploader("Upload Cloudy Output File", type=["txt"])

if uploaded_file:
    # Read and process the file content
    file_content = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
    wavelengths, intensities, labels, results, all_lines = extract_cloudy_data(file_content)

    # Display Input Parameters at the Start
    st.subheader("Input Parameters")
    st.write("### Uploaded File Content:")
    st.text_area("Cloudy File Content", file_content, height=200)
    st.write("### Total Emission Lines Extracted:", len(wavelengths))
    st.write("### Relevant Results:")
    st.write("\n".join(results) if results else "No additional results found.")

    # Create a DataFrame for the line data
    line_data = pd.DataFrame({
        "Label": labels,
        "Wavelength (Å)": wavelengths,
        "Log(Intensity) [erg/s]": intensities
    })

    # Full emission line data
    st.subheader("Full Emission Line Data")
    st.dataframe(line_data, height=300)
    st.download_button(
        label="Download Emission Line Data as CSV",
        data=line_data.to_csv(index=False),
        file_name="emission_line_data.csv",
        mime="text/csv"
    )

    # Plotting Section
    st.subheader("Plot Options")

    # Option 1: Plot Specific Line Label
    st.write("### Plot a Specific Line Label")
    specific_label = st.text_input("Enter the line label to plot (e.g., 'O3bn'):")
    specific_line = line_data[line_data["Label"].str.contains(specific_label, case=False, na=False)]

    if not specific_line.empty:
        st.write(f"Plotting specific line: **{specific_label}**")
        fig_single, ax_single = plt.subplots(figsize=(10, 5))
        ax_single.bar(specific_line["Wavelength (Å)"], specific_line["Log(Intensity) [erg/s]"], width=1.0, color="red", alpha=0.7)
        for _, row in specific_line.iterrows():
            ax_single.text(row["Wavelength (Å)"], row["Log(Intensity) [erg/s]"], f"{row['Label']} ({row['Wavelength (Å)']:.2f} Å)", fontsize=10, ha="center", color="black")
        ax_single.set_title(f"Emission Line: {specific_label}", fontsize=16)
        ax_single.set_xlabel("Wavelength (Å)", fontsize=14)
        ax_single.set_ylabel("Log(Intensity) [erg/s]", fontsize=14)
        ax_single.grid(axis="y", linestyle="--", alpha=0.6)
        st.pyplot(fig_single)
    elif specific_label:
        st.warning("No line found for the given label!")

    # Option 2: Plot Lines in Wavelength Range
    st.write("### Plot Emission Lines in a Specific Wavelength Range")
    zoom_min = st.number_input("Minimum Wavelength (Å)", min_value=min(wavelengths), max_value=max(wavelengths), value=min(wavelengths))
    zoom_max = st.number_input("Maximum Wavelength (Å)", min_value=min(wavelengths), max_value=max(wavelengths), value=max(wavelengths))

    if zoom_min < zoom_max:
        # Filter the data for the specified wavelength range
        zoomed_data = line_data[(line_data["Wavelength (Å)"] >= zoom_min) & (line_data["Wavelength (Å)"] <= zoom_max)]
        
        if not zoomed_data.empty:
            st.write(f"Plotting lines between {zoom_min} Å and {zoom_max} Å")
            fig_zoom, ax_zoom = plt.subplots(figsize=(10, 5))
            ax_zoom.bar(zoomed_data["Wavelength (Å)"], zoomed_data["Log(Intensity) [erg/s]"], width=1.0, color="green", alpha=0.7)
            ax_zoom.set_title(f"Emission Lines from {zoom_min} Å to {zoom_max} Å", fontsize=16)
            ax_zoom.set_xlabel("Wavelength (Å)", fontsize=14)
            ax_zoom.set_ylabel("Log(Intensity) [erg/s]", fontsize=14)
            ax_zoom.grid(axis="y", linestyle="--", alpha=0.6)
            st.pyplot(fig_zoom)
        else:
            st.warning("No emission lines found in the specified wavelength range!")
    else:
        st.warning("Invalid wavelength range!")

    # Original Full Graph
    st.subheader("Full Emission Line Intensities")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(wavelengths, intensities, width=1.0, color="blue", alpha=0.7)
    ax.set_title("Full Emission Line Intensities", fontsize=16)
    ax.set_xlabel("Wavelength (Å)", fontsize=14)
    ax.set_ylabel("Log(Intensity) [erg/s]", fontsize=14)
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    st.pyplot(fig)
