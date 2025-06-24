import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import simpson, trapezoid
from matplotlib.lines import Line2D

def read_file(uploaded_file):
    try:
        if st.checkbox("Small space is separating criteria"):
            return pd.read_csv(uploaded_file, delim_whitespace=True)
        else:
            return pd.read_csv(uploaded_file)
    except:
        st.error("Unsupported file format. Please upload a valid CSV file with tabular data (comma or space-separated).")
        return None

def plot_graph(data, x_column, y_columns, custom_labels, x_log_scale, y_log_scale, x_range, y_range,
               graph_title, style_map, color_map, x_label, y_label):
    plt.figure(figsize=(10, 6))

    # Reverse maps for legend creation
    color_groups = {}
    for y_col, c_info in color_map.items():
        color_groups.setdefault(c_info['label'], set()).add(y_col)

    style_groups = {}
    for y_col, style_info in style_map.items():
        style_groups.setdefault(style_info['label'], style_info['style'])

    # Plot each line with color and style
    for y_col in y_columns:
        # Get color & label
        c = color_map[y_col]['color'] if y_col in color_map else None
        c_label = color_map[y_col]['label'] if y_col in color_map else y_col
        # Get style & label
        ls = style_map[y_col]['style'] if y_col in style_map else '-'
        ls_label = style_map[y_col]['label'] if y_col in style_map else 'Solid'

        # Plot line with label = None (we'll create custom legends)
        plt.plot(data[x_column], data[y_col], marker='o', linestyle=ls, color=c, label=None)

    if x_log_scale:
        plt.xscale('log')
    if y_log_scale:
        plt.yscale('log')
    if x_range:
        plt.xlim(x_range)
    if y_range:
        plt.ylim(y_range)

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(graph_title)
    plt.grid(True)

    # Create custom legend for colors
    color_legend_handles = [
        Line2D([0], [0], color=next(iter([v['color'] for k,v in color_map.items() if color_map[k]['label']==label])), lw=2)
        for label in color_groups
    ]
    plt.legend(color_legend_handles, list(color_groups.keys()), title="Color Groups", loc='upper left')

    # Create custom legend for line styles
    style_legend_handles = [
        Line2D([0], [0], color='black', lw=2, linestyle=style_groups[label])
        for label in style_groups
    ]
    plt.legend(style_legend_handles, list(style_groups.keys()), title="Line Style Groups", loc='upper right')

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

            st.subheader("Color Grouping (Multiple Y columns per color group)")
            st.write("Select one or more Y-axis columns per color group and provide a label for that group.")

            color_groups = {}
            used_columns_color = set()
            max_color_groups = 5
            for i in range(max_color_groups):
                cols = st.multiselect(f"Color Group {i+1} - Select Y columns", [col for col in y_columns if col not in used_columns_color])
                label = st.text_input(f"Color Group {i+1} Label", key=f"color_label_{i}")
                if cols and label:
                    for c in cols:
                        used_columns_color.add(c)
                    color_groups[label] = cols

            # Assign colors for each group
            base_colors = plt.cm.get_cmap('tab10').colors
            color_map = {}
            for idx, (label, cols) in enumerate(color_groups.items()):
                col_color = base_colors[idx % len(base_colors)]
                for c in cols:
                    color_map[c] = {'color': col_color, 'label': label}

            # For columns not assigned to color groups, assign unique colors
            for c in y_columns:
                if c not in color_map:
                    idx = len(color_map)
                    col_color = base_colors[idx % len(base_colors)]
                    color_map[c] = {'color': col_color, 'label': c}

            st.subheader("Line Style Grouping (Multiple Y columns per style group)")
            st.write("Select one or more Y-axis columns per line style group and provide a label for that group.")

            # Available line styles
            available_styles = ['-', '--', '-.', ':']
            style_names = ['Solid', 'Dashed', 'Dash-dot', 'Dotted']

            style_groups = {}
            used_columns_style = set()
            max_style_groups = 4
            for i in range(max_style_groups):
                cols = st.multiselect(f"Style Group {i+1} - Select Y columns", [col for col in y_columns if col not in used_columns_style])
                label = st.text_input(f"Style Group {i+1} Label", key=f"style_label_{i}")
                if cols and label:
                    for c in cols:
                        used_columns_style.add(c)
                    style_groups[label] = {'columns': cols, 'style': available_styles[i % len(available_styles)]}

            style_map = {}
            for label, group_info in style_groups.items():
                for c in group_info['columns']:
                    style_map[c] = {'style': group_info['style'], 'label': label}

            # Assign solid style for columns not in any style group
            for c in y_columns:
                if c not in style_map:
                    style_map[c] = {'style': '-', 'label': 'Solid'}

            custom_labels_input = st.text_input("Enter custom legends for Y lines (comma-separated, optional)", "")
            custom_labels = [label.strip() for label in custom_labels_input.split(",")] if custom_labels_input else []

            y_log_detected = all([is_probably_log(data[col]) for col in y_columns])
            y_log_scale = st.checkbox("Log scale for Y-axis", value=y_log_detected)
            y_range_min = st.number_input("Y-axis min", value=float(data[y_columns[0]].min()) if y_columns else 0.0, format="%.10e")
            y_range_max = st.number_input("Y-axis max", value=float(data[y_columns[0]].max()) if y_columns else 1.0, format="%.10e")

            graph_title = st.text_input("Enter Graph Title", f"Multiple Curves: Y vs {x_column}")
            x_axis_label = st.text_input("X-axis Label", x_column)
            y_axis_label = st.text_input("Y-axis Label", "Y Values")

            if st.button("Plot Line Graph"):
                x_range = (x_range_min, x_range_max)
                y_range = (y_range_min, y_range_max)
                plot_graph(data, x_column, y_columns, custom_labels,
                           x_log_scale, y_log_scale, x_range, y_range,
                           graph_title, style_map, color_map,
                           x_axis_label, y_axis_label)

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
