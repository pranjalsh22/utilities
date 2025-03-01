import streamlit as st
from math import *

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

    # LaTeX: Redshift relation
    st.latex(r"a = \frac{1}{1+z}")
    
    # LaTeX: Age of the Universe formula
    st.latex(r"Age = \int_{a(z)}^{1} \frac{da}{a \sqrt{ \Omega_k + \frac{\Omega_m}{a} + \frac{\Omega_r}{a^2} + \Omega_\Lambda a^2 }}")

    for i in range(n):
        a = az * (i + 0.5) / n
        adot = sqrt(WK + (WM / a) + (WR / (a * a)) + (WV * a * a))
        age = age + 1.0 / adot

    zage = az * age / n
    zage_Gyr = (Tyr / H0) * zage
    DTT = 0.0
    DCMR = 0.0

    # LaTeX: Comoving Distance formula
    st.latex(r"D_{CMR} = \int_{a(z)}^{1} \frac{da}{a \sqrt{\Omega_k + \frac{\Omega_m}{a} + \frac{\Omega_r}{a^2} + \Omega_\Lambda a^2 }}")

    # Do integral over a = 1/(1+z) from az to 1 in n steps, midpoint rule
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

    # LaTeX: Angular size distance formula
    st.latex(r"D_A = \frac{D_{CMR}}{1+z}")

    # LaTeX: Luminosity distance formula
    st.latex(r"D_L = D_A \cdot (1+z)^2")

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

    # LaTeX: Volume formula
    st.latex(r"V = \frac{D_{CMR}^3}{3}")

    VCM = ratio * DCMR * DCMR * DCMR / 3.0
    V_Gpc = 4.0 * pi * ((0.001 * c / H0) ** 3) * VCM

    # Display results using Streamlit info and success for clear visualization
    st.info(f"**For Hubble Constant (H₀):** {H0} km/s/Mpc")
    st.info(f"**Omega Matter (Ωₘ):** {WM}")
    st.info(f"**Omega Vacuum (Ωλ):** {WV}")
    st.info(f"**Redshift (z):** {z}")
    
    st.success(f"The current age of the universe is: **{age_Gyr:.1f} Gyr**")
    st.success(f"The age at redshift z was: **{zage_Gyr:.1f} Gyr**")
    st.success(f"The comoving radial distance is: **{DCMR_Mpc:.1f} Mpc** or **{DCMR_Gyr:.1f} Gly**")
    st.success(f"The angular size distance (Dₐ) is: **{DA_Mpc:.1f} Mpc** or **{DA_Gyr:.1f} Gly**")
    st.success(f"The luminosity distance (Dₗ) is: **{DL_Mpc:.1f} Mpc** or **{DL_Gyr:.1f} Gly**")
    st.success(f"The scale is: **{kpc_DA:.2f} kpc/”**")
    st.success(f"The comoving volume at redshift z is: **{V_Gpc:.1f} Gpc³**")

def main():
    st.title('Cosmology Calculator')

    z = st.number_input('Redshift (z)', min_value=0.0, value=1.0, step=0.1)
    H0 = st.number_input('Hubble Constant (H₀)', min_value=50.0, value=75.0, step=1.0)
    WM = st.number_input('Omega Matter (Ωₘ)', min_value=0.0, max_value=1.0, value=0.3, step=0.01)
    WV = st.number_input('Omega Vacuum (Ωλ)', min_value=0.0, max_value=1.0, value=0.7, step=0.01)

    if st.button('Calculate'):
        cosmology_calculator(z, H0, WM, WV)

if __name__ == "__main__":
    main()
