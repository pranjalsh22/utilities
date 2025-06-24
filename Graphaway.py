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

def plot_graph(data, x_column, y_columns, color_groups, pattern_groups, 
               color_labels, pattern_labels, x_log_scale, y_log_scale, x_range, y_range, 
               title, x_label, y_label):
    
    plt.figure(figsize=(10, 6))
    
    pattern_styles = {
        'solid': '-',
        'dotted': ':',
        'dashed': '--',
        'dashdot': '-.'
    }

    # Plot color groups (each group same color, solid line)
    for idx, group in enumerate(color_groups):
        color = plt.cm.tab10(idx % 10)
        label = color_labels[idx] if color_labels and idx < len(color_labels) else f"Color group {idx+1}"
        for col in group:
            plt.plot(data[x_column], data[col], marker='o', linestyle='-', color=color, label=label)
    
    # Plot pattern groups (all black color, different line styles)
    for idx, group in enumerate(pattern_groups):
        if pattern_labels and idx < len(pattern_labels):
            pattern_label, pattern_style_key = pattern_labels[idx]
            linestyle = pattern_styles.get(pattern_style_key, '-')
        else:
            pattern_label = f"Pattern group {idx+1}"
            linestyle = '-'
        for col in group:
            plt.plot(data[x_column], data[col], marker='o', linestyle=linestyle, color='black', label=pattern_label)

    # Remove duplicate legend entries
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), title="Legend")

    if x_log_scale:
        plt.xscale('log')
    if y_log_scale:
        plt.yscale('log')
    if x_range:
        plt.xlim(x_range)
    if y_range:
        plt.ylim(y_range)

    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt)

def is_probably_log(column_data):
    col = np.array(column_data)
    if np.any(col <= 0):
        return False
    if (np.min(col) > -10) and (np.max(col) < 10):
        return True
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
        if data is None:
            return
        
        display_data = data.applymap(lambda x: f'{x:.3e}' if isinstance(x, (float, int)) else x)
        st.subheader("Data Preview")
        st.write(display_data)
        columns = data.columns.tolist()

        # Sidebar for title and axis labels
        st.sidebar.header("Graph Title & Axis Labels")
        x_column = st.sidebar.selectbox("Select X-axis column", columns)
        title = st.sidebar.text_input("Graph Title", value=f'Multiple Curves: Y vs {x_column}')
        x_axis_label = st.sidebar.text_input("X-axis Label", value=x_column)
        y_axis_label = st.sidebar.text_input("Y-axis Label", value="Y Values")

        x_log_detected = is_probably_log(data[x_column])
        y_log_detected_default = False  # We'll compute after Y selection

        with st.expander("X-axis Settings", expanded=True):
            x_log_scale = st.checkbox("Log scale for X-axis", value=x_log_detected)
            x_range_min = st.number_input(f"X-axis min", value=float(data[x_column].min()), format="%.10e")
            x_range_max = st.number_input(f"X-axis max", value=float(data[x_column].max()), format="%.10e")

        with st.expander("Y-axis Settings", expanded=True):
            y_columns = st.multiselect("Select Y-axis columns", columns, default=[columns[1]])
            if y_columns:
                y_log_detected_default = all(is_probably_log(data[col]) for col in y_columns)
                y_log_scale = st.checkbox("Log scale for Y-axis", value=y_log_detected_default)
                y_range_min = st.number_input("Y-axis min", value=float(data[y_columns[0]].min()), format="%.10e")
                y_range_max = st.number_input("Y-axis max", value=float(data[y_columns[0]].max()), format="%.10e")
            else:
                st.warning("Please select at least one Y-axis column.")
                return

        with st.expander("Color Groups (Colored Solid Lines)"):
            st.markdown(
                "Enter groups of Y columns separated by semicolons. Columns in a group separated by commas.\n"
                "**Example:** `col1,col2; col3,col4`"
            )
            color_groups_input = st.text_area(
                "Color Groups",
                value=f"{','.join(y_columns)}",
                height=80
            )
            color_labels_input = st.text_input(
                "Labels for Color Groups (comma-separated)",
                value=""
            )
            color_groups = [grp.strip().split(",") for grp in color_groups_input.split(";") if grp.strip()]
            color_labels = [label.strip() for label in color_labels_input.split(",")] if color_labels_input else []

        with st.expander("Pattern Groups (Black Lines with Patterns)"):
            st.markdown(
                "Enter groups of Y columns separated by semicolons. Columns in a group separated by commas.\n"
                "**Example:** `col1,col2; col3`\n\n"
                "Then specify pattern labels and styles (solid, dotted, dashed, dashdot) separated by semicolons.\n"
                "**Format:** `label|pattern`\n"
                "**Example:** `Group A|dashed; Group B|dotted`"
            )
            pattern_groups_input = st.text_area(
                "Pattern Groups",
                value="",
                height=80
            )
            pattern_labels_input = st.text_area(
                "Pattern Labels & Types",
                value="",
                height=80
            )
            pattern_groups = [grp.strip().split(",") for grp in pattern_groups_input.split(";") if grp.strip()]
            pattern_labels = []
            if pattern_labels_input:
                for item in pattern_labels_input.split(";"):
                    if "|" in item:
                        label, pattern = item.split("|", 1)
                        pattern_labels.append((label.strip(), pattern.strip()))

        if st.button("Plot Line Graph"):
            x_range = (x_range_min, x_range_max)
            y_range = (y_range_min, y_range_max)
            plot_graph(
                data, x_column, y_columns,
                color_groups, pattern_groups,
                color_labels, pattern_labels,
                x_log_scale, y_log_scale,
                x_range, y_range,
                title, x_axis_label, y_axis_label
            )

        # ---------------- Integration Section ----------------
        with st.expander("Integration (Area under curve)"):
            st.write("Estimate area under the curve.")

            st.markdown(f"**Detected log scales:** X-axis: {x_log_detected}, Y-axis: {y_log_detected_default}")
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
