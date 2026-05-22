import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import os
from scipy.interpolate import interp1d
from astropy import units as u
from astropy.constants import c


from astropy.table import Table
from astropy.io import fits

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Multi-Spectrum Combiner",
    layout="wide"
)

st.title("Astrophysical Multi-Spectrum Combiner")

st.markdown("""
Upload multiple spectra with different:
- x-axis grids,
- x-axis units,
- y-axis definitions.

The app converts everything internally to:
- Frequency (Hz)
- F_nu

Then interpolates and combines all spectra.
""")

# ============================================================
# FUNCTIONS
# ============================================================

def load_spectrum(uploaded_file):

    filename = uploaded_file.name.lower()

    ext = os.path.splitext(filename)[1]

    # ======================================================
    # FITS
    # ======================================================

    if ext in [".fits", ".fit", ".fts"]:

        hdul = fits.open(uploaded_file)

        data = hdul[1].data

        df = pd.DataFrame(data)

        hdul.close()

    # ======================================================
    # XLSX
    # ======================================================

    elif ext == ".xlsx":

        df = pd.read_excel(uploaded_file)

    # ======================================================
    # TEXT-BASED FILES
    # ======================================================

    else:

        uploaded_file.seek(0)

        try:

            # Astropy auto-detects format
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

    # ======================================================
    # VALIDATION
    # ======================================================

    if len(df.columns) < 2:

        st.error(
            f"{uploaded_file.name} has fewer than 2 columns."
        )

        return None, None

    # ======================================================
    # SHOW DETECTED COLUMNS
    # ======================================================

    st.write(f"Detected columns in {uploaded_file.name}:")
    st.write(df.head())

    # ======================================================
    # USER SELECTS COLUMNS
    # ======================================================

    col1, col2 = st.columns(2)

    with col1:

        x_col = st.selectbox(
            f"X column ({uploaded_file.name})",
            df.columns,
            key=f"xcol_{uploaded_file.name}"
        )

    with col2:

        y_col = st.selectbox(
            f"Y column ({uploaded_file.name})",
            df.columns,
            key=f"ycol_{uploaded_file.name}"
        )

    # ======================================================
    # CONVERT TO NUMERIC
    # ======================================================

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

    # ======================================================
    # CHECK FOR NaNs
    # ======================================================

    if np.any(~np.isfinite(x)):

        st.warning(
            f"{uploaded_file.name}: X column contains invalid values."
        )

    if np.any(~np.isfinite(y)):

        st.warning(
            f"{uploaded_file.name}: Y column contains invalid values."
        )

    return x, y
# ============================================================
# X CONVERSION
# ============================================================

def convert_x_to_frequency(x, xtype, unit):

    if xtype == "Frequency":

        quantity = x * u.Unit(unit)

        nu = quantity.to(u.Hz)

    elif xtype == "Wavelength":

        quantity = x * u.Unit(unit)

        nu = quantity.to(
            u.Hz,
            equivalencies=u.spectral()
        )

    elif xtype == "Energy":

        quantity = x * u.Unit(unit)

        wavelength = quantity.to(
            u.m,
            equivalencies=u.spectral()
        )

        nu = wavelength.to(
            u.Hz,
            equivalencies=u.spectral()
        )

    return nu.value


# ============================================================
# Y CONVERSION
# ============================================================

def convert_y_to_fnu(nu, y, ytype):

    lam = c.value / nu

    if ytype == "F_nu":
        return y

    elif ytype == "nuF_nu":
        return y / nu

    elif ytype == "F_lambda":
        return y * (lam**2 / c.value)

    elif ytype == "lambdaF_lambda":

        f_lambda = y / lam

        return f_lambda * (lam**2 / c.value)

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
    )

    x = x[mask]
    y = y[mask]

    interp_func = interp1d(
        np.log10(x),
        np.log10(y),
        bounds_error=False,
        fill_value=-np.inf
    )

    y_new = 10**interp_func(
        np.log10(common_x)
    )

    y_new[np.isinf(y_new)] = 0

    return y_new


