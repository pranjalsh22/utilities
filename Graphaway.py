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

def is_probably_log(column_data):
    try:
        col = pd.to_numeric(column_data, errors='coerce').dropna().values
        if len(col) == 0:
            return False
        if np.any(col <= 0):
            return False
        if (np.min(col) > -10) and (np.max(col) < 10):
            return True
    except Exception as e:
        return False
    return False


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
    st.title("Line Graph Plotting")
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
                x_log_detected = is_probably_log(data[x_column])
                x_log_scale = st.checkbox("Log scale for X-axis", value=x_log_detected)
                x_range_min = st.number_input(f"X-axis {x_column} min", value=float(data[x_column].min()), format="%.10e")
                x_range_max = st.number_input(f"X-axis {x_column} max", value=float(data[x_column].max()), format="%.10e")

            with col2:
                y_columns = st.multiselect("Select Y-axis columns", columns, default=[columns[1]])
                custom_labels_input = st.text_input("Enter custom legends (comma-separated, optional)", "")
                custom_labels = [label.strip() for label in custom_labels_input.split(",")] if custom_labels_input else []
                y_log_detected = all([is_probably_log(data[col]) for col in y_columns])
                y_log_scale = st.checkbox("Log scale for Y-axis", value=y_log_detected)
                y_range_min = st.number_input("Y-axis min", value=float(data[y_columns[0]].min()), format="%.10e")
                y_range_max = st.number_input("Y-axis max", value=float(data[y_columns[0]].max()), format="%.10e")

            if st.button("Plot Line Graph"):
                x_range = (x_range_min, x_range_max)
                y_range = (y_range_min, y_range_max)
                plot_graph(data, x_column, y_columns, custom_labels, x_log_scale, y_log_scale, x_range, y_range)

            # ---------------- Integration Section ----------------
            st.subheader("🔢 Integration")
            st.write("Estimate area under the curve.")

            st.markdown(f"**Log detection:** X-axis: {x_log_detected}, Y-axis: {y_log_detected}")
            override_log_x = st.checkbox("Override: X-axis data is in log scale", value=x_log_scale)
            override_log_y = st.checkbox("Override: Y-axis data is in log scale", value=y_log_scale)

            method = st.selectbox("Integration Method", ["trapezoid", "Simpson 1/3", "Simpson 3/8"])

            if st.button("➕ Calculate Integral"):
                if len(y_columns) != 1:
                    st.warning("Please select only one Y-axis column for integration.")
                else:
                    x_vals = data[x_column].values
                    y_vals = data[y_columns[0]].values
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

def plot_bar_chart():
    st.title("Bar Chart Visualization")
    uploaded_file = st.file_uploader("Upload your data file", key="barchart")

    if uploaded_file is not None:
        data = read_file(uploaded_file)

        if data is not None:
            st.subheader("Data Preview")
            st.write(data)

            columns = data.columns.tolist()
            x_column = st.selectbox("Select X-axis column", columns)
            y_column = st.selectbox("Select Y-axis column", columns, index=1)

            use_labels = st.checkbox("Use custom labels from a column?")
            if use_labels:
                label_column = st.selectbox("Select column for labels", columns)
                labels = data[label_column].astype(str)
            else:
                labels = data[x_column].astype(str)

            fig, ax = plt.subplots()
            ax.bar(labels, data[y_column])
            ax.set_xlabel(x_column)
            ax.set_ylabel(y_column)
            ax.set_title(f'Bar Chart of {y_column} vs {x_column}')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

# ---------------- Main App ------------------
choice = st.selectbox("Choose a graph type", ["Line Graph", "Pie Chart", "Bar Graph"])

if choice == "Line Graph":
    linegraph()
elif choice == "Pie Chart":
    plot_pie_chart()
elif choice == "Bar Graph":
    plot_bar_chart()

# Sidebar Info
st.sidebar.info("version 3")
st.sidebar.write("✅ Line Graph: multiple curves, custom labels")
st.sidebar.write("✅ Pie Chart: simple value distribution")
st.sidebar.write("✅ Bar Graph: custom labels for categories")
