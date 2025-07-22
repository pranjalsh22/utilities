import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

st.title("Luminosity & Luminosity Density Calculator from Flux Data")

#-------------------------------------------------READ FILE------------------------------------------------
uploaded_file = st.file_uploader("Upload a .txt file with tab, comma, or space delimiters", type=["txt"])

if uploaded_file is not None:
    try:
        content = uploaded_file.getvalue().decode("utf-8")
        df = pd.read_csv(io.StringIO(content), sep=None, engine='python')
    except Exception as e:
        st.error(f"Could not read file: {e}")
        st.stop()

    st.header("# Uploaded Data")
    df_display = df.copy()
    for col in df.columns.tolist():
        df_display[col] = df[col].map(lambda x: f"{x:.3e}")
        
    st.dataframe(df_display)

#------------------------------------------------SELECT COLUMNS------------------------------------------------

    columns = df.columns.tolist()
    energy_col = st.selectbox("Select the column for energy", columns)
    nuFnu = st.selectbox("Select the column for nuFnu", [c for c in columns if c != energy_col])

 #------------------------------------------------GIVE DISTANCE------------------------------------------------
    ohwait = st.toggle("is it nuFnu instead of Fnu")

    islog = st.toggle("input in log value?",value=True)
    if islog:
        log10_distance = st.number_input("Enter the distance in log10(cm)", value=16.49)
        distance_cm = 10 ** log10_distance
    else:
        distance_cm =st.number_input("Enter the distance in cm", value=3.086e18)
#-------------------------------------------------FIND LUMINOSIY------------------------------------------------
    if st.button("Calculate Luminosity"):
        #- - - - - - - - - - - - - - - - - - - -CHECK VALID ENTERIES- - - - - - - - - - - - - - - - 
        energy_numeric = pd.to_numeric(df[energy_col], errors='coerce')
        invalid_energy = df[energy_numeric.isna()]
        if not invalid_energy.empty:
            st.error(f"Non-numeric values found in '{energy_col}' at rows: {invalid_energy.index.tolist()}")
            st.write("Problematic rows (energy):")
            st.dataframe(invalid_energy)
            st.stop()

        nuFnu_numeric = pd.to_numeric(df[nuFnu], errors='coerce')
        invalid_flux = df[nuFnu_numeric.isna()]
        if not invalid_flux.empty:
            st.error(f"Non-numeric values found in '{nuFnu}' at rows: {invalid_flux.index.tolist()}")
            st.write("Problematic rows (flux):")
            st.dataframe(invalid_flux)
            st.stop()

        df[energy_col] = energy_numeric
        df[nuFnu] = nuFnu_numeric
 #- - - - - - - - - - - - - - - - - - - -CHECK MONOTONICALLY INCREASING- - - - - - - - - - - - - - - - 

        if not df[energy_col].is_monotonic_increasing:
            unsorted_mask = df[energy_col] != df[energy_col].sort_values().values
            unsorted_rows = df[unsorted_mask]

            st.warning("Energy values were not sorted. Sorting has been applied for accurate plotting and integration.")
            st.write("### ⚠️ Rows out of order (before sorting):")
            st.dataframe(unsorted_rows)

            df = df.sort_values(by=energy_col).reset_index(drop=True)
        else:
            st.info("Energy values are already sorted.")
        #- - - - - - - - - - - - - - - - - - - -CONVERT UNITS- - - - - - - - - - - - - - - - 

        rydberg_to_erg = 2.1798723611035e-11
        h = 6.62607015e-27

        energy_raw = df[energy_col] #RYDBERG
        freq = energy_raw * rydberg_to_erg / h  # Hz

        nfn = df[nuFnu]
        #--------------
        #nfn just means second collumn to be processed. giving meaning here :
        if ohwait:
            flux= np.array([a/b for a,b in zip(nfn,freq)])
        else:
            flux=np.array(nfn)
        #--------------
        lum_density = flux * 4 * np.pi * distance_cm ** 2
        lum_type = "Luminosity density (erg/s/Hz)"

        df["Luminosity_Density"] = lum_density
        df["Frequency_Hz"] = freq

        st.write(f"### Data with {lum_type}")
        df_display = df.copy()
        for col in df.columns.tolist():
            df_display[col] = df[col].map(lambda x: f"{x:.3e}")
        
        st.write(f"### Data with {lum_type} (scientific notation)")
        st.dataframe(df_display)

        fig, ax = plt.subplots()
        ax.plot(energy_raw, lum_density, label=lum_type)
        ax.set_xlabel("Energy (Rydberg)")
        ax.set_ylabel("Luminosity density")
        ax.set_title(f"{lum_type} vs Energy")
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

     
        total_luminosity = np.trapz(lum_density, freq)
        
        def integrate_curve(x, y,a=1,b=1): 
            integral = 0.0
            for i in range(1,len(x)):
                if y[i-1]!=np.inf and y[i]!=np.inf:
                    dx = (x[i] - x[i-1]) #/a
                    dy = (np.float128(y[i]) + np.float128(y[i-1])) #/b
                    integral +=  (np.float128(dy)*np.float128(dx))#*(a*b)
            return integral
        st.success(f"### Total Bolometric Luminosity by np: {total_luminosity:.3e} erg/s")
        st.info(f' Total Bolometric Luminosity by dxdy : {integrate_curve(lum_density, freq)} erg/s')
