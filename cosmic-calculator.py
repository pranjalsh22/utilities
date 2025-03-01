import streamlit as st
from math import *

def cosmology_calculator(z, H0, WM, WV, verbose=False):
    WR = 0.0        # Omega(radiation)
    WK = 0.0        # Omega curvature = 1 - Omega(total)
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

    # Loop to calculate age and redshift-related values
    for i in range(n):
        a = az * (i + 0.5) / n
        adot = sqrt(WK + (WM / a) + (WR / (a * a)) + (WV * a * a))
        age = age + 1.0 / adot

    zage = az * age / n
    zage_Gyr = (Tyr / H0) * zage
    DTT = 0.0
    DCMR = 0.0

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

    # Calculate angular size and luminosity distances
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

    # Compute comoving volume
    ratio = 1.0
    x = sqrt(abs(WK)) * DCMR
    if x > 0.1:
        if WK > 0:
            ratio = (0.125 * (exp(2.0 * x) - exp(-2.0 * x)) - x / 2.0) / (x * x * x / 3.0)
        else:
            ratio = (x / 2.0 - sin(2.0 * x) / 4.0) / (x * x * x / 3.0)
    else:
        y = x * x
        if WK < 0:
            y = -y
        ratio = 1.0 + y / 5.0 + (2.0 / 105.0) * y * y

    VCM = ratio * DCMR * DCMR * DCMR / 3.0
    V_Gpc = 4.0 * pi * ((0.001 * c / H0) ** 3) * VCM

    # Output results
    if verbose:
        st.write(f"For H_o = {H0}, Omega_M = {WM}, Omega_vac = {WV}, z = {z}")
        st.write(f"It is now {age_Gyr:.1f} Gyr since the Big Bang.")
        st.write(f"The age at redshift z was {zage_Gyr:.1f} Gyr.")
        st.write(f"The light travel time was {DTT_Gyr:.1f} Gyr.")
        st.write(f"The comoving radial distance is {DCMR_Mpc:.1f} Mpc or {DCMR_Gyr:.1f} Gly.")
        st.write(f"The comoving volume within redshift z is {V_Gpc:.1f} Gpc^3.")
        st.write(f"The angular size distance D_A is {DA_Mpc:.1f} Mpc or {DA_Gyr:.1f} Gly.")
        st.write(f"This gives a scale of {kpc_DA:.2f} kpc/".")
        st.write(f"The luminosity distance D_L is {DL_Mpc:.1f} Mpc or {DL_Gyr:.1f} Gly.")
        st.write(f"The distance modulus, m-M, is {(5 * log10(DL_Mpc * 1e6) - 5):.2f}")
    else:
        st.write(f"{zage_Gyr:.2f}, {DCMR_Mpc:.2f}, {kpc_DA:.2f}, {(5 * log10(DL_Mpc * 1e6) - 5):.2f}")

def main():
    st.title('Cosmology Calculator')

    # User Inputs
    z = st.number_input('Redshift (z)', min_value=0.0, value=1.0, step=0.1)
    H0 = st.number_input('Hubble Constant (H0)', min_value=50.0, value=75.0, step=1.0)
    WM = st.number_input('Omega_M (Omega_m)', min_value=0.0, max_value=1.0, value=0.3, step=0.01)
    WV = st.number_input('Omega_vac (Omega_lambda)', min_value=0.0, max_value=1.0, value=0.7, step=0.01)
    verbose = st.checkbox('Verbose Output', value=False)

    if st.button('Calculate'):
        cosmology_calculator(z, H0, WM, WV, verbose)

if __name__ == "__main__":
    main()
import streamlit as st
from math import *

def cosmology_calculator(z, H0, WM, WV, verbose=False):
    WR = 0.0        # Omega(radiation)
    WK = 0.0        # Omega curvature = 1 - Omega(total)
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

    # Loop to calculate age and redshift-related values
    for i in range(n):
        a = az * (i + 0.5) / n
        adot = sqrt(WK + (WM / a) + (WR / (a * a)) + (WV * a * a))
        age = age + 1.0 / adot

    zage = az * age / n
    zage_Gyr = (Tyr / H0) * zage
    DTT = 0.0
    DCMR = 0.0

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

    # Calculate angular size and luminosity distances
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

    # Compute comoving volume
    ratio = 1.0
    x = sqrt(abs(WK)) * DCMR
    if x > 0.1:
        if WK > 0:
            ratio = (0.125 * (exp(2.0 * x) - exp(-2.0 * x)) - x / 2.0) / (x * x * x / 3.0)
        else:
            ratio = (x / 2.0 - sin(2.0 * x) / 4.0) / (x * x * x / 3.0)
    else:
        y = x * x
        if WK < 0:
            y = -y
        ratio = 1.0 + y / 5.0 + (2.0 / 105.0) * y * y

    VCM = ratio * DCMR * DCMR * DCMR / 3.0
    V_Gpc = 4.0 * pi * ((0.001 * c / H0) ** 3) * VCM

    # Output results
    if verbose:
        st.write(f"For H_o = {H0}, Omega_M = {WM}, Omega_vac = {WV}, z = {z}")
        st.write(f"It is now {age_Gyr:.1f} Gyr since the Big Bang.")
        st.write(f"The age at redshift z was {zage_Gyr:.1f} Gyr.")
        st.write(f"The light travel time was {DTT_Gyr:.1f} Gyr.")
        st.write(f"The comoving radial distance is {DCMR_Mpc:.1f} Mpc or {DCMR_Gyr:.1f} Gly.")
        st.write(f"The comoving volume within redshift z is {V_Gpc:.1f} Gpc^3.")
        st.write(f"The angular size distance D_A is {DA_Mpc:.1f} Mpc or {DA_Gyr:.1f} Gly.")
        st.write(f"This gives a scale of {kpc_DA:.2f} kpc/".")
        st.write(f"The luminosity distance D_L is {DL_Mpc:.1f} Mpc or {DL_Gyr:.1f} Gly.")
        st.write(f"The distance modulus, m-M, is {(5 * log10(DL_Mpc * 1e6) - 5):.2f}")
    else:
        st.write(f"{zage_Gyr:.2f}, {DCMR_Mpc:.2f}, {kpc_DA:.2f}, {(5 * log10(DL_Mpc * 1e6) - 5):.2f}")

def main():
    st.title('Cosmology Calculator')

    # User Inputs
    z = st.number_input('Redshift (z)', min_value=0.0, value=1.0, step=0.1)
    H0 = st.number_input('Hubble Constant (H0)', min_value=50.0, value=75.0, step=1.0)
    WM = st.number_input('Omega_M (Omega_m)', min_value=0.0, max_value=1.0, value=0.3, step=0.01)
    WV = st.number_input('Omega_vac (Omega_lambda)', min_value=0.0, max_value=1.0, value=0.7, step=0.01)
    verbose = st.checkbox('Verbose Output', value=False)

    if st.button('Calculate'):
        cosmology_calculator(z, H0, WM, WV, verbose)

if __name__ == "__main__":
    main()
