import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import os

from scipy.interpolate import interp1d
from astropy import units as u
from astropy.table import Table
from astropy.io import fits

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Multi-Spectrum Combiner",
    layout="wide"
)

st.title("Multi-Spectrum Frequency Combiner")

st.markdown("""
Upload multiple spectra in frequency space.

Supported:
- Frequency units:
  Hz, kHz, MHz, GHz, THz

- Flux formats:
  F_nu
  nuF_nu

The app:
- converts all spectra to F_nu,
- interpolates onto a common frequency grid,
- combines all spectra,
- plots the total spectrum.
""")

# ============================================================
# FUNCTIONS
# ============================================================

def load_spectrum(uploaded_file):

    filename = uploaded_file.name.lower()

    ext = os.path.splitext(filename)[1]

    # ========================================================
    # FITS FILES
    # ========================================================

    if ext in [".fits", ".fit", ".fts"]:

        hdul = fits.open(uploaded_file)

        data = hdul[1].data

        df = pd.DataFrame(data)

        hdul.close()

    # ========================================================
    # EXCEL FILES
    # ========================================================

    elif ext == ".xlsx":

        df = pd.read_excel(uploaded_file)

    # ========================================================
    # TEXT-BASED FILES
    # ========================================================

    else:

        uploaded_file.seek(0)

        try:

            table = Table.read(
                uploaded_file,
                format="ascii"
            )

            df = table.to_pandas()

        except Exception as e:

            st.error(f"""
Could not parse file:

{uploaded_file.name}

Reason:
{e}
""")

            return None, None

    # ========================================================
    # VALIDATION
    # ========================================================

    if len(df.columns) < 2:

        st.error(
            f"{uploaded_file.name} has fewer than 2 columns."
        )

        return None, None

    # ========================================================
    # SHOW DETECTED COLUMNS
    # ========================================================

    st.write(f"Detected columns in {uploaded_file.name}")
    st.dataframe(df.head())

    # ========================================================
    # USER COLUMN SELECTION
    # ========================================================

    col1, col2 = st.columns(2)

    with col1:

        x_col = st.selectbox(
            f"Frequency Column ({uploaded_file.name})",
            df.columns,
            key=f"xcol_{uploaded_file.name}"
        )

    with col2:

        y_col = st.selectbox(
            f"Flux Column ({uploaded_file.name})",
            df.columns,
            key=f"ycol_{uploaded_file.name}"
        )

    # ========================================================
    # NUMERIC CONVERSION
    # ========================================================

    try:

        x = np.array(
            pd.to_numeric(df[x_col]),
            dtype=float
        )

        y = np.array(
            pd.to_numeric(df[y_col]),
            dtype=float
        )

    except Exception as e:

        st.error(f"""
Could not convert selected columns to numeric values.

Reason:
{e}
""")

        return None, None

    # ========================================================
    # VALIDATION
    # ========================================================

    if np.any(~np.isfinite(x)):

        st.warning(
            f"{uploaded_file.name}: Frequency column contains invalid values."
        )

    if np.any(~np.isfinite(y)):

        st.warning(
            f"{uploaded_file.name}: Flux column contains invalid values."
        )

    return x, y


# ============================================================
# X CONVERSION
# Frequency only
# ============================================================

def convert_x_to_frequency(x, unit):

    quantity = x * u.Unit(unit)

    nu = quantity.to(u.Hz)

    return nu.value


# ============================================================
# Y CONVERSION
# Only:
# F_nu
# nuF_nu
# ============================================================

def convert_y_to_fnu(nu, y, ytype):

    # already F_nu
    if ytype == "F_nu":

        return y

    # convert nuF_nu -> F_nu
    elif ytype == "nuF_nu":

        return y / nu

    else:

        return y


# ============================================================
# LOG INTERPOLATION
# ============================================================

def log_interp(x, y, common_x):

    mask = (
        (x > 0)
        &
        (y > 0)
        &
        np.isfinite(x)
        &
        np.isfinite(y)
    )

    x = x[mask]
    y = y[mask]

    interp_func = interp1d(
        np.log10(x),
        np.log10(y),
        bounds_error=False,
        fill_value=np.nan
    )

    interp_vals = interp_func(
        np.log10(common_x)
    )

    y_new = 10**interp_vals

    y_new[~np.isfinite(y_new)] = np.nan

    return y_new


# ============================================================
# FILE UPLOAD
# ============================================================

uploaded_files = st.file_uploader(
    "Upload Spectra",
    type=[
        "csv",
        "txt",
        "dat",
        "ascii",
        "ecsv",
        "fits",
        "fit",
        "fts",
        "xlsx"
    ],
    accept_multiple_files=True
)

# ============================================================
# MAIN
# ============================================================

