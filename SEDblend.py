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
    page_title="SEDBlend",
    layout="wide"
)

st.title("SEDBlend")

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
# SPECTRAL REGIONS
# ============================================================

def add_spectral_regions(fig):

    spectral_regions = [

        {
            "name": "Radio",
            "x0": 1e6,
            "x1": 3e11,
            "color": "rgba(0, 100, 255, 1)"
        },

        {
            "name": "Microwave",
            "x0": 3e11,
            "x1": 3e12,
            "color": "rgba(0, 255, 255, 1)"
        },

        {
            "name": "Infrared",
            "x0": 3e12,
            "x1": 4e14,
            "color": "rgba(255, 140, 0, 1)"
        },

        {
            "name": "Optical",
            "x0": 4e14,
            "x1": 7.5e14,
            "color": "rgba(255, 255, 0, 1)"
        },

        {
            "name": "Ultraviolet",
            "x0": 7.5e14,
            "x1": 3e16,
            "color": "rgba(180, 0, 255, 1)"
        },

        {
            "name": "X-ray",
            "x0": 3e16,
            "x1": 3e19,
            "color": "rgba(255, 0, 0, 1)"
        },

        {
            "name": "Gamma-ray",
            "x0": 3e19,
            "x1": 1e25,
            "color": "rgba(100, 100, 100, 1)"
        }
    ]

    for region in spectral_regions:

        fig.add_vrect(
            x0=region["x0"],
            x1=region["x1"],

            fillcolor=region["color"],

            opacity=1,

            line_width=0,

            annotation_text=region["name"],

            annotation_position="top left",

            annotation=dict(
                font_size=12,
                font_color="black"
            )
        )

    return fig


# ============================================================
# LOAD SPECTRUM
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
    # TEXT FILES
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
    # SHOW COLUMNS
    # ========================================================

    st.subheader(f"Detected Columns: {uploaded_file.name}")

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

    return x, y


# ============================================================
# X CONVERSION
# ============================================================

def convert_x_to_frequency(x, unit):

    quantity = x * u.Unit(unit)

    nu = quantity.to(u.Hz)

    return nu.value


# ============================================================
# Y CONVERSION
# ============================================================