# ============================================================
# FILE UPLOAD
# ============================================================

uploaded_files = st.file_uploader(
    "Upload Spectra",
    type=["csv", "txt", "dat"],
    accept_multiple_files=True
)

# ============================================================
# MAIN
# ============================================================

if uploaded_files:

    spectra = []

    st.sidebar.header("Spectrum Settings")

    # --------------------------------------------------------
    # USER SETTINGS FOR EACH FILE
    # --------------------------------------------------------

    for i, uploaded_file in enumerate(uploaded_files):

        st.sidebar.subheader(f"Spectrum {i+1}")

        x_type = st.sidebar.selectbox(
            f"X-axis Type ({uploaded_file.name})",
            ["Frequency", "Wavelength", "Energy"],
            key=f"x_type_{i}"
        )

    
        # ======================================================
        # UNIT OPTIONS
        # ======================================================
        
        frequency_units = [
            "Hz",
            "kHz",
            "MHz",
            "GHz",
            "THz"
        ]
        
        wavelength_units = [
            "Angstrom",
            "nm",
            "um",
            "mm",
            "cm",
            "m"
        ]
        
        energy_units = [
            "eV",
            "keV",
            "MeV",
            "GeV"
        ]
        
        # ======================================================
        # UNIT SELECTOR
        # ======================================================
        
        if x_type == "Frequency":
        
            x_unit = st.sidebar.selectbox(
                f"Frequency Unit ({uploaded_file.name})",
                frequency_units,
                key=f"x_unit_{i}"
            )
        
        elif x_type == "Wavelength":
        
            x_unit = st.sidebar.selectbox(
                f"Wavelength Unit ({uploaded_file.name})",
                wavelength_units,
                key=f"x_unit_{i}"
            )
        
        elif x_type == "Energy":
        
            x_unit = st.sidebar.selectbox(
                f"Energy Unit ({uploaded_file.name})",
                energy_units,
                key=f"x_unit_{i}"
            )
        y_type = st.sidebar.selectbox(
            f"Y-axis Type ({uploaded_file.name})",
            ["F_nu", "nuF_nu", "F_lambda", "lambdaF_lambda"],
            key=f"y_type_{i}"
        )

        # ----------------------------------------------------
        # LOAD DATA
        # ----------------------------------------------------

        x, y = load_spectrum(uploaded_file)

        if x is None:
            continue

        # ----------------------------------------------------
        # CONVERT X
        # ----------------------------------------------------

        nu = convert_x_to_frequency(
            x,
            x_type,
            x_unit
        )

        # ----------------------------------------------------
        # CONVERT Y
        # ----------------------------------------------------

        fnu = convert_y_to_fnu(
            nu,
            y,
            y_type
        )

        # ----------------------------------------------------
        # SORT
        # ----------------------------------------------------

        sort_idx = np.argsort(nu)

        nu = nu[sort_idx]
        fnu = fnu[sort_idx]

        spectra.append({
            "name": uploaded_file.name,
            "nu": nu,
            "fnu": fnu
        })

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

        total_fnu += interp_flux

    # ========================================================
    # TABS
    # ========================================================

    tab1, tab2, tab3 = st.tabs([
        "Original Spectra",
        "Interpolated Spectra",
        "Combined Spectrum"
    ])

    # ========================================================
    # ORIGINAL
    # ========================================================

    with tab1:

        fig = go.Figure()

        for spectrum in spectra:

            fig.add_trace(
                go.Scatter(
                    x=spectrum["nu"],
                    y=spectrum["fnu"],
                    mode='lines',
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

            fig.add_trace(
                go.Scatter(
                    x=common_nu,
                    y=interp_spec["flux"],
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

            fig.add_trace(
                go.Scatter(
                    x=common_nu,
                    y=interp_spec["flux"],
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

    # add individual components
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