if uploaded_files:

    spectra = []

    st.sidebar.header("Spectrum Settings")

    # ========================================================
    # UNIT OPTIONS
    # ========================================================

    frequency_units = [
        "Hz",
        "kHz",
        "MHz",
        "GHz",
        "THz"
    ]

    # ========================================================
    # PROCESS FILES
    # ========================================================

    for i, uploaded_file in enumerate(uploaded_files):

        st.sidebar.subheader(f"Spectrum {i+1}")

        # ----------------------------------------------------
        # FREQUENCY UNIT
        # ----------------------------------------------------

        x_unit = st.sidebar.selectbox(
            f"Frequency Unit ({uploaded_file.name})",
            frequency_units,
            key=f"x_unit_{i}"
        )

        # ----------------------------------------------------
        # Y TYPE
        # ----------------------------------------------------

        y_type = st.sidebar.selectbox(
            f"Y-axis Type ({uploaded_file.name})",
            ["F_nu", "nuF_nu"],
            key=f"y_type_{i}"
        )

        # ----------------------------------------------------
        # LOAD DATA
        # ----------------------------------------------------

        x, y = load_spectrum(uploaded_file)

        if x is None:
            continue

        # ----------------------------------------------------
        # CONVERT TO Hz
        # ----------------------------------------------------

        nu = convert_x_to_frequency(
            x,
            x_unit
        )

        # ----------------------------------------------------
        # CONVERT TO F_nu
        # ----------------------------------------------------

        fnu = convert_y_to_fnu(
            nu,
            y,
            y_type
        )

        # ----------------------------------------------------
        # CLEANING
        # ----------------------------------------------------

        mask = (
            np.isfinite(nu)
            &
            np.isfinite(fnu)
            &
            (nu > 0)
            &
            (fnu > 0)
        )

        nu = nu[mask]
        fnu = fnu[mask]

        # ----------------------------------------------------
        # SORT
        # ----------------------------------------------------

        sort_idx = np.argsort(nu)

        nu = nu[sort_idx]
        fnu = fnu[sort_idx]

        # ----------------------------------------------------
        # STORE
        # ----------------------------------------------------

        spectra.append({
            "name": uploaded_file.name,
            "nu": nu,
            "fnu": fnu
        })

    # ========================================================
    # VALIDATE
    # ========================================================

    if len(spectra) == 0:

        st.error("No valid spectra loaded.")

        st.stop()

    # ========================================================
    # COMMON GRID
    # ========================================================

    min_nu = min([
        s["nu"].min()
        for s in spectra
    ])

    max_nu = max([
        s["nu"].max()
        for s in spectra
    ])

    common_nu = np.logspace(
        np.log10(min_nu),
        np.log10(max_nu),
        5000
    )

    # ========================================================
    # INTERPOLATE + SUM
    # ========================================================

    interpolated_spectra = []

    total_fnu = np.zeros_like(common_nu)

    for spectrum in spectra:

        interp_flux = log_interp(
            spectrum["nu"],
            spectrum["fnu"],
            common_nu
        )

        interpolated_spectra.append({
            "name": spectrum["name"],
            "flux": interp_flux
        })

        total_fnu += np.nan_to_num(interp_flux)

    # ========================================================
    # TABS
    # ========================================================

    tab1, tab2, tab3 = st.tabs([
        "Original Spectra",
        "Interpolated Spectra",
        "Combined Spectrum"
    ])

    # ========================================================
    # ORIGINAL SPECTRA
    # ========================================================

    with tab1:

        fig = go.Figure()

        for spectrum in spectra:

            fig.add_trace(
                go.Scatter(
                    x=spectrum["nu"],
                    y=spectrum["fnu"],
                    mode='lines+markers',
                    name=spectrum["name"]
                )
            )

        fig.update_layout(
            title="Original Spectra",
            xaxis_title="Frequency (Hz)",
            yaxis_title="F_nu",
            xaxis_type="log",
            yaxis_type="log",
            height=700
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ========================================================
    # INTERPOLATED
    # ========================================================

    with tab2:

        fig = go.Figure()

        for interp_spec in interpolated_spectra:

            mask = np.isfinite(interp_spec["flux"])

            fig.add_trace(
                go.Scatter(
                    x=common_nu[mask],
                    y=interp_spec["flux"][mask],
                    mode='lines',
                    name=interp_spec["name"]
                )
            )

        fig.update_layout(
            title="Interpolated Spectra",
            xaxis_title="Frequency (Hz)",
            yaxis_title="F_nu",
            xaxis_type="log",
            yaxis_type="log",
            height=700
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ========================================================
    # COMBINED
    # ========================================================

    with tab3:

        fig = go.Figure()

        # individual components
        for interp_spec in interpolated_spectra:

            mask = np.isfinite(interp_spec["flux"])

            fig.add_trace(
                go.Scatter(
                    x=common_nu[mask],
                    y=interp_spec["flux"][mask],
                    mode='lines',
                    opacity=0.4,
                    name=interp_spec["name"]
                )
            )

        # total spectrum
        fig.add_trace(
            go.Scatter(
                x=common_nu,
                y=total_fnu,
                mode='lines',
                line=dict(width=4),
                name='TOTAL'
            )
        )

        fig.update_layout(
            title="Combined Spectrum",
            xaxis_title="Frequency (Hz)",
            yaxis_title="F_nu",
            xaxis_type="log",
            yaxis_type="log",
            height=700
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ========================================================
    # DOWNLOAD
    # ========================================================

    output_df = pd.DataFrame({
        "Frequency_Hz": common_nu,
        "Fnu_Total": total_fnu
    })

    # add individual spectra
    for interp_spec in interpolated_spectra:

        output_df[
            interp_spec["name"]
        ] = interp_spec["flux"]

    csv = output_df.to_csv(index=False)

    st.download_button(
        label="Download Combined Spectrum CSV",
        data=csv,
        file_name="combined_spectrum.csv",
        mime="text/csv"
    )

# ============================================================
# EMPTY
# ============================================================

else:

    st.info("Upload one or more spectra.")
