import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import simpson, trapezoid as simps, trapezoid

def read_file(uploaded_file):
    try:
        if st.checkbox("Small space is separating criteria"):
            return pd.read_csv(uploaded_file, delim_whitespace=True)
        else:
            return pd.read_csv(uploaded_file)
    except:
        st.error("Unsupported file format. Please upload a valid CSV file with tabular data (comma or space-separated).")
        return None

def plot_graph(data, x_column, y_column, x_log_scale, y_log_scale, x_range, y_range):
    x_data = data[x_column]
    y_data = data[y_column]

    plt.figure(figsize=(10, 6))
    plt.plot(x_data, y_data, marker='o', linestyle='-', color='b')
    if x_log_scale:
        plt.xscale('log')
    if y_log_scale:
        plt.yscale('log')
    if x_range:
        plt.xlim(x_range)
    if y_range:
        plt.ylim(y_range)

    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.title(f'Plot of {y_column} vs {x_column}')
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt)

def integrate_curve(x_data, y_data, log_x=False, log_y=False, method='trapezoid'):
    # Convert back from log if log scale was used but data was not in log
    if log_x:
        x_data = np.power(10, x_data)
    if log_y:
        y_data = np.power(10, y_data)

    if method == 'trapezoid':
        return trapezoid(y_data, x_data)
    elif method == 'simpson':
        if len(x_data) < 3:
            return "Simpson's rule requires at least 3 points."
        if len(x_data) % 2 == 0:
            return "Simpson's rule requires an odd number of points. Try removing one row."
        return simps(y_data, x_data)
    else:
        return "Unknown method"

def linegraph():
    st.title("Interactive Data Plotting with Streamlit")
    uploaded_file = st.file_uploader("Upload your data file", key="linegraph")

    if uploaded_file is not None:
        data = read_file(uploaded_file)
        
        if data is not None:
            display_data = data.applymap(lambda x: f'{x:.3e}' if isinstance(x, (float, int)) else x)
            st.subheader("Data Preview")
            st.write(display_data)
            columns = data.columns.tolist()

            col1, col2 = st.columns(2)

            with col1:
                x_column = st.selectbox("Select X-axis column", columns)
                x_log_scale = st.checkbox("Log scale for X-axis", value=False)
                x_range_min = st.number_input(f"X-axis {x_column} min", value=float(data[x_column].min()), format="%.10e")
                x_range_max = st.number_input(f"X-axis {x_column} max", value=float(data[x_column].max()), format="%.10e")

            with col2:
                y_column = st.selectbox("Select Y-axis column", columns, index=1)
                y_log_scale = st.checkbox("Log scale for Y-axis", value=False)
                y_range_min = st.number_input(f"Y-axis {y_column} min", value=float(data[y_column].min()), format="%.10e")
                y_range_max = st.number_input(f"Y-axis {y_column} max", value=float(data[y_column].max()), format="%.10e")

            if st.button("Plot Graph"):
                x_range = (x_range_min, x_range_max)
                y_range = (y_range_min, y_range_max)
                plot_graph(data, x_column, y_column, x_log_scale, y_log_scale, x_range, y_range)

            # ---------------- Integration Section ----------------
            st.subheader("Optional: Integrate Curve")
            st.write("Calculate the area under the curve using numerical methods.")
            log_data = st.checkbox("Is the data already in log scale (before plotting)?", value=False)
            method = st.selectbox("Choose integration method", ["trapezoid", "simpson"])

            if st.button("Find Integral"):
                x_vals = data[x_column].values
                y_vals = data[y_column].values
                result = integrate_curve(
                    x_vals, y_vals,
                    log_x=x_log_scale and not log_data,
                    log_y=y_log_scale and not log_data,
                    method=method
                )
                st.success(f"Estimated integral using {method} rule: {result}")
            # ------------------------------------------------------

def plot_pie_chart():
    """Handles file upload and plots a pie chart based on the selected column."""
    st.title("Pie Chart Visualization")
    uploaded_file = st.file_uploader("Upload your data file", key="piechart")

    if uploaded_file is not None:
        data = read_file(uploaded_file)

        if data is not None:
            st.subheader("Data Preview")
            st.write(data)

            column = st.selectbox("Select a column for the pie chart", data.columns)

            fig, ax = plt.subplots()
            data[column].value_counts().plot.pie(autopct='%1.1f%%', ax=ax)
            ax.set_title(f"Pie Chart of {column}")
            st.pyplot(fig)

# Main App Logic
choice = st.selectbox("Choose an option", ["Line Graph", "Pie Chart"])
if choice == "Line Graph":
    linegraph()
elif choice == "Pie Chart":
    plot_pie_chart()

# Sidebar info
st.sidebar.info("version 2")
st.sidebar.write("version 2: added pie chart")
