#version5
import re
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from io import StringIO
#-------------------- USER DEFINED FUNCTIONS---------------------------------------------

# Function to extract line luminosities and other relevant results

def extract_cloudy_data(file_content):
    wavelengths = []
    luminosities = []
    labels = []
    warnings = []

    # Normalize all whitespace: tabs, multiple spaces, newlines -> single space
    normalized = re.sub(r'\s+', ' ', file_content)

    # Updated regex to handle labels like "he 2", "C 3", "[Fe X]"
    pattern = re.compile(r'([A-Za-z0-9\[\]\+\-\/\.\(\) ]+?)\s+([\d.]+)(A|m)\s+([\d.]+)\s+([\d.]+)')

    matches = pattern.findall(normalized)

    for match in matches:
        label, value, unit, lum1, lum2 = match
        try:
            wavelength = float(value)
            luminosity = float(lum1)
            if unit == "m":
                wavelength *= 1e4  # convert microns to angstroms
            labels.append(label.strip())
            wavelengths.append(wavelength)
            luminosities.append(luminosity)
        except ValueError:
            continue

    for line in file_content.splitlines():
        if any(keyword in line.lower() for keyword in ["warning", "caution"]):
            warnings.append(line.strip())

    return wavelengths, luminosities, labels, warnings


def final_iteration_content(content):
    final_iter_match = re.search(r'Cloudy ends:.*?(\d+)\s+iterations?', content)
    if final_iter_match:
        final_iteration = int(final_iter_match.group(1))
        iteration_pattern = fr'iteration\s+{final_iteration}\b'
        iter_match = list(re.finditer(iteration_pattern, content, re.IGNORECASE))
        if iter_match:
            match = re.search(r'iteration\s+6', content, re.IGNORECASE)
            if match:
                # Slice content starting after 'iteration 6'
                content_after = content[match.end():]
                return content_after
        else:
            st.write(f"'content of iteration {final_iteration}' not found in file.")
    else:
        st.write("Could not find final iteration in 'Cloudy ends' line.")



def extract_emergent_lines(content):
    pattern = r"Emergent line intensities\s+general properties\.{5,}"
    match = re.search(pattern, content, re.IGNORECASE)
    if match:
        return content[match.end():]  # Return everything after the header
    else:
        st.warning("Could not find 'Emergent line intensities' block.")
        return ""

#-------------------------------------------------------------------------
st.title("Cloudy Output File Processor")
st.write("Upload a Cloudy output file to extract and visualize line luminosities, and explore other results.")

uploaded_file = st.file_uploader("Upload Cloudy Output File", type=["txt","out"])

main_lines=["o 3","o3bn"]

if uploaded_file:
    file_content = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
    content1=final_iteration_content(file_content)
    content=extract_emergent_lines(content1)
    wavelengths, luminosities, labels,warnings= extract_cloudy_data(content)
    # Create a DataFrame for the line data
    line_data = pd.DataFrame({
        "Label": labels,
        "Wavelength(Å)": wavelengths,
        "luminosity(erg/s)": luminosities
    })
    # Display Input Parameters at the Start
    st.subheader("Input Parameters")
    st.write("### Total Emission Lines Extracted:", len(wavelengths))
    if st.checkbox("see warnings"):
        st.write("### Warnings:")
        st.write("\n".join(warnings) if warnings else "No additional results found.")

