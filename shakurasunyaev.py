import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(page_title="Accretion Disk Calculator", layout="wide")

st.title("Accretion Disk Calculator")
st.write("Calculate the values of T and n for regions a, b, and c using the formulae and fiducial values given in the document.")


# ============================================================
# FUNCTIONS
# ============================================================

def eddington_luminosity(f1, m):
    return f1 * 10**38 * m


def eddington_accretion_rate(f1, etaE, m):
    return (f1 * (0.06 / etaE)) * 3.0e-8 * m


def temperature_a(alpha, m, rs):
    return 2.3e7 * 3**(3 / 4) * (alpha * m)**(-1 / 4) * rs**(-3 / 4)


def density_a(f1, etaE, alpha, m, mdot, rs):
    return (
        4.3e17
        * 3**(-3 / 2)
        * (f1 * (0.06 / etaE))**(-2)
        * alpha**(-1)
        * m**(-1)
        * mdot**(-2)
        * rs**(3 / 2)
        * (1 - (3 / rs)**0.5)**(-2)
    )


def temperature_b(f1, etaE, alpha, m, mdot, rs):
    return (
        3.1e8
        * 3**(9 / 10)
        * (f1 * (0.06 / etaE))**(2 / 5)
        * alpha**(-1 / 5)
        * m**(-1 / 5)
        * mdot**(2 / 5)
        * rs**(-9 / 10)
        * (1 - (3 / rs)**0.5)**(2 / 5)
    )


def density_b(f1, etaE, alpha, m, mdot, rs):
    return (
        4.2e24
        * 3**(33 / 20)
        * (f1 * (0.06 / etaE))**(2 / 5)
        * alpha**(-7 / 10)
        * m**(-7 / 10)
        * mdot**(2 / 5)
        * rs**(-33 / 20)
        * (1 - (3 / rs)**0.5)**(2 / 5)
    )


def temperature_c(f1, etaE, alpha, m, mdot, rs):
    return (
        8.6e7
        * 3**(3 / 4)
        * (f1 * (0.06 / etaE))**(3 / 10)
        * alpha**(-1 / 5)
        * m**(-1 / 5)
        * mdot**(3 / 10)
        * rs**(-3 / 4)
        * (1 - (3 / rs)**0.5)**(3 / 10)
    )


def density_c(f1, etaE, alpha, m, mdot, rs):
    return (
        3e25
        * 3**(15 / 8)
        * (f1 * (0.06 / etaE))**(11 / 12)
        * alpha**(-7 / 10)
        * m**(-7 / 10)
        * mdot**(11 / 12)
        * rs**(-15 / 8)
        * (1 - (3 / rs)**0.5)**(11 / 20)
    )


# ============================================================
# INPUT PARAMETERS
# ============================================================

