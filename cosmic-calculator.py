import streamlit as st
from math import *

# Function to perform the cosmological calculations
def cosmology_calculator(z, H0, WM, WV):
    WR = 0.0
    WK = 0.0
    c = 299792.458  # velocity of light in km/sec
    Tyr = 977.8     # coefficient for converting 1/H into Gyr
    n = 1000        # number of points in integrals

    h = H0 / 100.0
    WR = 4.165E-5 / (h * h)  # includes 3 massless neutrino species, T0 = 2.72528
    WK = 1 - WM - WR - WV
    az = 1.0 / (1.0 + z)
    age = 0.0
    zage = 0.1
    DTT = 0.5
    DCMR = 0.0

    # Perform integral calculations for age and distances
    for i in range(n):
        a = az * (i + 0.5) / n
        adot = sqrt(WK + (WM / a) + (WR / (a * a)) + (WV * a * a))
        age = age + 1.0 / adot

    zage = az * age / n
    zage_Gyr = (Tyr / H0) * zage
    DTT = 0.0
    DCMR = 0.0

    # Comoving distance calculation
    for i in range(n):
        a = az + (1 - az) * (i + 0.5) / n
        adot = sqrt(WK + (WM / a) + (WR / (a * a)) + (WV * a * a))
        DTT = DTT + 1.0 / adot
        DCMR = DCMR + 1.0 / (a * adot)

    DTT = (1.0 - az) * DTT / n
    DCMR = (1.0 - az) * DCMR / n
    age = DTT + zage
    age_Gyr = age * (Tyr / H0)
    DTT_Gyr = (Tyr / H0) * DTT
    DCMR_Gyr = (Tyr / H0) * DCMR
    DCMR_Mpc = (c / H0) * DCMR

    # Angular size distance and luminosity distance
    ratio = 1.0
    x = sqrt(abs(WK)) * DCMR
    if x > 0.1:
        if WK > 0:
            ratio = 0.5 * (exp(x) - exp(-x)) / x
        else:
            ratio = sin(x) / x
    else:
        y = x * x
        if WK < 0:
            y = -y
        ratio = 1.0 + y / 6.0 + y * y / 120.0

    DCMT = ratio * DCMR
    DA = az * DCMT
    DA_Mpc = (c / H0) * DA
    kpc_DA = DA_Mpc / 206.264806
    DA_Gyr = (Tyr / H0) * DA
    DL = DA / (az * az)
    DL_Mpc = (c / H0) * DL
    DL_Gyr = (Tyr / H0) * DL

    # Volume calculation
    VCM = ratio * DCMR * DCMR * DCMR / 3.0
    V_Gpc = 4.0 * pi * ((0.001 * c / H0) ** 3) * VCM

    return {
        "age_Gyr": age_Gyr,
        "zage_Gyr": zage_Gyr,
        "DCMR_Mpc": DCMR_Mpc,
        "DCMR_Gyr": DCMR_Gyr,
        "DA_Mpc": DA_Mpc,
        "DA_Gyr": DA_Gyr,
        "kpc_DA": kpc_DA,
        "DL_Mpc": DL_Mpc,
        "DL_Gyr": DL_Gyr,
        "V_Gpc": V_Gpc
    }

# Displaying Formulas
st.title('Cosmology Calculator')

# Input fields for cosmology parameters
z = st.number_input('Redshift (z)', min_value=0.0, value=1.0, step=0.1)
H0 = st.number_input('Hubble Constant (H₀)', min_value=50.0, value=75.0, step=1.0)
WM = st.number_input('Omega Matter (Ωₘ)', min_value=0.0, max_value=1.0, value=0.3, step=0.01)
WV = st.number_input('Omega Vacuum (Ωλ)', min_value=0.0, max_value=1.0, value=0.7, step=0.01)

# Displaying formulas and their meanings using st.columns
st.subheader('Formulas Used:')
col1, col2 = st.columns([3, 1])

with col1:
    st.latex(r"a = \frac{1}{1+z}")
    st.latex(r"Age = \int_{a(z)}^{1} \frac{da}{a \sqrt{ \Omega_k + \frac{\Omega_m}{a} + \frac{\Omega_r}{a^2} + \Omega_\Lambda a^2 }}")
    st.latex(r"D_{CMR} = \int_{a(z)}^{1} \frac{da}{a \sqrt{\Omega_k + \frac{\Omega_m}{a} + \frac{\Omega_r}{a^2} + \Omega_\Lambda a^2 }}")
    st.latex(r"D_A = \frac{D_{CMR}}{1+z}")
    st.latex(r"D_L = D_A \cdot (1+z)^2")
    st.latex(r"V = \frac{D_{CMR}^3}{3}")

with col2:
    st.write("**a (Scale Factor)**: Fractional size of the universe at redshift z.")
    st.write("**Ωₘ (Matter Density)**: Fraction of the universe's energy density due to matter.")
    st.write("**Ωλ (Vacuum Density)**: Fraction of the universe's energy density due to dark energy.")
    st.write("**Ωₖ (Curvature Density)**: Fraction of the universe's energy density due to spatial curvature.")
    st.write("**Ωᵣ (Radiation Density)**: Fraction of the universe's energy density due to radiation (massless neutrinos).")

# Calculation button
if st.button('Calculate'):
    results = cosmology_calculator(z, H0, WM, WV)

    # Display results using st.info and st.success for clarity
    st.info("### Cosmology Results")
    st.success(f"**Age of the Universe**: {results['age_Gyr']:.1f} Gyr")
    st.success(f"**Age at Redshift z = {z}**: {results['zage_Gyr']:.1f} Gyr")
    st.success(f"**Comoving Radial Distance (Dₖ)**: {results['DCMR_Mpc']:.1f} Mpc or {results['DCMR_Gyr']:.1f} Gly")
    st.success(f"**Angular Size Distance (Dₐ)**: {results['DA_Mpc']:.1f} Mpc or {results['DA_Gyr']:.1f} Gly")
    st.success(f"**Scale (kpc/”)**: {results['kpc_DA']:.2f} kpc/”")
    st.success(f"**Luminosity Distance (Dₗ)**: {results['DL_Mpc']:.1f} Mpc or {results['DL_Gyr']:.1f} Gly")
    st.success(f"**Comoving Volume (V)**: {results['V_Gpc']:.1f} Gpc³")
#--------
st.header("References")
st.markdown('[Astro.ucla.edu](https://www.astro.ucla.edu/~wright/CC.python)')
