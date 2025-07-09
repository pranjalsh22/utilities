import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Physical constants
h = 6.62607015e-27  # Planck constant in erg·s
c = 2.99792458e10   # Speed of light in cm/s
rydberg_to_erg = 2.1798723611035e-11  # 1 Ryd in erg
ev_to_erg = 1.602176634e-12  # 1 eV in erg

st.title("Luminosity & Luminosity Density Calculator from Flux Data")

uploaded_file = st.file_uploader("Upload a .txt file with tab, comma, or space delimiters", type=["txt"])

if uploaded_file is not None:
    # Try reading with common delimiters
    try:
        df = pd.read_csv(uploaded_file, delim_whitespace=True)
    except:
        try:
            df = pd.read_csv(uploaded_file, sep=',')
        except:
            df = pd.read_csv(uploaded_file, sep='\t')

    st.write("### Preview of Uploaded Data")
    st.dataframe(df.head())

    # Let user pick energy and flux columns
    columns = df.columns.tolist()
    energy_col = st.selectbox("Select the column for energy", columns)
    flux_col = st.selectbox("Select the column for flux", columns)

    # Unit selection
    energy_unit = st.selectbox("Select energy unit", ["Rydberg", "eV", "Hz"])
    flux_unit = st.selectbox("Select flux unit", [
        "erg/s/cm²/Hz", "erg/s/cm²/Å", "erg/s/cm²"
    ])

    log10_distance = st.number_input("Enter the distance in log10(cm)", value=27.0)
    distance_cm = 10 ** log10_distance

    if st.button("Calculate Luminosity"):
        # Extract and convert energy
        energy_raw = df[energy_col].astype(float)

        if energy_unit == "Rydberg":
            freq = energy_raw * rydberg_to_erg / h  # Convert to Hz
        elif energy_unit == "eV":
            freq = energy_raw * ev_to_erg / h  # Convert to Hz
        elif energy_unit == "Hz":
            freq = energy_raw
        else:
            st.error("Unsupported energy unit.")
            st.stop()

        # Wavelength in Å (for Lλ if needed)
        wavelength_angstrom = c / freq * 1e8

        # Extract flux
        flux = df[flux_col].astype(float)

        # Convert flux to luminosity density
        if flux_unit == "erg/s/cm²/Hz":
            lum_density = flux * 4 * np.pi * distance_cm ** 2  # Lν
            lum_type = "Lν (erg/s/Hz)"
        elif flux_unit == "erg/s/cm²/Å":
            lum_density = flux * 4 * np.pi * distance_cm ** 2  # Lλ
            lum_type = "Lλ (erg/s/Å)"
        elif flux_unit == "erg/s/cm²":
            lum_density = flux * 4 * np.pi * distance_cm ** 2  # broadband luminosity
            lum_type = "Luminosity (erg/s)"
        else:
            st.error("Unsupported flux unit.")
            st.stop()

        df["Luminosity_Density"] = lum_density

        # Show table
        st.write(f"### Data with {lum_type}")
        st.dataframe(df)

        # Plotting
        fig, ax = plt.subplots()
        if flux_unit == "erg/s/cm²/Hz":
            ax.plot(freq, lum_density, label=lum_type)
            ax.set_xlabel("Frequency (Hz)")
        elif flux_unit == "erg/s/cm²/Å":
            ax.plot(wavelength_angstrom, lum_density, label=lum_type)
            ax.set_xlabel("Wavelength (Å)")
        else:
            ax.plot(energy_raw, lum_density, label=lum_type)
            ax.set_xlabel(f"Energy ({energy_unit})")

        ax.set_ylabel("Luminosity")
        ax.set_title(f"{lum_type} vs Energy")
        ax.grid(True)
        st.pyplot(fig)

        # Integrate to find bolometric luminosity
        if flux_unit == "erg/s/cm²/Hz":
            total_luminosity = np.trapz(lum_density, freq)
        elif flux_unit == "erg/s/cm²/Å":
            total_luminosity = np.trapz(lum_density, wavelength_angstrom)
        else:
            total_luminosity = np.trapz(lum_density, energy_raw)

        st.write(f"### Total Bolometric Luminosity: {total_luminosity:.3e} erg/s")