def convert_y_to_fnu(nu, y, ytype):

    if ytype == "F_nu":

        return y

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

    frequency_units = [
        "Hz",
        "kHz",
        "MHz",
        "GHz",
        "THz"
    ]

    # ========================================================
    # PLOT MODE
    # ========================================================

    plot_mode = st.sidebar.selectbox(
        "Plot Representation",
        ["F_nu", "nuF_nu"]
    )

    # ========================================================
    # PROCESS FILES
    # ========================================================

    for i, uploaded_file in enumerate(uploaded_files):

        st.sidebar.subheader(f"Spectrum {i+1}")

        x_unit = st.sidebar.selectbox(
            f"Frequency Unit ({uploaded_file.name})",
            frequency_units,
            key=f"x_unit_{i}"
        )

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
        # CLEAN
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

        valid = np.isfinite(interp_flux)

        total_fnu[valid] += interp_flux[valid]

    total_fnu[total_fnu == 0] = np.nan

    # ========================================================
    # PLOT CONFIG
    # ========================================================

    plot_config = {

        "displayModeBar": True,

        "modeBarButtonsToRemove": [
            "lasso2d",
            "select2d",
            "autoScale2d"
        ],

        "toImageButtonOptions": {

            "format": "png",
            "filename": "SEDBlend",
            "height": 900,
            "width": 1600,
            "scale": 3
        },

        "scrollZoom": True,
        "responsive": True
    }

    # ========================================================
    # COMMON LAYOUT
    # ========================================================

    def apply_layout(fig, title):

        fig.update_layout(

            title=title,

            xaxis_title="Frequency (Hz)",

            yaxis_title=plot_mode,

            height=700,

            hovermode="x unified",

            template="plotly_white",

            paper_bgcolor="white",
            plot_bgcolor="white",

            font=dict(
                size=16,
                color="black"
            ),

            legend=dict(
                bgcolor="rgba(255,255,255,0.7)",
                borderwidth=0
            ),

            margin=dict(
                l=40,
                r=40,
                t=60,
                b=40
            ),

            xaxis=dict(

                type="log",

                showgrid=True,

                gridcolor="rgba(0,0,0,0.12)",

                tickformat=".0e",

                exponentformat="power"
            ),

            yaxis=dict(

                type="log",

                showgrid=True,

                gridcolor="rgba(0,0,0,0.12)",

                tickformat=".0e",

                exponentformat="power"
            )
        )

        return fig

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

        fig = add_spectral_regions(fig)

        for spectrum in spectra:

            if plot_mode == "nuF_nu":

                plot_flux = (
                    spectrum["nu"]
                    *
                    spectrum["fnu"]
                )

            else:

                plot_flux = spectrum["fnu"]

            fig.add_trace(
                go.Scatter(
                    x=spectrum["nu"],
                    y=plot_flux,
                    mode='lines+markers',
                    name=spectrum["name"],

                    hovertemplate=
                    "Frequency: %{x:.3e} Hz<br>" +
                    "Flux: %{y:.3e}<extra></extra>"
                )
            )

        fig = apply_layout(fig, "Original Spectra")

        st.plotly_chart(
            fig,
            use_container_width=True,
            config=plot_config
        )

    # ========================================================
    # INTERPOLATED
    # ========================================================

    with tab2:

        fig = go.Figure()

        fig = add_spectral_regions(fig)

        for interp_spec in interpolated_spectra:

            mask = np.isfinite(interp_spec["flux"])

            if plot_mode == "nuF_nu":

                plot_flux = (
                    common_nu[mask]
                    *
                    interp_spec["flux"][mask]
                )

            else:

                plot_flux = interp_spec["flux"][mask]

            fig.add_trace(
                go.Scatter(
                    x=common_nu[mask],
                    y=plot_flux,
                    mode='lines',
                    name=interp_spec["name"],

                    hovertemplate=
                    "Frequency: %{x:.3e} Hz<br>" +
                    "Flux: %{y:.3e}<extra></extra>"
                )
            )

        fig = apply_layout(fig, "Interpolated Spectra")

        st.plotly_chart(
            fig,
            use_container_width=True,
            config=plot_config
        )

    # ========================================================
    # COMBINED
    # ========================================================

    with tab3:

        fig = go.Figure()

        fig = add_spectral_regions(fig)

        # ----------------------------------------------------
        # INDIVIDUAL COMPONENTS
        # ----------------------------------------------------

        for interp_spec in interpolated_spectra:

            mask = np.isfinite(interp_spec["flux"])

            if plot_mode == "nuF_nu":

                plot_flux = (
                    common_nu[mask]
                    *
                    interp_spec["flux"][mask]
                )

            else:

                plot_flux = interp_spec["flux"][mask]

            fig.add_trace(
                go.Scatter(
                    x=common_nu[mask],
                    y=plot_flux,
                    mode='lines',
                    opacity=0.35,
                    name=interp_spec["name"],

                    hovertemplate=
                    "Frequency: %{x:.3e} Hz<br>" +
                    "Flux: %{y:.3e}<extra></extra>"
                )
            )

        # ----------------------------------------------------
        # TOTAL
        # ----------------------------------------------------

        total_mask = np.isfinite(total_fnu)

        if plot_mode == "nuF_nu":

            total_plot = (
                common_nu[total_mask]
                *
                total_fnu[total_mask]
            )

        else:

            total_plot = total_fnu[total_mask]

        fig.add_trace(
            go.Scatter(
                x=common_nu[total_mask],
                y=total_plot,
                mode='lines',
                line=dict(width=5),
                name='TOTAL',

                hovertemplate=
                "Frequency: %{x:.3e} Hz<br>" +
                "Flux: %{y:.3e}<extra></extra>"
            )
        )

        fig = apply_layout(fig, "Combined Spectrum")

        st.plotly_chart(
            fig,
            use_container_width=True,
            config=plot_config
        )

else:

    st.info("Upload one or more spectra.")
