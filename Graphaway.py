import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import simpson, trapezoid

def read_file(uploaded_file):
    try:
        if st.checkbox("Small space is separating criteria"):
            return pd.read_csv(uploaded_file, delim_whitespace=True)
        else:
            return pd.read_csv(uploaded_file)
    except:
        st.error("Unsupported file format. Please upload a valid CSV file with tabular data (comma or space-separated).")
        return None

def plot_graph(data, x_column, y_columns, custom_labels, x_log_scale, y_log_scale, x_range, y_range):
    plt.figure(figsize=(10, 6))

    for idx, y_column in enumerate(y_columns):
        label = custom_labels[idx] if custom_labels and idx < len(custom_labels) else y_column
        plt.plot(data[x_column], data[y_column], marker='o', linestyle='-', label=label)

    if x_log_scale:
        plt.xscale('log')
    if y_log_scale:
        plt.yscale('log')
    if x_range:
        plt.xlim(x_range)
    if y_range:
        plt.ylim(y_range)

    plt.xlabel(x_column)
    plt.ylabel("Y Values")
    plt.title(f'Multiple Curves: Y vs {x_column}')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    st.pyplot(plt)

def integrate_curve(x_data, y_data, log_x=False, log_y=False, method='trapezoid'):
    if log_x:
        x_data = np.power(10, x_data)
    if log_y:
        y_data = np.power(10, y_data)

    n = len(x_data)

    if method == 'trapezoid':
        return trapezoid(y_data, x_data)

    elif method == 'Simpson 1/3':
        if n < 3:
            return "❌ Simpson's 1/3 rule requires at least 3 points."
        if (n - 1) % 2 != 0:
            return "❌ Simpson's 1/3 rule needs an even number of intervals (odd number of points)."
        return simpson(y_data, x_data)

    elif method == 'Simpson 3/8':
        if n < 4:
            return "❌ Simpson's 3/8 rule requires at least 4 points."
        if (n - 1) % 3 != 0:
            return "❌ Simpson's 3/8 rule requires the number of intervals to be a multiple of 3."
        h = (x_data[-1] - x_data[0]) / (n - 1)
        result = y_data[0] + y_data[-1]
        for i in range(1, n - 1):
            result += 3 * y_data[i] if i % 3 != 0 else 2 * y_data[i]
        return (3 * h / 8) * result

    else:
        return "❌ Unknown method selected."

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
                x_col_numeric = pd.to_numeric(data[x_column], errors='coerce')
                x_log_scale = st.checkbox("Log scale for X-axis", value=False)
                x_range_min = st.number_input(f"X-axis {x_column} min", value=float(x_col_numeric.min()), format="%.10e")
                x_range_max = st.number_input(f"X-axis {x_column} max", value=float(x_col_numeric.max()), format="%.10e")

            with col2:
                y_columns = st.multiselect("Select Y-axis columns", columns, default=[columns[1]])
                custom_labels_input = st.text_input("Enter custom legends (comma-separated, optional)", "")
                custom_labels = [label.strip() for label in custom_labels_input.split(",")] if custom_labels_input else []
                y_col_numeric = pd.to_numeric(data[y_columns[0]], errors='coerce')
                y_log_scale = st.checkbox("Log scale for Y-axis", value=False)
                y_range_min = st.number_input("Y-axis min", value=float(y_col_numeric.min()), format="%.10e")
                y_range_max = st.number_input("Y-axis max", value=float(y_col_numeric.max()), format="%.10e")

            if st.button("Plot Graph"):
                x_range = (x_range_min, x_range_max)
                y_range = (y_range_min, y_range_max)
                plot_graph(data, x_column, y_columns, custom_labels, x_log_scale, y_log_scale, x_range, y_range)

            # ---------------- Integration Section ----------------
            st.subheader("🔢 Integration")
            st.write("Estimate area under the curve.")

            override_log_x = st.checkbox("Override: X-axis data is in log scale", value=x_log_scale)
            override_log_y = st.checkbox("Override: Y-axis data is in log scale", value=y_log_scale)

            method = st.selectbox("Integration Method", ["trapezoid", "Simpson 1/3", "Simpson 3/8"])

            if st.button("➕ Calculate Integral"):
                if len(y_columns) != 1:
                    st.warning("Please select only one Y-axis column for integration.")
                else:
                    x_vals = pd.to_numeric(data[x_column], errors='coerce').values
                    y_vals = pd.to_numeric(data[y_columns[0]], errors='coerce').values
                    result = integrate_curve(
                        x_vals, y_vals,
                        log_x=override_log_x,
                        log_y=override_log_y,
                        method=method
                    )
                    if isinstance(result, str) and result.startswith("❌"):
                        st.error(result)
                    else:
                        st.success(f"Estimated integral using {method} rule: {result:E}")
            # ------------------------------------------------------

def plot_pie_chart():
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
st.sidebar.info("version 3")
st.sidebar.write("version 2: added pie chart")
st.sidebar.write("version 2: added advanced integration options")
st.sidebar.write("version 3: added support for multiple Y-axis curves and custom legends")