st.header("Input Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    f1 = st.number_input("f₁", value=1.3, format="%.6f")
    etaE = st.number_input("ηE", value=0.1, format="%.6f")
    eta = st.number_input("η", value=0.05, format="%.6f")

with col2:
    alpha = st.number_input("α", value=0.1, format="%.6f")
    m = st.number_input("m (M☉)", value=1e8, format="%.6e")
    mdot = st.number_input("ṁ", value=1e-2, format="%.6e")

with col3:
    Rin = st.number_input("Rin (RS)", value=3.0, format="%.6f")
    Rtr = st.number_input("Rtr (RS)", value=50.0, format="%.6f")
    Rout = st.number_input("Rout (RS)", value=1e4, format="%.6e")
    rs = st.number_input("rs", value=50.0, format="%.6f")


# ============================================================
# CALCULATIONS
# ============================================================

LE = eddington_luminosity(f1, m)
MdotE = eddington_accretion_rate(f1, etaE, m)

Ta = temperature_a(alpha, m, rs)
na = density_a(f1, etaE, alpha, m, mdot, rs)

Tb = temperature_b(f1, etaE, alpha, m, mdot, rs)
nb = density_b(f1, etaE, alpha, m, mdot, rs)

Tc = temperature_c(f1, etaE, alpha, m, mdot, rs)
nc = density_c(f1, etaE, alpha, m, mdot, rs)


# ============================================================
# ACCRETION FORMULAE
# ============================================================

with st.expander("Accretion Formulae"):

    st.subheader("Eddington luminosity")

    st.latex(r"L_E = f_1\,10^{38}\left(\frac{M}{M_\odot}\right)\ {\rm erg/s}")
    st.latex(rf"L_E = {LE:.6e}\ {{\rm erg/s}}")

    st.divider()

    st.subheader("Eddington accretion rate")

    st.latex(r"\dot{M}_E = \left[f_1\left(\frac{0.06}{\eta_E}\right)\right]3.0\times10^{-8}\left(\frac{M}{M_\odot}\right)\ M_\odot/{\rm yr}")
    st.latex(rf"\dot{{M}}_E = {MdotE:.6e}\ M_\odot/{{\rm yr}}")

    st.divider()

    st.subheader("Mass accretion rate in scaled unit")

    st.latex(r"\dot{m} = \left[\frac{\dot{M}\ M_\odot/{\rm yr}}{f_1\left(\frac{0.06}{\eta_E}\right)\left[3.0\times10^{-8}\left(\frac{M}{M_\odot}\right)\right]\ M_\odot/{\rm yr}}\right]")

    st.divider()

    st.subheader("Scaled radius")

    st.latex(r"r = \frac{R}{3R_S} = \frac{R}{\left(6GM/c^2\right)}")
    st.latex(r"r_s = \frac{R}{R_S} = \frac{R}{\left(2GM/c^2\right)}")
    st.latex(r"r = \frac{r_s}{3}")


# ============================================================
# REGION a
# ============================================================

with st.expander("Region a", expanded=True):

    st.subheader("Temperature")

    st.latex(r"\left[\frac{T}{K}\right] = (2.3\times10^7)[3^{3/4}](\alpha m)^{-1/4}r_s^{-3/4}")
    st.latex(rf"T = {Ta:.6e}\ {{\rm K}}")

    st.divider()

    st.subheader("Number density")

    st.latex(r"\left[\frac{n}{cm^{-3}}\right] = 4.3\times10^{17}[3^{-3/2}]\left[\left(f_1\frac{0.06}{\eta_E}\right)^{-2}\right]\alpha^{-1}m^{-1}\dot{m}^{-2}r_s^{3/2}\left[1-\sqrt{\frac{3}{r_s}}\right]^{-2}")
    st.latex(rf"n = {na:.6e}\ {{\rm cm^{{-3}}}}")


# ============================================================
# REGION b
# ============================================================

with st.expander("Region b"):

    st.subheader("Temperature")

    st.latex(r"\left[\frac{T}{K}\right] = 3.1\times10^8[3^{9/10}]\left[\left(f_1\frac{0.06}{\eta_E}\right)^{2/5}\right]\alpha^{-1/5}m^{-1/5}\dot{m}^{2/5}r_s^{-9/10}\left[1-\sqrt{\frac{3}{r_s}}\right]^{2/5}")
    st.latex(rf"T = {Tb:.6e}\ {{\rm K}}")

    st.divider()

    st.subheader("Number density")

    st.latex(r"\left[\frac{n}{cm^{-3}}\right] = 4.2\times10^{24}[3^{33/20}]\left[\left(f_1\frac{0.06}{\eta_E}\right)^{2/5}\right]\alpha^{-7/10}m^{-7/10}\dot{m}^{2/5}r_s^{-33/20}\left[1-\sqrt{\frac{3}{r_s}}\right]^{2/5}")
    st.latex(rf"n = {nb:.6e}\ {{\rm cm^{{-3}}}}")


# ============================================================
# REGION c
# ============================================================

with st.expander("Region c"):

    st.subheader("Temperature")

    st.latex(r"\left[\frac{T}{K}\right] = [8.6\times10^7][3^{3/4}]\left[\left(f_1\frac{0.06}{\eta_E}\right)^{3/10}\right]\alpha^{-1/5}m^{-1/5}\dot{m}^{3/10}r_s^{-3/4}\left[1-\sqrt{\frac{3}{r_s}}\right]^{3/10}")
    st.latex(rf"T = {Tc:.6e}\ {{\rm K}}")

    st.divider()

    st.subheader("Number density")

    st.latex(r"\left[\frac{n}{cm^{-3}}\right] = [3\times10^{25}][3^{15/8}]\left[\left(f_1\frac{0.06}{\eta_E}\right)^{11/12}\right]\alpha^{-7/10}m^{-7/10}\dot{m}^{11/12}r_s^{-15/8}\left[1-\sqrt{\frac{3}{r_s}}\right]^{11/20}")
    st.latex(rf"n = {nc:.6e}\ {{\rm cm^{{-3}}}}")
