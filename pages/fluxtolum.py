import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

st.title("Luminosity & Luminosity Density Calculator from Flux Data")

uploaded_file = st.file_uploader("Upload a .txt file with tab, comma, or space delimiters", type=["txt"])

if uploaded_file is not None:
    # Try to auto-detect delimiter and load data
    try:
        content = uploaded_file.getvalue().decode("utf-8")
        df = pd.read_csv(io.StringIO(content), sep=None, engine='python')
    except Exception as e:
        st.error(f"Could not read file: {e}")
        st.stop()

    st.write("### Preview of Uploaded Data")
    st.dataframe(df.head())

    # Let user pick energy and flux columns
    columns = df.columns.tolist()
    energy_col = st.selectbox("Select the column for energy", columns)
    flux_col = st.selectbox("Select the column for flux", columns)

    log10_distance = st.number_input("Enter the distance in log10(cm)", value=27.0)
    distance_cm = 10 ** log10_distance

    if st.button("Calculate Luminosity"):
        # Convert columns to float safely
    # Try converting energy column
        energy_numeric = pd.to_numeric(df[energy_col], errors='coerce')
        invalid_energy = df[energy_numeric.isna()]
        if not invalid_energy.empty:
            st.error(f"Non-numeric values found in '{energy_col}' at rows: {invalid_energy.index.tolist()}")
            st.write("Problematic rows (energy):")
            st.dataframe(invalid_energy)
            st.stop()
        
        # Try converting flux column
        flux_numeric = pd.to_numeric(df[flux_col], errors='coerce')
        invalid_flux = df[flux_numeric.isna()]
        if not invalid_flux.empty:
            st.error(f"Non-numeric values found in '{flux_col}' at rows: {invalid_flux.index.tolist()}")
            st.write("Problematic rows (flux):")
            st.dataframe(invalid_flux)
            st.stop()
        
        # If all good, assign numeric columns
        df[energy_col] = energy_numeric
        df[flux_col] = flux_numeric

        # Extract and convert energy
        energy_raw = df[energy_col]
        rydberg_to_erg = 2.1798723611035e-11
        h = 6.62607015e-27
        freq = energy_raw * rydberg_to_erg / h  # Convert to Hz
        
        # Extract flux
        flux = df[flux_col]


        lum_density = flux * 4 * np.pi * distance_cm ** 2  # broadband luminosity
        lum_type = "Luminosity (erg/s)"

        df["Luminosity_Density"] = lum_density

        # Show table
        st.write(f"### Data with {lum_type}")
        st.dataframe(df)

        # Plotting
        fig, ax = plt.subplots()

        ax.plot(energy_raw, lum_density, label=lum_type)
        ax.set_xlabel(f"Energy ({energy_unit})")

        ax.set_ylabel("Luminosity")
        ax.set_title(f"{lum_type} vs Energy")
        ax.grid(True)
        ax.set_xscale('log')
        ax.set_yscale('log')
        st.pyplot(fig)

        total_luminosity = np.trapz(lum_density, energy_raw)

        st.write(f"### Total Bolometric Luminosity: {total_luminosity:.3e} erg/s")