#--------------------GRAPH 1: ONLY MAIN LINES------------------------------
    st.subheader("Main Emission Lines Only")

    main_lines_lower = [ml.lower() for ml in main_lines]
    main_data = line_data[line_data["Label"].str.lower().isin(main_lines_lower)]

    if not main_data.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(
            main_data["Wavelength(Å)"],
            main_data["luminosity(erg/s)"],
            width=5.0,  # Slightly wider bars for visibility
            color="green",
            edgecolor="black",
            linewidth=0.3,
            alpha=0.8
        )

        # Annotate each line with its label
        for _, row in main_data.iterrows():
            ax.text(row["Wavelength(Å)"], row["luminosity(erg/s)"] + 0.1, row["Label"],
                    fontsize=10, color="darkgreen")

        ax.set_title("Main Emission Lines", fontsize=16)
        ax.set_xlabel("Wavelength (Å)", fontsize=14)
        ax.set_ylabel("Log(luminosity) [erg/s]", fontsize=14)
        ax.set_ylim(bottom=0)
        # User input for custom X-axis range
        st.subheader("Set X-Axis Range for Main Emission Line Plot")
        col1, col2 = st.columns(2)

        with col1:
            min_x = st.number_input("Minimum Wavelength (Å)", value=int(min(wavelengths)))

        with col2:
            max_x = st.number_input("Maximum Wavelength (Å)", value=int(max(wavelengths)))

        ax.set_xlim(min_x,max_x)
        ax.grid(axis="y", linestyle="--", alpha=0.6)
        st.pyplot(fig)
    else:
        st.write("No main emission lines found in the data.")

#--------------------GRAPH 2:FILTERED GRAPH------------------------------
    # Display the emission lines in a scrollable box
    st.subheader("Emission Line Strengths")
    
    st.dataframe(line_data, height=300, use_container_width=True)

    st.subheader("Filter Emission Lines by Wavelength and Log(luminosity)")

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

    # Input for log luminosity range
    min_luminosity = st.number_input(
        "Minimum Log(luminosity)",
        min_value=int(min(luminosities)),
        max_value=int(max(luminosities)),
        value=int(min(luminosities))
    )

    max_luminosity = st.number_input(
        "Maximum Log(luminosity)",
        min_value=int(min(luminosities)),
        max_value=int(max(luminosities)),
        value=int(max(luminosities))
    )

    # Filter the line data based on the selected ranges
    filtered_data = line_data[
        (line_data["Wavelength(Å)"] >= min_wavelength) & 
        (line_data["Wavelength(Å)"] <= max_wavelength) & 
        (line_data["luminosity(erg/s)"] >= min_luminosity) & 
        (line_data["luminosity(erg/s)"] <= max_luminosity)
    ]

    # Display filtered data
    st.write(f"### Filtered Emission Lines (Wavelength: {min_wavelength} - {max_wavelength} Å, Log(luminosity): {min_luminosity} - {max_luminosity})")
    if not filtered_data.empty:
        st.dataframe(filtered_data, height=300, use_container_width = True)

        # Plotting Section: Plot the filtered data
        st.write("### Plot the Filtered Emission Lines")
        fig, ax = plt.subplots(figsize=(10, 5))
        # Plot all bars
        ax.bar(filtered_data["Wavelength(Å)"], filtered_data["luminosity(erg/s)"],width=1.0,
    color="blue",
    edgecolor="black",      # Adds a visible outline
    linewidth=0.2,          # Controls thickness of bar edges
    alpha=0.7)        # Highlight and label only "O 3" and "O3bn"
        for _, row in filtered_data.iterrows():
            label_clean = row["Label"].strip().lower()
            if label_clean in main_lines:
                ax.text(row["Wavelength(Å)"], row["luminosity(erg/s)"] + 0.1, row["Label"],
                        fontsize=10, color="red")
        
        # Set the y-axis limits to match the user input range
        ax.set_ylim(0, max_luminosity)
        
        ax.set_title("Filtered Emission Line luminosities", fontsize=16)
        ax.set_xlabel("Wavelength (Å)", fontsize=14)
        ax.set_ylabel("Log(luminosity)", fontsize=14)
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
#--------------------GRAPH 3: ALL LINES------------------------------
    st.subheader("Full Emission Line luminosities")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(
    wavelengths,
    luminosities,
    width=1.0,
    color="blue",
    edgecolor="black",   
    linewidth=0.2,       
    alpha=0.7)
    for wl, lum, label in zip(wavelengths, luminosities, labels):
        label_clean = label.strip().lower()
        if any(tag in label_clean for tag in main_lines):
            ax.text(wl, lum + 0.1, label, fontsize=9, color="red")


    ax.set_title("Full Emission Line luminosities", fontsize=16)
    ax.set_xlabel("Wavelength (Å)", fontsize=14)
    ax.set_ylabel("Log(luminosity) [erg/s]", fontsize=14)
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    st.pyplot(fig)
