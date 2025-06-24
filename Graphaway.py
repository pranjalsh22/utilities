import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import simpson, trapezoid
import matplotlib.lines as mlines
import itertools

def read_file(uploaded_file):
    try:
        if st.checkbox("Small space is separating criteria"):
            return pd.read_csv(uploaded_file, delim_whitespace=True)
        else:
            return pd.read_csv(uploaded_file)
    except:
        st.error("Unsupported file format. Please upload a valid CSV file with tabular data (comma or space-separated).")
        return None

def plot_graph(data, x_column, y_columns, custom_labels, x_log_scale, y_log_scale, x_range, y_range, graph_title, style_map, color_map):
    plt.figure(figsize=(10, 6))

    used_colors = {}
    used_styles = {}
    color_palette = itertools.cycle(plt.cm.tab10.colors)  # fallback

    assigned_colors = {}

    for idx, y_column in enumerate(y_columns):
        label = custom_labels[idx] if custom_labels and idx < len(custom_labels) else y_column
        style, style_label = style_map.get(y_column, ('solid', 'Default Style'))
        color_label = color_map.get(y_column, 'Default Color')

        # assign consistent color for each color label
        if color_label not in assigned_colors:
            assigned_colors[color_label] = next(color_palette)
        color = assigned_colors[color_label]

        plt.plot(data[x_column], data[y_column], linestyle=style, color=color, marker='o', label=label)
        used_colors[color_label] = color
        used_styles[style_label] = style

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
    plt.title(graph_title)
    plt.grid(True)

    # First legend: Color
    color_legend = [mlines.Line2D([], [], color=clr, linestyle='-', label=label) for label, clr in used_colors.items()]
    first_legend = plt.legend(handles=color_legend, title='Color Groups', loc='upper left')
    plt.gca().add_artist(first_legend)

    # Second legend: Line Style
    style_legend = [mlines.Line2D([], [], color='black', linestyle=sty, label=lbl) for lbl, sty in used_styles.items()]
    plt.legend(handles=style_legend, title='Style Groups', loc='upper right')

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
    st.title("📈 Line Graph Plotting")
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

            graph_title = st.text_input("Enter Graph Title", f"Multiple Curves: Y vs {x_column}")

            # Line Style Groups
            st.markdown("### 🧵 Line Style Groups")
            style_groups = []
            available_style_cols = set(y_columns)
            num_style_groups = st.number_input("How many style groups?", min_value=1, max_value=5, value=2)

            for i in range(num_style_groups):
                with st.expander(f"Style Group {i+1}"):
                    label = st.text_input(f"Style Label for Group {i+1}", key=f"style_label_{i}")
                    style = st.selectbox(f"Line Style for Group {i+1}", ['solid', 'dashed', 'dashdot', 'dotted'], key=f"style_type_{i}")
                    cols = st.multiselect(f"Select Y-columns for this style", sorted(list(available_style_cols)), key=f"style_cols_{i}")
                    available_style_cols -= set(cols)
                    style_groups.append({'label': label, 'style': style, 'columns': cols})

            # Color Groups
            st.markdown("### 🎨 Color Groups")
            color_groups = []
            available_color_cols = set(y_columns)
            num_color_groups = st.number_input("How many color groups?", min_value=1, max_value=5, value=2)

            for i in range(num_color_groups):
                with st.expander(f"Color Group {i+1}"):
                    label = st.text_input(f"Color Label for Group {i+1}", key=f"color_label_{i}")
                    cols = st.multiselect(f"Select Y-columns for this color group", sorted(list(available_color_cols)), key=f"color_cols_{i}")
                    available_color_cols -= set(cols)
                    color_groups.append({'label': label, 'columns': cols})

            style_map = {}
            for group in style_groups:
                for col in group['columns']:
                    style_map[col] = (group['style'], group['label'])

            color_map = {}
            for group in color_groups:
                for col in group['columns']:
                    color_map[col] = group['label']

            if st.button("Plot Line Graph"):
                x_range = (x_range_min, x_range_max)
                y_range = (y_range_min, y_range_max)
                plot_graph(data, x_column, y_columns, custom_labels, x_log_scale, y_log_scale, x_range, y_range, graph_title, style_map, color_map)

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
